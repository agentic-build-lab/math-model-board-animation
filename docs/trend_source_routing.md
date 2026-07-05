# Trend Source Routing

This document adapts the upstream trend-source routing protocol.

Trend sources are a material feed, not the creative decision-maker. They help
discover candidate topics, but every item still needs scoring, evidence review,
and a human publishing gate.

## When To Use Trend Sources

| Scenario | Default |
|---|---|
| User gives a concrete personal experience or internal idea. | Do not fetch trends. |
| User gives a timely public event and wants context. | Ask before fetching. |
| User has no ideas and wants candidates. | Fetch enabled sources. |
| User requests batch topic discovery. | Fetch enabled sources once. |
| Candidate pool is stale. | Suggest refresh. |

## Source Classes

| Source | Best For | Local Status |
|---|---|---|
| `manual` | User-provided titles, URLs, notes. | implemented |
| `zhihu_hot` | Chinese public discussion. | best-effort implemented |
| `weibo_hot` | Chinese real-time hot search. | best-effort implemented |
| `aihot` | AI industry, models, papers, tools. | isolated contract |
| `trendradar_mcp` | Cross-platform public trends. | isolated contract |

## Degradation

Adapters should return an empty list plus a clear status when blocked. Do not
invent hot topics to fill a quota.

Degradation order:

1. primary enabled source;
2. secondary enabled source;
3. manual input;
4. no candidates, with a clear explanation.

## Candidate Contract

Every trend item must normalize to `content_candidate`:

- `title`
- `source`
- `snapshot_text`
- `snapshot_at`
- optional `url`
- optional `raw`

The adapter is responsible for expanding links into readable `snapshot_text`.
