import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Fresh client for API testing
    with TestClient(app) as c:
        c.post("/api/state/reset")
        yield c

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_get_initial_state(client):
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.json()
    assert len(data["farms"]) == 15
    assert len(data["balers"]) == 3
    assert len(data["buyers"]) == 4
    assert data["scenario"] == "initial"
    assert data["current_plan"] is None

def test_full_simulation_flow(client):
    """
    End-to-end integration test of the key hackathon demo flow:
    1. Generate initial schedule
    2. Approve initial schedule
    3. Inject Baler Breakdown & Rain disruptions
    4. Replan affected jobs
    5. Verify AI summary & constraints
    6. Approve revised plan
    """
    # Step 1: Generate initial schedule
    gen_res = client.post("/api/schedule/generate")
    assert gen_res.status_code == 200
    plan_v1 = gen_res.json()
    assert plan_v1["version"] == 1
    assert len(plan_v1["jobs"]) == 15
    assert plan_v1["status"] == "pending_approval"

    # Step 2: Approve initial schedule
    app_res = client.post("/api/schedule/approve")
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "approved"

    # Step 3: Inject disruption (Breakdown of Baler 2)
    disrupt_res = client.post("/api/schedule/disrupt", json={"preset": "breakdown"})
    assert disrupt_res.status_code == 200
    state_disrupted = disrupt_res.json()
    assert state_disrupted["scenario"] == "disrupted"
    assert len(state_disrupted["active_disruptions"]) == 1
    
    # Verify Baler 2 is marked broken_down
    baler_2 = next(b for b in state_disrupted["balers"] if b["id"] == "baler-02")
    assert baler_2["status"] == "broken_down"

    # Step 4: Replan schedule
    replan_res = client.post("/api/schedule/replan")
    assert replan_res.status_code == 200
    plan_v2 = replan_res.json()
    assert plan_v2["version"] == 2
    assert plan_v2["status"] == "pending_approval"
    assert plan_v2["disruption_summary"] is not None
    assert "Dynamic Schedule Replanning Report" in plan_v2["disruption_summary"]

    # Verify no jobs on Baler 2 after breakdown hour (10.0)
    for j in plan_v2["jobs"]:
        if j["baler_id"] == "baler-02":
            assert j["end_hour"] <= 10.01

    # Step 5: Approve revised plan
    app2_res = client.post("/api/schedule/approve")
    assert app2_res.status_code == 200
    assert app2_res.json()["status"] == "approved"

def test_ai_farmer_intake_parser(client):
    """Test AI extraction from informal/Hinglish farmer input."""
    sample_text = "Mera naam Harpreet Singh hai, Nadana gaon me 9 kille dhaan cut gaya hai. Parso tak straw uthva do."
    res = client.post("/api/ai/parse-request", json={"text": sample_text})
    assert res.status_code == 200
    data = res.json()["extracted_data"]

    assert data["village"].lower() == "nadana"
    assert data["acres"] == 9.0
    assert data["estimated_straw_tons"] > 18.0
    assert data["farmer_name"] == "Harpreet Singh"
