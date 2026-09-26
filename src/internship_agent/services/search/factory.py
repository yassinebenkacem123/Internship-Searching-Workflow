from internship_agent.config import get_settings
from internship_agent.services.search.base import SearchProvider
from internship_agent.services.search.tavily import TavilySearchProvider


def get_search_provider() -> SearchProvider:
    """Return the configured search provider."""
    settings = get_settings()
    provider_name = (settings.search_provider or "").lower()
    if provider_name == "tavily" or settings.search_api_key:
        return TavilySearchProvider(api_key=settings.search_api_key)
    return TavilySearchProvider(api_key=settings.search_api_key)
