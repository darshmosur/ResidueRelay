from pydantic import BaseModel
from typing import Optional
from enum import Enum

class DisruptionType(str, Enum):
    RAIN = "rain"
    BALER_BREAKDOWN = "baler_breakdown"
    BUYER_CONGESTION = "buyer_congestion"

class DisruptionEvent(BaseModel):
    id: str
    type: DisruptionType
    target_id: str  # cluster name (e.g., 'Taraori') or baler id (e.g., 'baler-02')
    start_hour: float
    duration_hours: float
    description: str
    severity: str = "critical"  # warning, critical
    is_active: bool = True
