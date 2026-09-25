"""
Shared LangGraph State Definition for KisanSaarthi Multi-Agent System.
Defines the state structure passed between the supervisor and specialized agent nodes.
"""

from typing import TypedDict, Optional, List, Dict, Any


class KisanSaarthiState(TypedDict, total=False):
    """
    Shared state schema for KisanSaarthi LangGraph workflows.
    Tracks session identity, multimodal input, agent routing, slot-filling,
    and structured response payloads.
    """

    farmer_id: str
    conversation_id: str
    language: str
    user_message: str

    image_bytes: Optional[bytes]
    crop_name: Optional[str]

    detected_intent: str
    active_agent: str

    status: str

    missing_information: List[str]
    next_question: Optional[str]

    response_text: str

    options: Optional[List[Dict[str, Any]]]
    confirmation_details: Optional[Dict[str, Any]]
    booking: Optional[Dict[str, Any]]

    agent_result: Optional[Dict[str, Any]]
    error: Optional[str]
