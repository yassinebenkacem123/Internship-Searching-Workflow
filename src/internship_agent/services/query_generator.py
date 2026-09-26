from internship_agent.models.candidate import CandidateProfile

# Curated deterministic category queries
BASE_CATEGORY_QUERIES: list[str] = [
    # Software Engineering
    '"PFE" "Software Engineer" Morocco',
    '"PFE" "Software Developer" Morocco',
    '"final year internship" software Morocco',
    '"stage fin d\'études" développeur Maroc',
    # Backend
    '"PFE" "Backend Engineer" Morocco',
    '"PFE" "Backend Developer" Morocco',
    '"stage fin d\'études" backend Maroc',
    # Java / Spring Boot
    '"PFE" "Java" "Spring Boot" Morocco',
    '"stage PFE" Java Maroc',
    # Full Stack
    '"PFE" "Full Stack" Morocco',
    '"stage fin d\'études" full stack Maroc',
    # DevOps
    '"PFE" DevOps Morocco',
    '"stage fin d\'études" DevOps Maroc',
    # Cloud
    '"PFE" Cloud Morocco',
    '"PFE" Docker Kubernetes Morocco',
    # AI / ML
    '"PFE" AI Morocco',
    '"PFE" "Machine Learning" Morocco',
    '"stage fin d\'études" intelligence artificielle Maroc',
    # LLM / RAG
    '"PFE" LLM Morocco',
    '"PFE" RAG Morocco',
]

SOURCE_SPECIFIC_QUERIES: list[str] = [
    # LinkedIn Jobs
    'site:linkedin.com/jobs "PFE" Morocco',
    'site:linkedin.com/jobs "Software Engineer Intern" Morocco',
    # LinkedIn Posts
    'site:linkedin.com/posts "PFE" Morocco',
    'site:linkedin.com/posts "stage PFE" "Java" Maroc',
    'site:linkedin.com/posts "stage fin d\'études" DevOps Maroc',
    # Indeed
    'site:indeed.com "PFE" Morocco software',
    # ReKrute
    'site:rekrute.com "PFE" informatique',
]


def generate_search_queries(candidate: CandidateProfile | None = None) -> list[str]:
    """Generate a deterministic, deduplicated list of internship search queries.

    Queries cover target technical domains, English/French variations for Moroccan
    PFE/internship terminology, and site-specific search footprints.
    """
    raw_queries: list[str] = list(BASE_CATEGORY_QUERIES)

    if candidate:
        for role in candidate.target_roles:
            raw_queries.append(f'"PFE" "{role}" Morocco')
        for skill in candidate.skills.high_priority:
            raw_queries.append(f'"PFE" "{skill}" Morocco')

    raw_queries.extend(SOURCE_SPECIFIC_QUERIES)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_queries: list[str] = []
    for query in raw_queries:
        normalized = query.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_queries.append(normalized)

    return unique_queries
