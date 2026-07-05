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
"""


def init_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()


def import_snapshot(database_path: Path, snapshot_path: Path) -> str:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return upsert_snapshot(database_path, snapshot)


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
                source.get("aweme_id"),
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


def _comment_fallback_id(comment: dict[str, Any]) -> str:
    raw = f"{comment.get('user_name') or ''}|{comment.get('text') or ''}|{comment.get('created_at') or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
