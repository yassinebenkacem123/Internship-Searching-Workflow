from internship_agent.models.job import JobOpportunity
from internship_agent.services.enricher import enrich_jobs
from internship_agent.state import InternshipSearchState


async def enrich_jobs_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to enrich deduplicated jobs with skills and recruiter info."""
    deduplicated = state.get("deduplicated_jobs", [])
    enriched = await enrich_jobs(deduplicated)
    return {"enriched_jobs": enriched}
