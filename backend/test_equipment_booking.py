"""
KisanSaarthi AI — Step 7 Equipment Booking Agent Verification Test Suite

Comprehensive automated test suite covering all 12 requirements:
1. Basic tractor request (intent, entities, options)
2. Missing information handling (date & location)
3. One-question-at-a-time collection (missing location)
4. Multi-turn state preservation across turns
5. Equipment availability search across 5 catalogue models
6. Time-slot filtering across the 4 standard slots
7. Equipment selection (number, option label, name)
8. Successful booking structured output
9. SQLite booking persistence & retrieval
10. Telugu request localization (options + confirmation)
11. Hindi request localization (options + confirmation)
12. Orchestrator routing via /api/chat HTTP endpoint
"""

import os
import sys
import unittest
import json
import urllib.request
from typing import Dict, Any

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from tools.tractor_tool import (
    EQUIPMENT_CATALOGUE,
    TIME_SLOTS,
    search_equipment,
)
from agents.tractor import TractorAgent
from services.orchestrator import KisanSaarthiOrchestrator
from database.connection import SessionLocal
from database import repository


def post_chat_api(
    message: str,
    farmer_id: str = "FARMER-EQ-TEST",
    language: str = "en",
    conversation_id: str = "conv-eq-001",
) -> tuple:
    url = "http://127.0.0.1:8000/api/chat"
    payload = {
        "farmer_id": farmer_id,
        "message": message,
        "language": language,
        "conversation_id": conversation_id,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


class TestEquipmentBookingAgent(unittest.TestCase):
    """Full test suite for KisanSaarthi Equipment Booking Agent."""

    def setUp(self):
        self.db = SessionLocal()
        self.farmer_id = "FARMER-TEST-EQ"
        TractorAgent.clear_session_state(self.farmer_id)

    def tearDown(self):
        TractorAgent.clear_session_state(self.farmer_id)
        self.db.close()

    # -----------------------------------------------------------------
    # TEST 1: Basic Tractor Request
    # -----------------------------------------------------------------
    def test_01_basic_tractor_request(self):
        """1. Basic tractor request extracts date, location, and displays options."""
        query = "I need a tractor tomorrow in Guntur"
        res = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query=query,
            language="en",
            db=self.db,
        )

        self.assertEqual(res["intent"], "tractor_booking")
        self.assertEqual(res["status"], "ready")
        self.assertIn("options", res)
        self.assertGreaterEqual(len(res["options"]), 1)
        self.assertEqual(res["details"]["location"], "Guntur")
        self.assertEqual(res["details"]["date"], "Tomorrow")
        self.assertIn("GreenField Tractor", res["response"])
        print("\n[PASS] Test 1: Basic tractor request successfully extracted date & location and presented options.")

    # -----------------------------------------------------------------
    # TEST 2: Missing Information Handling
    # -----------------------------------------------------------------
    def test_02_missing_information_handling(self):
        """2. Missing information handling asks ONLY for location first when neither is provided."""
        query = "I need a tractor"
        res = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query=query,
            language="en",
            db=self.db,
        )

        self.assertEqual(res["status"], "needs_information")
        self.assertEqual(res["missing_information"], ["location"])
        self.assertIsNotNone(res["next_question"])
        self.assertEqual(res["next_question"], "Which village or field do you need the tractor in?")
        print("\n[PASS] Test 2: Missing information correctly asked ONLY for location first.")

    # -----------------------------------------------------------------
    # TEST 3: One-Question-at-a-Time Collection
    # -----------------------------------------------------------------
    def test_03_one_question_at_a_time(self):
        """3. When date is provided but location is missing, asks ONLY for location."""
        query = "I need a tractor tomorrow"
        res = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query=query,
            language="en",
            db=self.db,
        )

        self.assertEqual(res["status"], "needs_information")
        self.assertEqual(res["missing_information"], ["location"])
        self.assertEqual(res["next_question"], "Which village or field do you need the tractor in?")
        print("\n[PASS] Test 3: One-question-at-a-time asked specifically for location when date was given.")

    # -----------------------------------------------------------------
    # TEST 4: Multi-turn State Preservation
    # -----------------------------------------------------------------
    def test_04_multiturn_state_preservation(self):
        """4. Preserves date across turns when farmer answers location in the next message."""
        # Turn 1: "I need a tractor tomorrow" -> records date="Tomorrow"
        t1 = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="I need a tractor tomorrow",
            language="en",
            db=self.db,
        )
        self.assertEqual(t1["status"], "needs_information")
        self.assertEqual(t1["missing_information"], ["location"])

        # Turn 2: "In Guntur" -> should remember date="Tomorrow" and now complete the request
        t2 = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="In Guntur",
            language="en",
            db=self.db,
        )
        self.assertEqual(t2["status"], "ready")
        self.assertEqual(t2["details"]["date"], "Tomorrow")
        self.assertEqual(t2["details"]["location"], "Guntur")
        self.assertGreaterEqual(len(t2["options"]), 1)
        print("\n[PASS] Test 4: Multi-turn state preservation maintained date and completed flow when location answered.")

    # -----------------------------------------------------------------
    # TEST 5: Equipment Availability Search across Catalogue Models
    # -----------------------------------------------------------------
    def test_05_equipment_availability_search(self):
        """5. Verifies all 5 catalogue models and hourly rates exist."""
        all_equipment = search_equipment(location="Guntur", date="Tomorrow", equipment_type=None)
        self.assertEqual(len(all_equipment), 5)

        names = [eq["name"] for eq in all_equipment]
        self.assertIn("GreenField Tractor", names)
        self.assertIn("Kisan Power Tractor", names)
        self.assertIn("Mahindra Farm Tractor", names)
        self.assertIn("Rotavator", names)
        self.assertIn("Power Tiller", names)

        # Check rates
        rates = {eq["name"]: eq["price"] for eq in all_equipment}
        self.assertEqual(rates["GreenField Tractor"], 800)
        self.assertEqual(rates["Kisan Power Tractor"], 750)
        self.assertEqual(rates["Mahindra Farm Tractor"], 850)
        self.assertEqual(rates["Rotavator"], 500)
        self.assertEqual(rates["Power Tiller"], 400)
        print("\n[PASS] Test 5: Equipment catalogue search verified all 5 models and exact hourly rates.")

    # -----------------------------------------------------------------
    # TEST 6: Time-slot Filtering
    # -----------------------------------------------------------------
    def test_06_time_slot_filtering(self):
        """6. Verifies predefined time slots (8-11, 11-2, 2-5, 5-8) and slot keyword mapping."""
        self.assertEqual(len(TIME_SLOTS), 4)
        self.assertIn("8:00 AM – 11:00 AM", TIME_SLOTS)
        self.assertIn("11:00 AM – 2:00 PM", TIME_SLOTS)
        self.assertIn("2:00 PM – 5:00 PM", TIME_SLOTS)
        self.assertIn("5:00 PM – 8:00 PM", TIME_SLOTS)

        # Test morning slot extraction
        morning_slot = TractorAgent.extract_time_slot("tomorrow morning")
        self.assertEqual(morning_slot, "8:00 AM – 11:00 AM")

        # Test afternoon slot extraction
        afternoon_slot = TractorAgent.extract_time_slot("at 2 pm in the afternoon")
        self.assertEqual(afternoon_slot, "2:00 PM – 5:00 PM")

        # Test evening slot extraction
        evening_slot = TractorAgent.extract_time_slot("evening time")
        self.assertEqual(evening_slot, "5:00 PM – 8:00 PM")
        print("\n[PASS] Test 6: Time-slot filtering correctly mapped keywords to the 4 predefined slots.")

    # -----------------------------------------------------------------
    # TEST 7: Equipment Selection
    # -----------------------------------------------------------------
    def test_07_equipment_selection(self):
        """7. Equipment selection recognizes number ('1'), option string ('Option 2'), or name ('GreenField')."""
        # Test number selection
        self.assertEqual(TractorAgent.is_selection_query("1"), 1)
        self.assertEqual(TractorAgent.is_selection_query("#2"), 2)

        # Test phrase selection
        self.assertEqual(TractorAgent.is_selection_query("Option 1"), 1)
        self.assertEqual(TractorAgent.is_selection_query("Option 2"), 2)
        self.assertEqual(TractorAgent.is_selection_query("option 3"), 3)

        # Test name selection
        self.assertEqual(TractorAgent.is_selection_query("I want GreenField Tractor"), 1)
        self.assertEqual(TractorAgent.is_selection_query("Kisan Power Tractor"), 2)
        self.assertEqual(TractorAgent.is_selection_query("Mahindra"), 3)
        self.assertEqual(TractorAgent.is_selection_query("Rotavator"), 4)
        self.assertEqual(TractorAgent.is_selection_query("Power Tiller"), 5)
        print("\n[PASS] Test 7: Selection detection successfully matched numbers, option labels, and names.")

    # -----------------------------------------------------------------
    # TEST 8: Successful Booking Structured Confirmation
    # -----------------------------------------------------------------
    def test_08_successful_booking(self):
        """8. Confirmed booking outputs structured details with Booking ID, name, date, slot, price, status."""
        # Initial request to populate options
        TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="I need a tractor tomorrow in Guntur",
            language="en",
            db=self.db,
        )

        # Step 1: Select Option 1 (GreenField Tractor) -> Returns Review Card
        review = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="Option 1",
            language="en",
            db=self.db,
        )
        self.assertEqual(review["status"], "ready")
        self.assertEqual(review["stage"], "awaiting_confirmation")
        self.assertIn("CONFIRM YOUR BOOKING", review["response"])
        self.assertIn("Farmer Details", review["response"])
        self.assertIn("GreenField Tractor", review["response"])

        # Step 2: Confirm Booking -> Confirmed output with Booking ID
        res = TractorAgent.execute(
            farmer_id=self.farmer_id,
            query="Confirm Booking",
            language="en",
            db=self.db,
        )
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["stage"], "confirmed")
        self.assertIsNotNone(res["booking_id"])
        self.assertTrue(res["booking_id"].startswith("KS-") or res["booking_id"].startswith("TRK-"))

        booking = res["booking"]
        self.assertIsNotNone(booking)
        self.assertEqual(booking["equipment_name"], "GreenField Tractor")
        self.assertEqual(booking["location"], "Guntur")
        self.assertEqual(booking["date"], "Tomorrow")
        self.assertEqual(booking["price"], 800.0)
        self.assertEqual(booking["status"], "confirmed")
        self.assertIn("BOOKING CONFIRMED", res["response"])
        print(f"\n[PASS] Test 8: Successful booking generated confirmation with Booking ID: {res['booking_id']}.")

    # -----------------------------------------------------------------
    # TEST 9: SQLite Booking Persistence
    # -----------------------------------------------------------------
    def test_09_sqlite_booking_persistence(self):
        """9. Verifies booking record is created and persists in SQLite bookings table."""
        # Clean farmer booking
        persist_farmer_id = "FARMER-SQLITE-TEST"
        TractorAgent.clear_session_state(persist_farmer_id)

        # Step 1: Options
        TractorAgent.execute(
            farmer_id=persist_farmer_id,
            query="I need a tractor tomorrow in Suryapet",
            language="en",
            db=self.db,
        )

        # Step 2: Select Option 2 (Kisan Power Tractor) -> Review Card
        review = TractorAgent.execute(
            farmer_id=persist_farmer_id,
            query="Option 2",
            language="en",
            db=self.db,
        )
        self.assertEqual(review["stage"], "awaiting_confirmation")

        # Step 3: Confirm Booking
        res = TractorAgent.execute(
            farmer_id=persist_farmer_id,
            query="Confirm Booking",
            language="en",
            db=self.db,
        )
        booking_id = res["booking_id"]

        # Step 4: Query SQLite database directly
        db_booking = repository.get_booking(self.db, booking_id)
        self.assertIsNotNone(db_booking)
        self.assertEqual(db_booking.id, booking_id)
        self.assertEqual(db_booking.farmer_id, persist_farmer_id)
        self.assertEqual(db_booking.equipment_name, "Kisan Power Tractor")
        self.assertEqual(db_booking.location, "Suryapet")
        self.assertEqual(db_booking.price, 750.0)
        self.assertEqual(db_booking.status, "confirmed")

        # Check farmer bookings list
        farmer_bookings = repository.list_farmer_bookings(self.db, farmer_id=persist_farmer_id)
        self.assertTrue(any(b.id == booking_id for b in farmer_bookings))
        print(f"\n[PASS] Test 9: SQLite persistence confirmed; booking {booking_id} retrieved directly from DB.")

    # -----------------------------------------------------------------
    # TEST 10: Telugu Request Localization
    # -----------------------------------------------------------------
    def test_10_telugu_request_localization(self):
        """10. Telugu language request generates Telugu options and Telugu confirmation."""
        te_farmer = "FARMER-TE-TEST"
        TractorAgent.clear_session_state(te_farmer)

        # Request in Telugu
        te_query = "నాకు రేపు గుంటూరులో ట్రాక్టర్ కావాలి"
        t1 = TractorAgent.execute(
            farmer_id=te_farmer,
            query=te_query,
            language="te",
            db=self.db,
        )
        self.assertEqual(t1["status"], "ready")
        self.assertIn("అందుబాటులో ఉన్న పరికరాలు", t1["response"])
        self.assertIn("రూ. 800/గంటకు", t1["response"])

        # Select in Telugu: "ఎంపిక 1" -> Review Card
        t2 = TractorAgent.execute(
            farmer_id=te_farmer,
            query="ఎంపిక 1",
            language="te",
            db=self.db,
        )
        self.assertEqual(t2["status"], "ready")
        self.assertEqual(t2["stage"], "awaiting_confirmation")
        self.assertIn("మీ బుకింగ్ వివరాలను నిర్ధారించండి", t2["response"])

        # Confirm in Telugu: "ధృవీకరించండి"
        t3 = TractorAgent.execute(
            farmer_id=te_farmer,
            query="ధృవీకరించండి",
            language="te",
            db=self.db,
        )
        self.assertEqual(t3["status"], "ready")
        self.assertEqual(t3["stage"], "confirmed")
        self.assertIn("బుకింగ్ నిర్ధారించబడింది", t3["response"])
        self.assertIn("బుకింగ్ ID:", t3["response"])
        print("\n[PASS] Test 10: Telugu localization verified for both options and booking confirmation.")

    # -----------------------------------------------------------------
    # TEST 11: Hindi Request Localization
    # -----------------------------------------------------------------
    def test_11_hindi_request_localization(self):
        """11. Hindi language request generates Hindi options and Hindi confirmation."""
        hi_farmer = "FARMER-HI-TEST"
        TractorAgent.clear_session_state(hi_farmer)

        # Request in Hindi
        hi_query = "मुझे कल गुंटूर में ट्रैक्टर चाहिए"
        t1 = TractorAgent.execute(
            farmer_id=hi_farmer,
            query=hi_query,
            language="hi",
            db=self.db,
        )
        self.assertEqual(t1["status"], "ready")
        self.assertIn("उपलब्ध कृषि उपकरण", t1["response"])
        self.assertIn("रु. 800/घंटा", t1["response"])

        # Select in Hindi: "विकल्प 1" -> Review Card
        t2 = TractorAgent.execute(
            farmer_id=hi_farmer,
            query="विकल्प 1",
            language="hi",
            db=self.db,
        )
        self.assertEqual(t2["status"], "ready")
        self.assertEqual(t2["stage"], "awaiting_confirmation")
        self.assertIn("अपनी बुकिंग की पुष्टि करें", t2["response"])

        # Confirm in Hindi: "पुष्टि करें"
        t3 = TractorAgent.execute(
            farmer_id=hi_farmer,
            query="पुष्टि करें",
            language="hi",
            db=self.db,
        )
        self.assertEqual(t3["status"], "ready")
        self.assertEqual(t3["stage"], "confirmed")
        self.assertIn("बुकिंग कन्फर्म हो गई", t3["response"])
        self.assertIn("बुकिंग आईडी:", t3["response"])
        print("\n[PASS] Test 11: Hindi localization verified for both options and booking confirmation.")

    # -----------------------------------------------------------------
    # TEST 12: Orchestrator Routing via /api/chat
    # -----------------------------------------------------------------
    def test_12_orchestrator_routing_chat_api(self):
        """12. Full end-to-end conversation via /api/chat HTTP endpoint."""
        api_farmer = "FARMER-CHAT-API-TEST"
        conv_id = "conv-api-booking-001"
        TractorAgent.clear_session_state(api_farmer)

        # Turn 1: Farmer requests tractor with date & location
        status1, res1 = post_chat_api(
            message="I need a tractor tomorrow in Guntur",
            farmer_id=api_farmer,
            language="en",
            conversation_id=conv_id,
        )
        self.assertEqual(status1, 200)
        self.assertEqual(res1.get("intent"), "tractor_booking")
        self.assertEqual(res1.get("agent"), "Tractor Booking Agent")
        self.assertEqual(res1.get("status"), "ready")
        self.assertIn("GreenField Tractor", res1.get("response", ""))

        # Turn 2: Farmer selects option 1 -> Review Card
        status2, res2 = post_chat_api(
            message="Option 1",
            farmer_id=api_farmer,
            language="en",
            conversation_id=conv_id,
        )
        self.assertEqual(status2, 200)
        self.assertEqual(res2.get("intent"), "tractor_booking")
        self.assertIn("CONFIRM YOUR BOOKING", res2.get("response", ""))

        # Turn 3: Farmer confirms booking
        status3, res3 = post_chat_api(
            message="Confirm Booking",
            farmer_id=api_farmer,
            language="en",
            conversation_id=conv_id,
        )
        self.assertEqual(status3, 200)
        self.assertEqual(res3.get("intent"), "tractor_booking")
        self.assertIn("BOOKING CONFIRMED", res3.get("response", ""))
        self.assertIn("Booking ID:", res3.get("response", ""))
        print("\n[PASS] Test 12: Orchestrator /api/chat end-to-end conversation passed with booking confirmation.")

    # -----------------------------------------------------------------
    # TEST 13: Single-Turn Natural Utterance with Specific Time
    # -----------------------------------------------------------------
    def test_13_natural_utterance_single_turn(self):
        """13. 'I need a tractor in Guntur tomorrow at 2:30 PM.' extracts all fields and displays options directly."""
        single_farmer = "FARMER-SINGLE-TURN"
        TractorAgent.clear_session_state(single_farmer)
        res = TractorAgent.execute(
            farmer_id=single_farmer,
            query="I need a tractor in Guntur tomorrow at 2:30 PM.",
            language="en",
            db=self.db,
        )
        self.assertEqual(res["intent"], "tractor_booking")
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["stage"], "options_presented")
        self.assertEqual(res["details"]["location"], "Guntur")
        self.assertEqual(res["details"]["date"], "Tomorrow")
        self.assertEqual(res["details"]["specific_time"], "2:30 PM")
        self.assertEqual(res["details"]["time_slot"], "2:00 PM – 5:00 PM")
        self.assertGreaterEqual(len(res["options"]), 1)
        print("\n[PASS] Test 13: Single-turn natural utterance extracted equipment, location, date, and specific time.")

    # -----------------------------------------------------------------
    # TEST 14: Multi-Turn 5-Step Complete Conversational Booking Flow
    # -----------------------------------------------------------------
    def test_14_five_turn_conversation_flow(self):
        """14. Complete 5-turn booking flow from initial vague request to confirmed SQLite record."""
        f_id = "FARMER-5TURN-TEST"
        TractorAgent.clear_session_state(f_id)

        # Turn 1: "I need a tractor."
        t1 = TractorAgent.execute(
            farmer_id=f_id,
            query="I need a tractor.",
            language="en",
            db=self.db,
        )
        self.assertEqual(t1["status"], "needs_information")

        # Turn 2: "Guntur."
        t2 = TractorAgent.execute(
            farmer_id=f_id,
            query="Guntur.",
            language="en",
            db=self.db,
        )
        self.assertEqual(t2["status"], "needs_information")
        self.assertIn("date", t2["missing_information"])

        # Turn 3: "Tomorrow at 2:30 PM."
        t3 = TractorAgent.execute(
            farmer_id=f_id,
            query="Tomorrow at 2:30 PM.",
            language="en",
            db=self.db,
        )
        self.assertEqual(t3["status"], "ready")
        self.assertEqual(t3["stage"], "options_presented")
        self.assertGreaterEqual(len(t3["options"]), 1)

        # Turn 4: "Option 1."
        t4 = TractorAgent.execute(
            farmer_id=f_id,
            query="Option 1.",
            language="en",
            db=self.db,
        )
        self.assertEqual(t4["status"], "ready")
        self.assertEqual(t4["stage"], "awaiting_confirmation")
        self.assertIn("CONFIRM YOUR BOOKING", t4["response"])
        self.assertEqual(t4["confirmation_details"]["time"], "2:30 PM")

        # Turn 5: "Yes, confirm."
        t5 = TractorAgent.execute(
            farmer_id=f_id,
            query="Yes, confirm.",
            language="en",
            db=self.db,
        )
        self.assertEqual(t5["status"], "ready")
        self.assertEqual(t5["stage"], "confirmed")
        self.assertIn("BOOKING CONFIRMED", t5["response"])
        self.assertIsNotNone(t5["booking_id"])

        # Check persistence in SQLite
        persisted = repository.get_booking(self.db, t5["booking_id"])
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.location, "Guntur")
        self.assertEqual(persisted.date, "Tomorrow")
        self.assertEqual(persisted.time, "2:30 PM")
        print("\n[PASS] Test 14: 5-turn conversational booking workflow completed and persisted in SQLite.")

    # -----------------------------------------------------------------
    # TEST 15: Non-Demo Catalogue Location (e.g. Kakinada)
    # -----------------------------------------------------------------
    def test_15_non_demo_catalogue_location(self):
        """15. Accepts any location (Kakinada), but does not invent availability if not in demo catalogue."""
        f_id = "FARMER-NON-DEMO"
        TractorAgent.clear_session_state(f_id)

        res = TractorAgent.execute(
            farmer_id=f_id,
            query="I need a tractor tomorrow in Kakinada.",
            language="en",
            db=self.db,
        )
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["details"]["location"], "Kakinada")
        self.assertEqual(len(res["options"]), 0)
        self.assertIn("couldn't find a tractor in our demo catalogue for Kakinada", res["response"])
        print("\n[PASS] Test 15: Non-demo location accepted, clear demo catalogue explanation returned.")

    # -----------------------------------------------------------------
    # TEST 16: Multi-Detail 'tomorrow and village name is peddapuram village'
    # -----------------------------------------------------------------
    def test_16_multidetail_natural_peddapuram(self):
        """16. Extracts both date and location from 'tomorrow and village name is peddapuram village'."""
        f_id = "FARMER-MULTI-DETAIL"
        TractorAgent.clear_session_state(f_id)

        res = TractorAgent.execute(
            farmer_id=f_id,
            query="tomorrow and village name is peddapuram village",
            language="en",
            db=self.db,
        )
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["details"]["location"], "Peddapuram")
        self.assertEqual(res["details"]["date"], "Tomorrow")
        self.assertGreaterEqual(len(res["options"]), 1)
        print("\n[PASS] Test 16: Multi-detail 'tomorrow and village name is peddapuram village' extracted date and location.")


if __name__ == "__main__":
    unittest.main()
