import pytest
from app.services.data_seeder import seed_farms, seed_balers, seed_buyers, get_initial_state
from app.services.distance_matrix import haversine_distance_km, calculate_travel_time_hours
from app.services.scheduler import ScheduleOptimizer
from app.models.disruption import DisruptionEvent, DisruptionType
from app.models.farm import Coordinates

def test_data_seeder_counts():
    """Verify standard demo dataset counts."""
    state = get_initial_state()
    assert len(state.farms) == 15, "Should have exactly 15 farms"
    assert len(state.balers) == 3, "Should have exactly 3 balers"
    assert len(state.buyers) == 4, "Should have exactly 4 buyers"
    assert sum(f.acres for f in state.farms) > 100, "Total acres should be > 100"

def test_distance_matrix():
    """Verify distance and travel calculations."""
    coord_taraori = Coordinates(lat=29.805, lng=76.924)
    coord_nilokheri = Coordinates(lat=29.835, lng=76.912)

    dist_km = haversine_distance_km(coord_taraori, coord_nilokheri)
    assert 2.0 < dist_km < 6.0, f"Distance should be ~3.5 km, got {dist_km}"

    travel_hours = calculate_travel_time_hours(coord_taraori, coord_nilokheri)
    assert 0.2 < travel_hours < 0.6, f"Travel time should be ~20 mins, got {travel_hours} hrs"

def test_initial_schedule_generation():
    """Verify OR-Tools generates a feasible, optimal initial plan for all 15 farms."""
    farms = seed_farms()
    balers = seed_balers()
    buyers = seed_buyers()

    optimizer = ScheduleOptimizer(farms=farms, balers=balers, buyers=buyers)
    plan = optimizer.solve(time_limit_seconds=3.0)

    assert plan is not None
    assert plan.version == 1
    assert len(plan.jobs) == 15, f"All 15 farms should be scheduled, got {len(plan.jobs)}"
    assert len(plan.unassigned_farms) == 0, f"Unassigned farms should be 0, got {plan.unassigned_farms}"

    # Verify no two jobs overlap on the same baler
    for b in balers:
        baler_jobs = [j for j in plan.jobs if j.baler_id == b.id]
        baler_jobs.sort(key=lambda j: j.start_hour)
        for idx in range(len(baler_jobs) - 1):
            curr_job = baler_jobs[idx]
            next_job = baler_jobs[idx + 1]
            assert curr_job.end_hour <= next_job.start_hour, (
                f"Overlap detected on {b.id}: Job {curr_job.id} ends at {curr_job.end_hour} "
                f"but Job {next_job.id} starts at {next_job.start_hour}"
            )

    # Verify each job starts after the farm's harvest time
    for job in plan.jobs:
        farm = next(f for f in farms if f.id == job.farm_id)
        assert job.start_hour >= farm.harvest_time_hours - 0.01, (
            f"Job {job.id} starts at {job.start_hour} before harvest ready {farm.harvest_time_hours}"
        )

    # Verify metrics
    assert plan.metrics.scheduled_farms == 15
    assert plan.metrics.total_straw_tons > 200
    assert plan.metrics.co2_avoided_tons > 300

def test_rain_disruption_replanning():
    """
    Test scenario: Rain hits the Taraori cluster from hour 2 to hour 14.
    Farms in Taraori cannot be baled until at least 20 hours (14 + 6 hr drying).
    """
    farms = seed_farms()
    balers = seed_balers()
    buyers = seed_buyers()

    # Initial plan
    base_plan = ScheduleOptimizer(farms=farms, balers=balers, buyers=buyers).solve()
    assert len(base_plan.jobs) == 15

    # Introduce Rain in Taraori
    rain_event = DisruptionEvent(
        id="disrupt-rain-01",
        type=DisruptionType.RAIN,
        target_id="Taraori",
        start_hour=2.0,
        duration_hours=12.0,
        description="Heavy monsoon showers in Taraori cluster. Straw moisture spiked above 25%."
    )

    replan_optimizer = ScheduleOptimizer(
        farms=farms,
        balers=balers,
        buyers=buyers,
        disruptions=[rain_event],
        previous_plan=base_plan
    )
    revised_plan = replan_optimizer.solve(time_limit_seconds=3.0)

    assert revised_plan is not None
    assert revised_plan.version == 2
    assert len(revised_plan.jobs) == 15

    # All Taraori farms must start at or after 20.0 hours (2 + 12 + 6)
    taraori_farm_ids = [f.id for f in farms if f.cluster.lower() == "taraori"]
    for job in revised_plan.jobs:
        if job.farm_id in taraori_farm_ids:
            assert job.start_hour >= 19.99, (
                f"Taraori job {job.farm_id} scheduled at {job.start_hour} hrs, "
                f"must be >= 20.0 hrs due to rain + drying buffer"
            )

def test_baler_breakdown_replanning():
    """
    Test scenario: Baler 2 breaks down at hour 10.
    All jobs originally on Baler 2 after hour 10 must be reassigned to Baler 1 or 3.
    """
    farms = seed_farms()
    balers = seed_balers()
    buyers = seed_buyers()

    # Initial plan
    base_plan = ScheduleOptimizer(farms=farms, balers=balers, buyers=buyers).solve()

    # Introduce Baler 2 Breakdown
    breakdown_event = DisruptionEvent(
        id="disrupt-baler-02",
        type=DisruptionType.BALER_BREAKDOWN,
        target_id="baler-02",
        start_hour=10.0,
        duration_hours=72.0,
        description="Hydraulic pump failure on Baler #2. Out of service for 3 days."
    )

    replan_optimizer = ScheduleOptimizer(
        farms=farms,
        balers=balers,
        buyers=buyers,
        disruptions=[breakdown_event],
        previous_plan=base_plan
    )
    revised_plan = replan_optimizer.solve(time_limit_seconds=3.0)

    assert revised_plan is not None
    # No jobs on baler-02 should run after hour 10.0
    for job in revised_plan.jobs:
        if job.baler_id == "baler-02":
            assert job.end_hour <= 10.01, (
                f"Baler 2 has job {job.farm_id} ending at {job.end_hour} after breakdown at hour 10.0"
            )

    # Most or all farms should still be scheduled by rerouting to Baler 1 and Baler 3
    assert len(revised_plan.jobs) >= 14, f"Should reschedule almost all farms, got {len(revised_plan.jobs)}"
