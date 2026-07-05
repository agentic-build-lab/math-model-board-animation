from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from .snapshot_store import init_database


def render_content_review_markdown(
    database_path: Path,
    *,
    max_rows: int = 10,
) -> str:
    """Render a human-readable review report from the content SQLite index."""

    generated_at = datetime.now(UTC).isoformat()
    init_database(database_path)
    lines = [
        "# Content Experiment Review",
        "",
        f"**Database**: `{database_path}`",
        f"**Generated at**: `{generated_at}`",
        "",
    ]

    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        lines.extend(_snapshot_section(connection, max_rows=max_rows))
        lines.extend(_transcript_section(connection, max_rows=max_rows))
        lines.extend(_candidate_section(connection, max_rows=max_rows))
        lines.extend(_brief_section(connection, max_rows=max_rows))
    return "\n".join(lines).rstrip() + "\n"


def write_content_review_markdown(
    database_path: Path,
    output_path: Path,
    *,
    max_rows: int = 10,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_content_review_markdown(database_path, max_rows=max_rows),
        encoding="utf-8",
    )
    return output_path


def _snapshot_section(connection: sqlite3.Connection, *, max_rows: int) -> list[str]:
    rows = connection.execute(
        """
        SELECT platform, title, author, play_count, like_count, comment_count,
               source_url, fetched_at
        FROM content_video_snapshots
        ORDER BY fetched_at DESC
        LIMIT ?
        """,
        (max_rows,),
    ).fetchall()

    lines = ["## Recent Public Video Snapshots", ""]
    if not rows:
        return lines + ["No snapshots imported yet.", ""]
    lines.extend(
        [
            "| Platform | Title | Plays | Likes | Comments | Source |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| {platform} | {title} | {plays} | {likes} | {comments} | {source} |".format(
                platform=_cell(row["platform"]),
                title=_cell(row["title"] or row["author"] or "untitled"),
                plays=_number(row["play_count"]),
                likes=_number(row["like_count"]),
                comments=_number(row["comment_count"]),
                source=_cell(row["source_url"]),
            )
        )
    lines.append("")
    return lines


def _candidate_section(connection: sqlite3.Connection, *, max_rows: int) -> list[str]:
    rows = connection.execute(
        """
        SELECT candidate_id, title, source, tier, composite_score,
               predicted_bucket, predicted_reason, url
        FROM content_candidates
        ORDER BY composite_score DESC, inserted_at DESC
        LIMIT ?
        """,
        (max_rows,),
    ).fetchall()

    lines = ["## Top Candidates", ""]
    if not rows:
        return lines + ["No candidates imported yet.", ""]
    lines.extend(
        [
            "| Candidate | Source | Tier | Score | Prediction | Reason |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| {title} | {source} | {tier} | {score} | {bucket} | {reason} |".format(
                title=_cell(row["title"]),
                source=_cell(row["source"]),
                tier=_cell(row["tier"] or ""),
                score=_number(row["composite_score"]),
                bucket=_cell(row["predicted_bucket"] or ""),
                reason=_cell(row["predicted_reason"] or ""),
            )
        )
    lines.append("")
    return lines


def _transcript_section(connection: sqlite3.Connection, *, max_rows: int) -> list[str]:
    rows = connection.execute(
        """
        SELECT title, source_type, language, engine, duration_s, source_path, inserted_at
        FROM content_transcripts
        ORDER BY inserted_at DESC
        LIMIT ?
        """,
        (max_rows,),
    ).fetchall()

    lines = ["## Recent Transcripts", ""]
    if not rows:
        return lines + ["No transcripts imported yet.", ""]
    lines.extend(
        [
            "| Title | Source Type | Language | Engine | Duration | Source |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| {title} | {source_type} | {language} | {engine} | {duration} | {source} |".format(
                title=_cell(row["title"]),
                source_type=_cell(row["source_type"]),
                language=_cell(row["language"] or ""),
                engine=_cell(row["engine"]),
                duration=_number(row["duration_s"]),
                source=_cell(row["source_path"]),
            )
        )
    lines.append("")
    return lines


def _brief_section(connection: sqlite3.Connection, *, max_rows: int) -> list[str]:
    rows = connection.execute(
        """
        SELECT target_workflow, title, hook, video_angle, created_at
        FROM video_topic_briefs
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (max_rows,),
    ).fetchall()

    lines = ["## Recent Video Briefs", ""]
    if not rows:
        return lines + ["No briefs generated yet.", ""]
    for row in rows:
        lines.extend(
            [
                f"### {_plain(row['title'])}",
                "",
                f"- Workflow: `{row['target_workflow']}`",
                f"- Hook: {_plain(row['hook'])}",
                f"- Angle: {_plain(row['video_angle'])}",
                "",
            ]
        )
    return lines


def _cell(value: object) -> str:
    text = _plain(str(value or ""))
    return text.replace("|", "\\|")


def _plain(value: str) -> str:
    return " ".join(value.split())


def _number(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)
