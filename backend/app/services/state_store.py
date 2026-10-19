import copy
from typing import List, Optional
from app.models.state import SimulationState
from app.models.farm import Farm
from app.models.baler import Baler
from app.models.buyer import Buyer
from app.models.schedule import SchedulePlan
from app.models.disruption import DisruptionEvent, DisruptionType
from app.services.data_seeder import get_initial_state

class StateStore:
    """In-memory singleton state store for hackathon simulation."""

    def __init__(self):
        self._state: SimulationState = get_initial_state()

    def get_state(self) -> SimulationState:
        return self._state

    def reset(self) -> SimulationState:
        self._state = get_initial_state()
        return self._state

    def set_plan(self, plan: SchedulePlan) -> SimulationState:
        # If there's an existing plan, save it as previous_plan for diff comparisons
        if self._state.current_plan:
            self._state.previous_plan = copy.deepcopy(self._state.current_plan)
        self._state.current_plan = plan
        self._state.scenario = "replanned" if self._state.previous_plan else "scheduled"

        # Update farm statuses based on jobs
        assigned_farm_ids = {job.farm_id for job in plan.jobs}
        for farm in self._state.farms:
            if farm.id in assigned_farm_ids:
                farm.status = "scheduled"
            else:
                farm.status = "pending"

        return self._state

    def approve_current_plan(self) -> Optional[SchedulePlan]:
        if self._state.current_plan:
            self._state.current_plan.status = "approved"
            for job in self._state.current_plan.jobs:
                job.status = "approved"
            return self._state.current_plan
        return None

    def apply_disruption(self, disruption: DisruptionEvent) -> SimulationState:
        self._state.active_disruptions.append(disruption)
        self._state.scenario = "disrupted"

        # Handle Baler Breakdown
        if disruption.type == DisruptionType.BALER_BREAKDOWN:
            for baler in self._state.balers:
                if baler.id.lower() == disruption.target_id.lower():
                    baler.status = "broken_down"
                    baler.breakdown_time_hours = disruption.start_hour

            # Flag affected jobs in the current plan
            if self._state.current_plan:
                for job in self._state.current_plan.jobs:
                    if job.baler_id.lower() == disruption.target_id.lower() and job.end_hour > disruption.start_hour:
                        job.status = "disrupted"
                        job.disruption_note = f"Disrupted by {disruption.description}"

        # Handle Rain Event
        elif disruption.type == DisruptionType.RAIN:
            target_cluster = disruption.target_id.lower()
            for farm in self._state.farms:
                if target_cluster in ["all", farm.cluster.lower(), farm.village.lower()]:
                    farm.moisture_pct = 26.5  # Too damp to bale
                    farm.status = "delayed"

            if self._state.current_plan:
                for job in self._state.current_plan.jobs:
                    farm = next((f for f in self._state.farms if f.id == job.farm_id), None)
                    if farm and target_cluster in ["all", farm.cluster.lower(), farm.village.lower()]:
                        rain_end_h = disruption.start_hour + disruption.duration_hours + 6.0  # +6h drying buffer
                        if job.start_hour < rain_end_h:
                            job.status = "disrupted"
                            job.disruption_note = f"Rain delay: straw moisture high until hour {rain_end_h:.1f}"

        return self._state

    def add_farm(self, farm: Farm) -> SimulationState:
        # Check if ID already exists
        existing_idx = next((i for i, f in enumerate(self._state.farms) if f.id == farm.id), None)
        if existing_idx is not None:
            self._state.farms[existing_idx] = farm
        else:
            self._state.farms.append(farm)
        return self._state

state_store = StateStore()
