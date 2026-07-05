# Sample gallery and review manifest

This gallery is a human-readable index of the current reviewable samples. It points to local render artifacts but does not require committing media files.

## Latest reviewable samples

| Scene | Version | Quality label | Recommended as case? | View locally | Config | Command | Review notes | Parameter / decision notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GARCH volatility memory | `v20260705T100110Z` | `candidate` | Yes, after mp4 + CJK font check | `outputs/renders/garch_volatility_memory/v20260705T100110Z_garch_volatility_scene/preview.html` | `examples/garch_volatility_scene.json` | `python scripts/render_model_video.py --config examples/garch_volatility_scene.json` | `outputs/renders/garch_volatility_memory/v20260705T100110Z_garch_volatility_scene/review_notes.md` | Cleaner baseline: shallow red fill, clear 4 px line, reduced glow, safer vertical mapping |
| CAPM beta regression | `v20260705T100222Z` | `candidate` | Yes, as second-model proof after human motion review | `outputs/renders/capm_beta_regression/v20260705T100222Z_capm_regression_scene/preview.html` | `examples/capm_regression_scene.json` | `python scripts/render_model_video.py --config examples/capm_regression_scene.json` | `outputs/renders/capm_beta_regression/v20260705T100222Z_capm_regression_scene/review_notes.md` | Teal points + gold fit line validates scatter/regression chart path |
| Loss surface pseudo-3D | `v20260705T100313Z` | `prototype` | Not yet; keep as 3D exploration | `outputs/renders/loss_surface_minimum/v20260705T100313Z_loss_surface_scene/preview.html` | `examples/loss_surface_scene.json` | `python scripts/render_model_video.py --config examples/loss_surface_scene.json` | `outputs/renders/loss_surface_minimum/v20260705T100313Z_loss_surface_scene/review_notes.md` | Useful 3D direction; needs stronger semantic labels and mp4 review before promotion |

## Retention decision

- Keep the latest three bundles for active review because each has contact sheet, report, config snapshot, review notes, WebP preview and HTML preview.
- Do not commit those media bundles to Git.
- If disk cleanup is needed, keep GARCH and CAPM bundles first, keep loss surface report/config/contact sheet, and delete any older frame sequences under `work/rendered_frames/`.

## Promotion gate

A sample can become an `approved_case` only when all are true:

1. `render_report.json` has `encode_status: success`.
2. Chinese title/subtitle/caption uses a real CJK font, not fallback boxes.
3. Contact sheet passes composition review.
4. mp4 passes motion review.
5. Reproduction recipe exists in `docs/recipes/` or `docs/codex_skill_plan.md`.
