from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from internship_agent.nodes.build_digest import build_digest_node
from internship_agent.nodes.build_queries import build_queries_node
from internship_agent.nodes.deduplicate_jobs import deduplicate_jobs_node
from internship_agent.nodes.enrich_jobs import enrich_jobs_node
from internship_agent.nodes.filter_jobs import filter_jobs_node
from internship_agent.nodes.normalize_jobs import normalize_jobs_node
from internship_agent.nodes.score_jobs import score_jobs_node
from internship_agent.nodes.search_sources import search_sources_node
from internship_agent.nodes.send_notification import send_notification_node
from internship_agent.state import InternshipSearchState


def create_internship_graph() -> CompiledStateGraph:
    """Build and compile the end-to-end LangGraph workflow."""
    workflow = StateGraph(InternshipSearchState)

    # Register pipeline nodes
    workflow.add_node("build_queries", build_queries_node)
    workflow.add_node("search_sources", search_sources_node)
    workflow.add_node("normalize_jobs", normalize_jobs_node)
    workflow.add_node("filter_jobs", filter_jobs_node)
    workflow.add_node("deduplicate_jobs", deduplicate_jobs_node)
    workflow.add_node("enrich_jobs", enrich_jobs_node)
    workflow.add_node("score_jobs", score_jobs_node)
    workflow.add_node("build_digest", build_digest_node)
    workflow.add_node("send_notification", send_notification_node)

    # Define linear execution edges
    workflow.add_edge(START, "build_queries")
    workflow.add_edge("build_queries", "search_sources")
    workflow.add_edge("search_sources", "normalize_jobs")
    workflow.add_edge("normalize_jobs", "filter_jobs")
    workflow.add_edge("filter_jobs", "deduplicate_jobs")
    workflow.add_edge("deduplicate_jobs", "enrich_jobs")
    workflow.add_edge("enrich_jobs", "score_jobs")
    workflow.add_edge("score_jobs", "build_digest")
    workflow.add_edge("build_digest", "send_notification")
    workflow.add_edge("send_notification", END)

    return workflow.compile()
