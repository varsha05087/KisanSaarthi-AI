import urllib.request
import json
import sys

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

base_url = "http://127.0.0.1:8000/api/chat"

test_queries = [
    ("Paddy Straw (EN)", "I have a lot of paddy straw. What can I do with it?", "en"),
    ("Cotton Stalks (EN)", "I have cotton stalks left after harvesting. What should I do?", "en"),
    ("Sugarcane Waste (EN)", "I have sugarcane waste. How can I use it?", "en"),
    ("Maize Stalks (EN)", "I have maize stalks. What is the best way to utilize them?", "en"),
    ("Farm Waste Unspecified (EN)", "I have farm waste. What can I do with it?", "en"),
    ("Paddy Straw (TE)", "వరి గడ్డి ఉంది ఏం చేయాలి?", "te"),
    ("Cotton Stalks (TE)", "పత్తి కట్టెలు ఉన్నాయి ఏం చేయాలి?", "te"),
    ("Farm Waste Unspecified (TE)", "పంట వ్యర్థాలు ఉన్నాయి ఏం చేయాలి?", "te"),
    ("Paddy Straw (HI)", "धान की पराली का क्या करें?", "hi"),
    ("Cotton Stalks (HI)", "कपास के डंठल हैं क्या करें?", "hi"),
    ("Farm Waste Unspecified (HI)", "फसल अवशेष हैं क्या करें?", "hi"),
]

all_passed = True
for label, query, lang in test_queries:
    data = json.dumps({"message": query, "language": lang, "farmer_id": "test_residue"}).encode("utf-8")
    req = urllib.request.Request(base_url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        intent = res.get("intent")
        agent = res.get("agent")
        text = res.get("response", "")
        status = res.get("status")
        
        print(f"=== {label} ===")
        print(f"Query: {query}")
        print(f"Intent: {intent} | Agent: {agent} | Status: {status}")
        print(f"Response:\n{text}\n")
        
        if intent != "agricycle":
            print(f"FAILURE: Expected intent 'agricycle', got '{intent}'")
            all_passed = False
        if not ("burn" in text.lower() or "కాల్చ" in text or "जला" in text):
            print(f"WARNING: No anti-burning advisory found!")
            all_passed = False

if all_passed:
    print(">>> ALL 11 MULTI-CROP RESIDUE API TESTS PASSED! <<<")
else:
    print(">>> SOME TESTS FAILED <<<")
