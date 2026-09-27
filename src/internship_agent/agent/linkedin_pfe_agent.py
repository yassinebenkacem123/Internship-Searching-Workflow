"""Autonomous LinkedIn PFE Internship Post Search and Extraction Agent."""

import asyncio
import logging
from typing import Any

from internship_agent.tools.linkedin_search import (
    analyze_and_filter_post,
    fetch_post_details,
    save_pfe_lead,
    search_linkedin_posts,
)

logger = logging.getLogger(__name__)

LINKEDIN_PFE_SYSTEM_PROMPT = """You are an autonomous PFE (Projet de Fin d'Études) Internship Discovery Agent for Morocco.
Your objective is to discover, fetch, validate, score, and persist genuine, high-quality PFE internship opportunities from LinkedIn posts.

Operational Guidelines:
1. Strict False Positive Filtering:
   - Instantly reject posts published by students seeking internships (e.g., 'à la recherche d'un stage', 'seeking an internship', 'mon cv').
   - Instantly reject CDI, CDD, or freelance postings that do not offer internships or require 5+ years of experience.
   - Instantly reject bootcamp, training center, or course advertisements ('formation payante', 'bootcamp', 'tarifs').
2. Explainable Match Scoring:
   - Score posts on a 0-100 scale based on PFE relevance, candidate tech stack (Java/Spring Boot, Full Stack, DevOps/Cloud, AI/LLM/RAG).
   - Filter out and do NOT persist any posting scoring below 60.
3. Grounded Extraction (Zero Hallucination):
   - Extract contact emails only when an explicit email address appears in the post.
   - Extract application links only when valid URLs (Google Forms, career links, application portals) are in the text.
   - Never fabricate, guess, or hallucinate contact emails or application links. Leave them empty if not present.
4. Persistence & Deduplication:
   - Validate against the PFELead schema and save to output/pfe_leads.json without duplicating post URLs.
"""


def execute_linkedin_pfe_pipeline(
    query: str = '("stage PFE" OR "PFE 2025" OR "sujet PFE") ("Software" OR "Fullstack" OR "DevOps" OR "IA")',
    time_filter: str = "past_week",
    output_file: str = "output/pfe_leads.json",
    min_score: int = 60,
    search_results_override: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Synchronous pipeline orchestrating LinkedIn PFE discovery, extraction, scoring, and saving."""
    logger.info("Starting LinkedIn PFE Discovery with query: '%s' (window: %s)", query, time_filter)

    # Step 1: Search LinkedIn posts (or use override for testing/mocking)
    if search_results_override is not None:
        posts = search_results_override
    else:
        posts = search_linkedin_posts(query=query, time_filter=time_filter)

    stats = {
        "searched_posts_count": len(posts),
        "evaluated_posts_count": 0,
        "rejected_false_positives_or_low_score": 0,
        "saved_leads_count": 0,
        "duplicate_leads_skipped": 0,
        "saved_leads": [],
    }

    # Step 2: Iterate over candidate posts
    for post in posts:
        stats["evaluated_posts_count"] += 1
        url = post.get("url", "")
        title = post.get("title", "")
        snippet = post.get("snippet", "")

        # Fetch full post details if available
        details = fetch_post_details(url)
        content_text = details.get("raw_text") or snippet
        external_links = details.get("links", [])

        # Step 3: Analyze, filter false positives, score (reject < min_score)
        lead = analyze_and_filter_post(
            post_url=url,
            title=title,
            content=content_text,
            links=external_links,
            min_score=min_score,
        )

        if lead is None:
            stats["rejected_false_positives_or_low_score"] += 1
            continue

        # Step 4: Validate and save lead
        saved = save_pfe_lead(lead.model_dump(), output_file=output_file)
        if saved:
            stats["saved_leads_count"] += 1
            stats["saved_leads"].append(lead.model_dump())
        else:
            stats["duplicate_leads_skipped"] += 1

    return stats


async def run_linkedin_pfe_agent(
    query: str = '("stage PFE" OR "PFE 2025" OR "sujet PFE") ("Software" OR "Fullstack" OR "DevOps" OR "IA")',
    time_filter: str = "past_week",
    output_file: str = "output/pfe_leads.json",
    min_score: int = 60,
) -> dict[str, Any]:
    """Asynchronous wrapper for LinkedIn PFE Agent execution."""
    return await asyncio.to_thread(
        execute_linkedin_pfe_pipeline,
        query=query,
        time_filter=time_filter,
        output_file=output_file,
        min_score=min_score,
    )
