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
    import_video_briefs,
)
from packages.content_experiment_engine.trend_sources import fetch_manual_topics


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


if __name__ == "__main__":
    unittest.main()
