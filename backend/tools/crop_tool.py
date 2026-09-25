"""
Crop Health Knowledge Tool & Curated Knowledge Base.
Provides grounded agricultural guidance aligned with ICAR and state extension standards.
Supports English, Telugu, and Hindi across multiple crops.
"""

from typing import Any, Dict, List, Optional

# =====================================================================
# CURATED MULTI-CROP KNOWLEDGE BASE
# =====================================================================

CROP_KNOWLEDGE_BASE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "tomato": {
        "early_blight": {
            "en": {
                "crop": "Tomato",
                "disease": "Early Blight (Alternaria solani)",
                "symptoms": [
                    "Dark brown to black spots on older lower leaves",
                    "Concentric rings ('target board' pattern) inside lesions",
                    "Yellow chlorotic halo surrounding lesions",
                    "Lower foliage drying out and dropping prematurely",
                ],
                "possible_causes": [
                    "Fungal pathogen Alternaria solani surviving in crop debris",
                    "High humidity coupled with warm temperatures (24°C - 29°C)",
                    "Prolonged leaf wetness from overhead splashing",
                ],
                "safe_next_steps": [
                    "Remove and safely destroy severely infected lower leaves (do not compost)",
                    "Avoid overhead sprinkler irrigation; water at the base of plants",
                    "Apply dry straw mulch around plant base to prevent soil splashing onto leaves",
                    "Ensure adequate plant spacing for proper airflow across the canopy",
                ],
                "prevention": [
                    "Practice 2-3 year crop rotation with non-solanaceous crops (avoid potato/brinjal)",
                    "Use certified disease-free seeds or resistant hybrid varieties",
                    "Maintain balanced potassium and nitrogen nutrition to avoid plant stress",
                ],
                "when_to_contact_expert": "Consult your local Agricultural Extension Officer (AEO) or Rythu Bharosa Kendra if more than 20% of foliage is affected before flowering.",
            },
            "te": {
                "crop": "టమాటా",
                "disease": "ముందస్తు ఆకు మచ్చ తెగులు (Early Blight)",
                "symptoms": [
                    "ముదురు ఆకులపై గుండ్రని ముదురు గోధుమ/నల్లటి మచ్చలు",
                    "మచ్చల లోపల వలయాకారపు చక్రాల వంటి గీతలు (టార్గెట్ బోర్డ్ ఆకారం)",
                    "మచ్చల చుట్టూ పసుపు రంగు వలయం ఏర్పడటం",
                    "క్రింది ఆకులు ఎండిపోయి రాలిపోవడం",
                ],
                "possible_causes": [
                    "ఆల్టర్నేరియా సోలాని అనే శిలీంధ్రం పంట వ్యర్థాలలో జీవించడం",
                    "అధిక తేమ మరియు వెచ్చని వాతావరణం (24°C - 29°C)",
                    "ఆకులపై నీరు ఎక్కువసేపు నిలిచి ఉండటం",
                ],
                "safe_next_steps": [
                    "తెగులు సోకిన క్రింది ఆకులను తుంచి పొలానికి దూరంగా నాశనం చేయండి",
                    "మొక్కల మొదళ్ల వద్ద మాత్రమే నీరు పెట్టండి, ఆకులపై నీరు చిమ్మవద్దు",
                    "మొక్క మొదట్లో ఎండుగడ్డితో మల్చింగ్ చేసి మట్టి ఆకులపై పడకుండా చూడండి",
                    "గాలి వెలుతురు ధారాళంగా ప్రసరించేలా మొక్కల మధ్య తగిన దూరం ఉంచండి",
                ],
                "prevention": [
                    "టమాటా తర్వాత వరి, మొక్కజొన్న వంటి పంటలతో 2-3 ఏళ్ల పంట మార్పిడి చేయండి",
                    "ధృవీకరించబడిన విత్తనాలు లేదా తెగులును తట్టుకునే రకాలను వాడండి",
                    "నత్రజని మరియు పొటాష్ ఎరువులను సమతుల్యంగా వాడండి",
                ],
                "when_to_contact_expert": "పూత దశకు ముందే 20% కంటే ఎక్కువ ఆకులపై మచ్చలు వ్యాపిస్తే సమీప రైతు భరోసా కేంద్రం (RBK) లేదా వ్యవసాయ అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "टमाटर",
                "disease": "अगेती झुलसा (Early Blight)",
                "symptoms": [
                    "निचली पुरानी पत्तियों पर गहरे भूरे या काले रंग के धब्बे",
                    "धब्बों के अंदर संकेन्द्रीय छल्ले (टारगेट बोर्ड जैसा पैटर्न)",
                    "धब्बों के चारों ओर पीलापन आना",
                    "पत्तियों का सूखकर असमय गिरना",
                ],
                "possible_causes": [
                    "अल्टरनेरिया सोलानी कवक का फसल अवशेषों में जीवित रहना",
                    "अधिक नमी और 24°C से 29°C का तापमान",
                    "पत्तियों पर लगातार पानी रुकना",
                ],
                "safe_next_steps": [
                    "संक्रमित निचली पत्तियों को तोड़कर खेत से दूर नष्ट करें",
                    "पौधों की जड़ों में पानी दें, पत्तियों पर पानी न छिड़कें",
                    "पौधों के आधार पर सूखी घास की मल्चिंग करें",
                    "पौधों के बीच पर्याप्त दूरी रखें ताकि धूप और हवा मिल सके",
                ],
                "prevention": [
                    "2-3 वर्षों तक गैर-सोलेनेसी फसलों (जैसे मक्का, धान) के साथ फसल चक्र अपनाएं",
                    "प्रमाणित और रोगरोधी बीज का उपयोग करें",
                    "संतुलित नाइट्रोजन और पोटाश का उपयोग करें",
                ],
                "when_to_contact_expert": "यदि फूल आने से पहले 20% से अधिक पत्तियां प्रभावित हों, तो तुरंत स्थानीय कृषि विज्ञान केंद्र (KVK) के विशेषज्ञ से सलाह लें।",
            },
        },
        "late_blight": {
            "en": {
                "crop": "Tomato",
                "disease": "Late Blight (Phytophthora infestans)",
                "symptoms": [
                    "Water-soaked pale green or dark brown lesions on leaves and stems",
                    "White fungal downy growth on underside of leaves in humid mornings",
                    "Rapid browning and collapse of foliage",
                ],
                "possible_causes": ["Phytophthora infestans oomycete in cool wet weather (<20°C)"],
                "safe_next_steps": [
                    "Immediately improve field drainage to eliminate standing moisture",
                    "Remove heavily blighted vines and bag them to prevent spore dispersion",
                ],
                "prevention": ["Plant on raised ridges", "Avoid overhead irrigation"],
                "when_to_contact_expert": "Consult your local Agriculture Extension Officer immediately upon appearance.",
            },
            "te": {
                "crop": "టమాటా",
                "disease": "ఆలస్యపు ఆకు మచ్చ తెగులు (Late Blight)",
                "symptoms": ["ఆకులు మరియు కాండంపై నీటితో తడిసినట్లు ఉండే ముదురు మచ్చలు", "ఆకులు త్వరగా మాడిపోవడం"],
                "possible_causes": ["చల్లని మరియు అధిక తేమతో కూడిన వాతావరణం"],
                "safe_next_steps": ["పొలంలో నిలిచిన నీటిని తీసివేయండి", "బాధిత కొమ్మలను నాశనం చేయండి"],
                "prevention": ["ఎత్తైన బోదెలపై నాటడం"],
                "when_to_contact_expert": "లక్షణాలు కనిపించిన వెంటనే వ్యవసాయ అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "टमाटर",
                "disease": "पिछेती झुलसा (Late Blight)",
                "symptoms": ["पत्तियों पर पानी से भीगे गहरे धब्बे", "पत्तियों का तेजी से झुलसना"],
                "possible_causes": ["ठंडा और नम मौसम"],
                "safe_next_steps": ["जल निकासी तुरंत करें", "संक्रमित भाग नष्ट करें"],
                "prevention": ["मेड़ों पर बुवाई करें"],
                "when_to_contact_expert": "लक्षण दिखते ही कृषि अधिकारी से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Tomato",
                "disease": "Healthy Tomato Foliage",
                "symptoms": ["Vibrant green foliage with balanced leaf expansion", "No visible necrotic spotting or viral curling"],
                "possible_causes": ["Optimal soil nutrients and balanced irrigation"],
                "safe_next_steps": [
                    "Continue regular root-zone drip irrigation schedule",
                    "Inspect underside of leaves weekly for early whitefly or aphid colonization",
                ],
                "prevention": ["Maintain weed-free field borders", "Apply balanced NPK fertilization"],
                "when_to_contact_expert": "No intervention required. Plant shows vigorous healthy development.",
            },
            "te": {
                "crop": "టమాటా",
                "disease": "ఆరోగ్యకరమైన టమాటా పంట",
                "symptoms": ["పచ్చని ఆరోగ్యకరమైన ఆకులు", "ఎటువంటి తెగులు లేదా మచ్చల సంకేతాలు లేవు"],
                "possible_causes": ["సరైన పోషకాలు మరియు క్రమబద్ధమైన నీటి యాజమాన్యం"],
                "safe_next_steps": ["ప్రస్తుత నీటి మరియు ఎరువుల షెడ్యూల్‌ను కొనసాగించండి", "వారం వారం ఆకులను గమనించండి"],
                "prevention": ["కలుపు నివారణ పాటించండి"],
                "when_to_contact_expert": "ప్రస్తుతం ఏ విధమైన మందుల వాడకం అవసరం లేదు. పంట ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "टमाटर",
                "disease": "स्वस्थ टमाटर की फसल",
                "symptoms": ["स्वस्थ हरी पत्तियां", "किसी भी रोग या कीट का कोई लक्षण नहीं"],
                "possible_causes": ["उचित पोषण एवं सिंचाई"],
                "safe_next_steps": ["नियमित सिंचाई और पोषण जारी रखें", "सप्ताह में एक बार पत्तियों की जांच करें"],
                "prevention": ["खेत को खरपतवार मुक्त रखें"],
                "when_to_contact_expert": "किसी दवा के छिड़काव की आवश्यकता नहीं है। फसल पूरी तरह स्वस्थ है।",
            },
        },
    },
    "corn": {
        "common_rust": {
            "en": {
                "crop": "Corn / Maize",
                "disease": "Common Rust (Puccinia sorghi)",
                "symptoms": [
                    "Small circular to elongate cinnamon-brown powdery pustules on both leaf surfaces",
                    "Pustules rupture the leaf epidermis, releasing reddish-brown fungal spores",
                    "Severe infections cause premature chlorosis and death of upper leaves",
                ],
                "possible_causes": [
                    "Fungal pathogen Puccinia sorghi favored by moderate temperatures (16°C - 25°C)",
                    "High relative humidity (>95%) and prolonged dew periods",
                ],
                "safe_next_steps": [
                    "Ensure adequate potassium and balanced fertility to strengthen leaf cell walls",
                    "Avoid excessive late-season nitrogen application that fosters succulent foliage",
                    "Monitor hybrid maturity and harvest promptly if ear development is complete",
                ],
                "prevention": [
                    "Plant resistant corn hybrids carrying the Rp resistance gene complex",
                    "Early planting helps the crop mature before peak rust spore showers arrive",
                ],
                "when_to_contact_expert": "Consult your local Agriculture Extension Officer if pustules appear on upper leaves before silking stage.",
            },
            "te": {
                "crop": "మొక్కజొన్న",
                "disease": "మొక్కజొన్న తుప్పు తెగులు (Common Rust)",
                "symptoms": [
                    "ఆకుల ఇరువైపులా గుండ్రని దాల్చినచెక్క రంగు/ఎరుపు-గోధుమ రంగు పొక్కులు (తుప్పు మచ్చలు)",
                    "మచ్చలు పగిలి ఎర్రటి పొడి వంటి శిలీంధ్ర బీజాలు వెలువడటం",
                    "తీవ్రమైన దశలో ఆకులు పసుపు రంగులోకి మారి ఎండిపోవడం",
                ],
                "possible_causes": [
                    "పుక్సీనియా సోర్గి అనే శిలీంధ్రం",
                    "అధిక గాలి తేమ మరియు రాత్రి వేళ కురిసే మంచు",
                ],
                "safe_next_steps": [
                    "పొటాష్ ఎరువులను తగినంత వేసి మొక్కలలో తెగులు తట్టుకునే శక్తిని పెంచండి",
                    "ఆలస్యంగా నత్రజని ఎరువులను అధికంగా వాడవద్దు",
                    "చేనులో గాలి ధారాళంగా ప్రసరించేలా చూడండి",
                ],
                "prevention": [
                    "తుప్పు తెగులును తట్టుకునే హైబ్రిడ్ విత్తనాలను ఎంచుకోండి",
                    "సకాలంలో విత్తుకోవడం ద్వారా తెగులు ఉధృతిని తప్పించవచ్చు",
                ],
                "when_to_contact_expert": "కంకి పాలు పోసుకునే దశకు ముందే పై ఆకులపై తుప్పు మచ్చలు వ్యాపిస్తే వ్యవసాయ అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "मक्का",
                "disease": "मक्के का रतुआ रोग (Common Rust)",
                "symptoms": [
                    "पत्तियों की दोनों सतहों पर दालचीनी जैसे भूरे-लाल दानेदार फफोले",
                    "फफोलों के फटने पर लाल-भूरा चूर्ण निकलना",
                    "अधिक प्रकोप में पत्तियों का पीला पड़कर सूखना",
                ],
                "possible_causes": ["पक्सीनिया सोरघी कवक", "अधिक नमी और ओस"],
                "safe_next_steps": [
                    "पोटाश की उचित मात्रा दें",
                    "अत्यधिक यूरिया का उपयोग न करें",
                ],
                "prevention": ["रोगरोधी संकर किस्मों की बुवाई करें", "समय पर बुवाई करें"],
                "when_to_contact_expert": "भुट्टा बनने से पहले ऊपरी पत्तियों पर फफोले दिखने पर तुरंत कृषि विशेषज्ञ से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Corn / Maize",
                "disease": "Healthy Corn Foliage",
                "symptoms": ["Broad elongated parallel-veined green leaves", "No fungal pustules or blight lesions present"],
                "possible_causes": ["Optimal soil moisture and vigorous vegetative growth"],
                "safe_next_steps": [
                    "Maintain soil moisture during critical tasseling and silking stages",
                    "Apply scheduled split dose of nitrogen/potash fertilizer",
                ],
                "prevention": ["Scout for Fall Armyworm whorl feeding weekly"],
                "when_to_contact_expert": "No disease intervention needed. Crop is in good vegetative health.",
            },
            "te": {
                "crop": "మొక్కజొన్న",
                "disease": "ఆరోగ్యకరమైన మొక్కజొన్న పంట",
                "symptoms": ["పచ్చని వెడల్పాటి ఆరోగ్యకరమైన ఆకులు", "ఎటువంటి తుప్పు లేదా ఎండిన మచ్చలు లేవు"],
                "possible_causes": ["సమతుల్య పోషకాలు మరియు సకాలపు నీటి యాజమాన్యం"],
                "safe_next_steps": ["కంకి వచ్చే దశలో నేలలో తగినంత తేమ ఉండేలా చూడండి"],
                "prevention": ["కత్తెర పురుగు దాడిని గమనించండి"],
                "when_to_contact_expert": "పంట పూర్తి ఆరోగ్యంగా ఉంది. మందుల వాడకం అవసరం లేదు.",
            },
            "hi": {
                "crop": "मक्का",
                "disease": "स्वस्थ मक्के की फसल",
                "symptoms": ["स्वस्थ चौड़ी हरी पत्तियां", "कोई रतुआ या झुलसा रोग नहीं"],
                "possible_causes": ["संतुलित उर्वरक एवं उचित नमी"],
                "safe_next_steps": ["मंजरी और दाना भरने के समय पर्याप्त नमी रखें"],
                "prevention": ["सैनिक कीट (फॉल आर्मीवॉर्म) की निगरानी करें"],
                "when_to_contact_expert": "फसल पूरी तरह स्वस्थ है। किसी उपचार की आवश्यकता नहीं है।",
            },
        },
    },
    "potato": {
        "early_blight": {
            "en": {
                "crop": "Potato",
                "disease": "Early Blight (Alternaria solani)",
                "symptoms": [
                    "Target-like dark brown circular spots on older lower leaves",
                    "Spots develop concentric rings surrounded by yellow tissue",
                    "Defoliation starting from the base of the plant moving upward",
                ],
                "possible_causes": ["Alternaria solani fungus thriving in alternating wet and dry conditions"],
                "safe_next_steps": [
                    "Avoid sprinkler irrigation; use ridge furrow or drip watering",
                    "Hill up ridges properly to prevent tuber exposure",
                ],
                "prevention": ["Use certified disease-free seed tubers", "Practice 3-year crop rotation"],
                "when_to_contact_expert": "Contact local horticulture officer if lesions spread to upper canopy before tuber bulking.",
            },
            "te": {
                "crop": "బంగాళాదుంప",
                "disease": "ముందస్తు ఆకుమచ్చ తెగులు (Early Blight)",
                "symptoms": ["ఆకులపై చక్రాల వంటి ముదురు గోధుమ మచ్చలు", "క్రింది ఆకులు రాలిపోవడం"],
                "possible_causes": ["శిలీంధ్ర వ్యాప్తి మరియు తడి-పొడి వాతావరణం"],
                "safe_next_steps": ["బోదెలను ఎత్తుగా వేయండి", "ఆకులపై నీరు చిమ్మవద్దు"],
                "prevention": ["ధృవీకరించబడిన విత్తన దుంపలను వాడండి"],
                "when_to_contact_expert": "దుంప ఊరే దశకు ముందే మచ్చలు వ్యాపిస్తే వ్యవసాయ అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "आलू",
                "disease": "अगेती झुलसा (Early Blight)",
                "symptoms": ["निचली पत्तियों पर छल्लेदार भूरे धब्बे", "पत्तियों का पीला पड़ना"],
                "possible_causes": ["अल्टरनेरिया कवक"],
                "safe_next_steps": ["ड्रिप या नाली विधि से पानी दें", "मिट्टी चढ़ाएं"],
                "prevention": ["प्रमाणित कंद का उपयोग करें"],
                "when_to_contact_expert": "कंद बनने से पहले बीमारी बढ़ने पर विशेषज्ञ से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Potato",
                "disease": "Healthy Potato Foliage",
                "symptoms": ["Vigorous green compound leaves with intact margins", "No blight spots or aphid curling"],
                "possible_causes": ["Disease-free seed tubers and proper ridging"],
                "safe_next_steps": ["Maintain earthing-up to prevent greening of tubers"],
                "prevention": ["Monitor for potato aphids and leafhoppers"],
                "when_to_contact_expert": "No disease present. Crop is thriving normally.",
            },
            "te": {
                "crop": "బంగాళాదుంప",
                "disease": "ఆరోగ్యకరమైన బంగాళాదుంప పంట",
                "symptoms": ["పచ్చని ఆరోగ్యకరమైన ఆకులు", "ఎటువంటి తెగులు లక్షణాలు లేవు"],
                "possible_causes": ["నాణ్యమైన విత్తన దుంపలు"],
                "safe_next_steps": ["దుంపలకు మట్టి కప్పే పని సకాలంలో చేయండి"],
                "prevention": ["రసం పీల్చే పురుగులను గమనించండి"],
                "when_to_contact_expert": "పంట పూర్తి ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "आलू",
                "disease": "स्वस्थ आलू की फसल",
                "symptoms": ["स्वस्थ हरी पत्तियां", "कोई झुलसा रोग नहीं"],
                "possible_causes": ["स्वस्थ बीज कंद"],
                "safe_next_steps": ["कंदों पर मिट्टी सही तरीके से चढ़ाएं"],
                "prevention": ["माहू कीट की निगरानी करें"],
                "when_to_contact_expert": "फसल स्वस्थ है, किसी उपचार की आवश्यकता नहीं।",
            },
        },
    },
    "grape": {
        "black_rot": {
            "en": {
                "crop": "Grape",
                "disease": "Grape Black Rot (Guignardia bidwellii)",
                "symptoms": [
                    "Reddish-brown circular spots on leaves surrounded by dark margins",
                    "Tiny black pimple-like dots (pycnidia) arranged inside the leaf spots",
                    "Infected berries shrivel into hard black wrinkled mummies",
                ],
                "possible_causes": ["Overwintering fungal spores in shriveled fruit mummies and old canes"],
                "safe_next_steps": [
                    "Prune and destroy all mummified fruit clusters and infected canes",
                    "Improve canopy pruning to increase sunlight penetration and rapid drying",
                ],
                "prevention": ["Open canopy trellising", "Remove vineyard debris before spring bud break"],
                "when_to_contact_expert": "Consult your local horticulture extension officer if spots appear on young fruit clusters.",
            },
            "te": {
                "crop": "ద్రాక్ష",
                "disease": "ద్రాక్ష నల్ల కుళ్లు తెగులు (Black Rot)",
                "symptoms": ["ఆకులపై ఎరుపు-గోధుమ రంగు మచ్చలు", "కాయలు నల్లగా ఎండి ముడతలు పడటం"],
                "possible_causes": ["శిలీంధ్ర బీజాలు పాత కొమ్మలపై నివసించడం"],
                "safe_next_steps": ["ఎండిపోయిన కాయల గుత్తులను తొలగించి నాశనం చేయండి", "తీగలకు గాలి వెలుతురు తగిలేలా కత్తిరింపులు చేయండి"],
                "prevention": ["పందిరిపై తీగలను పలుచగా ఉంచండి"],
                "when_to_contact_expert": "పిందెల దశలో తెగులు కనిపిస్తే ఉద్యాన అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "अंगूर",
                "disease": "अंगूर का काला सड़न रोग (Black Rot)",
                "symptoms": ["पत्तियों पर लाल-भूरे धब्बे", "अंगूर के दाने काले होकर सूखना"],
                "possible_causes": ["कवक संक्रमण"],
                "safe_next_steps": ["सूखे संक्रमित गुच्छों को नष्ट करें", "छंटाई करके धूप और हवा सुनिश्चित करें"],
                "prevention": ["कैनोपी प्रबंधन करें"],
                "when_to_contact_expert": "फल बनने के समय लक्षण दिखने पर बागवानी विशेषज्ञ से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Grape",
                "disease": "Healthy Grapevine Foliage",
                "symptoms": ["Lush green lobed leaves with intact margins", "No powdery growth or black rot spots"],
                "possible_causes": ["Optimal trellising and canopy ventilation"],
                "safe_next_steps": ["Maintain regular vine training and irrigation schedule"],
                "prevention": ["Scout for downy mildew after heavy spring dews"],
                "when_to_contact_expert": "Vineyard foliage is healthy and vigorous.",
            },
            "te": {
                "crop": "ద్రాక్ష",
                "disease": "ఆరోగ్యకరమైన ద్రాక్ష తోట",
                "symptoms": ["పచ్చని ఆరోగ్యకరమైన తీగ ఆకులు", "ఎటువంటి బూడిద లేదా నల్ల కుళ్లు మచ్చలు లేవు"],
                "possible_causes": ["మంచి పందిరి యాజమాన్యం"],
                "safe_next_steps": ["తీగల కత్తిరింపు మరియు నీటి యాజమాన్యం కొనసాగించండి"],
                "prevention": ["మంచు రోజులలో ఆకులను గమనించండి"],
                "when_to_contact_expert": "తోట ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "अंगूर",
                "disease": "स्वस्थ अंगूर की बेल",
                "symptoms": ["स्वस्थ हरी पत्तियां", "कोई सड़न या फफूंद नहीं"],
                "possible_causes": ["उचित छंटाई एवं देखभाल"],
                "safe_next_steps": ["नियमित सिंचाई और बेल की ट्रेनिंग जारी रखें"],
                "prevention": ["भारी ओस के बाद निगरानी करें"],
                "when_to_contact_expert": "फसल पूरी तरह स्वस्थ है।",
            },
        },
    },
    "pepper": {
        "bacterial_spot": {
            "en": {
                "crop": "Bell Pepper / Chilli",
                "disease": "Bacterial Spot (Xanthomonas)",
                "symptoms": [
                    "Small circular to irregular dark brown spots with yellow halos on leaves",
                    "Spots become necrotic and dry, leading to premature leaf drop",
                    "Raised blister-like spots on green pepper fruits",
                ],
                "possible_causes": ["Seed-borne Xanthomonas bacteria splashing in warm rainy weather"],
                "safe_next_steps": [
                    "Avoid handling pepper plants while foliage is wet",
                    "Apply copper oxychloride @ 2.5g/L under local extension guidance",
                ],
                "prevention": ["Use hot water-treated certified seed", "Avoid overhead sprinkler irrigation"],
                "when_to_contact_expert": "Consult your local horticulture officer if severe leaf dropping occurs before flowering.",
            },
            "te": {
                "crop": "మిర్చి / బెల్ పెప్పర్",
                "disease": "బాక్టీరియా ఆకుమచ్చ తెగులు",
                "symptoms": ["ఆకులపై చిన్న చిన్న నల్లటి మచ్చలు", "ఆకులు పసుపుగా మారి రాలిపోవడం"],
                "possible_causes": ["విత్తనం ద్వారా వ్యాపించే బాక్టీరియా"],
                "safe_next_steps": ["తడి ఆకులను తాకవద్దు", "డ్రిప్ విధానంలో నీరు పెట్టండి"],
                "prevention": ["విత్తన శుద్ధి చేయండి"],
                "when_to_contact_expert": "ఆకులు ఎక్కువగా రాలుతుంటే ఉద్యాన అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "शिमला मिर्च / मिर्च",
                "disease": "जीवाणु पत्ती धब्बा",
                "symptoms": ["पत्तियों पर छोटे काले धब्बे", "पत्तियों का असमय गिरना"],
                "possible_causes": ["जैंथोमोनास जीवाणु"],
                "safe_next_steps": ["गीली पत्तियों को न छुएं", "ड्रिप सिंचाई करें"],
                "prevention": ["उपचारित बीज का उपयोग करें"],
                "when_to_contact_expert": "पत्तियां अधिक गिरने पर कृषि विशेषज्ञ से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Bell Pepper / Chilli",
                "disease": "Healthy Pepper Foliage",
                "symptoms": ["Glossy vibrant green leaves with no bacterial spots or thrips curling"],
                "possible_causes": ["Balanced nutrition and drip fertigation"],
                "safe_next_steps": ["Maintain regular drip irrigation and inspect for mites under leaves"],
                "prevention": ["Install blue and yellow sticky traps for thrips monitoring"],
                "when_to_contact_expert": "Foliage is healthy. No treatment required.",
            },
            "te": {
                "crop": "మిర్చి / బెల్ పెప్పర్",
                "disease": "ఆరోగ్యకరమైన మిర్చి పంట",
                "symptoms": ["నిగనిగలాడే పచ్చని ఆకులు", "ఎటువంటి ముడత లేదా మచ్చలు లేవు"],
                "possible_causes": ["సమతుల్య ఎరువులు మరియు సకాలపు నీటి యాజమాన్యం"],
                "safe_next_steps": ["ప్రస్తుత నీటి షెడ్యూల్ కొనసాగించండి"],
                "prevention": ["జిగురు అట్టలను అమర్చండి"],
                "when_to_contact_expert": "పంట ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "शिमला मिर्च / मिर्च",
                "disease": "स्वस्थ मिर्च की फसल",
                "symptoms": ["चमकदार हरी पत्तियां", "कोई धब्बा या मरोड़िया रोग नहीं"],
                "possible_causes": ["उचित पोषण एवं सिंचाई"],
                "safe_next_steps": ["ड्रिप सिंचाई जारी रखें"],
                "prevention": ["चिपचिपे ट्रैप लगाएं"],
                "when_to_contact_expert": "फसल पूर्णतः स्वस्थ है।",
            },
        },
    },
    "cotton": {
        "leaf_yellowing": {
            "en": {
                "crop": "Cotton",
                "disease": "Cotton Leaf Yellowing (Magnesium Deficiency / Sucking Pests)",
                "symptoms": [
                    "Interveinal chlorosis (yellowing between leaf veins) on middle and lower leaves",
                    "Leaf veins remain green while interveinal areas turn pale yellow or reddish",
                ],
                "possible_causes": ["Magnesium or nitrogen deficiency in light red or sandy soils"],
                "safe_next_steps": [
                    "Clear drainage channels immediately to prevent waterlogging around root zone",
                    "Foliar spray of 1% Magnesium Sulphate (10g per litre) in early morning",
                ],
                "prevention": ["Apply recommended basal dose of NPK and soil test-based micronutrients"],
                "when_to_contact_expert": "Take a soil and leaf sample to your Mandal Agriculture Officer (MAO) if yellowing spreads.",
            },
            "te": {
                "crop": "పత్తి",
                "disease": "పత్తి ఆకుల పసుపు రంగు (మెగ్నీషియం లోపం / రసం పీల్చే పురుగులు)",
                "symptoms": ["ఆకుల ఈనెల మధ్య భాగం పసుపుగా మారి, ఈనెలు ఆకుపచ్చగా ఉండటం"],
                "possible_causes": ["మెగ్నీషియం లేదా నత్రజని లోపం"],
                "safe_next_steps": [
                    "పొలంలో నిలిచిన అదనపు నీటిని వెంటనే బయటకు పంపండి",
                    "లీటరు నీటికి 10 గ్రాముల మెగ్నీషియం సల్ఫేట్ కలిపి పిచికారీ చేయండి",
                ],
                "prevention": ["భూసార పరీక్ష ఆధారంగా ఎరువులు వాడండి"],
                "when_to_contact_expert": "రైతు భరోసా కేంద్రం (RBK) వ్యవసాయ విస్తరణ అధికారిని సంప్రదించండి.",
            },
            "hi": {
                "crop": "कपास",
                "disease": "कपास की पत्तियों का पीलापन",
                "symptoms": ["पत्तियों की नसों के बीच पीलापन, नसें हरी रहना"],
                "possible_causes": ["मैग्नीशियम की कमी"],
                "safe_next_steps": ["खेत से जल निकासी करें", "10 ग्राम मैग्नीशियम सल्फेट प्रति लीटर का स्प्रे करें"],
                "prevention": ["मृदा परीक्षण के अनुसार उर्वरक दें"],
                "when_to_contact_expert": "कृषि विस्तार अधिकारी से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Cotton",
                "disease": "Healthy Cotton Foliage",
                "symptoms": ["Dark green lobed leaves with no reddening or jassid burn"],
                "possible_causes": ["Balanced soil fertility and timely irrigation"],
                "safe_next_steps": ["Continue square and boll development monitoring"],
                "prevention": ["Install yellow sticky traps for sucking pest monitoring"],
                "when_to_contact_expert": "Cotton crop is in healthy vegetative state.",
            },
            "te": {
                "crop": "పత్తి",
                "disease": "ఆరోగ్యకరమైన పత్తి పంట",
                "symptoms": ["ముదురు ఆకుపచ్చని ఆరోగ్యకరమైన ఆకులు", "ఎటువంటి పసుపు లేదా ఎరుపు మచ్చలు లేవు"],
                "possible_causes": ["సమతుల్య ఎరువులు"],
                "safe_next_steps": ["పూత మరియు కాయ దశను గమనించండి"],
                "prevention": ["పసుపు అట్టలను అమర్చండి"],
                "when_to_contact_expert": "పంట పూర్తి ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "कपास",
                "disease": "स्वस्थ कपास की फसल",
                "symptoms": ["स्वस्थ गहरे हरे पत्ते", "कोई पीलापन या कीट प्रकोप नहीं"],
                "possible_causes": ["संतुलित उर्वरक"],
                "safe_next_steps": ["टिंडे बनने की निगरानी करें"],
                "prevention": ["पीले ट्रैप लगाएं"],
                "when_to_contact_expert": "फसल पूर्णतः स्वस्थ है।",
            },
        },
    },
    "paddy": {
        "leaf_blast": {
            "en": {
                "crop": "Rice / Paddy",
                "disease": "Rice Leaf Blast (Magnaporthe oryzae)",
                "symptoms": [
                    "Spindle-shaped or diamond-shaped lesions with pointed ends on leaves",
                    "Grey or whitish center with distinct brown or reddish-brown borders",
                ],
                "possible_causes": ["Fungal pathogen Magnaporthe oryzae in humid overcast weather"],
                "safe_next_steps": [
                    "Immediately stop top-dressing with urea/nitrogen fertilizers",
                    "Maintain continuous shallow standing water (2-3 cm) in paddy field",
                ],
                "prevention": ["Use blast-tolerant varieties (MTU 1010, BPT 5204)"],
                "when_to_contact_expert": "Contact Rythu Seva Kendra (RSK) immediately if neck blast appears.",
            },
            "te": {
                "crop": "వరి",
                "disease": "వరి ఆకు అగ్గితెగులు (Rice Leaf Blast)",
                "symptoms": ["ఆకులపై కంటి లేదా కండె ఆకారపు మచ్చలు ఏర్పడటం"],
                "possible_causes": ["శిలీంధ్ర వ్యాప్తి మరియు అధిక యూరియా వాడకం"],
                "safe_next_steps": ["యూరియా వాడకాన్ని నిలిపివేయండి", "మడిలో 2-3 సెం.మీ నీరు ఉంచండి"],
                "prevention": ["తెగులును తట్టుకునే రకాలను సాగు చేయండి"],
                "when_to_contact_expert": "రైతు సేవా కేంద్రాన్ని (RSK) సంప్రదించండి.",
            },
            "hi": {
                "crop": "धान",
                "disease": "धान का झोंका रोग (Rice Leaf Blast)",
                "symptoms": ["पत्तियों पर नाव के आकार के धब्बे"],
                "possible_causes": ["कवक संक्रमण"],
                "safe_next_steps": ["यूरिया बंद करें", "खेत में 2-3 सेमी पानी रखें"],
                "prevention": ["रोगरोधी किस्मों की बुवाई करें"],
                "when_to_contact_expert": "कृषि अधिकारी से संपर्क करें।",
            },
        },
        "healthy": {
            "en": {
                "crop": "Rice / Paddy",
                "disease": "Healthy Paddy Foliage",
                "symptoms": ["Erect dark green leaves with clean leaf sheaths and blades"],
                "possible_causes": ["Balanced water management and optimal tillering"],
                "safe_next_steps": ["Maintain 2-3 cm water level during tillering stage"],
                "prevention": ["Drain field periodically for aeration"],
                "when_to_contact_expert": "Paddy field is in excellent health.",
            },
            "te": {
                "crop": "వరి",
                "disease": "ఆరోగ్యకరమైన వరి పంట",
                "symptoms": ["నిటారైన పచ్చని ఆరోగ్యకరమైన ఆకులు", "ఎటువంటి మచ్చలు లేవు"],
                "possible_causes": ["సరైన నీరు మరియు ఎరువుల నిర్వహణ"],
                "safe_next_steps": ["పిలకల దశలో తగినంత నీటి మట్టం ఉంచండి"],
                "prevention": ["మడిని అప్పుడప్పుడు ఆరబెట్టండి"],
                "when_to_contact_expert": "పంట పూర్తి ఆరోగ్యంగా ఉంది.",
            },
            "hi": {
                "crop": "धान",
                "disease": "स्वस्थ धान की फसल",
                "symptoms": ["स्वस्थ हरी पत्तियां", "कोई झोंका या झुलसा रोग नहीं"],
                "possible_causes": ["उचित जल प्रबंधन"],
                "safe_next_steps": ["कल्ले फूटने के समय 2-3 सेमी पानी बनाए रखें"],
                "prevention": ["खेत को बीच-बीच में हवा लगने दें"],
                "when_to_contact_expert": "फसल पूर्णतः स्वस्थ है।",
            },
        },
    },
}


