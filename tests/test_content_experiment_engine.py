from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from packages.content_experiment_engine.douyin_public_video import (
    _sanitize_url,
    extract_aweme_id,
)
from packages.content_experiment_engine.snapshot_store import import_snapshot


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


if __name__ == "__main__":
    unittest.main()
