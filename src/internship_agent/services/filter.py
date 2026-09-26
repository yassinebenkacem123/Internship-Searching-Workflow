import re

from internship_agent.models.job import JobOpportunity

INTERNSHIP_TERMS = [
    r"\bpfe\b",
    r"stage\s+pfe",
    r"stage\s+de\s+fin\s+d['’]études",
    r"stage\s+fin\s+d['’]études",
    r"final\s+year\s+internship",
    r"end[- ]of[- ]stud(y|ies)\s+internship",
    r"\binternship\b",
    r"\bintern\b",
    r"\bstagiaire\b",
    r"\bstage\b",
]

TECHNICAL_TERMS = [
    r"software\s+engineer",
    r"software\s+developer",
    r"développeur",
    r"developpeur",
    r"\bbackend\b",
    r"\bfrontend\b",
    r"full\s*stack",
    r"web\s+developer",
    r"\bjava\b",
    r"spring\s+boot",
    r"\breact\b",
    r"next\.?js",
    r"node\.?js",
    r"\bpython\b",
    r"\bai\b",
    r"artificial\s+intelligence",
    r"intelligence\s+artificielle",
    r"machine\s+learning",
    r"\bllm\b",
    r"\brag\b",
    r"\bdevops\b",
    r"\bcloud\b",
    r"\bdocker\b",
    r"\bkubernetes\b",
    r"\bterraform\b",
    r"\binformatique\b",
]

NEGATIVE_TERMS = [
    r"\b(5\+?|6\+?|7\+?|8\+?|9\+?|10\+?)\s+ans\b",
    r"\b(5\+?|6\+?|7\+?|8\+?|9\+?|10\+?)\s+years\b",
    r"pas\s+de\s+stage",
    r"aucun\s+stage",
    r"non\s+ouvert\s+aux\s+stages",
    r"\bcomptable\b",
    r"\binfirmier\b",
    r"\bplombier\b",
    r"\bmédical\b",
    r"\bgénie\s+civil\b",
]


def is_relevant_job(job: JobOpportunity) -> bool:
    """Determine if a job opportunity represents a valid technical PFE/internship in Morocco/Remote."""
    combined_text = f"{job.title} {job.company or ''} {job.location or ''} {job.description or ''}".lower()

    # Reject on strong negative terms
    for neg in NEGATIVE_TERMS:
        if re.search(neg, combined_text, flags=re.IGNORECASE):
            return False

    # Check positive internship intent
    has_internship = any(re.search(term, combined_text, flags=re.IGNORECASE) for term in INTERNSHIP_TERMS)
    if not has_internship:
        return False

    # Check technical relevance
    return any(re.search(term, combined_text, flags=re.IGNORECASE) for term in TECHNICAL_TERMS)


def filter_jobs(jobs: list[JobOpportunity]) -> list[JobOpportunity]:
    """Filter list of JobOpportunities down to only relevant opportunities."""
    return [job for job in jobs if is_relevant_job(job)]
