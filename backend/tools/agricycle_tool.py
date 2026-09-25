"""
AgriCycle Agricultural Waste & Biomass Utilization Tool.
Matches crop residue, stubble, stalks, trash, and farm waste with sustainable economic reuse pathways.
Supports multi-crop residues (Paddy, Cotton, Sugarcane, Maize, Wheat, Groundnut, Vegetables, and General Farm Waste).
"""

from typing import Dict, Any, Optional


def extract_residue_type(query: str) -> Optional[str]:
    """
    Identifies the specific agricultural residue mentioned in the farmer's query.
    Returns canonical identifier: 'paddy', 'cotton', 'sugarcane', 'maize', 'wheat', 'groundnut', 'vegetable', or None.
    """
    if not query:
        return None
    lowered = query.lower()

    # Cotton stalks
    if any(w in lowered for w in ["cotton", "stalk", "stalks", "పత్తి", "కట్టెలు", "కపాస్", "कपास", "डंठल"]):
        return "cotton"

    # Sugarcane trash/waste/bagasse
    if any(w in lowered for w in ["sugarcane", "cane", "bagasse", "trash", "చెరకు", "గన్న", "गन्ना", "खोई"]):
        return "sugarcane"

    # Maize/corn stalks/cobs
    if any(w in lowered for w in ["maize", "corn", "cob", "cobs", "మొక్కజొన్న", "మక్క", "मक्का", "मक्के"]):
        return "maize"

    # Wheat straw/turi/bhusa
    if any(w in lowered for w in ["wheat", "turi", "bhusa", "గోధుమ", "తూరి", "భూసా", "गेहूं", "भूसा", "तूड़ी"]):
        return "wheat"

    # Groundnut haulms/shells
    if any(w in lowered for w in ["groundnut", "peanut", "haulm", "haulms", "shell", "shells", "వేరుశనగ", "పల్లీ", "मूंगफली"]):
        return "groundnut"

    # Vegetable waste
    if any(w in lowered for w in ["vegetable", "vegetables", "veggie", "veggies", "కూరగాయ", "కూరగాయలు", "సబ్జీ", "सब्जी", "सब्जियां"]):
        return "vegetable"

    # Paddy straw / stubble (checked after specific crops to avoid false positives on 'straw')
    if any(w in lowered for w in ["paddy", "rice", "straw", "stubble", "parali", "వరి", "గడ్డి", "వరి గడ్డి", "మోడు", "ధాన్", "धान", "पराली", "पुआल"]):
        return "paddy"

    return None


