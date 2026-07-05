# Douyin Session Adapter Contract

Status: design migrated, executable crawler not vendored.

The upstream adapter uses Playwright with persistent browser login state to
inspect the creator center and public video pages. This repository keeps only
the reusable contract and safety rules.

## Purpose

Collect user-authorized Douyin creator performance data for the user's own
videos:

- video list;
- public video metadata;
- public comments;
- creator metrics when available, such as completion or retention fields;
- markdown report for retrospective analysis.

## Proposed Output

The adapter should normalize to the existing snapshot/report contracts:

- `content_video_snapshot` for public metrics and comments;
- optional `creator_private_metrics` section for authorized owner-only metrics;
- `report.md` for human review;
- raw response paths under ignored runtime output folders only.

## Required Runtime Isolation

Use these ignored paths:

- `.auth/` for browser login state;
- `.cheat-cache/douyin-session-debug/` for debug URL dumps and screenshots;
- `outputs/content_experiment/douyin_session/` for normalized output.

Never commit these paths.

## Implementation Notes

- Use Playwright persistent context only in local or explicitly authorized
  environments.
- Prefer official Open Platform APIs for product-facing workflows when scopes
  are available.
- Public-page capture remains `best_effort_public_observation`.
- Session collection should require an explicit command, never automatic
  background scraping.

## Future Module Names

- `douyin_authorized_session.py`
- `scripts/analyze_authorized_douyin.py`

## Blockers Before Executable Migration

- confirm account authorization boundary;
- decide whether this remains local-only;
- add a redacted fixture format;
- add tests that do not require browser login.
