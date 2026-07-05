# Render CI Environment

This project uses GitHub Actions and a devcontainer to keep video rendering
reproducible. The CI runner installs the real render dependencies instead of
expecting a Codex task container to provide them.

## Runtime Dependencies

- Python 3.12
- `ffmpeg`
- `fonts-noto-cjk`
- `fonts-noto-color-emoji`
- `fonts-dejavu-core`
- Python packages from `requirements.txt`

## CI Contract

The workflow at `.github/workflows/render-preview.yml` runs:

1. dependency installation;
2. unit tests;
3. a sample GARCH render;
4. artifact validation;
5. artifact upload.

The generated MP4, contact sheet, and render report are uploaded as GitHub
Actions artifacts with short retention. They are not committed to Git by
default.

## Local Devcontainer

Open the repository in the devcontainer and run:

```bash
python scripts/render_model_video.py \
  --config examples/garch_volatility_scene.json \
  --output-dir outputs/renders/local_garch_volatility_scene
```

## Artifact Policy

Commit source configs, recipes, manifests, review notes, and small diagnostic
fixtures. Keep large videos, frame sequences, temporary browser state, cookies,
and failed experimental renders out of Git unless a specific artifact has been
reviewed and approved as a durable case study.
