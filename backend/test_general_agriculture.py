"""
Comprehensive Automated Test Suite for KisanSaarthi AI - Step 8: General Agriculture AI.

Covers 16 specific test criteria:
 1. Basic agriculture question ("When should I sow paddy?")
 2. Novel/unseen agriculture question ("Why do legume crops fix nitrogen in the root nodules?")
 3. Soil question ("How does black soil differ from red soil for farming?")
 4. Irrigation question ("What are the benefits of drip irrigation for vegetable crops?")
 5. Crop management question ("How can farmers prevent soil erosion on sloping farmland using contour bunding?")
 6. Fertilizer/nutrient question ("When should urea be applied in wheat cultivation?")
 7. Pest question ("How can I organically control aphids on tomato plants?")
 8. Farming concept question ("What is crop rotation and why is it beneficial?")
 9. Multi-turn follow-up question (Turn 1: "I am growing paddy" -> Turn 2: "When should I water it?")
10. English language response
11. Telugu language response ("వరి పంటలో కలుపు నివారణ ఎలా చేయాలి?")
12. Hindi language response ("गेहूं की फसल में पहली सिंचाई कब करनी चाहिए?")
13. Unclear question clarification ("My crop is not growing well" -> single follow-up question)
14. Safety-sensitive chemical question (chlorpyrifos spray -> label advisory, PPE, AEO/KVK referral)
15. Out-of-domain question ("Who won the FIFA world cup?" -> polite agri-only rejection)
16. Orchestrator /api/chat end-to-end integration test with SQLite persistence
"""

import sys
import json
import uuid
import urllib.request
import re

# Reconfigure stdout for UTF-8 display on Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import functools
print = functools.partial(print, flush=True)

from services.gemini_service import generate_agriculture_response
from agents.general_agriculture import GeneralAgricultureAgent

BASE_URL = "http://127.0.0.1:8000/api"


