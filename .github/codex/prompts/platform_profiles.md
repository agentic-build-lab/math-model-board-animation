# Codex Task: Platform Profiles

Read:

- `docs/platform_expansion_roadmap.md`
- `docs/cloud_codex_platform_tasks.md`
- `packages/content_experiment_engine/rubric.py`
- `packages/content_experiment_engine/brief_generator.py`
- `tests/test_content_experiment_engine.py`

Task 2 is already implemented. Continue by reviewing and improving the existing
profile weights only if the current tests and docs show a clear gap.

Constraints:

- Keep profiles data-driven and easy to edit.
- Do not break existing `score_candidate`.
- Add clear default profiles for:
  - `youtube_long`
  - `youtube_shorts`
  - `bilibili`
  - `douyin`
  - `tiktok`
  - `x`
  - `xiaohongshu`
- Include readiness labels and unavailable metric notes.
- Add tests for weight normalization and profile lookup.

Before finishing, run:

```powershell
python -m unittest tests.test_content_experiment_engine
python -m compileall packages\content_experiment_engine tests\test_content_experiment_engine.py
```
