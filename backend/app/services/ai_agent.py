import json
import re
import requests
from typing import Dict, Any, Optional, List
from app.config import settings
from app.models.farm import Farm, Coordinates
from app.models.schedule import SchedulePlan
from app.models.disruption import DisruptionEvent

KNOWN_VILLAGES: Dict[str, Dict[str, Any]] = {
    "taraori": {"lat": 29.805, "lng": 76.924, "cluster": "Taraori"},
    "nadana": {"lat": 29.792, "lng": 76.915, "cluster": "Taraori"},
    "sultanpur": {"lat": 29.821, "lng": 76.905, "cluster": "Taraori"},
    "nilokheri": {"lat": 29.835, "lng": 76.912, "cluster": "Nilokheri"},
    "pujam": {"lat": 29.845, "lng": 76.930, "cluster": "Nilokheri"},
    "samana": {"lat": 29.855, "lng": 76.945, "cluster": "Nilokheri"},
    "anjanthali": {"lat": 29.838, "lng": 76.885, "cluster": "Nilokheri"},
    "indri": {"lat": 29.882, "lng": 77.062, "cluster": "Indri"},
    "bhadaur": {"lat": 29.870, "lng": 77.045, "cluster": "Indri"},
    "khanpur": {"lat": 29.895, "lng": 77.080, "cluster": "Indri"},
    "ghir": {"lat": 29.860, "lng": 77.030, "cluster": "Indri"},
    "uchana": {"lat": 29.725, "lng": 76.968, "cluster": "Karnal Central"},
    "kunjpura": {"lat": 29.712, "lng": 77.085, "cluster": "Karnal Central"},
    "gharaunda": {"lat": 29.542, "lng": 76.972, "cluster": "Karnal Central"},
    "karnal": {"lat": 29.685, "lng": 76.990, "cluster": "Karnal Central"},
}

