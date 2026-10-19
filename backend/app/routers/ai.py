from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.ai_agent import parse_farmer_request_llm, generate_replan_narrative
from app.services.state_store import state_store

router = APIRouter(prefix="/ai", tags=["AI"])

class ParseRequestInput(BaseModel):
    text: str
    add_to_farms: bool = False

class ExplainRequestInput(BaseModel):
    custom_prompt: Optional[str] = None

@router.post("/parse-request")
def parse_farmer_message(payload: ParseRequestInput) -> Dict[str, Any]:
    """
    Parses a natural language colloquial SMS / voice transcription from a farmer.
    Returns structured agricultural parameters.
    """
    extracted = parse_farmer_request_llm(payload.text)
    return {
        "status": "success",
        "raw_text": payload.text,
        "extracted_data": extracted
    }

@router.post("/explain-plan")
def explain_plan():
    """Generates an executive dispatch narrative and farmer notification draft."""
    state = state_store.get_state()
    if not state.current_plan:
        return {"summary": "No schedule plan has been generated yet."}

    summary = generate_replan_narrative(
        previous_plan=state.previous_plan,
        new_plan=state.current_plan,
        disruptions=state.active_disruptions
    )
    return {"summary": summary}
