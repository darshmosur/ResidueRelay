from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    id: str
    farm_id: str
    baler_id: str
    buyer_id: str
    start_hour: float  # Hours from T0
    end_hour: float    # Hours from T0
    duration_hours: float
    travel_time_hours: float = 0.0
    straw_tons: float
    status: str = "draft"  # draft, approved, in_progress, completed, disrupted
    delay_hours: float = 0.0  # delay past ready harvest time
    exceeds_deadline: bool = False  # True if end_hour > sowing_deadline_hours
    disruption_note: Optional[str] = None
