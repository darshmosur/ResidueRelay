from pydantic import BaseModel, Field
from typing import Optional, Tuple
from app.models.farm import Coordinates

class Baler(BaseModel):
    id: str
    operator_name: str
    operator_phone: str
    baler_type: str = "Square Baler"  # Square Baler, Round Baler
    throughput_acres_per_hour: float = 2.0  # e.g., 2.0 acres/hr
    depot_location: Coordinates
    operating_hours_daily: Tuple[int, int] = (7, 19)  # 07:00 to 19:00 daylight window
    status: str = "available"  # available, busy, broken_down, maintenance
    breakdown_time_hours: Optional[float] = None  # If broken down, hour from T0
    notes: Optional[str] = None
