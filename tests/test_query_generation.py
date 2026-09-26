from internship_agent.models.candidate import CandidateProfile
from internship_agent.services.query_generator import generate_search_queries


def test_generates_pfe_queries() -> None:
    queries = generate_search_queries()
    assert len(queries) > 0
    pfe_queries = [q for q in queries if "PFE" in q]
    assert len(pfe_queries) > 0


def test_generates_english_queries() -> None:
    queries = generate_search_queries()
    english_queries = [
        q for q in queries if "Software Engineer" in q or "final year internship" in q
    ]
    assert len(english_queries) > 0
    assert any('"PFE" "Software Engineer" Morocco' in q for q in queries)
    assert any('"final year internship" software Morocco' in q for q in queries)


def test_generates_french_queries() -> None:
    queries = generate_search_queries()
    french_queries = [
        q
        for q in queries
        if "stage fin d'études" in q or "stage PFE" in q or "développeur" in q or "Maroc" in q
    ]
    assert len(french_queries) > 0
    assert any("développeur Maroc" in q for q in queries)
    assert any("DevOps Maroc" in q for q in queries)


def test_generates_linkedin_jobs_query() -> None:
    queries = generate_search_queries()
    linkedin_jobs = [q for q in queries if "site:linkedin.com/jobs" in q]
    assert len(linkedin_jobs) > 0
    assert 'site:linkedin.com/jobs "PFE" Morocco' in queries


def test_generates_linkedin_posts_query() -> None:
    queries = generate_search_queries()
    linkedin_posts = [q for q in queries if "site:linkedin.com/posts" in q]
    assert len(linkedin_posts) > 0
    assert 'site:linkedin.com/posts "PFE" Morocco' in queries


def test_generates_indeed_query() -> None:
    queries = generate_search_queries()
    indeed_queries = [q for q in queries if "site:indeed.com" in q]
    assert len(indeed_queries) > 0
    assert 'site:indeed.com "PFE" Morocco software' in queries


def test_generates_rekrute_query() -> None:
    queries = generate_search_queries()
    rekrute_queries = [q for q in queries if "site:rekrute.com" in q]
    assert len(rekrute_queries) > 0
    assert 'site:rekrute.com "PFE" informatique' in queries


def test_does_not_contain_duplicates() -> None:
    queries = generate_search_queries()
    assert len(queries) == len(set(queries))

    # Test with candidate profile passed
    candidate = CandidateProfile()
    queries_with_candidate = generate_search_queries(candidate=candidate)
    assert len(queries_with_candidate) == len(set(queries_with_candidate))
