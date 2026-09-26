from pydantic import BaseModel, Field


class CandidateSkills(BaseModel):
    """Priority skills for internship matching."""

    high_priority: list[str] = Field(
        default_factory=lambda: [
            "Java",
            "Spring Boot",
            "PostgreSQL",
            "Docker",
        ]
    )
    medium_priority: list[str] = Field(
        default_factory=lambda: [
            "React",
            "Kubernetes",
            "Python",
            "AI",
            "LLM",
        ]
    )


class CandidateProfile(BaseModel):
    """Candidate profile containing target roles and prioritized skills."""

    target_roles: list[str] = Field(
        default_factory=lambda: [
            "Software Engineer",
            "Backend Engineer",
            "Full Stack Developer",
            "DevOps Engineer",
            "AI Engineer",
        ]
    )
    skills: CandidateSkills = Field(default_factory=CandidateSkills)
