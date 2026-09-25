"""
KisanSaarthi Insurance Knowledge Base Retrieval Service.

Provides simple, reliable, and deterministic retrieval of crop insurance
guidance based on farmer query topic and keyword matching.
No complex vector databases or non-deterministic embeddings are used.
Adheres strictly to general assistance principles without hallucinating rules.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "insurance")

GENERAL_DISCLAIMER = (
    "This guidance is for general informational assistance only. Specific terms, deadlines, "
    "and documentation requirements may vary depending on the applicable scheme (e.g. PMFBY/RWBCIS), "
    "state government notifications, and designated insurer. Always verify with your local "
    "Agriculture Extension Officer, bank branch, or official scheme portal."
)

UNVERIFIED_FALLBACK_MESSAGE = (
    "I don't have enough verified information to answer that reliably. "
    "Please check the applicable insurer or official scheme guidance."
)

UNVERIFIED_FALLBACK_MESSAGES = {
    "te": "ఖచ్చితంగా సమాధానం ఇవ్వడానికి నా వద్ద తగినంత ధృవీకరించిన సమాచారం లేదు. దయచేసి సంబంధిత బీమా కంపెనీ లేదా అధికారిక పథక మార్గదర్శకాలను సంప్రదించండి.",
    "hi": "सटीक उत्तर देने के लिए मेरे पास पर्याप्त सत्यापित जानकारी उपलब्ध नहीं है। कृपया संबंधित बीमा कंपनी या आधिकारिक योजना के दिशानिर्देशों की जांच करें।",
    "en": UNVERIFIED_FALLBACK_MESSAGE,
}

GENERAL_DISCLAIMERS = {
    "te": (
        "ఈ మార్గదర్శకం సాధారణ సమాచార సహాయం కొరకు మాత్రమే. నిర్దిష్ట నిబంధనలు, గడువులు మరియు అవసరమైన పత్రాలు "
        "వర్తించే పథకం (ఉదా. PMFBY/RWBCIS), రాష్ట్ర ప్రభుత్వ నోటిఫికేషన్‌లు మరియు కేటాయించిన బీమా సంస్థపై ఆధారపడి మారవచ్చు. "
        "ఎల్లప్పుడూ మీ స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO), బ్యాంక్ బ్రాంచ్ లేదా అధికారిక పథక పోర్టల్‌లో ధృవీకరించుకోండి."
    ),
    "hi": (
        "यह मार्गदर्शन केवल सामान्य सूचनात्मक सहायता के लिए है। विशिष्ट शर्तें, समय सीमा और आवश्यक दस्तावेज "
        "लागू योजना (जैसे PMFBY/RWBCIS), राज्य सरकार की अधिसूचनाओं और नामित बीमा कंपनी के आधार पर भिन्न हो सकते हैं। "
        "हमेशा अपने स्थानीय कृषि विस्तार अधिकारी, बैंक शाखा या आधिकारिक योजना पोर्टल से सत्यापन करें।"
    ),
    "en": GENERAL_DISCLAIMER,
}


def get_unverified_fallback_message(language: str = "en") -> str:
    """Returns unverified notice in the farmer's preferred language."""
    lang = (language or "en").lower()[:2]
    return UNVERIFIED_FALLBACK_MESSAGES.get(lang, UNVERIFIED_FALLBACK_MESSAGES["en"])


def get_general_disclaimer(language: str = "en") -> str:
    """Returns general assistance disclaimer in the farmer's preferred language."""
    lang = (language or "en").lower()[:2]
    return GENERAL_DISCLAIMERS.get(lang, GENERAL_DISCLAIMERS["en"])

# In-memory cache for knowledge entries
_KNOWLEDGE_CACHE: Optional[List[Dict[str, Any]]] = None


def load_knowledge_base(force_reload: bool = False) -> List[Dict[str, Any]]:
    """
    Loads all JSON knowledge files from backend/knowledge/insurance/ into memory.
    """
    global _KNOWLEDGE_CACHE
    if _KNOWLEDGE_CACHE is not None and not force_reload:
        return _KNOWLEDGE_CACHE

    entries: List[Dict[str, Any]] = []
    if not os.path.exists(KNOWLEDGE_DIR):
        _KNOWLEDGE_CACHE = entries
        return entries

    json_files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".json")]
    for filename in sorted(json_files):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    entries.extend(data)
                elif isinstance(data, dict):
                    entries.append(data)
        except Exception as e:
            print(f"[InsuranceRetrievalService] Error loading {file_path}: {e}")

    _KNOWLEDGE_CACHE = entries
    return entries


