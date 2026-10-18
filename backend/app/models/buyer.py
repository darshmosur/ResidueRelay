from pydantic import BaseModel, Field
from typing import Optional
from app.models.farm import Coordinates

class Buyer(BaseModel):
    id: str
    name: str
    buyer_type: str  # bio_cng, power_plant, paper_mill, fodder_hub
    location: Coordinates
    daily_intake_capacity_tons: float  # Maximum daily capacity
    price_per_ton: float  # ₹ per ton of straw
    current_allocated_tons: float = 0.0
    contact_person: Optional[str] = None
    notes: Optional[str] = None
