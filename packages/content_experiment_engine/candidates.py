from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit


@dataclass(slots=True)
class Candidate:
    id: str
    title: str
    source: str
    snapshot_text: str
    snapshot_at: str
    url: str | None = None
    tier: str | None = None
    read_status: str | None = "unread"
    category: str | None = None
    composite_score: float | None = None
    dimension_scores: dict[str, int] | None = None
    scored_under_rubric_version: str | None = None
    predicted_bucket: str | None = None
    predicted_reason: str | None = None
    note: str | None = None
    risk_flags: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def candidate_id(source: str, title: str, url: str | None = None) -> str:
    """Stable 12-character id for dedupe across adapters."""
    source_type = (source.split(":", 1)[0] or source).strip().lower()
    normalized_title = re.sub(r"\s+", "", title.strip().lower())
    url_path = _normalized_url_path(url)
    raw = f"{source_type}|{normalized_title}|{url_path}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def normalize_candidate(
    *,
    title: str,
    source: str,
    snapshot_text: str | None = None,
    url: str | None = None,
    snapshot_at: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
    raw: dict[str, Any] | None = None,
) -> Candidate:
    active_snapshot_text = snapshot_text or title
    active_snapshot_at = snapshot_at or datetime.now(UTC).isoformat()
    return Candidate(
        id=candidate_id(source, title, url),
        title=title.strip(),
        source=source.strip(),
        snapshot_text=active_snapshot_text.strip(),
        snapshot_at=active_snapshot_at,
        url=_without_query(url) if url else None,
        category=category,
        tags=tags or [],
        raw=raw or {},
    )


def _normalized_url_path(url: str | None) -> str:
    if not url:
        return ""
    parsed = urlsplit(url)
    return urlunsplit(("", parsed.netloc.lower(), parsed.path.rstrip("/"), "", ""))


def _without_query(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
