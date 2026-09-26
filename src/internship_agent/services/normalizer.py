import re
from urllib.parse import urlparse

from internship_agent.models.job import JobOpportunity
from internship_agent.models.search_result import SearchResult


def classify_url(url: str) -> dict[str, str | None]:
    """Classify a job URL into specific source platform categories."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()

    mapping: dict[str, str | None] = {
        "linkedin_job_url": None,
        "linkedin_post_url": None,
        "indeed_url": None,
        "rekrute_url": None,
        "company_careers_url": None,
        "ats_url": None,
        "original_url": url,
    }

    if "linkedin.com" in netloc:
        if "/jobs" in path:
            mapping["linkedin_job_url"] = url
        elif "/posts" in path or "/feed" in path:
            mapping["linkedin_post_url"] = url
        else:
            mapping["original_url"] = url
    elif "indeed." in netloc:
        mapping["indeed_url"] = url
    elif "rekrute.com" in netloc:
        mapping["rekrute_url"] = url
    elif any(ats in netloc for ats in ["greenhouse.io", "lever.co", "workday", "smartrecruiters.com", "myworkdayjobs.com"]):
        mapping["ats_url"] = url
    elif "careers" in netloc or "careers" in path or "jobs" in path:
        mapping["company_careers_url"] = url

    return mapping


def extract_title_and_company(raw_title: str) -> tuple[str, str | None]:
    """Extract a cleaned position title and company name from a search result title."""
    clean = re.sub(r"\s*\|\s*(LinkedIn|Indeed|ReKrute|Rekrute).*", "", raw_title, flags=re.IGNORECASE)
    clean = re.sub(r"^[A-Za-z0-9_]+:\s*", "", clean)  # e.g. "Indeed: ..."

    delimiters = [" - ", " chez ", " at ", " @ "]
    for delim in delimiters:
        if delim in clean:
            parts = clean.split(delim, 1)
            title = parts[0].strip()
            company = parts[1].strip()
            # Clean trailing company artifacts
            company = re.sub(r"\s*\(.*\)", "", company).strip()
            return title, company or None

    return clean.strip(), None


def extract_location(text: str) -> str | None:
    """Detect prominent Moroccan cities or Remote mode in text."""
    cities = [
        "Remote",
        "Télétravail",
        "Casablanca",
        "Rabat",
        "Marrakech",
        "Tangier",
        "Tanger",
        "Fes",
        "Fès",
        "Agadir",
        "Kenitra",
        "Kénitra",
        "Sale",
        "Salé",
        "Morocco",
        "Maroc",
    ]
    for city in cities:
        if re.search(r"\b" + re.escape(city) + r"\b", text, flags=re.IGNORECASE):
            return city.capitalize()
    return None


def normalize_search_result(result: SearchResult) -> JobOpportunity:
    """Convert a raw SearchResult into a normalized JobOpportunity."""
    title, company = extract_title_and_company(result.title)
    url_sources = classify_url(result.url)

    combined_text = f"{result.title} {result.snippet or ''}"
    location = extract_location(combined_text)

    is_pfe = bool(re.search(r"\b(pfe|fin d['’]études|end of stud)\b", combined_text, flags=re.IGNORECASE))
    internship_type = "PFE" if is_pfe else "Internship"

    source_names = []
    if url_sources["linkedin_job_url"]:
        source_names.append("LinkedIn Jobs")
    if url_sources["linkedin_post_url"]:
        source_names.append("LinkedIn Posts")
    if url_sources["indeed_url"]:
        source_names.append("Indeed")
    if url_sources["rekrute_url"]:
        source_names.append("ReKrute")
    if url_sources["ats_url"]:
        source_names.append("ATS")
    if url_sources["company_careers_url"]:
        source_names.append("Company Careers")
    if not source_names and result.source:
        source_names.append(result.source)

    return JobOpportunity(
        title=title or result.title,
        company=company,
        description=result.snippet,
        location=location,
        internship_type=internship_type,
        source_names=source_names,
        original_url=result.url,
        linkedin_job_url=url_sources["linkedin_job_url"],
        linkedin_post_url=url_sources["linkedin_post_url"],
        indeed_url=url_sources["indeed_url"],
        rekrute_url=url_sources["rekrute_url"],
        company_careers_url=url_sources["company_careers_url"],
        ats_url=url_sources["ats_url"],
        status="New",
    )
