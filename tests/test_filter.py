from internship_agent.models.job import JobOpportunity
from internship_agent.services.filter import is_relevant_job


def test_filter_valid_pfe_role() -> None:
    job = JobOpportunity(
        title="Stage PFE Développeur Full Stack",
        company="Tech Co",
        location="Casablanca",
        description="Stage fin d'études en Java, React et Docker.",
    )
    assert is_relevant_job(job) is True


def test_filter_rejects_cdi_only() -> None:
    job = JobOpportunity(
        title="Software Engineer",
        company="Corp",
        description="Poste en CDI uniquement, aucun stage accepté. Expérience requise.",
    )
    assert is_relevant_job(job) is False


def test_filter_rejects_senior_roles() -> None:
    job = JobOpportunity(
        title="Senior Lead Developer",
        company="Corp",
        description="Nous cherchons un profil avec 7+ ans d'expérience. PFE non éligible.",
    )
    assert is_relevant_job(job) is False


def test_filter_rejects_unrelated_domain() -> None:
    job = JobOpportunity(
        title="Stage Stagiaire Comptable",
        company="Finance Group",
        description="Stage en comptabilité et gestion administrative.",
    )
    assert is_relevant_job(job) is False
