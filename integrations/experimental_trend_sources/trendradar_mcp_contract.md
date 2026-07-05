# TrendRadar MCP Source Contract

This contract adapts the upstream TrendRadar MCP idea into this repository's
candidate-discovery model.

## Purpose

Use a multi-platform trend aggregation service as an optional source for:

- public hot topics;
- cross-platform topic comparison;
- sentiment or trend direction enrichment;
- early candidate discovery for evidence-driven videos.

## Integration Boundary

TrendRadar should remain an optional external MCP integration. This repository
does not vendor the TrendRadar server, data store, or runtime.

## Useful Operations

- latest news or hot-list fetch;
- keyword search;
- topic trend analysis;
- period comparison;
- sentiment summary.

## Normalized Output

Every returned item should become a `content_candidate` with:

- title;
- source such as `trend:trendradar`;
- readable snapshot text;
- source URL when available;
- timestamp;
- raw metadata under `raw`.

## Degradation

If the MCP server is not installed, not reachable, or times out, topic discovery
should continue with other enabled sources or manual input.
