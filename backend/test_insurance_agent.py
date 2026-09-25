"""
KisanSaarthi AI — Step 6B Insurance Assistance Agent Verification Suite.

Tests all 12 required test cases:
TEST 1:  Heavy rain damaged my paddy crop -> insurance_assistance, heavy_rain
TEST 2:  My field was flooded -> flood_waterlogging
TEST 3:  No rain for weeks and my crop is drying -> drought
TEST 4:  Hail destroyed my crop -> hailstorm
TEST 5:  Heavy rain damaged my paddy crop in Guntur yesterday -> Does NOT ask for crop/location/cause/date
TEST 6:  Multi-turn conversation -> Context preserved across turns
TEST 7:  What documents are useful for crop insurance? -> Documents guidance without incident interview
TEST 8:  Will I definitely get the insurance money? -> No guarantee clarification
TEST 9:  Tell me the capital of France -> Does not force insurance response
TEST 10: Telugu insurance request -> Telugu localized response
TEST 11: Hindi insurance request -> Hindi localized response
TEST 12: Complete insurance conversation -> Preliminary incident report generated
"""

import sys
import unittest
from agents.insurance import InsuranceAgent
from services.orchestrator import KisanSaarthiOrchestrator
from database.connection import SessionLocal
from database import repository


class TestInsuranceAssistanceAgent(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Reset session states
        InsuranceAgent.reset_session("FARMER-TEST-INS")
        InsuranceAgent.reset_session("FARMER-TEST-MULTITURN")

    def tearDown(self):
        self.db.close()

    def test_01_heavy_rain_intent_and_peril(self):
        """TEST 1: 'Heavy rain damaged my paddy crop.' -> insurance_assistance, heavy_rain"""
        query = "Heavy rain damaged my paddy crop."
        intents = KisanSaarthiOrchestrator.detect_intents(query)
        self.assertIn("insurance_assistance", intents)

        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["intent"], "insurance_assistance")
        self.assertEqual(res["collected_information"]["damage_type"], "heavy_rain")
        self.assertEqual(res["collected_information"]["crop"], "Paddy")
        self.assertEqual(res["status"], "information_collection")

    def test_02_flooded_field_peril(self):
        """TEST 2: 'My field was flooded.' -> flood_waterlogging"""
        query = "My field was flooded."
        intents = KisanSaarthiOrchestrator.detect_intents(query)
        self.assertIn("insurance_assistance", intents)

        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["collected_information"]["damage_type"], "flood_waterlogging")

    def test_03_drought_crop_drying(self):
        """TEST 3: 'No rain for weeks and my crop is drying.' -> drought"""
        query = "No rain for weeks and my crop is drying."
        intents = KisanSaarthiOrchestrator.detect_intents(query)
        self.assertIn("insurance_assistance", intents)

        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["collected_information"]["damage_type"], "drought")

    def test_04_hail_destroyed_crop(self):
        """TEST 4: 'Hail destroyed my crop.' -> hailstorm"""
        query = "Hail destroyed my crop."
        intents = KisanSaarthiOrchestrator.detect_intents(query)
        self.assertIn("insurance_assistance", intents)

        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["collected_information"]["damage_type"], "hailstorm")

    def test_05_information_extraction_no_redundant_questions(self):
        """TEST 5: 'Heavy rain damaged my paddy crop in Guntur yesterday.' -> Does NOT re-ask crop/location/cause/date."""
        InsuranceAgent.reset_session("FARMER-TEST-INS-5")
        query = "Heavy rain damaged my paddy crop in Guntur yesterday."
        res = InsuranceAgent.execute("FARMER-TEST-INS-5", query, language="en")

        state = res["collected_information"]
        self.assertEqual(state["crop"], "Paddy")
        self.assertEqual(state["damage_type"], "heavy_rain")
        self.assertEqual(state["location"], "Guntur")
        self.assertEqual(state["damage_date"], "Yesterday")

        # Must not ask for crop, location, damage_type, or date
        missing = res["missing_information"]
        self.assertNotIn("crop", missing)
        self.assertNotIn("damage_type", missing)
        self.assertNotIn("location", missing)
        self.assertNotIn("damage_date", missing)

        # Must ask for damage_extent as the next logical question
        self.assertEqual(missing[0], "damage_extent")
        self.assertIn("how much of the crop was affected", res["next_question"].lower())

    def test_06_multi_turn_conversation_context_preservation(self):
        """TEST 6: Multi-turn conversation remembers all previously provided answers."""
        import uuid
        farmer_id = f"FARMER-TEST-MULTITURN-{uuid.uuid4().hex[:6]}"
        InsuranceAgent.reset_session(farmer_id)

        # Turn 1
        res1 = InsuranceAgent.execute(farmer_id, "Heavy rain damaged my paddy.", language="en", db=self.db)
        self.assertEqual(res1["collected_information"]["crop"], "Paddy")
        self.assertEqual(res1["collected_information"]["damage_type"], "heavy_rain")
        self.assertIn("location", res1["missing_information"])

        # Turn 2: Farmer provides location
        res2 = InsuranceAgent.execute(farmer_id, "Guntur", language="en", db=self.db)
        self.assertEqual(res2["collected_information"]["crop"], "Paddy", "Lost previous crop")
        self.assertEqual(res2["collected_information"]["damage_type"], "heavy_rain", "Lost previous damage_type")
        self.assertEqual(res2["collected_information"]["location"], "Guntur")
        self.assertIn("damage_date", res2["missing_information"])

        # Turn 3: Farmer provides date
        res3 = InsuranceAgent.execute(farmer_id, "Yesterday", language="en", db=self.db)
        self.assertEqual(res3["collected_information"]["crop"], "Paddy")
        self.assertEqual(res3["collected_information"]["damage_type"], "heavy_rain")
        self.assertEqual(res3["collected_information"]["location"], "Guntur")
        self.assertEqual(res3["collected_information"]["damage_date"], "Yesterday")
        self.assertIn("damage_extent", res3["missing_information"])

    def test_07_documents_guidance_no_forced_interview(self):
        """TEST 7: 'What documents are useful for crop insurance?' -> Guidance without incident interview."""
        query = "What documents are useful for crop insurance?"
        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["retrieved_topic"], "documents_guidance")
        self.assertIsNone(res["report"])
        self.assertIn("Useful Documents", res["response"])
        self.assertIn("Pattadar Passbook", res["response"])

    def test_08_no_guarantee_clarification(self):
        """TEST 8: 'Will I definitely get the insurance money?' -> Refuses guarantee."""
        query = "Will I definitely get the insurance money?"
        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["retrieved_topic"], "no_guarantee_notice")
        self.assertIn("cannot guarantee claim approval", res["response"].lower())

    def test_09_unknown_out_of_domain_query(self):
        """TEST 9: 'Tell me the capital of France.' -> Does not force insurance response."""
        query = "Tell me the capital of France."
        intents = KisanSaarthiOrchestrator.detect_intents(query)
        self.assertNotIn("insurance_assistance", intents)

        res = InsuranceAgent.execute("FARMER-TEST-INS", query, language="en")
        # Should return unverified fallback or clarification
        self.assertTrue(
            "verified information" in res["response"].lower() or "clarification" in res.get("status", "")
        )

    def test_10_telugu_localized_response(self):
        """TEST 10: Telugu request receives natural Telugu response."""
        query = "భారీ వర్షాల వల్ల నా వరి పంట దెబ్బతింది"
        res = InsuranceAgent.execute("FARMER-TEST-TE", query, language="te")
        self.assertIn("te", res.get("language", "te"))
        # Check for Telugu script in question
        has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in res["response"])
        self.assertTrue(has_telugu, "Response must be in Telugu script.")

    def test_11_hindi_localized_response(self):
        """TEST 11: Hindi request receives natural Hindi response."""
        query = "भारी बारिश से मेरी धान की फसल खराब हो गई"
        res = InsuranceAgent.execute("FARMER-TEST-HI", query, language="hi")
        has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in res["response"])
        self.assertTrue(has_devanagari, "Response must be in Devanagari (Hindi) script.")

    def test_12_complete_interview_and_report_generation(self):
        """TEST 12: Complete conversation generates structured preliminary incident report."""
        import uuid
        farmer_id = f"FARMER-COMPLETE-E2E-{uuid.uuid4().hex[:6]}"
        InsuranceAgent.reset_session(farmer_id)

        # Step 1: Crop & cause
        r1 = InsuranceAgent.execute(farmer_id, "Heavy rain damaged my paddy crop.", language="en", db=self.db)
        self.assertEqual(r1["status"], "information_collection")

        # Step 2: Location
        r2 = InsuranceAgent.execute(farmer_id, "Guntur", language="en", db=self.db)
        self.assertEqual(r2["status"], "information_collection")

        # Step 3: Date
        r3 = InsuranceAgent.execute(farmer_id, "Yesterday", language="en", db=self.db)
        self.assertEqual(r3["status"], "information_collection")

        # Step 4: Extent
        r4 = InsuranceAgent.execute(farmer_id, "About half", language="en", db=self.db)
        self.assertEqual(r4["status"], "information_collection")

        # Step 5: Photo confirmation
        r5 = InsuranceAgent.execute(farmer_id, "Yes, I have a photo", language="en", db=self.db)
        self.assertEqual(r5["status"], "report_generated")
        self.assertIsNotNone(r5["report"])

        report = r5["report"]
        self.assertIn("CROP INSURANCE ASSISTANCE REPORT", report)
        self.assertIn("Paddy", report)
        self.assertIn("Heavy Rain", report)
        self.assertIn("Guntur", report)
        self.assertIn("Yesterday", report)
        self.assertIn("Photo available", report)
        self.assertIn("NEXT STEPS", report)
        self.assertIn("This is a preliminary assistance report", report)

    def test_13_orchestrator_routing_and_multi_turn(self):
        """TEST 13: Orchestrator automatically routes damage queries to Insurance Agent and preserves context."""
        import uuid
        farmer_id = f"FARMER-ORCH-{uuid.uuid4().hex[:6]}"
        conv_id = f"conv-{uuid.uuid4().hex[:6]}"

        # Turn 1: Farmer reports flood
        o1 = KisanSaarthiOrchestrator.process(farmer_id, "My field was flooded with water.", language="en", conversation_id=conv_id, db=self.db)
        self.assertEqual(o1.intent, "insurance_assistance")
        self.assertEqual(o1.agent, "Insurance Assistance Agent")
        self.assertEqual(o1.status, "information_collection")
        self.assertIn("Which crop", o1.response)

        # Turn 2: Farmer says crop
        o2 = KisanSaarthiOrchestrator.process(farmer_id, "Paddy", language="en", conversation_id=conv_id, db=self.db)
        self.assertEqual(o2.intent, "insurance_assistance")
        self.assertEqual(o2.agent, "Insurance Assistance Agent")
        self.assertIn("district or village", o2.response)


if __name__ == "__main__":
    unittest.main()
