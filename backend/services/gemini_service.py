"""
Gemini AI Generative Service for KisanSaarthi AI.

Provides real-time open-ended agronomic intelligence for farmers:
- Dynamic FarmGPT-style agricultural question answering
- System-level agriculture persona and out-of-domain rejection
- Safety guardrails (no chemical dosage hallucination, AEO/KVK expert referral)
- Intelligent single follow-up questions for vague farmer queries
- Multi-turn conversation context tracking
- Native multilingual support for English, Telugu, and Hindi
"""

import re
import sys
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from config import settings

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-flash-latest"]

AGRICULTURE_SYSTEM_PROMPT = """You are KisanSaarthi, an AI agricultural assistant designed to help farmers understand farming problems and make better-informed agricultural decisions.

Your core operating principles:
1. Farmer-First Communication:
   - Use clear, practical, and conversational language suitable for rural farmers.
   - Avoid unnecessary academic jargon or overly complex technical terminology. Explain concepts simply and directly.
   - Give a direct answer before providing additional details or context.

2. Agricultural Scope & Out-of-Domain Guard:
   - Your sole domain is agriculture, farming, crops, sowing, planting, seeds, germination, irrigation, soil, soil fertility, fertilizers, manure, organic farming, pests, crop diseases, weeds, harvesting, post-harvest practices, storage, weather impact on farming, crop rotation, intercropping, sustainable agriculture, and farm equipment concepts.
   - If a question is COMPLETELY UNRELATED to agriculture (e.g. software programming, movies, sports, video games, general trivia, politics), politely decline and explain: "I am KisanSaarthi, an AI assistant dedicated specifically to farming and agriculture. I cannot assist with this topic, but I am happy to help with any crop, soil, weather, or farming questions."

3. Multilingual Fidelity:
   - Respond in the language requested by the farmer (English, Telugu, or Hindi).
   - If the farmer asks in Telugu or Hindi, respond naturally in authentic Telugu or Hindi script.
   - Do not unnecessarily mix languages or switch scripts mid-sentence.

4. Safety & Chemical Responsibility:
   - For chemical fertilizers, pesticides, insecticides, fungicides, or weedicides: NEVER invent chemical dosages or provide blind chemical spray prescriptions.
   - Always advise checking the manufacturer's product label for exact dosage and dilution rates.
   - Emphasize wearing protective gear (masks, gloves) during chemical application.
   - Recommend consulting the local Agricultural Extension Officer (AEO), Krishi Vigyan Kendra (KVK), or Rythu Bharosa Kendra (RBK) before applying hazardous chemicals.
   - For crop disease diagnosis without an image: Explain that foliar symptoms (like yellowing or spotting) can have multiple causes (fungal, bacterial, viral, or nutrient deficiency). Recommend taking a clear close-up leaf photo and using KisanSaarthi's Crop Health feature for image analysis.

5. Intelligent Follow-up for Vague Queries:
   - If a farmer asks a very broad or underspecified question (e.g. "My crop is not growing well", "Leaves are turning yellow"), provide a brief direct explanation of the common causes, and ask ONLY ONE useful, focused follow-up question to gather critical context (e.g. "Which crop are you growing, and approximately how many days old is it?").

6. Response Style & Structure:
   - For direct questions: Give a clear direct answer, followed by 2-4 practical action points.
   - For practical farming problems:
     1. What may be happening
     2. What to check in the field
     3. Practical next steps
     4. When to contact a local agricultural expert
   - Keep answers practical, actionable, and encouraging.
"""

# Language prompt instructions
LANGUAGE_INSTRUCTIONS = {
    "te": "IMPORTANT: You MUST respond entirely in Telugu (తెలుగు లిపి). Use clear, authentic Telugu suitable for farmers in Telangana and Andhra Pradesh.",
    "hi": "IMPORTANT: You MUST respond entirely in Hindi (हिंदी देवनागरी लिपि). Use simple, farmer-friendly Hindi vocabulary.",
    "en": "IMPORTANT: You MUST respond in clear, simple English suitable for farmers.",
}


