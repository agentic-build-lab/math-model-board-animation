# Content Learning Artifacts

This document adapts the useful cold-start and long-term learning artifacts from
the upstream `cheat-on-content` workflow into this repository.

The important distinction is:

- scoring artifacts decide whether an idea is likely to perform;
- learning artifacts improve what we write, who we write for, and which
  references we trust;
- retrospective artifacts may contain actual performance data and must not be
  fed into blind scoring.

## Artifact Set

| Artifact | Purpose | Blind Scoring Access |
|---|---|---|
| `audience.md` | Data-derived audience profile from comments and retros. | forbidden |
| `benchmark.md` | Benchmark account imports and cold-start reference samples. | forbidden |
| `script_patterns.md` | Drafting structures, user edit patterns, and benchmark imports. | forbidden |
| `rubric_notes.md` | Current blind-safe scoring rules. | allowed if leak check passes |
| `rubric-memo.md` | Evidence, calibration tables, and bump rationale. | forbidden |

Use:

```powershell
python scripts\initialize_content_learning_artifacts.py `
  --output-dir outputs\content_experiment\learning_workspace `
  --project-name evidence_video_account `
  --benchmark-name "reference creator" `
  --platform youtube
```

This creates:

- `audience.md`
- `benchmark.md`
- `script_patterns.md`
- `content_experiment_state.json`

## Audience Profile

The audience profile answers "who is actually watching and reacting?" It should
be rebuilt from retrospectives, top comments, objections, repeat phrases, and
topic appetite.

Rules:

- verified traits need comment evidence;
- user guesses go under hypotheses until evidence confirms them;
- anti-persona evidence is valuable and should be kept visible;
- persona can guide drafting and topic choice, but not blind scoring.

## Benchmark Account

Benchmark imports are strongest during cold start. They provide:

- sample scripts or transcripts;
- public performance numbers or manually recorded impressions;
- user impression labels such as high, medium, or low;
- qualitative rubric signals;
- imported patterns marked as untested.

Do not turn 5-10 benchmark samples into numeric weights. Treat them as
directional priors until the local channel has calibration samples.

## Script Pattern Library

The pattern library teaches drafting. It should contain structures such as:

- scene plus reversal;
- direct data contrast;
- metaphor-first explanation;
- case-driven narrative;
- three-part compression;
- language and rhythm libraries.

Every pattern should be tagged by evidence state:

- `imported_untested`
- `pending_validation`
- `validated_local`
- `disproven`

Disproven patterns should be removed from the current working file after the
decision is captured in git history or a short memo.

## Blind Boundary

Check blind-safe files before using them in scoring:

```powershell
python scripts\check_blind_boundaries.py rubric_notes.md
```

The scanner flags metric words and performance numbers such as actual views,
plays, likes, comments, shares, retention, and conversion. Bucket boundaries are
allowed because they are rules, not observed outcomes.
