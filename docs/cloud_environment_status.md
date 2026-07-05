# Cloud environment status — 2026-07-05

## Git / PR verification

- Current branch observed in this cloud worker: `work`.
- Current commit observed before this round: `a5a4abe`.
- Working tree at the start of this round: clean.
- `gh` CLI is not installed in this worker, and no GitHub remote was available from `git remote -v`, so this worker cannot independently verify that a GitHub PR exists on `agentic-build-lab/math-model-board-animation`.
- The session can still call the provided `make_pr` tool after each commit, but that is a platform PR-recording action rather than a verifiable `gh pr view` result inside the container.

## Blocker matrix

| Blocker | Current status | Can agent solve in repo? | User / platform action needed |
| --- | --- | --- | --- |
| `ffmpeg` missing | `command -v ffmpeg` returns empty | Partially: scripts now keep frames/contact sheet/report/review notes and WebP/HTML preview without mp4 | Cloud/devcontainer/CI image must install `ffmpeg` for publishable mp4 |
| CJK fonts missing | no Noto/WenQuanYi CJK font discovered under `/usr/share/fonts` | Partially: renderer falls back to default fonts so runs do not crash | Install `fonts-noto-cjk` or mount approved brand fonts for final Chinese output |
| apt/pip proxy 403 | proxy variables are present; earlier apt/pip installs failed with HTTP 403 | Repo can document devcontainer/GitHub Actions install path | Platform/network owner must allow package install or provide prebuilt image |
| GitHub PR verification | `gh` absent and no remote configured | Agent can call `make_pr` tool after commit | User/platform should confirm PR in GitHub UI or expose `gh`/remote credentials |

## Recommended reproducible setup

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg fonts-noto-cjk
python -m pip install -r requirements.txt
python scripts/validate_model_video_input.py examples/garch_volatility_scene.json examples/capm_regression_scene.json examples/loss_surface_scene.json
python scripts/render_model_video.py --config examples/garch_volatility_scene.json
```

If apt/pip are blocked, use `.devcontainer/Dockerfile` or `.github/workflows/validate-and-render.yml` as the canonical dependency declaration and run in an environment where Debian and PyPI are reachable.
