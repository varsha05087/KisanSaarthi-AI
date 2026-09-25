import json
import urllib.request
from services.orchestrator import KisanSaarthiOrchestrator


def post_chat(message: str, farmer_id: str = "F001", language: str = "en"):
    """Sends chat message to POST /api/chat."""
    url = "http://127.0.0.1:8000/api/chat"
    payload = {
        "farmer_id": farmer_id,
        "message": message,
        "language": language,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_tests():
    print("==================================================")
    print("KISANSAARTHI ORCHESTRATOR — STEP 4 VERIFICATION")
    print("==================================================")

    test_cases = [
        {
            "id": 1,
            "message": "I need a tractor tomorrow",
            "expected_intent": "tractor_booking",
            "desc": "Tractor intent with date specified",
        },
        {
            "id": 2,
            "message": "My crop has a disease",
            "expected_intent": "crop_health",
            "desc": "Crop health intent",
        },
        {
            "id": 3,
            "message": "I need insurance help",
            "expected_intent": "insurance_assistance",
            "desc": "Crop insurance assistance intent",
        },
        {
            "id": 4,
            "message": "I need seeds",
            "expected_intent": "seed_assistance",
            "desc": "Seed procurement intent",
        },
        {
            "id": 5,
            "message": "What can you help me with?",
            "expected_intent": "general_help",
            "desc": "General capabilities inquiry",
        },
        {
            "id": 6,
            "message": "I have a crop problem and need a tractor",
            "expected_intent": "multi_intent",
            "desc": "Multiple intents in single message",
        },
        {
            "id": 7,
            "message": "I don't know what to do",
            "expected_intent": "unknown",
            "expected_status": "needs_clarification",
            "desc": "Unclear / ambiguous request",
        },
        {
            "id": 8,
            "message": "I need a tractor",
            "expected_intent": "tractor_booking",
            "expected_status": "needs_information",
            "expected_missing": ["date", "location"],
            "desc": "Missing information trigger",
        },
    ]

    all_passed = True

    for t in test_cases:
        msg = t["message"]
        # Direct service evaluation
        res_direct = KisanSaarthiOrchestrator.process("F001", msg, language="en")

        # API endpoint evaluation
        status_code, res_api = post_chat(msg, farmer_id="F001", language="en")

        intent = res_api.get("intent")
        status = res_api.get("status")
        missing = res_api.get("missing_information", [])
        next_q = res_api.get("next_question")
        tasks = res_api.get("tasks", [])
        agent = res_api.get("agent")

        # Validation checks
        passed = (status_code == 200) and (intent == t["expected_intent"])
        if "expected_status" in t:
            passed = passed and (status == t["expected_status"])
        if "expected_missing" in t:
            passed = passed and (missing == t["expected_missing"])

        if not passed:
            all_passed = False

        status_flag = "PASS" if passed else "FAIL"
        print(f"\n[{status_flag}] Test {t['id']}: \"{msg}\"")
        print(f"       -> Intent: {intent} | Status: {status} | Agent: {agent}")
        if missing:
            print(f"       -> Missing Info: {missing} | Next Question: \"{next_q}\"")
        if t["expected_intent"] == "multi_intent":
            print(f"       -> Sub-tasks generated: {[task['intent'] for task in tasks]}")

    print("\n--------------------------------------------------")
    print(f"ALL 8 ORCHESTRATOR TESTS PASSED: {all_passed}")
    print("--------------------------------------------------")
    return all_passed


if __name__ == "__main__":
    run_tests()
