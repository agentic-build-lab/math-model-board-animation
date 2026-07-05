# Recipe: GARCH volatility memory candidate

## Purpose

A premium blackboard-style quantitative finance sample that visualizes GARCH volatility clustering. This is currently the best candidate for a reusable project example once mp4 encoding and CJK fonts are available.

## Input config

- `examples/garch_volatility_scene.json`
- Scene id: `garch_volatility_memory`
- Chart type: `volatility_area`
- Duration: 3.9 seconds, 1920x1080, 60 fps

## Key visual parameters

Implemented in `packages/model_animation/styles/blackboard_formula.py`:

- Vertical mapping: `0.10 + y_norm * 0.76`, leaving comfortable top/bottom space.
- Area fill: `alpha_low=42`, `alpha_high=108`, preserving a light premium red wash.
- Main curve: width `4`, red core, reduced glow alpha `105`, glow width `9`, blur radius `1.25`.
- Formula y position: about `75.5%` of frame height.

## Render command

```bash
python scripts/render_model_video.py --config examples/garch_volatility_scene.json
```

## Latest reviewed output

- Directory: `outputs/renders/garch_volatility_memory/v20260705T100110Z_garch_volatility_scene/`
- Draft preview: `preview.html`
- Contact sheet: `garch_volatility_scene_v20260705T100110Z_contact_sheet.jpg`
- Report: `render_report.json`
- Review gate: `review_notes.md`

## Quality judgment

- Current label: `candidate`.
- Keep as active baseline because it demonstrates the intended shallow-fill + bright-contour style.
- Not yet `approved_case` because current cloud worker has no `ffmpeg` and no final CJK font package.

## Failure paths learned

- Heavy red fill makes the chart look cheap and hides the curve.
- Over-strong glow makes the line feel neon rather than premium.
- Peak mapping too high collides visually with title/subtitle area.
- Without ffmpeg, WebP/HTML preview is useful for draft motion screening but cannot replace final mp4 review.
