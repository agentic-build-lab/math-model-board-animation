# LinkedIn Session Adapter Contract

This contract preserves the useful upstream LinkedIn adapter design without
vendoring Playwright scripts, cookies, or debug dumps into the main runtime.

## Purpose

Capture authorized post-level performance for the user's own LinkedIn posts or
pages they are permitted to inspect.

## Authorization Boundary

- Uses a persistent browser context after the user logs in.
- Session data belongs in project-local `.auth-linkedin/`.
- Debug DOM text belongs in `.cheat-cache/linkedin-session-debug/`.
- Neither directory should be committed.

## Input

```json
{
  "platform": "linkedin",
  "activity_id_or_url": "https://www.linkedin.com/feed/update/urn:li:activity:...",
  "script_path": "optional/path/to/script.md",
  "output_dir": "outputs/content_experiment/linkedin_post"
}
```

## Output

The eventual adapter should normalize to the repository snapshot contract:

- `snapshot.json`
- `raw_responses.jsonl` or `debug_dom.txt`
- optional evidence screenshot;
- `report.md` for human review.

Expected metrics:

- impressions;
- reactions;
- comments;
- reposts;
- author or page metadata when available.

## Failure Handling

- If login is missing or expired, return a clear `auth_required` status.
- If DOM labels change, write debug text and preserve the failing sample.
- If metrics are unavailable, emit nulls and a limitation note rather than
  fabricating values.

## Product Note

LinkedIn is useful for B2B creator analytics, but should remain authorized-only.
