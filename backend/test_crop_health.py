"""
End-to-End Verification Test Suite for Step 5C — Real Multi-Crop Disease Detection Layer.

16 MANDATORY STEP 5C TESTS:
1.  Tomato healthy image (real model recognizes healthy tomato foliage)
2.  Tomato Early Blight image (real model recognizes Early Blight)
3.  Corn Common Rust image (real model recognizes Common Rust)
4.  Corn healthy image (real model recognizes Healthy Corn)
5.  Blurry image (detects blur, returns needs_better_image or uncertain, confidence < 0.60)
6.  Non-plant image (detects non-plant object, returns invalid_image or uncertain, crop=None)
7.  Unsupported crop (detects crop outside model, lists supported crops)
8.  Knowledge base match (returns knowledge_found=True, safe steps, prevention, expert contact)
9.  Knowledge base missing (returns knowledge_found=False, fallback to AEO/KVK expert)
10. English response formatting (sections: Crop, Possible problem, Confidence, Symptoms, Safe steps)
11. Telugu response formatting (Telugu script Unicode, localized sections)
12. Hindi response formatting (Hindi script Unicode, localized sections)
13. API endpoint /api/crop/health multipart upload & schema conformance
14. /api/chat crop intent routing (Orchestrator routes to Crop Health Agent, prompts for image)
15. Tractor booking flow regression (Orchestrator routes to Tractor Booking Agent)
16. SQLite database persistence (requests durably stored and retrievable via /api/requests)
"""

import json
import os
import sys
import urllib.request
import uuid

# Reconfigure stdout for UTF-8 / Telugu / Hindi printing on Windows consoles
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000/api"
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "data", "samples")


def make_multipart_payload(fields: dict, filename: str = None, file_bytes: bytes = None):
    """Builds standard multipart/form-data payload."""
    boundary = f"----WebKitBoundary{uuid.uuid4().hex}"
    body = bytearray()

    for k, v in fields.items():
        if v is not None:
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
            body.extend(f"{v}\r\n".encode("utf-8"))

    if file_bytes is not None and filename is not None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode("utf-8"))
        content_type = "image/png" if filename.endswith(".png") else "image/jpeg"
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(file_bytes)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return boundary, bytes(body)


