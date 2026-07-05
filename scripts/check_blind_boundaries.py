from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.blind_boundaries import (
    find_blind_metric_leaks,
    is_forbidden_for_blind_scoring,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether files are safe for blind scoring.")
    parser.add_argument("paths", nargs="+", help="Markdown or text files to scan.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    results = []
    has_problem = False
    for raw_path in args.paths:
        path = Path(raw_path)
        forbidden = is_forbidden_for_blind_scoring(path)
        text = path.read_text(encoding="utf-8")
        leaks = find_blind_metric_leaks(text, source=str(path))
        if forbidden or leaks:
            has_problem = True
        results.append(
            {
                "path": str(path),
                "forbidden_for_blind_scoring": forbidden,
                "metric_leaks": [finding.to_dict() for finding in leaks],
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "blocked" if result["forbidden_for_blind_scoring"] or result["metric_leaks"] else "ok"
            print(f"{status}: {result['path']}")
            if result["forbidden_for_blind_scoring"]:
                print("  - file name is forbidden for blind scoring")
            for finding in result["metric_leaks"]:
                print(f"  - line {finding['line_number']}: {finding['reason']} :: {finding['excerpt']}")
    raise SystemExit(1 if has_problem else 0)


if __name__ == "__main__":
    main()
