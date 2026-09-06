from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from services import reconciliation_service

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/{source}")
def get_transactions(
    source: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
):
    """source: one of 'store', 'gateway', 'bank', 'exceptions'."""
    try:
        return reconciliation_service.get_transactions(source, page=page, page_size=page_size, search=search)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
