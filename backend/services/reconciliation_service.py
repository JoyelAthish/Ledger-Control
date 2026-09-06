"""
Reconciliation service.

Wraps the existing reconcile.py business logic (unchanged classification
rules) so it can be called from FastAPI, and adds an enrichment step that
joins each exception back to its Store / Gateway / Bank source rows so the
UI can show a real Store -> Gateway -> Bank -> Variance breakdown (this data
existed in the join but was never persisted to reconciliation_exceptions.csv
by the original script).
"""
import os
import pandas as pd
from functools import lru_cache

DATA_DIR = os.environ.get("FINANCE_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))

STORE_CSV = os.path.join(DATA_DIR, "internal_store_ledger.csv")
GATEWAY_CSV = os.path.join(DATA_DIR, "razorpay_payment_report.csv")
BANK_CSV = os.path.join(DATA_DIR, "acquiring_bank_statement.csv")
EXCEPTIONS_CSV = os.path.join(DATA_DIR, "reconciliation_exceptions.csv")

PRIORITY_ORDER = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _load_raw():
    df_erp = pd.read_csv(STORE_CSV)
    df_razorpay = pd.read_csv(GATEWAY_CSV)
    df_bank = pd.read_csv(BANK_CSV)
    return df_erp, df_razorpay, df_bank


def _build_full_join():
    """Same join reconcile.py performs, kept identical so classification stays consistent."""
    df_erp, df_razorpay, df_bank = _load_raw()

    df_bank = df_bank.copy()
    df_bank["payment_id"] = df_bank["description"].str.extract(r"(pay_[a-f0-9]+)")[0]
    df_bank_unique = df_bank.drop_duplicates(subset=["payment_id"], keep="first")

    merged = pd.merge(df_erp, df_razorpay, on="order_id", how="left", suffixes=("_erp", "_rzp"))
    full_recon = pd.merge(merged, df_bank_unique, on="payment_id", how="left")
    return full_recon


@lru_cache(maxsize=1)
def _cached_join():
    return _build_full_join()


def clear_cache():
    _cached_join.cache_clear()
    load_exceptions.cache_clear()


@lru_cache(maxsize=1)
def load_exceptions() -> pd.DataFrame:
    """Loads reconciliation_exceptions.csv (produced by reconcile.py) and
    enriches each row with store/gateway/bank amounts + fee for the detail view."""
    if not os.path.exists(EXCEPTIONS_CSV):
        raise FileNotFoundError(
            f"'{EXCEPTIONS_CSV}' not found. Run the reconciliation engine first."
        )

    df = pd.read_csv(EXCEPTIONS_CSV)
    df["priority_rank"] = df["risk_level"].map(PRIORITY_ORDER)
    df = df.sort_values(by=["priority_rank", "discrepancy_amount"], ascending=[True, False])

    full_recon = _cached_join()
    lookup = full_recon.set_index("order_id")

    def enrich(row):
        oid = row["order_id"]
        if oid in lookup.index:
            src = lookup.loc[oid]
            if isinstance(src, pd.DataFrame):  # duplicate order_id guard
                src = src.iloc[0]
            store_amt = src.get("expected_amount", None)
            # pandas merge treats NaN == NaN as a match, so an order with no
            # Razorpay row (payment_id is NaN) can spuriously join to a
            # leftover unmatched bank row. If there's no real payment_id,
            # there can be no real gateway/bank figures for this order.
            has_payment_match = pd.notna(src.get("payment_id"))
            gateway_amt = src.get("net_payout", None) if has_payment_match else 0.0
            bank_amt = src.get("deposited_amount", None) if has_payment_match else 0.0
            fee_amt = src.get("razorpay_fee", None) if has_payment_match else 0.0
        else:
            store_amt = gateway_amt = bank_amt = fee_amt = None
        return pd.Series({
            "store_amount": store_amt,
            "gateway_amount": gateway_amt,
            "bank_amount": bank_amt,
            "gateway_fee": fee_amt,
        })

    enrichment = df.apply(enrich, axis=1)
    df = pd.concat([df, enrichment], axis=1)
    for col in ["store_amount", "gateway_amount", "bank_amount", "gateway_fee"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).round(2)

    return df


def get_dashboard_summary() -> dict:
    df = load_exceptions()
    df_erp, _, _ = _load_raw()
    total_orders = len(df_erp)
    return {
        "total_orders": total_orders,
        "flagged_exceptions": int(len(df)),
        "high_priority_cases": int((df["risk_level"] == "HIGH").sum()),
        "total_disputed_amount": round(float(df["discrepancy_amount"].sum()), 2),
        "match_rate_pct": round((total_orders - len(df)) / total_orders * 100, 2) if total_orders else 0.0,
    }


def get_exceptions(risk_levels=None, issue_types=None, search=None,
                    sort_by="priority_rank", sort_dir="asc",
                    page=1, page_size=25) -> dict:
    df = load_exceptions()

    if risk_levels:
        df = df[df["risk_level"].isin(risk_levels)]
    if issue_types:
        df = df[df["issue_type"].isin(issue_types)]
    if search:
        s = search.strip().lower()
        df = df[
            df["order_id"].str.lower().str.contains(s, na=False)
            | df["customer_name"].str.lower().str.contains(s, na=False)
        ]

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(sort_dir == "asc"))

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    cols = ["order_id", "customer_name", "issue_type", "risk_level",
            "discrepancy_amount", "store_amount", "gateway_amount",
            "bank_amount", "gateway_fee", "description", "action"]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": page_df[cols].to_dict(orient="records"),
    }


def get_exception_by_order_id(order_id: str) -> dict | None:
    df = load_exceptions()
    match = df[df["order_id"] == order_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_analytics() -> dict:
    df = load_exceptions()

    loss_by_issue = (
        df.groupby("issue_type")["discrepancy_amount"].sum().round(2).sort_values(ascending=False)
    )
    risk_counts = df["risk_level"].value_counts()
    top_10 = df.nlargest(10, "discrepancy_amount")[
        ["order_id", "customer_name", "issue_type", "discrepancy_amount"]
    ]

    return {
        "loss_by_issue_type": [
            {"issue_type": k, "total_loss": v} for k, v in loss_by_issue.items()
        ],
        "exceptions_by_risk": [
            {"risk_level": k, "count": int(v)} for k, v in risk_counts.items()
        ],
        "top_10_exceptions": top_10.to_dict(orient="records"),
    }


def get_transactions(source: str, page=1, page_size=50, search=None) -> dict:
    files = {
        "store": STORE_CSV,
        "gateway": GATEWAY_CSV,
        "bank": BANK_CSV,
        "exceptions": EXCEPTIONS_CSV,
    }
    if source not in files:
        raise ValueError(f"Unknown source '{source}'. Expected one of {list(files)}.")

    df = pd.read_csv(files[source])
    if search:
        s = search.strip().lower()
        mask = df.apply(lambda col: col.astype(str).str.lower().str.contains(s, na=False))
        df = df[mask.any(axis=1)]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "columns": list(df.columns),
        "results": page_df.to_dict(orient="records"),
    }
