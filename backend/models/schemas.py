from pydantic import BaseModel
from typing import Optional, List, Any


class DashboardSummary(BaseModel):
    total_orders: int
    flagged_exceptions: int
    high_priority_cases: int
    total_disputed_amount: float
    match_rate_pct: float


class ExceptionRecord(BaseModel):
    order_id: str
    customer_name: str
    issue_type: str
    risk_level: str
    discrepancy_amount: float
    store_amount: float
    gateway_amount: float
    bank_amount: float
    gateway_fee: float
    description: str
    action: str


class PaginatedExceptions(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[ExceptionRecord]


class ResolutionRequest(BaseModel):
    force_regenerate: bool = False


class ResolutionResponse(BaseModel):
    order_id: str
    diagnosis: str
    email: str
    status: str
    from_cache: bool


class CacheStats(BaseModel):
    cached_ticket_count: int
    cache_file: str


class HealthStatus(BaseModel):
    status: str
    reconciliation_engine: str
    ai_model: str
    data_source: str
    cache_status: str
