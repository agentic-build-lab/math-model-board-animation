from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine import (
    fetch_public_bilibili_snapshot,
    fetch_public_video_snapshot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture a normalized public-video snapshot for content analysis."
    )
    parser.add_argument("--platform", choices=["douyin", "bilibili"], default="douyin")
    parser.add_argument("--url", required=True, help="Public video URL or aweme id.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/content_experiment/public_video_snapshot"),
    )
    parser.add_argument("--max-scrolls", type=int, default=8)
    parser.add_argument("--max-comments", type=int, default=30)
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Show browser window. Recommended for Douyin comment capture on local machines.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.platform == "bilibili":
        snapshot = fetch_public_bilibili_snapshot(
            args.url,
            args.output_dir,
            max_comments=args.max_comments,
        )
    else:
        snapshot = await fetch_public_video_snapshot(
            args.url,
            args.output_dir,
            max_scrolls=args.max_scrolls,
            headless=not args.headed,
        )
    print(json.dumps({
        "snapshot_path": str(args.output_dir / "snapshot.json"),
        "comments": len(snapshot.get("comments") or []),
        "limitations": snapshot.get("limitations") or [],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
