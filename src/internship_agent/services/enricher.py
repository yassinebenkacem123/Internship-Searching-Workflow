import json
import logging
import re

import httpx

from internship_agent.config import get_settings
from internship_agent.models.job import JobOpportunity

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

COMMON_SKILLS = [
    "Java", "Spring Boot", "Python", "React", "Next.js", "Node.js", "Docker",
    "Kubernetes", "PostgreSQL", "MySQL", "MongoDB", "AWS", "Azure", "GCP",
    "DevOps", "CI/CD", "Git", "Terraform", "Linux", "AI", "Machine Learning",
    "LLM", "RAG", "FastAPI", "Django", "TypeScript", "JavaScript", "C++", "C#"
]


def extract_deterministic_skills(text: str) -> list[str]:
    """Extract skills deterministically using word boundaries."""
    found: list[str] = []
    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)
    return found


async def enrich_job_with_ollama(job: JobOpportunity, client: httpx.AsyncClient) -> JobOpportunity:
    """Enrich job description with structured skills and recruiter details using Ollama."""
    settings = get_settings()
    combined_text = f"Title: {job.title}\nCompany: {job.company or 'Unknown'}\nDescription: {job.description or ''}"

    # Extract email deterministically
    email_match = EMAIL_REGEX.search(combined_text)
    if email_match and not job.contact_email:
        job.contact_email = email_match.group(0)

    # Initial deterministic skills
    det_skills = extract_deterministic_skills(combined_text)
    job.required_skills = list(set(job.required_skills + det_skills))

    # Attempt Ollama extraction
    endpoint = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    prompt = (
        "You are an assistant extracting structured technical internship information. "
        "Return ONLY a valid JSON object with keys: "
        "'skills' (list of strings), 'recruiter_name' (string or null), 'contact_email' (string or null). "
        "Do not invent or hallucinate information. If unknown, use null.\n\n"
        f"Job posting text:\n{combined_text[:1200]}"
    )

    try:
        response = await client.post(
            endpoint,
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            raw_response = data.get("response", "{}")
            extracted = json.loads(raw_response)

            extracted_skills = extracted.get("skills", [])
            if isinstance(extracted_skills, list):
                job.required_skills = list(set(job.required_skills + [s for s in extracted_skills if isinstance(s, str)]))

            recruiter = extracted.get("recruiter_name")
            if recruiter and isinstance(recruiter, str) and not job.recruiter_name:
                job.recruiter_name = recruiter.strip()

            email = extracted.get("contact_email")
            if email and isinstance(email, str) and not job.contact_email:
                job.contact_email = email.strip()
    except (httpx.HTTPError, json.JSONDecodeError, TimeoutError, KeyError) as exc:
        # Fall back silently so offline Ollama does not block the workflow
        logger.debug("Ollama enrichment skipped or timed out: %s", exc)

    return job


async def enrich_jobs(jobs: list[JobOpportunity]) -> list[JobOpportunity]:
    """Enrich list of jobs with skills, contact details, and metadata."""
    async with httpx.AsyncClient() as client:
        enriched = []
        for job in jobs:
            enriched_job = await enrich_job_with_ollama(job, client)
            enriched.append(enriched_job)
        return enriched
