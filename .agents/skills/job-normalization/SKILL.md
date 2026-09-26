# Skill: job-normalization

## Purpose

Convert heterogeneous search results into a single `JobOpportunity` schema.

## Rules

Normalize before applying business logic.

Preserve original display values while creating normalized forms for matching.

Useful operations:

- lowercase
- trim whitespace
- collapse duplicate spaces
- normalize punctuation
- normalize company suffixes carefully

## Source URL detection

Recognize patterns for:

```text
linkedin.com/jobs
linkedin.com/posts
indeed.*
rekrute.com
greenhouse.io
lever.co
workday.*
```

Populate the corresponding URL field.

Do not overwrite a previously discovered source URL with `None`.
