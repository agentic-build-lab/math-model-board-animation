from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine import write_content_review_markdown  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a human-readable markdown review from the content experiment SQLite database."
    )
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-rows", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = write_content_review_markdown(
        args.database,
        args.output,
        max_rows=args.max_rows,
    )
    print(json.dumps({"review_path": str(output_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
