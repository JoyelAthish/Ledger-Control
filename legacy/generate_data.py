import random
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_synthetic_finance_data(num_orders=2000, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    start_date = datetime(2026, 8, 1)

    first_names = [
        "Aarav",
        "Ananya",
        "Rohan",
        "Priya",
        "Karthik",
        "Meera",
        "Vikram",
        "Sneha",
        "Arjun",
        "Divya",
        "Siddharth",
        "Pooja",
        "Rahul",
        "Neha",
        "Aditya",
        "Kavya",
    ]
    last_names = [
        "Sharma",
        "Verma",
        "Patel",
        "Rao",
        "Iyer",
        "Nair",
        "Reddy",
        "Gupta",
        "Joshi",
        "Singh",
        "Kumar",
        "Das",
        "Menon",
        "Pillai",
    ]

    # --- 1. Dataset A: Internal Store / ERP Ledger (2,000 Records) ---
    orders = []
    for i in range(1, num_orders + 1):
        order_id = f"ORD-2026-{i:05d}"
        customer_name = (
            f"{random.choice(first_names)} {random.choice(last_names)}"
        )
        created_at = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        expected_amount = round(random.uniform(200, 15000), 2)

        orders.append({
            "order_id": order_id,
            "customer_name": customer_name,
            "date": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "expected_amount": expected_amount,
        })

    df_erp = pd.DataFrame(orders)

    # --- 2. Dataset B: Razorpay Payment Gateway Report (~1,940 Records) ---
    razorpay_records = []

    for idx, row in df_erp.iterrows():
        # Edge Case 1: Missing in Razorpay (~3% chance - abandoned orders/system drops)
        if random.random() < 0.03:
            continue

        payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        order_id = row["order_id"]
        trx_amount = row["expected_amount"]

        # Edge Case 2: Failed Transaction (~2% chance)
        if random.random() < 0.02:
            status = "failed"
            fee = 0.0
            net_payout = 0.0
        else:
            status = "captured"
            # Edge Case 3: Fee Overcharge Anomaly (3.5% instead of contracted 2.0%) (~5% chance)
            fee_rate = 0.035 if random.random() < 0.05 else 0.020
            fee = round(trx_amount * fee_rate, 2)
            net_payout = round(trx_amount - fee, 2)

        payout_date = datetime.strptime(
            row["date"], "%Y-%m-%d %H:%M:%S"
        ) + timedelta(hours=random.randint(1, 12))

        razorpay_records.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "transaction_amount": trx_amount,
            "razorpay_fee": fee,
            "net_payout": net_payout,
            "status": status,
            "payout_date": payout_date.strftime("%Y-%m-%d %H:%M:%S"),
        })

    df_razorpay = pd.DataFrame(razorpay_records)

    # --- 3. Dataset C: Acquiring Bank Statement (~1,950 Records) ---
    bank_records = []
    settlement_counter = 10001

    # Individual transaction settlements from Razorpay into acquiring bank
    df_captured = df_razorpay[df_razorpay["status"] == "captured"]

    for idx, row in df_captured.iterrows():
        bank_settlement_id = f"BANK-TXN-{settlement_counter}"
        settlement_counter += 1

        deposit_amt = row["net_payout"]
        # Edge Case 4: Bank deposit mismatch/shortfall (~3% chance)
        if random.random() < 0.03:
            deposit_amt = round(deposit_amt - random.uniform(10, 100), 2)

        settlement_date = (
            datetime.strptime(row["payout_date"], "%Y-%m-%d %H:%M:%S")
            + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        bank_records.append({
            "bank_settlement_id": bank_settlement_id,
            "deposited_amount": deposit_amt,
            "settlement_date": settlement_date,
            "description": f"Razorpay Settlement for {row['payment_id']}",
        })

    # Edge Case 5: Unmatched / Orphan Bank Credits (~50 records)
    for _ in range(50):
        bank_settlement_id = f"BANK-TXN-{settlement_counter}"
        settlement_counter += 1
        bank_records.append({
            "bank_settlement_id": bank_settlement_id,
            "deposited_amount": round(random.uniform(500, 10000), 2),
            "settlement_date": "2026-08-15",
            "description": "ACH Credit - Direct Deposit / Unmatched Transfer",
        })

    df_bank = pd.DataFrame(bank_records)

    # --- Save files to disk ---
    df_erp.to_csv("internal_store_ledger.csv", index=False)
    df_razorpay.to_csv("razorpay_payment_report.csv", index=False)
    df_bank.to_csv("acquiring_bank_statement.csv", index=False)

    print("Data Generation Complete!")
    print(
        f"Dataset A (Store ERP Ledger):      {len(df_erp):,} records saved to"
        " internal_store_ledger.csv"
    )
    print(
        f"Dataset B (Razorpay Report):       {len(df_razorpay):,} records saved"
        " to razorpay_payment_report.csv"
    )
    print(
        f"Dataset C (Bank Statement):        {len(df_bank):,} records saved to"
        " acquiring_bank_statement.csv"
    )


if __name__ == "__main__":
    generate_synthetic_finance_data(num_orders=2000)