def format_chat_history(conversation_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sanitizes conversation history into alternating 'user' and 'model' turns
    required by the Gemini SDK.
    """
    if not conversation_context:
        return []

    formatted = []
    for item in conversation_context:
        sender = (item.get("sender") or "").lower()
        content = item.get("message") or item.get("text") or item.get("content") or ""
        content = content.strip()
        if not content:
            continue

        role = "user" if sender in ["user", "farmer"] else "model"

        # Ensure strict turn alternation
        if formatted and formatted[-1]["role"] == role:
            formatted[-1]["parts"][0] = f"{formatted[-1]['parts'][0]}\n{content}"
        else:
            formatted.append({"role": role, "parts": [content]})

    # Gemini requires first history turn to be 'user'
    while formatted and formatted[0]["role"] != "user":
        formatted.pop(0)

    # Gemini requires last history turn before send_message to be 'model'
    while formatted and formatted[-1]["role"] == "user":
        formatted.pop(-1)

    return formatted


def generate_agriculture_response(
    message: str,
    language: str = "en",
    conversation_context: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generates a dynamic, conversational agricultural response using Google Gemini.
    """
    trimmed = message.strip()
    api_key = settings.GEMINI_API_KEY

    # Detect language if not explicitly provided
    lang = language
    for ch in trimmed:
        if "\u0c00" <= ch <= "\u0c7f":
            lang = "te"
            break
        elif "\u0900" <= ch <= "\u097f":
            lang = "hi"
            break

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS["en"])

    # Fallback if no valid API key is present
    if not api_key or api_key == "your_gemini_api_key_here":
        fallback_msg = _generate_resilient_fallback(trimmed, lang)
        return {
            "response": fallback_msg,
            "text": fallback_msg,
            "language": lang,
            "model": "local_fallback",
            "status": "ready",
            "agent": "General Agriculture AI",
            "is_out_of_domain": False,
        }

    # Configure Gemini SDK
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        fallback_msg = _generate_resilient_fallback(trimmed, lang)
        return {
            "response": fallback_msg,
            "text": fallback_msg,
            "language": lang,
            "model": "local_fallback",
            "status": "ready",
            "agent": "General Agriculture AI",
            "is_out_of_domain": False,
        }

    # Prepare chat prompt with language instruction
    user_prompt = f"{trimmed}\n\n[Instruction: {lang_instruction}]"

    # Models to attempt in priority order
    candidate_models = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    last_error = None

    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=AGRICULTURE_SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    temperature=0.35,
                    top_p=0.95,
                    max_output_tokens=1000,
                ),
            )

            history = format_chat_history(conversation_context or [])

            if history:
                chat = model.start_chat(history=history)
                response = chat.send_message(user_prompt, request_options={"timeout": 15})
            else:
                response = model.generate_content(user_prompt, request_options={"timeout": 15})

            response_text = response.text.strip()
            if response_text:
                # Detect out-of-domain flag from content
                is_ood = bool(
                    re.search(
                        r"\b(only\s*help\s*with|dedicated\s*specifically\s*to|focuses\s*on\s*agriculture|cannot\s*assist\s*with\s*this\s*topic|వ్యవసాయానికి\s*మాత్రమే|कृषि\s*तक\s*ही\s*सीमित)\b",
                        response_text,
                        re.IGNORECASE,
                    )
                )

                return {
                    "response": response_text,
                    "text": response_text,
                    "language": lang,
                    "model": model_name,
                    "status": "ready",
                    "agent": "General Agriculture AI",
                    "is_out_of_domain": is_ood,
                }
        except Exception as err:
            last_error = err
            continue

    # Graceful fallback if all remote models fail or quota is exceeded
    fallback_text = _generate_resilient_fallback(trimmed, lang)
    return {
        "response": fallback_text,
        "text": fallback_text,
        "language": lang,
        "model": "local_fallback",
        "status": "ready",
        "agent": "General Agriculture AI",
        "is_out_of_domain": False,
        "error": str(last_error) if last_error else None,
    }


def _generate_resilient_fallback(query: str, lang: str = "en") -> str:
    """Provides a safe, practical fallback message when Gemini API is unreachable."""
    if lang == "te":
        return (
            "🌱 [కిసాన్ సారథి వ్యవసాయ సలహాదారు]:\n"
            "మీ వ్యవసాయ ప్రశ్నకు ధన్యవాదాలు. పంట యాజమాన్యం, నేల సారవంతం, నీటి పారుదల మరియు తెగుళ్ల నివారణకు సంబంధించిన ఖచ్చితమైన వివరాల కోసం స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO) లేదా రైతు భరోసా కేంద్రాన్ని (RBK) సంప్రదించండి.\n\n"
            "పంట ఆకులపై తెగుళ్లు ఉంటే స్పష్టమైన ఫోటోను తీసి కిసాన్ సారథి క్రాప్ హెల్త్ ఫీచర్‌లో అప్‌లోడ్ చేయండి."
        )
    elif lang == "hi":
        return (
            "🌱 [किसान सारथी कृषि सलाहकार]:\n"
            "आपके कृषि संबंधी प्रश्न के लिए धन्यवाद। फसल प्रबंधन, मिट्टी की उर्वरता, सिंचाई एवं कीट नियंत्रण की सटीक जानकारी के लिए अपने स्थानीय कृषि विस्तार अधिकारी या कृषि विज्ञान केंद्र (KVK) से संपर्क करें।\n\n"
            "यदि पत्तियों पर कोई बीमारी है, तो उसकी साफ़ फ़ोटो किसान सारथी क्रॉप हेल्थ में अपलोड करें।"
        )
    else:
        return (
            "🌱 [KisanSaarthi Agricultural Advisor]:\n"
            "Thank you for your farming inquiry. For best agronomic practices suited to your local soil and climate, "
            "we recommend consulting your local Agricultural Extension Officer (AEO) or Krishi Vigyan Kendra (KVK).\n\n"
            "If your crops show visible symptoms, please take a clear close-up leaf photo and upload it via our Crop Health feature for disease analysis."
        )
