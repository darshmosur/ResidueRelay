import time
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def run_e2e():
    print(">>> Starting ResidueRelay Live End-to-End Smoke Test...")
    
    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Health Check Passed: Backend is online")

    # 2. Reset state
    res = requests.post(f"{BASE_URL}/state/reset")
    assert res.status_code == 200
    state = res.json()
    assert len(state["farms"]) == 15
    assert len(state["balers"]) == 3
    assert len(state["buyers"]) == 4
    print("[OK] State Reset: 15 farms, 3 balers, 4 buyers pre-seeded")

    # 3. Generate initial schedule
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/schedule/generate")
    t1 = time.time()
    assert res.status_code == 200
    plan_v1 = res.json()
    assert plan_v1["version"] == 1
    assert len(plan_v1["jobs"]) == 15
    assert plan_v1["status"] == "pending_approval"
    print(f"[OK] Initial Schedule Generated in {t1 - t0:.2f}s: 15/15 farms scheduled, {plan_v1['metrics']['total_straw_tons']} tons straw")

    # 4. Human-in-the-loop approval
    res = requests.post(f"{BASE_URL}/schedule/approve")
    assert res.status_code == 200
    assert res.json()["status"] == "approved"
    print("[OK] Plan v1 Approved: Field dispatch orders committed")

    # 5. Simulate Disruption: Dual Rain in Taraori + Baler 2 breakdown
    res = requests.post(f"{BASE_URL}/schedule/disrupt", json={"preset": "both"})
    assert res.status_code == 200
    state_disrupted = res.json()
    assert state_disrupted["scenario"] == "disrupted"
    assert len(state_disrupted["active_disruptions"]) == 2
    print("[OK] Disruption Triggered: Baler 2 offline + Taraori cluster rain delayed")

    # 6. Dynamic Replan with OR-Tools
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/schedule/replan")
    t1 = time.time()
    assert res.status_code == 200
    plan_v2 = res.json()
    assert plan_v2["version"] == 2
    assert plan_v2["status"] == "pending_approval"
    assert len(plan_v2["jobs"]) >= 14
    assert plan_v2["disruption_summary"] is not None
    print(f"[OK] Dynamic Replan Computed in {t1 - t0:.2f}s: Plan v2 with minimal churn and AI dispatch brief")

    # 7. Approve Plan v2
    res = requests.post(f"{BASE_URL}/schedule/approve")
    assert res.status_code == 200
    assert res.json()["status"] == "approved"
    print("[OK] Plan v2 Approved: Revised dispatch orders committed")

    # 8. Test AI Farmer Message Intake
    test_msg = "Mera naam Sukhdev Brar hai, Indri gaon me 14 acre dhaan combine se cut gaya. Kal subah baler chahiye."
    res = requests.post(f"{BASE_URL}/ai/parse-request", json={"text": test_msg})
    assert res.status_code == 200
    data = res.json()["extracted_data"]
    assert data["village"].lower() == "indri"
    assert data["acres"] == 14.0
    print(f"[OK] AI NLP Intake Parser Verified: Extracted {data['farmer_name']} ({data['acres']} acres in {data['village']})")

    # 9. Clean reset
    requests.post(f"{BASE_URL}/state/reset")
    print("[OK] State Reset back to clean baseline")
    print("\nALL LIVE END-TO-END VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        run_e2e()
    except Exception as e:
        print(f"[ERROR] Error during E2E verification: {e}")
        sys.exit(1)
