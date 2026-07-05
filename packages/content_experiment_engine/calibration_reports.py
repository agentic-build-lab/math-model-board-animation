from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_BUCKET_CENTERS: dict[str, float] = {
    "<5w": 2.5,
    "5-30w": 17.5,
    "30-100w": 65.0,
    "100-150w": 125.0,
    ">150w": 200.0,
}

BUCKET_RE = re.compile(r"^\*\*Bucket\*\*:\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
EXPLICIT_CENTER_RE = re.compile(
    r"(?:predicted[_\s-]*center|center|中枢|中位数)\s*[:：~约 ]+\s*(\d+(?:\.\d+)?)\s*(w|万|views|plays)?",
    re.IGNORECASE,
)
ACTUAL_VALUE_RE = re.compile(
    r"(?:actual[_\s-]*(?:plays|views)|播放|播放量|views|plays)\s*[:：= ]+\s*(\d+(?:\.\d+)?)\s*(w|万)?",
    re.IGNORECASE,
)
DATE_FROM_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True, slots=True)
class CalibrationSample:
    file: str
    date: str
    bucket: str | None
    predicted_center: float | None
    actual_value: float | None

    @property
    def has_actual(self) -> bool:
        return self.actual_value is not None

    @property
    def signed_error_percent(self) -> float | None:
        if self.predicted_center is None or self.actual_value is None or self.predicted_center == 0:
            return None
        return (self.actual_value - self.predicted_center) / self.predicted_center * 100

    @property
    def absolute_error_percent(self) -> float | None:
        value = self.signed_error_percent
        return abs(value) if value is not None else None


def parse_prediction_for_calibration(
    path: Path,
    *,
    bucket_centers: dict[str, float] | None = None,
) -> CalibrationSample:
    text = path.read_text(encoding="utf-8")
    active_bucket_centers = bucket_centers or DEFAULT_BUCKET_CENTERS
    prediction_text, _, retro_text = text.partition("## Retro")

    bucket_match = BUCKET_RE.search(prediction_text)
    bucket = bucket_match.group(1).strip() if bucket_match else None

    center_match = EXPLICIT_CENTER_RE.search(prediction_text)
    if center_match:
        predicted_center = _number_with_unit(center_match.group(1), center_match.group(2))
    elif bucket:
        predicted_center = active_bucket_centers.get(bucket)
    else:
        predicted_center = None

    actual_match = ACTUAL_VALUE_RE.search(retro_text or text)
    actual_value = (
        _number_with_unit(actual_match.group(1), actual_match.group(2))
        if actual_match
        else None
    )

    return CalibrationSample(
        file=str(path),
        date=_date_for_path(path),
        bucket=bucket,
        predicted_center=predicted_center,
        actual_value=actual_value,
    )


def collect_calibration_samples(
    predictions_dir: Path,
    *,
    bucket_centers: dict[str, float] | None = None,
) -> list[CalibrationSample]:
    samples: list[CalibrationSample] = []
    for path in sorted(predictions_dir.glob("*.md")):
        try:
            samples.append(parse_prediction_for_calibration(path, bucket_centers=bucket_centers))
        except (OSError, ValueError):
            continue
    return samples


def rolling_mean(values: list[float], window: int) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    output: list[float] = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        chunk = values[start : index + 1]
        output.append(sum(chunk) / len(chunk))
    return output


def render_calibration_csv(samples: list[CalibrationSample]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([
        "file",
        "date",
        "bucket",
        "predicted_center",
        "actual_value",
        "signed_error_percent",
        "absolute_error_percent",
    ])
    for sample in samples:
        writer.writerow([
            sample.file,
            sample.date,
            sample.bucket or "",
            _optional_float(sample.predicted_center),
            _optional_float(sample.actual_value),
            _optional_float(sample.signed_error_percent),
            _optional_float(sample.absolute_error_percent),
        ])
    return buffer.getvalue()


def render_calibration_markdown(
    samples: list[CalibrationSample],
    *,
    window: int = 5,
) -> str:
    scored = [
        sample
        for sample in samples
        if sample.absolute_error_percent is not None
    ]
    abs_errors = [sample.absolute_error_percent or 0.0 for sample in scored]
    rolling = rolling_mean(abs_errors, window) if abs_errors else []
    mean_abs_error = sum(abs_errors) / len(abs_errors) if abs_errors else None

    lines = [
        "# Content Prediction Calibration Report",
        "",
        f"- Total prediction files: {len(samples)}",
        f"- With actual values: {len(scored)}",
        f"- Mean absolute error: {_optional_float(mean_abs_error)}%",
        f"- Rolling window: {window}",
        "",
        "| File | Bucket | Predicted | Actual | Error % | Rolling Abs Error % |",
        "|---|---|---:|---:|---:|---:|",
    ]
    rolling_by_file = {sample.file: rolling[index] for index, sample in enumerate(scored)}
    for sample in samples:
        lines.append(
            "| {file} | {bucket} | {predicted} | {actual} | {error} | {rolling} |".format(
                file=Path(sample.file).name,
                bucket=sample.bucket or "",
                predicted=_optional_float(sample.predicted_center),
                actual=_optional_float(sample.actual_value),
                error=_optional_float(sample.signed_error_percent),
                rolling=_optional_float(rolling_by_file.get(sample.file)),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _date_for_path(path: Path) -> str:
    match = DATE_FROM_FILENAME_RE.search(path.name)
    if match:
        return match.group(1)
    timestamp = path.stat().st_mtime
    return datetime.fromtimestamp(timestamp).date().isoformat()


def _number_with_unit(value: str, unit: str | None) -> float:
    number = float(value)
    if unit in {"w", "万"}:
        return number
    return number


def _optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}".rstrip("0").rstrip(".")
