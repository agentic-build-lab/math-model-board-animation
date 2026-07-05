"""Reusable content experiment adapters for video production systems."""

from .brief_generator import generate_video_brief
from .bilibili_public_video import extract_bvid, fetch_public_bilibili_snapshot
from .candidates import Candidate, candidate_id, normalize_candidate
from .douyin_public_video import extract_aweme_id, fetch_public_video_snapshot
from .prediction_records import PredictionRecord, append_retro, write_prediction
from .rubric import score_candidate

__all__ = [
    "Candidate",
    "PredictionRecord",
    "append_retro",
    "candidate_id",
    "extract_bvid",
    "extract_aweme_id",
    "fetch_public_bilibili_snapshot",
    "fetch_public_video_snapshot",
    "generate_video_brief",
    "normalize_candidate",
    "score_candidate",
    "write_prediction",
]
