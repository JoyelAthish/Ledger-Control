import os
from fastapi import APIRouter
from services import cache_service, reconciliation_service

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/cache")
def get_cache_stats():
    return cache_service.cache_stats()


@router.delete("/cache")
def clear_cache():
    cache_service.clear_cache()
    return {"status": "cleared", **cache_service.cache_stats()}


@router.get("/health")
def health():
    data_ok = os.path.exists(reconciliation_service.EXCEPTIONS_CSV)
    return {
        "status": "ok" if data_ok else "degraded",
        "reconciliation_engine": "Rule-based deterministic join (reconcile.py)",
        "ai_model": "gemini-3.6-flash",
        "gemini_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "data_source": "ok" if data_ok else "reconciliation_exceptions.csv missing - run reconcile.py",
        "cache_status": cache_service.cache_stats(),
    }
