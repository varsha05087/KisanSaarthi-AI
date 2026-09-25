"""
Tractor & Agricultural Equipment Booking Specialized Agent for KisanSaarthi AI.

Provides farmer-friendly, reliable conversational equipment booking:
1. Understands equipment booking requests naturally across English, Telugu, and Hindi.
2. Extracts equipment type, date, location, and preferred time slot.
3. Asks only ONE missing question at a time.
4. Preserves multi-turn state across messages.
5. Searches local/mock equipment catalogue across 4 predefined time slots:
   - 8:00 AM – 11:00 AM
   - 11:00 AM – 2:00 PM
   - 2:00 PM – 5:00 PM
   - 5:00 PM – 8:00 PM
6. Returns available equipment options with details:
   - Name, Type, Location, Date, Time slot, Price, Availability
7. Handles selection by option number, label, or equipment name.
8. Persists confirmed bookings in SQLite database via repository.create_booking.
9. Returns structured booking confirmation with booking ID.
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from tools.tractor_tool import (
    EQUIPMENT_CATALOGUE,
    TIME_SLOTS,
    search_equipment,
    search_nearby_tractors,
)
from database import repository


# In-memory session state store for multi-turn equipment booking
_SESSION_STATES: Dict[str, Dict[str, Any]] = {}


class TractorAgent:
    name = "Tractor Booking Agent"

    # Known locations
    KNOWN_LOCATIONS = [
        "guntur", "miryalaguda", "suryapet", "nalgonda", "khammam", "warangal",
        "krishna", "karimnagar", "kurnool", "anantapur", "peddapuram", "medak",
        "nizamabad", "rangareddy", "mahbubnagar", "adilabad", "prakasam", "nellore",
        "గుంటూరు", "మిర్యాలగూడ", "పెద్దాపురం", "నల్గొండ", "సూర్యాపేట", "ఖమ్మం", "వరంగల్",
        "गुंटूर", "मिर्यालगुडा", "सूर्यापेट", "नलगोंडा", "खम्मम", "वारंगल",
    ]

    # Equipment types mapping
    EQUIPMENT_TYPE_MAP = {
        "tractor": "tractor",
        "tractors": "tractor",
        "ట్రాక్టర్": "tractor",
        "ట్రాక్టరు": "tractor",
        "ట్రాక్టర్లు": "tractor",
        "ट्रैक्टर": "tractor",
        "rotavator": "rotavator",
        "రోటవేటర్": "rotavator",
        "రోటావేటర్": "rotavator",
        "रोटावेटर": "rotavator",
        "power tiller": "power_tiller",
        "power-tiller": "power_tiller",
        "tiller": "power_tiller",
        "పవర్ టిల్లర్": "power_tiller",
        "టిల్లర్": "power_tiller",
        "पावर टिलर": "power_tiller",
        "टिलर": "power_tiller",
    }

    # Time slot mapping
    TIME_SLOT_KEYWORDS = {
        "morning": "8:00 AM – 11:00 AM",
        "ఉదయం": "8:00 AM – 11:00 AM",
        "सुबह": "8:00 AM – 11:00 AM",
        "midday": "11:00 AM – 2:00 PM",
        "noon": "11:00 AM – 2:00 PM",
        "మధ్యాహ్నం": "11:00 AM – 2:00 PM",
        "दोपहर": "11:00 AM – 2:00 PM",
        "afternoon": "2:00 PM – 5:00 PM",
        "సాయంత్రం": "2:00 PM – 5:00 PM",
        "evening": "5:00 PM – 8:00 PM",
        "రాత్రి": "5:00 PM – 8:00 PM",
        "शाम": "5:00 PM – 8:00 PM",
    }

    # Relative and absolute date terms
    DATE_TERMS_MAP = {
        "day after tomorrow": "Day after tomorrow",
        "ఎల్లుండి": "Day after tomorrow",
        "परसों": "Day after tomorrow",
        "tomorrow": "Tomorrow",
        "tommorow": "Tomorrow",
        "tommorrow": "Tomorrow",
        "రేపు": "Tomorrow",
        "कल": "Tomorrow",
        "today": "Today",
        "ఈరోజు": "Today",
        "आज": "Today",
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
        "సోమవారం": "Monday",
        "మంగళవారం": "Tuesday",
        "బుధవారం": "Wednesday",
        "గురువారం": "Thursday",
        "శుక్రవారం": "Friday",
        "శనివారం": "Saturday",
        "ఆదివారం": "Sunday",
        "सोमवार": "Monday",
        "मंगलवार": "Tuesday",
        "बुधवार": "Wednesday",
        "गुरुवार": "Thursday",
        "शुक्रवार": "Friday",
        "शनिवार": "Saturday",
        "रविवार": "Sunday",
    }

    # ------------------------------------------------------------------
    # SESSION STATE MANAGEMENT
    # ------------------------------------------------------------------
    @classmethod
    def _get_session_key(cls, farmer_id: str, conversation_id: Optional[str] = None) -> str:
        """Computes isolated session key for farmer and conversation."""
        if conversation_id:
            return f"{farmer_id}:{conversation_id}"
        return farmer_id

    @classmethod
    def get_session_state(cls, farmer_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns active booking session state for a farmer and conversation."""
        key = cls._get_session_key(farmer_id, conversation_id)
        if key not in _SESSION_STATES:
            _SESSION_STATES[key] = {
                "farmer_id": farmer_id,
                "conversation_id": conversation_id,
                "equipment_type": None,
                "date": None,
                "location": None,
                "time_slot": None,
                "options": [],
                "status": "initial",
                "booking_id": None,
            }
        return _SESSION_STATES[key]

    @classmethod
    def clear_session_state(cls, farmer_id: str, conversation_id: Optional[str] = None) -> None:
        """Clears booking session state."""
        key = cls._get_session_key(farmer_id, conversation_id)
        if key in _SESSION_STATES:
            del _SESSION_STATES[key]
        if not conversation_id:
            # Also clean up any sub-keys starting with farmer_id:
            prefix = f"{farmer_id}:"
            keys_to_del = [k for k in list(_SESSION_STATES.keys()) if k.startswith(prefix)]
            for k in keys_to_del:
                del _SESSION_STATES[k]

    @classmethod
    def has_active_options(cls, farmer_id: str, conversation_id: Optional[str] = None) -> bool:
        """Checks if options were presented and awaiting selection."""
        key = cls._get_session_key(farmer_id, conversation_id)
        state = _SESSION_STATES.get(key)
        if not state:
            return False
        return bool(state.get("options")) and state.get("status") in ["options_presented", "ready"]

    @classmethod
    def is_awaiting_confirmation(cls, farmer_id: str, conversation_id: Optional[str] = None) -> bool:
        """Checks if a selected option is awaiting final farmer confirmation."""
        key = cls._get_session_key(farmer_id, conversation_id)
        state = _SESSION_STATES.get(key)
        if not state:
            return False
        return state.get("status") == "awaiting_confirmation" and bool(state.get("selected_option"))

    @classmethod
    def is_confirmation_query(cls, text: str) -> bool:
        """Checks if text is a confirmation utterance."""
        lowered = text.strip().lower()
        confirm_terms = [
            "confirm", "yes, confirm", "confirm booking", "yes confirm",
            "yes, please confirm", "proceed", "correct", "yes", "okay", "ok",
            "all correct", "right", "సరే", "అవును", "ధృవీకరించు", "ధృవీకరించండి",
            "కన్ఫర్మ్", "కన్ఫర్మ్ చేయండి", "హౌ", "బాగుంది", "బుకింగ్ నిర్ధారించండి",
            "నిర్ధారించండి", "బుకింగ్ కన్ఫర్మ్ చేయండి", "బుకింగ్ ధృవీకరించండి",
            "हाँ", "पुष्टि करें", "कन्फर्म", "कन्फर्म करें", "सही है", "ठीक है",
            "बुकिंग की पुष्टि करें",
        ]
        for term in confirm_terms:
            if re.search(rf"\b{re.escape(term)}\b", lowered) or term in lowered:
                return True
        return False

    @classmethod
    def is_change_details_query(cls, text: str) -> bool:
        """Checks if text requests changing booking details."""
        lowered = text.strip().lower()
        change_terms = [
            "change details", "change detail", "change", "edit", "modify",
            "మార్చు", "సవరించు", "మార్చండి", "బదలాయించు", "బుకింగ్ వివరాలు మార్చండి",
            "వివరాలు మార్చండి", "వివరాలు సవరించండి", "बदलें", "संशोधन", "बदलो",
            "विवरण बदलें",
        ]
        for term in change_terms:
            if re.search(rf"\b{re.escape(term)}\b", lowered) or term in lowered:
                return True
        return False

    # ------------------------------------------------------------------
    # ENTITY EXTRACTION
    # ------------------------------------------------------------------
    @classmethod
    def detect_language(cls, text: str, fallback: str = "te") -> str:
        """Detects whether text is in Telugu, Hindi (Devanagari), or English."""
        for ch in text:
            if "\u0c00" <= ch <= "\u0c7f":
                return "te"
            if "\u0900" <= ch <= "\u097f":
                return "hi"
        return fallback if fallback in ["te", "hi", "en"] else "en"

    @classmethod
    def extract_equipment_type(cls, text: str) -> Optional[str]:
        """Extracts equipment type (tractor, rotavator, power_tiller)."""
        lowered = text.lower()
        # Check specific implements first
        if any(k in lowered for k in ["rotavator", "రోటవేటర్", "రోటావేటర్", "रोटावेटर"]):
            return "rotavator"
        if any(k in lowered for k in ["power tiller", "power-tiller", "tiller", "పవర్ టిల్లర్", "టిల్లర్", "पावर टिलर", "टिलर"]):
            return "power_tiller"
        if any(k in lowered for k in ["tractor", "ట్రాక్టర్", "ట్రాక్టరు", "ట్రాక్టర్లు", "ट्रैक्टर"]):
            return "tractor"
        return None

    @classmethod
    def extract_date(cls, text: str) -> Optional[str]:
        """Extracts booking date from text."""
        lowered = text.lower()

        # Check keyword mappings (longer phrases first)
        for term, normalized in cls.DATE_TERMS_MAP.items():
            if re.search(rf"\b{re.escape(term)}\b", lowered) or term in lowered:
                return normalized

        # Check explicit formats: 25th September, 25 Sept, 2026-09-25, 25/09/2026
        explicit_match = re.search(
            r"\b(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*(?:\s+\d{4})?)\b",
            lowered,
        )
        if explicit_match:
            raw = explicit_match.group(1)
            formatted = re.sub(
                r"^(\d{1,2})(st|nd|rd|th)?\s+([a-z]+)(\s+\d{4})?$",
                lambda m: f"{m.group(1)}{m.group(2).lower() if m.group(2) else ''} {m.group(3).capitalize()}{m.group(4) or ''}",
                raw,
            )
            return formatted

        explicit_match2 = re.search(
            r"\b(?:on\s+)?((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?)\b",
            lowered,
        )
        if explicit_match2:
            return explicit_match2.group(1).title()

        num_date_match = re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", lowered)
        if num_date_match:
            return num_date_match.group(0)

        iso_date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", lowered)
        if iso_date_match:
            return iso_date_match.group(0)

        return None

    @classmethod
    def extract_location(cls, text: str) -> Optional[str]:
        """Extracts district or village location from text, accepting any location."""
        lowered = text.lower().strip()

        # Known agricultural locations
        for loc in cls.KNOWN_LOCATIONS:
            if re.search(rf"\b{re.escape(loc)}\b", lowered) or loc in lowered:
                return loc.capitalize()

        # Field patterns: 'my field near Guntur', 'field in Kakinada', 'my farm at Vijayawada'
        field_match = re.search(r"\b(?:my\s+)?(?:field|farm)\s+(?:near|in|at)\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+(?:\s+village)?)\b", text, re.IGNORECASE)
        if field_match:
            return field_match.group(1).strip().capitalize()

        # Prepositional patterns: 'in Kakinada', 'at Peddapuram', 'near Suryapet'
        match = re.search(r"\b(?:in|at|near|around)\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+(?:\s+village)?)\b", text, re.IGNORECASE)
        if match:
            cand = match.group(1).strip()
            stopwords = {"the", "a", "an", "my", "our", "this", "village", "field", "farm", "tractor", "tomorrow", "today", "morning", "evening"}
            if cand.lower() not in stopwords:
                return cand.capitalize()

        # Patterns like "village name is XYZ", "village is XYZ"
        v_match = re.search(r"\bvillage\s+(?:name\s+)?(?:is\s+)?([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+(?:\s+village)?)\b", text, re.IGNORECASE)
        if v_match:
            cand = v_match.group(1).strip()
            stopwords = {"the", "a", "an", "my", "our", "this", "village", "field", "farm", "tractor", "tomorrow", "today", "morning", "evening"}
            if cand.lower() not in stopwords:
                return cand.capitalize()

        # Pattern like "<Name> village" (e.g. "Peddapuram village")
        v_match2 = re.search(r"\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+village\b", text, re.IGNORECASE)
        if v_match2:
            cand = v_match2.group(1).strip()
            stopwords = {"the", "a", "an", "my", "our", "this", "village", "field", "farm", "tractor", "tomorrow", "today", "morning", "evening"}
            if cand.lower() not in stopwords:
                return cand.capitalize()

        # Telugu post-position 'లో' (e.g. 'గుంటూరులో', 'మిర్యాలగూడలో')
        te_match = re.search(r"([A-Za-z\u0c00-\u0c7f]+)\s*లో\b", text)
        if te_match:
            cand = te_match.group(1).strip()
            if cand not in ["పొలం", "చేను", "ఊరి"]:
                return cand.capitalize()

        # Hindi post-position 'में' (e.g. 'गुंटूर में', 'गाँव में')
        hi_match = re.search(r"([A-Za-z\u0900-\u097f]+)\s+में\b", text)
        if hi_match:
            cand = hi_match.group(1).strip()
            if cand not in ["खेत", "गाँव"]:
                return cand.capitalize()

        # Direct short answer (e.g. 'Kakinada', 'Vijayawada', 'Rajahmundry', 'Peddapuram village')
        words = text.strip().split()
        if 1 <= len(words) <= 3:
            cleaned = text.strip().rstrip(".,!?")
            lower_clean = cleaned.lower()
            not_loc_words = {
                "tractor", "tractors", "need", "want", "book", "booking", "tomorrow", "today",
                "morning", "evening", "afternoon", "yes", "no", "confirm", "option", "help",
                "hello", "hi", "namaste", "please", "okay", "ok", "i", "a",
                "ట్రాక్టర్", "ట్రాక్టరు", "కావాలి", "నాకు", "రేపు", "ఈరోజు", "ఉదయం", "సాయంత్రం",
                "సరే", "అవును", "ఎంపిక", "సహాయం", "నమస్కారం",
                "ट्रैक्टर", "चाहिए", "मुझे", "कल", "आज", "सुबह", "शाम", "हाँ", "नहीं", "विकल्प", "मदद", "नमस्ते"
            }
            if not any(w in not_loc_words for w in lower_clean.split()):
                return cleaned.capitalize()

        return None

    @classmethod
    def extract_specific_time(cls, text: str) -> Optional[str]:
        """Extracts explicit time mention like '2:30 PM', '10:00 AM', '2 PM', '2 30 pm'."""
        match = re.search(r"\b([0-1]?[0-9]|2[0-3])(?:[:\s]([0-5][0-9]))?\s*(am|pm|a\.m\.|p\.m\.)\b", text, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            minutes = match.group(2) or "00"
            meridiem = match.group(3).upper().replace(".", "")
            return f"{hour}:{minutes} {meridiem}"

        match24 = re.search(r"\b([0-1]?[0-9]|2[0-3])[:\s]([0-5][0-9])\b", text)
        if match24:
            hour = int(match24.group(1))
            minutes = match24.group(2)
            meridiem = "PM" if hour >= 12 else "AM"
            h12 = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)
            return f"{h12}:{minutes} {meridiem}"

        return None

    @classmethod
    def extract_time_slot(cls, text: str) -> Optional[str]:
        """Extracts preferred predefined time slot."""
        lowered = text.lower()

        # Check exact slot matches
        for slot in TIME_SLOTS:
            norm_slot = slot.lower().replace("–", "-")
            norm_text = lowered.replace("–", "-")
            if norm_slot in norm_text:
                return slot

        # Check time slot keywords with word boundaries
        for kw, slot in cls.TIME_SLOT_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", lowered) or (not kw.isascii() and kw in lowered):
                return slot

        # Check specific hours with optional minutes: e.g. 2:30 PM, 2 PM, 8:00 AM, 2 30 pm etc.
        if re.search(r"\b(8|9|10)(?:[:\s]\d{2})?\s*(?:am|a\.m\.)\b", lowered):
            return "8:00 AM – 11:00 AM"
        if re.search(r"\b(11|12)(?:[:\s]\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)\b|\b1(?:[:\s]\d{2})?\s*(?:pm|p\.m\.)\b", lowered):
            return "11:00 AM – 2:00 PM"
        if re.search(r"\b(2|3|4)(?:[:\s]\d{2})?\s*(?:pm|p\.m\.)\b", lowered):
            return "2:00 PM – 5:00 PM"
        if re.search(r"\b(5|6|7)(?:[:\s]\d{2})?\s*(?:pm|p\.m\.)\b", lowered):
            return "5:00 PM – 8:00 PM"

        return None

    # ------------------------------------------------------------------
    # SELECTION DETECTION
    # ------------------------------------------------------------------
    @classmethod
    def is_selection_query(cls, text: str, options: Optional[List[Dict[str, Any]]] = None) -> Optional[int]:
        """
        Detects if user is selecting an option by number, label, or equipment name.
        Returns 1-based index (1..N) if matched, else None.
        """
        trimmed = text.strip()
        lowered = trimmed.lower()

        # Direct number match: "1", "2", "3", "4", "5", "#1"
        num_match = re.match(r"^(?:option\s*|ఎంపిక\s*|विकल्प\s*|#\s*)?([1-5])(?:\s*(?:st|nd|rd|th)?(?:\s*option)?)?$", lowered)
        if num_match:
            return int(num_match.group(1))

        # Phrased selection: "Option 1", "Option 2", "1st option", "first option"
        phrase_match = re.search(r"\boption\s*#?\s*([1-5])\b", lowered)
        if phrase_match:
            return int(phrase_match.group(1))

        te_phrase_match = re.search(r"(?:ఎంపిక|ఆప్షన్)\s*#?\s*([1-5])", lowered)
        if te_phrase_match:
            return int(te_phrase_match.group(1))

        hi_phrase_match = re.search(r"(?:विकल्प|ऑप्शन)\s*#?\s*([1-5])", lowered)
        if hi_phrase_match:
            return int(hi_phrase_match.group(1))

        # Equipment name matching
        name_map = [
            ("greenfield", 1),
            ("గ్రీన్‌ఫీల్డ్", 1),
            ("ग्रीनफील्ड", 1),
            ("kisan power", 2),
            ("కిసాన్ పవర్", 2),
            ("किसान पावर", 2),
            ("mahindra", 3),
            ("మహీంద్రా", 3),
            ("महिंद्रा", 3),
            ("rotavator", 4),
            ("రోటవేటర్", 4),
            ("रोटावेटर", 4),
            ("power tiller", 5),
            ("tiller", 5),
            ("పవర్ టిల్లర్", 5),
            ("పావర్ టిల్లర్", 5),
            ("पावर टिलर", 5),
        ]

        # Check options list if provided
        if options:
            for opt in options:
                opt_name = opt.get("name", "").lower()
                opt_num = opt.get("option_number", 1)
                if opt_name and opt_name in lowered:
                    return opt_num

        for token, idx in name_map:
            if token in lowered:
                return idx

        return None

    # ------------------------------------------------------------------
    # EXECUTION WORKFLOW
    # ------------------------------------------------------------------
    @classmethod
    def execute(
        cls,
        farmer_id: str,
        query: str,
        language: str = "te",
        db: Optional[Session] = None,
        context: Optional[Dict[str, Any]] = None,
        auto_confirm: bool = False,
    ) -> Dict[str, Any]:
        """
        Coordinates full multi-turn equipment booking conversation.
        Supports 2-step selection -> review card -> final confirmation flow.
        """
        trimmed = query.strip()
        lang = cls.detect_language(trimmed, fallback=language)
        conversation_id = (context or {}).get("conversation_id")
        state = cls.get_session_state(farmer_id, conversation_id=conversation_id)

        if state.get("status") == "confirmed":
            cls.clear_session_state(farmer_id, conversation_id=conversation_id)
            state = cls.get_session_state(farmer_id, conversation_id=conversation_id)

        # Fallback: if in-memory state is missing location/date, restore from SQLite chat_messages history
        if db and conversation_id and (not state.get("location") or not state.get("date")):
            history = repository.get_conversation_history(db, farmer_id=farmer_id, conversation_id=conversation_id, limit=10)
            for h_msg in history:
                if h_msg.sender == "farmer":
                    h_loc = cls.extract_location(h_msg.message)
                    if h_loc and not state.get("location"):
                        state["location"] = h_loc
                    h_date = cls.extract_date(h_msg.message)
                    if h_date and not state.get("date"):
                        state["date"] = h_date
                    h_slot = cls.extract_time_slot(h_msg.message)
                    if h_slot and not state.get("time_slot"):
                        state["time_slot"] = h_slot
                    h_time = cls.extract_specific_time(h_msg.message)
                    if h_time and not state.get("specific_time"):
                        state["specific_time"] = h_time

        # -------------------------------------------------------------
        # STEP 1: Update session state from current query
        # -------------------------------------------------------------
        extracted_type = cls.extract_equipment_type(trimmed)
        extracted_date = cls.extract_date(trimmed)
        extracted_loc = cls.extract_location(trimmed)
        extracted_slot = cls.extract_time_slot(trimmed)
        extracted_time = cls.extract_specific_time(trimmed)

        if extracted_type:
            state["equipment_type"] = extracted_type
        elif not state.get("equipment_type"):
            state["equipment_type"] = "tractor"

        if extracted_date:
            state["date"] = extracted_date

        if extracted_loc:
            state["location"] = extracted_loc

        if extracted_slot:
            state["time_slot"] = extracted_slot

        if extracted_time:
            state["specific_time"] = extracted_time

        # -------------------------------------------------------------
        # STEP 2: Check if already in awaiting_confirmation state
        # -------------------------------------------------------------
        if state.get("status") == "awaiting_confirmation":
            # Case A: User confirms booking
            if cls.is_confirmation_query(trimmed):
                selected_option = state.get("selected_option")
                if selected_option:
                    return cls._confirm_booking(
                        farmer_id=farmer_id,
                        selected_option=selected_option,
                        state=state,
                        lang=lang,
                        db=db,
                    )

            # Case B: User wants to change details
            if cls.is_change_details_query(trimmed):
                state["status"] = "options_presented"
                state["selected_option"] = None
                if state.get("options"):
                    resp_text = cls._format_options_presentation(
                        options=state["options"],
                        location=state.get("location", "Guntur"),
                        date=state.get("date", "Tomorrow"),
                        lang=lang,
                    )
                    return {
                        "agent": cls.name,
                        "intent": "tractor_booking",
                        "status": "ready",
                        "stage": "options_presented",
                        "options": state["options"],
                        "missing_information": [],
                        "next_question": "Which equipment would you like to book? (Reply with option number or equipment name)",
                        "response": resp_text,
                        "text": resp_text,
                        "booking": None,
                    }
                else:
                    msg = (
                        "వివరాలు మార్చడానికి మీ కొత్త వివరాలను తెలపండి." if lang == "te" else
                        "विवरण बदलने के लिए कृपया नया विवरण बताएं।" if lang == "hi" else
                        "What details would you like to change?"
                    )
                    return {
                        "agent": cls.name,
                        "intent": "tractor_booking",
                        "status": "needs_information",
                        "response": msg,
                        "text": msg,
                    }

            # Case C: User selected a different option while in awaiting_confirmation
            new_sel_idx = cls.is_selection_query(trimmed, options=state.get("options"))
            if new_sel_idx is not None and state.get("options"):
                opts = state["options"]
                if 1 <= new_sel_idx <= len(opts):
                    selected_option = opts[new_sel_idx - 1]
                    state["selected_option"] = selected_option
                    return cls._present_confirmation_review(
                        farmer_id=farmer_id,
                        selected_option=selected_option,
                        state=state,
                        lang=lang,
                        db=db,
                    )

        # -------------------------------------------------------------
        # STEP 3: Check for Option Selection
        # -------------------------------------------------------------
        selected_idx = cls.is_selection_query(trimmed, options=state.get("options"))
        if selected_idx is not None and state.get("options"):
            opts = state["options"]
            if 1 <= selected_idx <= len(opts):
                selected_option = opts[selected_idx - 1]
                state["selected_option"] = selected_option
                state["status"] = "awaiting_confirmation"

                if auto_confirm:
                    return cls._confirm_booking(
                        farmer_id=farmer_id,
                        selected_option=selected_option,
                        state=state,
                        lang=lang,
                        db=db,
                    )

                return cls._present_confirmation_review(
                    farmer_id=farmer_id,
                    selected_option=selected_option,
                    state=state,
                    lang=lang,
                    db=db,
                )

        # Immediate selection if equipment name specified with date and location
        if selected_idx is not None and not state.get("options") and state.get("date") and state.get("location"):
            options = search_equipment(
                location=state["location"],
                date=state["date"],
                equipment_type=None,
                preferred_slot=state.get("time_slot"),
            )
            state["options"] = options
            if 1 <= selected_idx <= len(options):
                selected_option = options[selected_idx - 1]
                state["selected_option"] = selected_option
                state["status"] = "awaiting_confirmation"

                if auto_confirm:
                    return cls._confirm_booking(
                        farmer_id=farmer_id,
                        selected_option=selected_option,
                        state=state,
                        lang=lang,
                        db=db,
                    )

                return cls._present_confirmation_review(
                    farmer_id=farmer_id,
                    selected_option=selected_option,
                    state=state,
                    lang=lang,
                    db=db,
                )

        # -------------------------------------------------------------
        # STEP 4: Detect Missing Information (One Question at a Time)
        # -------------------------------------------------------------
        has_date = bool(state.get("date"))
        has_location = bool(state.get("location"))

        if not has_location:
            state["status"] = "needs_information"
            if lang == "te":
                q_text = "మీకు ట్రాక్టర్ ఏ గ్రామం లేదా పొలంలో అవసరం?"
            elif lang == "hi":
                q_text = "आपको ट्रैक्टर किस गाँव या खेत में चाहिए?"
            else:
                q_text = "Which village or field do you need the tractor in?"

            return {
                "agent": cls.name,
                "intent": "tractor_booking",
                "status": "needs_information",
                "missing_information": ["location"],
                "next_question": q_text,
                "response": q_text,
                "text": q_text,
                "booking": None,
            }

        elif not has_date:
            state["status"] = "needs_information"
            if lang == "te":
                q_text = "మీకు ఎప్పుడు ట్రాక్టర్ అవసరం?"
            elif lang == "hi":
                q_text = "आपको ट्रैक्टर कब चाहिए?"
            else:
                q_text = "When do you need the tractor?"

            return {
                "agent": cls.name,
                "intent": "tractor_booking",
                "status": "needs_information",
                "missing_information": ["date"],
                "next_question": q_text,
                "response": q_text,
                "text": q_text,
                "booking": None,
            }

        # -------------------------------------------------------------
        # STEP 5: All Information Present -> Search Equipment Catalogue
        # -------------------------------------------------------------
        date = state["date"]
        location = state["location"]
        eq_type = state.get("equipment_type") or "tractor"
        time_slot = state.get("time_slot")

        options = search_equipment(
            location=location,
            date=date,
            equipment_type=eq_type,
            preferred_slot=time_slot,
        )

        # Fallback if no specific implements match
        if not options and eq_type != "tractor":
            options = search_equipment(location=location, date=date, equipment_type=None, preferred_slot=time_slot)

        if not options:
            state["options"] = []
            state["status"] = "ready"
            if lang == "te":
                no_opt_text = f"మా డెమో కేటలాగ్‌లో {location} కోసం ట్రాక్టర్ అందుబాటులో లేదు. దయచేసి సమీపంలోని మరొక ప్రాంతాన్ని ప్రయత్నించండి."
            elif lang == "hi":
                no_opt_text = f"हमारे डेमो कैटलॉग में {location} के लिए कोई ट्रैक्टर उपलब्ध नहीं मिला। कृपया किसी अन्य नजदीकी स्थान का प्रयास करें।"
            else:
                no_opt_text = f"I couldn't find a tractor in our demo catalogue for {location}. Please try another nearby location."

            return {
                "agent": cls.name,
                "intent": "tractor_booking",
                "status": "ready",
                "stage": "no_options",
                "options": [],
                "missing_information": [],
                "next_question": None,
                "response": no_opt_text,
                "text": no_opt_text,
                "booking": None,
                "details": {
                    "equipment_type": eq_type,
                    "location": location,
                    "date": date,
                    "time_slot": time_slot,
                },
            }

        state["options"] = options
        state["status"] = "options_presented"

        response_text = cls._format_options_presentation(
            options=options,
            location=location,
            date=date,
            lang=lang,
        )

        return {
            "agent": cls.name,
            "intent": "tractor_booking",
            "status": "ready",
            "stage": "options_presented",
            "options": options,
            "missing_information": [],
            "next_question": "Which equipment would you like to book? (Reply with option number or equipment name)",
            "response": response_text,
            "text": response_text,
            "details": {
                "location": location,
                "date": date,
                "equipment_type": eq_type,
                "time_slot": time_slot,
                "specific_time": state.get("specific_time"),
                "count": len(options),
            },
            "booking": None,
        }

    # ------------------------------------------------------------------
    # FORMATTING & CONFIRMATION HELPERS
    # ------------------------------------------------------------------
    @classmethod
    def _format_options_presentation(
        cls,
        options: List[Dict[str, Any]],
        location: str,
        date: str,
        lang: str = "en",
    ) -> str:
        """Formats the list of available equipment options into farmer-friendly text cards."""
        lines = []
        loc_display = f"Near {location}" if not location.startswith("Near") else location

        if lang == "te":
            lines.append(f"🚜 [అందుబాటులో ఉన్న పరికరాలు (డెమో కేటలాగ్) - {location} సమీపంలో | {date}]:\n")
            for opt in options:
                lines.append(
                    f"{opt['option_number']}. {opt['name']}\n"
                    f"   {opt.get('specs', opt['type'])}\n"
                    f"   {location} సమీపంలో\n"
                    f"   {opt['time_slot']}\n"
                    f"   రూ. {opt['price']}/గంటకు\n"
                    f"   [ఎంచుకోండి]\n"
                )
            lines.append(
                "మీరు బుక్ చేయాలనుకుంటున్న పరికరం ఎంపిక సంఖ్యను తెలపండి (ఉదాహరణకు: '1' లేదా 'ఎంపిక 1')."
            )
        elif lang == "hi":
            lines.append(f"🚜 [उपलब्ध कृषि उपकरण (डेमो कैटलॉग) - {location} के पास | {date}]:\n")
            for opt in options:
                lines.append(
                    f"{opt['option_number']}. {opt['name']}\n"
                    f"   {opt.get('specs', opt['type'])}\n"
                    f"   {location} के पास\n"
                    f"   {opt['time_slot']}\n"
                    f"   रु. {opt['price']}/घंटा\n"
                    f"   [चुनें]\n"
                )
            lines.append(
                "जिस उपकरण को आप बुक करना चाहते हैं उसका विकल्प नंबर बताएं (जैसे: '1' या 'विकल्प 1')।"
            )
        else:
            lines.append(f"AVAILABLE TRACTORS NEAR {location.upper()}\n")
            for opt in options:
                lines.append(
                    f"{opt['option_number']}. {opt['name']}\n"
                    f"   {opt.get('specs', opt['type'])}\n"
                    f"   {loc_display}\n"
                    f"   {opt['time_slot']}\n"
                    f"   ₹{opt['price']}/hour\n"
                    f"   [Select]\n"
                )
            lines.append(
                "To select an option, reply with option number (e.g. 'Option 1') or click [Select]."
            )

        return "\n".join(lines).strip()

    @classmethod
    def _present_confirmation_review(
        cls,
        farmer_id: str,
        selected_option: Dict[str, Any],
        state: Dict[str, Any],
        lang: str = "en",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Presents the farmer profile + booking confirmation review card before creating booking."""
        booking_date = state.get("date") or selected_option.get("date") or "Tomorrow"
        booking_loc = state.get("location") or selected_option.get("location") or "Guntur"
        specific_time = state.get("specific_time")
        time_slot = state.get("time_slot") or selected_option.get("time_slot") or "2:00 PM – 5:00 PM"
        time_display = specific_time if specific_time else time_slot
        price_val = float(selected_option.get("price", 800))
        equipment_name = selected_option.get("name", selected_option.get("full_name", "GreenField Tractor"))

        # Retrieve farmer profile from existing SQLite database
        farmer_name = "Ramu"
        farmer_phone = "9876543210"
        farmer_village = booking_loc

        if db:
            farmer = repository.get_farmer(db, farmer_id)
            if farmer:
                if farmer.name and not farmer.name.startswith("Farmer FARMER-"):
                    farmer_name = farmer.name
                if farmer.phone:
                    farmer_phone = farmer.phone

        if lang == "te":
            review_text = (
                f"📋 మీ బుకింగ్ వివరాలను నిర్ధారించండి\n\n"
                f"రైతు వివరాలు:\n"
                f"• పేరు: {farmer_name}\n"
                f"• ఫోన్: {farmer_phone}\n"
                f"• గ్రామం: {farmer_village}\n\n"
                f"బుకింగ్ వివరాలు:\n"
                f"• పరికరం: {equipment_name}\n"
                f"• తేదీ: {booking_date}\n"
                f"• సమయం: {time_display}\n"
                f"• ప్రాంతం: {booking_loc}\n"
                f"• ధర: రూ. {int(price_val)}/గంటకు\n\n"
                f"అన్ని వివరాలు సరిగ్గా ఉన్నాయా?\n\n"
                f"[బుకింగ్ నిర్ధారించండి]  [వివరాలు మార్చండి]"
            )
        elif lang == "hi":
            review_text = (
                f"📋 अपनी बुकिंग की पुष्टि करें\n\n"
                f"किसान विवरण:\n"
                f"• नाम: {farmer_name}\n"
                f"• फ़ोन: {farmer_phone}\n"
                f"• गाँव: {farmer_village}\n\n"
                f"बुकिंग विवरण:\n"
                f"• उपकरण: {equipment_name}\n"
                f"• दिनांक: {booking_date}\n"
                f"• समय: {time_display}\n"
                f"• स्थान: {booking_loc}\n"
                f"• किराया: रु. {int(price_val)}/घंटा\n\n"
                f"क्या सभी विवरण सही हैं?\n\n"
                f"[बुकिंग की पुष्टि करें]  [विवरण बदलें]"
            )
        else:
            review_text = (
                f"CONFIRM YOUR BOOKING\n\n"
                f"Farmer Details\n"
                f"Name: {farmer_name}\n"
                f"Phone: {farmer_phone}\n"
                f"Village: {farmer_village}\n\n"
                f"Booking Details\n"
                f"Equipment: {equipment_name}\n"
                f"Date: {booking_date}\n"
                f"Time: {time_display}\n"
                f"Location: {booking_loc}\n"
                f"Rate: ₹{int(price_val)}/hour\n\n"
                f"Is everything correct?\n\n"
                f"[Confirm Booking]  [Change Details]"
            )

        conf_data = {
            "farmer_name": farmer_name,
            "farmer_phone": farmer_phone,
            "village": farmer_village,
            "equipment_name": equipment_name,
            "equipment_id": selected_option.get("id", "TRK-GFT-50"),
            "date": booking_date,
            "time": time_display,
            "location": booking_loc,
            "rate": f"₹{int(price_val)}/hour",
            "price": price_val,
        }

        next_q = (
            "అన్ని వివరాలు సరిగ్గా ఉన్నాయా? [బుకింగ్ నిర్ధారించండి] [వివరాలు మార్చండి]" if lang == "te"
            else "क्या सभी विवरण सही हैं? [बुकिंग की पुष्टि करें] [विवरण बदलें]" if lang == "hi"
            else "Is everything correct? [Confirm Booking] [Change Details]"
        )

        return {
            "agent": cls.name,
            "intent": "tractor_booking",
            "status": "ready",
            "stage": "awaiting_confirmation",
            "confirmation_details": conf_data,
            "selected_option": selected_option,
            "options": state.get("options", []),
            "missing_information": [],
            "next_question": next_q,
            "response": review_text,
            "text": review_text,
            "booking": None,
        }

    @classmethod
    def _confirm_booking(
        cls,
        farmer_id: str,
        selected_option: Dict[str, Any],
        state: Dict[str, Any],
        lang: str = "en",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Creates SQLite booking record and produces structured confirmation."""
        booking_date = state.get("date") or selected_option.get("date") or "Tomorrow"
        booking_loc = state.get("location") or selected_option.get("location") or "Guntur"
        specific_time = state.get("specific_time")
        booking_slot = state.get("time_slot") or selected_option.get("time_slot") or "2:00 PM – 5:00 PM"
        time_display = specific_time if specific_time else booking_slot
        price_val = float(selected_option.get("price", 800))
        equipment_id = selected_option.get("id", "TRK-GFT-50")
        equipment_name = selected_option.get("name", selected_option.get("full_name", "GreenField Tractor"))
        equipment_type = selected_option.get("type", "Tractor")
        owner_name = selected_option.get("owner", "Registered Service Provider")

        # Retrieve farmer profile
        farmer_name = "Ramu"
        farmer_phone = "9876543210"

        if db:
            farmer = repository.get_farmer(db, farmer_id)
            if not farmer:
                farmer = repository.create_farmer(
                    db,
                    name="Ramu",
                    phone="9876543210",
                    farmer_id=farmer_id,
                    language=lang,
                )
            if farmer.name and not farmer.name.startswith("Farmer FARMER-"):
                farmer_name = farmer.name
            if farmer.phone:
                farmer_phone = farmer.phone

        booking_id = f"KS-{uuid.uuid4().hex[:6].upper()}"

        if db:
            # Persist in SQLite bookings table
            db_booking = repository.create_booking(
                db=db,
                farmer_id=farmer_id,
                equipment_id=equipment_id,
                equipment_name=equipment_name,
                date=booking_date,
                time=time_display,
                location=booking_loc,
                price=price_val,
                status="confirmed",
                booking_id=booking_id,
            )
            booking_id = db_booking.id

            # Also persist in SQLite requests table
            repository.create_request(
                db=db,
                farmer_id=farmer_id,
                type="tractor_booking",
                status="completed",
                current_step=f"Equipment booked: {booking_id}",
                result=f"Booked {equipment_name} for {booking_date} at {booking_loc} ({booking_id})",
            )

        state["status"] = "confirmed"
        state["booking_id"] = booking_id

        # Localized structured booking confirmation matching prompt design
        if lang == "te":
            conf_text = (
                f"🎉 బుకింగ్ నిర్ధారించబడింది ✅\n\n"
                f"బుకింగ్ ID: {booking_id}\n"
                f"పరికరం: {equipment_name}\n"
                f"రైతు: {farmer_name}\n"
                f"ప్రాంతం: {booking_loc}\n"
                f"తేదీ: {booking_date}\n"
                f"సమయం: {time_display}\n"
                f"ధర: రూ. {int(price_val)}/గంటకు\n"
                f"స్థితి: నిర్ధారించబడింది\n\n"
                f"మీ బుకింగ్ విజయవంతంగా నమోదైంది. ఆపరేటర్ ({owner_name}) సమయానికి ముందుగా మిమ్మల్ని సంప్రదిస్తారు."
            )
        elif lang == "hi":
            conf_text = (
                f"🎉 बुकिंग की पुष्टि हो गई ✅\n\n"
                f"बुकिंग आईडी: {booking_id}\n"
                f"उपकरण: {equipment_name}\n"
                f"किसान: {farmer_name}\n"
                f"स्थान: {booking_loc}\n"
                f"दिनांक: {booking_date}\n"
                f"समय: {time_display}\n"
                f"किराया: रु. {int(price_val)}/घंटा\n"
                f"स्थिति: पुष्टि की गई\n\n"
                f"आपकी बुकिंग सफलतापूर्वक दर्ज कर ली गई है। ऑपरेटर ({owner_name}) निर्धारित समय से पहले आपसे संपर्क करेगा।"
            )
        else:
            conf_text = (
                f"BOOKING CONFIRMED\n\n"
                f"Booking ID: {booking_id}\n"
                f"Equipment: {equipment_name}\n"
                f"Farmer: {farmer_name}\n"
                f"Location: {booking_loc}\n"
                f"Date: {booking_date}\n"
                f"Time: {time_display}\n"
                f"Rate: ₹{int(price_val)}/hour\n"
                f"Status: Confirmed\n\n"
                f"The booking has been successfully confirmed and recorded in our database."
            )

        booking_summary = {
            "booking_id": booking_id,
            "equipment_id": equipment_id,
            "equipment_name": equipment_name,
            "farmer_name": farmer_name,
            "farmer_phone": farmer_phone,
            "type": equipment_type,
            "date": booking_date,
            "time": time_display,
            "time_slot": booking_slot,
            "location": booking_loc,
            "price": price_val,
            "rate": f"₹{int(price_val)}/hour",
            "status": "confirmed",
        }

        return {
            "agent": cls.name,
            "intent": "tractor_booking",
            "status": "ready",
            "stage": "confirmed",
            "booking_id": booking_id,
            "booking": booking_summary,
            "missing_information": [],
            "next_question": None,
            "response": conf_text,
            "text": conf_text,
            "details": booking_summary,
        }
