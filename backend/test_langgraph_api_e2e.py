"""
End-to-End API Integration Suite for KisanSaarthi LangGraph Architecture (Phase 4).
Tests the real POST /api/chat endpoint against the FastAPI application,
proving execution travels through LangGraph, supervisor, specialized agent nodes,
and returns the valid OrchestratorResponse contract across multi-turn sessions.
"""

import os
import sys
import uuid
import unittest
from unittest.mock import patch

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app
from agents.tractor import TractorAgent
from agents.insurance import InsuranceAgent
from graph.workflow import get_kisansaarthi_graph


class TestLangGraphApiE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_tractor_5_turn_api_flow(self):
        """TEST 1: Complete 5-turn Tractor Booking flow via POST /api/chat."""
        fid = f"api_farmer_trac_{uuid.uuid4().hex[:6]}"
        cid = f"api_conv_trac_{uuid.uuid4().hex[:6]}"
        TractorAgent.clear_session_state(fid, conversation_id=cid)

        # Turn 1: Farmer requests tractor
        r1 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "I need a tractor",
        })
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["intent"], "tractor_booking")
        self.assertEqual(d1["status"], "needs_information")
        self.assertEqual(d1["agent"], "Tractor Booking Agent")
        self.assertIn("Which village or field do you need the tractor in?", d1["next_question"])

        # Turn 2: Farmer gives location
        r2 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Peddapuram",
        })
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["intent"], "tractor_booking")
        self.assertEqual(d2["status"], "needs_information")
        self.assertIn("When do you need the tractor?", d2["next_question"])

        # Turn 3: Farmer gives date & time
        r3 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Tomorrow at 2:30 PM",
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["intent"], "tractor_booking")
        self.assertEqual(d3["status"], "ready")
        self.assertTrue(d3.get("options") and len(d3["options"]) > 0)
        self.assertIn("Peddapuram", d3["response"])

        # Turn 4: Farmer selects Option 1
        r4 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Option 1",
        })
        self.assertEqual(r4.status_code, 200)
        d4 = r4.json()
        self.assertEqual(d4["status"], "ready")
        self.assertIsNotNone(d4.get("confirmation_details"))
        self.assertIn("CONFIRM YOUR BOOKING", d4["response"])

        # Turn 5: Farmer confirms booking
        r5 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Yes, confirm booking",
        })
        self.assertEqual(r5.status_code, 200)
        d5 = r5.json()
        self.assertEqual(d5["status"], "ready")
        self.assertIsNotNone(d5.get("booking"))
        self.assertTrue(d5["booking"]["booking_id"].startswith("KS-"))

    def test_02_general_agriculture_api(self):
        """TEST 2: General Agriculture queries in English, Telugu, and Hindi via POST /api/chat."""
        # English
        r_en = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_gen",
            "conversation_id": "api_conv_gen_en",
            "language": "en",
            "message": "When should I sow paddy in Kharif season?",
        })
        self.assertEqual(r_en.status_code, 200)
        d_en = r_en.json()
        self.assertEqual(d_en["intent"], "general_agriculture")
        self.assertEqual(d_en["agent"], "General Agriculture AI")
        self.assertTrue(len(d_en["response"]) > 20)

        # Telugu
        r_te = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_gen",
            "conversation_id": "api_conv_gen_te",
            "language": "te",
            "message": "వరిని ఎప్పుడు విత్తాలి?",
        })
        self.assertEqual(r_te.status_code, 200)
        d_te = r_te.json()
        self.assertEqual(d_te["intent"], "general_agriculture")
        self.assertTrue(any('\u0c00' <= ch <= '\u0c7f' for ch in d_te["response"]))

        # Hindi
        r_hi = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_gen",
            "conversation_id": "api_conv_gen_hi",
            "language": "hi",
            "message": "धान की बुवाई कब करें?",
        })
        self.assertEqual(r_hi.status_code, 200)
        d_hi = r_hi.json()
        self.assertEqual(d_hi["intent"], "general_agriculture")
        self.assertTrue(any('\u0900' <= ch <= '\u097f' for ch in d_hi["response"]))

    def test_03_insurance_multi_turn_api(self):
        """TEST 3: Multi-turn Insurance guided interview via POST /api/chat."""
        fid = f"api_farmer_ins_{uuid.uuid4().hex[:6]}"
        cid = f"api_conv_ins_{uuid.uuid4().hex[:6]}"
        InsuranceAgent.reset_session(fid)

        # Turn 1
        r1 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Heavy rain damaged my paddy.",
        })
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["intent"], "insurance_assistance")
        self.assertEqual(d1["status"], "information_collection")
        self.assertIn("location", d1.get("missing_information", []))
        self.assertIn("village did the damage occur", d1.get("next_question", "").lower())

        # Turn 2
        r2 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Guntur",
        })
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["intent"], "insurance_assistance")
        self.assertIn("damage_date", d2.get("missing_information", []))
        self.assertIn("when did the damage happen", d2.get("next_question", "").lower())

        # Turn 3
        r3 = self.client.post("/api/chat", json={
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "message": "Yesterday",
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["intent"], "insurance_assistance")
        self.assertIn("damage_extent", d3.get("missing_information", []))
        self.assertIn("how much of the crop was affected", d3.get("next_question", "").lower())

    def test_04_crop_residue_api(self):
        """TEST 4: Crop residue queries via POST /api/chat in English, Telugu, and Hindi."""
        # English
        r_en = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_res",
            "conversation_id": "api_conv_res_en",
            "language": "en",
            "message": "I have a lot of paddy straw. What can I do?",
        })
        self.assertEqual(r_en.status_code, 200)
        d_en = r_en.json()
        self.assertEqual(d_en["intent"], "agricycle")
        self.assertEqual(d_en["agent"], "AgriCycle Waste Agent")
        self.assertIn("AgriCycle", d_en["response"])

        # Telugu
        r_te = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_res",
            "conversation_id": "api_conv_res_te",
            "language": "te",
            "message": "వరి గడ్డి ఉంది ఏం చేయాలి?",
        })
        self.assertEqual(r_te.status_code, 200)
        d_te = r_te.json()
        self.assertEqual(d_te["intent"], "agricycle")
        self.assertIn("వ్యవసాయ వ్యర్థాల", d_te["response"])

        # Hindi
        r_hi = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_res",
            "conversation_id": "api_conv_res_hi",
            "language": "hi",
            "message": "पराली का क्या करें?",
        })
        self.assertEqual(r_hi.status_code, 200)
        d_hi = r_hi.json()
        self.assertEqual(d_hi["intent"], "agricycle")
        self.assertIn("अपशिष्ट", d_hi["response"])

    def test_05_crop_health_chat_api(self):
        """TEST 5: Crop health leaf inquiry without photo via POST /api/chat prompts for image."""
        r = self.client.post("/api/chat", json={
            "farmer_id": "api_farmer_crop",
            "conversation_id": "api_conv_crop",
            "language": "en",
            "message": "My paddy leaves have yellow spots and blight",
        })
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["intent"], "crop_health")
        self.assertEqual(d["agent"], "Crop Health Agent")
        self.assertEqual(d["status"], "needs_image")
        self.assertIn("photo", d["response"].lower())

    def test_06_prove_langgraph_invocation(self):
        """TEST 6: Proves compiled LangGraph workflow is strictly invoked by POST /api/chat."""
        graph = get_kisansaarthi_graph()
        original_invoke = graph.invoke
        call_count = {"count": 0}

        def mock_invoke(state, *args, **kwargs):
            call_count["count"] += 1
            return original_invoke(state, *args, **kwargs)

        with patch.object(graph, "invoke", side_effect=mock_invoke):
            r = self.client.post("/api/chat", json={
                "farmer_id": "api_proof_farmer",
                "conversation_id": "api_proof_conv",
                "language": "en",
                "message": "I need a tractor",
            })
            self.assertEqual(r.status_code, 200)
            self.assertEqual(call_count["count"], 1, "Expected LangGraph graph.invoke to be called exactly once")


if __name__ == "__main__":
    unittest.main()
