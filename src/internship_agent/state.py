from typing import TypedDict

from internship_agent.models.job import JobOpportunity
from internship_agent.models.search_result import SearchResult


class InternshipSearchState(TypedDict, total=False):
    """LangGraph workflow state for internship discovery."""

    queries: list[str]
    raw_results: list[SearchResult]
    normalized_jobs: list[JobOpportunity]
    filtered_jobs: list[JobOpportunity]
    deduplicated_jobs: list[JobOpportunity]
    enriched_jobs: list[JobOpportunity]
    scored_jobs: list[JobOpportunity]
    created_jobs: list[JobOpportunity]
    updated_jobs: list[JobOpportunity]
    errors: list[str]
    digest: str
    notification_sent: bool
