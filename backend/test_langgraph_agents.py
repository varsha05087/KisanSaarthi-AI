"""
End-to-End Validation Suite for KisanSaarthi LangGraph Multi-Agent Architecture (Phase 3).
Verifies specialized agent nodes execution, supervisor conditional routing,
multilingual execution, multi-turn continuation, and SQLite integration.
"""

import os
import sys
import unittest

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from graph.state import KisanSaarthiState
from graph.workflow import build_kisansaarthi_graph, get_kisansaarthi_graph, reset_kisansaarthi_graph
from agents.tractor import TractorAgent
from agents.insurance import InsuranceAgent


class TestLangGraphAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_kisansaarthi_graph()
        cls.graph = get_kisansaarthi_graph()

    def test_01_crop_health_execution(self):
        """TEST 1: Crop Health query routes to AND executes crop_health_node."""
        state: KisanSaarthiState = {
            "farmer_id": "farmer_crop_test",
            "conversation_id": "conv_crop_1",
            "language": "en",
            "user_message": "My paddy leaves have yellow spots and blight",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "crop_health")
        self.assertEqual(result["detected_intent"], "crop_health")
        self.assertIn("response_text", result)
        self.assertTrue(len(result["response_text"]) > 0)
        self.assertIn(result["status"], ["needs_image", "completed", "ready"])

    def test_02_tractor_execution(self):
        """TEST 2: Tractor query routes to AND executes tractor_node returning options."""
        TractorAgent.clear_session_state("farmer_trac_exec", conversation_id="conv_trac_exec")
        state: KisanSaarthiState = {
            "farmer_id": "farmer_trac_exec",
            "conversation_id": "conv_trac_exec",
            "language": "en",
            "user_message": "Need a tractor tomorrow in Miryalaguda",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "tractor")
        self.assertEqual(result["detected_intent"], "tractor_booking")
        self.assertTrue(result.get("options") and len(result["options"]) > 0)
        self.assertIn("Miryalaguda", result["response_text"])

    def test_03_insurance_execution(self):
        """TEST 3: Insurance query routes to AND executes insurance_node."""
        InsuranceAgent.reset_session("farmer_ins_exec")
        state: KisanSaarthiState = {
            "farmer_id": "farmer_ins_exec",
            "conversation_id": "conv_ins_exec",
            "language": "en",
            "user_message": "Heavy rain damaged my cotton crop in Guntur",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "insurance")
        self.assertEqual(result["detected_intent"], "insurance")
        self.assertIsNotNone(result.get("next_question"))
        self.assertTrue(len(result["response_text"]) > 0)

    def test_04_general_agri_execution(self):
        """TEST 4: Open agriculture query routes to AND executes general_agri_node."""
        state: KisanSaarthiState = {
            "farmer_id": "farmer_gen_exec",
            "conversation_id": "conv_gen_exec",
            "language": "en",
            "user_message": "When should I sow paddy in Kharif season?",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "general_agriculture")
        self.assertEqual(result["detected_intent"], "general_agriculture")
        self.assertTrue(len(result.get("response_text", "")) > 10)

    def test_05_crop_residue_execution(self):
        """TEST 5: Stubble management query routes to AND executes crop_residue_node."""
        state: KisanSaarthiState = {
            "farmer_id": "farmer_res_exec",
            "conversation_id": "conv_res_exec",
            "language": "en",
            "user_message": "I have paddy straw, what should I do with it?",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "crop_residue")
        self.assertEqual(result["detected_intent"], "crop_residue")
        self.assertIn("AgriCycle", result["response_text"])
        self.assertTrue("Biomass" in result["response_text"] or "compost" in result["response_text"].lower())

    def test_06_telugu_routing_and_execution(self):
        """TEST 6: Telugu input correctly routes and executes with localized response."""
        TractorAgent.clear_session_state("farmer_te_exec", conversation_id="conv_te_exec")
        state: KisanSaarthiState = {
            "farmer_id": "farmer_te_exec",
            "conversation_id": "conv_te_exec",
            "language": "te",
            "user_message": "ట్రాక్టర్ కావాలి",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "tractor")
        self.assertIn("మీకు ట్రాక్టర్", result["response_text"])

        # Telugu residue query
        res_state: KisanSaarthiState = {
            "farmer_id": "farmer_te_exec",
            "conversation_id": "conv_te_res",
            "language": "te",
            "user_message": "వరి గడ్డి ఉంది ఏం చేయాలి?",
        }
        res_result = self.graph.invoke(res_state)
        self.assertEqual(res_result["active_agent"], "crop_residue")
        self.assertIn("వ్యవసాయ వ్యర్థాల", res_result["response_text"])

    def test_07_hindi_routing_and_execution(self):
        """TEST 7: Hindi input correctly routes and executes with localized response."""
        TractorAgent.clear_session_state("farmer_hi_exec", conversation_id="conv_hi_exec")
        state: KisanSaarthiState = {
            "farmer_id": "farmer_hi_exec",
            "conversation_id": "conv_hi_exec",
            "language": "hi",
            "user_message": "ट्रैक्टर चाहिए",
        }
        result = self.graph.invoke(state)
        self.assertEqual(result["active_agent"], "tractor")
        self.assertIn("ट्रैक्टर", result["response_text"])

        # Hindi residue query
        res_state: KisanSaarthiState = {
            "farmer_id": "farmer_hi_exec",
            "conversation_id": "conv_hi_res",
            "language": "hi",
            "user_message": "पराली का क्या करें?",
        }
        res_result = self.graph.invoke(res_state)
        self.assertEqual(res_result["active_agent"], "crop_residue")
        self.assertIn("अपशिष्ट", res_result["response_text"])

    def test_08_graph_compilation_and_nodes(self):
        """TEST 8: Graph compiles and all 7 nodes exist in workflow graph."""
        graph = build_kisansaarthi_graph()
        self.assertIsNotNone(graph)
        node_keys = graph.nodes.keys()
        expected_nodes = [
            "supervisor",
            "crop_health_node",
            "tractor_node",
            "insurance_node",
            "general_agri_node",
            "crop_residue_node",
            "post_processor",
        ]
        for node in expected_nodes:
            self.assertIn(node, node_keys, f"Missing node in compiled graph: {node}")

    def test_09_tractor_multi_turn_continuation(self):
        """TEST 9: Complete 5-turn Tractor Booking workflow executed through LangGraph."""
        fid = "farmer_tractor_multiturn"
        cid = "conv_tractor_multiturn"
        TractorAgent.clear_session_state(fid, conversation_id=cid)

        # Turn 1: Farmer requests tractor
        t1 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "I need a tractor",
        })
        self.assertEqual(t1["active_agent"], "tractor")
        self.assertEqual(t1["status"], "needs_information")
        self.assertIn("village or field", t1["next_question"])

        # Turn 2: Farmer provides location only
        t2 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Peddapuram",
        })
        self.assertEqual(t2["active_agent"], "tractor")
        self.assertEqual(t2["status"], "needs_information")
        self.assertIn("When do you need the tractor?", t2["next_question"])

        # Turn 3: Farmer provides date/time
        t3 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Tomorrow at 2:30 PM",
        })
        self.assertEqual(t3["active_agent"], "tractor")
        self.assertTrue(t3.get("options") and len(t3["options"]) > 0)
        self.assertIn("Peddapuram", t3["response_text"])

        # Turn 4: Farmer selects Option 1
        t4 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Option 1",
        })
        self.assertEqual(t4["active_agent"], "tractor")
        self.assertIsNotNone(t4.get("confirmation_details"))
        self.assertIn("CONFIRM YOUR BOOKING", t4["response_text"])

        # Turn 5: Farmer confirms booking
        t5 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Yes, confirm booking",
        })
        self.assertEqual(t5["active_agent"], "tractor")
        self.assertIsNotNone(t5.get("booking"))
        self.assertTrue((t5.get("booking") or {}).get("booking_id", "").startswith("KS-"))

    def test_10_insurance_multi_turn_continuation(self):
        """TEST 10: Multi-turn Insurance interview preserved across turns through LangGraph."""
        import uuid
        fid = f"farmer_ins_{uuid.uuid4().hex[:6]}"
        cid = f"conv_ins_{uuid.uuid4().hex[:6]}"
        InsuranceAgent.reset_session(fid)

        # Turn 1: Farmer reports peril
        t1 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Heavy rain damaged my paddy.",
        })
        self.assertEqual(t1["active_agent"], "insurance")
        self.assertIn("location", t1.get("missing_information", []))
        self.assertIn("village did the damage occur", t1.get("next_question", "").lower())

        # Turn 2: Farmer provides location
        t2 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Guntur",
        })
        self.assertEqual(t2["active_agent"], "insurance")
        self.assertIn("damage_date", t2.get("missing_information", []))
        self.assertIn("when did the damage happen", t2.get("next_question", "").lower())

        # Turn 3: Farmer provides date
        t3 = self.graph.invoke({
            "farmer_id": fid,
            "conversation_id": cid,
            "language": "en",
            "user_message": "Yesterday",
        })
        self.assertEqual(t3["active_agent"], "insurance")
        self.assertIn("damage_extent", t3.get("missing_information", []))
        self.assertIn("how much of the crop was affected", t3.get("next_question", "").lower())


if __name__ == "__main__":
    unittest.main()
