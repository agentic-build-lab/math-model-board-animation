# Codex Task: YouTube Public Adapter

Read:

- `docs/platform_expansion_roadmap.md`
- `docs/cloud_codex_platform_tasks.md`
- `docs/content_experiment_module.md`
- `packages/content_experiment_engine/bilibili_public_video.py`
- `packages/content_experiment_engine/snapshot_store.py`
- `scripts/analyze_public_video.py`
- `tests/test_content_experiment_engine.py`

Implement Task 1 from `docs/cloud_codex_platform_tasks.md`.

Constraints:

- Use only official YouTube Data API endpoints.
- Require `YOUTUBE_API_KEY` only for live calls, not for unit tests.
- Keep fixtures small and synthetic.
- Do not commit runtime outputs, secrets, browser caches, raw videos, or large
  media.
- Preserve existing Douyin and Bilibili behavior.

Before finishing, run:

```powershell
python -m unittest tests.test_content_experiment_engine
python -m compileall packages\content_experiment_engine scripts\analyze_public_video.py tests\test_content_experiment_engine.py
```

If `YOUTUBE_API_KEY` is present, run one live probe and document the result.
