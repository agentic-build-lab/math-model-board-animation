# Recipe: Factor exposure surface showcase

## Goal

A 24-second pseudo-3D quant-finance sample that presents factor exposure as a calm, premium surface rather than a noisy HUD. It extends the loss-surface grammar into a finance model setting.

## Input config

- `examples/factor_exposure_surface_scene.json`
- Scene id: `factor_exposure_surface`
- Chart type: `rotating_surface`
- Animation chart mode: `surface_showcase_orbit`
- Spec: 1920x1080, 30 fps, 24 seconds

## Timing grammar

| start_ms | end_ms | Segment | Rule |
| --- | --- | --- | --- |
| 0 | 2000 | Hook | Title + empty stage; no factor definition pile-up |
| 2000 | 7000 | Construction | Sparse surface grid builds slowly |
| 7000 | 14000 | Model identity | Formula appears while surface remains legible |
| 14000 | 21000 | Focus point | Gold point marks portfolio/regime focus |
| 21000 | 24000 | Hold | Stable formula + surface pause |

## Quality gate

- Surface grid is structural, not decorative.
- Gold point should read as a model focus/regime point.
- Formula must stay legible during orbit.
- Use WebP/HTML preview for draft rhythm only; mp4 requires `ffmpeg`.

## Render command

```bash
python scripts/render_model_video.py --config examples/factor_exposure_surface_scene.json
```

## Failure paths to avoid

- Treating factor names as dense labels on every grid point.
- Adding heavy HUD frames that compete with formula.
- Rotating too fast and making the surface unreadable.
