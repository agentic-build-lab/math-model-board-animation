from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BLIND_FORBIDDEN_BASENAMES = frozenset(
    {
        "audience.md",
        "benchmark.md",
        "script_patterns.md",
        "rubric-memo.md",
        "content_review.md",
        "calibration_report.md",
    }
)

METRIC_KEYWORD_RE = re.compile(
    r"\b(actual|views?|plays?|impressions?|likes?|comments?|shares?|retention|conversion)\b"
    r"|播放|阅读|曝光|点赞|评论|转发|分享|完播|转粉|实绩|实际",
    re.IGNORECASE,
)
METRIC_NUMBER_RE = re.compile(r"(?<![\w.-])\d+(?:\.\d+)?\s*(?:w|万|k|m)(?![\w.-])", re.IGNORECASE)
SAFE_BUCKET_LINE_RE = re.compile(r"\b(bucket|probability|range|boundary|center)\b|概率|分布|桶|边界", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class LeakFinding:
    line_number: int
    excerpt: str
    reason: str
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_forbidden_for_blind_scoring(path: str | Path) -> bool:
    return Path(path).name.lower() in BLIND_FORBIDDEN_BASENAMES


def find_blind_metric_leaks(text: str, *, source: str | None = None) -> list[LeakFinding]:
    findings: list[LeakFinding] = []
    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        keyword_match = METRIC_KEYWORD_RE.search(stripped)
        if keyword_match:
            findings.append(
                LeakFinding(
                    line_number=index,
                    excerpt=_shorten(stripped),
                    reason=f"metric_keyword:{keyword_match.group(0)}",
                    source=source,
                )
            )
            continue
        number_match = METRIC_NUMBER_RE.search(stripped)
        if number_match and not SAFE_BUCKET_LINE_RE.search(stripped):
            findings.append(
                LeakFinding(
                    line_number=index,
                    excerpt=_shorten(stripped),
                    reason=f"metric_number:{number_match.group(0)}",
                    source=source,
                )
            )
    return findings


def scan_file_for_blind_leaks(path: Path) -> list[LeakFinding]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return find_blind_metric_leaks(path.read_text(encoding="utf-8"), source=str(path))


def scan_files_for_blind_leaks(paths: list[Path]) -> list[LeakFinding]:
    findings: list[LeakFinding] = []
    for path in paths:
        findings.extend(scan_file_for_blind_leaks(path))
    return findings


def _shorten(value: str, limit: int = 160) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."
