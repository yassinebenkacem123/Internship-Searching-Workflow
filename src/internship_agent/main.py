import argparse
import asyncio

from internship_agent.agent.linkedin_pfe_agent import run_linkedin_pfe_agent
from internship_agent.graph import create_internship_graph


async def run_pipeline() -> None:
    """Execute the end-to-end internship discovery graph and report results."""
    print("🚀 Morocco PFE Internship Discovery Agent (Graph Workflow)")
    print("=========================================================\n")

    graph = create_internship_graph()
    result = await graph.ainvoke({})

    queries = result.get("queries", [])
    raw_results = result.get("raw_results", [])
    normalized = result.get("normalized_jobs", [])
    filtered = result.get("filtered_jobs", [])
    deduped = result.get("deduplicated_jobs", [])
    scored = result.get("scored_jobs", [])
    digest = result.get("digest", "")

    print("📊 Workflow Execution Summary:")
    print(f"  • Queries generated:   {len(queries)}")
    print(f"  • Raw results fetched: {len(raw_results)}")
    print(f"  • Normalized jobs:     {len(normalized)}")
    print(f"  • Qualified PFE jobs:  {len(filtered)}")
    print(f"  • Deduplicated jobs:   {len(deduped)}")
    print(f"  • Scored opportunities:{len(scored)}\n")

    if digest:
        print("📋 Daily Digest:")
        print("----------------")
        print(digest)
        print("----------------\n")


async def run_linkedin_mode(query: str, time_filter: str, output: str) -> None:
    """Execute the dedicated LinkedIn PFE post search and extraction agent."""
    print("🎯 Autonomous LinkedIn PFE Post Search & Extraction Agent")
    print("=========================================================\n")
    print(f"🔎 Query: {query}")
    print(f"⏳ Recency: {time_filter}")
    print(f"💾 Output file: {output}\n")

    stats = await run_linkedin_pfe_agent(query=query, time_filter=time_filter, output_file=output)

    print("📊 LinkedIn Post Discovery Results:")
    print(f"  • Posts found:              {stats['searched_posts_count']}")
    print(f"  • Posts evaluated:          {stats['evaluated_posts_count']}")
    print(f"  • Rejected (false positive/low score): {stats['rejected_false_positives_or_low_score']}")
    print(f"  • Newly saved leads:        {stats['saved_leads_count']}")
    print(f"  • Duplicate leads skipped:  {stats['duplicate_leads_skipped']}")
    print(f"  • File saved to:            {output}\n")


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Morocco PFE Internship Discovery Agent")
    parser.add_argument(
        "--mode",
        choices=["graph", "linkedin-posts", "all"],
        default="graph",
        help="Execution mode: 'graph' (default workflow), 'linkedin-posts' (feed post search), or 'all'",
    )
    parser.add_argument(
        "--query",
        default='("stage PFE" OR "PFE 2025" OR "sujet PFE") ("Software" OR "Fullstack" OR "DevOps" OR "IA")',
        help="Search query for LinkedIn post discovery",
    )
    parser.add_argument(
        "--time-filter",
        default="past_week",
        choices=["past_24h", "past_week", "day", "week"],
        help="Recency filter for search results",
    )
    parser.add_argument(
        "--output",
        default="output/pfe_leads.json",
        help="Destination path for saving verified PFE leads",
    )

    args = parser.parse_args()

    if args.mode == "linkedin-posts":
        asyncio.run(run_linkedin_mode(query=args.query, time_filter=args.time_filter, output=args.output))
    elif args.mode == "all":
        asyncio.run(run_linkedin_mode(query=args.query, time_filter=args.time_filter, output=args.output))
        asyncio.run(run_pipeline())
    else:
        asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
