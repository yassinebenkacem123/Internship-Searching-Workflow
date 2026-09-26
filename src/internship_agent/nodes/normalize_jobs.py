from internship_agent.models.job import JobOpportunity
from internship_agent.services.normalizer import normalize_search_result
from internship_agent.state import InternshipSearchState


def normalize_jobs_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to normalize raw search results into JobOpportunity instances."""
    raw_results = state.get("raw_results", [])
    normalized_jobs = [normalize_search_result(r) for r in raw_results]
    return {"normalized_jobs": normalized_jobs}
