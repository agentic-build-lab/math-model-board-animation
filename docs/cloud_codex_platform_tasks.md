# Cloud Codex Platform Tasks

Use these tasks as handoff prompts for Codex web/cloud. They are written so the
cloud agent can work from GitHub without relying on local browser state or large
raw media.

## Task 1: YouTube Public Adapter

Goal:

Build a YouTube official Data API adapter that normalizes a public video into
the existing `content_video_snapshot` shape.

Inputs:

- YouTube video URL or video id.
- `YOUTUBE_API_KEY` as a secret or environment variable.
- Optional `max_comments`.

Expected files:

- `packages/content_experiment_engine/youtube_public_video.py`
- update `scripts/analyze_public_video.py`
- update `schemas/content_video_snapshot.schema.json`
- update `schemas/content_experiment.schema.sql` only if needed
- tests in `tests/test_content_experiment_engine.py`
- docs update in `docs/content_experiment_module.md`

Requirements:

- Use official YouTube Data API endpoints only.
- Fetch video metadata/statistics with `videos.list`.
- Fetch public comment threads with `commentThreads.list`.
- Do not require OAuth for public video snapshots.
- Normalize platform fields:
  - `platform`: `youtube`
  - `platform_video_id`: video id
  - `metrics`: view, like, comment, favorite if available
  - comments: text, like count, reply count, author display name, published time
- Store raw API responses as JSONL.
- Add clear limitations for disabled comments, quota errors, unavailable like
  counts, and API-key absence.

Verification:

- Unit tests for URL/id parsing and response normalization using fixtures.
- Compile check.
- A live probe only when `YOUTUBE_API_KEY` is present.

## Task 2: Platform Profiles

Goal:

Add a platform-specific scoring profile layer so the same topic can be scored
differently for YouTube, YouTube Shorts, Bilibili, Douyin, TikTok, X, and
Xiaohongshu.

Status:

Implemented in `packages/content_experiment_engine/platform_profiles.py`.
Future work should refine weights with real prediction/retro data rather than
replacing the contract.

Expected files:

- `packages/content_experiment_engine/platform_profiles.py`
- optional `schemas/platform_profile.schema.json`
- tests
- docs update

Requirements:

- Profiles must be data-driven.
- Include dimensions and weights.
- Include product readiness levels:
  - `official_api_ready`
  - `authorized_only`
  - `best_effort_public_observation`
  - `research_or_experimental`
- Do not break existing `score_candidate`.

## Task 3: Comment Mining

Goal:

Extract audience insight from comments across platforms.

Expected outputs:

- top questions;
- objections;
- requests for follow-up;
- emotional signals;
- product/commercial intent;
- confusing points;
- reusable hook lines.

Requirements:

- Work from normalized snapshot comments.
- No platform-specific parsing in the core module.
- Include a JSON output schema and markdown summary.

## Task 4: Xiaohongshu Feasibility Spike

Goal:

Assess Xiaohongshu as two distinct tracks:

- public observation for internal research;
- authorized ecommerce/marketing/store signals for product workflows.

Expected output:

- `docs/xiaohongshu_feasibility.md`
- list of official APIs and gaps;
- proposed schema extensions;
- decision on whether to implement a first adapter.

Rules:

- Do not commit auth state.
- Do not promise public scraping stability.
- Prefer official or user-authorized APIs for product-facing workflows.

## Task 5: TikTok And X Feasibility Spike

Goal:

Map official API options and build the smallest possible adapter plan for each.

Expected output:

- `docs/tiktok_x_platform_feasibility.md`
- API capability matrix;
- pricing/quota notes;
- environment variables and secrets needed;
- first implementation task for each platform.

Rules:

- TikTok Display API and Research API are separate tracks.
- X API pay-per-use needs cost controls from day one.
- Quant use remains hypothesis-only until validated against market data.
