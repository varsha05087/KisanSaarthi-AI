"""
Agent Registry for KisanSaarthi AI.
Maps recognized agricultural intents to their specialized agent classes and metadata.
"""

from typing import Any, Dict
from agents.crop_health_agent import CropHealthAgent
from agents.input_verification import InputVerificationAgent
from agents.tractor import TractorAgent
from agents.insurance import InsuranceAgent
from agents.agricycle import AgriCycleAgent
from agents.seed import SeedAgent
from agents.general_agriculture import GeneralAgricultureAgent

AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "crop_health": {
        "name": "Crop Health Agent",
        "class": CropHealthAgent,
        "description": "Diagnoses crop diseases, pest infestations, and leaf symptoms.",
    },
    "input_verification": {
        "name": "Input Verification Agent",
        "class": InputVerificationAgent,
        "description": "Validates authenticity of fertilizers, chemicals, and seeds.",
    },
    "tractor_booking": {
        "name": "Tractor Booking Agent",
        "class": TractorAgent,
        "description": "Locates, schedules, and confirms tractor and implement bookings.",
    },
    "insurance_assistance": {
        "name": "Insurance Assistance Agent",
        "class": InsuranceAgent,
        "description": "Guides farmers through PMFBY claim preparation and document checklists.",
    },
    "agricycle": {
        "name": "AgriCycle Waste Agent",
        "class": AgriCycleAgent,
        "description": "Matches crop residue and stubble with bio-energy and recycling pathways.",
    },
    "seed_assistance": {
        "name": "Seed Assistance Agent",
        "class": SeedAgent,
        "description": "Locates certified seed varieties and RSK cooperative center stock.",
    },
    "general_agriculture": {
        "name": "General Agriculture AI",
        "class": GeneralAgricultureAgent,
        "description": "Dynamic open-ended agricultural assistant for farming questions, soil, irrigation, and crop management.",
    },
}


def get_agent_name(intent: str) -> str:
    """Returns the user-friendly name of the specialized agent mapped to the intent."""
    info = AGENT_REGISTRY.get(intent)
    return info["name"] if info else "KisanSaarthi General Assistant"


def get_agent_class(intent: str):
    """Returns the agent class for executing specialized tasks."""
    info = AGENT_REGISTRY.get(intent)
    return info["class"] if info else None