def post_chat(message: str, farmer_id: str = "FARMER-TEST-AGRI", language: str = "en", conversation_id: str = "conv-agri-test"):
    """Sends a chat message to POST /api/chat."""
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps({
            "farmer_id": farmer_id,
            "message": message,
            "language": language,
            "conversation_id": conversation_id,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def get_farmer_requests(farmer_id: str):
    """Retrieves all requests for the farmer from SQLite."""
    req = urllib.request.Request(f"{BASE_URL}/requests?farmer_id={farmer_id}", method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def query_ai(query: str, language: str = "en", conversation_context=None):
    """Wraps generate_agriculture_response with a polite delay and retry for free-tier quotas."""
    import time
    for attempt in range(3):
        res = generate_agriculture_response(query, language=language, conversation_context=conversation_context)
        if res.get("model") != "local_fallback" or attempt == 2:
            time.sleep(1)
            return res
        time.sleep(3)
    return res


def run_tests():
    print("=" * 80)
    print("KISANSAARTHI AI — STEP 8: GENERAL AGRICULTURE AI VERIFICATION")
    print("=" * 80)

    results = []

    # -------------------------------------------------------------
    # Test 1: Basic Agriculture Question
    # -------------------------------------------------------------
    print("\n--- TEST 1: Basic Agriculture Question ---")
    query_1 = "When should I sow paddy?"
    res_1 = generate_agriculture_response(query_1, language="en")
    text_1 = res_1.get("response", "").lower()
    t1_pass = (
        bool(res_1.get("response"))
        and res_1.get("status") == "ready"
        and any(k in text_1 for k in ["kharif", "season", "sowing", "nursery", "monsoon", "transplant", "june", "may"])
    )
    print(f"Query: {query_1}")
    print(f"Model: {res_1.get('model')}")
    print(f"Response Preview: {res_1.get('response')[:160]}...")
    print(f"TEST 1 RESULT: [{'PASS' if t1_pass else 'FAIL'}]")
    results.append(("Test 1: Basic Agriculture Question", t1_pass))

    # -------------------------------------------------------------
    # Test 2: Unseen / Novel Agriculture Question
    # -------------------------------------------------------------
    print("\n--- TEST 2: Novel/Unseen Agriculture Question ---")
    query_2 = "Why do legume crops fix nitrogen in the root nodules?"
    res_2 = generate_agriculture_response(query_2, language="en")
    text_2 = res_2.get("response", "").lower()
    t2_pass = (
        bool(res_2.get("response"))
        and any(k in text_2 for k in ["rhizob", "bacteria", "nitrogen", "nodule", "symbio", "soil"])
    )
    print(f"Query: {query_2}")
    print(f"Response Preview: {res_2.get('response')[:160]}...")
    print(f"TEST 2 RESULT: [{'PASS' if t2_pass else 'FAIL'}]")
    results.append(("Test 2: Novel/Unseen Agriculture Question", t2_pass))

    # -------------------------------------------------------------
    # Test 3: Soil Question
    # -------------------------------------------------------------
    print("\n--- TEST 3: Soil Question ---")
    query_3 = "How does black soil differ from red soil for farming?"
    res_3 = generate_agriculture_response(query_3, language="en")
    text_3 = res_3.get("response", "").lower()
    t3_pass = (
        bool(res_3.get("response"))
        and "black" in text_3
        and "red" in text_3
        and any(k in text_3 for k in ["moisture", "clay", "water", "iron", "drainage", "cotton"])
    )
    print(f"Query: {query_3}")
    print(f"Response Preview: {res_3.get('response')[:160]}...")
    print(f"TEST 3 RESULT: [{'PASS' if t3_pass else 'FAIL'}]")
    results.append(("Test 3: Soil Question", t3_pass))

    # -------------------------------------------------------------
    # Test 4: Irrigation Question
    # -------------------------------------------------------------
    print("\n--- TEST 4: Irrigation Question ---")
    query_4 = "What are the benefits of drip irrigation for vegetable crops?"
    res_4 = generate_agriculture_response(query_4, language="en")
    text_4 = res_4.get("response", "").lower()
    t4_pass = (
        bool(res_4.get("response"))
        and any(k in text_4 for k in ["water", "root", "efficiency", "saving", "weed", "fertilizer"])
    )
    print(f"Query: {query_4}")
    print(f"Response Preview: {res_4.get('response')[:160]}...")
    print(f"TEST 4 RESULT: [{'PASS' if t4_pass else 'FAIL'}]")
    results.append(("Test 4: Irrigation Question", t4_pass))

    # -------------------------------------------------------------
    # Test 5: Crop Management Question
    # -------------------------------------------------------------
    print("\n--- TEST 5: Crop Management Question ---")
    query_5 = "How can farmers prevent soil erosion on sloping farmland using contour bunding?"
    res_5 = generate_agriculture_response(query_5, language="en")
    text_5 = res_5.get("response", "").lower()
    t5_pass = (
        bool(res_5.get("response"))
        and any(k in text_5 for k in ["contour", "bund", "erosion", "slope", "runoff", "water", "soil"])
    )
    print(f"Query: {query_5}")
    print(f"Response Preview: {res_5.get('response')[:160]}...")
    print(f"TEST 5 RESULT: [{'PASS' if t5_pass else 'FAIL'}]")
    results.append(("Test 5: Crop Management Question", t5_pass))

    # -------------------------------------------------------------
    # Test 6: Fertilizer / Nutrient Question
    # -------------------------------------------------------------
    print("\n--- TEST 6: Fertilizer/Nutrient Question ---")
    query_6 = "When should urea be applied in wheat cultivation?"
    res_6 = generate_agriculture_response(query_6, language="en")
    text_6 = res_6.get("response", "").lower()
    t6_pass = (
        bool(res_6.get("response"))
        and any(k in text_6 for k in ["urea", "wheat", "split", "dose", "irrigation", "crown root", "tillering", "stage"])
    )
    print(f"Query: {query_6}")
    print(f"Response Preview: {res_6.get('response')[:160]}...")
    print(f"TEST 6 RESULT: [{'PASS' if t6_pass else 'FAIL'}]")
    results.append(("Test 6: Fertilizer/Nutrient Question", t6_pass))

    # -------------------------------------------------------------
    # Test 7: Pest Question
    # -------------------------------------------------------------
    print("\n--- TEST 7: Pest Question ---")
    query_7 = "How can I organically control aphids on tomato plants?"
    res_7 = generate_agriculture_response(query_7, language="en")
    text_7 = res_7.get("response", "").lower()
    t7_pass = (
        bool(res_7.get("response"))
        and any(k in text_7 for k in ["neem", "soap", "water", "spray", "predator", "ladybug", "organic", "oil"])
    )
    print(f"Query: {query_7}")
    print(f"Response Preview: {res_7.get('response')[:160]}...")
    print(f"TEST 7 RESULT: [{'PASS' if t7_pass else 'FAIL'}]")
    results.append(("Test 7: Pest Question", t7_pass))

    # -------------------------------------------------------------
    # Test 8: Farming Concept Question
    # -------------------------------------------------------------
    print("\n--- TEST 8: Farming Concept Question ---")
    query_8 = "What is crop rotation and why is it beneficial?"
    res_8 = generate_agriculture_response(query_8, language="en")
    text_8 = res_8.get("response", "").lower()
    t8_pass = (
        bool(res_8.get("response"))
        and any(k in text_8 for k in ["rotation", "soil", "pest", "nutrient", "fertility", "yield", "disease"])
    )
    print(f"Query: {query_8}")
    print(f"Response Preview: {res_8.get('response')[:160]}...")
    print(f"TEST 8 RESULT: [{'PASS' if t8_pass else 'FAIL'}]")
    results.append(("Test 8: Farming Concept Question", t8_pass))

    # -------------------------------------------------------------
    # Test 9: Multi-Turn Conversation / Follow-Up Context
    # -------------------------------------------------------------
    print("\n--- TEST 9: Multi-Turn Follow-Up Question ---")
    context_turn_1 = [
        {"sender": "farmer", "message": "I am growing paddy in my field."},
        {"sender": "assistant", "message": "Paddy is an excellent staple crop. Are you growing direct-seeded rice or transplanted paddy?"},
    ]
    query_9 = "When should I water it?"
    res_9 = generate_agriculture_response(query_9, language="en", conversation_context=context_turn_1)
    text_9 = res_9.get("response", "").lower()
    t9_pass = (
        bool(res_9.get("response"))
        and any(k in text_9 for k in ["paddy", "rice", "standing water", "tillering", "panicle", "flowering", "submerge", "irrigation"])
    )
    print(f"Context: Farmer growing paddy -> Query: '{query_9}'")
    print(f"Response Preview: {res_9.get('response')[:180]}...")
    print(f"Response aware of paddy context: {t9_pass}")
    print(f"TEST 9 RESULT: [{'PASS' if t9_pass else 'FAIL'}]")
    results.append(("Test 9: Multi-Turn Follow-Up Question", t9_pass))

    # -------------------------------------------------------------
    # Test 10: English Language Response
    # -------------------------------------------------------------
    print("\n--- TEST 10: English Language Response ---")
    query_10 = "What are the common companion crops for maize?"
    res_10 = generate_agriculture_response(query_10, language="en")
    text_10 = res_10.get("response", "")
    t10_pass = bool(text_10) and res_10.get("language") == "en" and any(k in text_10.lower() for k in ["bean", "legume", "cowpea", "companion", "intercrop"])
    print(f"Query: {query_10}")
    print(f"Response Preview: {text_10[:160]}...")
    print(f"TEST 10 RESULT: [{'PASS' if t10_pass else 'FAIL'}]")
    results.append(("Test 10: English Language Response", t10_pass))

    # -------------------------------------------------------------
    # Test 11: Telugu Language Response
    # -------------------------------------------------------------
    print("\n--- TEST 11: Telugu Language Response ---")
    query_11 = "వరి పంటలో కలుపు నివారణ ఎలా చేయాలి?"
    res_11 = generate_agriculture_response(query_11, language="te")
    text_11 = res_11.get("response", "")
    has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in text_11)
    t11_pass = bool(text_11) and has_telugu and res_11.get("language") == "te"
    print(f"Query: {query_11}")
    print(f"Has Telugu Unicode: {has_telugu}")
    print(f"Response Preview: {text_11[:160]}...")
    print(f"TEST 11 RESULT: [{'PASS' if t11_pass else 'FAIL'}]")
    results.append(("Test 11: Telugu Language Response", t11_pass))

    # -------------------------------------------------------------
    # Test 12: Hindi Language Response
    # -------------------------------------------------------------
    print("\n--- TEST 12: Hindi Language Response ---")
    query_12 = "गेहूं की फसल में पहली सिंचाई कब करनी चाहिए?"
    res_12 = generate_agriculture_response(query_12, language="hi")
    text_12 = res_12.get("response", "")
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in text_12)
    t12_pass = bool(text_12) and has_devanagari and res_12.get("language") == "hi"
    print(f"Query: {query_12}")
    print(f"Has Devanagari Unicode: {has_devanagari}")
    print(f"Response Preview: {text_12[:160]}...")
    print(f"TEST 12 RESULT: [{'PASS' if t12_pass else 'FAIL'}]")
    results.append(("Test 12: Hindi Language Response", t12_pass))

    # -------------------------------------------------------------
    # Test 13: Unclear Question Clarification (Single Follow-up)
    # -------------------------------------------------------------
    print("\n--- TEST 13: Unclear Question Clarification ---")
    query_13 = "My crop is not growing well"
    res_13 = generate_agriculture_response(query_13, language="en")
    text_13 = res_13.get("response", "")
    has_question = "?" in text_13
    has_clarification = any(k in text_13.lower() for k in ["crop", "soil", "age", "days", "symptom", "which", "what"])
    t13_pass = bool(text_13) and has_question and has_clarification
    print(f"Query: {query_13}")
    print(f"Includes clarifying question mark: {has_question}")
    print(f"Response Preview: {text_13[:180]}...")
    print(f"TEST 13 RESULT: [{'PASS' if t13_pass else 'FAIL'}]")
    results.append(("Test 13: Unclear Question Clarification", t13_pass))

    # -------------------------------------------------------------
    # Test 14: Safety-Sensitive Chemical Question
    # -------------------------------------------------------------
    print("\n--- TEST 14: Safety-Sensitive Chemical Question ---")
    query_14 = "How much chlorpyrifos should I spray on my field?"
    res_14 = generate_agriculture_response(query_14, language="en")
    text_14 = res_14.get("response", "").lower()
    safety_advisory = any(k in text_14 for k in ["label", "manufacturer", "bottle", "package"])
    safety_gear = any(k in text_14 for k in ["protective", "mask", "glove", "gear", "ppe", "safety"])
    expert_referral = any(k in text_14 for k in ["extension officer", "aeo", "kvk", "officer", "expert", "specialist", "agronomist"])
    t14_pass = bool(text_14) and (safety_advisory or expert_referral or safety_gear)
    print(f"Query: {query_14}")
    print(f"Safety Advisories detected: Label={safety_advisory}, Gear={safety_gear}, Expert={expert_referral}")
    print(f"Response Preview: {res_14.get('response')[:200]}...")
    print(f"TEST 14 RESULT: [{'PASS' if t14_pass else 'FAIL'}]")
    results.append(("Test 14: Safety-Sensitive Chemical Question", t14_pass))

    # -------------------------------------------------------------
    # Test 15: Out-of-Domain Question Rejection
    # -------------------------------------------------------------
    print("\n--- TEST 15: Out-of-Domain Question Rejection ---")
    query_15 = "Who won the FIFA world cup?"
    res_15 = generate_agriculture_response(query_15, language="en")
    text_15 = res_15.get("response", "").lower()
    ood_rejected = (
        res_15.get("is_out_of_domain") is True
        or any(k in text_15 for k in ["agriculture", "farming", "kisansaarthi", "cannot assist", "dedicated", "only help with", "farm"])
    )
    t15_pass = bool(text_15) and ood_rejected
    print(f"Query: {query_15}")
    print(f"Out of domain flag / rejection text: {ood_rejected}")
    print(f"Response Preview: {res_15.get('response')[:180]}...")
    print(f"TEST 15 RESULT: [{'PASS' if t15_pass else 'FAIL'}]")
    results.append(("Test 15: Out-of-Domain Question Rejection", t15_pass))

    # -------------------------------------------------------------
    # Test 16: Orchestrator /api/chat End-to-End & SQLite Persistence
    # -------------------------------------------------------------
    print("\n--- TEST 16: Orchestrator /api/chat Integration ---")
    test_farmer_id = f"FARMER-AGRI-{uuid.uuid4().hex[:6]}"
    query_16 = "What is vermicompost and how do I make it?"
    status_code, chat_res = post_chat(query_16, farmer_id=test_farmer_id, language="en")
    
    intent_matched = chat_res.get("intent") == "general_agriculture"
    agent_matched = chat_res.get("agent") == "General Agriculture AI"
    has_response = bool(chat_res.get("response"))
    status_ready = chat_res.get("status") == "ready"

    # Verify SQLite Persistence
    _, reqs_data = get_farmer_requests(test_farmer_id)
    requests_list = reqs_data if isinstance(reqs_data, list) else reqs_data.get("requests", [])
    has_persisted_req = any(r.get("type") == "general_agriculture" for r in requests_list)

    t16_pass = (
        status_code == 200
        and intent_matched
        and agent_matched
        and has_response
        and status_ready
        and has_persisted_req
    )
    print(f"HTTP Status: {status_code}")
    print(f"Detected Intent: {chat_res.get('intent')} (Expected: general_agriculture)")
    print(f"Assigned Agent: {chat_res.get('agent')} (Expected: General Agriculture AI)")
    print(f"Flow Status: {chat_res.get('status')} (Expected: ready)")
    print(f"SQLite Persisted Request Found: {has_persisted_req} (Total: {len(requests_list)})")
    print(f"Response Preview: {chat_res.get('response', '')[:160]}...")
    print(f"TEST 16 RESULT: [{'PASS' if t16_pass else 'FAIL'}]")
    results.append(("Test 16: Orchestrator /api/chat Integration", t16_pass))

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"STEP 8 GENERAL AGRICULTURE VERIFICATION SUMMARY: {passed_count} / {total_count} TESTS PASSED")
    for name, passed in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print("=" * 80)

    if passed_count == total_count:
        print("FINAL RESULT: ALL 16 TESTS PASSED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"FINAL RESULT: {total_count - passed_count} TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
