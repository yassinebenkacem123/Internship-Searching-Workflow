from internship_agent.models.job import JobOpportunity
from internship_agent.services.filter import filter_jobs
from internship_agent.state import InternshipSearchState


def filter_jobs_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to filter out irrelevant or unqualified jobs."""
    normalized_jobs = state.get("normalized_jobs", [])
    filtered = filter_jobs(normalized_jobs)
    return {"filtered_jobs": filtered}
