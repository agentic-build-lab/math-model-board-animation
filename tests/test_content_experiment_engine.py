from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from packages.content_experiment_engine.douyin_public_video import (
    _sanitize_url,
    extract_aweme_id,
)
from packages.content_experiment_engine.brief_generator import generate_video_brief
from packages.content_experiment_engine.candidates import candidate_id, normalize_candidate
from packages.content_experiment_engine.rubric import score_candidate
from packages.content_experiment_engine.snapshot_store import import_snapshot
from packages.content_experiment_engine.snapshot_store import (
    import_candidates,
    import_transcript,
    import_video_briefs,
)
from packages.content_experiment_engine.trend_sources import fetch_manual_topics
from packages.content_experiment_engine.bilibili_public_video import extract_bvid
from packages.content_experiment_engine.prediction_records import (
    PredictionRecord,
    append_retro,
    immutable_prediction_hash,
    render_prediction_markdown,
    write_prediction,
)
from packages.content_experiment_engine.review_report import render_content_review_markdown
from packages.content_experiment_engine.transcripts import (
    create_transcript_artifact,
    normalize_transcript_text,
    write_transcript_artifact,
)


class DouyinPublicVideoTests(unittest.TestCase):
    def test_extract_aweme_id_from_direct_url(self) -> None:
        self.assertEqual(
            extract_aweme_id("https://www.douyin.com/video/7636402601549974818"),
            "7636402601549974818",
        )

    def test_extract_aweme_id_from_raw_id(self) -> None:
        self.assertEqual(extract_aweme_id("7636402601549974818"), "7636402601549974818")

    def test_sanitize_url_removes_query_and_fragment(self) -> None:
        self.assertEqual(
            _sanitize_url("https://www.douyin.com/aweme/v1/web/comment/list/?msToken=secret#frag"),
            "https://www.douyin.com/aweme/v1/web/comment/list/",
        )


class CandidateAndBriefTests(unittest.TestCase):
    def test_candidate_id_is_stable_across_query_params(self) -> None:
        first = candidate_id("trend:source_a", "Hello World", "https://example.com/path?utm=1")
        second = candidate_id("trend:source_b", "hello  world", "https://example.com/path?utm=2")
        self.assertEqual(first, second)

    def test_score_candidate_and_generate_brief(self) -> None:
        candidate = normalize_candidate(
            title="AI agents are changing video production",
            source="manual:user",
            snapshot_text="AI agents are changing video production",
        )
        scored = score_candidate(
            candidate,
            {"er": 4, "hp": 5, "ql": 4, "na": 3, "ab": 4, "sr": 5, "ev": 3},
        )
        self.assertEqual(scored.predicted_bucket, "tier1")
        brief = generate_video_brief(scored, target_workflow="evidence_driven_ai_video")
        self.assertEqual(brief.candidate_id, candidate.id)
        self.assertIn("official_webpage_or_pdf", brief.evidence_needed)

    def test_manual_topic_source(self) -> None:
        candidates = fetch_manual_topics(["topic one", "topic two"])
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].source, "manual:user")


class BilibiliPublicVideoTests(unittest.TestCase):
    def test_extract_bvid_from_url(self) -> None:
        self.assertEqual(
            extract_bvid("https://www.bilibili.com/video/BV1xx411c7mD/?spm_id_from=333"),
            "BV1xx411c7mD",
        )


class PredictionRecordTests(unittest.TestCase):
    def test_retro_append_preserves_prediction_hash(self) -> None:
        record = PredictionRecord(
            candidate_id="abc123",
            title="Sample",
            target_workflow="evidence_driven_ai_video",
            rubric_version="content_video_v0",
            predicted_bucket="tier2",
            probability={"tier1": 20, "tier2": 50, "tier3": 20, "skip": 10},
            reason="sample reason",
            factors=[],
        )
        content = render_prediction_markdown(record)
        before_hash = immutable_prediction_hash(content)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "prediction.md"
            written_hash = write_prediction(path, record)
            after_hash = append_retro(path, "### T+3 review\n- Actual result recorded.")
            self.assertEqual(before_hash, written_hash)
            self.assertEqual(before_hash, after_hash)


