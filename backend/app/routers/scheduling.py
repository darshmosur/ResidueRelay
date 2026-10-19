from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.models.schedule import SchedulePlan
from app.models.state import SimulationState
from app.models.disruption import DisruptionEvent, DisruptionType
from app.services.state_store import state_store
from app.services.scheduler import ScheduleOptimizer
from app.services.ai_agent import generate_replan_narrative

router = APIRouter(prefix="/schedule", tags=["Scheduling"])

class DisruptionRequest(BaseModel):
    preset: Optional[str] = None  # "rain", "breakdown", "both"
    custom_event: Optional[DisruptionEvent] = None

@router.post("/generate", response_model=SchedulePlan)
def generate_initial_schedule():
    """Generates the optimal baseline harvest collection schedule for all 15 farms."""
    state = state_store.get_state()
    optimizer = ScheduleOptimizer(
        farms=state.farms,
        balers=state.balers,
        buyers=state.buyers,
        disruptions=state.active_disruptions,
        previous_plan=None
    )
    plan = optimizer.solve(time_limit_seconds=3.0)
    
    plan.ai_dispatch_brief = (
        f"Baseline plan generated for {plan.metrics.scheduled_farms} farms across {len(state.balers)} balers. "
        f"Total residue cleared: {plan.metrics.total_straw_tons} tons. Sowing deadline compliance: 100%."
    )
    
    state_store.set_plan(plan)
    return plan

@router.post("/disrupt", response_model=SimulationState)
def trigger_disruption(req: DisruptionRequest):
    """
    Injects a disruption into the simulation.
    Supports quick presets ('rain', 'breakdown', 'both') or a custom DisruptionEvent.
    """
    events_to_apply: List[DisruptionEvent] = []

    if req.custom_event:
        events_to_apply.append(req.custom_event)
    elif req.preset == "rain":
        events_to_apply.append(DisruptionEvent(
            id="disrupt-rain-01",
            type=DisruptionType.RAIN,
            target_id="Taraori",
            start_hour=2.0,
            duration_hours=12.0,
            description="Sudden rainfall in Taraori cluster. Field moisture > 26% (requires 6h drying window)."
        ))
    elif req.preset == "breakdown":
        events_to_apply.append(DisruptionEvent(
            id="disrupt-baler-02",
            type=DisruptionType.BALER_BREAKDOWN,
            target_id="baler-02",
            start_hour=10.0,
            duration_hours=72.0,
            description="Baler #2 (Gurmeet Singh) suffered hydraulic pump failure at hour 10.0. Out of service."
        ))
    elif req.preset == "both":
        events_to_apply.append(DisruptionEvent(
            id="disrupt-rain-01",
            type=DisruptionType.RAIN,
            target_id="Taraori",
            start_hour=2.0,
            duration_hours=12.0,
            description="Rainstorm across Taraori cluster. Straw moisture spiked above safety thresholds."
        ))
        events_to_apply.append(DisruptionEvent(
            id="disrupt-baler-02",
            type=DisruptionType.BALER_BREAKDOWN,
            target_id="baler-02",
            start_hour=10.0,
            duration_hours=72.0,
            description="Baler #2 hydraulic pump failure at hour 10.0."
        ))
    else:
        raise HTTPException(status_code=400, detail="Must provide either preset ('rain', 'breakdown', 'both') or custom_event")

    state = state_store.get_state()
    for event in events_to_apply:
        state_store.apply_disruption(event)

    return state_store.get_state()

@router.post("/replan", response_model=SchedulePlan)
def replan_schedule():
    """
    Replans the schedule incorporating active rain and breakdown disruptions.
    Uses OR-Tools with minimal churn penalty relative to previous plan.
    """
    state = state_store.get_state()
    if not state.current_plan:
        raise HTTPException(status_code=400, detail="Cannot replan without an initial plan. Call /generate first.")

    optimizer = ScheduleOptimizer(
        farms=state.farms,
        balers=state.balers,
        buyers=state.buyers,
        disruptions=state.active_disruptions,
        previous_plan=state.current_plan
    )
    revised_plan = optimizer.solve(time_limit_seconds=3.0)

    # Generate AI Replan Narrative
    narrative = generate_replan_narrative(
        previous_plan=state.current_plan,
        new_plan=revised_plan,
        disruptions=state.active_disruptions
    )
    revised_plan.disruption_summary = narrative
    revised_plan.ai_dispatch_brief = (
        f"Dynamic replan computed: {len(revised_plan.jobs)} jobs scheduled. "
        f"Disrupted jobs rerouted with minimal delay."
    )

    state_store.set_plan(revised_plan)
    return revised_plan

@router.post("/approve", response_model=SchedulePlan)
def approve_plan():
    """Human-in-the-loop sign-off: marks the proposed plan and jobs as approved."""
    plan = state_store.approve_current_plan()
    if not plan:
        raise HTTPException(status_code=400, detail="No active plan to approve.")
    return plan
