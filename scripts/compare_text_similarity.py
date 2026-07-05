from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine import text_diff_percent  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two text/script/transcript files after markdown normalization."
    )
    parser.add_argument("original", type=Path)
    parser.add_argument("revised", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = text_diff_percent(
        args.original.read_text(encoding="utf-8"),
        args.revised.read_text(encoding="utf-8"),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