class TranscriptTests(unittest.TestCase):
    def test_normalize_transcript_text_strips_srt_noise(self) -> None:
        source = """WEBVTT

1
00:00:01,000 --> 00:00:03,000
First sentence.

2
00:00:04,000 --> 00:00:06,000
Second sentence.
"""
        self.assertEqual(
            normalize_transcript_text(source),
            "First sentence.\n\nSecond sentence.",
        )

    def test_write_and_import_transcript_artifact(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = create_transcript_artifact(
                source_path="sample.mp4",
                title="Sample Video",
                transcript_text="First sentence. Second sentence.",
                language="en",
                engine="manual_transcript",
            )
            json_path, markdown_path = write_transcript_artifact(artifact, root / "transcript")
            database_path = root / "content.db"
            transcript_id = import_transcript(database_path, json_path)
            self.assertEqual(transcript_id, artifact.transcript_id)
            self.assertTrue(markdown_path.is_file())


class SnapshotStoreTests(unittest.TestCase):
    def test_import_snapshot_to_sqlite(self) -> None:
        snapshot = {
            "schema_version": "1.0",
            "source": {
                "platform": "douyin",
                "adapter": "douyin_public_video",
                "url": "https://www.douyin.com/video/7636402601549974818",
                "resolved_url": "https://www.douyin.com/video/7636402601549974818",
                "aweme_id": "7636402601549974818",
                "fetched_at": "2026-07-05T00:00:00+00:00",
            },
            "video": {
                "title": "sample",
                "description": "sample",
                "author": "author",
                "created_at": None,
                "duration_ms": 1000,
            },
            "metrics": {
                "play_count": None,
                "like_count": 1,
                "comment_count": 1,
                "share_count": 0,
                "collect_count": 0,
            },
            "comments": [
                {
                    "id": "comment_1",
                    "text": "good",
                    "like_count": 2,
                    "reply_count": 0,
                    "created_at": None,
                    "user_name": "user",
                    "ip_label": "",
                }
            ],
            "evidence": {
                "screenshot_path": "public_video_page.png",
                "raw_response_path": "raw_responses.jsonl",
                "captured_api_urls": [],
            },
            "limitations": [],
        }
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_path = root / "snapshot.json"
            database_path = root / "content.db"
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
            snapshot_id = import_snapshot(database_path, snapshot_path)
            self.assertTrue(snapshot_id)
            self.assertTrue(database_path.is_file())

    def test_import_candidates_and_briefs_to_sqlite(self) -> None:
        candidate = normalize_candidate(
            title="Topic",
            source="manual:user",
            snapshot_text="Topic",
        )
        scored = score_candidate(
            candidate,
            {"er": 3, "hp": 3, "ql": 3, "na": 3, "ab": 3, "sr": 3, "ev": 3},
        )
        brief = generate_video_brief(scored, target_workflow="math_model_board_animation")
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates_path = root / "candidates.json"
            briefs_path = root / "briefs.json"
            database_path = root / "content.db"
            candidates_path.write_text(json.dumps([scored.to_dict()]), encoding="utf-8")
            briefs_path.write_text(json.dumps([brief.to_dict()]), encoding="utf-8")
            candidate_ids = import_candidates(database_path, candidates_path)
            brief_ids = import_video_briefs(database_path, briefs_path)
            self.assertEqual(candidate_ids, [candidate.id])
            self.assertEqual(len(brief_ids), 1)

    def test_render_content_review_markdown(self) -> None:
        candidate = normalize_candidate(
            title="Topic",
            source="manual:user",
            snapshot_text="Topic",
        )
        scored = score_candidate(
            candidate,
            {"er": 3, "hp": 3, "ql": 3, "na": 3, "ab": 3, "sr": 3, "ev": 3},
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates_path = root / "candidates.json"
            database_path = root / "content.db"
            candidates_path.write_text(json.dumps([scored.to_dict()]), encoding="utf-8")
            import_candidates(database_path, candidates_path)
            report = render_content_review_markdown(database_path)
            self.assertIn("Content Experiment Review", report)
            self.assertIn("Topic", report)


if __name__ == "__main__":
    unittest.main()
