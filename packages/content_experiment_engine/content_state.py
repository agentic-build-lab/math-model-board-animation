from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


STATE_SCHEMA_VERSION = "1.0"
DEFAULT_STATE_FILE_NAME = "content_experiment_state.json"


@dataclass(frozen=True, slots=True)
class ConfidenceBand:
    key: str
    min_samples: int
    max_samples: int | None
    label: str
    error_margin_percent: int | None
    guidance: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CONFIDENCE_BANDS: tuple[ConfidenceBand, ...] = (
    ConfidenceBand(
        "none",
        0,
        0,
        "no calibration data",
        None,
        "Use the workflow to collect baseline samples; do not use scores for decisions.",
    ),
    ConfidenceBand(
        "very_low",
        1,
        2,
        "very low",
        50,
        "Use direction only; absolute buckets are weak guesses.",
    ),
    ConfidenceBand(
        "low",
        3,
        5,
        "low",
        40,
        "Bucket ranking is usable as one input, but center estimates are unstable.",
    ),
    ConfidenceBand(
        "medium",
        6,
        10,
        "medium",
        25,
        "Scores can participate in decisions when evidence quality is also strong.",
    ),
    ConfidenceBand(
        "high",
        11,
        20,
        "high",
        15,
        "The rubric shape is becoming stable; inspect systematic misses before bumping.",
    ),
    ConfidenceBand(
        "data_driven",
        21,
        None,
        "data driven",
        10,
        "Use calibration statistics and re-scoring before changing weights.",
    ),
)


def confidence_for_samples(calibration_samples: int) -> dict[str, Any]:
    if not isinstance(calibration_samples, int) or calibration_samples < 0:
        raise ValueError("calibration_samples must be a non-negative integer")
    for band in CONFIDENCE_BANDS:
        if calibration_samples >= band.min_samples and (
            band.max_samples is None or calibration_samples <= band.max_samples
        ):
            data = band.to_dict()
            data["calibration_samples"] = calibration_samples
            return data
    raise AssertionError("confidence bands are incomplete")


def create_initial_state(
    *,
    project_name: str = "content_experiment",
    content_form: str = "mixed",
    typical_duration_seconds: int = 180,
    target_publish_cadence_days: int | None = None,
    enabled_trend_sources: list[str] | None = None,
    enabled_perf_adapters: list[str] | None = None,
    initialized_at: str | None = None,
) -> dict[str, Any]:
    if typical_duration_seconds <= 0:
        raise ValueError("typical_duration_seconds must be positive")
    calibration_samples = 0
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "project_name": project_name,
        "content_form": content_form,
        "typical_duration_seconds": typical_duration_seconds,
        "target_publish_cadence_days": target_publish_cadence_days,
        "rubric_version": "content_video_v0",
        "calibration_samples": calibration_samples,
        "calibration_samples_at_last_bump": 0,
        "confidence": confidence_for_samples(calibration_samples),
        "benchmark_status": "none",
        "benchmark_name": None,
        "benchmark_sample_count": 0,
        "baseline_plays": None,
        "data_collection": "manual",
        "enabled_trend_sources": enabled_trend_sources or ["manual"],
        "enabled_perf_adapters": enabled_perf_adapters or [],
        "learning_artifacts": {
            "audience": "audience.md",
            "benchmark": "benchmark.md",
            "script_patterns": "script_patterns.md",
        },
        "blind_boundary": {
            "forbidden_for_blind_scoring": [
                "audience.md",
                "benchmark.md",
                "script_patterns.md",
                "rubric-memo.md",
                "content_review.md",
                "calibration_report.md",
            ],
            "blind_safe_rubric": "rubric_notes.md",
        },
        "pending_retros": [],
        "shoots": [],
        "consecutive_directional_errors": [],
        "last_bump_at": None,
        "last_published_at": None,
        "last_retro_at": None,
        "last_trends_run_at": None,
        "initialized_at": initialized_at or datetime.now(UTC).isoformat(),
    }


def merge_state_defaults(state: dict[str, Any]) -> dict[str, Any]:
    merged = create_initial_state(
        project_name=str(state.get("project_name") or "content_experiment"),
        content_form=str(state.get("content_form") or "mixed"),
        typical_duration_seconds=int(state.get("typical_duration_seconds") or 180),
        target_publish_cadence_days=state.get("target_publish_cadence_days"),
        enabled_trend_sources=list(state.get("enabled_trend_sources") or ["manual"]),
        enabled_perf_adapters=list(state.get("enabled_perf_adapters") or []),
        initialized_at=str(state.get("initialized_at") or datetime.now(UTC).isoformat()),
    )
    merged.update(state)
    calibration_samples = int(merged.get("calibration_samples") or 0)
    merged["confidence"] = confidence_for_samples(calibration_samples)
    return merged


def read_state(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"State file must contain a JSON object: {path}")
    return merge_state_defaults(data)


def write_state(path: Path, state: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = merge_state_defaults(state)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp_path.replace(path)
    return path
