from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from services import reconciliation_service, ai_resolution_service
from models.schemas import PaginatedExceptions, ResolutionRequest, ResolutionResponse

router = APIRouter(prefix="/api/exceptions", tags=["exceptions"])


@router.get("", response_model=PaginatedExceptions)
def list_exceptions(
    risk: Optional[List[str]] = Query(None, description="Filter by risk level(s)"),
    issue_type: Optional[List[str]] = Query(None, description="Filter by issue type(s)"),
    search: Optional[str] = Query(None, description="Search order_id or customer name"),
    sort_by: str = Query("priority_rank"),
    sort_dir: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    try:
        return reconciliation_service.get_exceptions(
            risk_levels=risk, issue_types=issue_type, search=search,
            sort_by=sort_by, sort_dir=sort_dir, page=page, page_size=page_size,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{order_id}")
def get_exception(order_id: str):
    exc = reconciliation_service.get_exception_by_order_id(order_id)
    if exc is None:
        raise HTTPException(status_code=404, detail=f"Exception '{order_id}' not found")
    cached = ai_resolution_service.cache_service.get_ticket(order_id)
    exc["ai_resolution"] = cached
    return exc


@router.post("/{order_id}/resolve", response_model=ResolutionResponse)
def resolve_exception(order_id: str, body: ResolutionRequest = ResolutionRequest()):
    try:
        return ai_resolution_service.generate_resolution(order_id, force_regenerate=body.force_regenerate)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/regenerate", response_model=ResolutionResponse)
def regenerate_exception(order_id: str):
    try:
        return ai_resolution_service.generate_resolution(order_id, force_regenerate=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{order_id}/approve")
def approve_exception(order_id: str):
    result = ai_resolution_service.approve_resolution(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No cached resolution for '{order_id}' to approve")
    return result
