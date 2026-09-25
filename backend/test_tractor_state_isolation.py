"""
Verification test for Tractor Booking session state isolation across conversations.
Ensures that starting a new conversation (conversation_id) does not leak stale date/location state.
"""

import sys
import unittest
from services.orchestrator import KisanSaarthiOrchestrator
from agents.tractor import TractorAgent
from database.connection import SessionLocal

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class TestTractorStateIsolation(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.farmer_id = "F001"
        # Reset any in-memory session states
        TractorAgent.clear_session_state(self.farmer_id)

    def tearDown(self):
        TractorAgent.clear_session_state(self.farmer_id)
        self.db.close()

    def test_state_isolation_between_conversations(self):
        print("\n--- TEST: State Isolation Between Conversations ---")
        
        # =================================================================
        # CONVERSATION A: Farmer enters '26th September'
        # =================================================================
        conv_a = "conv_session_A_test"
        
        # Turn 1: "I want a tractor"
        r1_a = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="I want a tractor",
            language="en",
            conversation_id=conv_a,
            db=self.db,
        )
        self.assertEqual(r1_a.status, "needs_information")
        self.assertEqual(r1_a.missing_information, ["location"])
        self.assertEqual(r1_a.next_question, "Which village or field do you need the tractor in?")
        print("Conv A Turn 1: Asked location [PASS]")

        # Turn 2: "Peddapuram"
        r2_a = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="Peddapuram",
            language="en",
            conversation_id=conv_a,
            db=self.db,
        )
        self.assertEqual(r2_a.status, "needs_information")
        self.assertEqual(r2_a.missing_information, ["date"])
        self.assertEqual(r2_a.next_question, "When do you need the tractor?")
        print("Conv A Turn 2: Asked date [PASS]")

        # Turn 3: "26th September" -> date is recorded
        r3_a = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="26th September",
            language="en",
            conversation_id=conv_a,
            db=self.db,
        )
        print(f"Conv A Turn 3 status: {r3_a.status}, response preview: {r3_a.text[:80]}...")
        # Conv A now has "26th September" in its state

        # =================================================================
        # CONVERSATION B: Brand NEW session
        # Farmer starts over and types: "I want a tractor"
        # MUST NOT remember "26th September" from Conv A!
        # =================================================================
        conv_b = "conv_session_B_test"
        
        r1_b = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="I want a tractor",
            language="en",
            conversation_id=conv_b,
            db=self.db,
        )

        print("\n--- Conv B Turn 1 Response ---")
        print(f"Status: {r1_b.status}")
        print(f"Missing: {r1_b.missing_information}")
        print(f"Response: {r1_b.text}")

        # Assert that Conv B does NOT reuse the stale date
        self.assertNotIn("26th September", r1_b.text)
        self.assertNotIn("couldn't find a tractor", r1_b.text.lower())
        self.assertEqual(r1_b.status, "needs_information")
        self.assertEqual(r1_b.missing_information, ["location"])
        self.assertEqual(r1_b.next_question, "Which village or field do you need the tractor in?")
        print("Conv B Turn 1: Successfully started fresh, asked for location only [PASS]")

        # Turn 2: "Peddapuram village"
        r2_b = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="Peddapuram village",
            language="en",
            conversation_id=conv_b,
            db=self.db,
        )
        self.assertEqual(r2_b.status, "needs_information")
        self.assertEqual(r2_b.missing_information, ["date"])
        self.assertEqual(r2_b.next_question, "When do you need the tractor?")
        print("Conv B Turn 2: Asked date [PASS]")

        # Turn 3: "Tomorrow at 2:30 PM"
        r3_b = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="Tomorrow at 2:30 PM",
            language="en",
            conversation_id=conv_b,
            db=self.db,
        )
        self.assertEqual(r3_b.status, "ready")
        self.assertIn("GreenField Tractor", r3_b.text)
        print("Conv B Turn 3: Options presented [PASS]")

        # Turn 4: Select "Option 1"
        r4_b = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="Option 1",
            language="en",
            conversation_id=conv_b,
            db=self.db,
        )
        self.assertIn("Confirm Booking", r4_b.text)
        print("Conv B Turn 4: Review card presented [PASS]")

        # Turn 5: "Confirm"
        r5_b = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="Confirm",
            language="en",
            conversation_id=conv_b,
            db=self.db,
        )
        self.assertIn("BOOKING CONFIRMED", r5_b.text)
        self.assertIn("KS-", r5_b.text)
        print("Conv B Turn 5: Booking confirmed successfully [PASS]")

    def test_post_confirmation_reset_in_same_conversation(self):
        print("\n--- TEST: Post-confirmation Reset in Same Conversation ---")
        conv = "conv_post_conf_test"
        
        # Complete a booking
        KisanSaarthiOrchestrator.process(farmer_id=self.farmer_id, message="I need a tractor in Guntur tomorrow", language="en", conversation_id=conv, db=self.db)
        KisanSaarthiOrchestrator.process(farmer_id=self.farmer_id, message="1", language="en", conversation_id=conv, db=self.db)
        r_conf = KisanSaarthiOrchestrator.process(farmer_id=self.farmer_id, message="Confirm", language="en", conversation_id=conv, db=self.db)
        self.assertIn("BOOKING CONFIRMED", r_conf.text)
        print("Initial booking confirmed [PASS]")

        # Now start a new request in the SAME conversation
        r_new = KisanSaarthiOrchestrator.process(
            farmer_id=self.farmer_id,
            message="I want a tractor",
            language="en",
            conversation_id=conv,
            db=self.db,
        )
        self.assertEqual(r_new.status, "needs_information")
        self.assertEqual(r_new.missing_information, ["location"])
        self.assertEqual(r_new.next_question, "Which village or field do you need the tractor in?")
        print("Post-confirmation booking reset cleanly [PASS]")


if __name__ == "__main__":
    unittest.main()
