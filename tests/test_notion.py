

import pytest

from internship_agent.models.job import JobOpportunity
from internship_agent.services.notion import NotionSyncService


@pytest.mark.asyncio
async def test_notion_payload_generation() -> None:
    service = NotionSyncService(token="fake_token", database_id="fake_db")
    schema = {
        "Position": "title",
        "Company": "rich_text",
        "Location": "rich_text",
        "Match Score": "number",
        "Status": "select",
        "Main Job Link": "url",
        "LinkedIn Job": "url",
        "Required Skills": "multi_select",
    }

    job = JobOpportunity(
        title="PFE Java Engineer",
        company="Capgemini",
        location="Casablanca",
        match_score=90,
        original_url="https://example.com/job",
        linkedin_job_url="https://linkedin.com/jobs/view/1",
        required_skills=["Java", "Spring Boot"],
    )

    payload = service._build_properties_payload(job, schema, is_new=True)

    assert payload["Position"]["title"][0]["text"]["content"] == "PFE Java Engineer"
    assert payload["Company"]["rich_text"][0]["text"]["content"] == "Capgemini"
    assert payload["Location"]["rich_text"][0]["text"]["content"] == "Casablanca"
    assert payload["Match Score"]["number"] == 90
    assert payload["Status"]["select"]["name"] == "New"
    assert payload["Main Job Link"]["url"] == "https://example.com/job"
    assert payload["LinkedIn Job"]["url"] == "https://linkedin.com/jobs/view/1"
    assert any(s["name"] == "Java" for s in payload["Required Skills"]["multi_select"])


@pytest.mark.asyncio
async def test_notion_does_not_overwrite_status_on_update() -> None:
    service = NotionSyncService(token="fake_token", database_id="fake_db")
    schema = {
        "Position": "title",
        "Status": "select",
        "LinkedIn Post": "url",
    }
    job = JobOpportunity(
        title="PFE DevOps",
        linkedin_post_url="https://linkedin.com/posts/xyz",
    )

    payload = service._build_properties_payload(job, schema, is_new=False)
    # When updating an existing job, Status must NOT be set so user decisions are preserved
    assert "Status" not in payload
    assert payload["LinkedIn Post"]["url"] == "https://linkedin.com/posts/xyz"
