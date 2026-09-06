import os
import pandas as pd
from google import genai

# Initialize Gemini Client (uses GEMINI_API_KEY environment variable)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# NOTE: a real API key was hardcoded here originally and has been redacted.
# That key is compromised (it was committed to source) — rotate it in
# Google AI Studio. This file is kept only for reference; its logic now
# lives in backend/services/ai_resolution_service.py.

def run_finance_agent():
    print("=" * 70)
    print("     TRACK 04: AI FINANCE CONTROLLER - EXCEPTION RESOLVER AGENT   ")
    print("=" * 70)

    # 1. Load flagged exceptions from reconciliation_exceptions.csv
    if not os.path.exists("reconciliation_exceptions.csv"):
        print(
            "Error: reconciliation_exceptions.csv not found! Run reconcile.py"
            " first."
        )
        return

    df_exceptions = pd.read_csv("reconciliation_exceptions.csv")

    # Filter for high-risk anomalies (e.g., fee overcharges & bank shortfalls)
    high_risk_exceptions = df_exceptions[
        df_exceptions["risk_level"] == "HIGH"
    ].head(5)

    print(
        f"\n[1/2] Processing Top {len(high_risk_exceptions)} High-Risk"
        " Exceptions with AI Agent...\n"
    )

    # 2. Process through LLM reasoning loop
    dispute_tickets = []

    for idx, row in high_risk_exceptions.reset_index(drop=True).iterrows():
        issue_type = row["issue_type"]
        order_id = row["order_id"]
        customer = row["customer_name"]
        amount = row["discrepancy_amount"]
        description = row["description"]

        prompt = f"""
You are an expert AI Finance Controller (FinOps Agent) for an e-commerce company.
Analyze this financial exception and draft an official, professional vendor dispute email to send to Razorpay support or the acquiring bank operations team.

EXCEPTION DATA:
- Order ID: {order_id}
- Customer Name: {customer}
- Issue Category: {issue_type}
- Discrepancy Amount: ₹{amount}
- Context Details: {description}

TASK:
1. Provide a concise 2-sentence financial root-cause diagnosis.
2. Draft a formal Dispute Email to Razorpay Merchant Support requesting resolution/refund. Keep it professional and under 150 words.
        """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        ticket_output = f"""
----------------------------------------------------------------------
EXCEPTION #{idx+1} | ISSUE: {issue_type} | ORDER: {order_id} | AMOUNT: ₹{amount}
----------------------------------------------------------------------
{response.text}
        """
        print(ticket_output)
        dispute_tickets.append(ticket_output)

    # Save outputs to file
    with open("generated_dispute_tickets.txt", "w", encoding="utf-8") as f:
        f.writelines(dispute_tickets)

    print("=" * 70)
    print(
        "AI Resolution Completed! Action tickets saved to"
        " 'generated_dispute_tickets.txt'"
    )


if __name__ == "__main__":
    run_finance_agent()