from internship_agent.models.job import JobOpportunity
from internship_agent.services.digest import generate_daily_digest


def test_generate_daily_digest_empty() -> None:
    digest = generate_daily_digest([])
    assert "No new PFE internship opportunities found today" in digest


def test_generate_daily_digest_with_jobs() -> None:
    job = JobOpportunity(
        title="AI Engineer PFE",
        company="Morocco AI Lab",
        location="Rabat",
        match_score=95,
        required_skills=["Python", "LLM", "RAG"],
        linkedin_job_url="https://linkedin.com/jobs/view/123",
    )

    digest = generate_daily_digest([job])
    assert "1 new PFE opportunity discovered" in digest
    assert "AI Engineer PFE — Morocco AI Lab" in digest
    assert "Match: 95/100" in digest
    assert "Python, LLM, RAG" in digest
    assert "https://linkedin.com/jobs/view/123" in digest
