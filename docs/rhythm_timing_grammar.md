# Timing grammar for model animation samples

## Required event fields

Each config may include `scene.timing_events[]` with:

- `start_ms`: event start in milliseconds.
- `end_ms`: event end in milliseconds.
- `visual_action`: what changes on screen.
- `camera_action`: camera or framing behavior.
- `text_density`: `none`, `low`, `medium`, or `high`.
- `comfort_note`: readability and motion-comfort constraint.

## Full 24-second teaching / showcase grammar

| Segment | Time | Rule |
| --- | --- | --- |
| Hook | 0-2s | First visual hook; do not pile on text. |
| Identity | 2-6s | Model name/core formula appears; graph begins motion. |
| Construction | 6-14s | Build main graph; one clear change every 1.5-3s. |
| Highlight | 14-24s | Key point/interval/parameter; slight push-in or local emphasis. |
| Teaching pause | final 2-4s | Hold clear formula and graph for explanation. |

## Compressed 4-second sample grammar

| Segment | Time | Rule |
| --- | --- | --- |
| Hook | 0-1s | Establish title and visual plane with low text density. |
| Build | 1-2.4s | Draw curve, reveal points, or construct surface. |
| Conclusion hold | 2.4s-end | Show key formula/line/focus point and hold. |

## Current config coverage

- `examples/garch_volatility_scene.json` includes compressed timing events for axis/curve/formula hold.
- `examples/capm_regression_scene.json` includes compressed timing events for plane/points/beta line.
- `examples/loss_surface_scene.json` includes compressed timing events for 3D stage/surface/focus point.
