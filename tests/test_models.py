from datetime import datetime

import pytest
from pydantic import ValidationError

from internship_agent.models.candidate import CandidateProfile
from internship_agent.models.job import JobOpportunity
from internship_agent.models.search_result import SearchResult


def test_search_result_instantiation() -> None:
    result = SearchResult(
        title="PFE Software Engineer",
        url="https://example.com/job/1",
        snippet="Looking for a PFE intern...",
        source="linkedin_jobs",
    )
    assert result.title == "PFE Software Engineer"
    assert result.url == "https://example.com/job/1"
    assert result.snippet == "Looking for a PFE intern..."
    assert result.source == "linkedin_jobs"
    assert result.published_date is None


def test_job_opportunity_can_be_instantiated() -> None:
    job = JobOpportunity(
        title="Full Stack Developer PFE",
        company="Tech Corp",
        location="Casablanca",
        internship_type="PFE",
    )
    assert job.title == "Full Stack Developer PFE"
    assert job.company == "Tech Corp"
    assert job.location == "Casablanca"
    assert job.internship_type == "PFE"
    assert job.status == "New"
    assert isinstance(job.found_date, datetime)


def test_job_opportunity_mutable_fields_are_not_shared() -> None:
    job1 = JobOpportunity(title="Job 1")
    job2 = JobOpportunity(title="Job 2")

    job1.source_names.append("linkedin")
    job1.required_skills.append("Python")
    job1.preferred_skills.append("Docker")
    job1.missing_skills.append("Kubernetes")
    job1.match_reasons.append("PFE keyword match")

    assert job2.source_names == []
    assert job2.required_skills == []
    assert job2.preferred_skills == []
    assert job2.missing_skills == []
    assert job2.match_reasons == []


def test_job_opportunity_score_validation() -> None:
    valid_job_0 = JobOpportunity(title="Job", match_score=0)
    valid_job_50 = JobOpportunity(title="Job", match_score=50)
    valid_job_100 = JobOpportunity(title="Job", match_score=100)

    assert valid_job_0.match_score == 0
    assert valid_job_50.match_score == 50
    assert valid_job_100.match_score == 100

    with pytest.raises(ValidationError):
        JobOpportunity(title="Job", match_score=-1)

    with pytest.raises(ValidationError):
        JobOpportunity(title="Job", match_score=101)


def test_job_opportunity_source_urls() -> None:
    job = JobOpportunity(
        title="Software Engineer Intern",
        original_url="https://example.com/original",
        linkedin_job_url="https://linkedin.com/jobs/view/123",
        linkedin_post_url="https://linkedin.com/feed/update/urn:li:activity:456",
        indeed_url="https://indeed.com/viewjob?jk=789",
        rekrute_url="https://rekrute.com/offre/101",
        company_careers_url="https://company.com/careers/pfe",
        ats_url="https://boards.greenhouse.io/company/jobs/202",
    )
    assert job.original_url == "https://example.com/original"
    assert job.linkedin_job_url == "https://linkedin.com/jobs/view/123"
    assert job.linkedin_post_url == "https://linkedin.com/feed/update/urn:li:activity:456"
    assert job.indeed_url == "https://indeed.com/viewjob?jk=789"
    assert job.rekrute_url == "https://rekrute.com/offre/101"
    assert job.company_careers_url == "https://company.com/careers/pfe"
    assert job.ats_url == "https://boards.greenhouse.io/company/jobs/202"


def test_candidate_profile_defaults() -> None:
    profile = CandidateProfile()
    assert "Software Engineer" in profile.target_roles
    assert "Backend Engineer" in profile.target_roles
    assert "Full Stack Developer" in profile.target_roles
    assert "DevOps Engineer" in profile.target_roles
    assert "AI Engineer" in profile.target_roles

    assert "Java" in profile.skills.high_priority
    assert "Spring Boot" in profile.skills.high_priority
    assert "PostgreSQL" in profile.skills.high_priority
    assert "Docker" in profile.skills.high_priority

    assert "React" in profile.skills.medium_priority
    assert "Kubernetes" in profile.skills.medium_priority
    assert "Python" in profile.skills.medium_priority
    assert "AI" in profile.skills.medium_priority
    assert "LLM" in profile.skills.medium_priority
