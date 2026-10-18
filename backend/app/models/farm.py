from pydantic import BaseModel, Field
from typing import Optional

class Coordinates(BaseModel):
    lat: float
    lng: float

class Farm(BaseModel):
    id: str
    farmer_name: str
    phone: str
    village: str
    cluster: str  # e.g., "Karnal North", "Taraori", "Indri", "Nilokheri"
    location: Coordinates
    acres: float
    estimated_straw_tons: float
    harvest_time_hours: float  # Hours from T0 when harvesting finishes & straw is ready
    sowing_deadline_hours: float  # Hours from T0 when wheat sowing prep begins (deadline)
    moisture_pct: float = 14.0  # Safe threshold <= 20%
    status: str = "pending"  # pending, scheduled, in_progress, completed, disrupted, delayed
    raw_request_text: Optional[str] = None
    notes: Optional[str] = None
