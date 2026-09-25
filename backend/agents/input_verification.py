"""
Agricultural Input Verification Specialized Agent.
Validates the genuineness of fertilizers, chemicals, and seeds.
"""

from typing import Dict, Any
from tools.input_tool import verify_agri_input


class InputVerificationAgent:
    name = "Input Verification Agent"

    @classmethod
    def execute(cls, farmer_id: str, query: str, language: str = "en", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provides verification guidelines to confirm genuine input."""
        res = verify_agri_input(product_name=query, language=language)

        title = res.get("title", "Input Verification")
        steps = res.get("verification_steps", [])
        warning = res.get("warning", "")

        response_text = (
            f"🔍 [{title}]:\n"
            f"Please verify these 4 authenticity checks:\n" +
            "\n".join(f"• {step}" for step in steps) +
            (f"\n\n⚠️ {warning}" if warning else "")
        )

        return {
            "agent": cls.name,
            "status": "completed",
            "verification_data": res,
            "response": response_text,
        }
