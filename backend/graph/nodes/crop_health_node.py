"""
Crop Health LangGraph Node for KisanSaarthi.
Wraps the existing CropHealthAgent, preserving MobileNetV2 disease detection,
ICAR knowledge grounding, and multilingual validation.
"""

from typing import Dict, Any
from agents.crop_health_agent import CropHealthAgent
from graph.state import KisanSaarthiState
from database.connection import SessionLocal


def crop_health_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Executes Crop Health diagnostic workflow using existing CropHealthAgent.
    Handles image validation, MobileNetV2 vision inference, and ICAR advisory.
    """
    farmer_id = state.get("farmer_id", "F001")
    message = state.get("user_message", "")
    language = state.get("language", "te")
    image_bytes = state.get("image_bytes")
    crop_name = state.get("crop_name")

    db = None
    try:
        db = SessionLocal()
        result = CropHealthAgent.process_request(
            farmer_id=farmer_id,
            message=message,
            language=language,
            image_bytes=image_bytes,
            crop_name=crop_name,
            db=db,
        )
    finally:
        if db:
            db.close()

    result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()

    return {
        "status": result.status,
        "response_text": result.response,
        "next_question": result.next_question,
        "agent_result": result_dict,
        "active_agent": "crop_health",
        "detected_intent": "crop_health",
    }
