#!/usr/bin/env python3
"""Dry-run test script for LinkedIn PFE post search, parsing, scoring, and output generation."""

import json
import sys
from pathlib import Path

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Ensure stdout is utf-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from internship_agent.agent.linkedin_pfe_agent import execute_linkedin_pfe_pipeline


def run_dry_run() -> None:
    print("[*] Running LinkedIn PFE Search & Extraction Dry-Run Verification...")
    print("==================================================================\n")

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    test_output_file = str(output_dir / "pfe_leads.json")

    # 1. Sample realistic test posts
    sample_posts = [
        {
            "title": "Offre de Stage PFE: Développeur Full Stack Java / React | TechMaroc",
            "url": "https://www.linkedin.com/posts/techmaroc_pfe-fullstack-casablanca-activity-7123456789",
            "snippet": (
                "TechMaroc recrute des stagiaires PFE pour son pôle ingénierie à Casablanca. "
                "Sujet: Plateforme Cloud microservices en Java, Spring Boot, React, Docker et PostgreSQL. "
                "Stage rémunéré pré-embauche. Envoyez vos CVs à pfe@techmaroc.ma "
                "ou postulez via https://forms.gle/techmarocPFE2025"
            ),
        },
        {
            "title": "Actuellement à la recherche d'un stage PFE | Mon Profil",
            "url": "https://www.linkedin.com/posts/student-seeking-stage-987654",
            "snippet": (
                "Bonjour à tous, je suis étudiant en 5ème année génie informatique. "
                "Je suis activement à la recherche d'un stage PFE de 6 mois à Casablanca ou Rabat. "
                "Looking for an internship. Voici mon CV en pièce jointe."
            ),
        },
        {
            "title": "Offre de Stage PFE DevOps / Cloud | Cloudify Morocco",
            "url": "https://www.linkedin.com/posts/cloudify_pfe-devops-activity-555555",
            "snippet": (
                "Nous cherchons un stagiaire PFE passionné par DevOps, Kubernetes, Terraform et AWS à Rabat. "
                "Travail en mode hybride. Contact direct: rh@cloudify.ma"
            ),
        },
        {
            "title": "Bootcamp intensif Dev Web - Session Payante | IT Training",
            "url": "https://www.linkedin.com/posts/bootcamp-training-1111",
            "snippet": (
                "Rejoignez notre bootcamp dev web de 3 mois pour trouver votre stage PFE! "
                "Tarifs: 4000 DH. Centre de formation certifiante."
            ),
        },
        {
            "title": "Recrutement Développeur Senior CDI | BigCorp",
            "url": "https://www.linkedin.com/posts/bigcorp-senior-cdi",
            "snippet": (
                "Poste en CDI uniquement. 8 ans d'expérience requise. Aucun stage accepté."
            ),
        },
    ]

    print(f"1. Evaluating {len(sample_posts)} candidate LinkedIn feed posts:")
    stats = execute_linkedin_pfe_pipeline(
        query='site:linkedin.com/posts ("stage PFE" OR "sujet PFE") Morocco',
        output_file=test_output_file,
        search_results_override=sample_posts,
    )

    print(f"   • Total evaluated:      {stats['evaluated_posts_count']}")
    print(f"   • Rejected (non-PFE/student/bootcamp): {stats['rejected_false_positives_or_low_score']}")
    print(f"   • Qualified Leads saved:{stats['saved_leads_count']}")
    print(f"   • Duplicates skipped:   {stats['duplicate_leads_skipped']}\n")

    # 2. Inspect generated JSON file
    assert Path(test_output_file).exists(), "Output file was not generated!"
    with open(test_output_file, "r", encoding="utf-8") as f:
        leads = json.load(f)

    print(f"2. Verifying saved file content in {test_output_file}:")
    print(f"   • Total leads in file: {len(leads)}")
    for i, lead in enumerate(leads, 1):
        print(f"\n   Lead #{i}:")
        print(f"     Title:        {lead['title']}")
        print(f"     Company:      {lead.get('company')}")
        print(f"     Location:     {lead.get('location')} ({lead.get('work_type')})")
        print(f"     Skills:       {', '.join(lead.get('required_skills', []))}")
        print(f"     Score:        {lead['match_score']}/100")
        print(f"     Email:        {lead.get('contact_email') or 'None'}")
        print(f"     Apply Link:   {lead.get('apply_link') or 'None'}")
        print(f"     Post URL:     {lead['post_url']}")
        print(f"     Rationale:    {'; '.join(lead.get('match_rationale', []))}")

    # 3. Test Deduplication
    print("\n3. Testing Deduplication Logic:")
    print("   Attempting to re-save the exact same leads...")
    stats_repeat = execute_linkedin_pfe_pipeline(
        query='site:linkedin.com/posts ("stage PFE" OR "sujet PFE") Morocco',
        output_file=test_output_file,
        search_results_override=sample_posts,
    )
    print(f"   • Newly saved on repeat:   {stats_repeat['saved_leads_count']} (expected: 0)")
    print(f"   • Duplicates detected:     {stats_repeat['duplicate_leads_skipped']} (expected: >= 2)")

    assert stats_repeat["saved_leads_count"] == 0, "Duplicate leads were incorrectly saved!"
    print("\n[+] Verification Successful: All tests and assertions passed!\n")


if __name__ == "__main__":
    run_dry_run()
