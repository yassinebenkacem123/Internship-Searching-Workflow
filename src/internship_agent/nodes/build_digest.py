from internship_agent.services.digest import generate_daily_digest
from internship_agent.state import InternshipSearchState


def build_digest_node(state: InternshipSearchState) -> dict[str, str]:
    """LangGraph node to compile the daily digest from created and updated jobs."""
    created = state.get("created_jobs", [])
    updated = state.get("updated_jobs", [])
    # If no Notion sync ran or Notion returned empty, fallback to scored_jobs for digest
    if not created and not updated and state.get("scored_jobs"):
        created = state.get("scored_jobs", [])

    digest = generate_daily_digest(created_jobs=created, updated_jobs=updated)
    return {"digest": digest}
