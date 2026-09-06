"""
AI ticket cache service.

Replaces the Streamlit session_state + JSON file pattern in app.py with a
plain file-backed cache FastAPI can read/write. Same file, same schema:
{ order_id: {"diagnosis": str, "email": str} }
"""
import json
import os
import threading

DATA_DIR = os.environ.get("FINANCE_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))
CACHE_FILE = os.path.join(DATA_DIR, "ai_tickets_cache.json")

_lock = threading.Lock()


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache_data: dict) -> None:
    with _lock:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)


def get_ticket(order_id: str) -> dict | None:
    return load_cache().get(order_id)


def set_ticket(order_id: str, diagnosis: str, email: str, status: str = "generated") -> dict:
    cache = load_cache()
    cache[order_id] = {"diagnosis": diagnosis, "email": email, "status": status}
    save_cache(cache)
    return cache[order_id]


def update_status(order_id: str, status: str) -> dict | None:
    cache = load_cache()
    if order_id not in cache:
        return None
    cache[order_id]["status"] = status
    save_cache(cache)
    return cache[order_id]


def clear_cache() -> None:
    save_cache({})
    if os.path.exists(CACHE_FILE):
        # keep the file but empty, matching a "cleared" state that's still inspectable
        pass


def cache_stats() -> dict:
    cache = load_cache()
    return {"cached_ticket_count": len(cache), "cache_file": CACHE_FILE}
