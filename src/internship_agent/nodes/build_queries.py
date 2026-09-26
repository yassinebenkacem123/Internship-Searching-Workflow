from internship_agent.config import get_settings
from internship_agent.services.query_generator import generate_search_queries
from internship_agent.state import InternshipSearchState


def build_queries_node(state: InternshipSearchState) -> dict[str, list[str]]:
    """LangGraph node to generate targeted search queries deterministically."""
    settings = get_settings()
    queries = generate_search_queries(candidate=settings.candidate)
    return {"queries": queries}
