import logging
from typing import Any

import httpx

from internship_agent.models.search_result import SearchResult
from internship_agent.services.search.base import SearchProvider

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    """SearchProvider implementation using Tavily Search API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.endpoint = "https://api.tavily.com/search"

    async def search(self, query: str) -> list[SearchResult]:
        """Execute search on Tavily and return raw results."""
        if not self.api_key:
            logger.warning("Tavily API key is not configured. Skipping search.")
            return []

        payload: dict[str, Any] = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 10,
            "include_answer": False,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.endpoint, json=payload)
                if response.status_code != 200:
                    logger.error(
                        "Tavily search failed with status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    return []

                data = response.json()
                results: list[SearchResult] = []
                for item in data.get("results", []):
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("content"),
                            source="tavily",
                            published_date=item.get("published_date"),
                        )
                    )
                return results
        except Exception:
            logger.exception("Error executing Tavily search for query '%s'", query)
            return []
