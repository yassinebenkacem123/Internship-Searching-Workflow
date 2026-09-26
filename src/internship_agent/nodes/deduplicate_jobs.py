from internship_agent.models.job import JobOpportunity
from internship_agent.services.deduplicator import deduplicate_jobs
from internship_agent.state import InternshipSearchState


def deduplicate_jobs_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to deduplicate jobs and merge duplicate source URLs."""
    filtered_jobs = state.get("filtered_jobs", [])
    deduped = deduplicate_jobs(filtered_jobs)
    return {"deduplicated_jobs": deduped}
