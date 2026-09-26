from typing import Protocol, runtime_checkable

from internship_agent.models.search_result import SearchResult


@runtime_checkable
class SearchProvider(Protocol):
    """Protocol interface for search providers."""

    async def search(self, query: str) -> list[SearchResult]:
        """Execute a search query asynchronously and return raw search results."""
        ...
