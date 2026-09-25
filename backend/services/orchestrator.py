import re
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session

from services.agent_registry import AGENT_REGISTRY, get_agent_name, get_agent_class
from models.orchestrator import AgentTask, OrchestratorResponse
from database import repository


class KisanSaarthiOrchestrator:
    """
    Central Orchestrator for KisanSaarthi AI.
    - Accurately detects intents across English, Telugu, and Hindi
    - Maintains multi-turn conversation context from SQLite
    - Dispatches to specialized agents with practical agronomic tools
    - Identifies missing information and prompts one question at a time
    - Handles multi-intent requests and safe fallbacks
    """

    # Comprehensive multi-lingual intent keywords
    INTENT_KEYWORDS = {
        "crop_health": [
            r"ఆకులు\s*పసుపు",
            r"పసుపుగా\s*మారుతున్నా",
            r"తెగులు",
            r"పురుగు",
            r"వరి\s*రోగం",
            r"పత్తి.*(రోగం|తెగులు|పురుగు|మచ్చ|సమస్య)",
            r"మిర్చి.*(రోగం|తెగులు|పురుగు|మచ్చ|ముడత|సమస్య)",
            r"\bdisease\b",
            r"\bpest\b",
            r"\binsect\b",
            r"\bworm\b",
            r"\bfungus\b",
            r"\bblight\b",
            r"\byellow\s*(leaves|leaf|spots)?\b",
            r"\bleaf\s*spots?\b",
            r"\bcrop\s*(problem|issue|damage|disease)\b",
            r"\bproblem\s*with\s*(my\s*)?(crop|rice|paddy|cotton|chilli|plants?)\b",
            r"रोग",
            r"कीड़ा",
            r"पीली\s*पत्तियां",
            r"फसल\s*(में\s*)?(बीमारी|समस्या)",
        ],
        "input_verification": [
            r"\bfertilizer\b.*(genuine|fake|verify|authentic|check|real)",
            r"\bverify\b.*(fertilizer|seed|pesticide|input)",
            r"\bgenuine\b",
            r"\bauthentic\b",
            r"\bcounterfeit\b",
            r"\bspurious\b",
            r"\blabel\s*check\b",
            r"నకిలీ\s*(ఎరువులు|మందులు|విత్తనాలు)",
            r"ఎరువులు.*అసలైనవా",
            r"నిజమైన.*ఎరువు",
            r"असली\s*खाद",
            r"खाद.*असली.*नकली",
            r"कीटनाशक.*जांच",
        ],
        "tractor_booking": [
            r"ట్రాక్టర్\s*కావాలి",
            r"ట్రాక్టర్\s*బుకింగ్",
            r"దుక్కి\s*దున్నడానికి",
            r"\btractor\b",
            r"\bplough\b",
            r"\bplow\b",
            r"\bharvester\b",
            r"\brotavator\b",
            r"\bpower\s*tiller\b",
            r"\btiller\b",
            r"\bgreenfield\b",
            r"\bkisan\s*power\b",
            r"\bmahindra\b",
            r"\bbook\s*(a\s*)?tractor\b",
            r"\bneed\s*(a\s*)?tractor\b",
            r"రోటవేటర్",
            r"పవర్\s*టిల్లర్",
            r"గ్రీన్‌ఫీల్డ్",
            r"కిసాన్\s*పవర్",
            r"మహీంద్రా",
            r"ट्रैक्टर\s*चाहिए",
            r"ट्रैक्टर\s*बुकिंग",
            r"जुताई",
            r"रोटावेटर",
            r"पावर\s*टिलर",
            r"ग्रीनफील्ड",
            r"किसान\s*पावर",
            r"महिंद्रा",
        ],
        "insurance_assistance": [
            r"భీమా",
            r"బీమా",
            r"పంట\s*భీమా",
            r"క్లెయిమ్",
            r"నష్టపరిహారం",
            r"\binsurance\b",
            r"\bpmfby\b",
            r"\bclaim\b",
            r"\bcompensation\b",
            r"\bcrop\s*insurance\b",
            r"\bapply\s*(for\s*)?(crop\s*)?insurance\b",
            r"फसल\s*बीमा",
            r"बीमा\s*(के\s*लिए|का\s*दावा)",
            r"क्लेम",
            # Calamity & Crop Damage Peril Patterns
            r"(heavy|excess(ive)?)\s*rain.*(damage|destroy|ruin|affect|loss)",
            r"rain(s)?\s*(damaged|destroyed|ruined|affected)",
            r"damaged\s*by\s*(heavy\s*)?rain",
            r"వరి\s*పంట\s*వర్షానికి",
            r"భారీ\s*వర్షం.*నష్టం",
            r"వర్షం\s*వల్ల\s*నష్టం",
            r"భారీ\s*వర్షాలు",
            r"भारी\s*बारिश.*(नुकसान|खराब)",
            r"बारिश\s*से\s*फसल.*(नुकसान|खराब)",
            r"\b(flood(ed|ing)?|waterlogg(ed|ing)|submerge(d)?|inundat(ed|ion))\b",
            r"water\s*entered\s*(my\s*)?(field|farm|crop|plot)",
            r"వరద",
            r"నీరు\s*చేరింది",
            r"మునిగిపోయింది",
            r"బాధ",
            r"जलभराव",
            r"पानी\s*भर\s*गया",
            r"खेत\s*डूब\s*गया",
            r"\b(drought|dry\s*spell)\b",
            r"no\s*rain.*(drying|wither)",
            r"crop\s*(is\s*)?drying",
            r"వర్షాలు\s*లేక.*ఎండిపో",
            r"కరువు",
            r"పంట\s*ఎండిపో",
            r"సూఖా",
            r"सूखा",
            r"बारिश\s*नहीं.*(सूख|नुकसान)",
            r"फसल\s*सूख",
            r"\bhail(storm|stones?)?\b",
            r"hail\s*(destroyed|damaged)",
            r"వడగళ్ళు",
            r"వడగండ్ల",
            r"ओलावृष्टि",
            r"ओले\s*पड़े",
            r"\b(storm|cyclone|gale|high\s*winds?|strong\s*winds?)\b.*(damage|lodg|uproot)?",
            r"wind\s*(damaged|lodged|uprooted)",
            r"తుఫాను",
            r"ఈదురుగాలులు",
            r"గాలివాన",
            r"तेज\s*हवा.*नुकसान",
            r"आंधी",
            r"\bcrop\s*damage.*(claim|assist|report|insurance)\b",
            r"\bclaim\s*(assistance|help|process)\b",
            r"పంట\s*నష్టం.*(పరిహారం|బీమా|క్లెయిమ్)",
            r"फसल\s*नुकसान.*(दावा|मुआवजा|बीमा)",
        ],
        "agricycle": [
            r"వ్యవసాయ\s*వ్యర్థాలు",
            r"వరి\s*గడ్డి",
            r"పంట\s*చెత్త",
            r"పంట\s*వ్యర్థాలు",
            r"పత్తి\s*కట్టెలు",
            r"చెరకు\s*(చెత్త|వ్యర్థాలు)",
            r"మొక్కజొన్న\s*కాడలు",
            r"\bagricultural\s*waste\b",
            r"\bcrop\s*waste\b",
            r"\bcrop\s*residue\b",
            r"\bstubble\b",
            r"\bagricycle\b",
            r"\bbiomass\b",
            r"\bpaddy\s*straw\b",
            r"\b(cotton\s*stalks?|sugarcane\s*(trash|waste)?|stalks?|maize\s*stalks?|corn\s*stalks?|wheat\s*(straw|bhusa)|groundnut\s*(haulms?|shells?))\b",
            r"\b(burn(ing)?\s*(my\s*)?(crop|residue|straw|stubble|waste))\b",
            r"\bburn\s*(my\s*)?crop\s*residue\b",
            r"\b(farm\s*waste|straw)\b",
            r"पराली",
            r"कृषि\s*अपशिष्ट",
            r"फसल\s*अवशेष",
            r"पुआल",
            r"कपास\s*के\s*डंठल",
            r"गन्ने\s*(की\s*पत्तियां|का\s*कचरा|के\s*अवशेष)",
            r"मक्के\s*के\s*डंठल",
            r"गेहूं\s*का\s*भूसा",
        ],
        "seed_assistance": [
            r"విత్తనాలు\s*కావాలి",
            r"విత్తనం",
            r"సర్టిఫైడ్\s*విత్తనాలు",
            r"\bseeds?\b",
            r"\bseed\s*variety\b",
            r"\bbpt\s*5204\b",
            r"\bmtu\s*1010\b",
            r"\bsowing\s*seeds?\b",
            r"बीज\s*चाहिए",
            r"प्रमाणित\s*बीज",
        ],
        "general_help": [
            r"\bwhat\s*(can|do)\s*you\s*(do|help)\b",
            r"\bhelp\s*me\s*with\b",
            r"\bwho\s*are\s*you\b",
            r"\bhow\s*does\s*this\s*work\b",
            r"\bhello\b",
            r"\bhi\b",
            r"\bnamaste\b",
            r"నమస్కారం",
            r"హలో",
            r"नमस्ते",
        ],
        "general_agriculture": [
            r"\bcrop\s*rotation\b",
            r"\bintercrop(ping)?\b",
            r"\bwhen\s*(should|can|to)\s*(i\s*)?(sow|plant|grow|harvest|water|irrigate|fertilize)\b",
            r"\bhow\s*(to|can\s*i)\s*(sow|plant|grow|harvest|water|irrigate|fertilize|manage|control|prepare)\b",
            r"\b(sow|sowing|planting|germination)\b",
            r"\b(soil|soil\s*health|soil\s*fertility|soil\s*testing|soil\s*type|clay|loam|sandy)\b",
            r"\b(irrigation|watering|drip|sprinkler|flood\s*irrigation)\b",
            r"\b(fertilizer|fertilizers|nutrient|nutrients|npk|nitrogen|phosphorus|potassium|potash|urea|dap|manure|compost|vermicompost)\b",
            r"\b(organic\s*farming|natural\s*farming|sustainable\s*farming|mulching|green\s*manure)\b",
            r"\b(weeds?|weeding|weed\s*control|weed\s*management)\b",
            r"\b(harvest|harvesting|threshing|crop\s*management|post\s*harvest|storage|store)\b",
            r"\b(earthworms?|beneficial\s*insects?|pollination|biofertilizer)\b",
            r"పంట\s*మార్పిడి",
            r"అంతర\s*పంట",
            r"విత్తడం",
            r"నాటడం",
            r"నీటి\s*యాజమాన్యం",
            r"నీటిపారుదల",
            r"నేల\s*సారవంతం",
            r"భూసార",
            r"సేంద్రీయ",
            r"సేంద్రీయ\s*వ్యవసాయం",
            r"ఎరువులు",
            r"కలుపు",
            r"కలుపు\s*నివారణ",
            r"దిగుబడి",
            r"వరి\s*పంట",
            r"వరిని\s*ఎప్పుడు",
            r"ఫసల్\s*చక్ర",
            r"फसल\s*चक्र",
            r"बुवाई",
            r"सिंचाई",
            r"उर्वरक",
            r"खाद",
            r"मिट्टी",
            r"जैविक\s*खेती",
            r"खरपतवार",
            r"पैदावार",
            r"धान\s*की\s*फसल",
        ],
    }

    DATE_TERMS = [
        "tomorrow", "today", "morning", "evening", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday", "రేపు", "ఈరోజు", "ఉదయం", "సాయంత్రం",
        "कल", "आज", "सुबह", "शाम"
    ]

    LOCATION_TERMS = [
        "in ", "at ", "village", "mandal", "district", "peddapuram", "miryalaguda",
        "nalgonda", "suryapet", "khammam", "warangal", "guntur",
        "మిర్యాలగూడ", "పెద్దాపురం", "నల్గొండ", "సూర్యాపేట", "ఖమ్మం", "వరంగల్", "గుంటూరు",
        "గ్రామం", "మండలం", "పొలం", "చేను", "లో", "गाँव"
    ]

    CROP_TERMS = [
        "cotton", "paddy", "rice", "chilli", "maize", "wheat", "tomato",
        "పత్తి", "వరి", "మిర్చి", "మొక్కజొన్న", "కપાસ", "धान", "मिर्च", "मक्का"
    ]

    @classmethod
    def detect_language(cls, message: str, fallback_lang: str = "te") -> str:
        """Determines if the text contains Telugu, Devanagari (Hindi), or English script."""
        for ch in message:
            # Telugu Unicode block
            if "\u0c00" <= ch <= "\u0c7f":
                return "te"
            # Devanagari Unicode block
            if "\u0900" <= ch <= "\u097f":
                return "hi"
        # If user explicitly specified or ASCII
        return fallback_lang if fallback_lang in ["te", "hi", "en"] else "en"

    @classmethod
    def detect_intents(cls, message: str) -> List[str]:
        """Scans message and returns all matched intents."""
        lowered = message.lower()
        matched = []

        for intent, patterns in cls.INTENT_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, lowered, re.IGNORECASE):
                    if intent not in matched:
                        matched.append(intent)
                    break

        if len(matched) > 1 and "general_agriculture" in matched:
            specialized = [i for i in matched if i != "general_agriculture"]
            if specialized:
                matched = specialized

        return matched

    @classmethod
    def check_missing_info(
        cls, intent: str, message: str, lang: str = "te", farmer_id: Optional[str] = None, conversation_id: Optional[str] = None, db: Optional[Session] = None
    ) -> Tuple[List[str], Optional[str]]:
        """
        Detects if critical parameters are missing for an intent.
        Returns (missing_fields, single_localized_question).
        """
        lowered = message.lower()

        if intent == "tractor_booking":
            from agents.tractor import TractorAgent

            # If message is selecting an option, confirming, or requesting details change, bypass missing info check
            if (
                TractorAgent.is_selection_query(message) is not None
                or (
                    farmer_id and TractorAgent.is_awaiting_confirmation(farmer_id, conversation_id=conversation_id)
                    and (TractorAgent.is_confirmation_query(message) or TractorAgent.is_change_details_query(message))
                )
            ):
                return [], None

            state = TractorAgent.get_session_state(farmer_id, conversation_id=conversation_id) if farmer_id else {}

            # Fallback: if in-memory state is missing location/date, restore from SQLite chat_messages history
            if db and farmer_id and (not state.get("location") or not state.get("date")):
                history = repository.get_conversation_history(db, farmer_id=farmer_id, conversation_id=conversation_id, limit=10)
                for h_msg in history:
                    if h_msg.sender == "farmer":
                        h_loc = TractorAgent.extract_location(h_msg.message)
                        if h_loc and not state.get("location"):
                            state["location"] = h_loc
                        h_date = TractorAgent.extract_date(h_msg.message)
                        if h_date and not state.get("date"):
                            state["date"] = h_date
                        h_slot = TractorAgent.extract_time_slot(h_msg.message)
                        if h_slot and not state.get("time_slot"):
                            state["time_slot"] = h_slot
                        h_time = TractorAgent.extract_specific_time(h_msg.message)
                        if h_time and not state.get("specific_time"):
                            state["specific_time"] = h_time

            if state.get("status") == "confirmed":
                if farmer_id:
                    TractorAgent.clear_session_state(farmer_id, conversation_id=conversation_id)
                    state = TractorAgent.get_session_state(farmer_id, conversation_id=conversation_id)

            ex_date = TractorAgent.extract_date(message)
            ex_loc = TractorAgent.extract_location(message)
            ex_slot = TractorAgent.extract_time_slot(message)
            ex_time = TractorAgent.extract_specific_time(message)

            if ex_date and farmer_id:
                state["date"] = ex_date
            if ex_loc and farmer_id:
                state["location"] = ex_loc
            if ex_slot and farmer_id:
                state["time_slot"] = ex_slot
            if ex_time and farmer_id:
                state["specific_time"] = ex_time

            has_location = bool(state.get("location")) or bool(ex_loc) or any(loc in lowered for loc in cls.LOCATION_TERMS)
            has_date = bool(state.get("date")) or bool(ex_date) or any(d in lowered for d in cls.DATE_TERMS) or bool(re.search(r"\d{1,2}(st|nd|rd|th)?", lowered))

            if not has_location:
                question = (
                    "మీకు ట్రాక్టర్ ఏ గ్రామం లేదా పొలంలో అవసరం?"
                    if lang == "te" else
                    "आपको ट्रैक्टर किस गाँव या खेत में चाहिए?"
                    if lang == "hi" else
                    "Which village or field do you need the tractor in?"
                )
                return ["location"], question
            elif not has_date:
                question = (
                    "మీకు ఎప్పుడు ట్రాక్టర్ అవసరం?"
                    if lang == "te" else
                    "आपको ट्रैक्टर कब चाहिए?"
                    if lang == "hi" else
                    "When do you need the tractor?"
                )
                return ["date"], question

        return [], None

    @classmethod
    def process(
        cls,
        farmer_id: str,
        message: str,
        language: str = "te",
        conversation_id: str = "default",
        db: Optional[Session] = None,
    ) -> OrchestratorResponse:
        """
        Full End-to-End Orchestrator Pipeline.
        1. Context recall from SQLite
        2. Multi-lingual intent analysis
        3. Agent routing & tool execution
        4. Multi-turn conversation persistence
        5. SQLite request tracking
        """
        trimmed = message.strip()
        lang = cls.detect_language(trimmed, fallback_lang=language)
        timestamp_str = datetime.now().strftime("%I:%M %p")
        msg_id = f"msg-{uuid.uuid4().hex[:8]}"

        # -------------------------------------------------------------
        # STEP A: Recall conversation context from SQLite
        # -------------------------------------------------------------
        context_intent = None
        is_explicitly_unclear = bool(re.search(r"\b(don't|do\s*not)\s*know\b|\bunclear\b|\bconfused\b", trimmed, re.I))

        if db and not is_explicitly_unclear:
            history = repository.get_conversation_history(db, farmer_id=farmer_id, conversation_id=conversation_id, limit=6)
            # Only resume context if the immediate previous message was an assistant question or option prompt
            if history:
                last_msg = history[-1]
                if last_msg.sender == "assistant" and (
                    last_msg.message.strip().endswith("?")
                    or "option" in last_msg.message.lower()
                    or "ఎంపిక" in last_msg.message.lower()
                    or "विकल्प" in last_msg.message.lower()
                ):
                    context_intent = last_msg.intent

        # Also check active TractorAgent options, awaiting confirmation, or ongoing booking collection
        if not context_intent and not is_explicitly_unclear and farmer_id:
            from agents.tractor import TractorAgent
            t_state = TractorAgent.get_session_state(farmer_id, conversation_id=conversation_id)
            if (
                TractorAgent.has_active_options(farmer_id, conversation_id=conversation_id)
                or TractorAgent.is_awaiting_confirmation(farmer_id, conversation_id=conversation_id)
                or (t_state.get("date") or t_state.get("location"))
            ):
                context_intent = "tractor_booking"

        matched_intents = cls.detect_intents(trimmed)

        # If current input is a direct follow-up answer (e.g. "tomorrow morning in Peddapuram" or "Option 1")
        if not matched_intents and context_intent and not is_explicitly_unclear:
            matched_intents = [context_intent]

        # -------------------------------------------------------------
        # CASE 1: Unknown / Unclear Request OR Open-Ended Agriculture
        # -------------------------------------------------------------
        if not matched_intents:
            if is_explicitly_unclear or not trimmed:
                if lang == "te":
                    response_text = (
                        "నేను మీకు ఈ విషయాలలో సహాయం చేయగలను:\n"
                        "1. 🌱 పంట తెగుళ్ల విశ్లేషణ & మందులు\n"
                        "2. 🔍 ఎరువులు & పురుగుమందుల ప్రామాణికత తనిఖీ\n"
                        "3. 🚜 ట్రాక్టర్ & వ్యవసాయ పరికరాల బుకింగ్\n"
                        "4. 🛡️ పంట భీమా (PMFBY) క్లెయిమ్ సహాయం\n"
                        "5. ♻️ వ్యవసాయ వ్యర్థాల (AgriCycle) వినియోగం\n"
                        "6. 🌾 సర్టిఫైడ్ విత్తనాల లభ్యత\n\n"
                        "మీ సమస్యను మీ మాటల్లో చెప్పండి."
                    )
                elif lang == "hi":
                    response_text = (
                        "मैं आपकी इन विषयों में सहायता कर सकता हूँ:\n"
                        "1. 🌱 फसल रोग जांच एवं उपचार\n"
                        "2. 🔍 उर्वरक/कीटनाशक प्रामाणिकता जांच\n"
                        "3. 🚜 ट्रैक्टर एवं कृषि उपकरण बुकिंग\n"
                        "4. 🛡️ फसल बीमा (PMFBY) दावा सहायता\n"
                        "5. ♻️ पराली एवं कृषि अपशिष्ट प्रबंधन\n"
                        "6. 🌾 प्रमाणित बीज उपलब्धता\n\n"
                        "कृपया अपनी समस्या बताएं।"
                    )
                else:
                    response_text = (
                        "I can help with crop health, fertilizer verification, tractor booking, "
                        "crop insurance claims, seeds, and agricultural waste management. "
                        "What do you need assistance with?"
                    )

                # Persist turns
                if db:
                    repository.save_chat_message(db, farmer_id, "farmer", trimmed, conversation_id, "unknown", lang)
                    repository.save_chat_message(db, farmer_id, "assistant", response_text, conversation_id, "unknown", lang)

                return OrchestratorResponse(
                    farmer_id=farmer_id,
                    message=trimmed,
                    language=lang,
                    intent="unknown",
                    status="needs_clarification",
                    agent=None,
                    missing_information=[],
                    next_question=None,
                    tasks=[],
                    response=response_text,
                    text=response_text,
                    id=msg_id,
                    sender="agent",
                    timestamp=timestamp_str,
                )
            else:
                # Open-ended agricultural question or out-of-domain query -> Route to General Agriculture AI
                matched_intents = ["general_agriculture"]

        # -------------------------------------------------------------
        # CASE 2: Multi-Intent Request
        # -------------------------------------------------------------
        if len(matched_intents) > 1 and "general_help" not in matched_intents:
            tasks = []
            agent_responses = []

            for intent in matched_intents:
                agent_name = get_agent_name(intent)
                agent_cls = get_agent_class(intent)

                request_id = None
                if db:
                    req = repository.create_request(
                        db,
                        farmer_id=farmer_id,
                        type=intent,
                        status="processing",
                        current_step=f"Orchestrator dispatched to {agent_name}",
                    )
                    request_id = req.id

                task_output = agent_cls.execute(farmer_id=farmer_id, query=trimmed, language=lang) if agent_cls else {}
                agent_responses.append(task_output.get("response", f"Delegated to {agent_name}."))

                tasks.append(
                    AgentTask(
                        intent=intent,
                        agent=agent_name,
                        description=f"Handle {intent.replace('_', ' ')}",
                        request_id=request_id,
                    )
                )

            combined_response = "\n\n---\n\n".join(agent_responses)
            agent_names = ", ".join(t.agent for t in tasks)

            if db:
                repository.save_chat_message(db, farmer_id, "farmer", trimmed, conversation_id, "multi_intent", lang)
                repository.save_chat_message(db, farmer_id, "assistant", combined_response, conversation_id, "multi_intent", lang)

            return OrchestratorResponse(
                farmer_id=farmer_id,
                message=trimmed,
                language=lang,
                intent="multi_intent",
                status="multi_task",
                agent=agent_names,
                missing_information=[],
                next_question=None,
                tasks=tasks,
                response=combined_response,
                text=combined_response,
                id=msg_id,
                sender="agent",
                timestamp=timestamp_str,
            )

        # -------------------------------------------------------------
        # CASE 3: Single Intent Request
        # -------------------------------------------------------------
        primary_intent = matched_intents[0]

        # 3A: General Help
        if primary_intent == "general_help":
            if lang == "te":
                resp_str = (
                    "నమస్కారం! నేను కిసాన్ సారథి AI ఏజెంట్ సహాయకుడిని.\n"
                    "నేను మీకు పంట తెగుళ్లు, ఎరువుల నిర్ధారణ, ట్రాక్టర్ బుకింగ్, పంట భీమా మరియు విత్తనాల సమాచారంలో సహాయపడగలను."
                )
            elif lang == "hi":
                resp_str = (
                    "नमस्ते! मैं किसान सारथी AI सहायक हूँ।\n"
                    "मैं फसल रोग, खाद सत्यापन, ट्रैक्टर बुकिंग, फसल बीमा और बीज सहायता में आपकी पूरी मदद कर सकता हूँ।"
                )
            else:
                resp_str = (
                    "Hello! I am KisanSaarthi AI, your agentic agricultural assistant.\n"
                    "I can assist with Crop Health, Fertilizer Verification, Tractor Booking, PMFBY Crop Insurance, and AgriCycle Waste."
                )

            if db:
                repository.save_chat_message(db, farmer_id, "farmer", trimmed, conversation_id, "general_help", lang)
                repository.save_chat_message(db, farmer_id, "assistant", resp_str, conversation_id, "general_help", lang)

            return OrchestratorResponse(
                farmer_id=farmer_id,
                message=trimmed,
                language=lang,
                intent="general_help",
                status="ready",
                agent="KisanSaarthi General Assistant",
                missing_information=[],
                next_question=None,
                tasks=[],
                response=resp_str,
                text=resp_str,
                id=msg_id,
                sender="agent",
                timestamp=timestamp_str,
            )

        # 3A: Input Verification direct handler
        if primary_intent == "input_verification":
            agent_cls = get_agent_class("input_verification")
            agent_name = get_agent_name("input_verification")
            agent_result = agent_cls.execute(farmer_id=farmer_id, query=trimmed, language=lang)
            agent_response_text = agent_result.get("response", "")
            resp_status = "ready"
            if db:
                req = repository.create_request(db, farmer_id=farmer_id, type="input_verification", status=resp_status, current_step="Input Verification", result=agent_response_text[:200])
                repository.save_chat_message(db, farmer_id, "farmer", trimmed, conversation_id, "input_verification", lang)
                repository.save_chat_message(db, farmer_id, "assistant", agent_response_text, conversation_id, "input_verification", lang)
                req_id = req.id
            else:
                req_id = None
            task = AgentTask(intent="input_verification", agent=agent_name, description="Verify input authenticity", request_id=req_id)
            return OrchestratorResponse(
                farmer_id=farmer_id,
                message=trimmed,
                language=lang,
                intent="input_verification",
                status=resp_status,
                agent=agent_name,
                missing_information=[],
                next_question=None,
                tasks=[task],
                response=agent_response_text,
                text=agent_response_text,
                id=msg_id,
                sender="agent",
                timestamp=timestamp_str,
            )

        # -------------------------------------------------------------
        # STEP 3: LangGraph Multi-Agent Workflow Execution
        # -------------------------------------------------------------
        from graph.workflow import get_kisansaarthi_graph
        from graph.state import KisanSaarthiState

        initial_state: KisanSaarthiState = {
            "farmer_id": farmer_id,
            "conversation_id": conversation_id,
            "language": lang,
            "user_message": trimmed,
            "crop_name": None,
        }

        graph = get_kisansaarthi_graph()
        final_state = graph.invoke(initial_state)

        # Extract agent execution output from LangGraph state
        graph_intent = final_state.get("detected_intent") or primary_intent
        graph_agent = final_state.get("active_agent") or primary_intent
        agent_status = final_state.get("status", "completed")
        agent_response_text = final_state.get("response_text", "")
        next_q = final_state.get("next_question")
        missing_fields = final_state.get("missing_information", [])
        options = final_state.get("options")
        confirmation_details = final_state.get("confirmation_details")
        booking = final_state.get("booking")
        agent_result = final_state.get("agent_result") or {}

        # Canonical mapping for OrchestratorResponse compatibility
        if graph_intent in ["insurance", "insurance_assistance"]:
            canonical_intent = "insurance_assistance"
        elif graph_intent in ["crop_residue", "agricycle"]:
            canonical_intent = "agricycle"
        elif graph_intent in ["tractor_booking", "tractor"]:
            canonical_intent = "tractor_booking"
        elif graph_intent in ["crop_health"]:
            canonical_intent = "crop_health"
        else:
            canonical_intent = "general_agriculture"

        agent_name = get_agent_name(canonical_intent)

        # Map execution status to Orchestrator response contract
        if agent_status in ["needs_information"]:
            resp_status = "needs_information"
            next_q = next_q or agent_response_text
            missing_fields = missing_fields or [next_q]
            step_desc = f"{agent_name}: needs_information"
            task_desc = f"Awaiting information for {canonical_intent.replace('_', ' ')}"
        elif agent_status in ["needs_image", "needs_better_image"]:
            resp_status = agent_status
            missing_fields = ["crop_image"] if agent_status == "needs_image" else ["clearer_crop_image"]
            next_q = next_q or agent_response_text
            step_desc = f"{agent_name}: {agent_status}"
            task_desc = f"Awaiting photo for {canonical_intent.replace('_', ' ')}"
        elif agent_status in ["information_collection"]:
            resp_status = "information_collection"
            missing_fields = missing_fields or ["incident_details"]
            next_q = next_q or agent_response_text
            step_desc = f"{agent_name}: collecting information"
            task_desc = f"Collecting information for {canonical_intent.replace('_', ' ')}"
        elif agent_status in ["report_generated"]:
            resp_status = "report_generated"
            missing_fields = []
            next_q = None
            step_desc = f"{agent_name}: Report generated"
            task_desc = f"Assistance report generated for {canonical_intent.replace('_', ' ')}"
        elif options or confirmation_details or agent_status in ["ready", "completed", "confirmed"]:
            resp_status = "ready"
            missing_fields = []
            next_q = None
            if booking and booking.get("booking_id"):
                step_desc = f"{agent_name}: Confirmed booking {booking.get('booking_id')}"
                task_desc = f"Equipment booked: {booking.get('booking_id')}"
            else:
                step_desc = f"Executed by {agent_name} via LangGraph"
                task_desc = f"Completed {canonical_intent.replace('_', ' ')}"
        else:
            resp_status = agent_status
            step_desc = f"{agent_name}: {agent_status}"
            task_desc = f"Processed {canonical_intent.replace('_', ' ')}"

        # SQLite persistence
        request_id = agent_result.get("request_id")
        if db:
            if not request_id:
                req = repository.create_request(
                    db,
                    farmer_id=farmer_id,
                    type=canonical_intent,
                    status=resp_status,
                    current_step=step_desc,
                    result=agent_response_text[:200],
                )
                request_id = req.id
            repository.save_chat_message(db, farmer_id, "farmer", trimmed, conversation_id, canonical_intent, lang)
            repository.save_chat_message(db, farmer_id, "assistant", agent_response_text, conversation_id, canonical_intent, lang)

        task = AgentTask(
            intent=canonical_intent,
            agent=agent_name,
            description=task_desc,
            request_id=request_id,
        )

        return OrchestratorResponse(
            farmer_id=farmer_id,
            message=trimmed,
            language=lang,
            intent=canonical_intent,
            status=resp_status,
            agent=agent_name,
            missing_information=missing_fields,
            next_question=next_q,
            tasks=[task],
            response=agent_response_text,
            text=agent_response_text,
            id=msg_id,
            sender="agent",
            timestamp=timestamp_str,
            options=options,
            confirmation_details=confirmation_details,
            booking=booking,
        )

