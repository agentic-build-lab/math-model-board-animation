# Observation Lifecycle Protocol

This document adapts the upstream observation-lifecycle rule into this
repository.

The rule is simple: current working files should describe what is true now, not
serve as a museum of every idea the system once believed.

## Stages

| Stage | Meaning | Typical Location |
|---|---|---|
| single_observation | One retro suggests a pattern. | retro or memo |
| cross_sample_observation | The same pattern appears across samples. | rubric memo or observation table |
| working_hypothesis | Worth testing, not yet a rule. | rubric memo |
| active_rule | Validated enough to influence scoring or drafting. | rubric notes or script patterns |
| absorbed | Merged into a dimension, weight, or stronger pattern. | remove from working list |
| disproven | Later data contradicts it. | remove from working list |

## Promotion Discipline

- One sample can create an observation, not a permanent rule.
- Two to four samples can create a hypothesis.
- Five or more calibrated samples can justify qualitative rule changes.
- Ten or more samples can justify small weight changes.
- Twenty or more samples can support data-driven analysis.

These thresholds are guidance, not mechanical truth. If a rule is promoted with
less data, the reason must be explicit.

## Cleanup Rules

Remove observations from the current working file when:

- the idea is absorbed into a formal dimension or pattern;
- newer data disproves it;
- the rule is stale and no longer influences decisions.

Keep the historical explanation in git history or a short bump memo, not inside
the live rule file.

## Blind Safety

Blind-safe files must not contain named samples plus actual outcomes. Keep
actual performance data in retros, calibration reports, or rubric memos.

Use:

```powershell
python scripts\check_blind_boundaries.py rubric_notes.md
```
