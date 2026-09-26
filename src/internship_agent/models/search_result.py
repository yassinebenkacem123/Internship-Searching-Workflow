from datetime import datetime

from pydantic import BaseModel


class SearchResult(BaseModel):
    """Represents a raw search result from a search provider."""

    title: str
    url: str
    snippet: str | None = None
    source: str | None = None
    published_date: datetime | str | None = None
