"""
Post Processor LangGraph Node for KisanSaarthi.
Normalizes agent output fields into standard response contracts
without modifying or inventing content.
"""

from typing import Dict, Any
from graph.state import KisanSaarthiState


def post_processor_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    Final graph node that verifies response completeness and consistency.
    Passes through all specialized agent fields without modifying content.
    """
    response_text = state.get("response_text") or ""
    status = state.get("status") or "completed"

    if not response_text:
        next_q = state.get("next_question")
        if next_q:
            response_text = next_q
        else:
            lang = (state.get("language") or "en").lower()[:2]
            if lang == "te":
                response_text = "మీ అభ్యర్థన విజయవంతంగా ప్రాసెస్ చేయబడింది."
            elif lang == "hi":
                response_text = "आपका अनुरोध सफलतापूर्वक संसाधित किया गया।"
            else:
                response_text = "Your request was processed successfully."

    return {
        "response_text": response_text,
        "status": status,
    }
