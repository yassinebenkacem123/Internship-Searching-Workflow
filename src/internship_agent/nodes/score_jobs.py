from internship_agent.models.job import JobOpportunity
from internship_agent.services.scorer import score_jobs
from internship_agent.state import InternshipSearchState


def score_jobs_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to calculate deterministic match scores."""
    enriched = state.get("enriched_jobs", [])
    scored = score_jobs(enriched)
    return {"scored_jobs": scored}
