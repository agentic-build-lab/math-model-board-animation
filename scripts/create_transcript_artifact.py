from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.content_experiment_engine import (  # noqa: E402
    create_transcript_artifact,
    write_transcript_artifact,
)
from packages.content_experiment_engine.snapshot_store import upsert_transcript  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize transcript text into transcript.json and transcript.md."
    )
    parser.add_argument("--source", required=True, help="Original media or source path.")
    parser.add_argument("--transcript-file", type=Path, help="Plain text, SRT, VTT, or markdown transcript.")
    parser.add_argument("--text", help="Inline transcript text.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("--source-type", default="local_media")
    parser.add_argument("--language")
    parser.add_argument("--engine", default="manual_transcript")
    parser.add_argument("--duration-s", type=float)
    parser.add_argument("--database", type=Path, help="Optional SQLite database to import transcript.json into.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.transcript_file and not args.text:
        raise SystemExit("--transcript-file or --text is required.")
    if args.transcript_file:
        transcript_text = args.transcript_file.read_text(encoding="utf-8")
    else:
        transcript_text = args.text or ""

    artifact = create_transcript_artifact(
        source_path=args.source,
        source_type=args.source_type,
        title=args.title,
        transcript_text=transcript_text,
        language=args.language,
        engine=args.engine,
        duration_s=args.duration_s,
    )
    json_path, markdown_path = write_transcript_artifact(artifact, args.output_dir)
    imported_id = upsert_transcript(args.database, artifact.to_dict()) if args.database else None
    print(json.dumps({
        "transcript_id": artifact.transcript_id,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "database_transcript_id": imported_id,
        "segments": len(artifact.segments),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
