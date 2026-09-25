"""
Crop Insurance Assistance Agent for KisanSaarthi AI.

Provides farmer-friendly, reliable, and non-hallucinating guidance for:
1. Crop damage intake and multi-turn interview (one question at a time)
2. Preliminary Incident Report generation
3. Document and evidence guidance
4. Claim process orientation and anti-fraud verification
5. Multi-lingual support (English, Telugu, Hindi)

Principle: Assistance only. Does not submit claims, approve claims, or guarantee payouts.
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from services.insurance_retrieval_service import (
    retrieve_insurance_guidance,
    GENERAL_DISCLAIMER,
    UNVERIFIED_FALLBACK_MESSAGE,
    get_unverified_fallback_message,
)
from database import repository


# In-memory session state fallback (for testing or stateless sessions)
_SESSION_STATES: Dict[str, Dict[str, Any]] = {}


class InsuranceAgent:
    name = "Insurance Assistance Agent"

    # Supported crops for extraction
    CROPS_MAP = {
        "paddy": "Paddy", "rice": "Paddy", "వరి": "Paddy", "धान": "Paddy", "चावल": "Paddy",
        "cotton": "Cotton", "పత్తి": "Cotton", "కపాస్": "Cotton", "कपास": "Cotton",
        "chilli": "Chilli", "chili": "Chilli", "chilly": "Chilli", "మిర్చి": "Chilli", "मिर्च": "Chilli",
        "maize": "Corn", "corn": "Corn", "మొక్కజొన్న": "Corn", "मक्का": "Corn",
        "wheat": "Wheat", "గోధుమ": "Wheat", "गेहूं": "Wheat",
        "tomato": "Tomato", "టమాటా": "Tomato", "टमाटर": "Tomato",
        "potato": "Potato", "బంగాళాదుంప": "Potato", "आलू": "Potato",
        "sugarcane": "Sugarcane", "చెరకు": "Sugarcane", "गन्ना": "Sugarcane",
        "groundnut": "Groundnut", "వేరుశనగ": "Groundnut", "मूंगफली": "Groundnut",
        "soybean": "Soybean", "సోయాబీన్": "Soybean", "सोयाबीन": "Soybean",
        "pulses": "Pulses", "gram": "Pulses", "కంది": "Pulses", "दाल": "Pulses",
    }

    # Known locations/districts for extraction
    KNOWN_LOCATIONS = [
        "guntur", "miryalaguda", "suryapet", "nalgonda", "khammam", "warangal",
        "krishna", "karimnagar", "kurnool", "anantapur", "peddapuram", "medak",
        "nizamabad", "rangareddy", "mahbubnagar", "adilabad", "prakasam", "nellore",
        "chittoor", "kadapa", "visakhapatnam", "vizag", "east godavari", "west godavari",
        "గుంటూరు", "మిర్యాలగూడ", "సూర్యాపేట", "నల్గొండ", "ఖమ్మం", "వరంగల్",
        "गुंटूर", "सूर्यापेट", "नलगोंडा", "खम्मम", "वारंगल",
    ]

    @classmethod
    def detect_language(cls, text: str, fallback: str = "en") -> str:
        """Identifies Telugu, Hindi (Devanagari), or English."""
        for ch in text:
            if "\u0c00" <= ch <= "\u0c7f":
                return "te"
            if "\u0900" <= ch <= "\u097f":
                return "hi"
        return fallback if fallback in ["te", "hi", "en"] else "en"

    @classmethod
    def extract_crop(cls, text: str) -> Optional[str]:
        """Extracts crop name from query text."""
        lowered = text.lower()
        for token, normalized_name in cls.CROPS_MAP.items():
            if re.search(rf"\b{token}\b", lowered, re.IGNORECASE) or token in lowered:
                return normalized_name
        return None

    @classmethod
    def extract_location(cls, text: str) -> Optional[str]:
        """Extracts district or village name."""
        lowered = text.lower()
        for loc in cls.KNOWN_LOCATIONS:
            if re.search(rf"\b{loc}\b", lowered, re.IGNORECASE) or loc in lowered:
                return loc.capitalize()

        # Check prepositional patterns: "in Guntur", "at Miryalaguda"
        match = re.search(r"\b(?:in|at|near|from)\s+([A-Za-z]+)\b", text, re.IGNORECASE)
        if match:
            candidate = match.group(1).capitalize()
            if candidate.lower() not in ["my", "the", "a", "an", "this", "our", "that", "field", "farm"]:
                return candidate
        return None

    @classmethod
    def extract_damage_date(cls, text: str) -> Optional[str]:
        """Extracts damage date or relative time reference."""
        lowered = text.lower()
        date_terms = {
            "yesterday": "Yesterday",
            "day before yesterday": "2 days ago",
            "today": "Today",
            "last night": "Last night",
            "last week": "Last week",
            "2 days ago": "2 days ago",
            "3 days ago": "3 days ago",
            "నిన్న": "Yesterday",
            "ఈరోజు": "Today",
            "కల్": "Yesterday",
            "कल": "Yesterday",
            "आज": "Today",
        }
        for term, normalized_date in date_terms.items():
            if term in lowered:
                return normalized_date

        # Explicit date patterns like "23 Sept", "20-09-2026", "23/09"
        date_match = re.search(r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*(?:\s+\d{4})?\b", lowered)
        if date_match:
            return date_match.group(0).title()

        num_date_match = re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", lowered)
        if num_date_match:
            return num_date_match.group(0)

        return None

    @classmethod
    def extract_damage_extent(cls, text: str) -> Optional[str]:
        """Extracts damage extent or acreage."""
        lowered = text.lower()
        extent_keywords = {
            "half": "Approximately 50%",
            "about half": "Approximately 50%",
            "around half": "Approximately 50%",
            "completely": "Completely (100%)",
            "entire": "Entire field (100%)",
            "total": "Total (100%)",
            "partially": "Partially",
            "partial": "Partially",
            "most of it": "Approximately 75%",
            "సగం": "దాదాపు 50%",
            "పూర్తిగా": "పూర్తిగా (100%)",
            "ఆధా": "लगभग 50%",
            "पूरा": "पूरी तरह से (100%)",
        }
        for k, v in extent_keywords.items():
            if k in lowered:
                return v

        # Pattern: "50%", "2 acres", "1.5 hectares"
        match = re.search(r"\b\d+(?:\.\d+)?\s*(?:%|percent|acres?|hectares?|acres?)\b", lowered)
        if match:
            return match.group(0).capitalize()

        return None

    @classmethod
    def extract_photo_available(cls, text: str) -> Optional[bool]:
        """Detects if farmer reported photo availability using word boundaries."""
        lowered = text.lower()

        # Word boundary checks for single affirmative and negative tokens
        if re.search(r"\b(yes|yeah|yep|sure|హా|हाँ)\b", lowered):
            return True
        if re.search(r"\b(no|nope|nah|లేదు|नहीं)\b", lowered) and not re.search(r"\bno\s+rain\b", lowered):
            return False

        positives = [
            "i have photo", "have a photo", "photo available", "photos available",
            "took photo", "took photos", "have pictures", "photo is there",
            "ఉంది", "ఫోటో ఉంది", "తీశాను", "फोटो है", "तस्वीर है"
        ]
        negatives = [
            "no photo", "don't have", "do not have", "no picture",
            "తీసుకోలేదు", "नहीं है", "फोटो नहीं"
        ]

        for n in negatives:
            if n in lowered:
                return False
        for p in positives:
            if p in lowered:
                return True
        return None

    @classmethod
    def extract_damage_type(cls, text: str) -> Optional[str]:
        """Identifies damage cause/peril using retrieval service."""
        res = retrieve_insurance_guidance(text)
        if res.get("matched"):
            tid = res.get("topic_id", "")
            if tid in ["heavy_rain", "flood_waterlogging", "drought", "hailstorm", "storm_wind", "pest_disease"]:
                return tid

        # Keyword fallbacks
        lowered = text.lower()
        if any(w in lowered for w in ["heavy rain", "rain", "rainfall", "వర్షం", "बारिश"]):
            return "heavy_rain"
        if any(w in lowered for w in ["flood", "waterlogging", "waterlogged", "submerged", "వరద", "बाढ़", "जलभराव"]):
            return "flood_waterlogging"
        if any(w in lowered for w in ["drought", "dry", "drying", "no rain", "కరువు", "ఎండి", "सूखा"]):
            return "drought"
        if any(w in lowered for w in ["hail", "hailstorm", "hailstones", "వడగళ్ళు", "ओलावृष्टि", "ओले"]):
            return "hailstorm"
        if any(w in lowered for w in ["storm", "cyclone", "wind", "winds", "gale", "తుఫాను", "గాలివాన", "तूफान", "आंधी"]):
            return "storm_wind"
        if any(w in lowered for w in ["pest", "disease", "insects", "worms", "పురుగులు", "తెగుళ్ళు", "कीट", "रोग"]):
            return "pest_disease"

        return None

    @classmethod
    def format_damage_type_name(cls, damage_type: Optional[str], lang: str = "en") -> str:
        """Formats damage type for farmer reports."""
        labels = {
            "heavy_rain": {"en": "Heavy Rain", "te": "భారీ వర్షం", "hi": "भारी बारिश"},
            "flood_waterlogging": {"en": "Flood / Waterlogging", "te": "వరద / నీటి ముంపు", "hi": "बाढ़ एवं जलभराव"},
            "drought": {"en": "Drought / Dry Spell", "te": "కరువు / వర్షాభావం", "hi": "सूखा"},
            "hailstorm": {"en": "Hailstorm", "te": "వడగండ్ల వాన", "hi": "ओलावृष्टि"},
            "storm_wind": {"en": "Storm / Strong Winds", "te": "తుఫాను / ఈదురుగాలులు", "hi": "तूफान एवं तेज हवा"},
            "pest_disease": {"en": "Pest / Disease Attack", "te": "పురుగులు / తెగుళ్ల నష్టం", "hi": "कीट/रोग प्रकोप"},
        }
        entry = labels.get(damage_type or "", {"en": "Crop Damage", "te": "పంట నష్టం", "hi": "फसल क्षति"})
        return entry.get(lang, entry["en"])

    @classmethod
    def generate_preliminary_report(cls, state: Dict[str, Any], lang: str = "en") -> str:
        """Generates a clean, structured preliminary incident report with disclaimers."""
        crop = state.get("crop") or "Crop"
        cause = cls.format_damage_type_name(state.get("damage_type"), lang=lang)
        location = state.get("location") or "Reported Village/District"
        date = state.get("damage_date") or "Recently reported"
        extent = state.get("damage_extent") or "Under assessment"
        has_photo = state.get("damage_photo_available", False)

        if lang == "te":
            photo_status = "ఫోటో అందుబాటులో ఉంది" if has_photo else "ఫోటో ఇంకా నమోదు కాలేదు"
            desc = state.get("damage_description") or f"రైతు {cause} వల్ల {crop} పంటకు నష్టం వాటిల్లినట్లు ప్రాథమికంగా నమోదు చేశారు."
            return (
                "-----------------------------------\n"
                "పంట బీమా ప్రాథమిక సహాయ నివేదిక\n"
                "-----------------------------------\n\n"
                f"🌱 పంట: {crop}\n"
                f"⚠️ నష్టం కారణం: {cause}\n"
                f"📍 ప్రాంతం: {location}\n"
                f"📅 నష్టం జరిగిన సమయం: {date}\n"
                f"📊 అంచనా నష్టం: {extent}\n"
                f"📷 నష్ట ఆధారాలు: {photo_status}\n"
                f"📝 వివరణ: {desc}\n\n"
                "-----------------------------------\n"
                "తదుపరి చర్యలు:\n"
                "1. మీ పట్టాదార్ పాస్‌బుక్, ఆధార్ మరియు బ్యాంక్ వివరాలను సిద్ధంగా ఉంచుకోండి.\n"
                "2. నష్టపోయిన పంట ఫోటోలు మరియు ఆధారాలను భద్రపరచండి.\n"
                "3. స్థానిక వ్యవసాయ అధికారి (AEO) లేదా టోల్-ఫ్రీ నంబర్ (1800-180-1551) ద్వారా అధికారికంగా నష్టాన్ని నమోదు చేయండి.\n\n"
                "ముఖ్య గమనిక:\n"
                "ఇది కేవలం సమాచార సహాయ నివేదిక మాత్రమే. దీని ద్వారా బీమా క్లెయిమ్ నమోదైనట్లు లేదా ఆమోదించబడినట్లు కాదు. "
                "అర్హత మరియు పరిహార నిర్ణయం ప్రభుత్వం మరియు బీమా కంపెనీ అధికారిక సర్వే ఆధారంగా మాత్రమే జరుగుతుంది.\n"
                "-----------------------------------"
            )
        elif lang == "hi":
            photo_status = "तस्वीर उपलब्ध है" if has_photo else "तस्वीर अभी उपलब्ध नहीं है"
            desc = state.get("damage_description") or f"किसान ने {cause} के कारण {crop} फसल में नुकसान की सूचना दी है।"
            return (
                "-----------------------------------\n"
                "फसल बीमा प्रारंभिक सहायता रिपोर्ट\n"
                "-----------------------------------\n\n"
                f"🌱 फसल: {crop}\n"
                f"⚠️ नुकसान का कारण: {cause}\n"
                f"📍 स्थान: {location}\n"
                f"📅 नुकसान की तारीख: {date}\n"
                f"📊 अनुमानित नुकसान: {extent}\n"
                f"📷 क्षति साक्ष्य: {photo_status}\n"
                f"📝 विवरण: {desc}\n\n"
                "-----------------------------------\n"
                "अगले कदम:\n"
                "1. अपने भू-अभिलेख (खतौनी/पट्टा), आधार और बैंक पासबुक तैयार रखें।\n"
                "2. फसल क्षति की तस्वीरों और साक्ष्यों को सुरक्षित रखें।\n"
                "3. स्थानीय कृषि अधिकारी या राष्ट्रीय फसल बीमा टोल-फ्री (1800-180-1551) पर आधिकारिक सूचना दर्ज कराएं।\n\n"
                "महत्वपूर्ण सूचना:\n"
                "यह केवल एक प्रारंभिक सहायता रिपोर्ट है। इसका अर्थ यह नहीं है कि बीमा दावा प्रस्तुत या स्वीकृत हो गया है। "
                "पात्रता और मुआवजा आधिकारिक संयुक्त सर्वेक्षण और योजना नियमों पर निर्भर करता है।\n"
                "-----------------------------------"
            )
        else:
            photo_status = "Photo available" if has_photo else "No photo reported yet"
            desc = state.get("damage_description") or f"Farmer reported {cause} related damage to the {crop} crop."
            return (
                "-----------------------------------\n"
                "CROP INSURANCE ASSISTANCE REPORT\n"
                "-----------------------------------\n\n"
                f"Crop:             {crop}\n"
                f"Damage Cause:     {cause}\n"
                f"Location:         {location}\n"
                f"Damage Date:      {date}\n"
                f"Estimated Damage: {extent}\n"
                f"Damage Evidence:  {photo_status}\n"
                f"Description:      {desc}\n\n"
                "-----------------------------------\n"
                "NEXT STEPS:\n"
                "1. Keep relevant insurance/policy information available.\n"
                "2. Keep farmer, land (RoR/passbook), and bank passbook information ready.\n"
                "3. Preserve photographs/evidence of the field damage.\n"
                "4. Follow the applicable insurer/scheme's official reporting process.\n\n"
                "IMPORTANT:\n"
                "This is a preliminary assistance report. It does NOT mean that an insurance claim "
                "has been submitted, accepted, or approved. Requirements and eligibility may vary "
                "depending on the applicable scheme or insurer.\n"
                "-----------------------------------"
            )

    @classmethod
    def get_next_question(cls, missing_field: str, state: Dict[str, Any], lang: str = "en") -> str:
        """Returns the single next question tailored to the missing attribute."""
        crop = state.get("crop")
        crop_mention = f" for your {crop}" if crop else ""

        if missing_field == "damage_type":
            if lang == "te":
                return "మీ పంట ఏ కారణం వల్ల దెబ్బతింది (ఉదాహరణకు: భారీ వర్షం, వరద, కరువు, వడగండ్లు)?"
            elif lang == "hi":
                return "आपकी फसल किस कारण से क्षतिग्रस्त हुई (जैसे: भारी बारिश, बाढ़, सूखा, ओलावृष्टि)?"
            else:
                return "What caused the damage to your crop?"

        elif missing_field == "crop":
            if lang == "te":
                return "నష్టపోయిన పంట ఏది (ఉదాహరణకు: వరి, పత్తి, మిర్చి)?"
            elif lang == "hi":
                return "क्षतिग्रस्त फसल कौन सी है (जैसे: धान, कपास, मिर्च)?"
            else:
                return "Which crop was damaged?"

        elif missing_field == "location":
            if lang == "te":
                return "ఈ పంట నష్టం ఏ జిల్లా లేదా గ్రామంలో జరిగింది?"
            elif lang == "hi":
                return "यह फसल क्षति किस जिले या गाँव में हुई?"
            else:
                return "Which district or village did the damage occur in?"

        elif missing_field == "damage_date":
            if lang == "te":
                return "పంట నష్టం ఎప్పుడు జరిగింది (తేదీ లేదా సమయం)?"
            elif lang == "hi":
                return "फसल नुकसान कब हुआ (अनुमानित तारीख या समय)?"
            else:
                return "When did the damage happen (approximate date or time)?"

        elif missing_field == "damage_extent":
            if lang == "te":
                return "దాదాపు ఎంత విస్తీర్ణంలో లేదా ఎంత శాతం పంట నష్టపోయింది?"
            elif lang == "hi":
                return "लगभग कितना क्षेत्र या कितना प्रतिशत फसल प्रभावित हुई है?"
            else:
                return "Approximately how much of the crop was affected?"

        elif missing_field == "damage_photo_available":
            if lang == "te":
                return "దెబ్బతిన్న పంట ఫోటోలు ఏమైనా మీ వద్ద ఉన్నాయా?"
            elif lang == "hi":
                return "क्या आपके पास क्षतिग्रस्त फसल की तस्वीरें हैं?"
            else:
                return "Do you have a photo of the damaged crop?"

        if lang == "te":
            return "పంట నష్టానికి సంబంధించి మరిన్ని వివరాలు చెప్పగలరా?"
        elif lang == "hi":
            return "क्या आप फसल क्षति के बारे में कुछ और विवरण दे सकते हैं?"
        return "Could you provide any additional details about the damage?"

    @classmethod
    def execute(
        cls,
        farmer_id: str,
        query: str,
        language: str = "en",
        context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main execution entry point for Orchestrator and API.
        Processes query, maintains state, and outputs one question or preliminary report.
        """
        lang = cls.detect_language(query, fallback=language)
        trimmed = query.strip()

        # -------------------------------------------------------------
        # STEP 1: Check for general queries via Retrieval Service
        # (Documents, Claim Process, Safety, Guarantee, Out-of-domain)
        # -------------------------------------------------------------
        retrieval = retrieve_insurance_guidance(trimmed, language=lang)
        matched_topic = retrieval.get("topic_id", "unknown")

        # 1A: Guarantee Inquiry (Refuse claim guarantees explicitly)
        if matched_topic == "no_guarantee_notice":
            if lang == "te":
                msg = (
                    "🛡️ [క్లెయిమ్ గ్యారెంటీ సమాచారం]:\n"
                    "కిసాన్ సారథి లేదా ఏ ఇతర యాప్ కూడా బీమా క్లెయిమ్ ఆమోదం లేదా పరిహారాన్ని హామీ (గ్యారెంటీ) ఇవ్వలేదు.\n"
                    "బీమా క్లెయిమ్ ఆమోదం అనేది అధికారిక క్షేత్ర స్థాయి సంయుక్త సర్వే (Joint Field Survey), "
                    "వాతావరణ రికార్డులు మరియు ప్రభుత్వం/బీమా కంపెనీ నిబంధనల ప్రకారం మాత్రమే నిర్ణయించబడుతుంది."
                )
            elif lang == "hi":
                msg = (
                    "🛡️ [दावा गारंटी स्पष्टीकरण]:\n"
                    "किसान सारथी या कोई भी ऐप दावा स्वीकृति या मुआवजे के भुगतान की गारंटी नहीं दे सकता।\n"
                    "दावा स्वीकृति पूरी तरह से सरकारी दिशानिर्देशों, संयुक्त क्षेत्र निरीक्षण और बीमा कंपनी के आधिकारिक नियमों पर निर्भर करती है।"
                )
            else:
                msg = (
                    "🛡️ [Claim Guarantee Notice]:\n"
                    "KisanSaarthi cannot guarantee claim approval or payment. "
                    "Eligibility and settlement depend entirely on the applicable scheme, "
                    "official joint loss surveys, threshold yields, and designated insurer rules."
                )
            return {
                "agent": cls.name,
                "intent": "insurance_assistance",
                "status": "ready",
                "response": msg,
                "text": msg,
                "missing_information": [],
                "retrieved_topic": "no_guarantee_notice",
                "guidance": retrieval.get("guidance", ""),
                "report": None,
            }

        # 1B: Document Checklist Question (Direct answer without starting incident interview)
        if matched_topic == "documents_guidance" and not (cls.extract_crop(trimmed) or cls.extract_damage_type(trimmed)):
            guidance = retrieval.get("guidance", "")
            docs = retrieval.get("information_to_collect", [])
            steps = retrieval.get("general_next_steps", [])
            if lang == "te":
                msg = (
                    "📄 [పంట బీమాకు ఉపయోగపడే పత్రాలు]:\n"
                    "సాధారణంగా బీమా సహాయం కోసం ఈ క్రింది పత్రాలు అవసరం కావచ్చు (వర్తించే పథకం ప్రకారం మారవచ్చు):\n" +
                    "\n".join(f"• {d}" for d in docs) +
                    f"\n\nసూచన: {guidance}"
                )
            elif lang == "hi":
                msg = (
                    "📄 [फसल बीमा के लिए उपयोगी दस्तावेज]:\n"
                    "सामान्यतः दावे के समय निम्नलिखित दस्तावेज आवश्यक हो सकते हैं (योजना अनुसार भिन्न हो सकते हैं):\n" +
                    "\n".join(f"• {d}" for d in docs) +
                    f"\n\nमार्गदर्शन: {guidance}"
                )
            else:
                msg = (
                    "📄 [Useful Documents for Crop Insurance]:\n"
                    "Depending on the applicable scheme and state rules, the following documents may be required:\n" +
                    "\n".join(f"• {d}" for d in docs) +
                    f"\n\nGuidance: {guidance}"
                )
            return {
                "agent": cls.name,
                "intent": "insurance_assistance",
                "status": "ready",
                "response": msg,
                "text": msg,
                "missing_information": [],
                "retrieved_topic": "documents_guidance",
                "guidance": guidance,
                "report": None,
            }

        # 1C: Claim Process Inquiry (Direct answer)
        if matched_topic == "claim_process" and not (cls.extract_crop(trimmed) or cls.extract_damage_type(trimmed)):
            guidance = retrieval.get("guidance", "")
            steps = retrieval.get("general_next_steps", [])
            if lang == "te":
                msg = (
                    "📋 [పంట బీమా క్లెయిమ్ సాధారణ ప్రక్రియ]:\n"
                    f"{guidance}\n\n"
                    "ప్రధాన చర్యలు:\n" + "\n".join(f"• {s}" for s in steps)
                )
            elif lang == "hi":
                msg = (
                    "📋 [फसल बीमा दावा सामान्य प्रक्रिया]:\n"
                    f"{guidance}\n\n"
                    "प्रमुख चरण:\n" + "\n".join(f"• {s}" for s in steps)
                )
            else:
                msg = (
                    "📋 [General Crop Insurance Claim Process]:\n"
                    f"{guidance}\n\n"
                    "Key Next Steps:\n" + "\n".join(f"• {s}" for s in steps)
                )
            return {
                "agent": cls.name,
                "intent": "insurance_assistance",
                "status": "ready",
                "response": msg,
                "text": msg,
                "missing_information": [],
                "retrieved_topic": "claim_process",
                "guidance": guidance,
                "report": None,
            }

        # 1D: Anti-Fraud Safety Inquiry (Direct answer)
        if matched_topic == "safety_verification":
            guidance = retrieval.get("guidance", "")
            steps = retrieval.get("general_next_steps", [])
            if lang == "te":
                msg = (
                    "🛡️ [రక్షణ & మోసాల నివారణ మార్గదర్శకం]:\n"
                    f"{guidance}\n\n"
                    "రక్షణ సూచనలు:\n" + "\n".join(f"• {s}" for s in steps)
                )
            elif lang == "hi":
                msg = (
                    "🛡️ [सुरक्षा और धोखाधड़ी रोकथाम मार्गदर्शन]:\n"
                    f"{guidance}\n\n"
                    "सुरक्षा सुझाव:\n" + "\n".join(f"• {s}" for s in steps)
                )
            else:
                msg = (
                    "🛡️ [Anti-Fraud & Safety Guidance]:\n"
                    f"{guidance}\n\n"
                    "Safety Tips:\n" + "\n".join(f"• {s}" for s in steps)
                )
            return {
                "agent": cls.name,
                "intent": "insurance_assistance",
                "status": "ready",
                "response": msg,
                "text": msg,
                "missing_information": [],
                "retrieved_topic": "safety_verification",
                "guidance": guidance,
                "report": None,
            }

        # -------------------------------------------------------------
        # STEP 2: Crop Damage Incident Flow & Multi-Turn Interview
        # -------------------------------------------------------------
        session_key = f"{farmer_id}_insurance"
        state = {
            "crop": None,
            "damage_type": None,
            "location": None,
            "damage_date": None,
            "damage_extent": None,
            "damage_description": None,
            "damage_photo_available": False,
            "policy_information_available": False,
        }

        # 2A: Recall active state from DB or memory
        db_request = None
        if db:
            # Check for existing request if request_id provided or latest active
            if request_id:
                db_request = repository.get_request(db, request_id)
            else:
                existing_reqs = repository.list_farmer_requests(db, farmer_id=farmer_id)
                for req in existing_reqs:
                    if req.type == "insurance_assistance" and req.status == "information_collection":
                        db_request = req
                        break

            if db_request and db_request.result:
                try:
                    loaded = json.loads(db_request.result)
                    if isinstance(loaded, dict) and "state" in loaded:
                        state.update(loaded["state"])
                except Exception:
                    pass
        elif session_key in _SESSION_STATES:
            state.update(_SESSION_STATES[session_key])

        # 2B: Extract new parameters from current turn
        new_crop = cls.extract_crop(trimmed)
        new_cause = cls.extract_damage_type(trimmed)
        new_loc = cls.extract_location(trimmed)
        new_date = cls.extract_damage_date(trimmed)
        new_extent = cls.extract_damage_extent(trimmed)
        new_photo = cls.extract_photo_available(trimmed)

        # Check if query is out-of-domain with no active insurance context or crop/damage entities
        has_active_state = bool(state["crop"] or state["damage_type"])
        has_entities = bool(new_crop or new_cause or (has_active_state and (new_loc or new_date or new_extent or new_photo is not None)))

        if not retrieval.get("matched") and not has_active_state and not has_entities:
            fallback_msg = get_unverified_fallback_message(lang)
            return {
                "agent": cls.name,
                "intent": "insurance_assistance",
                "status": "needs_clarification",
                "response": fallback_msg,
                "text": fallback_msg,
                "missing_information": [],
                "retrieved_topic": "unknown",
                "guidance": "",
                "report": None,
            }

        if new_crop and not state["crop"]:
            state["crop"] = new_crop
        if new_cause and not state["damage_type"]:
            state["damage_type"] = new_cause
        if new_loc and not state["location"]:
            state["location"] = new_loc
        if new_date and not state["damage_date"]:
            state["damage_date"] = new_date
        if new_extent and not state["damage_extent"]:
            state["damage_extent"] = new_extent
        if new_photo is not None:
            state["damage_photo_available"] = new_photo

        if not state["damage_description"] and state["damage_type"] and state["crop"]:
            cause_name = cls.format_damage_type_name(state["damage_type"], lang="en")
            state["damage_description"] = f"Farmer reported {cause_name} damage to the {state['crop']} crop."

        # 2C: Identify missing information in priority order
        missing = []
        if not state["damage_type"]:
            missing.append("damage_type")
        if not state["crop"]:
            missing.append("crop")
        if not state["location"]:
            missing.append("location")
        if not state["damage_date"]:
            missing.append("damage_date")
        if not state["damage_extent"]:
            missing.append("damage_extent")
        if new_photo is None and not state["damage_photo_available"]:
            # Prompt photo as final optional piece of evidence
            missing.append("damage_photo_available")

        # -------------------------------------------------------------
        # STEP 3: Generate Response: Ask Next Question OR Generate Report
        # -------------------------------------------------------------
        if missing:
            # Still collecting information -> ask exactly ONE single question
            next_field = missing[0]
            next_q = cls.get_next_question(next_field, state, lang=lang)
            status_code = "information_collection"
            report_content = None
            response_text = next_q
        else:
            # All essential fields collected -> Generate Preliminary Incident Report
            status_code = "report_generated"
            next_q = None
            report_content = cls.generate_preliminary_report(state, lang=lang)
            response_text = report_content

        # -------------------------------------------------------------
        # STEP 4: Persist Updated State to Database and Memory
        # -------------------------------------------------------------
        payload_result = json.dumps({
            "state": state,
            "missing_information": missing,
            "status": status_code,
            "report": report_content,
        })

        req_id = f"REQ-INS-{uuid.uuid4().hex[:8].upper()}"
        if db:
            if db_request:
                db_request.status = status_code
                db_request.current_step = f"Waiting for: {missing[0]}" if missing else "Report generated"
                db_request.result = payload_result
                db.commit()
                req_id = db_request.id
            else:
                new_req = repository.create_request(
                    db,
                    farmer_id=farmer_id,
                    type="insurance_assistance",
                    status=status_code,
                    current_step=f"Waiting for: {missing[0]}" if missing else "Report generated",
                    result=payload_result,
                )
                req_id = new_req.id

        _SESSION_STATES[session_key] = state

        return {
            "agent": cls.name,
            "request_id": req_id,
            "intent": "insurance_assistance",
            "status": status_code,
            "message": response_text,
            "response": response_text,
            "text": response_text,
            "next_question": next_q,
            "missing_information": missing,
            "collected_information": state,
            "retrieved_topic": state.get("damage_type") or matched_topic,
            "report": report_content,
        }

    @classmethod
    def reset_session(cls, farmer_id: str):
        """Clears in-memory session cache for farmer."""
        session_key = f"{farmer_id}_insurance"
        if session_key in _SESSION_STATES:
            del _SESSION_STATES[session_key]
