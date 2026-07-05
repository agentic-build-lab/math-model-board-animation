# Whisper Script Extraction Contract

This contract preserves the upstream Whisper adapter idea without forcing an ASR
engine into the core package.

## Purpose

Convert user-provided audio or video files into transcript artifacts for:

- benchmark account learning;
- video review;
- script comparison;
- downstream topic and hook analysis.

## Boundary

The repository already supports normalized transcript artifacts through:

- `packages.content_experiment_engine.transcripts`
- `scripts/create_transcript_artifact.py`

Whisper, whisper.cpp, cloud ASR, or manual transcripts can all feed that same
contract.

## Expected Local Input

```json
{
  "source_path": "samples/reference_creator/video/source.mp4",
  "engine": "whisper_cpp_medium",
  "language": "zh",
  "output_dir": "outputs/content_experiment/transcripts/reference_video"
}
```

## Expected Output

- `transcript.json`
- `transcript.md`

The transcript should be paragraph-readable, not raw subtitle line fragments.

## Operational Notes

- Prefer user-provided transcripts when available; they are usually more
  accurate than ASR.
- Do not download benchmark videos inside this adapter.
- Keep model files and raw media out of git.
