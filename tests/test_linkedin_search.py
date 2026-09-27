"""Unit and integration tests for LinkedIn PFE Search, Extraction, and Persistence."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from internship_agent.agent.linkedin_pfe_agent import execute_linkedin_pfe_pipeline
from internship_agent.tools.linkedin_search import (
    PFELead,
    analyze_and_filter_post,
    fetch_post_details,
    save_pfe_lead,
    search_linkedin_posts,
)


def test_search_linkedin_posts_query_and_recency(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test query formulation and time filter mapping for LinkedIn post search."""
    monkeypatch.setenv("TAVILY_API_KEY", "mock_key")

    with patch("tavily.TavilyClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        mock_instance.search.return_value = {
            "results": [
                {
                    "title": "Stage PFE Fullstack | LinkedIn",
                    "url": "https://www.linkedin.com/posts/acme_stage-pfe-fullstack-activity-12345",
                    "content": "Offre de stage PFE Java Spring Boot à Casablanca. Contact: hr@acme.ma",
                }
            ]
        }

        # 1. Test standard search with recency past_week
        results = search_linkedin_posts(query="PFE Java Morocco", time_filter="past_week")
        assert len(results) == 1
        assert "linkedin.com/posts" in results[0]["url"]
        assert results[0]["title"] == "Stage PFE Fullstack | LinkedIn"

        # Verify search args passed to Tavily
        mock_instance.search.assert_called_once()
        _args, kwargs = mock_instance.search.call_args
        assert kwargs["time_range"] == "week"
        assert "site:linkedin.com/posts" in kwargs["query"]

        # 2. Test 24h filter
        mock_instance.search.reset_mock()
        search_linkedin_posts(query="PFE DevOps", time_filter="past_24h")
        _args2, kwargs2 = mock_instance.search.call_args
        assert kwargs2["time_range"] == "day"


def test_fetch_post_details_html_cleaning_and_links() -> None:
    """Test HTML parsing, script removal, link extraction, and timestamp handling."""
    mock_html = """
    <html>
        <head><title>LinkedIn Post</title></head>
        <body>
            <script>console.log("analytics");</script>
            <style>body { background: white; }</style>
            <time datetime="2026-02-15T10:00:00Z">15 Feb 2026</time>
            <p>Offre de stage PFE Développeur Backend chez InovTech.</p>
            <p>Postulez sur https://forms.gle/xyzPFE123 ou par mail rh@inovtech.ma</p>
            <a href="https://external-careers.com/job/1">Lien carrières</a>
        </body>
    </html>
    """

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = mock_html
        mock_get.return_value = mock_resp

        data = fetch_post_details("https://www.linkedin.com/posts/inovtech_pfe-activity-999")

        assert data["status_code"] == 200
        assert "console.log" not in data["raw_text"]
        assert "Offre de stage PFE Développeur Backend" in data["raw_text"]
        assert data["timestamp"] == "2026-02-15T10:00:00Z"
        assert "https://forms.gle/xyzPFE123" in data["links"]
        assert "https://external-careers.com/job/1" in data["links"]


def test_fetch_post_details_error_handling() -> None:
    """Ensure HTTP errors or exceptions do not crash post fetching."""
    with patch("requests.get", side_effect=requests.RequestException("Network timeout")):
        data = fetch_post_details("https://www.linkedin.com/posts/unavailable")
        assert data["raw_text"] == ""
        assert "Network timeout" in data.get("error", "")


def test_analyze_and_filter_rejects_student_seeking_internship() -> None:
    """Ensure student job-seeker posts are rejected as false positives."""
    title = "Actuellement en recherche d'un stage PFE | LinkedIn"
    text = (
        "Bonjour le réseau, je suis élève-ingénieur en dernière année à l'ENSIAS. "
        "Je suis activement à la recherche d'un stage PFE de 6 mois dans le domaine du génie logiciel. "
        "Voici mon profil et mon CV. Looking for an internship!"
    )
    result = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/student_post-1",
        title=title,
        content=text,
    )
    assert result is None


def test_analyze_and_filter_rejects_bootcamp_ad() -> None:
    """Ensure bootcamp and paid courses are rejected."""
    title = "Rejoignez notre bootcamp dev web | LinkedIn"
    text = (
        "Centre de formation organise un bootcamp intensif en développement web pour décrocher votre stage PFE. "
        "Tarif: 3500 DH. Session payante débutant le mois prochain. Inscrivez-vous à notre formation."
    )
    result = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/bootcamp-1",
        title=title,
        content=text,
    )
    assert result is None


def test_analyze_and_filter_rejects_cdi_senior() -> None:
    """Ensure CDI roles requiring senior experience without internship are rejected."""
    title = "Recrutement Senior Lead Developer | LinkedIn"
    text = (
        "Nous recrutons un Lead Developer avec 7 ans d'expérience. "
        "Poste en CDI uniquement. Aucun stage accepté."
    )
    result = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/senior-cdi",
        title=title,
        content=text,
    )
    assert result is None


