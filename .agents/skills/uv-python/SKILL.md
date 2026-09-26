# Skill: uv-python

## Purpose

Manage this project's Python environment and dependencies exclusively with uv.

## Rules

Use:

```bash
uv init
uv add
uv remove
uv sync
uv lock
uv run
uv tree
```

Do not default to:

```text
pip install
python -m venv
poetry
pipenv
```

## New project

```bash
uv init internship-agent
cd internship-agent
```

## Add runtime dependency

```bash
uv add langgraph
```

## Add development dependency

```bash
uv add --dev pytest
```

## Run application

```bash
uv run python -m internship_agent.main
```

## Run tests

```bash
uv run pytest
```

## Important

Do not manually modify `.venv`.

Do not commit `.venv`.

Commit:

```text
pyproject.toml
uv.lock
```

Keep the lockfile synchronized with dependency changes.
