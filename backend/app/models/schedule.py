from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.job import Job

class ScheduleMetrics(BaseModel):
    total_farms: int
    scheduled_farms: int
    unassigned_farms_count: int
    total_acres: float
    total_straw_tons: float
    avg_delay_hours: float
    max_delay_hours: float
    burning_risk_count: int  # Farms that exceed deadline
    burning_risk_pct: float
    co2_avoided_tons: float  # Stubble burning emits ~1.5 tons CO2 eq per ton of straw

class SchedulePlan(BaseModel):
    plan_id: str
    version: int = 1
    status: str = "pending_approval"  # pending_approval, approved, superseded
    created_at_iso: str
    jobs: List[Job]
    unassigned_farms: List[str] = []
    metrics: ScheduleMetrics
    ai_dispatch_brief: Optional[str] = None
    disruption_summary: Optional[str] = None
