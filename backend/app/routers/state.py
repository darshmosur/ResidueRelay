from fastapi import APIRouter
from app.models.state import SimulationState
from app.services.state_store import state_store

router = APIRouter(prefix="/state", tags=["State"])

@router.get("", response_model=SimulationState)
def get_current_state():
    """Retrieve full live simulation state."""
    return state_store.get_state()

@router.post("/reset", response_model=SimulationState)
def reset_state():
    """Reset the entire simulation to fresh initial state."""
    return state_store.reset()
