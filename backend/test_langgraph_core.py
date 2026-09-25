"""
Unit tests for KisanSaarthi LangGraph Core Foundation (Phase 2).
Tests routing, supervisor node, StateGraph compilation, multilingual input, and state preservation.
"""

import os
import sys

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from graph.state import KisanSaarthiState
from graph.router import route_message, supervisor_node
from graph.workflow import build_kisansaarthi_graph, get_kisansaarthi_graph


def test_graph_compilation():
    """Test 8: Graph compiles successfully and singleton getter works."""
    print("Testing Graph compilation...")
    graph = build_kisansaarthi_graph()
    assert graph is not None, "Failed to compile LangGraph StateGraph"

    cached_graph = get_kisansaarthi_graph()
    assert cached_graph is not None, "get_kisansaarthi_graph returned None"
    print("  PASS: LangGraph StateGraph compiled cleanly.")


def test_tractor_routing():
    """Test 1: Tractor message routes to tractor_booking and tractor agent."""
    print("Testing Tractor routing...")
    queries = [
        "I need a tractor",
        "Book a 45HP tractor in Peddapuram",
        "Need a rotavator for ploughing",
    ]
    graph = get_kisansaarthi_graph()
    for q in queries:
        state: KisanSaarthiState = {
            "farmer_id": "test_farmer_1",
            "conversation_id": "conv_tractor",
            "language": "en",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == "tractor_booking", f"Expected tractor_booking, got {result['detected_intent']} for: {q}"
        assert result["active_agent"] == "tractor", f"Expected tractor, got {result['active_agent']}"
        assert result["status"] in ["routed", "needs_information", "ready", "completed"]
        assert result["farmer_id"] == "test_farmer_1"
    print("  PASS: Tractor messages routed correctly.")


def test_crop_health_routing():
    """Test 2: Crop health message routes to crop_health."""
    print("Testing Crop Health routing...")
    queries = [
        "My paddy leaves have spots",
        "Yellow leaves and blight on cotton crop",
        "There is a disease affecting my chilli plants",
    ]
    graph = get_kisansaarthi_graph()
    for q in queries:
        state: KisanSaarthiState = {
            "farmer_id": "test_farmer_1",
            "conversation_id": "conv_crop",
            "language": "en",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == "crop_health", f"Expected crop_health, got {result['detected_intent']} for: {q}"
        assert result["active_agent"] == "crop_health", f"Expected crop_health, got {result['active_agent']}"

    # Multimodal image test
    image_state: KisanSaarthiState = {
        "farmer_id": "test_farmer_1",
        "conversation_id": "conv_crop_img",
        "language": "en",
        "user_message": "Check this",
        "image_bytes": b"fake_leaf_image_bytes",
    }
    img_result = graph.invoke(image_state)
    assert img_result["detected_intent"] == "crop_health"
    assert img_result["active_agent"] == "crop_health"
    print("  PASS: Crop Health messages and image routed correctly.")


def test_insurance_routing():
    """Test 3: Insurance message routes to insurance."""
    print("Testing Insurance routing...")
    queries = [
        "I need crop insurance",
        "Heavy rain damaged my crops and I want to claim PMFBY compensation",
        "Crop loss due to flood",
    ]
    graph = get_kisansaarthi_graph()
    for q in queries:
        state: KisanSaarthiState = {
            "farmer_id": "test_farmer_1",
            "conversation_id": "conv_insurance",
            "language": "en",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == "insurance", f"Expected insurance, got {result['detected_intent']} for: {q}"
        assert result["active_agent"] == "insurance", f"Expected insurance, got {result['active_agent']}"
    print("  PASS: Insurance messages routed correctly.")


def test_crop_residue_routing():
    """Test 4: Crop residue message routes to crop_residue."""
    print("Testing Crop Residue routing...")
    queries = [
        "I have paddy straw, what should I do?",
        "How to manage crop residue without burning?",
        "What can I do with agricultural waste and stubble?",
    ]
    graph = get_kisansaarthi_graph()
    for q in queries:
        state: KisanSaarthiState = {
            "farmer_id": "test_farmer_1",
            "conversation_id": "conv_residue",
            "language": "en",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == "crop_residue", f"Expected crop_residue, got {result['detected_intent']} for: {q}"
        assert result["active_agent"] == "crop_residue", f"Expected crop_residue, got {result['active_agent']}"
    print("  PASS: Crop residue messages routed correctly.")


def test_general_agriculture_routing():
    """Test 5: General agriculture message routes to general_agriculture."""
    print("Testing General Agriculture routing...")
    queries = [
        "When should I sow paddy?",
        "What is the best crop rotation for cotton?",
        "How much fertilizer should I use for rice?",
    ]
    graph = get_kisansaarthi_graph()
    for q in queries:
        state: KisanSaarthiState = {
            "farmer_id": "test_farmer_1",
            "conversation_id": "conv_general",
            "language": "en",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == "general_agriculture", f"Expected general_agriculture, got {result['detected_intent']} for: {q}"
        assert result["active_agent"] == "general_agriculture", f"Expected general_agriculture, got {result['active_agent']}"
    print("  PASS: General agriculture messages routed correctly.")


def test_telugu_input():
    """Test 6: Telugu input does not crash and routes accurately."""
    print("Testing Telugu input handling...")
    telugu_queries = [
        ("ట్రాక్టర్ కావాలి", "tractor_booking", "tractor"),
        ("వరి ఆకులపై మచ్చలు ఉన్నాయి", "crop_health", "crop_health"),
        ("పంట భీమా కావాలి", "insurance", "insurance"),
        ("వరి గడ్డి ఉంది ఏం చేయాలి?", "crop_residue", "crop_residue"),
        ("వరిని ఎప్పుడు విత్తాలి?", "general_agriculture", "general_agriculture"),
    ]
    graph = get_kisansaarthi_graph()
    for q, expected_intent, expected_agent in telugu_queries:
        state: KisanSaarthiState = {
            "farmer_id": "telugu_farmer",
            "conversation_id": "conv_te",
            "language": "te",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == expected_intent, f"Expected {expected_intent}, got {result['detected_intent']} for '{q}'"
        assert result["active_agent"] == expected_agent, f"Expected {expected_agent}, got {result['active_agent']} for '{q}'"
        assert bool(result.get("status")), f"Empty status returned for '{q}'"
    print("  PASS: Telugu queries handled safely without crash.")


def test_hindi_input():
    """Test 7: Hindi input does not crash and routes accurately."""
    print("Testing Hindi input handling...")
    hindi_queries = [
        ("ट्रैक्टर चाहिए", "tractor_booking", "tractor"),
        ("पत्तियों पर धब्बे हैं", "crop_health", "crop_health"),
        ("फसल बीमा", "insurance", "insurance"),
        ("पराली का क्या करें?", "crop_residue", "crop_residue"),
        ("धान की बुवाई कब करें?", "general_agriculture", "general_agriculture"),
    ]
    graph = get_kisansaarthi_graph()
    for q, expected_intent, expected_agent in hindi_queries:
        state: KisanSaarthiState = {
            "farmer_id": "hindi_farmer",
            "conversation_id": "conv_hi",
            "language": "hi",
            "user_message": q,
        }
        result = graph.invoke(state)
        assert result["detected_intent"] == expected_intent, f"Expected {expected_intent}, got {result['detected_intent']} for '{q}'"
        assert result["active_agent"] == expected_agent, f"Expected {expected_agent}, got {result['active_agent']} for '{q}'"
        assert bool(result.get("status")), f"Empty status returned for '{q}'"
    print("  PASS: Hindi queries handled safely without crash.")


if __name__ == "__main__":
    print("\n--- RUNNING KISANSAARTHI LANGGRAPH CORE TESTS ---")
    test_graph_compilation()
    test_tractor_routing()
    test_crop_health_routing()
    test_insurance_routing()
    test_crop_residue_routing()
    test_general_agriculture_routing()
    test_telugu_input()
    test_hindi_input()
    print("\n>>> ALL LANGGRAPH CORE TESTS PASSED SUCCESSFULLY! <<<\n")
