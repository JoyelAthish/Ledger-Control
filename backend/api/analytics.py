from fastapi import APIRouter, HTTPException
from services import reconciliation_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
def get_analytics():
    try:
        return reconciliation_service.get_analytics()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
