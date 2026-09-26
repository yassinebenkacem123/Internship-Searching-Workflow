from internship_agent.models.job import JobOpportunity
from internship_agent.services.deduplicator import deduplicate_jobs


def test_deduplicate_same_company_and_title_merges_urls() -> None:
    job1 = JobOpportunity(
        title="Software Engineer PFE",
        company="Oracle Morocco",
        linkedin_job_url="https://linkedin.com/jobs/view/111",
        source_names=["LinkedIn Jobs"],
        original_url="https://linkedin.com/jobs/view/111",
    )
    job2 = JobOpportunity(
        title="PFE Software Engineer",
        company="Oracle",
        indeed_url="https://indeed.com/viewjob?jk=222",
        source_names=["Indeed"],
        original_url="https://indeed.com/viewjob?jk=222",
    )

    deduped = deduplicate_jobs([job1, job2])
    assert len(deduped) == 1

    merged = deduped[0]
    assert merged.linkedin_job_url == "https://linkedin.com/jobs/view/111"
    assert merged.indeed_url == "https://indeed.com/viewjob?jk=222"
    assert "LinkedIn Jobs" in merged.source_names
    assert "Indeed" in merged.source_names


def test_deduplicate_keeps_distinct_roles_separate() -> None:
    job_backend = JobOpportunity(
        title="Backend Engineer PFE",
        company="Capgemini",
        location="Casablanca",
        original_url="https://example.com/backend",
    )
    job_frontend = JobOpportunity(
        title="Frontend React PFE",
        company="Capgemini",
        location="Casablanca",
        original_url="https://example.com/frontend",
    )

    deduped = deduplicate_jobs([job_backend, job_frontend])
    assert len(deduped) == 2
