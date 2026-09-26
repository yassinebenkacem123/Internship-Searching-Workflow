from internship_agent.models.job import JobOpportunity


def generate_daily_digest(
    created_jobs: list[JobOpportunity],
    updated_jobs: list[JobOpportunity] | None = None,
) -> str:
    """Generate a clean, readable text digest of newly discovered internship opportunities."""
    if updated_jobs is None:
        updated_jobs = []

    total_new = len(created_jobs)
    if total_new == 0 and not updated_jobs:
        return "🔍 No new PFE internship opportunities found today."

    lines: list[str] = [
        f"🔥 {total_new} new PFE opportunit{'y' if total_new == 1 else 'ies'} discovered in Morocco!\n"
    ]

    # Sort new jobs by match score descending
    sorted_new = sorted(created_jobs, key=lambda j: j.match_score or 0, reverse=True)

    for idx, job in enumerate(sorted_new[:10], start=1):
        score_str = f"{job.match_score}/100" if job.match_score is not None else "N/A"
        company = job.company or "Company not specified"
        location = job.location or "Morocco (or Remote)"

        lines.append(f"{idx}. {job.title} — {company}")
        lines.append(f"   📍 {location} | 🎯 Match: {score_str}")

        if job.required_skills:
            lines.append(f"   🛠️ Skills: {', '.join(job.required_skills[:5])}")

        # Primary link
        link = (
            job.linkedin_job_url
            or job.linkedin_post_url
            or job.indeed_url
            or job.rekrute_url
            or job.company_careers_url
            or job.ats_url
            or job.original_url
        )
        if link:
            lines.append(f"   🔗 Link: {link}")

        lines.append("")

    if updated_jobs:
        lines.append(f"ℹ️ {len(updated_jobs)} existing opportunit{'y was' if len(updated_jobs) == 1 else 'ies were'} updated with new sources.")

    return "\n".join(lines).strip()
