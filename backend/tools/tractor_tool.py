"""
Agricultural Equipment Catalogue and Search Tools for KisanSaarthi AI.
Provides local equipment availability, rates, time-slots, and filtering.
"""

from typing import Dict, Any, List, Optional

TIME_SLOTS = [
    "8:00 AM – 11:00 AM",
    "11:00 AM – 2:00 PM",
    "2:00 PM – 5:00 PM",
    "5:00 PM – 8:00 PM",
]

EQUIPMENT_CATALOGUE = [
    {
        "id": "TRK-GFT-50",
        "name": "GreenField Tractor",
        "full_name": "GreenField Tractor (50 HP)",
        "type": "tractor",
        "specs": "50 HP",
        "rate_per_hour": 800,
        "owner": "Suresh Kumar",
        "slots": TIME_SLOTS,
        "available": True,
    },
    {
        "id": "TRK-KPT-45",
        "name": "Kisan Power Tractor",
        "full_name": "Kisan Power Tractor (45 HP)",
        "type": "tractor",
        "specs": "45 HP",
        "rate_per_hour": 750,
        "owner": "Ramesh Yadav",
        "slots": TIME_SLOTS,
        "available": True,
    },
    {
        "id": "TRK-MFT-55",
        "name": "Mahindra Farm Tractor",
        "full_name": "Mahindra Farm Tractor (55 HP)",
        "type": "tractor",
        "specs": "55 HP",
        "rate_per_hour": 850,
        "owner": "Srinivas Reddy",
        "slots": TIME_SLOTS,
        "available": True,
    },
    {
        "id": "IMP-ROTV-01",
        "name": "Rotavator",
        "full_name": "Rotavator (Land preparation)",
        "type": "rotavator",
        "specs": "Land preparation",
        "rate_per_hour": 500,
        "owner": "Venkatesh Rao",
        "slots": TIME_SLOTS,
        "available": True,
    },
    {
        "id": "IMP-PTIL-02",
        "name": "Power Tiller",
        "full_name": "Power Tiller (Inter-cultivation)",
        "type": "power_tiller",
        "specs": "Inter-cultivation",
        "rate_per_hour": 400,
        "owner": "Narayana Swamy",
        "slots": TIME_SLOTS,
        "available": True,
    },
]

# Legacy backward-compatible dataset
AVAILABLE_TRACTORS = [
    {
        "id": "TRK-575",
        "model": "Mahindra 575 DI (45 HP)",
        "owner": "Srinivas Reddy",
        "distance": "2.8 km",
        "rate_per_hour": 850,
        "available_immediately": True,
    },
    {
        "id": "TRK-5050",
        "model": "John Deere 5050 D (50 HP)",
        "owner": "Ramesh Yadav",
        "distance": "4.2 km",
        "rate_per_hour": 900,
        "available_immediately": True,
    },
]


DEMO_LOCATIONS = {
    "guntur", "peddapuram", "miryalaguda", "suryapet", "nalgonda", "khammam", "warangal",
    "medak", "nizamabad", "karimnagar", "kurnool", "anantapur", "rangareddy", "mahbubnagar",
    "adilabad", "prakasam", "nellore", "krishna",
    "గుంటూరు", "పెద్దాపురం", "మిర్యాలగూడ", "సూర్యాపేట", "నల్గొండ", "ఖమ్మం", "వరంగల్",
    "गुंटूर", "मिर्यालगुडा", "सूर्यापेट", "नलगोंडा", "खम्मम", "वारंगल",
}


def search_equipment(
    location: str,
    date: str,
    equipment_type: Optional[str] = None,
    preferred_slot: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Searches the equipment catalogue based on location, date, equipment type, and time slot.
    Returns structured options with option numbers if location is in demo catalogue coverage.
    """
    norm_loc = (location or "").strip().lower()
    # Check if location matches any demo coverage area
    is_covered = any(dl in norm_loc for dl in DEMO_LOCATIONS) or any(norm_loc in dl for dl in DEMO_LOCATIONS)
    if not is_covered:
        return []

    matched = []
    norm_type = (equipment_type or "").strip().lower()

    for item in EQUIPMENT_CATALOGUE:
        if norm_type in ["tractor", "tractors"]:
            if item["type"] != "tractor":
                continue
        elif norm_type in ["rotavator", "rotavators"]:
            if item["type"] != "rotavator":
                continue
        elif norm_type in ["power_tiller", "power tiller", "tiller", "tillers"]:
            if item["type"] != "power_tiller":
                continue
        # If type is not specified or general 'equipment', all items are eligible

        # Determine slot
        assigned_slot = preferred_slot if preferred_slot in TIME_SLOTS else item["slots"][len(matched) % len(TIME_SLOTS)]

        matched.append({
            "option_number": len(matched) + 1,
            "id": item["id"],
            "name": item["name"],
            "full_name": item["full_name"],
            "type": item["type"].replace("_", " ").title(),
            "specs": item["specs"],
            "location": location,
            "date": date,
            "time_slot": assigned_slot,
            "price": item["rate_per_hour"],
            "rate_per_hour": item["rate_per_hour"],
            "owner": item["owner"],
            "availability": "Available" if item["available"] else "Unavailable",
        })

    return matched


def search_nearby_tractors(location: str = "local", language: str = "te") -> Dict[str, Any]:
    """Returns available tractors and localized booking prompt (legacy support)."""
    if language == "te":
        return {
            "equipment_list": AVAILABLE_TRACTORS,
            "summary": f"{location} సమీపంలో 2 ట్రాక్టర్లు దుక్కి దున్నడానికి సిద్ధంగా ఉన్నాయి.",
            "base_rate": "రూ. 850 - 900 / గంటకు",
        }
    elif language == "hi":
        return {
            "equipment_list": AVAILABLE_TRACTORS,
            "summary": f"{location} के पास 2 ट्रैक्टर जुताई कार्य के लिए उपलब्ध हैं।",
            "base_rate": "रु. 850 - 900 / घंटा",
        }
    else:
        return {
            "equipment_list": AVAILABLE_TRACTORS,
            "summary": f"2 verified tractors available near {location} for ploughing and land preparation.",
            "base_rate": "Rs. 850 - 900 / hour",
        }
