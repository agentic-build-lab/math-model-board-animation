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
from packages.content_experiment_engine.platform_profiles import (
    get_platform_profile,
    list_platform_profiles,
    normalized_weights,
    platform_weighted_score,
)
from packages.content_experiment_engine.review_report import render_content_review_markdown
from packages.content_experiment_engine.text_similarity import text_diff_percent
from packages.content_experiment_engine.calibration_reports import (
    collect_calibration_samples,
    render_calibration_markdown,
)
from packages.content_experiment_engine.blind_boundaries import (
    find_blind_metric_leaks,
    is_forbidden_for_blind_scoring,
)
from packages.content_experiment_engine.content_state import (
    confidence_for_samples,
    create_initial_state,
    read_state,
    write_state,
)
from packages.content_experiment_engine.learning_artifacts import initialize_learning_artifacts
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


class PlatformProfileTests(unittest.TestCase):
    def test_default_profiles_cover_target_platforms(self) -> None:
        keys = {profile.key for profile in list_platform_profiles()}
        self.assertIn("youtube_long", keys)
        self.assertIn("youtube_shorts", keys)
        self.assertIn("bilibili", keys)
        self.assertIn("douyin", keys)
        self.assertIn("tiktok", keys)
        self.assertIn("x", keys)
        self.assertIn("xiaohongshu", keys)

    def test_normalized_weights_sum_to_one(self) -> None:
        for profile in list_platform_profiles():
            total = sum(normalized_weights(profile).values())
            self.assertAlmostEqual(total, 1.0, places=4)

    def test_platform_weighted_score(self) -> None:
        result = platform_weighted_score(
            "youtube-long",
            {"wi": 5, "si": 4, "hd": 5, "cev": 3, "ef": 4, "cf": 4, "lt": 5},
        )
        self.assertEqual(result["profile_key"], "youtube_long")
        self.assertGreaterEqual(result["composite_score"], 8.0)
        self.assertEqual(len(result["top_dimensions"]), 3)

    def test_get_platform_profile_rejects_unknown_key(self) -> None:
        with self.assertRaises(KeyError):
            get_platform_profile("unknown_platform")


class TextSimilarityTests(unittest.TestCase):
    def test_markdown_noise_does_not_dominate_diff(self) -> None:
        original = "# Title\n\n- First sentence.\n- Second sentence."
        revised = "First sentence. Second sentence."
        result = text_diff_percent(original, revised)
        self.assertLessEqual(result["diff_percent"], 10)
        self.assertGreater(result["original_normalized_length"], 0)


class CalibrationReportTests(unittest.TestCase):
    def test_collect_prediction_samples_and_render_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            prediction = root / "2026-07-05_sample.md"
            prediction.write_text(
                "\n".join(
                    [
                        "# Sample",
                        "",
                        "## Prediction v1",
                        "",
                        "**Bucket**: `30-100w`",
                        "",
                        "## Retro",
                        "",
                        "actual_plays: 80w",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            samples = collect_calibration_samples(root)
            self.assertEqual(len(samples), 1)
            self.assertEqual(samples[0].predicted_center, 65.0)
            self.assertEqual(samples[0].actual_value, 80.0)
            report = render_calibration_markdown(samples, window=1)
            self.assertIn("Mean absolute error", report)
            self.assertIn("30-100w", report)


class ContentStateTests(unittest.TestCase):
    def test_confidence_for_samples_uses_expected_bands(self) -> None:
        self.assertEqual(confidence_for_samples(0)["key"], "none")
        self.assertEqual(confidence_for_samples(7)["key"], "medium")
        self.assertEqual(confidence_for_samples(21)["key"], "data_driven")

    def test_state_write_and_read_merges_defaults(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "content_experiment_state.json"
            state = create_initial_state(project_name="demo", typical_duration_seconds=120)
            write_state(path, state)
            loaded = read_state(path)
            self.assertEqual(loaded["project_name"], "demo")
            self.assertEqual(loaded["confidence"]["key"], "none")
            self.assertIn("audience.md", loaded["blind_boundary"]["forbidden_for_blind_scoring"])


class LearningArtifactTests(unittest.TestCase):
    def test_initialize_learning_artifacts_writes_expected_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = initialize_learning_artifacts(
                root,
                project_name="demo",
                benchmark_name="sample_benchmark",
                platform="youtube",
            )
            names = {path.name for path in written}
            self.assertIn("audience.md", names)
            self.assertIn("benchmark.md", names)
            self.assertIn("script_patterns.md", names)
            self.assertIn("content_experiment_state.json", names)
            self.assertIn("sample_benchmark", (root / "benchmark.md").read_text(encoding="utf-8"))


class BlindBoundaryTests(unittest.TestCase):
    def test_metric_leak_detection_ignores_bucket_boundaries(self) -> None:
        safe = "Bucket boundaries: 5-30w / 30-100w / >100w"
        unsafe = "Actual plays reached 80w after T+3 review."
        self.assertEqual(find_blind_metric_leaks(safe), [])
        leaks = find_blind_metric_leaks(unsafe)
        self.assertEqual(len(leaks), 1)
        self.assertIn("Actual", leaks[0].excerpt)

    def test_forbidden_blind_scoring_files(self) -> None:
        self.assertTrue(is_forbidden_for_blind_scoring("audience.md"))
        self.assertFalse(is_forbidden_for_blind_scoring("rubric_notes.md"))


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
