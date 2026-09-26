from datetime import UTC, datetime

from pydantic import BaseModel, Field


class JobOpportunity(BaseModel):
    """Core domain model representing a normalized internship opportunity."""

    id: str | None = None

    title: str
    company: str | None = None

    description: str | None = None
    location: str | None = None
    work_mode: str | None = None
    internship_type: str | None = None

    posted_date: datetime | None = None
    found_date: datetime = Field(default_factory=lambda: datetime.now(UTC))

    source_names: list[str] = Field(default_factory=list)

    original_url: str | None = None
    linkedin_job_url: str | None = None
    linkedin_post_url: str | None = None
    indeed_url: str | None = None
    rekrute_url: str | None = None
    company_careers_url: str | None = None
    ats_url: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    recruiter_name: str | None = None
    recruiter_linkedin: str | None = None
    contact_email: str | None = None

    duration: str | None = None
    deadline: datetime | None = None

    match_score: int | None = Field(default=None, ge=0, le=100)
    match_reasons: list[str] = Field(default_factory=list)

    status: str = "New"
