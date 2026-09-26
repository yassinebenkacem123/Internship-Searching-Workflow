from internship_agent.models.search_result import SearchResult
from internship_agent.services.normalizer import (
    classify_url,
    extract_location,
    extract_title_and_company,
    normalize_search_result,
)


def test_classify_url_sources() -> None:
    linkedin_job = classify_url("https://www.linkedin.com/jobs/view/123456")
    assert linkedin_job["linkedin_job_url"] == "https://www.linkedin.com/jobs/view/123456"

    linkedin_post = classify_url("https://www.linkedin.com/posts/recruiter_pfe-activity-789")
    assert linkedin_post["linkedin_post_url"] == "https://www.linkedin.com/posts/recruiter_pfe-activity-789"

    indeed = classify_url("https://ma.indeed.com/viewjob?jk=abc123")
    assert indeed["indeed_url"] == "https://ma.indeed.com/viewjob?jk=abc123"

    rekrute = classify_url("https://www.rekrute.com/offre-emploi-stage-pfe-101.html")
    assert rekrute["rekrute_url"] == "https://www.rekrute.com/offre-emploi-stage-pfe-101.html"

    ats_greenhouse = classify_url("https://boards.greenhouse.io/mycompany/jobs/999")
    assert ats_greenhouse["ats_url"] == "https://boards.greenhouse.io/mycompany/jobs/999"

    ats_lever = classify_url("https://jobs.lever.co/company/888")
    assert ats_lever["ats_url"] == "https://jobs.lever.co/company/888"

    careers = classify_url("https://careers.google.com/jobs/results/777")
    assert careers["company_careers_url"] == "https://careers.google.com/jobs/results/777"


def test_extract_title_and_company() -> None:
    title, company = extract_title_and_company("Software Engineer Intern - Capgemini | LinkedIn")
    assert title == "Software Engineer Intern"
    assert company == "Capgemini"

    title2, company2 = extract_title_and_company("Stage PFE Développeur chez OCP Group")
    assert title2 == "Stage PFE Développeur"
    assert company2 == "OCP Group"


def test_extract_location() -> None:
    assert extract_location("Stage PFE basé à Casablanca") == "Casablanca"
    assert extract_location("Opportunité à Rabat pour étudiants") == "Rabat"
    assert extract_location("Remote position in Morocco") == "Remote"


def test_normalize_search_result() -> None:
    raw = SearchResult(
        title="PFE Java Spring Boot Developer - Atos | LinkedIn",
        url="https://www.linkedin.com/jobs/view/456",
        snippet="Nous recherchons un stagiaire PFE Java Spring Boot à Casablanca.",
        source="tavily",
    )
    job = normalize_search_result(raw)

    assert job.title == "PFE Java Spring Boot Developer"
    assert job.company == "Atos"
    assert job.location == "Casablanca"
    assert job.internship_type == "PFE"
    assert job.linkedin_job_url == "https://www.linkedin.com/jobs/view/456"
    assert "LinkedIn Jobs" in job.source_names
