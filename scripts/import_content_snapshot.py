from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.snapshot_store import import_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a content snapshot JSON into SQLite.")
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("outputs/content_experiment/content_experiment.db"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    snapshot_id = import_snapshot(args.database, args.snapshot)
    print(f"imported snapshot_id={snapshot_id} database={args.database}")


if __name__ == "__main__":
    main()
