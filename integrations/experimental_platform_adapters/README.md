# Experimental Platform Adapters

This folder isolates adapter contracts that came from the upstream
`cheat-on-content` project but should not be copied directly into the main
runtime package yet.

The goal is to preserve useful implementation knowledge without polluting the
repository with browser profiles, cookies, caches, raw screenshots, large media,
or platform-specific scraper assumptions.

## What Can Live Here

- adapter contracts;
- field mappings;
- setup notes;
- expected input/output shapes;
- safety boundaries;
- TODOs for future implementation;
- small synthetic fixtures if needed later.

## What Must Not Live Here

- `.auth/`, `.auth-xhs/`, browser profiles, cookies, session state;
- `.cheat-cache/`, debug screenshots, raw API dumps;
- `node_modules/`, Playwright browser binaries, Chromium downloads;
- raw videos, downloaded platform media, rendered output videos;
- platform credentials, API keys, tokens, or account identifiers.

## Migrated Upstream Concepts

- Douyin session adapter: persisted login + passive XHR interception + report
  rendering. See `douyin_session_contract.md`.
- Xiaohongshu explore adapter: public page fallback + creator/authorized data
  track + report rendering. See `xiaohongshu_contract.md`.

Implementation should happen in a separate milestone only after the target
platform's authorization and compliance boundary is clear.
