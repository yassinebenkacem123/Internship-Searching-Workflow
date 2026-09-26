# Morocco PFE Internship Discovery Agent

An intelligent internship discovery and tracking system built with **Python**, **LangGraph**, **uv**, and **Notion**.

The project is designed to automatically search for **PFE / final-year internship opportunities in Morocco**, especially in:

- Software Engineering
- Backend Engineering
- Full Stack Development
- Web Development
- DevOps
- Cloud Engineering
- Artificial Intelligence
- Machine Learning
- LLM / RAG
- Java / Spring Boot
- React / Next.js
- Docker / Kubernetes

The long-term goal is to run the workflow every day, discover newly posted opportunities across multiple sources, remove duplicates, score opportunities against a candidate profile, store everything in Notion, and generate a daily digest.

---

## Project Goals

The system should eventually be able to:

1. Generate targeted internship search queries.
2. Search multiple public job sources.
3. Detect relevant:
   - LinkedIn Jobs pages
   - LinkedIn recruiter/company posts
   - Indeed listings
   - ReKrute listings
   - company career pages
   - ATS-hosted opportunities
4. Normalize results into a common data model.
5. Filter irrelevant jobs.
6. Detect duplicate opportunities.
7. Merge multiple URLs that belong to the same internship.
8. Extract relevant skills and internship details.
9. Calculate an explainable match score.
10. Create or update internship records in Notion.
11. Preserve manual application status and notes.
12. Generate a daily digest of new opportunities.
13. Send optional notifications through Telegram, email, or Discord.

---

# Architecture

The project uses **LangGraph** as the workflow orchestration layer.

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

The workflow is intentionally designed as an explicit graph instead of one large autonomous agent.

This makes the application easier to:

- test
- debug
- maintain
- extend
- observe
- explain in a technical interview

---

# Current Development Phase

## Phase 1 — Foundation

The first development phase focuses on building a clean application foundation.

Current scope:

- uv project setup
- source-layout Python project
- configuration with `pydantic-settings`
- domain models
- candidate profile model
- LangGraph state
- deterministic query generation
- search provider abstraction
- minimal LangGraph workflow
- CLI entry point
- unit tests
- Ruff configuration

The initial graph is intentionally simple:

```text
START
  |
  v
build_queries
  |
  v
END
```

Real search APIs, Notion synchronization, LLM enrichment, and notifications are added in later phases.

---

# Technology Stack

## Core

| Technology | Purpose |
|---|---|
| Python | Main application language |
| LangGraph | Workflow orchestration |
| Pydantic | Domain models and validation |
| pydantic-settings | Environment-based configuration |
| uv | Dependency and environment management |

## Planned Integrations

| Technology | Purpose |
|---|---|
| Notion API | Internship CRM and persistence |
| Tavily / Brave / Serper | Search provider options |
| Ollama (Local LLM) | Structured semantic enrichment |
| Telegram / Email / Discord | Daily notifications |
| pytest | Automated testing |
| Ruff | Linting and code quality |

---

# Project Structure

```text
internship-agent/
│
├── .agents/
│   ├── AGENT.md
│   └── skills/
│       ├── configuration/
│       ├── internship-search/
│       ├── job-deduplication/
│       ├── job-normalization/
│       ├── job-scoring/
│       ├── langgraph-architecture/
│       ├── llm-enrichment/
│       ├── notifications/
│       ├── notion-sync/
│       ├── scheduler-deployment/
│       ├── testing/
│       └── uv-python/
│
├── src/
│   └── internship_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── graph.py
│       ├── state.py
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── candidate.py
│       │   ├── job.py
│       │   └── search_result.py
│       │
│       ├── nodes/
│       │   ├── __init__.py
│       │   └── build_queries.py
│       │
│       └── services/
│           ├── __init__.py
│           └── search/
│               ├── __init__.py
│               └── base.py
│
├── tests/
│   ├── test_graph.py
│   ├── test_models.py
│   └── test_query_generation.py
│
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

The structure will evolve as new phases are implemented.

---

# Package Management

This project uses **uv exclusively**.

Do not use:

```bash
pip install
python -m venv
poetry
pipenv
conda
```

Use:

```bash
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
```

---

# Getting Started

## 1. Install uv

Follow the official uv installation instructions for your operating system.

Verify:

```bash
uv --version
```

---

## 2. Clone the repository

```bash
git clone <your-repository-url>
cd internship-agent
```

---

## 3. Install dependencies

```bash
uv sync
```

This creates and synchronizes the project environment using `pyproject.toml` and `uv.lock`.

---

## 4. Configure environment variables

Copy:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

SEARCH_PROVIDER=
SEARCH_API_KEY=

NOTION_TOKEN=
NOTION_DATABASE_ID=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

During Phase 1, most integration credentials are optional.

Never commit real secrets.

---

# Running the Application

Run:

```bash
uv run python -m internship_agent.main
```

During Phase 1, the application generates internship search queries.

Example output:

```text
Internship Discovery Agent

