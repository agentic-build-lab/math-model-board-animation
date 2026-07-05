# Recipe: GARCH 24-second teaching version

## Goal

A longer teaching-pause variant that expands the compressed GARCH sample into calm / shock / clustering / decay beats.

## Input config

- `examples/garch_teaching_scene.json`
- Scene id: `garch_volatility_teaching`
- Chart type: `volatility_area`
- Animation chart mode: `staged_volatility_teaching`
- Spec: 1920x1080, 30 fps, 24 seconds

## Timing beats

| start_ms | end_ms | Beat | Purpose |
| --- | --- | --- | --- |
| 0 | 2000 | Hook | Title/subtitle only; no text pile-up |
| 2000 | 6000 | Formula identity | Core GARCH formula appears before full curve construction |
| 6000 | 10000 | Calm | Low-volatility baseline |
| 10000 | 14000 | Shock | Conditional variance rises toward spike |
| 14000 | 18500 | Clustering | Elevated volatility persists |
| 18500 | 22000 | Decay | Volatility slowly settles |
| 22000 | 24000 | Teaching pause | Hold formula and full curve for narration |

## Render command

```bash
python scripts/render_model_video.py --config examples/garch_teaching_scene.json
```

## Quality gate

- Stage labels must clarify, not clutter.
- Curve and formula remain the visual hierarchy.
- End frame must be useful as a pause screen.
- Current cloud can create WebP/HTML preview; mp4 requires `ffmpeg`.