def post_crop_health(fields: dict, filename: str = None, file_bytes: bytes = None):
    boundary, data = make_multipart_payload(fields, filename, file_bytes)
    req = urllib.request.Request(
        f"{BASE_URL}/crop/health",
        data=data,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def post_chat(message: str, farmer_id: str = "F001", language: str = "te"):
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps({
            "farmer_id": farmer_id,
            "message": message,
            "language": language,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def get_farmer_requests(farmer_id: str):
    req = urllib.request.Request(f"{BASE_URL}/requests?farmer_id={farmer_id}", method="GET")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_all_tests():
    print("=" * 80)
    print("KISANSAARTHI AI — STEP 5C REAL MULTI-CROP DISEASE DETECTION LAYER VERIFICATION")
    print("=" * 80)

    # Read real sample images from disk
    tomato_healthy_path = os.path.join(SAMPLE_DIR, "tomato_healthy.jpg")
    tomato_blight_path = os.path.join(SAMPLE_DIR, "tomato_early_blight.jpg")
    corn_rust_path = os.path.join(SAMPLE_DIR, "corn_common_rust.jpg")
    corn_healthy_path = os.path.join(SAMPLE_DIR, "corn_healthy.jpg")
    blurry_img_path = os.path.join(SAMPLE_DIR, "blurry_leaf.jpg")
    non_crop_img_path = os.path.join(SAMPLE_DIR, "non_crop_object.jpg")
    unsupported_path = os.path.join(SAMPLE_DIR, "unsupported_crop.jpg")
    cotton_path = os.path.join(SAMPLE_DIR, "cotton_yellow_leaf.jpg")

    with open(tomato_healthy_path, "rb") as f:
        tomato_healthy_bytes = f.read()
    with open(tomato_blight_path, "rb") as f:
        tomato_blight_bytes = f.read()
    with open(corn_rust_path, "rb") as f:
        corn_rust_bytes = f.read()
    with open(corn_healthy_path, "rb") as f:
        corn_healthy_bytes = f.read()
    with open(blurry_img_path, "rb") as f:
        blurry_bytes = f.read()
    with open(non_crop_img_path, "rb") as f:
        non_crop_bytes = f.read()
    with open(unsupported_path, "rb") as f:
        unsupported_bytes = f.read()
    with open(cotton_path, "rb") as f:
        cotton_bytes = f.read()

    farmer_id = f"FARMER-5C-{uuid.uuid4().hex[:6]}"
    all_passed = True
    test_results = []

    def record_test(test_num: int, title: str, passed: bool, details: str):
        nonlocal all_passed
        if not passed:
            all_passed = False
        status_tag = "[PASS]" if passed else "[FAIL]"
        test_results.append((test_num, title, passed, details))
        print(f"\n--- TEST {test_num}: {title} ---")
        print(details)
        print(f"TEST {test_num} RESULT: {status_tag}")

    # -----------------------------------------------------------------
    # TEST 1: Tomato Healthy Image Analysis
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Tomato", "language": "en"},
        filename="tomato_healthy.jpg",
        file_bytes=tomato_healthy_bytes,
    )
    prob = res.get("possible_problem") or res.get("possible_issue") or ""
    t1_pass = (
        status == 200
        and res.get("status") == "completed"
        and res.get("crop") == "Tomato"
        and ("Healthy" in prob or "healthy" in prob.lower())
        and (res.get("confidence") or 0.0) >= 0.60
        and len(res.get("visible_symptoms", [])) > 0
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Crop: {res.get('crop')} | Problem: {prob}\n"
        f"Confidence: {res.get('confidence')} | KB Grounded: {res.get('knowledge_found')}"
    )
    record_test(1, "Tomato Healthy Image (Real Model Detection)", t1_pass, details)

    # -----------------------------------------------------------------
    # TEST 2: Tomato Early Blight Image Analysis
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Tomato", "language": "en"},
        filename="tomato_early_blight.jpg",
        file_bytes=tomato_blight_bytes,
    )
    prob = res.get("possible_problem") or res.get("possible_issue") or ""
    t2_pass = (
        status == 200
        and res.get("status") == "completed"
        and res.get("crop") == "Tomato"
        and "Early Blight" in prob
        and (res.get("confidence") or 0.0) >= 0.60
        and len(res.get("visible_symptoms", [])) > 0
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Crop: {res.get('crop')} | Problem: {prob}\n"
        f"Confidence: {res.get('confidence')} | Symptoms: {res.get('visible_symptoms')[:1]}"
    )
    record_test(2, "Tomato Early Blight Image (Real Model Detection)", t2_pass, details)

    # -----------------------------------------------------------------
    # TEST 3: Corn Common Rust Image Analysis
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Corn", "language": "en"},
        filename="corn_common_rust.jpg",
        file_bytes=corn_rust_bytes,
    )
    prob = res.get("possible_problem") or res.get("possible_issue") or ""
    crop = res.get("crop") or ""
    t3_pass = (
        status == 200
        and res.get("status") == "completed"
        and ("Corn" in crop or "Maize" in crop)
        and "Common Rust" in prob
        and (res.get("confidence") or 0.0) >= 0.60
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Crop: {crop} | Problem: {prob}\n"
        f"Confidence: {res.get('confidence')} | KB Grounded: {res.get('knowledge_found')}"
    )
    record_test(3, "Corn Common Rust Image (Real Model Detection)", t3_pass, details)

    # -----------------------------------------------------------------
    # TEST 4: Corn Healthy Image Analysis
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Corn", "language": "en"},
        filename="corn_healthy.jpg",
        file_bytes=corn_healthy_bytes,
    )
    prob = res.get("possible_problem") or res.get("possible_issue") or ""
    crop = res.get("crop") or ""
    t4_pass = (
        status == 200
        and res.get("status") == "completed"
        and ("Corn" in crop or "Maize" in crop)
        and ("Healthy" in prob or "healthy" in prob.lower())
        and (res.get("confidence") or 0.0) >= 0.60
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Crop: {crop} | Problem: {prob}\n"
        f"Confidence: {res.get('confidence')} | KB Grounded: {res.get('knowledge_found')}"
    )
    record_test(4, "Corn Healthy Image (Real Model Detection)", t4_pass, details)

    # -----------------------------------------------------------------
    # TEST 5: Blurry / Poor Quality Image Guard
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "language": "en"},
        filename="blurry_leaf.jpg",
        file_bytes=blurry_bytes,
    )
    conf = res.get("confidence", 1.0)
    t5_pass = (
        status == 200
        and res.get("status") in ["needs_better_image", "uncertain"]
        and (conf is not None and conf < 0.60)
        and res.get("uncertain") is True
        and bool(res.get("next_question"))
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')} (Expected: 'needs_better_image')\n"
        f"Confidence: {conf} (< 0.60) | Uncertain: {res.get('uncertain')}\n"
        f"Next Question Prompt: {res.get('next_question')}"
    )
    record_test(5, "Blurry / Poor Quality Image Guard", t5_pass, details)

    # -----------------------------------------------------------------
    # TEST 6: Non-Plant / Non-Crop Image Guard
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "language": "en"},
        filename="non_crop_object.jpg",
        file_bytes=non_crop_bytes,
    )
    t6_pass = (
        status == 200
        and res.get("status") == "uncertain"
        and res.get("crop") is None
        and res.get("uncertain") is True
        and "not appear to contain a crop" in (res.get("response") or "").lower()
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Crop: {res.get('crop')} (Expected: None) | Uncertain: {res.get('uncertain')}\n"
        f"Warning Response: {res.get('response')[:80]}..."
    )
    record_test(6, "Non-Plant / Non-Crop Image Guard", t6_pass, details)

    # -----------------------------------------------------------------
    # TEST 7: Unsupported Crop Guard
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Dragonfruit", "message": "dragonfruit leaf issue", "language": "en"},
        filename="unsupported_crop.jpg",
        file_bytes=unsupported_bytes,
    )
    resp_text = (res.get("response") or "") + (res.get("warning") or "")
    t7_pass = (
        status == 200
        and res.get("status") in ["unsupported", "uncertain"]
        and res.get("uncertain") is True
        and "Tomato" in resp_text
        and "Corn" in resp_text
    )
    details = (
        f"HTTP Status: {status} | Agent Status: {res.get('status')}\n"
        f"Uncertain: {res.get('uncertain')} | Warning: {res.get('warning')}\n"
        f"Lists Supported Crops: {'Tomato' in resp_text and 'Corn' in resp_text}"
    )
    record_test(7, "Unsupported Crop Guard", t7_pass, details)

    # -----------------------------------------------------------------
    # TEST 8: Knowledge Base Match (Tomato Early Blight)
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Tomato", "language": "en"},
        filename="tomato_early_blight.jpg",
        file_bytes=tomato_blight_bytes,
    )
    t8_pass = (
        status == 200
        and res.get("knowledge_found") is True
        and len(res.get("safe_next_steps", [])) >= 2
        and len(res.get("prevention", [])) >= 2
        and bool(res.get("when_to_contact_expert"))
    )
    details = (
        f"Knowledge Found: {res.get('knowledge_found')}\n"
        f"Safe Next Steps: {len(res.get('safe_next_steps', []))} steps\n"
        f"Prevention: {len(res.get('prevention', []))} points\n"
        f"Expert Advice: {(res.get('when_to_contact_expert') or '')[:70]}..."
    )
    record_test(8, "Knowledge Base Match (Curated ICAR Grounding)", t8_pass, details)

    # -----------------------------------------------------------------
    # TEST 9: Knowledge Base Missing (Unknown/Exotic Condition)
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Dragonfruit", "message": "rare stem necrosis", "language": "en"},
        filename="cotton_yellow_leaf.jpg",
        file_bytes=cotton_bytes,
    )
    expert_trigger = (res.get("when_to_contact_expert") or "").lower()
    t9_pass = (
        status == 200
        and res.get("knowledge_found") is False
        and ("guidelines are unavailable" in expert_trigger or "officer" in expert_trigger or "specialist" in expert_trigger)
    )
    details = (
        f"Knowledge Found: {res.get('knowledge_found')} (Expected: False)\n"
        f"Fallback Expert Advisory: {res.get('when_to_contact_expert')[:75]}..."
    )
    record_test(9, "Knowledge Base Missing Guard & Advisory", t9_pass, details)

    # -----------------------------------------------------------------
    # TEST 10: English Response Formatting
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Tomato", "language": "en"},
        filename="tomato_early_blight.jpg",
        file_bytes=tomato_blight_bytes,
    )
    resp = res.get("response", "")
    t10_pass = (
        status == 200
        and res.get("language") == "en"
        and "🌱 Crop:" in resp
        and "🔎 Possible problem:" in resp
        and "📊 Confidence:" in resp
        and "✅ What you can do now:" in resp
        and "⚠️ Important:" in resp
    )
    details = (
        f"Language: {res.get('language')} | Standardized Sections Present: {t10_pass}\n"
        f"Response Preview: {resp[:120]}..."
    )
    record_test(10, "English Response Formatting", t10_pass, details)

    # -----------------------------------------------------------------
    # TEST 11: Telugu Response Formatting
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "పత్తి", "language": "te"},
        filename="cotton_yellow_leaf.jpg",
        file_bytes=cotton_bytes,
    )
    resp = res.get("response", "")
    has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in resp)
    t11_pass = (
        status == 200
        and res.get("language") == "te"
        and "🌱 పంట:" in resp
        and "🔎 సాధ్యమైన సమస్య:" in resp
        and "📊 ఖచ్చితత్వం:" in resp
        and has_telugu
    )
    details = (
        f"Language: {res.get('language')} | Telugu Script Unicode Detected: {has_telugu}\n"
        f"Telugu Sections Present: {t11_pass}\n"
        f"Response Preview: {resp[:100]}..."
    )
    record_test(11, "Telugu Response Formatting", t11_pass, details)

    # -----------------------------------------------------------------
    # TEST 12: Hindi Response Formatting
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "टमाटर", "language": "hi"},
        filename="tomato_early_blight.jpg",
        file_bytes=tomato_blight_bytes,
    )
    resp = res.get("response", "")
    has_hindi = any("\u0900" <= ch <= "\u097f" for ch in resp)
    t12_pass = (
        status == 200
        and res.get("language") == "hi"
        and "🌱 फसल:" in resp
        and "🔎 संभावित समस्या:" in resp
        and "📊 विश्वसनीयता:" in resp
        and has_hindi
    )
    details = (
        f"Language: {res.get('language')} | Hindi Script Unicode Detected: {has_hindi}\n"
        f"Hindi Sections Present: {t12_pass}\n"
        f"Response Preview: {resp[:100]}..."
    )
    record_test(12, "Hindi Response Formatting", t12_pass, details)

    # -----------------------------------------------------------------
    # TEST 13: /api/crop/health API Endpoint & Schema Conformance
    # -----------------------------------------------------------------
    status, res = post_crop_health(
        {"farmer_id": farmer_id, "crop_name": "Tomato", "language": "en"},
        filename="tomato_early_blight.jpg",
        file_bytes=tomato_blight_bytes,
    )
    required_keys = ["farmer_id", "crop", "possible_problem", "confidence", "uncertain", "visible_symptoms", "knowledge_found", "safe_next_steps", "prevention", "status", "response", "agent"]
    missing_keys = [k for k in required_keys if k not in res]
    t13_pass = (status == 200 and len(missing_keys) == 0 and res.get("agent") == "Crop Health Agent")
    details = (
        f"HTTP Status: {status} | Endpoint: /api/crop/health\n"
        f"Schema Validation: {'All required fields present' if not missing_keys else f'Missing {missing_keys}'}\n"
        f"Agent Name: {res.get('agent')}"
    )
    record_test(13, "/api/crop/health Multipart API & Schema Conformance", t13_pass, details)

    # -----------------------------------------------------------------
    # TEST 14: /api/chat Crop Intent Routing (Needs Image Prompt)
    # -----------------------------------------------------------------
    status, res = post_chat("నా పత్తి ఆకులు పసుపుగా మారుతున్నాయి", farmer_id=farmer_id, language="te")
    t14_pass = (
        status == 200
        and res.get("intent") == "crop_health"
        and res.get("agent") == "Crop Health Agent"
        and res.get("status") == "needs_image"
        and bool(res.get("next_question"))
    )
    details = (
        f"HTTP Status: {status} | Detected Intent: {res.get('intent')}\n"
        f"Routed Agent: {res.get('agent')} | Flow Status: {res.get('status')}\n"
        f"Image Request Prompt: {res.get('next_question')[:80]}..."
    )
    record_test(14, "Orchestrator /api/chat Crop Intent Routing", t14_pass, details)

    # -----------------------------------------------------------------
    # TEST 15: Tractor Booking Regression Check
    # -----------------------------------------------------------------
    status, res = post_chat("I need a tractor tomorrow morning in Miryalaguda", farmer_id=farmer_id, language="en")
    t15_pass = (
        status == 200
        and res.get("intent") == "tractor_booking"
        and res.get("agent") == "Tractor Booking Agent"
        and res.get("status") == "ready"
    )
    details = (
        f"HTTP Status: {status} | Detected Intent: {res.get('intent')}\n"
        f"Routed Agent: {res.get('agent')} | Flow Status: {res.get('status')}\n"
        f"Booking Confirmation Summary: {res.get('response')[:80]}..."
    )
    record_test(15, "Tractor Booking Orchestrator Regression Check", t15_pass, details)

    # -----------------------------------------------------------------
    # TEST 16: SQLite Database Persistence Check
    # -----------------------------------------------------------------
    status, reqs = get_farmer_requests(farmer_id)
    t16_pass = (status == 200 and len(reqs) >= 4)
    details = (
        f"HTTP Status: {status} | Total Persisted Requests for {farmer_id}: {len(reqs)}\n"
        + "\n".join(f"  • ID: {r['id']} | Type: {r['type']} | Status: {r['status']}" for r in reqs[:4])
    )
    record_test(16, "SQLite Database Persistence Across Workflows", t16_pass, details)

    print("\n" + "=" * 80)
    print(f"STEP 5C VERIFICATION SUMMARY: {len([r for r in test_results if r[2]])} / 16 TESTS PASSED")
    print(f"FINAL RESULT: {'ALL 16 TESTS PASSED SUCCESSFULLY' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
