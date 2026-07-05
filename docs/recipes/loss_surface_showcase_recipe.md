# Recipe: Loss surface 30-second showcase

## Goal

A high-impact, future-facing model animation sample that uses a pseudo-3D loss basin, slow orbit, sparse labels, and a gold minimum point. The goal is premium model presence, not a cheap HUD effect.

## Input config

- `examples/loss_surface_showcase_scene.json`
- Scene id: `loss_surface_showcase`
- Chart type: `rotating_surface`
- Animation chart mode: `surface_showcase_orbit`
- Spec: 1920x1080, 30 fps, 30 seconds

## Timing beats

| start_ms | end_ms | Beat | Purpose |
| --- | --- | --- | --- |
| 0 | 2000 | Hook | Title and empty 3D stage; low text |
| 2000 | 6000 | Sparse construction | Surface begins forming; avoid dense HUD |
| 6000 | 14000 | Model identity | Surface completes; axes/formula appear |
| 14000 | 24000 | Minimum highlight | Gold minimum point becomes the focus |
| 24000 | 30000 | Showcase hold | Clean final card for teaching or commercial intro |

## Aesthetic parameters

- Cyan grid alpha remains low; glow is present but soft.
- Gold is reserved for the minimum point only.
- Labels are functional: `θ₁`, `θ₂`, and `min L(θ)`.
- Rotation must be slow enough to preserve comfort.

## Render command

```bash
python scripts/render_model_video.py --config examples/loss_surface_showcase_scene.json
```

## Rejection criteria

- Looks like generic sci-fi HUD instead of a model landscape.
- Gold point is visually lost or mislabeled.
- Motion is too fast for formula readability.
- Final frame cannot be used as a pause/title card.
