from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.prediction_records import append_retro


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append retrospective notes without changing prediction text.")
    parser.add_argument("--prediction", type=Path, required=True)
    parser.add_argument("--retro", type=Path, help="Markdown file to append.")
    parser.add_argument("--text", help="Inline retrospective markdown.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.retro:
        retro_markdown = args.retro.read_text(encoding="utf-8")
    elif args.text:
        retro_markdown = args.text
    else:
        raise SystemExit("Provide --retro or --text.")
    prediction_hash = append_retro(args.prediction, retro_markdown)
    print(json.dumps({
        "prediction_path": str(args.prediction),
        "immutable_prediction_hash": prediction_hash,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
