from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.learning_artifacts import initialize_learning_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Create content experiment learning artifacts.")
    parser.add_argument("--output-dir", required=True, help="Directory for audience, benchmark, patterns, and state.")
    parser.add_argument("--project-name", default="content_experiment")
    parser.add_argument("--benchmark-name", default="[benchmark-name]")
    parser.add_argument("--platform", default="[platform]")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    written = initialize_learning_artifacts(
        Path(args.output_dir),
        project_name=args.project_name,
        benchmark_name=args.benchmark_name,
        platform=args.platform,
        overwrite=args.overwrite,
    )
    print(json.dumps({"written": [str(path) for path in written]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
