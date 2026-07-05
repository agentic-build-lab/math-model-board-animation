"""Reusable content experiment adapters for video production systems."""

from .brief_generator import generate_video_brief
from .blind_boundaries import find_blind_metric_leaks, is_forbidden_for_blind_scoring
from .calibration_reports import (
    collect_calibration_samples,
    render_calibration_csv,
    render_calibration_markdown,
)
from .bilibili_public_video import extract_bvid, fetch_public_bilibili_snapshot
from .candidates import Candidate, candidate_id, normalize_candidate
from .content_state import confidence_for_samples, create_initial_state, read_state, write_state
from .douyin_public_video import extract_aweme_id, fetch_public_video_snapshot
from .learning_artifacts import initialize_learning_artifacts
from .platform_profiles import (
    PlatformProfile,
    get_platform_profile,
    list_platform_profiles,
    platform_weighted_score,
    profiles_as_dict,
)
from .prediction_records import PredictionRecord, append_retro, write_prediction
from .review_report import render_content_review_markdown, write_content_review_markdown
from .rubric import score_candidate
from .text_similarity import normalize_for_similarity, text_diff_percent
from .transcripts import (
    TranscriptArtifact,
    create_transcript_artifact,
    render_transcript_markdown,
    write_transcript_artifact,
)

__all__ = [
    "Candidate",
    "PlatformProfile",
    "PredictionRecord",
    "TranscriptArtifact",
    "append_retro",
    "candidate_id",
    "confidence_for_samples",
    "collect_calibration_samples",
    "create_initial_state",
    "create_transcript_artifact",
    "extract_bvid",
    "extract_aweme_id",
    "fetch_public_bilibili_snapshot",
    "fetch_public_video_snapshot",
    "find_blind_metric_leaks",
    "generate_video_brief",
    "get_platform_profile",
    "initialize_learning_artifacts",
    "is_forbidden_for_blind_scoring",
    "list_platform_profiles",
    "normalize_candidate",
    "platform_weighted_score",
    "profiles_as_dict",
    "normalize_for_similarity",
    "read_state",
    "render_content_review_markdown",
    "render_calibration_csv",
    "render_calibration_markdown",
    "render_transcript_markdown",
    "score_candidate",
    "text_diff_percent",
    "write_content_review_markdown",
    "write_prediction",
    "write_state",
    "write_transcript_artifact",
]