def parse_farmer_request_fallback(text: str) -> Dict[str, Any]:
    """
    Robust rule-based parser for Indian colloquial/Hinglish farmer messages.
    Extracts acres (or kille), village/location, name, and timing.
    """
    clean_text = text.lower()

    # 1. Extract Acres / Kille
    # Matches: '8 acre', '8.5 acres', '8 kille', '10 killa', '8.0 kille'
    acres = 5.0  # default
    acre_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:acre|acres|kille|killa|kila|kile)', clean_text)
    if acre_match:
        try:
            acres = float(acre_match.group(1))
        except ValueError:
            acres = 5.0
    else:
        # Generic number lookup if near straw or dhaan
        num_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ke\s*paas|par|me|area)', clean_text)
        if num_match:
            try:
                acres = float(num_match.group(1))
            except ValueError:
                pass

    # 2. Extract Village / Location
    matched_village = "Karnal"
    matched_info = KNOWN_VILLAGES["karnal"]
    for village, info in KNOWN_VILLAGES.items():
        if village in clean_text:
            matched_village = village.capitalize()
            matched_info = info
            break

    # 3. Extract Farmer Name
    # Matches: 'Mera naam X', 'X from Y', 'X se', 'X bol raha hu'
    farmer_name = "Farmer Partner"
    name_patterns = [
        r'(?:naam|name)\s*(?:hai|is)?\s*([a-zA-Z]+(?:\s+[a-zA-Z]+)?)',
        r'([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s*(?:from|se|bol\s*raha)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            if candidate.lower() not in ["mera", "gaon", "farm", "khet", "dhaan", "taraori", "indri", "nilokheri"]:
                farmer_name = candidate
                break

    # 4. Harvest and Deadline Estimates
    harvest_hours = 0.0
    if "kal" in clean_text or "tomorrow" in clean_text:
        harvest_hours = 12.0
    elif "parso" in clean_text or "day after" in clean_text:
        harvest_hours = 24.0
    elif "aaj" in clean_text or "today" in clean_text or "cut chuka" in clean_text:
        harvest_hours = 0.0

    deadline_hours = harvest_hours + 48.0  # standard 48h wheat sowing prep buffer
    if "jaldi" in clean_text or "urgent" in clean_text:
        deadline_hours = harvest_hours + 36.0

    straw_tons = round(acres * 2.25, 1)

    return {
        "farmer_name": farmer_name,
        "village": matched_village,
        "cluster": matched_info["cluster"],
        "lat": matched_info["lat"],
        "lng": matched_info["lng"],
        "acres": acres,
        "estimated_straw_tons": straw_tons,
        "harvest_time_hours": harvest_hours,
        "sowing_deadline_hours": deadline_hours,
        "phone": "+91 98000 00000",
        "notes": f"Auto-parsed from farmer intake: '{text[:80]}...'"
    }

def parse_farmer_request_llm(text: str) -> Dict[str, Any]:
    """Uses Gemini API to parse natural language farmer requests with fallback."""
    if not settings.GEMINI_API_KEY:
        return parse_farmer_request_fallback(text)

    prompt = f"""
You are an agricultural AI dispatch assistant for ResidueRelay in Haryana/Punjab, India.
Parse the following farmer SMS/voice message into structured JSON.
Message: "{text}"

Target Villages: Taraori, Nilokheri, Indri, Gharaunda, Nadana, Pujam, Uchana, Kunjpura.
Note: 1 killa = 1 acre. If not specified, default acres to 6.0.
Output ONLY valid JSON with no markdown wrapping:
{{
  "farmer_name": string,
  "village": string,
  "cluster": string,
  "lat": float,
  "lng": float,
  "acres": float,
  "estimated_straw_tons": float,
  "harvest_time_hours": float,
  "sowing_deadline_hours": float,
  "phone": string,
  "notes": string
}}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        res = requests.post(url, json=payload, timeout=4.0)
        if res.status_code == 200:
            data = res.json()
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_json)
        else:
            return parse_farmer_request_fallback(text)
    except Exception:
        return parse_farmer_request_fallback(text)

def generate_replan_narrative(
    previous_plan: Optional[SchedulePlan],
    new_plan: SchedulePlan,
    disruptions: List[DisruptionEvent]
) -> str:
    """
    Generates an executive briefing explaining how the system replanned jobs
    in response to rain or equipment breakdowns.
    """
    # Analyze changes
    disruption_notes = []
    for d in disruptions:
        if d.is_active:
            disruption_notes.append(f"• **{d.type.value.upper()}** on `{d.target_id}`: {d.description}")

    # Compare assignments
    reassigned_jobs = []
    if previous_plan:
        prev_map = {j.farm_id: j for j in previous_plan.jobs}
        for j in new_plan.jobs:
            if j.farm_id in prev_map:
                p = prev_map[j.farm_id]
                if p.baler_id != j.baler_id:
                    reassigned_jobs.append(f"- **Farm `{j.farm_id}`** shifted from `{p.baler_id}` to `{j.baler_id}` (Start: hour {j.start_hour:.1f})")
                elif abs(p.start_hour - j.start_hour) >= 2.0:
                    reassigned_jobs.append(f"- **Farm `{j.farm_id}`** deferred by {j.start_hour - p.start_hour:+.1f} hrs (Straw drying / sequence optimization)")

    narrative = []
    narrative.append("### 🌾 Dynamic Schedule Replanning Report")
    narrative.append(f"**Plan Version:** `v{new_plan.version}` | **Status:** `Pending Human Approval`\n")

    if disruption_notes:
        narrative.append("#### Active Disruption Triggers")
        narrative.extend(disruption_notes)
        narrative.append("")

    narrative.append("#### Operational Impact Summary")
    narrative.append(f"- **Scheduled Farms:** {new_plan.metrics.scheduled_farms} / {new_plan.metrics.total_farms} ({new_plan.metrics.total_straw_tons} tons straw)")
    narrative.append(f"- **Average Harvest-to-Collection Delay:** {new_plan.metrics.avg_delay_hours} hours")
    narrative.append(f"- **Wheat Sowing Deadlines Protected:** {100.0 - new_plan.metrics.burning_risk_pct:.1f}% compliance")
    narrative.append(f"- **Estimated CO₂ Emissions Prevented:** {new_plan.metrics.co2_avoided_tons} tons")
    narrative.append("")

    if reassigned_jobs:
        narrative.append("#### Key Job Reassignments (Minimal Churn Applied)")
        narrative.extend(reassigned_jobs)
        narrative.append("")
    else:
        narrative.append("All jobs remain stable with optimized sequence.\n")

    narrative.append("#### Dispatch Action Items")
    narrative.append("1. **Operator Briefing**: Alert Baler #1 and #3 operators of newly routed farms via automated SMS dispatch.")
    narrative.append("2. **Buyer Coordination**: Confirm off-take capacity with Indri Bio-CNG and Panipat Power Station.")
    narrative.append("3. **Farmer Notifications**: Send revised arrival time notifications to affected farmers.")

    return "\n".join(narrative)
