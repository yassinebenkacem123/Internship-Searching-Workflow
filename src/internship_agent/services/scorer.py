import re

from internship_agent.config import get_settings
from internship_agent.models.candidate import CandidateProfile
from internship_agent.models.job import JobOpportunity


def score_job_opportunity(job: JobOpportunity, candidate: CandidateProfile | None = None) -> JobOpportunity:
    """Calculate an explainable 0-100 match score against the candidate profile."""
    if candidate is None:
        candidate = get_settings().candidate

    text = f"{job.title} {job.description or ''} {' '.join(job.required_skills)}".lower()

    score = 0
    reasons: list[str] = []

    # +30 Explicit PFE / final-year internship
    if job.internship_type == "PFE" or re.search(r"\b(pfe|fin d['’]études|final year|end of stud)\b", text):
        score += 30
        reasons.append("+30: Explicit PFE / final-year internship")

    # +20 Java / Spring Boot
    if re.search(r"\b(java|spring boot|springboot)\b", text):
        score += 20
        reasons.append("+20: Java / Spring Boot")

    # +15 Backend / Software Engineering
    if re.search(r"\b(backend|software engineer|software developer|développeur)\b", text):
        score += 15
        reasons.append("+15: Backend / Software Engineering")

    # +15 AI / LLM / RAG / Machine Learning
    if re.search(r"\b(ai|artificial intelligence|intelligence artificielle|machine learning|llm|rag)\b", text):
        score += 15
        reasons.append("+15: AI / LLM / RAG")

    # +15 DevOps / Cloud / Kubernetes / Terraform
    if re.search(r"\b(devops|cloud|kubernetes|terraform|ci/cd)\b", text):
        score += 15
        reasons.append("+15: DevOps / Cloud")

    # +10 React / Next.js
    if re.search(r"\b(react|next\.?js)\b", text):
        score += 10
        reasons.append("+10: React / Next.js")

    # +5 PostgreSQL
    if re.search(r"\b(postgresql|postgres)\b", text):
        score += 5
        reasons.append("+5: PostgreSQL")

    # +5 Docker
    if re.search(r"\bdocker\b", text):
        score += 5
        reasons.append("+5: Docker")

    # Negative factors
    if re.search(r"\b(5\+?|6\+?|7\+?|8\+?|9\+?|10\+?)\s*(years|ans)\b", text):
        score -= 40
        reasons.append("-40: Substantial professional experience required")

    if re.search(r"\b(cdi uniquement|pas de stage|aucun stage)\b", text):
        score -= 40
        reasons.append("-40: Full-time / CDI only")

    # Clamp score to [0, 100]
    final_score = max(0, min(score, 100))
    job.match_score = final_score
    job.match_reasons = reasons

    # Compute missing skills against candidate profile
    candidate_skills = set(candidate.skills.high_priority + candidate.skills.medium_priority)
    job_skills_lower = {s.lower() for s in job.required_skills}

    missing: list[str] = []
    for skill in candidate_skills:
        if skill.lower() not in job_skills_lower and re.search(r"\b" + re.escape(skill) + r"\b", text):
            # Not missing, it's mentioned
            pass
        elif skill.lower() not in job_skills_lower:
            missing.append(skill)

    job.missing_skills = missing[:5]  # Keep top 5 missing skills concise

    return job


def score_jobs(jobs: list[JobOpportunity]) -> list[JobOpportunity]:
    """Score a list of jobs against candidate profile and sort descending by score."""
    scored = [score_job_opportunity(j) for j in jobs]
    return sorted(scored, key=lambda x: (x.match_score or 0), reverse=True)
