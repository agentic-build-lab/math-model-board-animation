from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.brief_generator import generate_video_brief
from packages.content_experiment_engine.rubric import score_candidate
from packages.content_experiment_engine.snapshot_store import (
    import_candidates,
    import_video_briefs,
)
from packages.content_experiment_engine.trend_sources import (
    fetch_manual_topics,
    fetch_weibo_hot,
    fetch_zhihu_hot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover topic candidates and create workflow-neutral briefs.")
    parser.add_argument("--source", choices=["manual", "zhihu_hot", "weibo_hot"], default="manual")
    parser.add_argument("--topic", action="append", default=[], help="Manual topic. Can be passed multiple times.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--target-workflow",
        choices=[
            "evidence_driven_ai_video",
            "math_model_board_animation",
            "ai_editing_workflow",
            "quant_signal_research",
        ],
        default="evidence_driven_ai_video",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/content_experiment/topic_discovery"),
    )
    parser.add_argument("--database", type=Path, help="Optional SQLite database to import candidates and briefs into.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidates = _fetch_candidates(args)
    scored = [
        score_candidate(
            candidate,
            _default_dimension_scores(candidate.title, candidate.snapshot_text, args.source),
        )
        for candidate in candidates
    ]
    briefs = [
        generate_video_brief(candidate, target_workflow=args.target_workflow).to_dict()
        for candidate in scored
    ]

    (args.output_dir / "candidates.json").write_text(
        json.dumps([candidate.to_dict() for candidate in scored], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "video_briefs.json").write_text(
        json.dumps(briefs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    imported = None
    if args.database:
        imported = {
            "candidate_ids": import_candidates(args.database, args.output_dir / "candidates.json"),
            "brief_ids": import_video_briefs(args.database, args.output_dir / "video_briefs.json"),
        }
    print(json.dumps({
        "candidates": len(scored),
        "briefs": len(briefs),
        "output_dir": str(args.output_dir),
        "database": str(args.database) if args.database else None,
        "imported": imported,
    }, ensure_ascii=False, indent=2))


def _fetch_candidates(args: argparse.Namespace):
    if args.source == "zhihu_hot":
        return fetch_zhihu_hot(limit=args.limit)
    if args.source == "weibo_hot":
        return fetch_weibo_hot(limit=args.limit)
    return fetch_manual_topics(args.topic or ["Codex content workflow"], source="manual:user")


def _default_dimension_scores(title: str, snapshot_text: str, source: str) -> dict[str, int]:
    text = f"{title}\n{snapshot_text}"
    scores = {
        "er": 3,
        "hp": 3,
        "ql": 3,
        "na": 3,
        "ab": 3,
        "sr": 3,
        "ev": 3,
    }
    if source in {"zhihu_hot", "weibo_hot"}:
        scores["sr"] = 4
        scores["ab"] = 4
    if any(token.lower() in text.lower() for token in ("ai", "agent", "codex", "github", "openai", "模型")):
        scores["sr"] = min(5, scores["sr"] + 1)
        scores["hp"] = min(5, scores["hp"] + 1)
    if "?" in text or "？" in text or any(token in text for token in ("为什么", "如何", "怎么")):
        scores["hp"] = min(5, scores["hp"] + 1)
        scores["na"] = min(5, scores["na"] + 1)
    return scores


if __name__ == "__main__":
    main()
