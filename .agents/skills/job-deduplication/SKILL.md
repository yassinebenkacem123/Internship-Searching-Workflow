# Skill: job-deduplication

## Goal

Prevent multiple records for the same internship while preserving all
discovered source links.

## First pass

Use deterministic identifiers where possible:

```text
normalized_company + normalized_title
```

Optionally include location.

## Second pass

For ambiguous cases compare:

- company
- title similarity
- location
- description similarity
- canonical URL

## Merge behavior

If two records represent the same internship:

```python
existing.linkedin_job_url = existing.linkedin_job_url or new.linkedin_job_url
existing.linkedin_post_url = existing.linkedin_post_url or new.linkedin_post_url
existing.indeed_url = existing.indeed_url or new.indeed_url
existing.rekrute_url = existing.rekrute_url or new.rekrute_url
existing.company_careers_url = (
    existing.company_careers_url or new.company_careers_url
)
```

Never drop discovered URLs.

## Safety

Do not merge:

```text
Backend PFE
Frontend PFE
```

simply because the company is the same.
