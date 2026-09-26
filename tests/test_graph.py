import pytest

from internship_agent.graph import create_internship_graph
from internship_agent.models.search_result import SearchResult
from internship_agent.services.search.base import SearchProvider


def test_graph_compilation_and_execution() -> None:
    graph = create_internship_graph()
    state = {}
    result = graph.invoke(state)

    assert "queries" in result
    queries = result["queries"]
    assert isinstance(queries, list)
    assert len(queries) > 0
    assert any("PFE" in q for q in queries)


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
