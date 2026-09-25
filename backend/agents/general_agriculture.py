"""
General Agriculture Specialized Agent for KisanSaarthi AI.
Coordinates dynamic open-ended agricultural question answering using Gemini.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from services.gemini_service import generate_agriculture_response
from database import repository


class GeneralAgricultureAgent:
    name = "General Agriculture AI"

    @classmethod
    def execute(
        cls,
        farmer_id: str,
        query: str,
        language: str = "en",
        db: Optional[Session] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processes an open-ended agriculture question with multi-turn conversation context.
        """
        conversation_context = []
        if db:
            conv_id = (context or {}).get("conversation_id", "default")
            history = repository.get_conversation_history(
                db,
                farmer_id=farmer_id,
                conversation_id=conv_id,
                limit=6,
            )
            for h in history:
                conversation_context.append({
                    "sender": h.sender,
                    "message": h.message,
                })

        # Generate dynamic response using Gemini
        ai_res = generate_agriculture_response(
            message=query,
            language=language,
            conversation_context=conversation_context,
        )

        response_text = ai_res.get("response", "")
        model_name = ai_res.get("model", "gemini-3.6-flash")

        # Persist request record in SQLite if db session is available
        if db:
            repository.create_request(
                db=db,
                farmer_id=farmer_id,
                type="general_agriculture",
                status="completed",
                current_step=f"Answered by {cls.name} ({model_name})",
                result=response_text[:200],
            )

        return {
            "agent": cls.name,
            "intent": "general_agriculture",
            "status": "ready",
            "response": response_text,
            "text": response_text,
            "language": ai_res.get("language", language),
            "model": model_name,
            "missing_information": [],
            "next_question": None,
        }
