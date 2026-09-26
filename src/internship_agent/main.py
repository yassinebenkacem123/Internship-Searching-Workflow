import asyncio

from internship_agent.graph import create_internship_graph


async def run_pipeline() -> None:
    """Execute the internship discovery graph and report results."""
    print("🚀 Morocco PFE Internship Discovery Agent")
    print("=========================================\n")

    graph = create_internship_graph()
    result = await graph.ainvoke({})

    queries = result.get("queries", [])
    raw_results = result.get("raw_results", [])
    normalized = result.get("normalized_jobs", [])
    filtered = result.get("filtered_jobs", [])
    deduped = result.get("deduplicated_jobs", [])
    scored = result.get("scored_jobs", [])
    created = result.get("created_jobs", [])
    updated = result.get("updated_jobs", [])
    digest = result.get("digest", "")

    print("📊 Workflow Execution Summary:")
    print(f"  • Queries generated:   {len(queries)}")
    print(f"  • Raw results fetched: {len(raw_results)}")
    print(f"  • Normalized jobs:     {len(normalized)}")
    print(f"  • Qualified PFE jobs:  {len(filtered)}")
    print(f"  • Deduplicated jobs:   {len(deduped)}")
    print(f"  • Scored opportunities:{len(scored)}")
    print(f"  • Notion Created:      {len(created)}")
    print(f"  • Notion Updated:      {len(updated)}\n")

    if digest:
        print("📋 Daily Digest:")
        print("----------------")
        print(digest)
        print("----------------\n")


def main() -> None:
    """CLI entrypoint."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
