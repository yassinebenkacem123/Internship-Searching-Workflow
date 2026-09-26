# AGENT.md — Morocco PFE Internship Discovery Agent

## Role

You are implementing a production-quality Python application that searches
for final-year internship / PFE opportunities in Morocco.

The application uses:

- Python
- LangGraph
- uv for package and environment management
- Notion as the main internship CRM/database
- Search APIs and public web sources for internship discovery
- An LLM only where semantic understanding is useful
- Optional email / Telegram / Discord notifications

The system searches for internships related to:

- Software Engineering
- Backend Engineering
- Frontend Engineering
- Full Stack Development
- Web Development
- Java
- Spring Boot
- React
- Next.js
- Node.js
- Python
- Artificial Intelligence
- Machine Learning
- LLMs
- RAG
- Data Engineering
- Cloud
- DevOps
- Docker
- Kubernetes
- Terraform

Primary geographical scope:

- Morocco
- Remote roles available to candidates in Morocco

Cities of particular interest include:

- Casablanca
- Rabat
- Fes
- Marrakech
- Tangier
- Agadir

---

# Primary Goal

Build a LangGraph workflow that runs automatically every day and:

1. Generates targeted internship search queries.
2. Searches multiple public sources.
3. Finds PFE / final-year internship opportunities.
4. Detects LinkedIn job pages when indexed.
5. Detects relevant LinkedIn recruiter/company posts when indexed.
6. Finds Indeed listings.
7. Finds ReKrute listings.
8. Finds company career pages.
9. Finds ATS-hosted job listings when possible.
10. Normalizes results into one internal Job model.
11. Filters irrelevant jobs.
12. Detects duplicate opportunities.
13. Merges multiple source URLs belonging to the same internship.
14. Extracts useful job information.
15. Scores the opportunity against the candidate profile.
16. Creates or updates a Notion database entry.
17. Generates a daily digest of newly discovered opportunities.
18. Sends an optional notification.

---

# Critical Rules

## 1. Never invent job information

Never fabricate:

- company names
- job titles
- locations
- technologies
- recruiter names
- email addresses
- posting dates
- salaries
- application deadlines
- internship durations
- URLs

If data is unavailable, use `None`.

## 2. Preserve source URLs

Each job may contain multiple source URLs:

- `linkedin_job_url`
- `linkedin_post_url`
- `indeed_url`
- `rekrute_url`
- `company_careers_url`
- `ats_url`
- `original_url`

Do not discard a new source merely because the internship already exists.

If an internship already exists in Notion but a new LinkedIn post is found,
update the existing Notion record rather than creating a duplicate.

## 3. Avoid fragile scraping

Do not implement authenticated LinkedIn scraping.

Prefer:

- search-engine-indexed LinkedIn pages
- official APIs where available
- public job pages
- company career pages
- public ATS listings

Examples:

```text
site:linkedin.com/jobs "PFE" Morocco
site:linkedin.com/posts "stage PFE" "Java" Maroc
site:linkedin.com/posts "DevOps" "PFE" Morocco
```

---

# LangGraph Architecture

Use LangGraph for workflow orchestration.

Preferred graph:

```text
START
  |
  v
build_queries
  |
  v
search_sources
  |
  v
normalize_jobs
  |
  v
filter_jobs
  |
  v
deduplicate_jobs
  |
  v
enrich_jobs
  |
  v
score_jobs
  |
  v
sync_notion
  |
  v
build_digest
  |
  v
send_notification
  |
  v
END
```

Use explicit nodes and predictable transitions. Prefer deterministic workflows
over unnecessary autonomous agent loops.

---

# State

Define strongly typed state.

```python
from typing import TypedDict

class InternshipSearchState(TypedDict, total=False):
    queries: list[str]
    raw_results: list[dict]
    normalized_jobs: list[dict]
    filtered_jobs: list[dict]
    deduplicated_jobs: list[dict]
    enriched_jobs: list[dict]
    scored_jobs: list[dict]
    created_jobs: list[dict]
    updated_jobs: list[dict]
    errors: list[str]
    digest: str
```

