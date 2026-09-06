from fastapi import APIRouter, HTTPException
from services import reconciliation_service
from models.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard():
    try:
        return reconciliation_service.get_dashboard_summary()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
