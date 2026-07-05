from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TranscriptArtifact:
    transcript_id: str
    source_path: str
    source_type: str
    title: str
    language: str | None
    engine: str
    created_at: str
    duration_s: float | None
    text: str
    segments: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_transcript_artifact(
    *,
    source_path: str,
    transcript_text: str,
    title: str | None = None,
    source_type: str = "local_media",
    language: str | None = None,
    engine: str = "manual_transcript",
    duration_s: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> TranscriptArtifact:
    """Normalize a transcript into a stable artifact for video workflows.

    This intentionally does not download media or require a specific ASR engine.
    If a workflow uses Whisper, cloud ASR, manual subtitles, or an existing SRT,
    the downstream contract remains the same.
    """

    normalized_text = normalize_transcript_text(transcript_text)
    active_title = title or Path(source_path).name or "transcript"
    created_at = datetime.now(UTC).isoformat()
    artifact_id = _transcript_id(source_path, normalized_text)
    return TranscriptArtifact(
        transcript_id=artifact_id,
        source_path=source_path,
        source_type=source_type,
        title=active_title,
        language=language,
        engine=engine,
        created_at=created_at,
        duration_s=duration_s,
        text=normalized_text,
        segments=segment_transcript(normalized_text),
        metadata=metadata or {},
    )


def write_transcript_artifact(
    artifact: TranscriptArtifact,
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "transcript.json"
    markdown_path = output_dir / "transcript.md"
    json_path.write_text(
        json.dumps(artifact.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(render_transcript_markdown(artifact), encoding="utf-8")
    return json_path, markdown_path


def render_transcript_markdown(artifact: TranscriptArtifact) -> str:
    lines = [
        f"# Transcript: {artifact.title}",
        "",
        f"**Transcript id**: `{artifact.transcript_id}`",
        f"**Source**: `{artifact.source_path}`",
        f"**Source type**: `{artifact.source_type}`",
        f"**Engine**: `{artifact.engine}`",
        f"**Language**: `{artifact.language or 'unknown'}`",
        f"**Created at**: `{artifact.created_at}`",
    ]
    if artifact.duration_s is not None:
        lines.append(f"**Duration seconds**: `{artifact.duration_s:g}`")
    lines.extend(["", "---", ""])
    lines.extend(artifact.segments or [artifact.text])
    lines.append("")
    return "\n".join(lines)


def normalize_transcript_text(value: str) -> str:
    value = _strip_srt_or_vtt_noise(value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def segment_transcript(value: str, *, target_chars: int = 420) -> list[str]:
    text = normalize_transcript_text(value)
    if not text:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    segments: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        if len(paragraph) > target_chars * 1.8:
            for sentence in _split_sentences(paragraph):
                buffer = _push_segment_piece(segments, buffer, sentence, target_chars)
            continue
        buffer = _push_segment_piece(segments, buffer, paragraph, target_chars)
    if buffer:
        segments.append(buffer.strip())
    return segments


def _strip_srt_or_vtt_noise(value: str) -> str:
    kept: list[str] = []
    for raw_line in value.replace("\ufeff", "").splitlines():
        line = raw_line.strip()
        if not line:
            kept.append("")
            continue
        if line.upper() == "WEBVTT":
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if re.search(r"\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*\d{1,2}:\d{2}:\d{2}", line):
            continue
        kept.append(line)
    return "\n".join(kept)


def _split_sentences(value: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?。！？])\s+", value)
    return [piece.strip() for piece in pieces if piece.strip()]


def _push_segment_piece(
    segments: list[str],
    buffer: str,
    piece: str,
    target_chars: int,
) -> str:
    if not buffer:
        return piece
    if len(buffer) + 1 + len(piece) <= target_chars:
        return f"{buffer} {piece}"
    segments.append(buffer.strip())
    return piece


def _transcript_id(source_path: str, text: str) -> str:
    raw = f"{source_path}|{text[:4000]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
