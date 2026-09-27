from unittest.mock import AsyncMock, patch

import httpx
import pytest

from internship_agent.graph import create_internship_graph
from internship_agent.models.search_result import SearchResult
from internship_agent.services.search.base import SearchProvider


@pytest.mark.asyncio
async def test_full_graph_execution() -> None:
    graph = create_internship_graph()

    sample_results = [
        SearchResult(
            title="Stage PFE Développeur Backend Java - Casablanca | LinkedIn",
            url="https://www.linkedin.com/jobs/view/123",
            snippet="Stage PFE pour étudiant en fin d'études en Java, Spring Boot et Docker à Casablanca.",
            source="tavily",
        ),
        SearchResult(
            title="Senior Lead Manager",
            url="https://example.com/senior",
            snippet="10 ans d'expérience. CDI uniquement. Pas de stage.",
            source="tavily",
        ),
    ]

    with patch(
        "internship_agent.services.search.tavily.TavilySearchProvider.search",
        new_callable=AsyncMock,
    ) as mock_search, patch(
        "internship_agent.services.notification.telegram.TelegramNotifier.send_message",
        new_callable=AsyncMock,
    ) as mock_telegram:
        mock_search.return_value = sample_results
        mock_telegram.return_value = True

        result = await graph.ainvoke({})

        assert "queries" in result
        assert len(result["queries"]) > 0

        assert "raw_results" in result
        assert len(result["raw_results"]) > 0

        assert "normalized_jobs" in result
        assert len(result["normalized_jobs"]) > 0

        assert "filtered_jobs" in result
        # Only the PFE role should pass filtering, senior CDI should be rejected
        assert len(result["filtered_jobs"]) == 1
        assert result["filtered_jobs"][0].internship_type == "PFE"

        assert "deduplicated_jobs" in result
        assert len(result["deduplicated_jobs"]) == 1

        assert "scored_jobs" in result
        assert len(result["scored_jobs"]) == 1
        assert (result["scored_jobs"][0].match_score or 0) > 50

        assert "digest" in result
        assert "Stage PFE Développeur Backend Java" in result["digest"]


@pytest.mark.asyncio
async def test_search_provider_protocol() -> None:
    class DummySearchProvider:
        async def search(self, query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    title="Mock PFE Title",
                    url="https://example.com/mock",
                    snippet=f"Found for query: {query}",
                    source="mock",
                )
            ]

    provider = DummySearchProvider()
    assert isinstance(provider, SearchProvider)

    results = await provider.search("PFE Morocco")
    assert len(results) == 1
    assert results[0].title == "Mock PFE Title"
    assert results[0].url == "https://example.com/mock"


@pytest.mark.asyncio
async def test_tavily_search_provider_returns_results() -> None:
    from internship_agent.services.search.tavily import TavilySearchProvider

    provider = TavilySearchProvider(api_key="mock_key")
    mock_response = httpx.Response(
        200,
        json={
            "results": [
                {
                    "title": "Stage PFE Fullstack",
                    "url": "https://example.com/pfe",
                    "content": "Description",
                    "published_date": "2026-01-01",
                }
            ]
        },
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await provider.search("PFE Morocco")
        assert res is not None
        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0].title == "Stage PFE Fullstack"
        assert res[0].url == "https://example.com/pfe"
