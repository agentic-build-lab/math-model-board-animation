# AIHot Trend Source Contract

This contract adapts the upstream AIHot trend-source idea.

## Purpose

Provide AI-industry topics for:

- AI tutorial videos;
- builder content;
- AI product commentary;
- model, paper, product, and workflow explainers.

## Expected Input

```json
{
  "query": "optional keyword",
  "limit": 10,
  "categories": ["model", "product", "industry", "paper", "technique"]
}
```

## Expected Candidate Output

Each item should normalize into `content_candidate`:

```json
{
  "title": "topic title",
  "source": "trend:aihot",
  "snapshot_text": "readable summary plus why it matters",
  "snapshot_at": "ISO timestamp",
  "url": "source URL if available",
  "category": "ai_industry",
  "tags": ["ai", "trend"]
}
```

## Routing

Use for AI-heavy content forms. For general social, lifestyle, financial, or
cultural topics, route to a general trend source instead.

## Failure Handling

- If the external endpoint is unavailable, return no candidates and explain the
  failure.
- Do not block topic discovery; fall back to manual topics or another source.
