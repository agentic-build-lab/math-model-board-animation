# Platform Expansion Roadmap

This project should evolve from a Douyin/Bilibili experiment into a
platform-neutral content intelligence engine. The core contract stays stable:

1. collect public or authorized platform data;
2. normalize it into snapshot/candidate/transcript artifacts;
3. score it with platform-specific profiles;
4. generate workflow briefs;
5. write blind predictions before performance data is reviewed;
6. append retrospectives after outcomes are known.

## Platform Priority

### Tier 1: Build First

#### YouTube

Why:

- Stable official Data API.
- Strong fit for creator tools and paid products.
- Public video metadata, public statistics, and public comments can be queried
  with official endpoints.
- Authenticated creator workflows can later add channel-owned analytics.

Initial module:

- `youtube_public_video`: public video snapshot by URL or video id.
- `youtube_channel_discovery`: channel video list and competitor seed list.
- `youtube_creator_brief`: title, hook, script, thumbnail, and comment-mining
  recommendations for long videos and Shorts.

Product direction:

- Creator growth lab for YouTube creators.
- Competitor analysis and topic planning.
- Prediction/retro calibration for titles, topics, hooks, and formats.

Guardrails:

- Use official YouTube Data API for product-facing workflows.
- Do not rely on undocumented YouTube interfaces.
- Do not store large downloaded videos in Git.
- Treat API quota as a product constraint.

#### Bilibili

Why:

- Public metadata, engagement, comments, coins, favorites, and danmaku are
  valuable for learning-oriented content.
- Current `bilibili_public_video` adapter already runs locally.

Next:

- Add danmaku normalization.
- Add Bilibili-specific scoring profile.
- Add long-tail educational value and community-fit dimensions.

### Tier 2: Explore With Official Or User-Authorized APIs

#### TikTok

Why:

- Very important for global short-video patterns.
- Official Display API supports authorized user video lists.
- Research API supports public data for approved research projects, including
  videos and comments.

Initial module:

- `tiktok_authorized_video_list`: own or authorized account videos through
  Display API.
- `tiktok_research_snapshot`: research-only public video/comment snapshot when
  the account has approved Research API access.

Guardrails:

- Keep Display API, Research API, Business API, and browser observation separate.
- Do not imply general public scraping support.
- Store access tokens only as secrets, never in Git.

#### X

Why:

- X is useful for topic heat, early public narratives, and market-event
  monitoring.
- Official API supports public conversations, posts, users, trends, and public
  metrics; private metrics require user context.

Initial module:

- `x_topic_snapshot`: keyword/topic/post snapshot.
- `x_public_metrics`: reposts, quotes, likes, replies, impressions, bookmarks
  where available.
- `x_market_event_seed`: optional bridge into quant research as hypothesis
  only.

Guardrails:

- API is pay-per-use, so every workflow needs cost limits.
- Social heat is not a trading signal without entity linking and market
  validation.

### Tier 3: Best-Effort Or Domain-Specific

#### Xiaohongshu

Why:

- Useful for consumer, education, lifestyle, finance-education, and ecommerce
  content.
- Official open capabilities are stronger around ecommerce, marketing, mini
  programs, stores, and ads than generic public note analytics.
- Heat prediction can transfer into ecommerce and marketing workflows if the
  output is framed as demand/intent/hook analysis rather than raw public data
  resale.

Two tracks:

- `xhs_public_observation`: best-effort public note/page observation for
  internal research only.
- `xhs_ecommerce_signal`: official ecommerce/marketing/store data when a user
  has authorized access.

Scoring emphasis:

- search intent;
- save/collect intent;
- cover and title strength;
- purchase or tutorial intent;
- comment questions and objections;
- product/category trend fit.

Guardrails:

- Do not promise stable public scraping as a paid product core.
- Keep ecommerce authorized data separate from public observations.
- Preserve review gates before publishing or commercial use.

#### Douyin

Why:

- Still core for Chinese short-video style learning.
- Current public front-page adapter can support internal research.
- Official Open Platform interaction APIs can support product-facing comment
  workflows after permission approval.

Next:

- Add official authorized comment adapter if credentials and scopes are
  available.
- Keep public-page capture marked as `best_effort`.

## Platform Profiles

The first profile layer is implemented in
`packages/content_experiment_engine/platform_profiles.py`.

Each profile defines:

- platform name;
- content formats;
- metric aliases;
- score dimensions;
- weights;
- unavailable metrics;
- legal/compliance notes;
- product readiness level.

Profiles currently included:

- `youtube_long`
- `youtube_shorts`
- `bilibili`
- `douyin`
- `tiktok`
- `x`
- `xiaohongshu`

Example dimensions:

- `hook_density`;
- `watch_intent`;
- `search_intent`;
- `save_intent`;
- `comment_question_rate`;
- `shareability`;
- `evidence_availability`;
- `creator_fit`;
- `platform_native_fit`;
- `commercial_intent`;
- `long_tail_value`.

## Productization Order

1. YouTube official API adapter.
2. Platform profile layer. Done in `platform_profiles`.
3. YouTube creator brief exporter.
4. Comment mining and audience-question clustering.
5. Web console for candidates, snapshots, predictions, and retros.
6. TikTok Display API / Research API exploration.
7. X topic snapshot and quant hypothesis bridge.
8. Xiaohongshu ecommerce/marketing authorized signal exploration.
9. Best-effort public observation adapters, clearly labeled as unstable.

## Storage And Runtime Rules

- Git stores source, docs, schemas, prompt files, small fixtures, and tests.
- `outputs/` and `work/` stay out of Git.
- Large videos, screenshots, browser profiles, auth state, and raw caches stay
  local or in external object storage.
- Use Git LFS only for intentional small demo binaries, not raw media archives.
- Cloud Codex tasks should work from reproducible setup scripts and small test
  fixtures.
