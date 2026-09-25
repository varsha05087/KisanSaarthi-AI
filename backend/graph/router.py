"""
LangGraph Supervisor & Router Foundation for KisanSaarthi.
Analyzes farmer input across English, Telugu, and Hindi and routes
to the appropriate specialized agent capability with multi-turn session context.
"""

import re
from typing import Dict, Any, Optional, Tuple
from services.orchestrator import KisanSaarthiOrchestrator
from graph.state import KisanSaarthiState

# Supplemental regex patterns for natural agricultural queries
_SUPPLEMENTAL_PATTERNS = {
    "crop_health": [
        r"\bspots?\b",
        r"\bblight\b",
        r"\brots?\b",
        r"\bwilt(ing)?\b",
        r"leaves?.*(spots?|yellow|dry|rot|damage|burnt|curling)",
        r"spots?\s*(on|in)\s*(the\s*)?(leaves?|leaf|crop|plants?)",
        r"మచ్చలు",
        r"ఆకులు\s*ఎండిపో",
        r"ధబ్బే|धब्बे",
        r"पत्तियों\s*पर\s*धब्बे",
    ],
    "crop_residue": [
        r"\b(crop\s*residue|residue|paddy\s*straw|straw|stubble|agricycle|biomass|crop\s*waste|farm\s*waste)\b",
        r"\b(cotton\s*stalks?|sugarcane\s*(trash|waste)?|stalks?|maize\s*stalks?|corn\s*stalks?|wheat\s*(straw|bhusa)|groundnut\s*(haulms?|shells?))\b",
        r"\b(mulch(ing)?|compost(ing)?|stubble\s*burn(ing)?|parali)\b",
        r"\b(burn(ing)?\s*(my\s*)?(crop|residue|straw|stubble|waste))\b",
        r"\bburn\s*(my\s*)?crop\s*residue\b",
        r"వరి\s*గడ్డి",
        r"వ్యవసాయ\s*వ్యర్థాలు",
        r"పంట\s*చెత్త",
        r"పంట\s*వ్యర్థాలు",
        r"పత్తి\s*కట్టెలు",
        r"చెరకు\s*(చెత్త|వ్యర్థాలు)",
        r"మొక్కజొన్న\s*కాడలు",
        r"గడ్డి\s*(కాల్చడం|నిర్వహణ)",
        r"पराली",
        r"फसल\s*अवशेष",
        r"पुआल",
        r"कपास\s*के\s*डंठल",
        r"गन्ने\s*(की\s*पत्तियां|का\s*कचरा|के\s*अवशेष)",
        r"मक्के\s*के\s*डंठल",
        r"गेहूं\s*का\s*भूसा",
    ],
    "tractor_booking": [
        r"\b(tractor|plough|plow|harvester|rotavator|power\s*tiller|tiller|cultivator)\b",
        r"ట్రాక్టర్",
        r"దుక్కి",
        r"ट्रैक्टर",
        r"जुताई",
    ],
    "insurance": [
        r"\b(insurance|pmfby|claim|compensation|crop\s*damage|damaged?\s*by\s*rain|flood|drought|hail)\b",
        r"భీమా|బీమా|నష్టపరిహారం",
        r"फसल\s*బీమా|बीमा|मुआवजा|क्लेम",
    ],
    "general_agriculture": [
        r"\b(sow|sowing|plant|planting|harvest|irrigation|soil|fertilizer|crop\s*rotation|yield|variety)\b",
        r"\bwhen\s*(should|can|to)\s*(i\s*)?(sow|plant|grow|harvest)\b",
        r"విత్తడం|నాటడం|నీటిపారుదల|సేంద్రీయ|ఎరువులు",
        r"వరిని\s*ఎప్పుడు",
        r"बुवाई|सिंचाई|खाद|मिट्टी|फसल\s*चक्र",
    ],
}


