"""
KisanSaarthi AI — Step 6A Insurance Knowledge Base & Retrieval Tests.

Verifies:
1. Heavy rain damage retrieval
2. Flood / waterlogging damage retrieval
3. Drought / dry spell retrieval
4. Hailstorm damage retrieval
5. Storm / wind damage retrieval
6. Pest / disease damage retrieval
7. General insurance document question
8. Unknown out-of-domain question (no forced match)
9. Question asking for guaranteed claim approval (no guarantees, clear refusal)
10. Knowledge base schema integrity and non-empty entries
"""

import sys
import unittest
from services.insurance_retrieval_service import (
    retrieve_insurance_guidance,
    load_knowledge_base,
    get_all_topics,
    UNVERIFIED_FALLBACK_MESSAGE,
    GENERAL_DISCLAIMER,
)


class TestInsuranceKnowledgeRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = load_knowledge_base()

    def test_00_knowledge_base_loaded(self):
        """Verifies knowledge base is properly loaded and has at least 10 entries."""
        self.assertGreaterEqual(len(self.entries), 10, "Knowledge base should contain at least 10 topics.")
        topics = get_all_topics()
        self.assertEqual(len(topics), len(self.entries))
        # Ensure essential keys are present in every entry
        required_keys = {"id", "topic", "keywords", "guidance", "information_to_collect", "useful_evidence", "general_next_steps"}
        for entry in self.entries:
            for k in required_keys:
                self.assertIn(k, entry, f"Missing required key '{k}' in entry {entry.get('id')}")
            self.assertGreater(len(entry["keywords"]), 0, f"Entry {entry.get('id')} has empty keywords")
            self.assertGreater(len(entry["guidance"]), 20, f"Entry {entry.get('id')} has too brief guidance")

    def test_01_heavy_rain_retrieval(self):
        """Test Case 1: 'My paddy crop was damaged because of heavy rain.'"""
        query = "My paddy crop was damaged because of heavy rain."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected heavy rain query to match.")
        self.assertEqual(res["topic_id"], "heavy_rain")
        self.assertIn("Heavy Rain", res["topic"])
        self.assertGreater(len(res["information_to_collect"]), 0)
        self.assertGreater(len(res["useful_evidence"]), 0)
        self.assertGreater(len(res["general_next_steps"]), 0)
        self.assertEqual(res["disclaimer"], GENERAL_DISCLAIMER)

    def test_02_flood_waterlogging_retrieval(self):
        """Test Case 2: 'Flood water entered my field.'"""
        query = "Flood water entered my field."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected flood/waterlogging query to match.")
        self.assertEqual(res["topic_id"], "flood_waterlogging")
        self.assertIn("Flood", res["topic"])
        self.assertTrue("submerge" in res["guidance"].lower() or "submergence" in res["guidance"].lower() or "water" in res["guidance"].lower())

    def test_03_drought_retrieval(self):
        """Test Case 3: 'There has been no rain and my crop is drying.'"""
        query = "There has been no rain and my crop is drying."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected drought query to match.")
        self.assertEqual(res["topic_id"], "drought")
        self.assertIn("Drought", res["topic"])

    def test_04_hailstorm_retrieval(self):
        """Test Case 4: 'Hail destroyed my crop.'"""
        query = "Hail destroyed my crop."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected hailstorm query to match.")
        self.assertEqual(res["topic_id"], "hailstorm")
        self.assertIn("Hailstorm", res["topic"])

    def test_05_storm_wind_retrieval(self):
        """Test Case 5: 'Strong wind damaged my plants.'"""
        query = "Strong wind damaged my plants."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected storm/wind query to match.")
        self.assertEqual(res["topic_id"], "storm_wind")
        self.assertIn("Storm", res["topic"])

    def test_06_pest_disease_retrieval(self):
        """Test Case 6: 'Pests damaged my crop.'"""
        query = "Pests damaged my crop."
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected pest/disease query to match.")
        self.assertEqual(res["topic_id"], "pest_disease")
        self.assertIn("Pest", res["topic"])

    def test_07_documents_guidance_retrieval(self):
        """Test Case 7: 'What documents should I keep for crop insurance?'"""
        query = "What documents should I keep for crop insurance?"
        res = retrieve_insurance_guidance(query)
        self.assertTrue(res["matched"], "Expected documents guidance to match.")
        self.assertEqual(res["topic_id"], "documents_guidance")
        self.assertIn("Documents", res["topic"])
        # Verify land records and bank details are mentioned in guidance/collected info
        combined_text = " ".join(res["information_to_collect"] + [res["guidance"]]).lower()
        self.assertTrue("land" in combined_text or "passbook" in combined_text or "aadhaar" in combined_text)

    def test_08_unknown_question_no_forced_match(self):
        """Test Case 8: Out-of-domain queries must return matched: False and never force an insurance topic."""
        unknown_queries = [
            "What is the capital of France?",
            "How do I repair a broken smartphone screen?",
            "Give me a recipe for chocolate cake",
            "Where can I buy football boots?",
        ]
        for q in unknown_queries:
            res = retrieve_insurance_guidance(q)
            self.assertFalse(res["matched"], f"Query '{q}' should not match any insurance topic.")
            self.assertEqual(res["topic_id"], "unknown")
            self.assertEqual(res["topic"], "unknown")
            self.assertEqual(res["message"], UNVERIFIED_FALLBACK_MESSAGE)

    def test_09_no_guarantee_clarification(self):
        """Test Case 9: Inquiries asking for guaranteed approval must NOT promise or guarantee approval."""
        guarantee_queries = [
            "Can you guarantee that my insurance claim will be approved?",
            "Will I definitely get money for my damaged crop?",
            "Promise me that 100% claim will be passed",
        ]
        for q in guarantee_queries:
            res = retrieve_insurance_guidance(q)
            self.assertTrue(res["matched"], f"Query '{q}' should match guarantee clarification topic.")
            self.assertEqual(res["topic_id"], "no_guarantee_notice")
            # Verify explicit refusal of guarantee
            guidance = res["guidance"].lower()
            self.assertTrue(
                "no" in guidance and ("guarantee" in guidance or "approval" in guidance),
                "Guidance must state that claim approval cannot be guaranteed.",
            )

    def test_10_multilingual_queries(self):
        """Test Case 10: Supports basic Telugu and Hindi queries."""
        # Telugu heavy rain
        res_te = retrieve_insurance_guidance("వరి పంట వర్షానికి దెబ్బతింది")
        self.assertTrue(res_te["matched"])
        self.assertEqual(res_te["topic_id"], "heavy_rain")

        # Telugu drought
        res_te_dry = retrieve_insurance_guidance("వర్షాలు లేక పంట ఎండిపోతోంది")
        self.assertTrue(res_te_dry["matched"])
        self.assertEqual(res_te_dry["topic_id"], "drought")

        # Hindi flood
        res_hi = retrieve_insurance_guidance("खेत में बाढ़ का पानी भर गया")
        self.assertTrue(res_hi["matched"])
        self.assertEqual(res_hi["topic_id"], "flood_waterlogging")

        # Hindi hailstorm
        res_hi_hail = retrieve_insurance_guidance("कल ओलावृष्टि से फसल नष्ट हो गई")
        self.assertTrue(res_hi_hail["matched"])
        self.assertEqual(res_hi_hail["topic_id"], "hailstorm")


if __name__ == "__main__":
    unittest.main()