Use Pydantic models for domain entities.

---

# Core Domain Model

Create a Pydantic model similar to:

```python
from datetime import datetime
from pydantic import BaseModel, Field

class JobOpportunity(BaseModel):
    id: str | None = None

    title: str
    company: str | None = None

    description: str | None = None
    location: str | None = None
    work_mode: str | None = None
    internship_type: str | None = None

    posted_date: datetime | None = None
    found_date: datetime

    source_names: list[str] = Field(default_factory=list)

    original_url: str | None = None
    linkedin_job_url: str | None = None
    linkedin_post_url: str | None = None
    indeed_url: str | None = None
    rekrute_url: str | None = None
    company_careers_url: str | None = None
    ats_url: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    recruiter_name: str | None = None
    recruiter_linkedin: str | None = None
    contact_email: str | None = None

    duration: str | None = None
    deadline: datetime | None = None

    match_score: int | None = None
    match_reasons: list[str] = Field(default_factory=list)

    status: str = "New"
```

---

# Search Queries

Generate deterministic queries such as:

```text
"PFE" "Software Engineer" Morocco
"PFE" "Java" "Spring Boot" Morocco
"PFE" "Backend Developer" Morocco
"PFE" "Full Stack" Morocco
"PFE" DevOps Morocco
"PFE" Kubernetes Morocco
"PFE" AI Morocco
"PFE" Machine Learning Morocco
"PFE" LLM Morocco
"PFE" RAG Morocco

"stage fin d'études" développeur Maroc
"stage fin d'études" DevOps Maroc
"stage fin d'études" intelligence artificielle Maroc

"final year internship" software Morocco
"end of studies internship" software Morocco
```

Site-specific searches:

```text
site:linkedin.com/jobs "PFE" Morocco
site:linkedin.com/posts "PFE" Morocco
site:indeed.com Morocco "PFE" software
site:rekrute.com "PFE" informatique
```

An LLM is not necessary for simple query templates.

---

# Search Abstraction

Search providers must be behind interfaces.

```python
from typing import Protocol

class SearchProvider(Protocol):
    async def search(self, query: str) -> list["SearchResult"]:
        ...
```

Possible implementations:

- Tavily
- Brave Search
- Serper
- another configurable provider

Do not tightly couple graph nodes to one provider.

---

# Filtering Rules

A result is relevant when it strongly suggests:

- PFE
- final-year internship
- end-of-study internship
- stage de fin d'études
- software / AI / devops / web internship

Positive internship terms:

```text
PFE
stage PFE
stage fin d'études
stage de fin d'études
final year internship
end-of-study internship
internship
stagiaire
```

Relevant technical terms:

```text
software engineer
software developer
backend
frontend
full stack
fullstack
web developer
java
spring boot
react
next.js
node.js
python
AI
artificial intelligence
machine learning
LLM
RAG
data
cloud
devops
docker
kubernetes
terraform
```

---

# Deduplication

Do not simply compare URLs.

Use multiple signals:

1. normalized company name
2. normalized job title
3. location
4. description similarity
5. canonical URL when available

Start with deterministic matching, then fuzzy similarity for ambiguous cases.

Never merge two offers solely because they come from the same company.

---

# Source Merge Behavior

If two results represent the same opportunity, merge source links instead of
creating duplicates.

Example:

```text
linkedin_job_url = ...
indeed_url = ...
company_careers_url = ...
```

---

# Job Scoring

Scoring must be explainable.

Do not ask an LLM to invent a score.

Example:

```text
+30 explicit PFE/final-year internship
+20 Java/Spring Boot
+15 Backend/software engineering
+15 AI/LLM/RAG
+15 DevOps/cloud
+10 React/Next.js
+5 PostgreSQL
+5 Docker

-40 substantial required professional experience
-40 CDI/full-time only with no internship
-50 unrelated technical field
```

Clamp:

```python
score = max(0, min(score, 100))
```

