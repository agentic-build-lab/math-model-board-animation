# Media retention policy

This project optimizes for reviewable, reproducible high-quality samples without committing large binary outputs to Git.

## Keep by default inside `outputs/renders/`

For every render version, keep the small-to-medium review bundle while the experiment is active:

- `render_report.json` — required audit metadata, environment, output paths, encode status, dimensions, fps and duration.
- `config_snapshot.json` — exact input needed to reproduce the run.
- `changes.md` — parameter and intent notes for the run.
- `review_notes.md` — human review gate and decisions.
- `*_contact_sheet.jpg` — fast composition review.
- `preview.html` and `*_preview.webp` — draft motion review when mp4 is blocked.
- Manifest entry in `outputs/renders/manifest.jsonl` — append-only local index.

## Keep selectively

- `*.mp4`: keep for candidate and approved samples, but do not commit to Git by default. Use release artifacts, object storage, Git LFS, or a media bucket when long-term retention is needed.
- Frame sequences under `work/rendered_frames/`: keep only during debugging or when a render failed before contact sheet/report generation. Delete after the version bundle is complete.
- Failed renders with no visual review value: keep `render_report.json` plus a short diagnostic note; remove frame dumps and heavyweight previews.

## Suggested quality labels

| Label | Meaning | Retention |
| --- | --- | --- |
| `approved_case` | Good enough to become a project/skill example after mp4 and font checks | Keep full review bundle + mp4 outside Git |
| `candidate` | Promising visual direction but needs human review or environment fix | Keep review bundle and preview |
| `prototype` | Useful for architecture or style exploration | Keep report/config/contact sheet; keep preview if small |
| `diagnostic_only` | Failed or ugly render, useful only for debugging | Keep report + notes; clean frames/previews |
| `reject_cleanup` | No longer useful | Keep changelog summary only, delete local media |

## Current cloud limitation

The current cloud worker still has no `ffmpeg` and no CJK font package. Until that is fixed, WebP/HTML previews and contact sheets are valid for draft review only. A sample cannot be promoted to `approved_case` until it has a successful mp4 encode and final Chinese font check.

## Git policy

Do not commit:

- `outputs/renders/**` media bundles.
- `work/rendered_frames/**` frame sequences.
- Big videos, fonts, ffmpeg binaries, credentials or secrets.

Do commit:

- Configs under `examples/`.
- Docs, recipes, review decisions and schema changes.
- Small source code and tests that make runs reproducible.
