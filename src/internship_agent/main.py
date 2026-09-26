from internship_agent.graph import create_internship_graph


def main() -> None:
    """CLI entry point for running the internship discovery graph."""
    graph = create_internship_graph()
    result = graph.invoke({})

    queries: list[str] = result.get("queries", [])

    print("Internship Discovery Agent\n")
    print(f"Generated {len(queries)} search queries.\n")
    for query in queries:
        print(f"- {query}")


if __name__ == "__main__":
    main()