Return both score and reasons.

---

# Candidate Profile

Keep candidate preferences in configuration.

```yaml
target_roles:
  - Software Engineer
  - Backend Engineer
  - Full Stack Developer
  - DevOps Engineer
  - AI Engineer

skills:
  high_priority:
    - Java
    - Spring Boot
    - PostgreSQL
    - Docker

  medium_priority:
    - React
    - Kubernetes
    - Python
    - AI
    - LLM
```

---

# Notion

Notion is the main persistent internship CRM.

Expected fields:

```text
Position
Company
Status
Match Score
Location
Work Mode
Posted Date
Found Date
Source
Main Job Link
LinkedIn Job
LinkedIn Post
Indeed
ReKrute
Company Careers
ATS URL
Recruiter
Recruiter LinkedIn
Contact Email
Required Skills
Missing Skills
Internship Type
Notes
```

Suggested statuses:

```text
New
To Review
Interested
Applied
Interview
Rejected
Offer
Ignored
```

When updating existing jobs, do not overwrite user-managed fields such as
Status, Notes, application history, or interview notes.

---

# LLM Usage

Use an LLM only when semantic interpretation adds value.

Good uses:

- extracting skills from messy descriptions
- deciding whether an unstructured recruiter post is truly a hiring opportunity
- summarizing jobs
- extracting recruiter details
- parsing messy text into structured data

Avoid using an LLM for:

- URL classification
- simple filtering
- date comparisons
- deterministic scoring
- Notion CRUD
- query templates

Use structured output with Pydantic whenever possible.

---

# Async

Use async I/O for network-heavy operations:

- search APIs
- page fetching
- Notion API
- LLM calls
- notifications

Avoid unnecessary blocking.

---

# Error Handling

One failed source must not terminate the whole workflow.

Collect errors in state.

Use bounded retry behavior for transient network failures.

Never use infinite retries.

---

# Configuration

Secrets belong in environment variables.

Example:

```env
OPENAI_API_KEY=
SEARCH_API_KEY=
NOTION_TOKEN=
NOTION_DATABASE_ID=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Never commit `.env`.

Provide `.env.example`.

---

# Python and uv

This project MUST use uv.

Do not use:

```text
pip install
python -m venv
poetry
pipenv
conda
```

unless specifically requested.

Use:

```bash
uv init
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
```

Commit:

- `pyproject.toml`
- `uv.lock`

Do not manually modify `.venv`.

---

# Testing

Use pytest.

Install:

```bash
uv add --dev pytest pytest-asyncio
```

Tests must cover:

- query generation
- normalization
- URL source detection
- filtering
- deduplication
- scoring
- Notion payload creation

Mock external services.

Do not consume paid API quotas in unit tests.

---

# Code Quality

Prefer:

- small functions
- typed functions
- dependency injection
- Pydantic models
- Protocol interfaces
- explicit service boundaries
- deterministic behavior
- structured logging

Avoid:

- giant graph nodes
- business logic inside `graph.py`
- global mutable state
- hard-coded secrets
- provider-specific logic scattered everywhere
- unnecessary autonomous-agent behavior

---

# Development Order

Implement in this order:

1. uv project initialization
2. configuration
3. domain models
4. search provider interface
5. query generation
6. normalization
7. filtering
8. deduplication
9. scoring
10. LangGraph state
11. graph nodes
12. graph construction
13. Notion integration
14. enrichment
15. digest
16. notifications
17. scheduler/deployment
18. tests and documentation

---

# Definition of Done

The project is complete when:

1. `uv sync` succeeds.
2. Tests succeed.
3. A local run can execute the graph.
4. Search results from multiple sources can be normalized.
5. Irrelevant jobs are rejected.
6. Duplicates are merged.
7. Source URLs are preserved.
8. Each relevant job receives an explainable score.
9. New jobs can be written to Notion.
10. Existing jobs can be enriched without overwriting user-managed fields.
11. A daily digest can be generated.
12. The project can be scheduled once per day.
