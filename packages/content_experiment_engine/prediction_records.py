from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PredictionRecord:
    candidate_id: str
    title: str
    target_workflow: str
    rubric_version: str
    predicted_bucket: str
    probability: dict[str, float]
    reason: str
    factors: list[dict[str, str]]
    blind_status: str = "confirmed_no_data_seen"
    prediction_basis: str = "pre_publish"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def render_prediction_markdown(record: PredictionRecord) -> str:
    probability_lines = [
        f"- `{bucket}`: {value:.1f}%"
        for bucket, value in record.probability.items()
    ]
    factor_lines = [
        f"| {item.get('factor', '')} | {item.get('direction', '')} | {item.get('confidence', '')} | {item.get('note', '')} |"
        for item in record.factors
    ]
    if not factor_lines:
        factor_lines = ["| no_factor | neutral | low | Not enough structured evidence yet. |"]

    body = "\n".join(
        [
            f"# {record.title} - prediction record",
            "",
            f"**Candidate ID**: `{record.candidate_id}`",
            f"**Target Workflow**: `{record.target_workflow}`",
            f"**Rubric Version**: `{record.rubric_version}`",
            f"**Prediction Basis**: `{record.prediction_basis}`",
            f"**Blind Status**: `{record.blind_status}`",
            f"**Created At**: `{record.created_at}`",
            "",
            "## Prediction v1",
            "",
            f"**Bucket**: `{record.predicted_bucket}`",
            "",
            "**Probability**:",
            *probability_lines,
            "",
            f"**One-line reason**: {record.reason}",
            "",
            "## Reasoning Factors",
            "",
            "| Factor | Direction | Confidence | Note |",
            "|---|---|---|---|",
            *factor_lines,
            "",
            "## Counterfactuals",
            "",
            "- If actual performance is much higher, inspect whether hook/social resonance was underweighted.",
            "- If actual performance is much lower, inspect whether evidence availability or audience breadth was overestimated.",
            "- If comments focus on a different question, update the brief and observation notes without editing this prediction.",
            "",
            "## Retro",
            "",
            "_Append retrospective notes here. Do not edit the prediction section above._",
            "",
        ]
    )
    return body


def write_prediction(path: Path, record: PredictionRecord) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Prediction already exists: {path}")
    content = render_prediction_markdown(record)
    path.write_text(content, encoding="utf-8")
    return immutable_prediction_hash(content)


def append_retro(path: Path, retro_markdown: str) -> str:
    existing = path.read_text(encoding="utf-8")
    before_hash = immutable_prediction_hash(existing)
    if "## Retro" not in existing:
        raise ValueError("Prediction file is missing `## Retro` section.")
    updated = existing.rstrip() + "\n\n" + retro_markdown.strip() + "\n"
    after_hash = immutable_prediction_hash(updated)
    if before_hash != after_hash:
        raise ValueError("Retro append would modify immutable prediction section.")
    path.write_text(updated, encoding="utf-8")
    return after_hash


def immutable_prediction_hash(markdown: str) -> str:
    section = _prediction_section(markdown)
    return hashlib.sha256(section.encode("utf-8")).hexdigest()


def _prediction_section(markdown: str) -> str:
    lines = markdown.splitlines()
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        if line.startswith("## Prediction") or line.startswith("## 预测"):
            start = index
            continue
        if start is not None and index > start and line.startswith("## ") and not (
            line.startswith("## Prediction") or line.startswith("## 预测")
        ):
            end = index
            break
    if start is None:
        raise ValueError("No prediction section found.")
    return "\n".join(lines[start:end]).strip()
