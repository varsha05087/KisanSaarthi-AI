"""
General Agriculture LangGraph Node for KisanSaarthi.
Wraps the existing GeneralAgricultureAgent, preserving Gemini-based
agronomic guidance, conversation context, safety guardrails, and multilingual support.
"""

from typing import Dict, Any
from agents.general_agriculture import GeneralAgricultureAgent
from graph.state import KisanSaarthiState
from database.connection import SessionLocal


def general_agri_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Executes general agricultural Q&A using existing GeneralAgricultureAgent.
    Preserves Gemini model integration, multilingual responses, and safety boundaries.
    """
    farmer_id = state.get("farmer_id", "default")
    conversation_id = state.get("conversation_id", "default")
    message = state.get("user_message", "")
    language = state.get("language", "en")

    db = None
    try:
        db = SessionLocal()
        result = GeneralAgricultureAgent.execute(
            farmer_id=farmer_id,
            query=message,
            language=language,
            db=db,
            context={"conversation_id": conversation_id},
        )
    finally:
        if db:
            db.close()

    response_text = result.get("response", "")
    status = result.get("status", "completed")

    return {
        "status": status,
        "response_text": response_text,
        "agent_result": result,
        "active_agent": "general_agriculture",
        "detected_intent": "general_agriculture",
    }
