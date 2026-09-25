"""
Agricultural Input Verification Tool.
Helps farmers verify genuine fertilizers, seeds, and agrochemicals.
Protects against spurious or adulterated agricultural inputs.
"""

from typing import Dict, Any


def verify_agri_input(product_name: str, language: str = "en") -> Dict[str, Any]:
    """
    Returns authentic input verification checklist and manufacturer compliance guidelines.
    """
    if language == "te":
        return {
            "status": "guidelines_ready",
            "title": "రసాయన ఎరువులు & విత్తనాల ప్రామాణికత తనిఖీ (Genuine Check)",
            "verification_steps": [
                "1. బస్తా లేదా ప్యాకెట్ సీలింగ్: అసలైన తయారీదారు కుట్లు (Stitching) మరియు ట్యాంపర్-ఎవిడెంట్ సీల్ సరిచూడండి.",
                "2. 12-అంకెల బ్యాచ్ నంబర్ & గడువు తేదీ (Mfg/Exp Date) స్పష్టంగా ముద్రించబడి ఉండాలి.",
                "3. QR కోడ్ లేదా బార్‌కోడ్: మొబైల్ కెమెరాతో స్కాన్ చేసి తయారీదారు పోర్టల్ వివరాలతో సరిపోల్చండి.",
                "4. రసీదు (Bill): అధీకృత రైతు సేవా కేంద్రం (RSK) లేదా లైసెన్స్ పొందిన డీలర్ నుండి మాత్రమే కొనుగోలు చేసి రశీదు తీసుకోండి.",
            ],
            "warning": "నకిలీ మందులు లేదా ఎరువుల అనుమానం ఉంటే వెంటనే టోల్-ఫ్రీ 1800-425-3434 నంబర్‌కు ఫిర్యాదు చేయండి.",
        }
    elif language == "hi":
        return {
            "status": "guidelines_ready",
            "title": "कृषि इनपुट (उर्वरक/बीज) प्रामाणिकता सत्यापन (Genuine Check)",
            "verification_steps": [
                "1. बोरी की सिलाई और सील: कंपनी की मूल सिलाई और होलोग्राम की जांच करें।",
                "2. बैच नंबर, निर्माण और समाप्ति तिथि (Mfg/Exp) स्पष्ट रूप से छपी होनी चाहिए।",
                "3. QR कोड को स्कैन करके कंपनी के डेटाबेस से मिलाएँ।",
                "4. अधिकृत डीलर या इफको/कृषि केंद्र से ही बिल सहित खरीदारी करें।",
            ],
            "warning": "नकली खाद या कीटनाशक की आशंका होने पर निकटतम कृषि अधिकारी को सूचित करें।",
        }
    else:
        return {
            "status": "guidelines_ready",
            "title": "Agricultural Input Authenticity Verification (Fertilizer / Chemical Check)",
            "verification_steps": [
                "1. Bag Stitching & Hologram: Inspect the factory machine-stitch and tamper-proof holographic seal.",
                "2. Mandatory Markings: Look for standard batch number, manufacturing date, expiry date, and MRP printing.",
                "3. QR Code Verification: Scan the fertilizer bag QR code with your mobile camera to verify Central FCO registration.",
                "4. Authorized Dealers: Always purchase from government-licensed dealers or Rythu Seva Kendras (RSK) with a valid GST tax invoice.",
            ],
            "warning": "Suspected counterfeit chemicals should be reported to the District Joint Director of Agriculture immediately.",
        }