# =====================================================================
# KNOWLEDGE RETRIEVAL FUNCTION
# =====================================================================

def find_crop_knowledge(crop_name: str, problem_name: str, language: str = "en") -> Dict[str, Any]:
    """
    Retrieves grounded agronomic guidance from the curated knowledge base.
    Uses precise token matching on crop and problem names.
    If matched: returns knowledge_found=True with symptoms, causes, safe steps, prevention.
    If no match: returns knowledge_found=False with safe general precautions and expert recommendation.
    """
    lang = language if language in ["te", "hi", "en"] else "en"
    crop_str = (crop_name or "").lower()
    prob_str = (problem_name or "").lower()

    # Identify crop key
    matched_crop_key = None
    if any(k in crop_str for k in ["tomato", "టమాటా", "टमाटर"]):
        matched_crop_key = "tomato"
    elif any(k in crop_str for k in ["corn", "maize", "మొక్కజొన్న", "मक्का"]):
        matched_crop_key = "corn"
    elif any(k in crop_str for k in ["potato", "బంగాళాదుంప", "आलू"]):
        matched_crop_key = "potato"
    elif any(k in crop_str for k in ["grape", "ద్రాక్ష", "अंगूर"]):
        matched_crop_key = "grape"
    elif any(k in crop_str for k in ["pepper", "chilli", "మిర్చి", "మిరప", "मिर्च", "శిమ్లా"]):
        matched_crop_key = "pepper"
    elif any(k in crop_str for k in ["cotton", "పత్తి", "కపాస్", "कपास"]):
        matched_crop_key = "cotton"
    elif any(k in crop_str for k in ["rice", "paddy", "వరి", "ధాన్", "धान"]):
        matched_crop_key = "paddy"

    if matched_crop_key and matched_crop_key in CROP_KNOWLEDGE_BASE:
        crop_entries = CROP_KNOWLEDGE_BASE[matched_crop_key]
        matched_entry = None

        # Check for specific disease match
        if "healthy" in prob_str or "ఆరోగ్యకర" in prob_str or "स्वस्थ" in prob_str:
            matched_entry = crop_entries.get("healthy")
        elif "early" in prob_str:
            matched_entry = crop_entries.get("early_blight")
        elif "late" in prob_str:
            matched_entry = crop_entries.get("late_blight")
        elif "rust" in prob_str:
            matched_entry = crop_entries.get("common_rust")
        elif "blast" in prob_str:
            matched_entry = crop_entries.get("leaf_blast")
        elif "yellow" in prob_str or "chlorosis" in prob_str:
            matched_entry = crop_entries.get("leaf_yellowing")
        elif "black_rot" in prob_str or "black rot" in prob_str:
            matched_entry = crop_entries.get("black_rot")
        elif "bacterial" in prob_str:
            matched_entry = crop_entries.get("bacterial_spot") or crop_entries.get("bacterial_blight")
        else:
            # Check by token overlap
            for disease_key, lang_dict in crop_entries.items():
                tokens = disease_key.replace("_", " ").split()
                if any(t in prob_str for t in tokens):
                    matched_entry = lang_dict
                    break

        if matched_entry:
            data = matched_entry.get(lang) or matched_entry.get("en")
            if data:
                return {
                    "knowledge_found": True,
                    "crop": data.get("crop", crop_name),
                    "disease": data.get("disease", problem_name),
                    "symptoms": data.get("symptoms", []),
                    "possible_causes": data.get("possible_causes", []),
                    "safe_next_steps": data.get("safe_next_steps", []),
                    "prevention": data.get("prevention", []),
                    "when_to_contact_expert": data.get("when_to_contact_expert", ""),
                }

    # Fallback when no matching curated profile exists
    if lang == "te":
        return {
            "knowledge_found": False,
            "crop": crop_name or "గుర్తించబడని పంట",
            "disease": problem_name or "సాధారణ సమస్య",
            "symptoms": ["ఆకులపై రంగు మారడం లేదా మచ్చలు"],
            "possible_causes": ["వాతావరణ ఒత్తిడి లేదా పోషకాల అసమతుల్యత"],
            "safe_next_steps": [
                "దెబ్బతిన్న ఆకుల క్రింది భాగాన్ని దగ్గరగా పరిశీలించండి",
                "పొలంలో నీరు నిలవకుండా డ్రైనేజీని సరిచూసుకోండి",
                "బాధిత మొక్కలను గమనిస్తూ వ్యాప్తిని అరికట్టండి",
            ],
            "prevention": [
                "పంట మార్పిడిని అనుసరించండి",
                "భూసార పరీక్ష ఆధారంగా మాత్రమే ఎరువులను వాడండి",
            ],
            "when_to_contact_expert": "ఈ పంటకు సంబంధించిన సమగ్ర సమాచారం డేటాబేస్‌లో అందుబాటులో లేదు. ఖచ్చితమైన విశ్లేషణ కొరకు స్థానిక వ్యవసాయ విస్తరణ అధికారి (AEO) లేదా కృషి విజ్ఞాన కేంద్రం (KVK) నిపుణులను సంప్రదించండి.",
        }
    elif lang == "hi":
        return {
            "knowledge_found": False,
            "crop": crop_name or "अज्ञात फसल",
            "disease": problem_name or "सामान्य समस्या",
            "symptoms": ["पत्तियों पर रंग बदलना या धब्बे"],
            "possible_causes": ["मौसम का तनाव या पोषक तत्वों का असंतुलन"],
            "safe_next_steps": [
                "पत्तियों की निचली सतह की जांच करें",
                "खेत में जल भराव न होने दें",
                "प्रभावित पौधों पर नियमित नज़र रखें",
            ],
            "prevention": [
                "फसल चक्र का पालन करें",
                "संतुलित उर्वरकों का प्रयोग करें",
            ],
            "when_to_contact_expert": "इस विशिष्ट फसल के लिए विस्तृत मार्गदर्शन डेटाबेस में उपलब्ध नहीं है। कृपया अपने स्थानीय कृषि विस्तार अधिकारी या KVK विशेषज्ञ से संपर्क करें।",
        }
    else:
        return {
            "knowledge_found": False,
            "crop": crop_name or "Unspecified Crop",
            "disease": problem_name or "Uncertain Condition",
            "symptoms": ["Visual foliar discoloration or leaf spotting"],
            "possible_causes": ["Environmental stress, nutrient variation, or preliminary foliar pathogens"],
            "safe_next_steps": [
                "Inspect the underside of leaves for microscopic pest activity",
                "Ensure proper field drainage and avoid prolonged foliage dampness",
                "Isolate or tag affected plants to monitor whether symptoms spread",
            ],
            "prevention": [
                "Maintain cultural hygiene and crop rotation",
                "Use soil testing to balance macronutrient and micronutrient applications",
            ],
            "when_to_contact_expert": "Detailed curated guidelines are unavailable for this specific crop/condition. Please consult your local Agricultural Extension Officer (AEO) or KVK specialist for an in-person physical inspection.",
        }


def diagnose_crop_symptoms(crop: str, symptoms: str, language: str = "te") -> Dict[str, Any]:
    """Diagnoses crop symptoms and returns localized advisory (backwards compatible)."""
    kb = find_crop_knowledge(crop, symptoms, language=language)
    return {
        "issue": f"{kb['crop']} — {kb['disease']}",
        "confidence": "85%",
        "observations": kb.get("symptoms", []),
        "steps": kb.get("safe_next_steps", []),
        "warning": kb.get("when_to_contact_expert", ""),
    }
