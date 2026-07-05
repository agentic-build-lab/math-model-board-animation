# Content State Protocol

This document adapts the upstream state-management protocol into a Codex-friendly
JSON state file.

The local state file is named `content_experiment_state.json` by default. It is
project-local and contains workflow configuration, calibration counters, enabled
sources, and learning artifact locations.

## Default State

The state is created by:

```powershell
python scripts\initialize_content_learning_artifacts.py `
  --output-dir outputs\content_experiment\learning_workspace `
  --project-name evidence_video_account
```

Important fields:

| Field | Meaning |
|---|---|
| `schema_version` | Current state schema version. |
| `content_form` | Content type, such as mixed, tutorial, short_video, or long_video. |
| `rubric_version` | Scoring rule version used for predictions. |
| `calibration_samples` | Count of completed retros that can calibrate predictions. |
| `confidence` | Derived from calibration sample count. |
| `benchmark_status` | none, pending, or imported. |
| `enabled_trend_sources` | Manual, public, MCP, or future source adapters. |
| `enabled_perf_adapters` | Authorized performance adapters. |
| `learning_artifacts` | Paths for audience, benchmark, and script pattern files. |
| `blind_boundary` | Files forbidden for blind scoring. |

## Confidence Bands

The module derives confidence from `calibration_samples`:

| Samples | Key | Meaning |
|---:|---|---|
| 0 | `none` | Data collection only. |
| 1-2 | `very_low` | Directional signal at best. |
| 3-5 | `low` | Buckets are usable as weak input. |
| 6-10 | `medium` | Scores can participate in decisions. |
| 11-20 | `high` | Rubric shape is becoming stable. |
| 21+ | `data_driven` | Use statistics before changing weights. |

Code entry points:

- `packages.content_experiment_engine.content_state.create_initial_state`
- `packages.content_experiment_engine.content_state.read_state`
- `packages.content_experiment_engine.content_state.write_state`
- `packages.content_experiment_engine.content_state.confidence_for_samples`

## Migration Rules

State changes should follow these rules:

1. Add fields when possible; avoid deleting or renaming fields.
2. Readers should use defaults for missing optional fields.
3. Any semantic change should bump `schema_version`.
4. Migrations should be explicit, idempotent, and documented.
5. A failed migration should leave diagnostic evidence in place.

This keeps Codex Cloud, local Codex, and future frontends compatible while the
workflow evolves.