def route_message(
    message: str,
    image_bytes: Optional[bytes] = None,
    farmer_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Determines the target intent and active agent for a given farmer message.
    Returns (detected_intent, active_agent).
    
    Target Capabilities:
    - ("crop_health", "crop_health")
    - ("tractor_booking", "tractor")
    - ("insurance", "insurance")
    - ("crop_residue", "crop_residue")
    - ("general_agriculture", "general_agriculture")
    """
    # 1. Multimodal priority: image input defaults to Crop Health
    if image_bytes is not None and len(image_bytes) > 0:
        return "crop_health", "crop_health"

    text = (message or "").strip().lower()

    # 2. Leverage existing orchestrator intent detection as primary source of truth
    orchestrator_intents = KisanSaarthiOrchestrator.detect_intents(text)

    # 3. Supplemental pattern checking
    supplemental_matches = []
    for intent, patterns in _SUPPLEMENTAL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                if intent not in supplemental_matches:
                    supplemental_matches.append(intent)
                break

    # 4. Context resumption for multi-turn conversational follow-up turns
    # If the message is a direct slot answer (e.g. "Peddapuram", "Tomorrow at 2:30 PM", "Option 1")
    # with no explicit new intent keywords, resume the active session intent.
    if not orchestrator_intents and not supplemental_matches and farmer_id:
        # Check active TractorAgent session
        try:
            from agents.tractor import TractorAgent
            t_state = TractorAgent.get_session_state(farmer_id, conversation_id=conversation_id)
            if (
                TractorAgent.has_active_options(farmer_id, conversation_id=conversation_id)
                or TractorAgent.is_awaiting_confirmation(farmer_id, conversation_id=conversation_id)
                or t_state.get("date")
                or t_state.get("location")
                or t_state.get("equipment_type")
                or t_state.get("status") in ["needs_information", "options_presented", "awaiting_confirmation"]
            ):
                return "tractor_booking", "tractor"
        except Exception:
            pass

        # Check active InsuranceAgent session
        try:
            from agents.insurance import _SESSION_STATES as _INS_STATES
            ins_key = f"{farmer_id}_insurance"
            if ins_key in _INS_STATES and _INS_STATES[ins_key].get("crop"):
                return "insurance", "insurance"
        except Exception:
            pass

        # Check SQLite history fallback if RAM state was flushed or session restarted
        try:
            from database.connection import SessionLocal
            from database import repository
            db_check = SessionLocal()
            try:
                hist = repository.get_conversation_history(db_check, farmer_id=farmer_id, conversation_id=conversation_id, limit=4)
                if hist:
                    last_asst = next((h for h in reversed(hist) if h.sender == "assistant"), None)
                    if last_asst and last_asst.intent:
                        if last_asst.intent in ["tractor_booking", "tractor"]:
                            return "tractor_booking", "tractor"
                        elif last_asst.intent in ["insurance", "insurance_assistance"]:
                            return "insurance", "insurance"
            finally:
                db_check.close()
        except Exception:
            pass

    # 5. Canonical resolution & precedence
    # Tractor booking precedence
    if "tractor_booking" in orchestrator_intents or "tractor_booking" in supplemental_matches:
        return "tractor_booking", "tractor"

    # Crop residue (AgriCycle) precedence
    if "agricycle" in orchestrator_intents or "crop_residue" in supplemental_matches:
        return "crop_residue", "crop_residue"

    # Insurance precedence
    if "insurance_assistance" in orchestrator_intents or "insurance" in supplemental_matches:
        return "insurance", "insurance"

    # Crop health precedence
    if "crop_health" in orchestrator_intents or "crop_health" in supplemental_matches:
        return "crop_health", "crop_health"

    # Seed assistance mapped to general agriculture or dedicated capability
    if "seed_assistance" in orchestrator_intents:
        return "general_agriculture", "general_agriculture"

    # General agriculture precedence
    if "general_agriculture" in orchestrator_intents or "general_agriculture" in supplemental_matches:
        return "general_agriculture", "general_agriculture"

    # 6. Default fallback to general agriculture
    return "general_agriculture", "general_agriculture"


def supervisor_node(state: KisanSaarthiState) -> Dict[str, Any]:
    """
    LangGraph node: Supervisor / Router.
    Inspects state and updates detected_intent, active_agent, and status.
    """
    message = state.get("user_message", "")
    image_bytes = state.get("image_bytes")
    farmer_id = state.get("farmer_id")
    conversation_id = state.get("conversation_id")

    detected_intent, active_agent = route_message(
        message,
        image_bytes=image_bytes,
        farmer_id=farmer_id,
        conversation_id=conversation_id,
    )

    return {
        "detected_intent": detected_intent,
        "active_agent": active_agent,
        "status": "routed",
    }
