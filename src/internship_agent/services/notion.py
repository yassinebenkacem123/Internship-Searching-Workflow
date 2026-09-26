import logging
from typing import Any

import httpx

from internship_agent.config import get_settings
from internship_agent.models.job import JobOpportunity

logger = logging.getLogger(__name__)

NOTION_VERSION = "2022-06-28"


class NotionSyncService:
    """Service to synchronize normalized internship opportunities with Notion database."""

    def __init__(self, token: str | None = None, database_id: str | None = None) -> None:
        settings = get_settings()
        self.token = token or settings.notion_token
        self.database_id = database_id or settings.notion_database_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    async def get_database_properties(self, client: httpx.AsyncClient) -> dict[str, str]:
        """Fetch existing database property names and their types."""
        url = f"https://api.notion.com/v1/databases/{self.database_id}"
        try:
            resp = await client.get(url, headers=self.headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                props = data.get("properties", {})
                return {name: prop["type"] for name, prop in props.items()}
            logger.warning("Could not fetch Notion database schema (status %d): %s", resp.status_code, resp.text)
        except (httpx.HTTPError, TimeoutError) as exc:
            logger.warning("Error fetching Notion schema: %s", exc)
        return {}

    def _build_properties_payload(self, job: JobOpportunity, schema: dict[str, str], is_new: bool) -> dict[str, Any]:
        """Build properties dictionary matching the Notion database schema."""
        props: dict[str, Any] = {}

        # Locate title property
        title_prop_name = next((k for k, v in schema.items() if v == "title"), "Position")
        props[title_prop_name] = {"title": [{"text": {"content": job.title[:100]}}]}

        def add_rich_text(key: str, val: str | None) -> None:
            if key in schema and schema[key] == "rich_text" and val:
                props[key] = {"rich_text": [{"text": {"content": val[:2000]}}]}

        def add_url(key: str, val: str | None) -> None:
            if key in schema and schema[key] == "url" and val:
                props[key] = {"url": val[:2000]}

        def add_select(key: str, val: str | None) -> None:
            if key in schema and schema[key] == "select" and val:
                props[key] = {"select": {"name": val[:100]}}

        def add_multi_select(key: str, vals: list[str]) -> None:
            if key in schema and schema[key] == "multi_select" and vals:
                # Notion multi_select names cannot contain commas
                clean_vals = [{"name": v.replace(",", " ")[:100]} for v in vals if v]
                if clean_vals:
                    props[key] = {"multi_select": clean_vals[:15]}

        add_rich_text("Company", job.company)
        add_rich_text("Location", job.location)
        add_rich_text("Recruiter", job.recruiter_name)
        add_rich_text("Notes", job.description)

        if "Match Score" in schema and schema["Match Score"] == "number" and job.match_score is not None:
            props["Match Score"] = {"number": job.match_score}

        add_select("Internship Type", job.internship_type)
        add_select("Work Mode", job.work_mode)

        if is_new:
            add_select("Status", "New")

        # Source URLs
        add_url("Main Job Link", job.original_url)
        add_url("LinkedIn Job", job.linkedin_job_url)
        add_url("LinkedIn Post", job.linkedin_post_url)
        add_url("Indeed", job.indeed_url)
        add_url("ReKrute", job.rekrute_url)
        add_url("Company Careers", job.company_careers_url)
        add_url("ATS URL", job.ats_url)
        add_url("Recruiter LinkedIn", job.recruiter_linkedin)

        if "Contact Email" in schema and schema["Contact Email"] == "email" and job.contact_email:
            props["Contact Email"] = {"email": job.contact_email}

        # Multi-selects
        add_multi_select("Required Skills", job.required_skills)
        add_multi_select("Missing Skills", job.missing_skills)
        add_multi_select("Source", job.source_names)

        return props

    async def find_existing_page(self, job: JobOpportunity, client: httpx.AsyncClient) -> str | None:
        """Search Notion database for an existing opportunity matching URL or company+title."""
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        # Check by main job link first if available
        if job.original_url:
            query = {
                "filter": {
                    "property": "Main Job Link",
                    "url": {"equals": job.original_url},
                }
            }
            try:
                resp = await client.post(url, headers=self.headers, json=query, timeout=10.0)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        return results[0]["id"]
            except (httpx.HTTPError, KeyError, IndexError, TimeoutError) as exc:
                logger.debug("Failed querying existing page by URL: %s", exc)

        return None

    async def sync_job(self, job: JobOpportunity, schema: dict[str, str], client: httpx.AsyncClient) -> tuple[JobOpportunity, bool]:
        """Create or update a job in Notion. Returns (job, is_created)."""
        existing_id = await self.find_existing_page(job, client)
        if existing_id:
            # Update existing page without touching user-managed fields like Status
            patch_url = f"https://api.notion.com/v1/pages/{existing_id}"
            payload = {"properties": self._build_properties_payload(job, schema, is_new=False)}
            await client.patch(patch_url, headers=self.headers, json=payload, timeout=10.0)
            job.id = existing_id
            return job, False
        else:
            # Create new page
            create_url = "https://api.notion.com/v1/pages"
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": self._build_properties_payload(job, schema, is_new=True),
            }
            resp = await client.post(create_url, headers=self.headers, json=payload, timeout=10.0)
            if resp.status_code in (200, 201):
                page_id = resp.json().get("id")
                job.id = page_id
            return job, True

    async def sync_jobs(self, jobs: list[JobOpportunity]) -> tuple[list[JobOpportunity], list[JobOpportunity]]:
        """Sync a batch of jobs with Notion. Returns (created_jobs, updated_jobs)."""
        if not self.token or not self.database_id:
            logger.warning("Notion token or database ID missing. Skipping Notion sync.")
            return [], []

        created: list[JobOpportunity] = []
        updated: list[JobOpportunity] = []

        async with httpx.AsyncClient() as client:
            schema = await self.get_database_properties(client)
            for job in jobs:
                try:
                    synced_job, is_new = await self.sync_job(job, schema, client)
                    if is_new:
                        created.append(synced_job)
                    else:
                        updated.append(synced_job)
                except (httpx.HTTPError, TimeoutError, KeyError) as exc:
                    logger.error("Failed to sync job '%s' to Notion: %s", job.title, exc)

        return created, updated
