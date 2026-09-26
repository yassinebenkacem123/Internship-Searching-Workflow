import asyncio
import logging

import httpx

from internship_agent.models.search_result import SearchResult
from internship_agent.services.search.factory import get_search_provider
from internship_agent.state import InternshipSearchState

logger = logging.getLogger(__name__)


async def search_sources_node(state: InternshipSearchState) -> dict[str, list[SearchResult] | list[str]]:
    """LangGraph node to execute search queries against configured search providers."""
    queries = state.get("queries", [])
    provider = get_search_provider()

    all_results: list[SearchResult] = []
    errors: list[str] = list(state.get("errors", []))

    # Concurrency limit to respect API rate limits
    semaphore = asyncio.Semaphore(3)

    async def _fetch(query: str) -> list[SearchResult]:
        async with semaphore:
            try:
                return await provider.search(query)
            except (httpx.HTTPError, RuntimeError, TimeoutError, ValueError) as exc:
                err_msg = f"Failed search for query '{query}': {exc}"
                logger.error(err_msg)
                errors.append(err_msg)
                return []

    # Run searches for queries
    tasks = [_fetch(q) for q in queries]
    if tasks:
        batch_results = await asyncio.gather(*tasks)
        for res in batch_results:
            all_results.extend(res)

    # Deduplicate raw results by URL
    seen_urls: set[str] = set()
    unique_results: list[SearchResult] = []
    for item in all_results:
        clean_url = item.url.strip()
        if clean_url and clean_url not in seen_urls:
            seen_urls.add(clean_url)
            unique_results.append(item)

    return {
        "raw_results": unique_results,
        "errors": errors,
    }