Generated 24 search queries.

- "PFE" "Software Engineer" Morocco
- "PFE" "Java" "Spring Boot" Morocco
- "PFE" "Full Stack" Morocco
- "PFE" DevOps Morocco
- "PFE" AI Morocco
...
```

---

# Running Tests

```bash
uv run pytest
```

The initial test suite should cover:

- domain models
- mutable default safety
- query generation
- LinkedIn query generation
- Indeed query generation
- ReKrute query generation
- duplicate query prevention
- LangGraph execution

External APIs must be mocked in unit tests.

---

# Code Quality

Run Ruff:

```bash
uv run ruff check .
```

Fix linting problems instead of disabling rules without a strong reason.

---

# Search Strategy

The application uses deterministic query templates instead of asking an LLM to invent search queries.

Example searches:

```text
"PFE" "Software Engineer" Morocco
"PFE" "Java" "Spring Boot" Morocco
"PFE" "Backend Developer" Morocco
"PFE" "Full Stack" Morocco
"PFE" DevOps Morocco
"PFE" AI Morocco
"PFE" Machine Learning Morocco
"PFE" LLM Morocco
"PFE" RAG Morocco

"stage fin d'études" développeur Maroc
"stage fin d'études" DevOps Maroc

"final year internship" software Morocco
```

Source-specific searches include:

```text
site:linkedin.com/jobs "PFE" Morocco
site:linkedin.com/posts "PFE" Morocco
site:indeed.com "PFE" Morocco software
site:rekrute.com "PFE" informatique
```

The project intentionally avoids fragile authenticated LinkedIn scraping.

---

# Job Data Model

Each opportunity is eventually normalized into a single model.

Example:

```python
JobOpportunity(
    title="Backend Software Engineer PFE",
    company="Example Company",
    location="Casablanca",
    internship_type="PFE",
    linkedin_job_url=None,
    linkedin_post_url=None,
    indeed_url=None,
    rekrute_url=None,
    company_careers_url=None,
    required_skills=["Java", "Spring Boot", "PostgreSQL"],
    match_score=90,
    status="New",
)
```

A single internship may have several source URLs.

For example:

```text
LinkedIn Job
+
LinkedIn recruiter post
+
Indeed
+
Company career page
```

These should be merged into one internship record rather than stored as duplicates.

---

# Deduplication Strategy

Duplicate detection must not rely only on URLs.

The same job can appear on several platforms.

The system will compare:

- normalized company name
- normalized position title
- location
- job description similarity
- canonical URLs

Example:

```text
Oracle
Software Engineer PFE
LinkedIn
```

and:

```text
Oracle
PFE Software Engineer
Indeed
```

may represent the same internship.

If confirmed as the same opportunity, the URLs are merged.

---

# Match Scoring

Opportunity ranking must be explainable and deterministic.

Example scoring:

```text
+30 explicit PFE / final-year internship
+20 Java / Spring Boot
+15 backend / software engineering
+15 AI / LLM / RAG
+15 DevOps / cloud
+10 React / Next.js
+5 PostgreSQL
+5 Docker

-40 substantial required professional experience
-40 full-time / CDI role without internship
-50 unrelated technical domain
```

Final score:

```python
score = max(0, min(score, 100))
```

The application should always preserve reasons for the score.

Example:

```text
Match: 90/100

