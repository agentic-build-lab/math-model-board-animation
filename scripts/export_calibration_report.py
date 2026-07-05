from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.calibration_reports import (  # noqa: E402
    collect_calibration_samples,
    render_calibration_csv,
    render_calibration_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a prediction calibration CSV and markdown report."
    )
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--window", type=int, default=5)
    parser.add_argument(
        "--bucket-centers-json",
        help="Optional JSON mapping from bucket label to numeric center.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bucket_centers = json.loads(args.bucket_centers_json) if args.bucket_centers_json else None
    if bucket_centers is not None:
        bucket_centers = {str(key): float(value) for key, value in bucket_centers.items()}

    samples = collect_calibration_samples(args.predictions, bucket_centers=bucket_centers)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(
        render_calibration_markdown(samples, window=args.window),
        encoding="utf-8",
    )
    csv_path = args.output_csv
    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        csv_path.write_text(render_calibration_csv(samples), encoding="utf-8")
    print(json.dumps({
        "prediction_files": len(samples),
        "with_actual_values": sum(1 for sample in samples if sample.has_actual),
        "markdown_path": str(args.output_md),
        "csv_path": str(csv_path) if csv_path else None,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
