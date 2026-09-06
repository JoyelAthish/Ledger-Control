"""
inject_low_variance_cases.py

One-time data-augmentation script for the Autonomous Finance Controller demo.

Picks a handful of ALREADY-RECONCILED orders (orders that currently match
perfectly across store ledger -> gateway -> bank) and introduces small,
controlled discrepancies into the source CSVs:

  - N orders get a tiny Razorpay fee overcharge (₹1.00-₹4.50) that reconcile.py
    (after the LOW-tier patch) will classify as MINOR_FEE_VARIANCE / LOW.
  - N orders get a tiny bank settlement shortfall (₹1.00-₹4.50) that will be
    classified as MINOR_SETTLEMENT_VARIANCE / LOW.

Run this ONCE from inside your data/ folder, BEFORE re-running reconcile.py.
It edits razorpay_payment_report.csv and acquiring_bank_statement.csv in
place (a .bak backup of each is written first).

Usage:
    cd F_C/data
    python inject_low_variance_cases.py
"""
import random
import pandas as pd

random.seed(42)

N_FEE_CASES = 5
N_BANK_CASES = 5
MIN_DELTA = 1.00
MAX_DELTA = 4.50

STORE_CSV = "internal_store_ledger.csv"
GATEWAY_CSV = "razorpay_payment_report.csv"
BANK_CSV = "acquiring_bank_statement.csv"
EXCEPTIONS_CSV = "reconciliation_exceptions.csv"


def main():
    erp = pd.read_csv(STORE_CSV)
    rzp = pd.read_csv(GATEWAY_CSV)
    bank = pd.read_csv(BANK_CSV)

    try:
        exc = pd.read_csv(EXCEPTIONS_CSV)
        exception_orders = set(exc["order_id"]) - {"N/A"}
    except FileNotFoundError:
        exception_orders = set()

    bank_tmp = bank.copy()
    bank_tmp["payment_id"] = bank_tmp["description"].str.extract(r"(pay_[a-f0-9]+)")[0]
    bank_unique = bank_tmp.drop_duplicates(subset=["payment_id"], keep="first")

    merged = pd.merge(erp, rzp, on="order_id", how="left", suffixes=("_erp", "_rzp"))
    full = pd.merge(merged, bank_unique, on="payment_id", how="left")

    clean = full[
        (~full["order_id"].isin(exception_orders))
        & full["deposited_amount"].notna()
        & full["status"].eq("captured")
    ]

    if len(clean) < N_FEE_CASES + N_BANK_CASES:
        raise SystemExit("Not enough clean reconciled orders to inject into. Aborting.")

    sample = clean.sample(n=N_FEE_CASES + N_BANK_CASES, random_state=42)
    fee_targets = sample.iloc[:N_FEE_CASES]
    bank_targets = sample.iloc[N_FEE_CASES:]

    # backups
    rzp.to_csv(GATEWAY_CSV + ".bak", index=False)
    bank.to_csv(BANK_CSV + ".bak", index=False)

    rzp = rzp.set_index("payment_id")
    bank_settlement_lookup = bank.set_index("bank_settlement_id")

    print("Injecting minor FEE variances (-> MINOR_FEE_VARIANCE / LOW):")
    for _, row in fee_targets.iterrows():
        pid = row["payment_id"]
        delta = round(random.uniform(MIN_DELTA, MAX_DELTA), 2)
        new_fee = round(rzp.loc[pid, "razorpay_fee"] + delta, 2)
        new_net_payout = round(rzp.loc[pid, "transaction_amount"] - new_fee, 2)
        rzp.loc[pid, "razorpay_fee"] = new_fee
        rzp.loc[pid, "net_payout"] = new_net_payout

        settlement_id = row["bank_settlement_id"]
        bank_settlement_lookup.loc[settlement_id, "deposited_amount"] = new_net_payout
        print(f"  {row['order_id']}  ({pid})  fee +₹{delta}")

    print("\nInjecting minor BANK settlement variances (-> MINOR_SETTLEMENT_VARIANCE / LOW):")
    for _, row in bank_targets.iterrows():
        settlement_id = row["bank_settlement_id"]
        delta = round(random.uniform(MIN_DELTA, MAX_DELTA), 2)
        new_deposit = round(row["net_payout"] - delta, 2)
        bank_settlement_lookup.loc[settlement_id, "deposited_amount"] = new_deposit
        print(f"  {row['order_id']}  ({settlement_id})  deposit -₹{delta}")

    rzp = rzp.reset_index()[["payment_id", "order_id", "transaction_amount", "razorpay_fee", "net_payout", "status", "payout_date"]]
    bank_out = bank_settlement_lookup.reset_index()[["bank_settlement_id", "deposited_amount", "settlement_date", "description"]]

    rzp.to_csv(GATEWAY_CSV, index=False)
    bank_out.to_csv(BANK_CSV, index=False)

    print(f"\nDone. Backups saved as {GATEWAY_CSV}.bak and {BANK_CSV}.bak")
    print("Next: run reconcile.py (with the LOW-tier patch applied) to regenerate reconciliation_exceptions.csv")


if __name__ == "__main__":
    main()
