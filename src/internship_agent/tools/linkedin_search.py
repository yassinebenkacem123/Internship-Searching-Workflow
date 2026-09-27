"""LinkedIn PFE Internship Post Search, Extraction, and Persistence Tools."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError

from internship_agent.config import get_settings

logger = logging.getLogger(__name__)


class PFELead(BaseModel):
    """Pydantic schema for validated and scored PFE internship leads."""

    title: str
    company: str | None = None
    location: str | None = None
    work_type: str | None = None  # e.g., On-site, Hybrid, Remote
    required_skills: list[str] = Field(default_factory=list)
    contact_email: str | None = None
    apply_link: str | None = None
    post_url: str
    match_score: int = Field(ge=0, le=100)
    match_rationale: list[str] = Field(default_factory=list)


def search_linkedin_posts(
    query: str = '("stage PFE" OR "PFE 2025" OR "sujet PFE") ("Software" OR "Fullstack" OR "DevOps" OR "IA")',
    time_filter: str = "past_week",
    max_results: int = 25,
) -> list[dict[str, str]]:
    """Execute targeted search queries targeting LinkedIn posts with recency filtering.

    Args:
        query: Search keywords or query string.
        time_filter: Time window for recency ('past_24h', 'past_week', 'day', 'week').
        max_results: Maximum search results to request from search provider (default: 25).

    Returns:
        Structured list of dicts with keys 'url', 'title', and 'snippet'.
    """
    settings = get_settings()
    api_key = settings.effective_tavily_key or os.environ.get("TAVILY_API_KEY")

    # Ensure site:linkedin.com/posts is included in the query
    clean_query = query.strip()
    if "site:linkedin.com" not in clean_query.lower():
        clean_query = f"site:linkedin.com/posts {clean_query}"

    # Map time_filter to Tavily time_range
    time_filter_lower = time_filter.lower()
    if time_filter_lower in ("past_24h", "24h", "day"):
        tavily_time_range = "day"
    else:
        tavily_time_range = "week"

    if not api_key:
        logger.warning("No Tavily API key found; search_linkedin_posts returning empty list.")
        return []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=clean_query,
            time_range=tavily_time_range,
            max_results=max_results,
            search_depth="basic",
        )
        raw_results = response.get("results", [])

        structured: list[dict[str, str]] = []
        for item in raw_results:
            url = item.get("url", "")
            # Verify URL belongs to LinkedIn posts or updates
            if "linkedin.com" in url:
                structured.append({
                    "url": url,
                    "title": item.get("title", ""),
                    "snippet": item.get("content") or item.get("snippet", ""),
                })
        return structured

    except Exception:
        logger.exception("Error executing search_linkedin_posts with query: %s", clean_query)
        return []


def fetch_post_details(post_url: str) -> dict[str, Any]:
    """Retrieve and clean the text of a LinkedIn post or webpage.

    Extracts raw text, potential timestamp metadata, and application/contact links.
    Handles HTTP errors, timeouts, and rate limits gracefully.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        response = requests.get(post_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning("HTTP %s when fetching post details from %s", response.status_code, post_url)
            return {
                "post_url": post_url,
                "raw_text": "",
                "timestamp": None,
                "links": [],
                "status_code": response.status_code,
            }

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Strip scripts, styles, svg, and non-content elements
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
            tag.decompose()

        # Extract text content
        raw_text = soup.get_text(separator="\n", strip=True)

        # Attempt to extract timestamp
        timestamp = None
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            timestamp = time_tag["datetime"]
        elif time_tag:
            timestamp = time_tag.get_text(strip=True)
        else:
            meta_time = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "date"})
            if meta_time and meta_time.get("content"):
                timestamp = meta_time["content"]

        # Extract external links from anchors
        extracted_links: list[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if (
                href.startswith("http")
                and "linkedin.com" not in href
                and not href.endswith((".png", ".jpg", ".jpeg", ".svg", ".css", ".js"))
            ):
                extracted_links.append(href)

        # Also search for text-based apply URLs (e.g., forms.gle, bit.ly, etc.)
        form_links = re.findall(
            r"https?://(?:forms\.gle|bit\.ly|docs\.google\.com/forms|forms\.office\.com|[\w-]+\.workable\.com)[^\s)\]]+",
            raw_text,
        )
        for fl in form_links:
            if fl not in extracted_links:
                extracted_links.append(fl)

        return {
            "post_url": post_url,
            "raw_text": raw_text,
            "timestamp": timestamp,
            "links": list(dict.fromkeys(extracted_links)),  # unique preserve order
            "status_code": 200,
        }

    except requests.RequestException as exc:
        logger.warning("Request failed for %s: %s", post_url, exc)
        return {
            "post_url": post_url,
            "raw_text": "",
            "timestamp": None,
            "links": [],
            "error": str(exc),
        }


def analyze_and_filter_post(
    post_url: str,
    title: str,
    content: str,
    links: list[str] | None = None,
    min_score: int = 60,
) -> PFELead | None:
    """Analyze a LinkedIn post, reject false positives, extract details, and score.

    System Rules Applied:
    1. Rejects false positives:
       - Students looking for internships ('cherche stage', 'à la recherche de', 'open to work', etc.)
       - General CDI/CDD only without internship context ('CDI uniquement', 5+ years experience)
       - Bootcamp or paid training advertisements ('formation payante', 'bootcamp', 'tarifs')
    2. Scores candidate posts on a 0-100 scale (filters out anything below min_score, default 60).
    3. Never hallucinates contact emails or URLs (leaves them None if not found in text/links).
    """
    links = links or []
    full_text = f"{title}\n{content}"
    text_lower = full_text.lower()

    # Rule 1.1: Reject student internship-seekers (candidates looking for internships)
    student_seeking_patterns = [
        r"\b(à la recherche|a la recherche|en recherche|en quête)\s+d['’](un\s+)?(stage|pfe)\b",
        r"\b(je\s+suis\s+(à\s+la\s+|a\s+la\s+)?recherche|je\s+cherche)\s+d['’]?(un\s+)?(stage|pfe|opportunité)\b",
        r"\b(étudiant|etudiant|élève-ingénieur|futur diplômé)\s+.*?\b(cherche|en quête|recherche)\b",
        r"\blooking\s+for\s+(a\s+)?(pfe|final\s+year|internship|intern)\b",
        r"\bseeking\s+(an?\s+)?(internship|pfe|opportunity)\b",
        r"\b(actively\s+seeking|open\s+to\s+work|hire\s+me)\b",
    ]
    hiring_keywords = [
        r"nous\s+recrutons",
        r"nous\s+recherchons",
        r"recrutement",
        r"offre\s+de\s+stage",
        r"sujet\s+pfe",
        r"stagiaire\s+pfe",
        r"we\s+are\s+hiring",
        r"join\s+our\s+team",
        r"postulez",
        r"envoyez\s+vos\s+cv",
        r"envoyez\s+votre\s+cv",
    ]
    is_seeking = any(re.search(pat, text_lower) for pat in student_seeking_patterns)
    has_hiring_indicator = any(re.search(kw, text_lower) for kw in hiring_keywords)
    if is_seeking and not has_hiring_indicator:
        logger.debug("Filtered out: Student seeking internship: %s", title)
        return None

    # Rule 1.2: Reject bootcamp and paid training advertisements
    bootcamp_patterns = [
        r"\bbootcamp\b",
        r"\bcentre\s+de\s+formation\b",
        r"\bformation\s+(certifiante|professionnelle|payante)\b",
        r"\btarifs?\s*:\s*\d+",
        r"\binscrivez-vous\s+à\s+notre\s+formation\b",
    ]
    if any(re.search(pat, text_lower) for pat in bootcamp_patterns):
        logger.debug("Filtered out: Bootcamp/training advertisement: %s", title)
        return None

    # Rule 1.3: Reject CDI only / excessive experience
    cdi_only_patterns = [
        r"\b(cdi\s+uniquement|aucun\s+stage|pas\s+de\s+stage|non\s+ouvert\s+aux\s+stages)\b",
        r"\b(5\+|6\+|7\+|8\+|9\+|10\+)\s*(ans|years)\b",
    ]
    if any(re.search(pat, text_lower) for pat in cdi_only_patterns):
        logger.debug("Filtered out: CDI only or senior requirements: %s", title)
        return None

    # Must contain an explicit internship or PFE intent
    internship_markers = [
        r"\bpfe\b",
        r"stage",
        r"internship",
        r"intern",
        r"stagiaire",
        r"fin\s+d['’]études",
        r"final\s+year",
    ]
    if not any(re.search(pat, text_lower) for pat in internship_markers):
        logger.debug("Filtered out: No internship markers in post: %s", title)
        return None

    # Rule 2: Strictly extract contact email without hallucination
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b", full_text)
    contact_email = email_match.group(0).lower() if email_match else None

    # Extract apply link if explicitly present in text or provided links
    apply_link = None
    form_match = re.search(
        r"https?://(?:forms\.gle|bit\.ly|docs\.google\.com/forms|forms\.office\.com|[\w-]+\.workable\.com)[^\s)\]]+",
        full_text,
    )
    if form_match:
        apply_link = form_match.group(0)
    elif links:
        apply_link = links[0]

    # Detect skills
    skills_catalog = {
        "Java": r"\bjava\b",
        "Spring Boot": r"\bspring\s*boot\b",
        "Python": r"\bpython\b",
        "React": r"\breact(?:\.js)?\b",
        "Next.js": r"\bnext(?:\.js)?\b",
        "Node.js": r"\bnode(?:\.js)?\b",
        "TypeScript": r"\btypescript\b",
        "Docker": r"\bdocker\b",
        "Kubernetes": r"\bkubernetes\b|\bk8s\b",
        "DevOps": r"\bdevops\b",
        "Cloud": r"\bcloud\b|\baws\b|\bazure\b|\bgcp\b",
        "AI": r"\bai\b|intelligence\s+artificielle|artificial\s+intelligence",
        "Machine Learning": r"\bmachine\s+learning\b|\bml\b",
        "LLM": r"\bllm\b|large\s+language\s+model",
        "RAG": r"\brag\b|retrieval\s+augmented",
        "PostgreSQL": r"\bpostgresql\b|\bpostgres\b",
    }
    extracted_skills: list[str] = [
        name for name, pattern in skills_catalog.items() if re.search(pattern, text_lower)
    ]

    # Location detection
    locations_map = {
        "Casablanca": r"\bcasablanca\b|\bcasa\b",
        "Rabat": r"\brabat\b",
        "Marrakech": r"\bmarrakech\b",
        "Tanger": r"\btanger\b|\btangier\b",
        "Fès": r"\bf[èe]s\b",
        "Agadir": r"\bagadir\b",
        "Morocco": r"\bmaroc\b|\bmorocco\b",
    }
    detected_location = None
    for loc_name, pat in locations_map.items():
        if re.search(pat, text_lower):
            detected_location = loc_name
            break

    # Work type detection
    work_type = "On-site"
    if re.search(r"\b(remote|télétravail|teletravail|à distance)\b", text_lower):
        work_type = "Remote"
    elif re.search(r"\b(hybride|hybrid)\b", text_lower):
        work_type = "Hybrid"

    # Company name estimation from title or text
    company_name = None
    comp_match = re.search(r"(?:chez|at|recrute\s+pour)\s+([A-Z][A-Za-z0-9&.\-_ ]{2,25})", full_text)
    if comp_match:
        company_name = comp_match.group(1).strip()
    elif " | " in title:
        parts = title.split(" | ")
        if len(parts) >= 2 and "linkedin" not in parts[0].lower():
            company_name = parts[0].strip()

    # Rule 3: Deterministic Match Scoring (0-100 scale)
    score = 0
    rationale: list[str] = []

    # +30 Explicit PFE / final-year internship
    if re.search(r"\b(pfe|fin d['’]études|final year)\b", text_lower):
        score += 30
        rationale.append("+30: Explicit PFE / final-year internship opportunity")

    # +20 Java / Spring Boot
    if "Java" in extracted_skills or "Spring Boot" in extracted_skills:
        score += 20
        rationale.append("+20: Involves Java / Spring Boot")

    # +15 Backend / Software Engineering
    if re.search(r"\b(backend|software|développeur|developpeur|ingénieur)\b", text_lower):
        score += 15
        rationale.append("+15: Software Engineering / Backend scope")

    # +15 AI / LLM / RAG / Machine Learning
    if any(s in extracted_skills for s in ("AI", "Machine Learning", "LLM", "RAG")):
        score += 15
        rationale.append("+15: Modern AI / LLM / ML topics")

    # +15 DevOps / Cloud / Containerization
    if any(s in extracted_skills for s in ("DevOps", "Docker", "Kubernetes", "Cloud")):
        score += 15
        rationale.append("+15: DevOps, Cloud, or Containerization skills")

    # +10 React / Next.js
    if "React" in extracted_skills or "Next.js" in extracted_skills:
        score += 10
        rationale.append("+10: Modern React / Next.js frontend")

    # +5 PostgreSQL / DB
    if "PostgreSQL" in extracted_skills:
        score += 5
        rationale.append("+5: PostgreSQL database")

    final_score = max(0, min(score, 100))

    # Reject posts below min_score (default 60)
    if final_score < min_score:
        logger.debug("Filtered out: Score %s < %s for post %s", final_score, min_score, title)
        return None

    # Derive clean title
    lead_title = title.split(" | ")[0].strip() if " | " in title else title.strip()
    if not lead_title:
        lead_title = "PFE Internship Opportunity"

    return PFELead(
        title=lead_title,
        company=company_name,
        location=detected_location or "Morocco",
        work_type=work_type,
        required_skills=extracted_skills,
        contact_email=contact_email,
        apply_link=apply_link,
        post_url=post_url,
        match_score=final_score,
        match_rationale=rationale,
    )


def save_pfe_lead(lead_data: dict[str, Any], output_file: str = "output/pfe_leads.json") -> bool:
    """Validate data against PFELead schema, deduplicate by post_url, and append to output file.

    Args:
        lead_data: Dictionary representation of the PFE lead.
        output_file: Target JSON file path (defaults to output/pfe_leads.json).

    Returns:
        True if the lead was newly saved; False if validation failed or post_url was already saved.
    """
    try:
        lead = PFELead.model_validate(lead_data)
    except ValidationError as err:
        logger.error("Validation error saving PFE lead: %s", err)
        return False

    file_path = Path(output_file)
    existing_leads: list[dict[str, Any]] = []

    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_leads = json.loads(content)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read existing file %s, initializing fresh list: %s", output_file, exc)
            existing_leads = []

    # Deduplicate strictly by post_url
    seen_urls = {
        item.get("post_url") for item in existing_leads if isinstance(item, dict) and item.get("post_url")
    }
    if lead.post_url in seen_urls:
        logger.info("Duplicate post_url already exists in %s: %s", output_file, lead.post_url)
        return False

    existing_leads.append(lead.model_dump())

    # Ensure output directory exists and write JSON
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_leads, f, indent=2, ensure_ascii=False)

    logger.info("Successfully saved PFE lead: '%s' (%s) -> %s", lead.title, lead.post_url, output_file)
    return True
