"""
Insurance Assistance LangGraph Node for KisanSaarthi.
Wraps the existing InsuranceAgent, preserving the multi-turn interview,
PMFBY retrieval grounding, preliminary claim assistance reports, and disclaimers.
"""

from typing import Dict, Any
from agents.insurance import InsuranceAgent
from graph.state import KisanSaarthiState
from database.connection import SessionLocal


def insurance_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Executes crop insurance workflow using existing InsuranceAgent.
    Preserves multi-turn loss interview, PMFBY guidelines retrieval,
    and preliminary incident report generation.
    """
    farmer_id = state.get("farmer_id", "default")
    conversation_id = state.get("conversation_id", "default")
    message = state.get("user_message", "")
    language = state.get("language", "en")

    db = None
    try:
        db = SessionLocal()
        result = InsuranceAgent.execute(
            farmer_id=farmer_id,
            query=message,
            language=language,
            db=db,
            context={"conversation_id": conversation_id},
        )
    finally:
        if db:
            db.close()

    response_text = result.get("response") or result.get("text", "")
    status = result.get("status", "completed")
    next_question = result.get("next_question")
    missing_info = result.get("missing_information", [])

    return {
        "status": status,
        "response_text": response_text,
        "next_question": next_question,
        "missing_information": missing_info,
        "agent_result": result,
        "active_agent": "insurance",
        "detected_intent": "insurance",
    }
