"""
LangGraph Workflow Engine for KisanSaarthi Multi-Agent System.
Assembles the complete state graph with supervisor conditional routing,
specialized agent nodes, and the post-processor node.
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END

from graph.state import KisanSaarthiState
from graph.router import supervisor_node
from graph.nodes.crop_health_node import crop_health_node
from graph.nodes.tractor_node import tractor_node
from graph.nodes.insurance_node import insurance_node
from graph.nodes.general_agri_node import general_agri_node
from graph.nodes.crop_residue_node import crop_residue_node
from graph.nodes.post_processor import post_processor_node

# Global singleton for the compiled graph
_COMPILED_GRAPH = None


def route_supervisor_decision(state: KisanSaarthiState) -> str:
    """
    Conditional edge router: Inspects supervisor's routing decisions
    and selects the matching specialized agent node.
    """
    target = state.get("active_agent") or state.get("detected_intent") or "general_agriculture"

    if target in ["crop_health"]:
        return "crop_health_node"
    elif target in ["tractor", "tractor_booking"]:
        return "tractor_node"
    elif target in ["insurance", "insurance_assistance"]:
        return "insurance_node"
    elif target in ["crop_residue", "agricycle"]:
        return "crop_residue_node"
    else:
        return "general_agri_node"


def build_kisansaarthi_graph():
    """
    Constructs and compiles the complete KisanSaarthi Multi-Agent StateGraph.

    Architecture:
        START
          ↓
        supervisor
          ↓ (conditional edges)
        ├── crop_health_node
        ├── tractor_node
        ├── insurance_node
        ├── general_agri_node
        └── crop_residue_node
          ↓
        post_processor
          ↓
        END
    """
    workflow = StateGraph(KisanSaarthiState)

    # 1. Add supervisor node
    workflow.add_node("supervisor", supervisor_node)

    # 2. Add specialized agent nodes
    workflow.add_node("crop_health_node", crop_health_node)
    workflow.add_node("tractor_node", tractor_node)
    workflow.add_node("insurance_node", insurance_node)
    workflow.add_node("general_agri_node", general_agri_node)
    workflow.add_node("crop_residue_node", crop_residue_node)

    # 3. Add post-processing node
    workflow.add_node("post_processor", post_processor_node)

    # 4. Entry edge: START -> supervisor
    workflow.add_edge(START, "supervisor")

    # 5. Conditional routing edges: supervisor -> specialized nodes
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor_decision,
        {
            "crop_health_node": "crop_health_node",
            "tractor_node": "tractor_node",
            "insurance_node": "insurance_node",
            "general_agri_node": "general_agri_node",
            "crop_residue_node": "crop_residue_node",
        },
    )

    # 6. Edges from all agent nodes to post_processor
    workflow.add_edge("crop_health_node", "post_processor")
    workflow.add_edge("tractor_node", "post_processor")
    workflow.add_edge("insurance_node", "post_processor")
    workflow.add_edge("general_agri_node", "post_processor")
    workflow.add_edge("crop_residue_node", "post_processor")

    # 7. Final edge: post_processor -> END
    workflow.add_edge("post_processor", END)

    # 8. Compile graph
    return workflow.compile()


def get_kisansaarthi_graph():
    """
    Returns the cached compiled StateGraph singleton.
    Builds the graph on first call.
    """
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_kisansaarthi_graph()
    return _COMPILED_GRAPH


def reset_kisansaarthi_graph():
    """Forces rebuild of the graph (useful for test resets)."""
    global _COMPILED_GRAPH
    _COMPILED_GRAPH = None
