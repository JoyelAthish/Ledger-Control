import os
import time
import pandas as pd


def run_reconciliation_pipeline():
    start_time = time.time()

    print("=" * 70)
    print("      TRACK 04: AI FINANCE CONTROLLER - RECONCILIATION ENGINE     ")
    print("=" * 70)

    # 1. Load Synthetic Datasets
    print("\n[1/4] Loading Financial Datasets...")
    df_erp = pd.read_csv("internal_store_ledger.csv")
    df_razorpay = pd.read_csv("razorpay_payment_report.csv")
    df_bank = pd.read_csv("acquiring_bank_statement.csv")

    print(f"  • Dataset A (Store Ledger):     {len(df_erp):,} records")
    print(f"  • Dataset B (Razorpay Report):  {len(df_razorpay):,} records")
    print(f"  • Dataset C (Bank Statement):   {len(df_bank):,} records")

    # 2. Multi-Source Matching Engine (Prevents Duplicate Explosions)
    print("\n[2/4] Executing Multi-Source Matching Engine...")

    # Extract payment_id from bank descriptions cleanly
    df_bank["payment_id"] = (
        df_bank["description"].str.extract(r"(pay_[a-f0-9]+)")[0]
    )

    # Deduplicate bank statement to 1 payment_id entry to prevent join multiplication
    df_bank_unique = df_bank.drop_duplicates(
        subset=["payment_id"], keep="first"
    )

    # Clean Left Joins: ERP -> Razorpay -> Unique Bank
    merged = pd.merge(
        df_erp, df_razorpay, on="order_id", how="left", suffixes=("_erp", "_rzp")
    )
    full_recon = pd.merge(merged, df_bank_unique, on="payment_id", how="left")

    # 3. Anomaly Classification Loop
    print("[3/4] Categorizing Transactions & Detecting Anomalies...")

    reconciled_list = []
    exceptions_list = []

    for idx, row in full_recon.iterrows():
        order_id = row["order_id"]
        customer_name = row["customer_name"]
        expected_amount = row["expected_amount"]
        rzp_status = row["status"]
        rzp_fee = row["razorpay_fee"]
        rzp_net = row["net_payout"]
        bank_deposit = row["deposited_amount"]

        # Standard contract fee rate = 2.0%
        expected_fee = round(expected_amount * 0.02, 2)

        # Below this, a fee/settlement mismatch is treated as negligible
        # noise (LOW) rather than a genuine dispute-worthy anomaly (HIGH).
        LOW_VARIANCE_THRESHOLD = 5.00

        # Condition 1: Missing in Razorpay
        if pd.isna(rzp_status):
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "MISSING_GATEWAY_PAYOUT",
                "risk_level": "HIGH",
                "discrepancy_amount": expected_amount,
                "description": "Order exists in store ledger but has no record in Razorpay payouts.",
                "action": "Investigate abandoned checkout or uncaptured payment gateway webhook.",
            })

        # Condition 2: Payment Failed
        elif rzp_status == "failed":
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "PAYMENT_FAILED",
                "risk_level": "MEDIUM",
                "discrepancy_amount": expected_amount,
                "description": "Transaction failed at payment gateway.",
                "action": "Verify if customer was charged; notify sales team for retry.",
            })

        # Condition 3: Razorpay Fee Overcharge (Fee Mismatch)
        elif abs(rzp_fee - expected_fee) > 0.05 and abs(rzp_fee - expected_fee) <= LOW_VARIANCE_THRESHOLD:
            overcharge = round(rzp_fee - expected_fee, 2)
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "MINOR_FEE_VARIANCE",
                "risk_level": "LOW",
                "discrepancy_amount": overcharge,
                "description": f"Razorpay fee ₹{rzp_fee} differs from the contracted ₹{expected_fee} by a negligible amount.",
                "action": "No action required; monitor for a recurring pattern.",
            })

        elif abs(rzp_fee - expected_fee) > LOW_VARIANCE_THRESHOLD:
            overcharge = round(rzp_fee - expected_fee, 2)
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "FEE_OVERCHARGE_ANOMALY",
                "risk_level": "HIGH",
                "discrepancy_amount": overcharge,
                "description": f"Razorpay charged fee ₹{rzp_fee} (3.5%) instead of contracted ₹{expected_fee} (2.0%).",
                "action": "Raise contractual dispute ticket with Razorpay support for fee adjustment.",
            })

        # Condition 4a: Minor Bank Settlement Variance (negligible, LOW)
        elif pd.notna(bank_deposit) and 0.05 < abs(bank_deposit - rzp_net) <= LOW_VARIANCE_THRESHOLD:
            shortfall = round(rzp_net - bank_deposit, 2)
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "MINOR_SETTLEMENT_VARIANCE",
                "risk_level": "LOW",
                "discrepancy_amount": shortfall,
                "description": f"Bank received ₹{bank_deposit} vs Razorpay net payout ₹{rzp_net} — a negligible settlement variance.",
                "action": "No action required; monitor for a recurring pattern.",
            })

        # Condition 4b: Bank Shortfall Mismatch
        elif pd.notna(bank_deposit) and abs(bank_deposit - rzp_net) > LOW_VARIANCE_THRESHOLD:
            shortfall = round(rzp_net - bank_deposit, 2)
            exceptions_list.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "issue_type": "BANK_DEPOSIT_SHORTFALL",
                "risk_level": "HIGH",
                "discrepancy_amount": shortfall,
                "description": f"Bank received ₹{bank_deposit}, but Razorpay net payout was ₹{rzp_net}.",
                "action": "Audit acquiring bank settlement deductions or intermediary transfer charges.",
            })

        # Condition 5: Fully Reconciled
        else:
            reconciled_list.append(order_id)

    # Condition 6: Orphan Bank Credits (Bank credits with no ERP payment_id match)
    matched_payment_ids = set(full_recon["payment_id"].dropna())
    orphan_bank_credits = df_bank[
        ~df_bank["payment_id"].isin(matched_payment_ids)
    ]

    for idx, row in orphan_bank_credits.iterrows():
        exceptions_list.append({
            "order_id": "N/A",
            "customer_name": "N/A",
            "issue_type": "ORPHAN_BANK_CREDIT",
            "risk_level": "MEDIUM",
            "discrepancy_amount": row["deposited_amount"],
            "description": f"Bank credit of ₹{row['deposited_amount']} received with description '{row['description']}' has no matching internal order.",
            "action": "Cross-reference treasury bank logs or offline wire transfers.",
        })

    # Save exceptions to CSV
    df_exceptions = pd.DataFrame(exceptions_list)
    df_exceptions.to_csv("reconciliation_exceptions.csv", index=False)

    execution_time = round(time.time() - start_time, 3)

    # 4. Generate Performance Metrics
    total_orders = len(df_erp)
    matched_count = len(reconciled_list)
    exception_count = len(df_exceptions)
    match_rate = round((matched_count / total_orders) * 100, 2)

    print("\n[4/4] Generating Audit Summary Report...")
    print("=" * 70)
    print("                    AUDIT & PERFORMANCE METRICS                   ")
    print("=" * 70)
    print(f"  • Throughput Execution Time : {execution_time} seconds")
    print(f"  • Total Orders Evaluated   : {total_orders:,}")
    print(f"  • Successfully Reconciled  : {matched_count:,}")
    print(f"  • Measured Accuracy Match Rate: {match_rate}%")
    print(f"  • Total Flagged Exceptions : {exception_count:,}")
    print("=" * 70)

    print("\nBREAKDOWN OF UNRESOLVED EXCEPTIONS:")
    print("-" * 70)
    issue_counts = df_exceptions["issue_type"].value_counts()
    for issue, count in issue_counts.items():
        print(f"  • {issue:<25}: {count} records")
    print("-" * 70)

    print(
        "\nDetailed exceptions saved to -> 'reconciliation_exceptions.csv'"
    )


if __name__ == "__main__":
    run_reconciliation_pipeline()