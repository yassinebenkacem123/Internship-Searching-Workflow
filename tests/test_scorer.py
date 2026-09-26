from internship_agent.models.candidate import CandidateProfile
from internship_agent.models.job import JobOpportunity
from internship_agent.services.scorer import score_job_opportunity


def test_scorer_awards_points_for_pfe_and_priority_skills() -> None:
    job = JobOpportunity(
        title="Stage PFE Backend Java Spring Boot",
        company="Tech Corp",
        description="PFE internship focusing on Java, Spring Boot, PostgreSQL and Docker.",
        internship_type="PFE",
    )

    scored = score_job_opportunity(job)
    assert scored.match_score is not None
    assert scored.match_score >= 70
    assert any("Explicit PFE" in r for r in scored.match_reasons)
    assert any("Java / Spring Boot" in r for r in scored.match_reasons)


def test_scorer_applies_penalties_and_clamps() -> None:
    job = JobOpportunity(
        title="Software Engineer",
        description="CDI uniquement. 10 ans d'expérience requise. Pas de stage.",
        internship_type="CDI",
    )

    scored = score_job_opportunity(job)
    assert scored.match_score == 0  # Clamped to 0
    assert any("-40: Full-time / CDI only" in r for r in scored.match_reasons)
    assert any("-40: Substantial professional experience" in r for r in scored.match_reasons)


def test_scorer_identifies_missing_skills() -> None:
    candidate = CandidateProfile()
    job = JobOpportunity(
        title="PFE Java Developer",
        description="PFE stage with Java and Docker.",
        internship_type="PFE",
        required_skills=["Java", "Docker"],
    )

    scored = score_job_opportunity(job, candidate=candidate)
    assert "Spring Boot" in scored.missing_skills or "PostgreSQL" in scored.missing_skills
