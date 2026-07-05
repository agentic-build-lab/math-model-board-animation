# Content Experiment Module

This module adapts the useful parts of `cheat-on-content` into a reusable
component for our video systems. The current goal is not to fork all upstream
code into this repository. The goal is to provide stable boundaries:

- public video snapshot capture;
- creator-dashboard capture later;
- normalized JSON output;
- evidence files for review;
- a small CLI that any system can call.

## Current Adapter

`douyin_public_video` captures public Douyin video pages with Playwright. It is
intended for public research:

- topic discovery;
- competitor video analysis;
- comment mining;
- hook and angle analysis;
- pre-production evidence collection.

It does not require creator-center login. It also cannot access private creator
dashboard metrics such as completion rate, traffic source, audience profile, or
follower conversion.

## Command

```powershell
python scripts\analyze_public_video.py `
  --platform douyin `
  --url https://www.douyin.com/video/7636402601549974818 `
  --output-dir outputs\content_experiment\douyin_7636402601549974818 `
  --headed
```

Install runtime dependencies first:

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

## Output Contract

The adapter writes:

- `snapshot.json`: normalized data for downstream systems;
- `raw_responses.jsonl`: captured API responses for debugging. Request URLs are
  stored without query strings by default;
- `public_video_page.png`: evidence screenshot.

The JSON shape is defined in
`schemas/content_video_snapshot.schema.json`.

Snapshots can be imported into SQLite:

```powershell
python scripts\import_content_snapshot.py `
  --snapshot outputs\content_experiment\douyin_7636402601549974818\snapshot.json `
  --database outputs\content_experiment\content_experiment.db
```

The database schema is mirrored in `schemas/content_experiment.schema.sql`.

## Integration Direction

Recommended downstream users:

- `evidence-driven-ai-video-workflow`: use public snapshots as source evidence
  and topic material.
- `math-model-board-animation`: use comment mining to choose examples and
  educational angles.
- future web console: display candidate videos, extracted comments, captured
  evidence, and analysis state.

## Boundaries

- Do not commit `.auth/`, `.cheat-cache/`, browser profiles, or downloaded raw
  media.
- Keep public-page capture separate from creator-dashboard capture.
- Keep adapter output append-only when used for experiments, so a good version
  can be traced and restored.
- Treat platform HTML and private APIs as unstable. Store screenshots and raw
  response URLs so failures can be debugged later.
