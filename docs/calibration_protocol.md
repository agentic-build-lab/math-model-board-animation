# Calibration And Bump Protocol

This document adapts the useful parts of the upstream `cheat-on-content`
calibration workflow into this repository's content experiment engine.

## Principles

- Predictions are written before outcome data is reviewed.
- Retrospectives append new information; they do not rewrite the original
  prediction.
- Rubric changes are versioned and validated against existing samples.
- Calibration reports measure whether prediction error narrows over time.
- New platform weights should be treated as hypotheses until outcome data
  supports them.

## Migrated Tools

### Text Similarity

Use script/transcript diffing to decide whether a script changed enough to need
a new prediction:

```powershell
python scripts\compare_text_similarity.py old_script.md new_script.md
```

The underlying module is `packages.content_experiment_engine.text_similarity`.
It strips markdown and whitespace noise before computing a normalized diff
percentage.

### Calibration Report

Use prediction markdown files plus appended retro outcome values:

```powershell
python scripts\export_calibration_report.py `
  --predictions outputs\content_experiment\predictions `
  --output-md outputs\content_experiment\calibration_report.md `
  --output-csv outputs\content_experiment\calibration_samples.csv
```

For custom buckets, pass a JSON mapping:

```powershell
python scripts\export_calibration_report.py `
  --predictions outputs\content_experiment\predictions `
  --output-md outputs\content_experiment\calibration_report.md `
  --bucket-centers-json "{\"tier1\":100,\"tier2\":30,\"tier3\":10,\"skip\":1}"
```

## Bump Rules

A rubric or platform-profile bump is required when any of these change:

- formula weights;
- dimensions added or removed;
- dimension definitions rewritten materially;
- normalization constants changed.

Before accepting a bump:

1. Write the full old and new scoring formula.
2. Re-score all calibration samples that have complete retros.
3. Compare rank order against actual outcomes.
4. Record a memo explaining evidence, limitations, and expected behavior.
5. Append re-score notes; do not edit immutable prediction sections.

## Cadence Rules

- Review due retros before generating too many new predictions.
- Keep experiments limited when the production buffer is low.
- Keep stable recommendations and experimental recommendations separate.
- Do not treat one viral or failed sample as enough evidence for a permanent
  scoring change.
