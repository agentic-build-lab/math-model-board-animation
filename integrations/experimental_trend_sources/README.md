# Experimental Trend Sources

This folder holds trend-source contracts adapted from upstream.

Trend sources are input adapters for candidate discovery. They should output
normalized content candidates, not finished scripts and not direct publish
decisions.

Rules:

- source failure should degrade to manual input;
- every item must include readable `snapshot_text`;
- raw URLs alone are not enough;
- adapters should add source, timestamp, and stable ids;
- paid or external services must be optional.

Current contracts:

- `aihot_contract.md`
- `trendradar_mcp_contract.md`
