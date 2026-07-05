from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine.prediction_records import PredictionRecord, write_prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an immutable content prediction markdown record.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--target-workflow", required=True)
    parser.add_argument("--predicted-bucket", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rubric-version", default="content_video_v0")
    parser.add_argument(
        "--probability-json",
        default='{"tier1": 25, "tier2": 40, "tier3": 25, "skip": 10}',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    probability = json.loads(args.probability_json)
    record = PredictionRecord(
        candidate_id=args.candidate_id,
        title=args.title,
        target_workflow=args.target_workflow,
        rubric_version=args.rubric_version,
        predicted_bucket=args.predicted_bucket,
        probability={str(key): float(value) for key, value in probability.items()},
        reason=args.reason,
        factors=[],
    )
    prediction_hash = write_prediction(args.output, record)
    print(json.dumps({
        "prediction_path": str(args.output),
        "immutable_prediction_hash": prediction_hash,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
