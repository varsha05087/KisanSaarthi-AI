import json
import sys
import urllib.request
import uuid

# Ensure UTF-8 stdout encoding for Telugu and Unicode characters on Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000/api"


def post_chat(message: str, farmer_id: str = "F001", language: str = "te", conversation_id: str = "test-conv"):
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
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def get_farmer_requests(farmer_id: str):
    """Retrieves all requests for the farmer from SQLite."""
    req = urllib.request.Request(f"{BASE_URL}/requests?farmer_id={farmer_id}", method="GET")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_e2e_tests():
    print("=" * 60)
    print("KISANSAARTHI ORCHESTRATOR — END-TO-END VERIFICATION")
    print("=" * 60)

    test_queries = [
        {
            "query": "నా పత్తి ఆకులు పసుపుగా మారుతున్నాయి",
            "lang": "te",
            "expected_intent": "crop_health",
            "expected_agent": "Crop Health Agent",
            "desc": "Telugu crop disease / yellow leaves query",
        },
        {
            "query": "I want to verify whether this fertilizer is genuine",
            "lang": "en",
            "expected_intent": "input_verification",
            "expected_agent": "Input Verification Agent",
            "desc": "Agricultural input / fertilizer authenticity check",
        },
        {
            "query": "నాకు ట్రాక్టర్ కావాలి",
            "lang": "te",
            "expected_intent": "tractor_booking",
            "expected_agent": "Tractor Booking Agent",
            "expected_status": "needs_information",
            "desc": "Telugu tractor booking without dates (missing info trigger)",
        },
        {
            "query": "How can I apply for crop insurance?",
            "lang": "en",
            "expected_intent": "insurance_assistance",
            "expected_agent": "Insurance Assistance Agent",
            "desc": "Crop insurance PMFBY guidance",
        },
        {
            "query": "What can I do with my agricultural waste?",
            "lang": "en",
            "expected_intent": "agricycle",
            "expected_agent": "AgriCycle Waste Agent",
            "desc": "AgriCycle crop residue & biomass utilization",
        },
        {
            "query": "I have a crop problem and also need a tractor tomorrow",
            "lang": "en",
            "expected_intent": "multi_intent",
            "expected_status": "multi_task",
            "desc": "Multi-intent query (Crop Health + Tractor)",
        },
        {
            "query": "I don't know what to do",
            "lang": "en",
            "expected_intent": "unknown",
            "expected_status": "needs_clarification",
            "desc": "Unclear input safe fallback",
        },
    ]

    all_passed = True

    for idx, tc in enumerate(test_queries, 1):
        q = tc["query"]
        status, res = post_chat(q, farmer_id="FARMER-TEST", language=tc["lang"])

        intent = res.get("intent")
        agent = res.get("agent")
        res_status = res.get("status")
        response_text = res.get("response", "")

        intent_match = (intent == tc["expected_intent"])
        status_match = ("expected_status" not in tc) or (res_status == tc["expected_status"])
        agent_match = ("expected_agent" not in tc) or (agent == tc["expected_agent"])

        passed = (status == 200) and intent_match and status_match and agent_match
        if not passed:
            all_passed = False

        status_str = "PASS" if passed else "FAIL"
        print(f"\n[{status_str}] Test {idx}: \"{q}\"")
        print(f"       Intent: {intent} (Expected: {tc['expected_intent']})")
        print(f"       Agent:  {agent}")
        print(f"       Status: {res_status}")
        preview_text = response_text.replace("\n", " ")[:110]
        print(f"       Output: {preview_text}...")

    # Multi-turn Context Continuity Test
    print("\n" + "-" * 60)
    print("Testing Multi-Turn Context Continuity:")
    conv_id = f"conv-seq-{uuid.uuid4().hex[:6]}"
    
    # Turn 1
    t1_status, t1_res = post_chat("నాకు ట్రాక్టర్ కావాలి", farmer_id="FARMER-CONTEXT", language="te", conversation_id=conv_id)
    print(f"  Turn 1 Farmer: \"నాకు ట్రాక్టర్ కావాలి\"")
    print(f"  Turn 1 Assistant: \"{t1_res.get('next_question')}\" (Status: {t1_res.get('status')})")

    # Turn 2: Farmer replies to the follow-up question
    t2_status, t2_res = post_chat("రేపు ఉదయం మిర్యాలగూడలో", farmer_id="FARMER-CONTEXT", language="te", conversation_id=conv_id)
    print(f"  Turn 2 Farmer: \"రేపు ఉదయం మిర్యాలగూడలో\"")
    print(f"  Turn 2 Assistant: {t2_res.get('agent')} -> Status: {t2_res.get('status')} | Intent: {t2_res.get('intent')}")
    preview_t2 = t2_res.get('response', '').replace('\n', ' ')[:100]
    print(f"  Turn 2 Output: {preview_t2}...")

    multiturn_passed = (t1_res.get("status") == "needs_information") and (t2_res.get("intent") == "tractor_booking") and (t2_res.get("status") == "ready")
    if not multiturn_passed:
        all_passed = False
    print(f"  Multi-turn Context Maintained: {'[PASS]' if multiturn_passed else '[FAIL]'}")

    # Test SQLite persistence of requests
    req_status, requests_list = get_farmer_requests("FARMER-TEST")
    print("\n" + "-" * 60)
    print(f"SQLite Persistence Check: Found {len(requests_list)} stored requests for FARMER-TEST (HTTP {req_status})")
    for r in requests_list[:4]:
        print(f"  • Request ID: {r['id']} | Type: {r['type']} | Status: {r['status']}")

    print("=" * 60)
    print(f"FINAL RESULT: {'ALL TESTS PASSED SUCCESSFULLY' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    run_e2e_tests()