Why:
✓ Explicit PFE opportunity
✓ Java requested
✓ Spring Boot requested
✓ PostgreSQL requested
✓ Docker requested
```

---

# Notion CRM

Notion will act as the main internship tracking database.

Recommended properties:

| Property | Type |
|---|---|
| Position | Title |
| Company | Text |
| Status | Select |
| Match Score | Number |
| Location | Text |
| Work Mode | Select |
| Posted Date | Date |
| Found Date | Date |
| Source | Multi-select |
| Main Job Link | URL |
| LinkedIn Job | URL |
| LinkedIn Post | URL |
| Indeed | URL |
| ReKrute | URL |
| Company Careers | URL |
| ATS URL | URL |
| Recruiter | Text |
| Recruiter LinkedIn | URL |
| Contact Email | Email |
| Required Skills | Multi-select |
| Missing Skills | Multi-select |
| Internship Type | Select |
| Notes | Text |

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

The automation must never overwrite user-managed fields such as:

- Status
- Notes
- application history
- interview notes
- personal decisions

---

# LLM Usage Philosophy

The project does not use an LLM for everything.

Use deterministic code where deterministic logic is enough.

## Good LLM use cases

- extracting skills from unstructured descriptions
- interpreting recruiter posts
- extracting structured job details
- summarizing long job descriptions
- generating match explanations from verified data

## Avoid LLM use for

- URL classification
- fixed query generation
- date comparison
- direct CRUD operations
- deterministic scoring
- exact duplicate identifiers

This keeps the system cheaper, more reliable, and easier to test.

---

# Development Roadmap

## Phase 1 — Foundation (Completed)

- [x] Initialize project with uv
- [x] Add core dependencies
- [x] Create source layout
- [x] Create settings
- [x] Create Pydantic models
- [x] Define LangGraph state
- [x] Implement deterministic query generation
- [x] Create search-provider abstraction
- [x] Create minimal graph
- [x] Add CLI
- [x] Add tests
- [x] Add Ruff

---

## Phase 2 — Real Search Layer

- [ ] Implement first real search provider
- [ ] Search LinkedIn indexed jobs
- [ ] Search LinkedIn indexed posts
- [ ] Search Indeed
- [ ] Search ReKrute
- [ ] Search company career pages
- [ ] Search ATS pages
- [ ] Handle pagination
- [ ] Handle provider failures
- [ ] Add retry policies

---

## Phase 3 — Normalization and Filtering

- [ ] Normalize provider responses
- [ ] Detect source type from URLs
- [ ] Filter PFE / internship opportunities
- [ ] Filter Morocco / remote roles
- [ ] Reject unrelated results
- [ ] Add tests for filtering

---

## Phase 4 — Deduplication

- [ ] Implement normalized title matching
- [ ] Implement normalized company matching
- [ ] Merge source URLs
- [ ] Add fuzzy comparison for ambiguous cases
- [ ] Add deduplication tests

---

## Phase 5 — Enrichment and Scoring

- [ ] Extract skills
- [ ] Extract recruiter details
- [ ] Extract internship metadata
- [ ] Implement deterministic match scoring
- [ ] Generate score explanations
- [ ] Add optional LLM enrichment

---

## Phase 6 — Notion Integration

- [ ] Connect Notion API
- [ ] Create internship pages
- [ ] Find existing internships
- [ ] Update source URLs
- [ ] Preserve manual fields
- [ ] Store scores and skills
- [ ] Add integration tests with mocked responses

---

## Phase 7 — Daily Digest

- [ ] Aggregate new opportunities
- [ ] Generate daily digest
- [ ] Add Telegram transport
- [ ] Add email transport
- [ ] Add Discord transport

---

## Phase 8 — Automation and Deployment

- [ ] Add daily scheduling
- [ ] Configure production environment
- [ ] Add structured logging
- [ ] Add run metrics
- [ ] Add deployment documentation

Potential deployment options:

- GitHub Actions
- Linux VPS + cron
- Docker
- cloud scheduler

---

# Example Final Workflow

```text
08:00
  |
  v
Generate Search Queries
  |
  v
Search Public Sources
  |
  +--> LinkedIn Jobs
  |
  +--> LinkedIn Posts
  |
  +--> Indeed
  |
  +--> ReKrute
  |
  +--> Company Careers
  |
  +--> ATS Pages
  |
  v
Normalize Results
  |
  v
Filter Relevant PFE Roles
  |
  v
Deduplicate Opportunities
  |
  v
Merge Source URLs
  |
  v
Extract Skills / Details
  |
  v
Calculate Match Score
  |
  v
Check Notion
  |
  +--> Existing -> Update
  |
  +--> New -> Create
  |
  v
Generate Daily Digest
  |
  v
Send Notification
```

---

# Design Principles

The project follows these principles:

### Deterministic first

Use normal code when normal code is sufficient.

### LLM only where useful

Use AI for semantic understanding, not basic business logic.

### One job, many sources

Several source URLs should enrich one internship record.

### Preserve user decisions

Automation must never destroy manually maintained application status or notes.

### Fail gracefully

A failed search provider should not stop the full workflow.

### Test core behavior

Search normalization, filtering, deduplication, scoring, and Notion payload generation should be testable without external APIs.

### Explicit workflow

LangGraph nodes should remain small and understandable.

---

# Security

Never commit:

```text
.env
API keys
Notion tokens
Telegram bot tokens
private credentials
```

Keep only:

```text
.env.example
```

in version control.

---

# Why This Project?

Finding PFE opportunities manually often means repeatedly checking different platforms and seeing the same job several times.

This project aims to transform that process into a structured workflow:

```text
Search
→ Filter
→ Deduplicate
→ Rank
→ Track
→ Notify
```

Instead of being only a scraper, the application acts as a personal internship discovery and application-tracking system.

---

# Future Ideas

Possible improvements after the core system is stable:

- CV-aware job scoring
- cover-letter generation
- recruiter outreach drafts
- application deadline reminders
- company watchlists
- job-status monitoring
- analytics dashboard
- application conversion statistics
- skill-gap analysis
- learning recommendations based on recurring missing skills
- human approval before automatic actions

---

# Status

✅ **Phase 1 — Foundation and Minimal LangGraph Workflow Completed**

Next target: **Phase 2 — Real Search Layer**

---

# License

Choose a license before publishing the repository publicly.

For a personal portfolio project, the MIT License is a common option.
