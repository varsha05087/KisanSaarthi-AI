"""
Seed Assistance Specialized Agent.
Assists farmers with certified seeds, RSK centers, and seasonal varieties.
"""

from typing import Dict, Any


class SeedAgent:
    name = "Seed Assistance Agent"

    @classmethod
    def execute(cls, farmer_id: str, query: str, language: str = "te", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provides seed variety availability and RSK guidance."""
        if language == "te":
            response_text = (
                f"🌾 [విత్తన సహాయ ఏజెంట్]:\n"
                f"రైతు సేవా కేంద్రం (RSK) మరియు నేషనల్ సీడ్స్ కార్పొరేషన్ వద్ద సర్టిఫైడ్ విత్తనాలు అందుబాటులో ఉన్నాయి:\n"
                f"• BPT 5204 (సాంబ మసూరి) — 25 కేజీల బస్తా రూ. 950 (రాయితీ లభ్యం)\n"
                f"• MTU 1010 (కాటన్‌దొర సన్నాలు) — 25 కేజీల బస్తా రూ. 920\n\n"
                f"మీ మండల RSK సెంటర్‌లో రిజర్వ్ చేయడానికి మీ రైతు ఆధార్ వివరాలు తెలియజేయండి."
            )
        elif language == "hi":
            response_text = (
                f"🌾 [बीज सहायता एजेंट]:\n"
                f"निकटतम कृषि सेवा केंद्र पर प्रमाणित बीज उपलब्ध हैं:\n"
                f"• BPT 5204 — 25 किग्रा बैग रु. 950\n"
                f"• MTU 1010 — 25 किग्रा बैग रु. 920\n\n"
                f"बुकिंग के लिए आधार विवरण साझा करें।"
            )
        else:
            response_text = (
                f"🌾 [Seed Assistance Agent]:\n"
                f"Certified seed stocks available at nearest Rythu Seva Kendra (RSK):\n"
                f"• BPT 5204 (Samba Mahsuri) — 25kg Bag @ Rs. 950\n"
                f"• MTU 1010 — 25kg Bag @ Rs. 920\n\n"
                f"Please provide your Mandal to reserve seed bags at the cooperative center."
            )

        return {
            "agent": cls.name,
            "status": "completed",
            "response": response_text,
        }
