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

`bilibili_public_video` captures public Bilibili video metadata and hot comments
through public HTTP APIs. It does not require login and is better suited for
repeatable public-video analysis.

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

Bilibili public video:

```powershell
python scripts\analyze_public_video.py `
  --platform bilibili `
  --url https://www.bilibili.com/video/BV1xx411c7mD `
  --output-dir outputs\content_experiment\bilibili_BV1xx411c7mD
```

## Output Contract

The adapter writes:

- `snapshot.json`: normalized data for downstream systems;
- `raw_responses.jsonl`: captured API responses for debugging. Request URLs are
  stored without query strings by default;
- `public_video_page.png`: evidence screenshot.

The JSON shape is defined in
`schemas/content_video_snapshot.schema.json`.

Topic discovery and brief generation:

```powershell
python scripts\discover_content_topics.py `
  --source manual `
  --topic "Codex content workflow" `
  --target-workflow evidence_driven_ai_video `
  --output-dir outputs\content_experiment\topic_discovery_demo
```

The candidate and brief shapes are defined in:

- `schemas/content_candidate.schema.json`
- `schemas/video_topic_brief.schema.json`

Snapshots can be imported into SQLite:

```powershell
python scripts\import_content_snapshot.py `
  --snapshot outputs\content_experiment\douyin_7636402601549974818\snapshot.json `
  --database outputs\content_experiment\content_experiment.db
```

The database schema is mirrored in `schemas/content_experiment.schema.sql`.

Platform-specific scoring profiles:

```powershell
python scripts\export_platform_profiles.py `
  --output outputs\content_experiment\platform_profiles.json
```

The profile schema is defined in `schemas/platform_profile.schema.json`.

Calibration and script-diff tools:

```powershell
python scripts\compare_text_similarity.py old_script.md new_script.md

python scripts\export_calibration_report.py `
  --predictions outputs\content_experiment\predictions `
  --output-md outputs\content_experiment\calibration_report.md `
  --output-csv outputs\content_experiment\calibration_samples.csv
```

The adapted calibration protocol is documented in
`docs/calibration_protocol.md`.

Transcript artifact generation adapts the upstream Whisper idea into a
Codex-friendly contract. The project does not force one ASR engine; it accepts
manual text, SRT, VTT, Whisper output, or cloud ASR output and normalizes it
into `transcript.json` and `transcript.md`:

```powershell
python scripts\create_transcript_artifact.py `
  --source samples\creator_video.mp4 `
  --transcript-file outputs\content_experiment\raw_transcript.srt `
  --output-dir outputs\content_experiment\transcripts\creator_video `
  --engine whisper_or_manual `
  --language zh `
  --database outputs\content_experiment\content_experiment.db
```

The transcript shape is defined in
`schemas/transcript_artifact.schema.json`.

Prediction records can be created and reviewed without relying on Claude hooks:

```powershell
python scripts\create_content_prediction.py `
  --candidate-id a16a0f05bde3 `
  --title "Codex content workflow" `
  --target-workflow evidence_driven_ai_video `
  --predicted-bucket tier2 `
  --reason "Strong hook and technical trend, but evidence needs review." `
  --output outputs\content_experiment\predictions\a16a0f05bde3.md

python scripts\append_content_retro.py `
  --prediction outputs\content_experiment\predictions\a16a0f05bde3.md `
  --text "### T+3 review`n- Metrics captured.`n- Comments suggest ..."
```

Codex skill draft:

- `codex_skills/content-experiment-engine/SKILL.md`

Human-readable SQLite review reports can be exported for inspection or handoff:

```powershell
python scripts\export_content_review.py `
  --database outputs\content_experiment\content_experiment.db `
  --output outputs\content_experiment\content_review.md
```

## Integration Direction

Recommended downstream users:

- `evidence-driven-ai-video-workflow`: use public snapshots as source evidence
  and topic material.
- `math-model-board-animation`: use comment mining to choose examples and
  educational angles.
- future web console: display candidate videos, extracted comments, captured
  evidence, transcripts, briefs, and analysis state.

## Boundaries

- Do not commit `.auth/`, `.cheat-cache/`, browser profiles, or downloaded raw
  media.
- Keep public-page capture separate from creator-dashboard capture.
- Keep adapter output append-only when used for experiments, so a good version
  can be traced and restored.
- Treat platform HTML and private APIs as unstable. Store screenshots and raw
  response URLs so failures can be debugged later.
- Keep ASR, downloading, and publishing as separate stages. Transcript artifacts
  should be normalized before downstream analysis.
