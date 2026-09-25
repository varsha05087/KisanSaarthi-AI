"""
Tractor Booking LangGraph Node for KisanSaarthi.
Wraps the existing TractorAgent, preserving 1-question-at-a-time flow,
session state preservation, option selection, and SQLite booking creation.
"""

from typing import Dict, Any
from agents.tractor import TractorAgent
from graph.state import KisanSaarthiState
from database.connection import SessionLocal


def tractor_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Executes equipment booking workflow using existing TractorAgent.
    Preserves multi-turn state, one-question-at-a-time dialogue,
    interactive catalogue options, and SQLite bookings.
    """
    farmer_id = state.get("farmer_id", "default")
    conversation_id = state.get("conversation_id", "default")
    message = state.get("user_message", "")
    language = state.get("language", "te")

    db = None
    try:
        db = SessionLocal()
        result = TractorAgent.execute(
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
    options = result.get("options")
    confirmation_details = result.get("confirmation_details")
    booking = result.get("booking")

    return {
        "status": status,
        "response_text": response_text,
        "next_question": next_question,
        "missing_information": missing_info,
        "options": options,
        "confirmation_details": confirmation_details,
        "booking": booking,
        "agent_result": result,
        "active_agent": "tractor",
        "detected_intent": "tractor_booking",
    }
