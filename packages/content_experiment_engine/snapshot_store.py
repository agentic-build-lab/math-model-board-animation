from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS content_video_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    adapter TEXT NOT NULL,
    source_url TEXT NOT NULL,
    resolved_url TEXT,
    platform_video_id TEXT,
    fetched_at TEXT NOT NULL,
    title TEXT,
    description TEXT,
    author TEXT,
    created_at TEXT,
    duration_ms INTEGER,
    play_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    collect_count INTEGER,
    screenshot_path TEXT,
    raw_response_path TEXT,
    snapshot_json TEXT NOT NULL,
    inserted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_video_comments (
    snapshot_id TEXT NOT NULL,
    comment_id TEXT NOT NULL,
    text TEXT NOT NULL,
    like_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    user_name TEXT,
    ip_label TEXT,
    inserted_at TEXT NOT NULL,
    PRIMARY KEY (snapshot_id, comment_id, text),
    FOREIGN KEY (snapshot_id) REFERENCES content_video_snapshots(snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_content_video_snapshots_platform_id
ON content_video_snapshots(platform, platform_video_id);

CREATE INDEX IF NOT EXISTS idx_content_video_comments_likes
ON content_video_comments(snapshot_id, like_count DESC);

CREATE TABLE IF NOT EXISTS content_candidates (
    candidate_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    snapshot_text TEXT NOT NULL,
    snapshot_at TEXT NOT NULL,
    url TEXT,
    tier TEXT,
    read_status TEXT,
    category TEXT,
    composite_score REAL,
    dimension_scores_json TEXT,
    rubric_version TEXT,
    predicted_bucket TEXT,
    predicted_reason TEXT,
    risk_flags_json TEXT,
    tags_json TEXT,
    raw_json TEXT,
    inserted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_scoring_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    rubric_version TEXT NOT NULL,
    dimension_scores_json TEXT NOT NULL,
    composite_score REAL,
    scored_at TEXT NOT NULL,
    scored_by TEXT,
    note TEXT,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS video_topic_briefs (
    brief_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    target_workflow TEXT NOT NULL,
    title TEXT NOT NULL,
    hook TEXT NOT NULL,
    video_angle TEXT NOT NULL,
    evidence_needed_json TEXT NOT NULL,
    suggested_assets_json TEXT NOT NULL,
    audience_questions_json TEXT NOT NULL,
    risk_notes_json TEXT NOT NULL,
    workflow_inputs_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS content_predictions (
    prediction_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    target_workflow TEXT NOT NULL,
    prediction_basis TEXT NOT NULL,
    blind_status TEXT NOT NULL,
    predicted_bucket TEXT,
    probability_json TEXT,
    reasoning_json TEXT,
    immutable_text_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS content_observations (
    observation_id TEXT PRIMARY KEY,
    candidate_id TEXT,
    source_snapshot_id TEXT,
    observation_type TEXT NOT NULL,
    observation_text TEXT NOT NULL,
    confidence TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id),
    FOREIGN KEY (source_snapshot_id) REFERENCES content_video_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS domain_signal_links (
    link_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    link_reason TEXT,
    validation_status TEXT NOT NULL DEFAULT 'unvalidated',
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);
"""


def init_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()


def import_snapshot(database_path: Path, snapshot_path: Path) -> str:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return upsert_snapshot(database_path, snapshot)


def import_candidates(database_path: Path, candidates_path: Path) -> list[str]:
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    return [upsert_candidate(database_path, candidate) for candidate in candidates]


def import_video_briefs(database_path: Path, briefs_path: Path) -> list[str]:
    briefs = json.loads(briefs_path.read_text(encoding="utf-8"))
    return [upsert_video_brief(database_path, brief) for brief in briefs]


def upsert_snapshot(database_path: Path, snapshot: dict[str, Any]) -> str:
    init_database(database_path)
    source = snapshot["source"]
    video = snapshot["video"]
    metrics = snapshot["metrics"]
    evidence = snapshot["evidence"]
    inserted_at = datetime.now(UTC).isoformat()
    snapshot_id = _snapshot_id(snapshot)
    snapshot_json = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO content_video_snapshots (
                snapshot_id, platform, adapter, source_url, resolved_url,
                platform_video_id, fetched_at, title, description, author,
                created_at, duration_ms, play_count, like_count, comment_count,
                share_count, collect_count, screenshot_path, raw_response_path,
                snapshot_json, inserted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                source["platform"],
                source["adapter"],
                source["url"],
                source.get("resolved_url"),
                source.get("platform_video_id") or source.get("aweme_id") or source.get("bvid"),
                source["fetched_at"],
                video.get("title"),
                video.get("description"),
                video.get("author"),
                video.get("created_at"),
                video.get("duration_ms"),
                metrics.get("play_count"),
                metrics.get("like_count"),
                metrics.get("comment_count"),
                metrics.get("share_count"),
                metrics.get("collect_count"),
                evidence.get("screenshot_path"),
                evidence.get("raw_response_path"),
                snapshot_json,
                inserted_at,
            ),
        )
        connection.executemany(
            """
            INSERT OR REPLACE INTO content_video_comments (
                snapshot_id, comment_id, text, like_count, reply_count,
                created_at, user_name, ip_label, inserted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    snapshot_id,
                    comment.get("id") or _comment_fallback_id(comment),
                    comment.get("text") or "",
                    comment.get("like_count") or 0,
                    comment.get("reply_count") or 0,
                    comment.get("created_at"),
                    comment.get("user_name"),
                    comment.get("ip_label"),
                    inserted_at,
                )
                for comment in snapshot.get("comments") or []
            ],
        )
        connection.commit()
    return snapshot_id


def upsert_candidate(database_path: Path, candidate: dict[str, Any]) -> str:
    init_database(database_path)
    inserted_at = datetime.now(UTC).isoformat()
    candidate_id_value = candidate["id"]
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO content_candidates (
                candidate_id, title, source, snapshot_text, snapshot_at, url,
                tier, read_status, category, composite_score,
                dimension_scores_json, rubric_version, predicted_bucket,
                predicted_reason, risk_flags_json, tags_json, raw_json,
                inserted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id_value,
                candidate["title"],
                candidate["source"],
                candidate["snapshot_text"],
                candidate["snapshot_at"],
                candidate.get("url"),
                candidate.get("tier"),
                candidate.get("read_status"),
                candidate.get("category"),
                candidate.get("composite_score"),
                json.dumps(candidate.get("dimension_scores"), ensure_ascii=False),
                candidate.get("scored_under_rubric_version"),
                candidate.get("predicted_bucket"),
                candidate.get("predicted_reason"),
                json.dumps(candidate.get("risk_flags") or [], ensure_ascii=False),
                json.dumps(candidate.get("tags") or [], ensure_ascii=False),
                json.dumps(candidate.get("raw") or {}, ensure_ascii=False),
                inserted_at,
            ),
        )
        if candidate.get("dimension_scores"):
            connection.execute(
                """
                INSERT INTO content_scoring_history (
                    candidate_id, rubric_version, dimension_scores_json,
                    composite_score, scored_at, scored_by, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id_value,
                    candidate.get("scored_under_rubric_version") or "unknown",
                    json.dumps(candidate.get("dimension_scores"), ensure_ascii=False),
                    candidate.get("composite_score"),
                    inserted_at,
                    "module",
                    candidate.get("predicted_reason"),
                ),
            )
        connection.commit()
    return candidate_id_value


def upsert_video_brief(database_path: Path, brief: dict[str, Any]) -> str:
    init_database(database_path)
    created_at = datetime.now(UTC).isoformat()
    brief_id = _brief_id(brief)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO video_topic_briefs (
                brief_id, candidate_id, target_workflow, title, hook,
                video_angle, evidence_needed_json, suggested_assets_json,
                audience_questions_json, risk_notes_json, workflow_inputs_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                brief_id,
                brief["candidate_id"],
                brief["target_workflow"],
                brief["title"],
                brief["hook"],
                brief["video_angle"],
                json.dumps(brief.get("evidence_needed") or [], ensure_ascii=False),
                json.dumps(brief.get("suggested_assets") or [], ensure_ascii=False),
                json.dumps(brief.get("audience_questions") or [], ensure_ascii=False),
                json.dumps(brief.get("risk_notes") or [], ensure_ascii=False),
                json.dumps(brief.get("workflow_inputs") or {}, ensure_ascii=False),
                created_at,
            ),
        )
        connection.commit()
    return brief_id


def _snapshot_id(snapshot: dict[str, Any]) -> str:
    source = snapshot["source"]
    raw = "|".join(
        [
            source.get("platform") or "",
            source.get("adapter") or "",
            source.get("aweme_id") or "",
            source.get("url") or "",
            source.get("fetched_at") or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _brief_id(brief: dict[str, Any]) -> str:
    raw = "|".join(
        [
            brief.get("candidate_id") or "",
            brief.get("target_workflow") or "",
            brief.get("title") or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _comment_fallback_id(comment: dict[str, Any]) -> str:
    raw = f"{comment.get('user_name') or ''}|{comment.get('text') or ''}|{comment.get('created_at') or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
