# Skill: testing

## Framework

Use pytest.

Install:

```bash
uv add --dev pytest pytest-asyncio
```

## Required tests

### Query generation

Verify categories create expected searches.

### Filtering

Test:

- valid PFE role
- unrelated role
- CDI-only role
- Moroccan location
- remote role

### URL classification

Test:

- LinkedIn Jobs
- LinkedIn Posts
- Indeed
- ReKrute
- company careers
- ATS pages

### Deduplication

Verify the same company + same opportunity + different source becomes one
internship with multiple URLs.

### Scoring

Test deterministically.

### Notion

Mock all Notion calls.

No unit test should create a real Notion page.

### Search APIs

Mock external search API requests.

Unit tests must not consume paid API quotas.
