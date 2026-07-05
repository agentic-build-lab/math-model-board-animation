from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .candidates import Candidate


@dataclass(frozen=True, slots=True)
class RubricDimension:
    code: str
    name: str
    weight: float
    description: str


CONTENT_VIDEO_V0: tuple[RubricDimension, ...] = (
    RubricDimension("er", "emotional_resonance", 1.0, "Human emotion, tension, surprise, or identity resonance."),
    RubricDimension("hp", "hook_potential", 1.0, "Whether the first seconds can make the viewer keep watching."),
    RubricDimension("ql", "quotable_lines", 1.0, "Density of reusable lines, claims, commands, or memorable wording."),
    RubricDimension("na", "narrativity", 1.0, "Whether the topic has a clear story arc or explainable progression."),
    RubricDimension("ab", "audience_breadth", 1.0, "How many target viewers can understand why this matters."),
    RubricDimension("sr", "social_resonance", 1.0, "Connection to current social, technical, market, or policy trends."),
    RubricDimension("ev", "evidence_availability", 1.0, "Whether claims can be supported by official sources or public evidence."),
)


def score_candidate(
    candidate: Candidate,
    dimension_scores: dict[str, int],
    *,
    rubric_version: str = "content_video_v0",
) -> Candidate:
    """Attach a weighted composite score to a candidate.

    Scores are intentionally explicit input. The module provides the contract
    and math; an agent, reviewer, or later ML model can supply the scores.
    """
    normalized_scores = {
        key.lower(): _validate_score(value, key) for key, value in dimension_scores.items()
    }
    dimensions = _dimensions_for_version(rubric_version)
    weighted_sum = 0.0
    weight_total = 0.0
    for dimension in dimensions:
        score = normalized_scores.get(dimension.code)
        if score is None:
            continue
        weighted_sum += score * dimension.weight
        weight_total += dimension.weight
    composite = round((weighted_sum / weight_total) * 2.0, 2) if weight_total else None

    candidate.dimension_scores = normalized_scores
    candidate.composite_score = composite
    candidate.scored_under_rubric_version = rubric_version
    candidate.predicted_bucket = _rough_bucket(composite)
    candidate.predicted_reason = _score_reason(candidate, dimensions)
    return candidate


def score_candidate_dict(
    candidate: dict[str, Any],
    dimension_scores: dict[str, int],
    *,
    rubric_version: str = "content_video_v0",
) -> dict[str, Any]:
    scored = score_candidate(Candidate(**candidate), dimension_scores, rubric_version=rubric_version)
    return scored.to_dict()


def _dimensions_for_version(rubric_version: str) -> tuple[RubricDimension, ...]:
    if rubric_version != "content_video_v0":
        raise ValueError(f"Unknown rubric_version: {rubric_version}")
    return CONTENT_VIDEO_V0


def _validate_score(value: int, key: str) -> int:
    if not isinstance(value, int) or value < 0 or value > 5:
        raise ValueError(f"dimension score {key} must be an integer from 0 to 5")
    return value


def _rough_bucket(composite: float | None) -> str | None:
    if composite is None:
        return None
    if composite >= 8.0:
        return "tier1"
    if composite >= 6.5:
        return "tier2"
    if composite >= 5.0:
        return "tier3"
    return "skip"


def _score_reason(candidate: Candidate, dimensions: tuple[RubricDimension, ...]) -> str:
    if not candidate.dimension_scores:
        return ""
    top = sorted(
        [
            (dimension.code, candidate.dimension_scores.get(dimension.code, 0))
            for dimension in dimensions
        ],
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    top_text = ", ".join(f"{code.upper()}={score}" for code, score in top)
    return f"{top_text}; composite={candidate.composite_score}"
