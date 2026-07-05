# cheat-on-content Upstream Audit

This repository does not vendor the full `cheat-on-content` repository. The
upstream project is treated as a reference implementation and methodology
source. We extract the stable concepts into a local module with explicit
interfaces.

## What We Imported Conceptually

- Candidate normalization: every topic, trend, source URL, or public video is
  normalized into a stable candidate object.
- Stable dedupe ids: source type + normalized title + URL path.
- Public performance capture: public video pages can be captured into
  `snapshot.json`.
- Rubric scoring: explicit dimensions, composite score, bucket, and reason.
- Blind prediction principle: predictions must be written before performance
  data is seen if they are used for calibration.
- Retro principle: performance data and comments should append a review record,
  not rewrite the original prediction.
- Observation lifecycle: one-off observations become tracked hypotheses only
  after repeated evidence.
- SQL as queryable index: markdown/JSON artifacts remain auditable, SQLite
  supports dashboards and cross-project analysis.
- Script extraction contract: transcripts become normalized artifacts before
  analysis, regardless of whether they came from Whisper, manual captions, or a
  cloud ASR service.
- Text-diff and calibration reports: script changes and prediction error are
  measured with local, dependency-light tools.

## What We Did Not Vendor

- Claude Code slash commands and hooks: useful upstream, but not directly
  portable to this Windows/Codex workspace.
- Global installer scripts: they mutate user-level skill directories and are not
  the right default for a reusable project module.
- Browser auth state and crawler caches: `.auth/`, `.cheat-cache/`, and raw
  debug captures must never enter Git.
- Full upstream rubrics verbatim: they are tuned for one content account. We use
  a neutral `content_video_v0` rubric and keep account-specific calibration in
  our own data.
- Platform adapters that are schema-only upstream: we document the source ideas,
  but only promote adapters when they run in our environment.

## Upstream Parts Still Worth Reusing Later

- Bilibili public-stat adapter. Imported locally as `bilibili_public_video`.
- Xiaohongshu Playwright adapter. Migrated as an isolated contract in
  `integrations/experimental_platform_adapters/xiaohongshu_contract.md`;
  executable crawler is intentionally not vendored yet.
- LinkedIn session adapter, only for the user's own account or permitted pages.
- Douyin session adapter. Migrated as an isolated contract in
  `integrations/experimental_platform_adapters/douyin_session_contract.md`;
  executable crawler is intentionally not vendored yet.
- Trend-source routing and cadence protocols, adapted into a platform profile
  and source-selection layer rather than copied as Claude-specific commands.
- Rubric bump validation and score-curve tools, adapted later into
  experiment-calibration reports.
- Whisper script extraction adapter. Adapted locally as the engine-neutral
  `transcripts` module and `create_transcript_artifact.py`.
- Rubric bump validation protocol.
- Prediction immutability hook. Adapted locally into `prediction_records.py`,
  `create_content_prediction.py`, and `append_content_retro.py` instead of a
  Claude hook.
- Human-readable markdown views generated from SQLite. Adapted locally as
  `review_report.py` and `export_content_review.py`.
- Upstream `diff_pct.py`. Adapted locally as `text_similarity.py` and
  `compare_text_similarity.py`.
- Upstream `score-curve.py`. Adapted locally as `calibration_reports.py` and
  `export_calibration_report.py`.

## Current Local Module

The local module is `packages/content_experiment_engine`.

Current interfaces:

- `douyin_public_video`: public Douyin video snapshot capture.
- `bilibili_public_video`: public Bilibili video snapshot capture.
- `candidates`: normalized candidate object and stable ids.
- `rubric`: scoring contract and starter rubric.
- `brief_generator`: converts a candidate into a workflow-neutral video brief.
- `trend_sources`: manual, Zhihu hot, and Weibo hot candidate sources.
- `prediction_records`: immutable prediction markdown and retro appends.
- `text_similarity`: normalized script/transcript difference checks.
- `calibration_reports`: prediction error reports and calibration samples.
- `transcripts`: normalized transcript JSON/markdown artifacts.
- `review_report`: human-readable SQLite review markdown.
- `snapshot_store`: SQLite schema bootstrap and snapshot import.

## Codex Version

The Codex-facing skill draft lives at:

- `codex_skills/content-experiment-engine/SKILL.md`

It is intentionally repo-local for now. After review, it can be copied or
installed into `~/.codex/skills/content-experiment-engine` for global discovery.

## Why This Shape Is Better Than a Full Copy

- The module can be imported by any workflow without inheriting upstream command
  assumptions.
- Upstream can still be updated separately and re-audited.
- Runtime artifacts stay outside Git.
- Our video pipelines get stable JSON/SQLite contracts instead of project-local
  markdown conventions only.
- The same candidate can route to evidence video, model animation, AI editing,
  or quant signal research.
