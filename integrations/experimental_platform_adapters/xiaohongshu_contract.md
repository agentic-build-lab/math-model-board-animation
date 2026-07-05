# Xiaohongshu Adapter Contract

Status: design migrated, executable crawler not vendored.

The upstream adapter combines public-page parsing, Playwright observation, and
authorized creator/ecommerce data. This repository preserves the useful design
while keeping auth state and browser artifacts out of Git.

## Two Tracks

### Public Observation

Use for internal research only:

- note URL or note id;
- visible title/body/tags when public page parsing works;
- visible engagement counters when available;
- top public comments when available;
- screenshot path if captured.

Readiness: `best_effort_public_observation`.

### Authorized Ecommerce Or Creator Data

Use only when the user owns or has permission for the account/store:

- creator note list;
- note performance;
- store/category/product signals;
- comment objections and purchase questions;
- archive summaries.

Readiness: `authorized_only`.

## Proposed Output

- public notes normalize into `content_video_snapshot` or a future
  `content_note_snapshot`;
- ecommerce/store signals should be stored as a separate authorized signal
  artifact, not mixed with public observations;
- comments should normalize into the same comment-mining input shape used by
  Douyin, Bilibili, and YouTube.

## Required Runtime Isolation

Use ignored paths:

- `.auth-xhs/` for login state;
- `.cheat-cache/xhs-explore-debug/` for debug screenshots and raw URL dumps;
- `outputs/content_experiment/xiaohongshu/` for normalized outputs.

Never commit these paths.

## Scoring Emphasis

The platform profile already captures the main weights:

- search intent;
- save/collect intent;
- cover and title strength;
- commercial intent;
- comment objections;
- product/category trend fit.

## Future Module Names

- `xiaohongshu_public_observation.py`
- `xiaohongshu_authorized_ecommerce.py`
- `scripts/analyze_xiaohongshu_note.py`

## Blockers Before Executable Migration

- decide whether the first implementation targets public observation or
  authorized ecommerce;
- define a redacted fixture shape;
- avoid committing browser state, cookies, or raw platform media;
- add explicit rate and review gates.
