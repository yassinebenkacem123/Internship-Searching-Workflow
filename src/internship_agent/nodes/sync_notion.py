from internship_agent.models.job import JobOpportunity
from internship_agent.services.notion import NotionSyncService
from internship_agent.state import InternshipSearchState


async def sync_notion_node(state: InternshipSearchState) -> dict[str, list[JobOpportunity]]:
    """LangGraph node to sync scored jobs with the Notion database."""
    scored_jobs = state.get("scored_jobs", [])
    service = NotionSyncService()
    created, updated = await service.sync_jobs(scored_jobs)
    return {
        "created_jobs": created,
        "updated_jobs": updated,
    }
