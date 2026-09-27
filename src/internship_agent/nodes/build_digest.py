from internship_agent.services.digest import generate_daily_digest
from internship_agent.state import InternshipSearchState
from internship_agent.tools.linkedin_search import save_pfe_lead


def build_digest_node(state: InternshipSearchState) -> dict[str, str]:
    """LangGraph node to compile the daily digest from discovered and scored jobs."""
    jobs = state.get("scored_jobs", [])

    # Automatically persist verified high-scoring PFE leads (score >= 60)
    for job in jobs:
        target_url = job.linkedin_post_url or job.linkedin_job_url or job.original_url
        if (job.match_score or 0) >= 60 and target_url:
            save_pfe_lead({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_type": job.work_mode,
                "required_skills": job.required_skills,
                "contact_email": job.contact_email,
                "apply_link": target_url,
                "post_url": target_url,
                "match_score": job.match_score or 0,
                "match_rationale": job.match_reasons,
            })

    digest = generate_daily_digest(created_jobs=jobs)
    return {"digest": digest}
