"""
Crop Residue LangGraph Node for KisanSaarthi.
Wraps the existing AgriCycle capability, providing practical, sustainable
pathways for stubble, straw, and biomass utilization while warning against burning.
"""

from typing import Dict, Any
from agents.agricycle import AgriCycleAgent
from graph.state import KisanSaarthiState


def crop_residue_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Executes crop residue guidance workflow using existing AgriCycleAgent.
    Preserves composting, mulching, bio-pellet monetization, and anti-burning guidance.
    """
    farmer_id = state.get("farmer_id", "default")
    message = state.get("user_message", "")
    language = state.get("language", "en")

    result = AgriCycleAgent.execute(
        farmer_id=farmer_id,
        query=message,
        language=language,
    )

    response_text = result.get("response", "")
    status = result.get("status", "completed")

    return {
        "status": status,
        "response_text": response_text,
        "agent_result": result,
        "active_agent": "crop_residue",
        "detected_intent": "crop_residue",
    }
