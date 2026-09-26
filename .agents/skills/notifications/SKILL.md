# Skill: notifications

## Goal

Generate one concise daily digest.

Example:

```text
🔥 6 new PFE opportunities

1. Backend Engineer PFE — Company A
   Casablanca
   Match: 92/100
   Java, Spring Boot, PostgreSQL
   LinkedIn: ...
   Company Careers: ...

2. AI Engineer Intern — Company B
   Rabat
   Match: 87/100
   Python, RAG, LLM
   LinkedIn Post: ...
```

Only include newly discovered or meaningfully updated opportunities.

Do not send the full historical database every day.

Keep digest generation separate from transport.

Possible transports:

- Telegram
- Email
- Discord
