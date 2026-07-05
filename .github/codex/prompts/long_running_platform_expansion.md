# Codex Long-Running Task: Platform Expansion Engine

You are working on the `content_experiment_engine` direction. Do not treat this
as a one-step task. Work through the backlog in order, committing small,
reviewable milestones when each one passes tests.

## Read First

- `AGENTS.md` if present.
- `docs/platform_expansion_roadmap.md`
- `docs/cloud_codex_platform_tasks.md`
- `docs/content_experiment_module.md`
- `codex_skills/content-experiment-engine/SKILL.md`
- `.github/codex/prompts/youtube_public_adapter.md`

## Execution Protocol

1. Start with Task 1: YouTube public adapter.
2. Preserve existing Douyin and Bilibili behavior.
3. Add small synthetic fixtures/tests first; live API probes are optional and
   only run when credentials are present.
4. After a milestone passes, update docs and the status table below.
5. Continue to the next task unless genuinely blocked.
6. If blocked, write the blocker into `docs/cloud_codex_platform_tasks.md` and
   stop with a clear next action.
7. Do not commit secrets, runtime outputs, browser profiles, raw videos,
   `node_modules`, or cache directories.

## Backlog Order

1. YouTube public adapter.
2. YouTube creator brief exporter.
3. Comment mining and audience-question clustering.
4. TikTok and X feasibility spike.
5. Xiaohongshu feasibility spike.
6. Evidence production package exporter.
7. Model animation scene config exporter.
8. AI editing shot-list exporter.
9. Web console skeleton for candidates, snapshots, predictions, and retros.

## Completion Standard

Each completed milestone should include:

- source code or docs as appropriate;
- tests or a clear reason tests are not applicable;
- compile check;
- docs update;
- no large generated artifacts in Git;
- a concise final summary with exact files changed.

## Required Checks

Run the smallest meaningful checks for the files changed. For Python module
changes, run:

```powershell
python -m unittest tests.test_content_experiment_engine
python -m compileall packages scripts tests
```

If the environment uses a virtualenv, use that interpreter instead.
