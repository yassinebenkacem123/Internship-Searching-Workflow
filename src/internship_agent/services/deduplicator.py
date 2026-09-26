import re

from internship_agent.models.job import JobOpportunity


def normalize_string(text: str | None) -> str:
    """Normalize text for consistent duplicate detection."""
    if not text:
        return ""
    # Lowercase, replace punctuation with spaces, collapse multiple spaces
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(cleaned.split())


def create_job_fingerprint(job: JobOpportunity) -> str:
    """Create a unique deterministic fingerprint for matching duplicate job postings."""
    norm_title = normalize_string(job.title)
    # Remove generic filler words from title
    norm_title = re.sub(r"\b(stage|pfe|internship|intern|stagiaire|maroc|morocco)\b", "", norm_title)
    norm_title = " ".join(norm_title.split())

    norm_company = normalize_string(job.company)
    # Remove corporate suffixes
    norm_company = re.sub(r"\b(sarl|sa|inc|corp|group|groupe|maroc|morocco)\b", "", norm_company)
    norm_company = " ".join(norm_company.split())

    return f"{norm_company}::{norm_title}"


def merge_job_opportunities(primary: JobOpportunity, secondary: JobOpportunity) -> JobOpportunity:
    """Merge source URLs, skills, and details from secondary into primary without losing information."""
    primary.linkedin_job_url = primary.linkedin_job_url or secondary.linkedin_job_url
    primary.linkedin_post_url = primary.linkedin_post_url or secondary.linkedin_post_url
    primary.indeed_url = primary.indeed_url or secondary.indeed_url
    primary.rekrute_url = primary.rekrute_url or secondary.rekrute_url
    primary.company_careers_url = primary.company_careers_url or secondary.company_careers_url
    primary.ats_url = primary.ats_url or secondary.ats_url
    primary.original_url = primary.original_url or secondary.original_url

    # Merge source names
    all_sources = list(primary.source_names)
    for s in secondary.source_names:
        if s not in all_sources:
            all_sources.append(s)
    primary.source_names = all_sources

    # Keep description if primary is empty
    if not primary.description and secondary.description:
        primary.description = secondary.description

    # Keep location if primary is empty
    if not primary.location and secondary.location:
        primary.location = secondary.location

    # Keep recruiter info if primary is empty
    primary.recruiter_name = primary.recruiter_name or secondary.recruiter_name
    primary.recruiter_linkedin = primary.recruiter_linkedin or secondary.recruiter_linkedin
    primary.contact_email = primary.contact_email or secondary.contact_email

    return primary


def deduplicate_jobs(jobs: list[JobOpportunity]) -> list[JobOpportunity]:
    """Deduplicate job opportunities, merging multiple source URLs into single records."""
    fingerprint_map: dict[str, JobOpportunity] = {}
    url_map: dict[str, JobOpportunity] = {}

    deduped: list[JobOpportunity] = []

    for job in jobs:
        # Check canonical/original URL match
        matched_job: JobOpportunity | None = None
        if job.original_url and job.original_url in url_map:
            matched_job = url_map[job.original_url]

        fp = create_job_fingerprint(job)
        if not matched_job and fp in fingerprint_map and job.company:
            matched_job = fingerprint_map[fp]

        if matched_job:
            merge_job_opportunities(matched_job, job)
            if job.original_url:
                url_map[job.original_url] = matched_job
        else:
            fingerprint_map[fp] = job
            if job.original_url:
                url_map[job.original_url] = job
            deduped.append(job)

    return deduped
