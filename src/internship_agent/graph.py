from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from internship_agent.nodes.build_queries import build_queries_node
from internship_agent.state import InternshipSearchState


def create_internship_graph() -> CompiledStateGraph:
    """Build and compile the minimal LangGraph workflow for Phase 1."""
    workflow = StateGraph(InternshipSearchState)
    workflow.add_node("build_queries", build_queries_node)
    workflow.add_edge(START, "build_queries")
    workflow.add_edge("build_queries", END)
    return workflow.compile()
