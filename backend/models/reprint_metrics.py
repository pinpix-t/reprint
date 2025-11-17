from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class ReprintMetrics(BaseModel):
    total_reprints: int
    period_start: datetime
    period_end: datetime
    previous_period_total: Optional[int] = None
    change_percentage: Optional[float] = None

class ProductMetrics(BaseModel):
    product_type: str
    count: int
    percentage: float
    top_reasons: List[Dict[str, int]]

class FacilityMetrics(BaseModel):
    facility: str
    count: int
    percentage: float
    top_products: List[Dict[str, int]]
    top_reasons: List[Dict[str, int]]

class ReasonMetrics(BaseModel):
    reason: str
    count: int
    percentage: float
    affected_products: List[str]

class TrendDataPoint(BaseModel):
    date: datetime
    count: int
    by_product: Optional[Dict[str, int]] = None
    by_facility: Optional[Dict[str, int]] = None
    by_reason: Optional[Dict[str, int]] = None

class ComparisonMetrics(BaseModel):
    current: int
    previous: int
    change: int
    change_percentage: float
    period: str  # "week", "month", "year"

class FacilityProductMatrix(BaseModel):
    facility: str
    product: str
    count: int
    reasons: Dict[str, int]

