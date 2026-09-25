"""
AgriCycle Agricultural Waste & Biomass Agent.
Matches crop stubble, residue, and waste with sustainable utilization options.
"""

from typing import Dict, Any
from tools.agricycle_tool import get_agricycle_recommendations, extract_residue_type


class AgriCycleAgent:
    name = "AgriCycle Waste Agent"

    @classmethod
    def execute(cls, farmer_id: str, query: str, language: str = "en", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Returns agricultural waste utilization and monetization options."""
        residue_type = extract_residue_type(query)
        res = get_agricycle_recommendations(residue_type=residue_type, language=language)
        title = res.get("title", "AgriCycle Waste Management")
        options = res.get("monetization_options", [])
        advisory = res.get("advisory", "")
        clarification = res.get("clarification_question")

        if language == "te":
            intro = "మీ వ్యవసాయ వ్యర్థాలను / పంట వ్యర్థాలను కాల్చకుండా ప్రయోజనకరంగా వినియోగించుకునే మార్గాలు:"
            advisory_label = "వ్యవసాయ సలహా"
        elif language == "hi":
            intro = "फसल अवशेषों एवं कृषि अपशिष्ट को जलाने के बजाय लाभकारी एवं सुरक्षित उपयोग के विकल्प:"
            advisory_label = "कृषि सलाह"
        else:
            intro = "Here are sustainable & practical pathways for your crop residue instead of burning:"
            advisory_label = "Advisory"

        content_lines = []
        if clarification:
            content_lines.append(f"❓ {clarification}\n")
        content_lines.append(intro)
        content_lines.extend(f"• {opt}" for opt in options)
        if advisory:
            content_lines.append(f"\n🌿 {advisory_label}: {advisory}")

        response_text = f"♻️ [{title}]:\n" + "\n".join(content_lines)

        return {
            "agent": cls.name,
            "status": "completed",
            "agricycle_data": res,
            "response": response_text,
        }
