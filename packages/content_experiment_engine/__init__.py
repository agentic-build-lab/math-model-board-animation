"""Reusable content experiment adapters for video production systems."""

from .brief_generator import generate_video_brief
from .bilibili_public_video import extract_bvid, fetch_public_bilibili_snapshot
from .candidates import Candidate, candidate_id, normalize_candidate
from .douyin_public_video import extract_aweme_id, fetch_public_video_snapshot
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
    "create_transcript_artifact",
    "extract_bvid",
    "extract_aweme_id",
    "fetch_public_bilibili_snapshot",
    "fetch_public_video_snapshot",
    "generate_video_brief",
    "get_platform_profile",
    "list_platform_profiles",
    "normalize_candidate",
    "platform_weighted_score",
    "profiles_as_dict",
    "render_content_review_markdown",
    "render_transcript_markdown",
    "score_candidate",
    "write_content_review_markdown",
    "write_prediction",
    "write_transcript_artifact",
]
