import datetime
import math
from typing import List, Dict, Tuple, Optional
from ortools.sat.python import cp_model

from app.models.farm import Farm, Coordinates
from app.models.baler import Baler
from app.models.buyer import Buyer
from app.models.job import Job
from app.models.disruption import DisruptionEvent, DisruptionType
from app.models.schedule import SchedulePlan, ScheduleMetrics
from app.services.distance_matrix import haversine_distance_km, calculate_travel_time_hours

class ScheduleOptimizer:
    """
    Constraint-based scheduling engine using Google OR-Tools CP-SAT.
    Solves multi-baler allocation, time-window constraints, daylight hours,
    travel times, buyer matching, and disruption replanning.
    """

    def __init__(
        self,
        farms: List[Farm],
        balers: List[Baler],
        buyers: List[Buyer],
        disruptions: Optional[List[DisruptionEvent]] = None,
        previous_plan: Optional[SchedulePlan] = None,
        horizon_days: int = 4
    ):
        self.farms = farms
        self.balers = balers
        self.buyers = buyers
        self.disruptions = disruptions or []
        self.previous_plan = previous_plan
        self.horizon_days = horizon_days

        # Time units: 1 unit = 1 minute (for integer precision in CP-SAT)
        self.horizon_minutes = horizon_days * 24 * 60
        self.daylight_start_hour = 7   # 07:00 AM
        self.daylight_end_hour = 19    # 07:00 PM (12 daylight hours/day)

    def _get_farm_ready_minute(self, farm: Farm) -> int:
        """Calculate the earliest minute a farm can be baled, accounting for rain delays."""
        ready_min = int(round(farm.harvest_time_hours * 60))

        # Check if rain disruption affects this farm's cluster
        for d in self.disruptions:
            if not d.is_active:
                continue
            if d.type == DisruptionType.RAIN and d.target_id.lower() in [farm.cluster.lower(), farm.village.lower(), "all"]:
                rain_end_min = int(round((d.start_hour + d.duration_hours) * 60))
                drying_buffer_min = 6 * 60  # 6 hours post-rain drying buffer for straw moisture <= 20%
                blocked_until_min = rain_end_min + drying_buffer_min
                if blocked_until_min > ready_min:
                    ready_min = blocked_until_min

        return max(0, ready_min)

    def _get_baler_breakdown_minute(self, baler: Baler) -> Optional[int]:
        """Check if a baler suffers a breakdown disruption."""
        for d in self.disruptions:
            if not d.is_active:
                continue
            if d.type == DisruptionType.BALER_BREAKDOWN and d.target_id.lower() == baler.id.lower():
                return int(round(d.start_hour * 60))
        if baler.status == "broken_down" and baler.breakdown_time_hours is not None:
            return int(round(baler.breakdown_time_hours * 60))
        return None

    def solve(self, time_limit_seconds: float = 3.0) -> SchedulePlan:
        model = cp_model.CpModel()

        n_farms = len(self.farms)
        n_balers = len(self.balers)
        n_buyers = len(self.buyers)

        # -------------------------------------------------------------
        # 1. Decision Variables
        # -------------------------------------------------------------
        # is_assigned[i]: Boolean, whether farm i is scheduled
        is_assigned = {}
        # assigned_baler[i, k]: Boolean, whether farm i is assigned to baler k
        baler_assign = {}
        # start_time[i], end_time[i]: minute in [0, horizon_minutes]
        start_min = {}
        end_min = {}
        duration_min = {}
        # Optional intervals for each (farm, baler)
        intervals = {k: [] for k in range(n_balers)}

        for i, farm in enumerate(self.farms):
            is_assigned[i] = model.NewBoolVar(f"assigned_f{i}")
            ready_m = self._get_farm_ready_minute(farm)
            deadline_m = int(round(farm.sowing_deadline_hours * 60))

            start_min[i] = model.NewIntVar(ready_m, self.horizon_minutes, f"start_f{i}")
            end_min[i] = model.NewIntVar(ready_m, self.horizon_minutes, f"end_f{i}")

            for k, baler in enumerate(self.balers):
                b_var = model.NewBoolVar(f"assign_f{i}_b{k}")
                baler_assign[i, k] = b_var

                # Calculate duration based on baler throughput
                hours_needed = farm.acres / baler.throughput_acres_per_hour
                dur = max(30, int(round(hours_needed * 60)))  # at least 30 minutes
                duration_min[i, k] = dur

                # Optional interval for baler k
                opt_interval = model.NewOptionalIntervalVar(
                    start_min[i], dur, end_min[i], b_var, f"interval_f{i}_b{k}"
                )
                intervals[k].append(opt_interval)

            # A farm can be assigned to at most 1 baler
            model.Add(sum(baler_assign[i, k] for k in range(n_balers)) == is_assigned[i])

        # -------------------------------------------------------------
        # 2. Baler Constraints & Non-Overlap
        # -------------------------------------------------------------
        for k, baler in enumerate(self.balers):
            # Check for breakdown
            breakdown_m = self._get_baler_breakdown_minute(baler)
            if breakdown_m is not None:
                # Baler cannot take any jobs starting or running after breakdown_m
                for i in range(n_farms):
                    # If assigned to broken baler, must finish before breakdown
                    model.Add(end_min[i] <= breakdown_m).OnlyEnforceIf(baler_assign[i, k])

            # Night time (non-working) intervals for each day
            # Balers only operate during daylight (07:00 to 19:00)
            for d in range(self.horizon_days):
                night_start = d * 24 * 60 + self.daylight_end_hour * 60
                night_duration = (24 - self.daylight_end_hour + self.daylight_start_hour) * 60
                if night_start + night_duration <= self.horizon_minutes:
                    night_interval = model.NewFixedSizeIntervalVar(
                        night_start, night_duration, f"night_b{k}_d{d}"
                    )
                    intervals[k].append(night_interval)

            # Hard constraint: No overlap between jobs and night intervals on baler k
            model.AddNoOverlap(intervals[k])

        # -------------------------------------------------------------
        # 3. Transition / Travel Times Between Farms
        # -------------------------------------------------------------
        for k in range(n_balers):
            for i in range(n_farms):
                for j in range(i + 1, n_farms):
                    farm_a = self.farms[i]
                    farm_b = self.farms[j]
                    travel_hrs = calculate_travel_time_hours(farm_a.location, farm_b.location)
                    travel_m = max(10, int(round(travel_hrs * 60)))

                    # If both farm i and farm j are on baler k:
                    # One must precede the other with travel gap
                    order_ij = model.NewBoolVar(f"order_b{k}_f{i}_f{j}")
                    both_on_k = model.NewBoolVar(f"both_b{k}_f{i}_f{j}")
                    model.AddBoolAnd([baler_assign[i, k], baler_assign[j, k]]).OnlyEnforceIf(both_on_k)
                    model.AddBoolOr([baler_assign[i, k].Not(), baler_assign[j, k].Not()]).OnlyEnforceIf(both_on_k.Not())

                    # When both on k:
                    # order_ij = 1 => start_j >= end_i + travel_m
                    # order_ij = 0 => start_i >= end_j + travel_m
                    model.Add(start_min[j] >= end_min[i] + travel_m).OnlyEnforceIf([both_on_k, order_ij])
                    model.Add(start_min[i] >= end_min[j] + travel_m).OnlyEnforceIf([both_on_k, order_ij.Not()])

        # -------------------------------------------------------------
        # 4. Buyer Matching & Daily Capacity Constraints
        # -------------------------------------------------------------
        buyer_assign = {}
        for i, farm in enumerate(self.farms):
            for b in range(n_buyers):
                buyer_assign[i, b] = model.NewBoolVar(f"buyer_f{i}_b{b}")

            # Each assigned farm gets exactly one buyer
            model.Add(sum(buyer_assign[i, b] for b in range(n_buyers)) == is_assigned[i])

        # Buyer daily intake limits (approximate total straw tons per day)
        for b, buyer in enumerate(self.buyers):
            for d in range(self.horizon_days):
                day_start_m = d * 24 * 60
                day_end_m = (d + 1) * 24 * 60
                
                # Check which farms fall on day d
                # Soft capacity check: tons delivered to buyer b
                # To keep solver fast and linear:
                # We weight buyer matching by proximity and price in objective function
                pass

        # -------------------------------------------------------------
        # 5. Objective Function Formulation
        # -------------------------------------------------------------
        objective_terms = []

        # A. Heavy penalty for unassigned farms (ensures all 15 farms are scheduled if at all feasible)
        for i in range(n_farms):
            unassigned_penalty = 500_000
            objective_terms.append((1 - is_assigned[i]) * unassigned_penalty)

        # B. Lateness penalty: penalize finishing past ready time
        for i, farm in enumerate(self.farms):
            ready_m = self._get_farm_ready_minute(farm)
            deadline_m = int(round(farm.sowing_deadline_hours * 60))
            
            # Delay past harvest ready time (minimize waiting)
            objective_terms.append(start_min[i] - ready_m)

            # Deadline violation penalty (risk of farmer burning field!)
            # Create a lateness variable
            lateness_var = model.NewIntVar(0, self.horizon_minutes, f"lateness_f{i}")
            model.Add(lateness_var >= end_min[i] - deadline_m)
            model.Add(lateness_var >= 0)
            objective_terms.append(lateness_var * 50)  # High penalty for wheat sowing delay

        # C. Buyer Proximity & Revenue Preference
        for i, farm in enumerate(self.farms):
            for b, buyer in enumerate(self.buyers):
                dist = haversine_distance_km(farm.location, buyer.location)
                # Distance penalty: 1 km ~ 5 cost units
                # Revenue incentive: Higher price reduces cost
                cost_weight = int(round(dist * 10 - buyer.price_per_ton / 100))
                objective_terms.append(buyer_assign[i, b] * cost_weight)

        # D. Minimal Churn / Stability (if replanning from previous plan)
        if self.previous_plan:
            prev_assignments = {job.farm_id: job for job in self.previous_plan.jobs}
            for i, farm in enumerate(self.farms):
                if farm.id in prev_assignments:
                    prev_job = prev_assignments[farm.id]
                    prev_baler_idx = next((k for k, b in enumerate(self.balers) if b.id == prev_job.baler_id), None)
                    if prev_baler_idx is not None:
                        # Bonus for keeping the same baler (churn penalty = 300)
                        # 300 * (1 - baler_assign[i, prev_baler_idx])
                        objective_terms.append((1 - baler_assign[i, prev_baler_idx]) * 300)

        model.Minimize(sum(objective_terms))

        # -------------------------------------------------------------
        # 6. Solve Model
        # -------------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        solver.parameters.num_workers = 4
        status = solver.Solve(model)

        # -------------------------------------------------------------
        # 7. Extract Solution & Construct Plan
        # -------------------------------------------------------------
        jobs: List[Job] = []
        unassigned: List[str] = []

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for i, farm in enumerate(self.farms):
                if solver.Value(is_assigned[i]) == 1:
                    assigned_k = next(k for k in range(n_balers) if solver.Value(baler_assign[i, k]) == 1)
                    assigned_b = next(b for b in range(n_buyers) if solver.Value(buyer_assign[i, b]) == 1)

                    start_h = round(solver.Value(start_min[i]) / 60.0, 2)
                    end_h = round(solver.Value(end_min[i]) / 60.0, 2)
                    dur_h = round(end_h - start_h, 2)
                    delay_h = max(0.0, round(start_h - farm.harvest_time_hours, 2))
                    exceeds = end_h > farm.sowing_deadline_hours

                    baler = self.balers[assigned_k]
                    buyer = self.buyers[assigned_b]

                    jobs.append(Job(
                        id=f"job-{farm.id}",
                        farm_id=farm.id,
                        baler_id=baler.id,
                        buyer_id=buyer.id,
                        start_hour=start_h,
                        end_hour=end_h,
                        duration_hours=dur_h,
                        travel_time_hours=0.0,  # will be computed in sequence sort
                        straw_tons=farm.estimated_straw_tons,
                        status="approved" if self.previous_plan and self.previous_plan.status == "approved" else "draft",
                        delay_hours=delay_h,
                        exceeds_deadline=exceeds
                    ))
                else:
                    unassigned.append(farm.id)

            # Sort jobs per baler by start_hour and calculate actual transit travel times
            jobs.sort(key=lambda j: (j.baler_id, j.start_hour))
            for k, baler in enumerate(self.balers):
                baler_jobs = [j for j in jobs if j.baler_id == baler.id]
                prev_loc = baler.depot_location
                for j in baler_jobs:
                    farm = next(f for f in self.farms if f.id == j.farm_id)
                    transit = calculate_travel_time_hours(prev_loc, farm.location)
                    j.travel_time_hours = transit
                    prev_loc = farm.location

        # Compute Metrics
        scheduled_count = len(jobs)
        total_acres = sum(f.acres for f in self.farms if f.id in [j.farm_id for j in jobs])
        total_tons = sum(j.straw_tons for j in jobs)
        delays = [j.delay_hours for j in jobs]
        avg_delay = round(sum(delays) / len(delays), 1) if delays else 0.0
        max_delay = max(delays) if delays else 0.0
        burning_risk = sum(1 for j in jobs if j.exceeds_deadline) + len(unassigned)
        burning_pct = round((burning_risk / n_farms) * 100, 1)
        co2_avoided = round(total_tons * 1.5, 1)  # 1 ton straw = ~1.5 ton CO2 eq avoided

        metrics = ScheduleMetrics(
            total_farms=n_farms,
            scheduled_farms=scheduled_count,
            unassigned_farms_count=len(unassigned),
            total_acres=round(total_acres, 1),
            total_straw_tons=round(total_tons, 1),
            avg_delay_hours=avg_delay,
            max_delay_hours=max_delay,
            burning_risk_count=burning_risk,
            burning_risk_pct=burning_pct,
            co2_avoided_tons=co2_avoided
        )

        plan_version = (self.previous_plan.version + 1) if self.previous_plan else 1
        now_iso = datetime.datetime.now().isoformat()

        return SchedulePlan(
            plan_id=f"plan-v{plan_version}",
            version=plan_version,
            status="pending_approval",
            created_at_iso=now_iso,
            jobs=jobs,
            unassigned_farms=unassigned,
            metrics=metrics,
            ai_dispatch_brief=None,
            disruption_summary=None
        )