def test_analyze_and_filter_accepts_valid_pfe_and_extracts_cleanly() -> None:
    """Test true positive PFE post with zero email hallucination and accurate scoring."""
    title = "Offre de Stage PFE: Fullstack Java / React | InovTech"
    text = (
        "Nous recrutons pour notre filiale à Casablanca des stagiaires PFE Développeurs Fullstack. "
        "Technologies: Java, Spring Boot, React, Docker, et PostgreSQL. "
        "Travail en mode hybride. Envoyez vos candidatures à recrutement@inovtech.ma "
        "ou postulez via https://forms.gle/samplePFE2025"
    )

    lead = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/inovtech_pfe-offer-2025",
        title=title,
        content=text,
    )

    assert lead is not None
    assert isinstance(lead, PFELead)
    assert lead.match_score >= 60
    assert "Java" in lead.required_skills
    assert "Spring Boot" in lead.required_skills
    assert "Docker" in lead.required_skills
    assert lead.location == "Casablanca"
    assert lead.work_type == "Hybrid"
    assert lead.contact_email == "recrutement@inovtech.ma"
    assert lead.apply_link == "https://forms.gle/samplePFE2025"


def test_analyze_and_filter_no_hallucination_when_email_missing() -> None:
    """Ensure that if no email exists, contact_email remains None (no hallucination)."""
    title = "Sujet PFE: Ingénieur Logiciel & IA / LLM | TechCorp"
    text = (
        "Nous recherchons des stagiaires PFE développeurs en AI, LLM et RAG pour des projets innovants à Rabat. "
        "Consultez les détails sur notre page entreprise."
    )

    lead = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/techcorp-ai-pfe",
        title=title,
        content=text,
    )

    assert lead is not None
    assert lead.contact_email is None  # Must NOT hallucinate an email
    assert lead.match_score >= 60
    assert "AI" in lead.required_skills
    assert "LLM" in lead.required_skills


def test_analyze_and_filter_rejects_below_score_threshold() -> None:
    """Ensure posts with score < 60 are filtered out."""
    title = "Stage PFE Marketing et Communication"
    text = "Offre de stage PFE en communication digitale et réseaux sociaux à Casablanca."
    result = analyze_and_filter_post(
        post_url="https://www.linkedin.com/posts/marketing-pfe",
        title=title,
        content=text,
    )
    assert result is None


def test_save_pfe_lead_validation_and_deduplication(tmp_path: Path) -> None:
    """Test persisting leads into a JSON file, deduplication by post_url, and file schema."""
    output_file = str(tmp_path / "leads" / "pfe_leads.json")

    lead_data = {
        "title": "Stage PFE DevOps",
        "company": "CloudMaroc",
        "location": "Casablanca",
        "work_type": "On-site",
        "required_skills": ["DevOps", "Docker", "Kubernetes"],
        "contact_email": "jobs@cloudmaroc.com",
        "apply_link": "https://cloudmaroc.com/careers/pfe",
        "post_url": "https://www.linkedin.com/posts/cloudmaroc-devops-pfe-123",
        "match_score": 85,
        "match_rationale": ["+30 PFE", "+15 DevOps", "+5 Docker"],
    }

    # 1. First save must succeed
    assert save_pfe_lead(lead_data, output_file=output_file) is True
    assert Path(output_file).exists()

    with open(output_file, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert len(saved) == 1
    assert saved[0]["post_url"] == lead_data["post_url"]
    assert saved[0]["company"] == "CloudMaroc"

    # 2. Duplicate save with the exact same post_url must return False and not duplicate
    assert save_pfe_lead(lead_data, output_file=output_file) is False

    with open(output_file, "r", encoding="utf-8") as f:
        saved2 = json.load(f)
    assert len(saved2) == 1


def test_execute_linkedin_pfe_pipeline_end_to_end(tmp_path: Path) -> None:
    """Test full execution pipeline with mocked search items and lead generation."""
    output_file = str(tmp_path / "pfe_leads.json")

    mock_search_results = [
        # Legitimate PFE Offer
        {
            "title": "Stage PFE Software Engineer | Casablanca",
            "url": "https://www.linkedin.com/posts/company-pfe-post-1",
            "snippet": "Nous recrutons des stagiaires PFE en Java et Spring Boot à Casablanca. Envoyez CV à rh@company.ma",
        },
        # Student seeking stage -> should be rejected
        {
            "title": "À la recherche d'un stage PFE | LinkedIn",
            "url": "https://www.linkedin.com/posts/student-seeking-stage-2",
            "snippet": "Actuellement en recherche d'un stage PFE de 6 mois. Mon profil est disponible...",
        },
    ]

    with patch("internship_agent.agent.linkedin_pfe_agent.fetch_post_details") as mock_fetch:
        mock_fetch.return_value = {
            "post_url": "https://www.linkedin.com/posts/company-pfe-post-1",
            "raw_text": "Nous recrutons des stagiaires PFE en Java et Spring Boot à Casablanca. Envoyez CV à rh@company.ma",
            "timestamp": "2026-03-01",
            "links": [],
        }

        stats = execute_linkedin_pfe_pipeline(
            query="Stage PFE",
            output_file=output_file,
            search_results_override=mock_search_results,
        )

        assert stats["searched_posts_count"] == 2
        assert stats["evaluated_posts_count"] == 2
        assert stats["rejected_false_positives_or_low_score"] == 1
        assert stats["saved_leads_count"] == 1

        # Check persisted file
        with open(output_file, "r", encoding="utf-8") as f:
            leads = json.load(f)
        assert len(leads) == 1
        assert leads[0]["post_url"] == "https://www.linkedin.com/posts/company-pfe-post-1"
        assert leads[0]["contact_email"] == "rh@company.ma"
