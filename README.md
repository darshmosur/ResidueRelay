# ResidueRelay: Autonomous Paddy Straw Logistics & Harvest Coordinator

ResidueRelay is a coordination and scheduling platform designed to solve the crop residue burning crisis in Northern India (Punjab & Haryana rice-wheat cropping system). By creating a synchronized, constraint-optimized harvest plan connecting farmers, machinery operators (balers), and bio-energy buyers, ResidueRelay ensures paddy straw is cleared and monetized on time before wheat sowing deadlines.

---

## Key Capabilities

1. **AI-Powered Farmer Intake**: Ingests unstructured voice notes and SMS messages in colloquial Hindi/Hinglish/Punjabi, extracting farm acreage, location, harvest completion time, and sowing deadlines.
2. **Constraint-Based Scheduling Engine**: Powered by **Google OR-Tools CP-SAT**, formulating multi-baler allocation, non-overlapping field intervals, daylight operating limits, travel times, and buyer intake quotas into an optimal dispatch schedule.
3. **Dynamic Disruption Replanning**: Instantly adapts to field realities (unseasonal rain spiking straw moisture, or machinery breakdowns) by re-optimizing assignments with minimal schedule churn.
4. **Human-in-the-Loop Approval**: Transparent before-and-after schedule diffs with clear AI dispatch summaries that operators can review and approve before field orders are finalized.

---

## Prototype Scope

- **15 Farms**: Located across Karnal District (Taraori, Nilokheri, Indri, and Central Karnal clusters).
- **3 Balers**: Custom Hiring Center square and round balers with defined throughputs and depot stations.
- **4 Buyers**: Industrial off-takers including Indri Bio-CNG Plant, Panipat Biomass Power Station, Karnal Paper Mill, and Kurukshetra Fodder Depot.

---

## Backend Architecture

```
backend/
├── app/
│   ├── models/           # Pydantic schemas (Farm, Baler, Buyer, Job, SchedulePlan, DisruptionEvent)
│   ├── services/
│   │   ├── data_seeder.py      # Pre-seeded 15 farms, 3 balers, 4 buyers
│   │   ├── distance_matrix.py  # Haversine distance and rural transit calculations
│   │   └── scheduler.py        # Google OR-Tools CP-SAT formulation and replanner
│   └── routers/          # FastAPI routes
└── tests/
    └── test_scheduler.py # Automated test suite for scheduling and disruption replanning
```

---

## Running Backend Tests

```bash
python -m pytest backend/tests -v
```
