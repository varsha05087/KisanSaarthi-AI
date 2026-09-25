"""
Crop Insurance & PMFBY Claim Assistance Tool.
Guides farmers on document requirements, 72-hour deadlines, and claim filing.
"""

from typing import Dict, Any


def get_insurance_guidance(language: str = "en") -> Dict[str, Any]:
    """
    Returns step-by-step crop insurance assistance guidelines.
    """
    if language == "te":
        return {
            "title": "ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY) క్లెయిమ్ మార్గదర్శకాలు",
            "critical_deadline": "నష్టం జరిగిన 72 గంటలలోపు పంట నష్టాన్ని నమోదు చేయాలి.",
            "required_documents": [
                "1. పట్టాదార్ పాస్ బుక్ (Pattadar Passbook / ల్యాండ్ రికార్డు)",
                "2. పంట సాగు ధృవీకరణ పత్రం (Crop Sowing Certificate)",
                "3. నష్టపోయిన పొలం జియో-ట్యాగ్డ్ ఫోటోలు (Geo-tagged field photos)",
                "4. ఆధార్ కార్డు & బ్యాంక్ పాస్‌బుక్ కాపీ",
            ],
            "next_step": "టోల్-ఫ్రీ నంబర్ 1800-180-1551 లేదా మీ స్థానిక వ్యవసాయ కార్యాలయంలో 72 గంటల్లోపు దరఖాస్తు నమోదు చేయండి.",
        }
    elif language == "hi":
        return {
            "title": "प्रधानमंत्री फसल बीमा योजना (PMFBY) दावा प्रक्रिया",
            "critical_deadline": "फसल क्षति के 72 घंटे के भीतर सूचना देना अनिवार्य है।",
            "required_documents": [
                "1. भू-अभिलेख / खतौनी / पट्टा पासबुक",
                "2. फसल बुवाई प्रमाण पत्र (पटवारी/ग्राम सेवक द्वारा)",
                "3. क्षतिग्रस्त खेत की स्पष्ट तस्वीरें (जियो-टैग सहित)",
                "4. आधार कार्ड एवं बैंक पासबुक की प्रति",
            ],
            "next_step": "टोल-फ्री नंबर 1800-180-1551 पर कॉल करें या कृषि रक्षक पोर्टल पर 72 घंटे में क्लेम दर्ज कराएं।",
        }
    else:
        return {
            "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY) Claim Application Guide",
            "critical_deadline": "Mandatory 72-hour crop loss intimation deadline after localized natural disaster.",
            "required_documents": [
                "1. Pattadar Passbook / Land Record (RoR)",
                "2. Crop Sowing Certificate (from Revenue/Agri Officer)",
                "3. Geo-tagged photographs of the damaged crop",
                "4. Bank Passbook copy (linked with Aadhaar)",
            ],
            "next_step": "Intimate crop loss via National Crop Insurance Portal (pmfby.gov.in), Toll-Free 1800-180-1551, or local Agriculture Office.",
        }
