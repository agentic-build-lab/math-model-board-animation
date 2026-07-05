# Changelog

## 2026-07-05 — Versioned renders, second model, and 3D prototype

- Added non-overwriting render directories with per-run config snapshots, change notes, review notes, render reports, and manifest append behavior.
- Added cloud-safe font fallbacks for Linux render workers without Windows fonts.
- Tuned GARCH area chart toward a cleaner premium look: shallower fill, clearer line, reduced glow, and safer vertical spacing.
- Added CAPM scatter-regression sample to validate a second model family.
- Added a low-cost pseudo-3D loss-surface prototype to test future 3D model animation direction.
- Documented visual baselines, experiment tracking, SQL schema planning, and skill extraction notes.
- Known blocker: current cloud environment has no `ffmpeg`; rendered contact sheets and reports are available, but mp4 output requires a worker image with `ffmpeg` installed.
