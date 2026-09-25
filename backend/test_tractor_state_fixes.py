"""
Targeted verification test suite for Tractor Booking state loss fix and date/time robustness.
Covers:
TEST 1: 3-turn flow ("I want a tractor" -> "Peddapuram" -> "Tomorrow at 2:30 PM")
TEST 2: Single-turn ("I want a tractor tomorrow at 2:30 PM in Peddapuram")
TEST 3: Multi-detail phrase ("tomorrow and village name is peddapuram village")
TEST 4: Typo and space-separated time ("I want a tractor" -> "Peddapuram" -> "tommorow at 2 30 pm")
TEST 5: Cross-conversation isolation (Conv A does not bleed Peddapuram into Conv B)
"""

import sys
import uuid
import unittest
from services.orchestrator import KisanSaarthiOrchestrator
from agents.tractor import TractorAgent
from database.connection import SessionLocal

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class TestTractorStateFixes(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.farmer_id = "FARMER-STATE-FIX"
        TractorAgent.clear_session_state(self.farmer_id)

    def tearDown(self):
        TractorAgent.clear_session_state(self.farmer_id)
        self.db.close()

    def test_01_three_turn_standard_flow(self):
        """TEST 1: Standard 3-turn flow preserves location as Peddapuram."""
        conv = f"conv_test_1_{uuid.uuid4().hex[:6]}"
        
        # Turn 1
        r1 = KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv, self.db)
        self.assertEqual(r1.status, "needs_information")
        self.assertEqual(r1.missing_information, ["location"])
        self.assertEqual(r1.next_question, "Which village or field do you need the tractor in?")
        
        # Turn 2
        r2 = KisanSaarthiOrchestrator.process(self.farmer_id, "Peddapuram", "en", conv, self.db)
        self.assertEqual(r2.status, "needs_information")
        self.assertEqual(r2.missing_information, ["date"])
        self.assertEqual(r2.next_question, "When do you need the tractor?")
        
        # Turn 3
        r3 = KisanSaarthiOrchestrator.process(self.farmer_id, "Tomorrow at 2:30 PM", "en", conv, self.db)
        self.assertEqual(r3.status, "ready")
        self.assertIn("Peddapuram", r3.text)
        self.assertIn("GreenField Tractor", r3.text)
        
        state = TractorAgent.get_session_state(self.farmer_id, conv)
        self.assertEqual(state["location"], "Peddapuram")
        self.assertEqual(state["date"], "Tomorrow")
        self.assertEqual(state["specific_time"], "2:30 PM")
        self.assertEqual(state["time_slot"], "2:00 PM – 5:00 PM")
        print("\n[PASS] Test 1: Standard 3-turn flow preserved location Peddapuram and showed options.")

    def test_02_single_turn_full_details(self):
        """TEST 2: 'I want a tractor tomorrow at 2:30 PM in Peddapuram' directly shows options."""
        conv = f"conv_test_2_{uuid.uuid4().hex[:6]}"
        query = "I want a tractor tomorrow at 2:30 PM in Peddapuram"
        r = KisanSaarthiOrchestrator.process(self.farmer_id, query, "en", conv, self.db)
        self.assertEqual(r.status, "ready")
        self.assertIn("Peddapuram", r.text)
        self.assertIn("GreenField Tractor", r.text)
        
        state = TractorAgent.get_session_state(self.farmer_id, conv)
        self.assertEqual(state["location"], "Peddapuram")
        self.assertEqual(state["date"], "Tomorrow")
        self.assertEqual(state["specific_time"], "2:30 PM")
        print("\n[PASS] Test 2: Single-turn full request directly showed tractor options.")

    def test_03_multi_detail_phrase(self):
        """TEST 3: 'tomorrow and village name is peddapuram village' recognizes date and location."""
        # Check extraction functions
        self.assertEqual(TractorAgent.extract_date("tomorrow and village name is peddapuram village"), "Tomorrow")
        self.assertEqual(TractorAgent.extract_location("tomorrow and village name is peddapuram village"), "Peddapuram")

        # Check TractorAgent.execute directly
        res = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="tomorrow and village name is peddapuram village",
            language="en",
            db=self.db,
        )
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["details"]["location"], "Peddapuram")
        self.assertEqual(res["details"]["date"], "Tomorrow")
        self.assertGreaterEqual(len(res["options"]), 1)

        # Check in multi-turn conversation via Orchestrator
        conv = f"conv_test_3_{uuid.uuid4().hex[:6]}"
        KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv, self.db)
        r = KisanSaarthiOrchestrator.process(self.farmer_id, "tomorrow and village name is peddapuram village", "en", conv, self.db)
        self.assertEqual(r.status, "ready")
        self.assertIn("Peddapuram", r.text)
        self.assertIn("GreenField Tractor", r.text)
        print("\n[PASS] Test 3: Multi-detail phrase recognized date and location.")

    def test_04_typo_and_space_time(self):
        """TEST 4: 'tommorow at 2 30 pm' recognized as tomorrow + 2:30 PM, location remains Peddapuram."""
        conv = f"conv_test_4_{uuid.uuid4().hex[:6]}"
        
        # Turn 1
        r1 = KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv, self.db)
        self.assertEqual(r1.status, "needs_information")
        self.assertEqual(r1.missing_information, ["location"])
        
        # Turn 2
        r2 = KisanSaarthiOrchestrator.process(self.farmer_id, "Peddapuram", "en", conv, self.db)
        self.assertEqual(r2.status, "needs_information")
        self.assertEqual(r2.missing_information, ["date"])
        
        # Turn 3 with typo 'tommorow' and space-separated '2 30 pm'
        r3 = KisanSaarthiOrchestrator.process(self.farmer_id, "tommorow at 2 30 pm", "en", conv, self.db)
        self.assertEqual(r3.status, "ready")
        self.assertIn("Peddapuram", r3.text)
        self.assertIn("GreenField Tractor", r3.text)
        
        state = TractorAgent.get_session_state(self.farmer_id, conv)
        self.assertEqual(state["location"], "Peddapuram")
        self.assertEqual(state["date"], "Tomorrow")
        self.assertEqual(state["specific_time"], "2:30 PM")
        self.assertEqual(state["time_slot"], "2:00 PM – 5:00 PM")
        print("\n[PASS] Test 4: Typo 'tommorow' and '2 30 pm' recognized; location remained Peddapuram; options shown.")

    def test_05_cross_conversation_isolation(self):
        """TEST 5: Conv A has Peddapuram. Conv B starts with 'I want a tractor' and must NOT inherit Peddapuram."""
        conv_a = f"conv_test_5_A_{uuid.uuid4().hex[:6]}"
        KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv_a, self.db)
        KisanSaarthiOrchestrator.process(self.farmer_id, "Peddapuram", "en", conv_a, self.db)
        KisanSaarthiOrchestrator.process(self.farmer_id, "Tomorrow", "en", conv_a, self.db)
        
        # Check Conv A has location
        state_a = TractorAgent.get_session_state(self.farmer_id, conv_a)
        self.assertEqual(state_a["location"], "Peddapuram")
        
        # Completely NEW conversation
        conv_b = f"conv_test_5_B_{uuid.uuid4().hex[:6]}"
        r_b = KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv_b, self.db)
        self.assertEqual(r_b.status, "needs_information")
        self.assertEqual(r_b.missing_information, ["location"])
        self.assertEqual(r_b.next_question, "Which village or field do you need the tractor in?")
        self.assertNotIn("Peddapuram", r_b.text)
        print("\n[PASS] Test 5: Cross-conversation isolation verified; Conv B did not inherit Peddapuram from Conv A.")

    def test_06_sqlite_fallback_recovery(self):
        """TEST 6: If RAM state is cleared between turns, SQLite history restores location Peddapuram."""
        conv = f"conv_test_6_{uuid.uuid4().hex[:6]}"
        
        # Turn 1
        KisanSaarthiOrchestrator.process(self.farmer_id, "I want a tractor", "en", conv, self.db)
        
        # Turn 2: Peddapuram is stored in DB
        KisanSaarthiOrchestrator.process(self.farmer_id, "Peddapuram", "en", conv, self.db)
        
        # SIMULATE RAM FLUSH / PROCESS RESTART (clear in-memory _SESSION_STATES)
        TractorAgent.clear_session_state(self.farmer_id, conv)
        self.assertIsNone(TractorAgent.get_session_state(self.farmer_id, conv).get("location"))
        
        # Turn 3: "Tomorrow at 2:30 PM" -> SQLite fallback restores Peddapuram!
        r3 = KisanSaarthiOrchestrator.process(self.farmer_id, "Tomorrow at 2:30 PM", "en", conv, self.db)
        self.assertEqual(r3.status, "ready")
        self.assertIn("Peddapuram", r3.text)
        self.assertIn("GreenField Tractor", r3.text)
        
        state = TractorAgent.get_session_state(self.farmer_id, conv)
        self.assertEqual(state["location"], "Peddapuram")
        self.assertEqual(state["date"], "Tomorrow")
        print("\n[PASS] Test 6: SQLite history successfully restored Peddapuram even after RAM state was wiped.")


if __name__ == "__main__":
    unittest.main()
