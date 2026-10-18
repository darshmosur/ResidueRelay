from pydantic import BaseModel
from typing import List, Optional
from app.models.farm import Farm
from app.models.baler import Baler
from app.models.buyer import Buyer
from app.models.schedule import SchedulePlan
from app.models.disruption import DisruptionEvent

class SimulationState(BaseModel):
    scenario: str = "initial"  # "initial", "scheduled", "disrupted", "replanned"
    farms: List[Farm]
    balers: List[Baler]
    buyers: List[Buyer]
    current_plan: Optional[SchedulePlan] = None
    previous_plan: Optional[SchedulePlan] = None
    active_disruptions: List[DisruptionEvent] = []