def normalize_text(text: str) -> str:
    """
    Normalizes query text by lowercasing and standardizing whitespace.
    Retains non-Latin characters (Telugu, Hindi, etc.) and punctuation-stripped alphanumeric.
    """
    if not text:
        return ""
    lowered = text.lower()
    # Replace punctuation with spaces while keeping unicode letters and numbers
    cleaned = re.sub(r"[^\w\s\u0900-\u097F\u0C00-\u0C7F]", " ", lowered)
    return " ".join(cleaned.split())


def score_entry(normalized_query: str, entry: Dict[str, Any]) -> float:
    """
    Computes a relevance score for an entry against the normalized query.
    Higher score indicates higher keyword/phrase alignment.
    """
    score = 0.0
    keywords = entry.get("keywords", [])
    topic_id = entry.get("id", "")
    topic_title = entry.get("topic", "").lower()

    # Exact topic match
    if topic_id in normalized_query:
        score += 8.0
    if topic_title and topic_title in normalized_query:
        score += 8.0

    query_words = set(normalized_query.split())

    for kw in keywords:
        kw_norm = normalize_text(kw)
        if not kw_norm:
            continue

        # Multi-word phrase matching
        if " " in kw_norm:
            if kw_norm in normalized_query:
                # Reward exact continuous multi-word phrases significantly
                word_count = len(kw_norm.split())
                score += 6.0 * word_count
            else:
                kw_word_set = set(kw_norm.split())
                if len(kw_word_set) >= 2 and kw_word_set.issubset(query_words):
                    score += 4.0 * len(kw_word_set)
        else:
            # Single-word matching with boundary checks
            if kw_norm in query_words:
                score += 3.5
            elif len(kw_norm) > 4 and kw_norm in normalized_query:
                score += 1.5

    return score


def retrieve_insurance_guidance(query: str, language: str = "en") -> Dict[str, Any]:
    """
    Retrieves the most relevant insurance guidance entry for a given farmer query.
    If no topic achieves reliable confidence, returns an unverified fallback response.

    Args:
        query: Farmer's natural language inquiry or loss description.
        language: Preferred language code ('en', 'te', 'hi').

    Returns:
        Structured dictionary with matched guidance or fallback notice.
    """
    fallback_message = get_unverified_fallback_message(language)

    if not query or not query.strip():
        return {
            "topic": "unknown",
            "topic_id": "unknown",
            "matched": False,
            "message": fallback_message,
        }

    entries = load_knowledge_base()
    if not entries:
        return {
            "topic": "unknown",
            "topic_id": "unknown",
            "matched": False,
            "message": fallback_message,
        }

    norm_q = normalize_text(query)

    # Score all entries
    best_entry: Optional[Dict[str, Any]] = None
    best_score = 0.0

    for entry in entries:
        s = score_entry(norm_q, entry)
        if s > best_score:
            best_score = s
            best_entry = entry

    # Minimum threshold for reliable retrieval
    MINIMUM_CONFIDENCE_THRESHOLD = 3.5

    if not best_entry or best_score < MINIMUM_CONFIDENCE_THRESHOLD:
        return {
            "topic": "unknown",
            "topic_id": "unknown",
            "matched": False,
            "message": fallback_message,
        }

    # Return structured guidance
    return {
        "topic": best_entry.get("topic", "Crop Insurance Guidance"),
        "topic_id": best_entry.get("id", "general"),
        "matched": True,
        "score": round(best_score, 2),
        "guidance": best_entry.get("guidance", ""),
        "information_to_collect": best_entry.get("information_to_collect", []),
        "useful_evidence": best_entry.get("useful_evidence", []),
        "general_next_steps": best_entry.get("general_next_steps", []),
        "disclaimer": get_general_disclaimer(language),
    }


def get_all_topics() -> List[Dict[str, str]]:
    """
    Returns a list of all supported insurance topics in the knowledge base.
    """
    entries = load_knowledge_base()
    return [{"id": e.get("id", ""), "topic": e.get("topic", "")} for e in entries]
