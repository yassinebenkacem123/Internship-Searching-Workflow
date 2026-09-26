# Skill: job-scoring

## Goal

Produce an explainable 0-100 match score.

## Rule

The primary score must be deterministic.

Do not ask an LLM to arbitrarily score a job.

## Example scoring

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
-40 full-time/CDI only
-50 unrelated domain
```

Clamp:

```python
score = max(0, min(score, 100))
```

## Output

Return both:

- `score`
- `reasons`

Reasons must be supported by the actual job content.
