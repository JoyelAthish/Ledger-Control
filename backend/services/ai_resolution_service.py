"""
AI resolution service.

Consolidates the Gemini prompt + call logic that previously existed in two
slightly different forms (app.py's inline call, agent.py's batch call).
The API key is read ONLY from the GEMINI_API_KEY environment variable.

SECURITY NOTE: the original agent.py had a Gemini API key hardcoded in
source. That key must be treated as compromised and rotated in Google AI
Studio; it is intentionally not carried into this file.
"""
import os
from . import cache_service, reconciliation_service

MODEL_NAME = "gemini-3.6-flash"


def _get_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your environment or .env file."
        )
    return genai.Client(api_key=api_key)


def _build_prompt(exc: dict) -> str:
    return f"""
You are an expert AI FinOps Controller. Analyze this exception and generate an action ticket.

DETAILS:
- Order ID: {exc['order_id']}
- Customer: {exc['customer_name']}
- Issue Type: {exc['issue_type']}
- Priority: {exc['risk_level']}
- Store Amount: ₹{exc.get('store_amount', 0)}
- Gateway Amount: ₹{exc.get('gateway_amount', 0)}
- Bank Amount: ₹{exc.get('bank_amount', 0)}
- Charged Fee: ₹{exc.get('gateway_fee', 0)}
- Discrepancy Amount: ₹{exc['discrepancy_amount']}

INSTRUCTIONS:
1. Provide a "Financial Root-Cause Diagnosis" (2-3 sentences explaining why this variance occurred mathematically).
2. Draft a formal "Vendor Dispute Email" to Razorpay/Bank citing order number, contracted terms, and exact refund claim amounts.
"""


def _split_response(full_text: str) -> tuple[str, str]:
    if "Vendor Dispute Email" in full_text:
        parts = full_text.split("Vendor Dispute Email")
        diagnosis = parts[0].replace("Financial Root-Cause Diagnosis", "").replace("#", "").strip()
        email = parts[1].strip()
    else:
        diagnosis = email = full_text
    return diagnosis, email


def generate_resolution(order_id: str, force_regenerate: bool = False) -> dict:
    """Returns {order_id, diagnosis, email, status, from_cache}. Raises
    FileNotFoundError / ValueError / RuntimeError on bad input or missing key."""
    if not force_regenerate:
        cached = cache_service.get_ticket(order_id)
        if cached:
            return {
                "order_id": order_id,
                "diagnosis": cached["diagnosis"],
                "email": cached["email"],
                "status": cached.get("status", "generated"),
                "from_cache": True,
            }

    exc = reconciliation_service.get_exception_by_order_id(order_id)
    if exc is None:
        raise ValueError(f"No exception found for order_id '{order_id}'")

    client = _get_client()
    prompt = _build_prompt(exc)
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    diagnosis, email = _split_response(response.text)

    saved = cache_service.set_ticket(order_id, diagnosis, email, status="generated")
    return {
        "order_id": order_id,
        "diagnosis": saved["diagnosis"],
        "email": saved["email"],
        "status": saved["status"],
        "from_cache": False,
    }


def approve_resolution(order_id: str) -> dict | None:
    return cache_service.update_status(order_id, "approved")
