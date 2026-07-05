# Review gate: GARCH / CAPM / loss surface

## Shared premium visual baseline

- Highlight should be clear but not sharp-neon: glow alpha should stay below the core line emphasis.
- Fill should be shallow and transparent; the line, points, and formula carry the information hierarchy.
- Main contours should be thin-bright rather than thick-saturated.
- Vertical placement should leave 10%-14% headroom and should not collide with title/subtitle.
- Peaks, fitted lines, and 3D focus points need visually pleasant positions, not just mathematically extreme positions.

## GARCH volatility area

- Current target: area fill `alpha_low=42`, `alpha_high=108`; main line width `4`; glow alpha `105`; vertical mapping `10%-86%`.
- Pass if the volatility cluster reads clearly in contact sheet without turning into a red block.
- Fail if the peak touches the subtitle area or the fill dominates the line.

## CAPM scatter regression

- Current target: teal points at moderate opacity, gold regression line after point reveal, white core only as subtle structure cue.
- Pass if beta line is readable and point cloud feels statistical rather than random noise.
- Fail if points look like background particles or the line arrives too late for a 4-second clip.

## Loss surface pseudo-3D

- Current target: cyan grid, low blur glow, gold focus point, slow oscillating viewing angle.
- Pass if the surface shape is legible from contact sheet and draft WebP preview.
- Fail if the grid looks like generic sci-fi decoration without communicating model landscape.

## Rhythm review overlay

### GARCH compressed timing

| start_ms | end_ms | visual_action | camera_action | text_density | comfort_note |
| --- | --- | --- | --- | --- | --- |
| 0 | 1200 | Title/subtitle fade in; empty chart stage | Locked wide | low | Hook should feel visual, not textual |
| 1200 | 2600 | Axis + curve + shallow area build | Locked wide | medium | Keep red fill soft |
| 2600 | 3900 | Cluster completes and formula holds | Locked wide | medium | Final frame must be pause-ready |

### CAPM compressed timing

| start_ms | end_ms | visual_action | camera_action | text_density | comfort_note |
| --- | --- | --- | --- | --- | --- |
| 0 | 900 | Title and return-return plane | Locked wide | low | Do not show too many words before points |
| 900 | 2200 | Teal observations fade into cloud | Locked wide | medium | Points should read as data, not particles |
| 2200 | 4200 | Gold beta line draws and holds | Locked wide | medium | Line is the conclusion; hold it cleanly |

### Loss surface compressed timing

| start_ms | end_ms | visual_action | camera_action | text_density | comfort_note |
| --- | --- | --- | --- | --- | --- |
| 0 | 1000 | Title reveals; empty 3D stage breathes | Locked wide | low | Avoid HUD clutter |
| 1000 | 2400 | Cyan surface grid constructs with slow rotation | Subtle orbit | medium | Motion must not feel decorative |
| 2400 | 3600 | Gold focus point and formula hold | Rotation slows | medium | End frame should support narration |
