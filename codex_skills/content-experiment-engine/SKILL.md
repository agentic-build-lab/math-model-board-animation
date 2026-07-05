---
name: content-experiment-engine
description: Use when Codex needs to discover content topics, score candidates, generate video workflow briefs, capture public video performance, create immutable predictions, append retrospectives, or connect trend and public-feedback signals to evidence videos, model animations, AI editing workflows, or quant research.
---

# Content Experiment Engine

Use this skill as the Codex-facing wrapper around `packages/content_experiment_engine`.
Prefer JSON, SQLite, and CLI contracts over ad hoc notes.

## Decision Tree

1. User wants topic ideas or hot topics:
   - Run `scripts/discover_content_topics.py`.
   - Use `--source manual` when the user gives topics.
   - Use `--source zhihu_hot` or `--source weibo_hot` only as best-effort public sources; they may return zero when blocked.

2. User gives a public video URL:
   - Run `scripts/analyze_public_video.py`.
   - Use `--platform douyin --headed` for Douyin comments on a local machine.
   - Use `--platform bilibili` for Bilibili public metrics and comments.

3. User wants a video production plan:
   - Generate candidates and briefs first.
   - Check platform-specific scoring with `platform_profiles` when the target
     platform is known.
   - Route the brief to `evidence_driven_ai_video`, `math_model_board_animation`, `ai_editing_workflow`, or `quant_signal_research`.

4. User wants prediction or calibration:
   - Create a prediction before viewing performance data.
   - Use `scripts/create_content_prediction.py`.
   - Append reviews with `scripts/append_content_retro.py`.
   - Use `scripts/export_calibration_report.py` after retros contain actual outcomes.
   - Never edit the `## Prediction` section after creation.

5. User gives a transcript, SRT, VTT, or ASR output:
   - Normalize it with `scripts/create_transcript_artifact.py`.
   - Import it to SQLite with `--database` when it should be used across workflows.
   - Keep downloading, ASR, and publishing outside this normalization step.

6. User wants a project status or handoff:
   - Export a markdown report with `scripts/export_content_review.py`.

7. User asks whether a trend can affect trading:
   - Treat it as a research hypothesis only.
   - Require entity linking, event timestamps, market data validation, and leakage checks.
   - Do not treat social heat as a direct trading signal.

## Commands

Manual candidate to video brief:

```powershell
python scripts\discover_content_topics.py `
  --source manual `
  --topic "AI agents for video production" `
  --target-workflow evidence_driven_ai_video `
  --output-dir outputs\content_experiment\topic_demo `
  --database outputs\content_experiment\content_experiment.db
```

Douyin public video:

```powershell
python scripts\analyze_public_video.py `
  --platform douyin `
  --url "https://www.douyin.com/video/<aweme_id>" `
  --headed `
  --output-dir outputs\content_experiment\douyin_<aweme_id>
```

Bilibili public video:

```powershell
python scripts\analyze_public_video.py `
  --platform bilibili `
  --url "https://www.bilibili.com/video/<BV_ID>" `
  --output-dir outputs\content_experiment\bilibili_<BV_ID>
```

Create immutable prediction:

```powershell
python scripts\create_content_prediction.py `
  --candidate-id "<id>" `
  --title "<title>" `
  --target-workflow evidence_driven_ai_video `
  --predicted-bucket tier2 `
  --reason "HP and SR are strong, evidence is available." `
  --output outputs\content_experiment\predictions\<id>.md
```

Append retro:

```powershell
python scripts\append_content_retro.py `
  --prediction outputs\content_experiment\predictions\<id>.md `
  --text "### T+3 review`n- Actual metrics captured.`n- Comment pattern: ..."
```

Normalize transcript:

```powershell
python scripts\create_transcript_artifact.py `
  --source "samples\creator_video.mp4" `
  --transcript-file "outputs\content_experiment\raw_transcript.srt" `
  --output-dir outputs\content_experiment\transcripts\creator_video `
  --engine whisper_or_manual `
  --language zh `
  --database outputs\content_experiment\content_experiment.db
```

Export SQLite review:

```powershell
python scripts\export_content_review.py `
  --database outputs\content_experiment\content_experiment.db `
  --output outputs\content_experiment\content_review.md
```

Export platform profiles:

```powershell
python scripts\export_platform_profiles.py `
  --output outputs\content_experiment\platform_profiles.json
```

Compare script or transcript drift:

```powershell
python scripts\compare_text_similarity.py old_script.md new_script.md
```

Export calibration report:

```powershell
python scripts\export_calibration_report.py `
  --predictions outputs\content_experiment\predictions `
  --output-md outputs\content_experiment\calibration_report.md `
  --output-csv outputs\content_experiment\calibration_samples.csv
```

## Output Contracts

- Candidate schema: `schemas/content_candidate.schema.json`
- Video brief schema: `schemas/video_topic_brief.schema.json`
- Public video snapshot schema: `schemas/content_video_snapshot.schema.json`
- Transcript artifact schema: `schemas/transcript_artifact.schema.json`
- Platform profile schema: `schemas/platform_profile.schema.json`
- SQLite schema: `schemas/content_experiment.schema.sql`

## Rules

- Keep runtime outputs under `outputs/content_experiment/`.
- Do not commit `.auth/`, `.cheat-cache/`, raw browser profiles, large media, or raw copyrighted videos.
- Do not auto-publish content. Preserve a review gate.
- Do not rewrite prediction text after performance data is known.
- Preserve old versions with timestamped output directories or Git commits.
- When an adapter returns zero candidates, report that source as blocked or empty; do not invent hot topics.

## References

- Upstream audit: `docs/cheat_on_content_upstream_audit.md`
- Integration plan: `docs/content_experiment_engine_integration_plan.md`
- Module guide: `docs/content_experiment_module.md`
- Calibration protocol: `docs/calibration_protocol.md`
- Experimental platform adapter contracts: `integrations/experimental_platform_adapters/`
