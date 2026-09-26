# Skill: langgraph-architecture

## Purpose

Implement the internship discovery pipeline using LangGraph.

## Principle

LangGraph orchestrates the workflow.

Business logic belongs in services/functions, not directly inside the graph
definition.

## State

```python
class InternshipSearchState(TypedDict, total=False):
    queries: list[str]
    raw_results: list[SearchResult]
    normalized_jobs: list[JobOpportunity]
    filtered_jobs: list[JobOpportunity]
    deduplicated_jobs: list[JobOpportunity]
    enriched_jobs: list[JobOpportunity]
    scored_jobs: list[JobOpportunity]
    created_jobs: list[JobOpportunity]
    updated_jobs: list[JobOpportunity]
    errors: list[str]
    digest: str
```

## Graph

```text
START
   |
build_queries
   |
search_sources
   |
normalize_jobs
   |
filter_jobs
   |
deduplicate_jobs
   |
enrich_jobs
   |
score_jobs
   |
sync_notion
   |
build_digest
   |
send_notification
   |
END
```

## Organization

Graph construction belongs in:

```text
src/internship_agent/graph.py
```

Nodes belong under:

```text
src/internship_agent/nodes/
```

## Conditional edges

Use conditional routing only when behavior truly branches.

Examples:

```text
no jobs found -> build empty digest
jobs found    -> process jobs
```

Avoid unnecessary loops.

## Persistence

Persistent business state belongs primarily in Notion/database.

LangGraph persistence may later be introduced for:

- resumable runs
- checkpoints
- workflow debugging
- human approval
