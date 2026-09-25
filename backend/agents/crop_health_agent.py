"""
Crop Health Specialized Agent for KisanSaarthi AI.

RESPONSIBILITIES:
- Accepts farmer query and uploaded crop leaf image.
- Validates image presence and integrity.
- Sends actual image to Real Vision Service (Gemini Vision or Local Spectral Engine).
- Grounds findings in curated agricultural knowledge base (ICAR guidelines).
- Formulates safe, non-technical, farmer-friendly explanations.
- Never guarantees a diagnosis or prescribes toxic chemicals.
- Follows requested response language (English, Telugu, Hindi).
- Persists request workflow state in SQLite database.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from models.crop import CropHealthResult
from services.disease_model_service import (
    predict_crop_disease,
    SUPPORTED_CROPS,
    SUPPORTED_CLASSES,
    MODEL_NAME,
    DATASET_NAME,
)
from services.vision_service import analyze_crop_image, validate_crop_image
from tools.crop_tool import find_crop_knowledge
from database import repository


class CropHealthAgent:
    name = "Crop Health Agent"

    @classmethod
    def process_request(
        cls,
        farmer_id: str = "F001",
        message: str = "",
        language: str = "te",
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        filename: Optional[str] = None,
        crop_name: Optional[str] = None,
        location: Optional[str] = None,
        growth_stage: Optional[str] = None,
        is_low_confidence: bool = False,
        db: Optional[Session] = None,
    ) -> CropHealthResult:
        """
        Complete end-to-end Crop Health Agent workflow:
        Image -> Real Vision -> Knowledge Base Grounding -> Farmer-Friendly Explanation
        """
        lang = language if language in ["te", "hi", "en"] else "te"
        trimmed_msg = (message or "").strip()

        # -------------------------------------------------------------
        # STEP 1: VALIDATE IMAGE PRESENCE
        # -------------------------------------------------------------
        if image_bytes is None and image_path is None:
            if lang == "te":
                response_text = (
                    "దయచేసి మీ పంట సమస్యను గుర్తించడానికి దెబ్బతిన్న పంట లేదా ఆకుల ఫోటోను తీసి అప్‌లోడ్ చేయండి. "
                    "నేను దానిని పరిశీలించి మీకు తగిన సలహా ఇవ్వగలను."
                )
                next_q = "దయచేసి దెబ్బతిన్న పంట ఆకుల ఫోటోను అప్‌లోడ్ చేయండి."
            elif lang == "hi":
                response_text = (
                    "कृपया अपनी फसल की समस्या जांचने के लिए प्रभावित फसल या पत्तियों की एक साफ़ फ़ोटो अपलोड करें। "
                    "ताकि मैं उसकी जांच कर आपकी सही मदद कर सकूँ।"
                )
                next_q = "कृपया प्रभावित फसल की पत्ती की एक साफ़ फ़ोटो अपलोड करें।"
            else:
                response_text = (
                    "Please take or upload a clear photo of the affected crop leaf so I can examine it for you."
                )
                next_q = "Please upload a clear photo of the affected crop leaf."

            req_id = cls._record_request(db, farmer_id, "crop_health", "needs_image", response_text, lang)

            return CropHealthResult(
                farmer_id=farmer_id,
                crop=crop_name,
                possible_issue=None,
                possible_problem=None,
                confidence=None,
                uncertain=True,
                visible_symptoms=[],
                evidence=[],
                observations=[],
                knowledge_found=False,
                safe_next_steps=[],
                prevention=[],
                when_to_contact_expert=None,
                recommendations=[],
                warning="No image provided. A clear crop photo is required for visual analysis.",
                language=lang,
                status="needs_image",
                response=response_text,
                next_question=next_q,
                agent=cls.name,
                request_id=req_id,
            )

        # -------------------------------------------------------------
        # STEP 2: VALIDATE IMAGE INTEGRITY
        # -------------------------------------------------------------
        is_valid, val_status, val_reason, raw_bytes = validate_crop_image(
            image_bytes=image_bytes,
            image_path=image_path,
            filename=filename,
        )

        if not is_valid:
            if lang == "te":
                response_text = (
                    "ఈ ఫోటోలో పంట స్పష్టంగా కనిపించడం లేదు లేదా ఫైల్ సరిగ్గా లేదు. "
                    "దయచేసి మంచి వెలుతురులో, ఆకులపై దగ్గరగా (close-up) స్పష్టమైన ఫోటో తీసి మళ్లీ పంపండి."
                )
            elif lang == "hi":
                response_text = (
                    "इस फ़ोटो में फसल साफ़ दिखाई नहीं दे रही है या फ़ाइल अमान्य है। "
                    "कृपया अच्छी रोशनी में पत्तियों की एक नज़दीकी (क्लोज़-अप) साफ़ फ़ोटो लें।"
                )
            else:
                response_text = (
                    "I couldn't get a clear view of the crop from this photo. "
                    "Please take a closer, well-lit photo of the affected leaves."
                )

            req_id = cls._record_request(db, farmer_id, "crop_health", val_status, response_text, lang)

            return CropHealthResult(
                farmer_id=farmer_id,
                crop=crop_name,
                possible_issue=None,
                possible_problem=None,
                confidence=None,
                uncertain=True,
                visible_symptoms=[],
                evidence=[],
                observations=[],
                knowledge_found=False,
                safe_next_steps=[],
                prevention=[],
                when_to_contact_expert=None,
                recommendations=[],
                warning=f"Image validation issue: {val_reason}",
                language=lang,
                status=val_status,
                response=response_text,
                next_question=response_text,
                agent=cls.name,
                request_id=req_id,
            )

        # -------------------------------------------------------------
        # STEP 3: ANALYZE IMAGE THROUGH REAL MULTI-CROP CLASSIFIER & VISION
        # -------------------------------------------------------------
        model_output = predict_crop_disease(
            image_bytes=raw_bytes,
            crop_hint=crop_name,
            message_hint=trimmed_msg,
            is_low_confidence_override=is_low_confidence,
        )

        vision_output = analyze_crop_image(
            image_bytes=raw_bytes,
            image_path=image_path,
            filename=filename,
            language=lang,
            is_low_confidence=is_low_confidence,
            crop_hint=crop_name,
            message_hint=trimmed_msg,
        )

        is_plant = model_output.get("is_plant", True) and vision_output.get("is_plant", True)
        model_status = model_output.get("status", "completed")

        # -------------------------------------------------------------
        # GUARD 1: NON-PLANT & NON-CROP IMAGES
        # -------------------------------------------------------------
        if not is_plant or model_status == "invalid_image":
            if lang == "te":
                response_text = (
                    "అప్‌లోడ్ చేసిన ఫోటోలో పంట లేదా ఆకులు కనిపించడం లేదు.\n"
                    "దయచేసి దెబ్బతిన్న పంట లేదా ఆకుల స్పష్టమైన ఫోటోను అప్‌లోడ్ చేయండి."
                )
                next_q = "ఇది ఏ పంట? దయచేసి పంట ఆకుల ఫోటోను పంపండి."
            elif lang == "hi":
                response_text = (
                    "अपलोड की गई फ़ोटो में कोई फसल या पत्ती दिखाई नहीं दे रही है।\n"
                    "कृपया प्रभावित फसल की पत्ती की एक साफ़ फ़ोटो अपलोड करें।"
                )
                next_q = "यह कौन सी फसल है? कृपया पत्ती की फ़ोटो भेजें।"
            else:
                response_text = (
                    "The uploaded image does not appear to contain a crop or plant leaf.\n"
                    "Please upload a clear close-up photo of the affected crop leaves."
                )
                next_q = "Which crop is this? Please upload a photo of the affected leaf."

            req_id = cls._record_request(db, farmer_id, "crop_health", "uncertain", response_text, lang)

            return CropHealthResult(
                farmer_id=farmer_id,
                crop=None,
                possible_issue=None,
                possible_problem=None,
                confidence=float(model_output.get("confidence", 0.15)),
                uncertain=True,
                visible_symptoms=model_output.get("visible_symptoms", []),
                evidence=model_output.get("evidence", []),
                observations=model_output.get("visible_symptoms", []),
                knowledge_found=False,
                safe_next_steps=[],
                prevention=[],
                when_to_contact_expert=None,
                recommendations=[],
                warning="The image does not appear to contain crop foliage.",
                language=lang,
                status="uncertain",
                response=response_text,
                next_question=next_q,
                agent=cls.name,
                request_id=req_id,
            )

        # -------------------------------------------------------------
        # GUARD 2: UNSUPPORTED CROPS
        # -------------------------------------------------------------
        if model_status == "unsupported":
            supported_str = ", ".join(SUPPORTED_CROPS)
            if lang == "te":
                response_text = (
                    f"🌱 పంట: {model_output.get('crop') or crop_name or 'గుర్తించబడని పంట'}\n\n"
                    f"⚠️ కిసాన్ సారథి ప్రస్తుత వ్యాధి గుర్తింపు మోడల్ ప్రధానంగా క్రింది పంటలకు మాత్రమే పరిమితం:\n"
                    f"• {supported_str}\n\n"
                    f"మీరు అభ్యర్థించిన పంట మా ప్రస్తుత డేటాసెట్‌లో అందుబాటులో లేదు. "
                    f"దయచేసి ఖచ్చితమైన నిర్ధారణ కొరకు స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO)ని సంప్రదించండి."
                )
                next_q = "దయచేసి మద్దతు ఉన్న పంటల ఫోటోను అందించండి లేదా AEO ని సంప్రదించండి."
            elif lang == "hi":
                response_text = (
                    f"🌱 फसल: {model_output.get('crop') or crop_name or 'असमर्थित फसल'}\n\n"
                    f"⚠️ किसान सारथी का वर्तमान रोग पहचान मॉडल निम्नलिखित फसलों का समर्थन करता है:\n"
                    f"• {supported_str}\n\n"
                    f"आपकी फसल वर्तमान में समर्थित नहीं है। सही निदान के लिए कृपया अपने स्थानीय कृषि विस्तार अधिकारी या KVK से संपर्क करें।"
                )
                next_q = "कृपया समर्थित फसल की फ़ोटो प्रदान करें या कृषि अधिकारी से संपर्क करें।"
            else:
                response_text = (
                    f"🌱 Crop: {model_output.get('crop') or crop_name or 'Unsupported Crop'}\n\n"
                    f"⚠️ The disease model currently supports foliar analysis for:\n"
                    f"• {supported_str}\n\n"
                    f"The requested crop is currently outside our supported model domain. "
                    f"Please consult your local Agricultural Extension Officer (AEO) or KVK specialist for personal guidance."
                )
                next_q = "Please upload an image of a supported crop or consult a local agricultural officer."

            req_id = cls._record_request(db, farmer_id, "crop_health", "unsupported", response_text, lang)

            return CropHealthResult(
                farmer_id=farmer_id,
                crop=model_output.get("crop") or crop_name,
                possible_issue=model_output.get("predicted_problem"),
                possible_problem=model_output.get("predicted_problem"),
                confidence=float(model_output.get("confidence", 0.35)),
                uncertain=True,
                visible_symptoms=model_output.get("visible_symptoms", []),
                evidence=model_output.get("evidence", []),
                observations=model_output.get("visible_symptoms", []),
                knowledge_found=False,
                safe_next_steps=["Consult your local Agricultural Extension Officer (AEO) or KVK specialist"],
                prevention=[],
                when_to_contact_expert="Consult your local agricultural officer for unsupported crops.",
                recommendations=["Consult your local Agricultural Extension Officer (AEO) or KVK specialist"],
                warning=f"Crop not supported in current model. Supported crops: {supported_str}.",
                language=lang,
                status="unsupported",
                response=response_text,
                next_question=next_q,
                agent=cls.name,
                request_id=req_id,
            )

        # -------------------------------------------------------------
        # GUARD 3: BLURRY / LOW-CONFIDENCE IMAGES
        # -------------------------------------------------------------
        model_conf = float(model_output.get("confidence", 0.0))
        is_uncertain = (
            model_output.get("uncertain", False)
            or model_status == "needs_better_image"
            or is_low_confidence
            or (model_conf < 0.60)
        )

        if is_uncertain:
            status_result = "needs_better_image"
            detected_crop = model_output.get("crop") or crop_name or "Uncertain Crop"
            detected_problem = model_output.get("predicted_problem") or "Signs are unclear"
            visible_symptoms = model_output.get("visible_symptoms", [])

            if lang == "te":
                response_text = (
                    f"🌱 పంట: {detected_crop}\n\n"
                    f"🔎 సాధ్యమైన సమస్య: {detected_problem}\n\n"
                    f"📊 ఖచ్చితత్వం: {int(model_conf * 100)}%\n\n"
                    f"👀 నేను గమనించినది:\n" + "\n".join(f"• {s}" for s in visible_symptoms) + "\n\n"
                    f"💡 దీని అర్థం:\nఫోటో పూర్తిగా స్పష్టంగా లేనందున తెగులును ఖచ్చితంగా నిర్ధారించలేకపోతున్నాను.\n\n"
                    f"✅ మీరు ఇప్పుడు చేయగలిగే పనులు:\n"
                    f"• పగటి వెలుతురులో ఆకులపై దగ్గరగా (close-up) స్పష్టమైన ఫోటో తీయండి.\n"
                    f"• పంట పేరు లేదా లక్షణాలను కిసాన్ సారథికి వివరంగా తెలియజేయండి.\n\n"
                    f"⚠️ ముఖ్య గమనిక:\nఇది ప్రాథమిక పరిశీలన మాత్రమే. రసాయన మందులు వాడే ముందు వ్యవసాయ అధికారిని సంప్రదించండి."
                )
                next_q = "దయచేసి మంచి వెలుతురులో ఆకులపై దగ్గరగా స్పష్టమైన ఫోటో తీయండి."
            elif lang == "hi":
                response_text = (
                    f"🌱 फसल: {detected_crop}\n\n"
                    f"🔎 संभावित समस्या: {detected_problem}\n\n"
                    f"📊 विश्वसनीयता: {int(model_conf * 100)}%\n\n"
                    f"👀 मुझे जो दिखाई दिया:\n" + "\n".join(f"• {s}" for s in visible_symptoms) + "\n\n"
                    f"💡 इसका क्या अर्थ हो सकता है:\nफ़ोटो पर्याप्त स्पष्ट नहीं है, इसलिए पक्का निदान संभव नहीं है।\n\n"
                    f"✅ आप अभी क्या कर सकते हैं:\n"
                    f"• दिन की रोशनी में पत्तियों की एक नज़दीकी साफ़ फ़ोटो लें।\n"
                    f"• कृपया बताएं कि यह कौन सी फसल है।\n\n"
                    f"⚠️ महत्वपूर्ण नोट:\nयह केवल एक प्राथमिक अवलोकन है। किसी भी रासायनिक उपचार से पहले कृषि अधिकारी से सलाह लें।"
                )
                next_q = "कृपया पत्तियों की नज़दीक से साफ़ फ़ोटो अपलोड करें।"
            else:
                response_text = (
                    f"🌱 Crop: {detected_crop}\n\n"
                    f"🔎 Possible problem: {detected_problem}\n\n"
                    f"📊 Confidence: {int(model_conf * 100)}%\n\n"
                    f"👀 What I can see:\n" + "\n".join(f"• {s}" for s in visible_symptoms) + "\n\n"
                    f"💡 What this may mean:\nThe image is not clear enough for a reliable assessment.\n\n"
                    f"✅ What you can do now:\n"
                    f"• Please take a closer, well-lit photo of the affected leaves in daylight.\n"
                    f"• Please share the crop name or specific symptoms if known.\n\n"
                    f"⚠️ Important:\nThis is a preliminary observation, not a guaranteed diagnosis. Consult your local agricultural officer before taking any action."
                )
                next_q = "Please upload a clearer, well-lit photo of the affected leaf."

            req_id = cls._record_request(db, farmer_id, "crop_health", status_result, response_text, lang)

            return CropHealthResult(
                farmer_id=farmer_id,
                crop=detected_crop,
                possible_issue=detected_problem,
                possible_problem=detected_problem,
                confidence=model_conf,
                uncertain=True,
                visible_symptoms=visible_symptoms,
                evidence=model_output.get("evidence", []),
                observations=visible_symptoms,
                knowledge_found=False,
                safe_next_steps=["Take a clearer close-up photo in daylight"],
                prevention=[],
                when_to_contact_expert=None,
                recommendations=["Take a clearer close-up photo in daylight"],
                warning="Assessment is uncertain due to low image clarity or low model confidence.",
                language=lang,
                status=status_result,
                response=response_text,
                next_question=next_q,
                agent=cls.name,
                request_id=req_id,
            )

        # -------------------------------------------------------------
        # STEP 4: PREDICTION RESOLUTION & DUAL-MODEL REASONING
        # -------------------------------------------------------------
        detected_crop = model_output.get("crop") or crop_name or "Crop"
        detected_problem = model_output.get("predicted_problem") or "Healthy"
        confidence = model_conf
        is_healthy = model_output.get("is_healthy", False)

        visible_symptoms = list(model_output.get("visible_symptoms", []))
        evidence = list(model_output.get("evidence", []))

        # Check for Gemini Vision disagreement if available
        if vision_output.get("engine") == "gemini_vision" and vision_output.get("is_plant"):
            gemini_crop = vision_output.get("crop")
            gemini_prob = vision_output.get("problem")
            gemini_conf = vision_output.get("confidence", 0.0)
            if gemini_conf >= 0.75:
                # Disagreement check: if model says healthy and gemini says disease or vice versa
                if (is_healthy and gemini_prob and "healthy" not in gemini_prob.lower()) or (
                    not is_healthy and gemini_prob and "healthy" in gemini_prob.lower()
                ):
                    confidence = 0.50
                    is_uncertain = True
                    evidence.append("Notice: Multi-crop classifier and Gemini Vision showed differing conclusions.")

        # -------------------------------------------------------------
        # STEP 5: GROUND WITH CURATED CROP KNOWLEDGE BASE
        # -------------------------------------------------------------
        kb_entry = find_crop_knowledge(
            crop_name=detected_crop,
            problem_name=detected_problem,
            language=lang,
        )

        knowledge_found = kb_entry.get("knowledge_found", False)
        safe_next_steps = kb_entry.get("safe_next_steps", [])
        prevention = kb_entry.get("prevention", [])
        when_expert = kb_entry.get("when_to_contact_expert")

        crop_display = kb_entry.get("crop") or detected_crop
        problem_display = kb_entry.get("disease") or detected_problem

        # -------------------------------------------------------------
        # STEP 6: FORMULATE SAFE FARMER-FRIENDLY EXPLANATION
        # -------------------------------------------------------------
        conf_pct = int(confidence * 100)
        symptoms_str = "\n".join(f"• {s}" for s in visible_symptoms) if visible_symptoms else "• Foliar structure analyzed"
        steps_str = "\n".join(f"• {step}" for step in safe_next_steps) if safe_next_steps else "• Monitor crop condition"
        prev_str = "\n".join(f"• {p}" for p in prevention)

        if lang == "te":
            response_text = (
                f"🌱 పంట: {crop_display}\n\n"
                f"🔎 సాధ్యమైన సమస్య:\n{problem_display}\n\n"
                f"📊 ఖచ్చితత్వం:\n{conf_pct}%\n\n"
                f"👀 నేను గమనించిన లక్షణాలు:\n{symptoms_str}\n\n"
                f"💡 దీని అర్థం:\nఈ లక్షణాలు {problem_display}కు అనుగుణంగా ఉన్నాయి.\n\n"
                f"✅ మీరు ఇప్పుడు చేయగలిగే సురక్షిత చర్యలు:\n{steps_str}\n\n"
                + (f"🛡️ నివారణ చర్యలు:\n{prev_str}\n\n" if prev_str else "")
                + f"⚠️ ముఖ్య గమనిక:\nఇది ప్రాథమిక ఫోటో పరిశీలన మాత్రమే, ఖచ్చితమైన నిర్ధారణ కాదు. "
                f"రసాయన మందుల వాడకానికి ముందు స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO)ని సంప్రదించండి."
                + (f"\n\n📞 ఎవరిని సంప్రదించాలి: {when_expert}" if when_expert else "")
            )
        elif lang == "hi":
            response_text = (
                f"🌱 फसल: {crop_display}\n\n"
                f"🔎 संभावित समस्या:\n{problem_display}\n\n"
                f"📊 विश्वसनीयता:\n{conf_pct}%\n\n"
                f"👀 मुझे जो दिखाई दिया:\n{symptoms_str}\n\n"
                f"💡 इसका क्या अर्थ हो सकता है:\nयह लक्षण {problem_display} के अनुकूल हैं।\n\n"
                f"✅ आप अभी क्या कर सकते हैं:\n{steps_str}\n\n"
                + (f"🛡️ रोकथाम:\n{prev_str}\n\n" if prev_str else "")
                + f"⚠️ महत्वपूर्ण नोट:\nयह एक प्राथमिक छवि-आधारित अवलोकन है, कोई पक्का निदान नहीं। "
                f"रासायनिक उपचार के लिए कृपया स्थानीय कृषि विशेषज्ञ से परामर्श करें।"
                + (f"\n\n📞 विशेषज्ञ सलाह: {when_expert}" if when_expert else "")
            )
        else:
            response_text = (
                f"🌱 Crop: {crop_display}\n\n"
                f"🔎 Possible problem:\n{problem_display}\n\n"
                f"📊 Confidence:\n{conf_pct}%\n\n"
                f"👀 What I can see:\n{symptoms_str}\n\n"
                f"💡 What this may mean:\nThe image is consistent with {problem_display}.\n\n"
                f"✅ What you can do now:\n{steps_str}\n\n"
                + (f"🛡️ Prevention:\n{prev_str}\n\n" if prev_str else "")
                + f"⚠️ Important:\nThis is a preliminary image-based assessment, not a guaranteed diagnosis. "
                f"For chemical treatment, consult a local agricultural expert before application."
                + (f"\n\n📞 Expert Advisory: {when_expert}" if when_expert else "")
            )

        req_id = cls._record_request(db, farmer_id, "crop_health", "completed", response_text, lang)

        return CropHealthResult(
            farmer_id=farmer_id,
            crop=crop_display,
            possible_issue=problem_display,
            possible_problem=problem_display,
            confidence=confidence,
            uncertain=False,
            visible_symptoms=visible_symptoms,
            evidence=evidence,
            observations=visible_symptoms,
            knowledge_found=knowledge_found,
            safe_next_steps=safe_next_steps,
            prevention=prevention,
            when_to_contact_expert=when_expert,
            recommendations=safe_next_steps,
            warning="This is an AI-assisted observation and is not a guaranteed diagnosis.",
            language=lang,
            status="completed",
            response=response_text,
            next_question=None,
            agent=cls.name,
            request_id=req_id,
        )

    @classmethod
    def execute(
        cls,
        farmer_id: str,
        query: str,
        language: str = "te",
        context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Standard agent interface compatible with KisanSaarthi Orchestrator dispatch.
        """
        ctx = context or {}
        image_bytes = ctx.get("image_bytes")
        image_path = ctx.get("image_path")
        filename = ctx.get("filename")
        crop_name = ctx.get("crop_name")
        location = ctx.get("location")
        growth_stage = ctx.get("growth_stage")
        is_low_confidence = ctx.get("is_low_confidence", False)

        result = cls.process_request(
            farmer_id=farmer_id,
            message=query,
            language=language,
            image_bytes=image_bytes,
            image_path=image_path,
            filename=filename,
            crop_name=crop_name,
            location=location,
            growth_stage=growth_stage,
            is_low_confidence=is_low_confidence,
            db=db,
        )

        return {
            "agent": cls.name,
            "status": result.status,
            "response": result.response,
            "result": result.dict(),
            "next_question": result.next_question,
        }

    @staticmethod
    def _record_request(
        db: Optional[Session],
        farmer_id: str,
        req_type: str,
        status: str,
        summary: str,
        language: str,
    ) -> Optional[str]:
        """Safely records request into SQLite if db session is available."""
        if not db:
            return None
        try:
            farmer = repository.get_farmer(db, farmer_id)
            if not farmer:
                repository.create_farmer(
                    db,
                    farmer_id=farmer_id,
                    name="Farmer",
                    phone="9876543210",
                    language=language,
                )
            req = repository.create_request(
                db,
                farmer_id=farmer_id,
                type=req_type,
                status=status,
                current_step=f"Crop Health Agent: {status}",
                result=summary[:300] if summary else None,
            )
            return req.id
        except Exception:
            return None
