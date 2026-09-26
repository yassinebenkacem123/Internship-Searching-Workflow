# Skill: llm-enrichment

## Purpose

Use an LLM only where semantic extraction improves quality.

## Good use cases

- extract technical skills from unstructured descriptions
- classify whether a recruiter post is an actual internship opportunity
- summarize an offer
- extract recruiter/contact information from messy text
- infer work mode only when explicitly supported by text

## Bad use cases

Do not use an LLM for:

- URL classification
- exact date comparisons
- deterministic scoring
- direct Notion CRUD
- simple keyword filtering
- fixed search query templates

## Structured output

Whenever possible, request structured output validated by Pydantic.

Never accept free-form LLM output directly into persistence without validation.

## Safety

Never allow the LLM to fabricate missing details.

Unknown values must remain `None`.
