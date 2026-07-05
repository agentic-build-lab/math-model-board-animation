# Blind Prediction Protocol

This repository keeps the upstream blind-prediction principle, but implements it
as ordinary files, CLI checks, and Python modules rather than Claude-specific
hooks.

## Definition

A prediction is blind only if it is written before the predictor sees any
post-publication performance data for that exact content item.

Performance data includes:

- views, plays, reads, impressions;
- likes, comments, shares, saves, coins, danmaku;
- retention, completion, follower conversion;
- top comments or screenshots captured after publication;
- ranking, trending placement, or creator-dashboard metrics.

Historical examples and benchmark performance can be used for calibration, but
they must not leak into the blind scoring context for a new item.

## Immutable Prediction Section

Prediction files created by `scripts/create_content_prediction.py` contain a
`## Prediction v1` section and a `## Retro` section.

Rules:

- do not edit `## Prediction v1` after creation;
- append retros below `## Retro`;
- if a prediction must be redone, create a new redo file rather than rewriting
  the original;
- `append_retro` checks that the immutable prediction hash is unchanged.

## Forbidden Blind Inputs

These files are blocked for blind scoring:

- `audience.md`
- `benchmark.md`
- `script_patterns.md`
- `rubric-memo.md`
- `content_review.md`
- `calibration_report.md`

They are useful for drafting, retrospectives, product strategy, and rubric bump
analysis, but not for blind score generation.

## Leak Check

Before using a scoring rule file as blind-safe context:

```powershell
python scripts\check_blind_boundaries.py rubric_notes.md
```

This catches accidental actual-performance leakage while allowing bucket
boundaries and probability ranges.

## Practical Workflow

1. Score candidate and write prediction before viewing performance data.
2. Publish or produce the content.
3. Capture public or authorized metrics.
4. Append retro notes without editing prediction.
5. Use calibration reports and retros to update future rules.
