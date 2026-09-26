# Skill: scheduler-deployment

## Purpose

Run the internship discovery workflow automatically once per day.

## Local development

The workflow should be runnable manually:

```bash
uv run python -m internship_agent.main
```

## Production options

Possible schedulers include:

- cron on a Linux VPS
- GitHub Actions scheduled workflow
- Docker + cron/supervisor
- a cloud scheduler calling an HTTP endpoint

## Rule

Scheduling is outside core business logic.

Do not put timing logic inside search or scoring services.

## Observability

A scheduled run should log:

- start time
- number of queries
- number of raw results
- number of relevant jobs
- number of new jobs
- number of updated jobs
- failures by provider
- end status
