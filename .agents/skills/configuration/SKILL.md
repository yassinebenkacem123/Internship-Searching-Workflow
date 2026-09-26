# Skill: configuration

## Purpose

Centralize application configuration and secrets.

## Use

Prefer `pydantic-settings`.

Example environment variables:

```env
OPENAI_API_KEY=
SEARCH_PROVIDER=
SEARCH_API_KEY=

NOTION_TOKEN=
NOTION_DATABASE_ID=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Rules

- never hard-code secrets
- never commit `.env`
- provide `.env.example`
- validate required values at startup
- keep candidate preferences in config rather than scattering them across code