def get_agricycle_recommendations(residue_type: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
    """
    Returns practical solutions, sustainable pathways, and anti-burning advisories
    tailored to the specific residue type and preferred language.
    """
    # -------------------------------------------------------------
    # 1. COTTON STALKS
    # -------------------------------------------------------------
    if residue_type == "cotton":
        if language == "te":
            return {
                "residue_type": "cotton",
                "title": "పత్తి కట్టెల నిర్వహణ & సద్వినియోగం (AgriCycle)",
                "monetization_options": [
                    "1. బయోమాస్ బ్రిక్వెట్స్ & పెల్లెట్స్: పత్తి కట్టెలకు అధిక ఇంధన విలువ (4,200 kcal/kg) ఉంటుంది; వీటిని పెల్లెట్లు మరియు బయో-కోల్ పరిశ్రమలకు విక్రయించవచ్చు.",
                    "2. బయోచార్ ఉత్పత్తి: పొలంలోనే బయోచార్ కిల్‌న్ల ద్వారా నాణ్యమైన బయోచార్ తయారు చేసి నేల సారాన్ని శాశ్వతంగా పెంచుకోవచ్చు.",
                    "3. ష్రెడ్డింగ్ & కంపోస్టింగ్: ట్రాక్టర్ ష్రెడ్డర్‌తో కట్టెలను చిన్న ముక్కలుగా చేసి పేడ మరియు ట్రైకోడెర్మాలతో నాణ్యమైన సేంద్రియ ఎరువుగా మార్చడం.",
                    "4. ఇన్-సిటు నేలలో కలపడం: తొలకరి దుక్కులకు ముందే కట్టెల పొడిని నల్లరేగడి నేలలో కలిపి తేమ నిల్వ సామర్థ్యాన్ని పెంచడం.",
                    "5. పార్టికల్ బోర్డ్ తయారీ: కట్టెల గుజ్జును అట్టపెట్టెలు మరియు పార్టికల్ బోర్డుల తయారీదారులకు అందించడం.",
                ],
                "advisory": "పత్తి కట్టెలను కాల్చవద్దు; ష్రెడ్డింగ్ చేసి బయోమాస్ లేదా బయోచార్ పరిశ్రమలకు విక్రయిస్తే ఎకరానికి అదనపు ఆదాయం లభిస్తుంది.",
            }
        elif language == "hi":
            return {
                "residue_type": "cotton",
                "title": "कपास के डंठल प्रबंधन एवं उपयोग (AgriCycle)",
                "monetization_options": [
                    "1. बायोमास ब्रिकेट्स एवं पेलेट्स: कपास के डंठल का कैलोरी मान अधिक होता है; इसे औद्योगिक बॉयलरों और बायो-कोल इकाइयों में बेचें।",
                    "2. बायोचार उत्पादन: खेत में ही पाइरोलिसिस विधि से डंठल को बायोचार में बदलकर मिट्टी की उर्वरता और जलधारण क्षमता बढ़ाएं।",
                    "3. श्रेडिंग एवं खाद निर्माण: ट्रैक्टर चालित श्रेडर से डंठल के टुकड़े करें और गोबर-ट्राइकोडर्मा के साथ कम्पोस्ट तैयार करें।",
                    "4. भूमि में समावेश: कतरन को खेत की मिट्टी में मिलाकर जैविक कार्बन और मिट्टी की संरचना में सुधार करें।",
                    "5. पार्टिकल बोर्ड उद्योग: डंठल के रेशे को कार्डबोर्ड और पार्टिकल बोर्ड निर्माताओं को व्यावसायिक रूप से बेचें।",
                ],
                "advisory": "कपास के डंठल को जलाएं नहीं; इन्हें ब्रिकेट प्लांट या बायोचार में उपयोग कर अतिरिक्त आमदनी प्राप्त करें।",
            }
        else:
            return {
                "residue_type": "cotton",
                "title": "Cotton Stalks & Biomass Management (AgriCycle)",
                "monetization_options": [
                    "1. Biomass Briquettes & Pellets: Cotton stalks have high calorific value (~4,200 kcal/kg); chip and supply to local industrial boilers or bio-coal units.",
                    "2. Biochar Production: Convert woody stalks using farm-scale pyrolysis kilns into porous biochar for permanent soil conditioning and carbon sequestration.",
                    "3. Mobile Shredding & Composting: Shred dry stalks in the field using a tractor-mounted shredder and compost with cow dung and Trichoderma.",
                    "4. In-Situ Deep Incorporation: Shred stalks directly into the soil before pre-monsoon rains to enhance water infiltration in black cotton soils.",
                    "5. Industrial Agro-Board: Supply shredded stalk fiber to particle-board, hardboard, and paper-manufacturing units.",
                ],
                "advisory": "Avoid burning cotton stalks; burning destroys valuable woody biomass that yields ₹1,500–₹2,500/tonne when sold to briquette or bio-coal processors.",
            }

    # -------------------------------------------------------------
    # 2. SUGARCANE TRASH / WASTE
    # -------------------------------------------------------------
    elif residue_type == "sugarcane":
        if language == "te":
            return {
                "residue_type": "sugarcane",
                "title": "చెరకు చెత్త & వ్యర్థాల నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. కార్శి తోటల్లో మల్చింగ్ (Trash Mulching): వరుసల మధ్య ఎకరానికి 3-4 టన్నుల చెరకు చెత్తను పరచడం ద్వారా తేమ ఆవిరి కాకుండా కాపాడడం మరియు కలుపును 70% నివారించడం.",
                    "2. త్వరిత కంపోస్ట్ తయారీ: చెత్తపై వేస్ట్ డీకంపోజర్ లేదా పేడ నీరు మరియు యూరియా చల్లి 45-60 రోజుల్లో నాణ్యమైన సేంద్రియ ఎరువుగా మార్చడం.",
                    "3. ట్రాష్ ష్రెడ్డర్‌తో నేలలో కలపడం: ట్రాక్టర్ ట్రాష్ ష్రెడ్డర్ ఉపయోగించి ముక్కలు చేసి అంతరకృషి సమయంలో నేలలో కలపడం.",
                    "4. చక్కెర మిల్లుల విద్యుత్ ఉత్పత్తికి సరఫరా: ఎండిన చెరకు చెత్తను చక్కెర మిల్లుల బయోమాస్ బాయిలర్లకు విక్రయించడం.",
                    "5. వర్మీ కంపోస్టింగ్: పచ్చి రొట్ట మరియు పేడతో కలిపి వానపాముల ఎరువుగా మార్చడం.",
                ],
                "advisory": "చెరకు తోటల్లో చెత్తను కాల్చవద్దు; అది పిలక మొగ్గలను దెబ్బతీస్తుంది మరియు ఎకరానికి 400 కిలోల సేంద్రియ కార్బన్‌ను నాశనం చేస్తుంది.",
            }
        elif language == "hi":
            return {
                "residue_type": "sugarcane",
                "title": "गन्ने की सूखी पत्ती (ट्रैश) एवं अपशिष्ट प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. पेड़ी (रतून) गन्ने में ट्रैश मल्चिंग: कतारों के बीच 3-4 टन सूखी पत्ती बिछाएं; इससे 70% खरपतवार नियंत्रण होता है और 2-3 सिंचाइयों की बचत होती है।",
                    "2. त्वरित कम्पोस्टिंग: पत्तियों पर वेस्ट डीकंपोजर या गोबर के घोल का छिड़काव कर 45-60 दिनों में उत्तम जैविक खाद तैयार करें।",
                    "3. ट्रैश श्रेडर से मिट्टी में मिलाना: पत्तियों को छोटे टुकड़ों में काटकर जुताई के समय खेत की मिट्टी में मिलाएं।",
                    "4. बायो-एनर्जी एवं को-जनरेशन: सूखी पत्ती और खोई को चीनी मिलों के बॉयलर या पेलेट निर्माताओं को बेचें।",
                    "5. केंचुआ खाद: पत्तियों को गोबर के साथ मिलाकर केंचुआ खाद की क्यारियों में उपयोग करें।",
                ],
                "advisory": "गन्ने की सूखी पत्तियों को कभी न जलाएं; आग लगाने से पेड़ी के कल्ले जल जाते हैं और मित्र कीट नष्ट हो जाते हैं।",
            }
        else:
            return {
                "residue_type": "sugarcane",
                "title": "Sugarcane Trash & Bagasse Management (AgriCycle)",
                "monetization_options": [
                    "1. Trash Mulching in Ratoon Crop: Spread 3–4 tonnes/acre of dried trash between cane rows to conserve soil moisture, reduce weed growth by 70%, and save 2–3 irrigations.",
                    "2. Rapid Trash Composting: Spray compost inoculant (Trichoderma / cow dung slurry) and 10 kg urea per tonne on chopped trash for conversion into rich humus in 45–60 days.",
                    "3. In-Situ Chopping & Incorporation: Use a tractor-operated trash shredder to cut trash into 2–3 inch pieces and incorporate during intercultivation.",
                    "4. Biomass Cogeneration: Supply bundled cane trash and surplus bagasse to sugar mill cogeneration plants and pellet mills.",
                    "5. Vermicomposting: Blend chopped sugarcane trash with green weeds and cattle manure in vermicompost pits.",
                ],
                "advisory": "Never burn sugarcane trash; burning destroys beneficial cane soil parasites, kills ratoon root buds, and wastes up to 30 kg nitrogen and 400 kg organic carbon per acre.",
            }

    # -------------------------------------------------------------
    # 3. MAIZE / CORN STALKS
    # -------------------------------------------------------------
    elif residue_type == "maize":
        if language == "te":
            return {
                "residue_type": "maize",
                "title": "మొక్కజొన్న కాడల నిర్వహణ & సద్వినియోగం (AgriCycle)",
                "monetization_options": [
                    "1. కుట్టి కోసి పశుగ్రాసంగా మార్చడం: చాఫ్ కట్టర్‌తో మొక్కజొన్న కాడలను చిన్న ముక్కలుగా కోసి పశువులకు పోషక ఆహారంగా అందించడం.",
                    "2. రోటరీ స్లాషర్‌తో నేలలో కలపడం: కాడలను పొలంలోనే ముక్కలు చేసి పప్పుధాన్యాల పంటకు ముందే నేలలో కలిపి భూసారాన్ని పెంచడం.",
                    "3. మొక్కజొన్న కండె (కంకి) బ్రిక్వెట్స్: కండెలతో బయో-బ్రిక్వెట్లు మరియు బయోచార్ తయారు చేయడం.",
                    "4. వర్మీ కంపోస్టింగ్: పేడ మరియు వ్యర్థాలతో కలిపి వానపాముల ఎరువుగా మార్చడం.",
                ],
                "advisory": "మొక్కజొన్న కాడలను కాల్చవద్దు; వీటిని నేలలో కలిపితే తదుపరి రబీ పంటకు 20% వరకు తేమ నిల్వ పెరుగుతుంది.",
            }
        elif language == "hi":
            return {
                "residue_type": "maize",
                "title": "मक्के के डंठल एवं अवशेष प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. कुट्टी काटकर पौष्टिक पशु चारा: चैफ कटर से डंठल को काटकर हरे चारे या गुड़-शीरे के साथ मिलाकर मवेशियों को खिलाएं।",
                    "2. खेत में रोटावेटर से मिलाना: डंठल को काटकर मिट्टी में मिलाएं जिससे अगली दलहनी फसल के लिए भूमि उपजाऊ बने।",
                    "3. भुट्टे के ठूंठ (कौब) से बायो-कोल: मक्के के भुट्टे के ठूंठ से उच्च ऊर्जा वाली ब्रिकेट्स और बायोचार बनाएं।",
                    "4. वर्मीकंपोस्टिंग: मक्के के अवशेषों को गोबर के साथ मिलाकर केंचुआ खाद तैयार करें।",
                ],
                "advisory": "मक्के के डंठल न जलाएं; इन्हें खेत में मिलाने से अगली रबी फसल के लिए नमी संचय 20% तक बढ़ जाता है।",
            }
        else:
            return {
                "residue_type": "maize",
                "title": "Maize & Corn Stalk Management (AgriCycle)",
                "monetization_options": [
                    "1. Chaff Cutting for Livestock Feed: Chop green or semi-dry stalks using a chaff cutter; blend with green fodder or treat with molasses for high-palatability cattle feed.",
                    "2. In-Situ Shredding & Mulching: Shred standing stalks with a rotary slasher/shredder and disc harrow to quickly incorporate organic matter before sowing pulses.",
                    "3. Corn Cob Biochar & Heating Briquettes: Dry corn cobs have very high energy density; use for clean domestic cooking fuel or sell to briquette makers.",
                    "4. Vermicomposting: Layer chopped stalks with livestock manure and soil to produce dark, friable compost within 60 days.",
                ],
                "advisory": "Do not burn maize stubble; incorporating stalks increases soil moisture retention by up to 20% for succeeding rabi crops.",
            }

    # -------------------------------------------------------------
    # 4. WHEAT STRAW
    # -------------------------------------------------------------
    elif residue_type == "wheat":
        if language == "te":
            return {
                "residue_type": "wheat",
                "title": "గోధుమ గడ్డి & తూరి నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. పశుగ్రాసం (తూరి/భూసా): స్ట్రా రీపర్‌తో నాణ్యమైన తూరి సేకరించి పాడి పశువులకు పోషక దాణాగా ఉపయోగించడం.",
                    "2. హ్యాపీ సీడర్‌తో ప్రత్యక్ష విత్తడం: మోడులను తొలగించకుండానే తదుపరి పెసర లేదా మొక్కజొన్న పంటను నేరుగా విత్తుకోవడం.",
                    "3. పుట్టగొడుగుల సాగు: బటన్ పుట్టగొడుగుల సాగుకు గోధుమ గడ్డి అత్యుత్తమ మాధ్యమం.",
                    "4. పేపర్ & కార్డ్‌బోర్డ్ పరిశ్రమలు: మిగులు గడ్డిని ప్యాకేజింగ్ మరియు కాగితం పరిశ్రమలకు విక్రయించడం.",
                ],
                "advisory": "గోధుమ గడ్డిని కాల్చవద్దు; అది భూమిలోని వానపాములను నాశనం చేస్తుంది మరియు చట్టరీత్యా నిషేధించబడింది.",
            }
        elif language == "hi":
            return {
                "residue_type": "wheat",
                "title": "गेहूं के अवशेष (भूसा/तूड़ी) प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. पौष्टिक भूसा/तूड़ी: स्ट्रॉ रीपर द्वारा मवेशियों के लिए उच्च मांग वाला पौष्टिक भूसा बनाएं।",
                    "2. हैप्पी सीडर से सीधी बुवाई: पराली को बिना जलाए अगली मूंग या मक्का फसल की सीधी बुवाई करें।",
                    "3. मशरूम उत्पादन: गेहूं का भूसा बटन और ढींगरी मशरूम के लिए सर्वोत्तम माध्यम है।",
                    "4. गत्ता व कागज उद्योग: अतिरिक्त भूसे की गांठें बनाकर पैकेजिंग एवं पेपर मिलों को बेचें।",
                ],
                "advisory": "गेहूं के अवशेषों को जलाना प्रतिबंधित है; इससे खेत के केंचुए और मित्र जीवाणु नष्ट होते हैं।",
            }
        else:
            return {
                "residue_type": "wheat",
                "title": "Wheat Straw & Turi Management (AgriCycle)",
                "monetization_options": [
                    "1. High-Value Cattle Fodder (Bhusa): Use straw reaper to collect clean wheat turi for premium local livestock feeding and dairy trade.",
                    "2. Turbo Happy Seeder Direct Sowing: Direct sow succeeding moong or maize directly through standing wheat stubble without field preparation.",
                    "3. Mushroom Cultivation Base: Wheat straw is the premium standard substrate for commercial button and oyster mushroom production.",
                    "4. Agro-Packaging & Paper Board: Sell excess baled wheat straw to packaging and paper pulp manufacturing units.",
                ],
                "advisory": "Avoid burning wheat straw; burning is strictly penalized and damages vital earthworms and natural soil organic matter.",
            }

    # -------------------------------------------------------------
    # 5. GROUNDNUT RESIDUES
    # -------------------------------------------------------------
    elif residue_type == "groundnut":
        if language == "te":
            return {
                "residue_type": "groundnut",
                "title": "వేరుశనగ వ్యర్థాలు & పొట్టు నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. ప్రొటీన్ అధికంగా ఉండే పశుగ్రాసం: వేరుశనగ మొక్కల తీగల్లో 10-12% ప్రొటీన్ ఉంటుంది; వీటిని ఎండబెట్టి పశువులకు బలవర్ధకమైన మేతగా వాడవచ్చు.",
                    "2. తోటల్లో పొట్టు మల్చింగ్: పండ్ల తోటల్లో చెట్ల మొదళ్ళ వద్ద వేరుశనగ పొట్టును పరచడం ద్వారా తేమ ఆవిరి కాకుండా చూడడం.",
                    "3. నేల గుల్లబారడానికి వినియోగం: బరువైన నల్లరేగడి నేలలో పొట్టును కలిపి గాలి ప్రసరణ మరియు మురుగునీటి పారుదల పెంచడం.",
                    "4. బయో-బ్రిక్వెట్లు: అధిక వేడినిచ్చే పారిశ్రామిక ఇంధన తయారీకి పొట్టును సరఫరా చేయడం.",
                ],
                "advisory": "వేరుశనగ వ్యర్థాలను కాల్చవద్దు; అవి పాడి పశువులకు అత్యంత విలువైన పోషక మేత.",
            }
        elif language == "hi":
            return {
                "residue_type": "groundnut",
                "title": "मूंगफली के अवशेष एवं छिलका प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. प्रोटीन युक्त पौष्टिक चारा: मूंगफली की पत्तियां एवं लताएं 10-12% प्रोटीन से भरपूर होती हैं; इन्हें सुखाकर पशुओं को खिलाएं।",
                    "2. बागवानी में छिलके की मल्चिंग: फलदार पौधों की जड़ों के पास छिलका बिछाने से नमी बनी रहती है और खरपतवार नहीं उगते।",
                    "3. भारी मिट्टी का सुधार: चिकनी मिट्टी में छिलका मिलाने से हवा का आवागमन और जल निकास बेहतर होता है।",
                    "4. बायोमास ब्रिकेट्स: छिलके से उच्च ताप क्षमता वाली औद्योगिक ब्रिकेट्स तैयार की जाती हैं।",
                ],
                "advisory": "मूंगफली के अवशेषों को कभी न जलाएं; यह दुधारू पशुओं के लिए अत्यधिक पौष्टिक चारा है।",
            }
        else:
            return {
                "residue_type": "groundnut",
                "title": "Groundnut Haulms & Shell Utilization (AgriCycle)",
                "monetization_options": [
                    "1. High-Protein Livestock Haulms: Groundnut haulms/vines contain 10–12% crude protein; harvest and dry for premium livestock feed.",
                    "2. Shell Mulching in Orchards: Groundnut shells make durable, decay-resistant mulch around fruit trees and vegetable beds, suppressing weeds.",
                    "3. Soil Conditioning for Heavy Soils: Work crushed shells into clay soils to permanently improve aeration and internal drainage.",
                    "4. Biomass Briquettes: High lignin content in shells yields high-heat industrial boiler fuel.",
                ],
                "advisory": "Never discard or burn groundnut haulms; they are one of the most protein-dense crop byproducts in Indian agriculture.",
            }

    # -------------------------------------------------------------
    # 6. VEGETABLE FARM WASTE
    # -------------------------------------------------------------
    elif residue_type == "vegetable":
        if language == "te":
            return {
                "residue_type": "vegetable",
                "title": "కూరగాయల వ్యర్థాల నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. త్వరిత వర్మీ కంపోస్టింగ్: కూరగాయల వ్యర్థాలు త్వరగా కుళ్ళుతాయి; ఎండుటాకులతో కలిపి 40 రోజుల్లో నాణ్యమైన వానపాముల ఎరువు తయారు చేయవచ్చు.",
                    "2. బయోగ్యాస్ ఉత్పత్తి: బయోగ్యాస్ ప్లాంట్ల ద్వారా వంటగ్యాస్ మరియు ద్రవ రూప సేంద్రియ ఎరువును పొందడం.",
                    "3. పచ్చిరొట్టగా నేలలో కలపడం: మిగిలిన మొక్కలను రోటవేటర్‌తో నేలలో కలిపి తదుపరి పంటకు సారాన్ని అందించడం.",
                ],
                "advisory": "వ్యర్థాలను నిల్వ ఉంచకుండా వెంటనే కంపోస్ట్ చేయండి; లేకపోతే పురుగులు మరియు తెగుళ్లు వ్యాపిస్తాయి.",
            }
        elif language == "hi":
            return {
                "residue_type": "vegetable",
                "title": "सब्जी फसल अपशिष्ट प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. त्वरित केंचुआ खाद: सब्जियों के अपशिष्ट से मात्र 40 दिनों में पोषक तत्वों से भरपूर केंचुआ खाद तैयार होती है।",
                    "2. बायोगैस एवं बायो-स्लरी: अपशिष्ट से रसोई गैस और तरल जैविक खाद तैयार करें।",
                    "3. हरी खाद के रूप में समावेश: खेत की मिट्टी में अवशेष मिलाकर जैविक खाद की पूर्ति करें।",
                ],
                "advisory": "सब्जियों के अवशेषों का तुरंत निस्तारण करें ताकि कीट व फफूंद न पनपे।",
            }
        else:
            return {
                "residue_type": "vegetable",
                "title": "Vegetable Crop Waste Management (AgriCycle)",
                "monetization_options": [
                    "1. Fast-Track Vermicomposting: Vegetable farm waste has high moisture and nitrogen; layer with dry leaves in vermicompost beds for rich compost in 40 days.",
                    "2. Biogas / Liquid Bio-Slurry: Feed succulent vegetable trimmings into biogas digesters for clean household cooking gas and liquid bio-fertilizer.",
                    "3. Green Manure Soil Incorporation: Rotovate leftover vegetable biomass directly into the bed to restore nutrients before the next planting.",
                ],
                "advisory": "Compost or incorporate vegetable residue quickly to prevent pathogen buildup and fruit-fly breeding.",
            }

    # -------------------------------------------------------------
    # 7. PADDY STRAW (Default if specified as paddy)
    # -------------------------------------------------------------
    elif residue_type == "paddy":
        if language == "te":
            return {
                "residue_type": "paddy",
                "title": "వరి గడ్డి మరియు మోడు నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. ఇన్-సిటు నేలలో కలపడం & మల్చింగ్: హ్యాపీ సీడర్ లేదా రోటవేటర్‌తో వ్యర్థాలను నేలలో కలిపి భూసారాన్ని పెంచడం మరియు తేమను కాపాడడం.",
                    "2. బయో-ఎనర్జీ & పెల్లెట్స్: వరి గడ్డి మరియు పత్తి కట్టెలను సమీప బయోమాస్ ఇంధన తయారీ కేంద్రాలకు విక్రయించవచ్చు.",
                    "3. వర్మీ కంపోస్టింగ్ (సేంద్రియ ఎరువు): వ్యర్థాలను నాణ్యమైన కంపోస్ట్‌గా మార్చి స్వయంగా వాడుకోవచ్చు లేదా విక్రయించవచ్చు.",
                    "4. పశుగ్రాసం: పోషక విలువలు పెంచడానికి యూరియా శుద్ధి ప్రక్రియ ద్వారా వరి గడ్డిని పశుగ్రాసంగా మార్చడం.",
                    "5. పుట్టగొడుగుల సాగు (Mushroom Cultivation): వరి గడ్డిని ఆధారం చేసుకుని అదనపు ఆదాయం పొందడం.",
                ],
                "advisory": "వరి గడ్డిని కాల్చవద్దు; అది భూసారాన్ని తగ్గిస్తుంది మరియు పర్యావరణాన్ని కలుషితం చేస్తుంది.",
            }
        elif language == "hi":
            return {
                "residue_type": "paddy",
                "title": "धान की पराली एवं अवशेष प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. इन-सीटू प्रबंधन एवं मल्चिंग (Mulching): रोटावेटर या हैप्पी सीडर से पराली को खेत में मिलाकर जैविक कार्बन बढ़ाएं और नमी सुरक्षित रखें।",
                    "2. बायोमास पेलेट्स/ऊर्जा: पराली और डंठल को स्थानीय बायो-एनर्जी प्लांट में बेचा जा सकता है।",
                    "3. केंचुआ खाद (वर्मीकंपोस्ट): फसल अवशेषों से उच्च गुणवत्ता वाली जैविक खाद तैयार करें।",
                    "4. पशु चारा: अवशेषों को पोषक चारे में परिवर्तित किया जा सकता है।",
                    "5. मशरूम उत्पादन: पुआल का उपयोग कर मशरूम की खेती से अतिरिक्त आय अर्जित करें।",
                ],
                "advisory": "फसल अवशेषों को जलाएं नहीं; यह मिट्टी के सूक्ष्म पोषक तत्वों को नष्ट करता है।",
            }
        else:
            return {
                "residue_type": "paddy",
                "title": "Paddy Straw & Stubble Management (AgriCycle)",
                "monetization_options": [
                    "1. In-Situ Field Incorporation & Mulching: Retain stubble in the soil using Happy Seeder/rotavator or use as mulching to preserve moisture and build soil organic carbon.",
                    "2. Biomass Pellets & Bio-Energy: Sell paddy straw and cotton stalks to local bio-coal/pellet processors.",
                    "3. Vermicomposting: Convert agricultural residue into nutrient-rich organic compost for soil replenishment.",
                    "4. Enriched Animal Fodder: Treat paddy straw with urea-molasses to improve digestibility for livestock.",
                    "5. Mushroom Cultivation: Utilize straw beds for high-margin button and oyster mushroom production.",
                ],
                "advisory": "Avoid in-field stubble burning; it depletes beneficial soil microbiota and degrades organic matter.",
            }

    # -------------------------------------------------------------
    # 8. GENERAL / UNSPECIFIED AGRICULTURAL WASTE
    # -------------------------------------------------------------
    else:
        if language == "te":
            return {
                "residue_type": "general",
                "clarification_question": "మీ వద్ద ఏ రకమైన వ్యవసాయ వ్యర్థాలు ఉన్నాయి (ఉదాహరణకు: వరి గడ్డి, పత్తి కట్టెలు, చెరకు చెత్త, మొక్కజొన్న కాడలు లేదా కూరగాయల వ్యర్థాలు)?",
                "title": "వ్యవసాయ వ్యర్థాల సాధారణ నిర్వహణ (AgriCycle)",
                "monetization_options": [
                    "1. ఇన్-సిటు నేలలో కలపడం లేదా మల్చింగ్: తేమను కాపాడడానికి మరియు సేంద్రియ కర్బనాన్ని పెంచడానికి రోటవేటర్‌తో నేలలో కలపడం.",
                    "2. వర్మీ కంపోస్టింగ్: పేడ మరియు వేస్ట్ డీకంపోజర్‌తో నాణ్యమైన సేంద్రియ ఎరువుగా మార్చడం.",
                    "3. బయోమాస్ పెల్లెట్లు & ఇంధనం: ఎండిన వ్యర్థాలను బయో-కోల్ పరిశ్రమలకు విక్రయించడం.",
                    "4. పశుగ్రాసంగా వినియోగం: తగిన పంట వ్యర్థాలను పశువుల మేతగా ఉపయోగించడం.",
                ],
                "advisory": "వ్యర్థాలను పొలంలో కాల్చవద్దు; అది విలువైన సేంద్రియ సారాన్ని తగ్గిస్తుంది.",
            }
        elif language == "hi":
            return {
                "residue_type": "general",
                "clarification_question": "आपके पास किस प्रकार का कृषि अपशिष्ट या फसल अवशेष है (जैसे: धान की पराली, कपास के डंठल, गन्ने की पत्तियां, मक्के के डंठल या सब्जी अवशेष)?",
                "title": "कृषि अपशिष्ट सामान्य प्रबंधन (AgriCycle)",
                "monetization_options": [
                    "1. इन-सीटू भूमि प्रबंधन एवं मल्चिंग: नमी संचय और जैविक कार्बन बढ़ाने के लिए रोटावेटर से मिट्टी में मिलाएं।",
                    "2. केंचुआ खाद (वर्मीकंपोस्ट): गोबर और डीकंपोजर की सहायता से उच्च गुणवत्ता वाली जैविक खाद बनाएं।",
                    "3. बायोमास पेलेट्स एवं ऊर्जा: सूखे अवशेषों को स्थानीय बायो-एनर्जी प्लांट में बेचें।",
                    "4. पशु चारा रूपांतरण: उपयुक्त अवशेषों को मवेशियों के चारे के रूप में उपयोग करें।",
                ],
                "advisory": "अवशेषों को कभी न जलाएं; इससे मिट्टी की उर्वरता नष्ट होती है।",
            }
        else:
            return {
                "residue_type": "general",
                "clarification_question": "What type of agricultural waste do you have (e.g. paddy straw, cotton stalks, sugarcane trash, maize stalks, or vegetable waste)?",
                "title": "General Agricultural Residue Management (AgriCycle)",
                "monetization_options": [
                    "1. In-Situ Mulching & Soil Incorporation: Rotavate or mulch residue to retain soil moisture and build organic matter.",
                    "2. Vermicomposting / Farmyard Compost: Convert waste with cow dung and decomposer into high-grade organic fertilizer.",
                    "3. Biomass Energy & Pellets: Supply dry crop residue to local bio-coal/pellet processing plants.",
                    "4. Animal Fodder Conversion: Treat suitable crop residues for livestock feed.",
                ],
                "advisory": "Avoid open in-field burning; burning wastes valuable organic carbon and harms soil health.",
            }
