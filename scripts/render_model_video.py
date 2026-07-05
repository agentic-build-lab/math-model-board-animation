from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = REPO_ROOT / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from model_animation.config_loader import load_video_config
from model_animation.media.contact_sheet import make_contact_sheet
from model_animation.render_context import RenderContext
from model_animation.styles.blackboard_formula import BlackboardFormulaRenderer


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a model board animation from JSON config.")
    parser.add_argument("--config", required=True, type=Path, help="Path to model video JSON config.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for final video outputs.")
    parser.add_argument("--keep-frames", action="store_true", help="Keep rendered frames under work/.")
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = load_video_config(config_path)
    ctx = RenderContext.from_config(config)
    renderer = build_renderer(config, ctx)

    slug = config_path.stem
    output_dir = (args.output_dir or REPO_ROOT / "outputs" / "renders" / slug).resolve()
    frames_dir = REPO_ROOT / "work" / "rendered_frames" / slug
    video_path = output_dir / f"{slug}.mp4"
    contact_sheet_path = output_dir / f"{slug}_contact_sheet.jpg"
    report_path = output_dir / "render_report.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    frame_count = int(round(renderer.duration * ctx.fps))
    started = time.perf_counter()
    for frame_index in range(frame_count):
        frame = renderer.render_frame(frame_index)
        frame.save(frames_dir / f"frame_{frame_index:05d}.jpg", quality=92, optimize=False)
        if frame_index % ctx.fps == 0:
            print(f"rendered {frame_index // ctx.fps:02d}s / {renderer.duration:.1f}s")

    encode_video(frames_dir, video_path, ctx.fps)
    make_contact_sheet(frames_dir, contact_sheet_path)
    elapsed = time.perf_counter() - started

    report = {
        "config_path": str(config_path),
        "video_path": str(video_path),
        "contact_sheet_path": str(contact_sheet_path),
        "frames_dir": str(frames_dir),
        "width": ctx.width,
        "height": ctx.height,
        "fps": ctx.fps,
        "duration": renderer.duration,
        "frame_count": frame_count,
        "elapsed_seconds": round(elapsed, 3),
        "template": config["style"]["template"],
        "chart_types": [scene["chart_type"] for scene in config["scenes"]],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.keep_frames:
        shutil.rmtree(frames_dir)
        report["frames_dir"] = None
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"video: {video_path}")
    print(f"contact_sheet: {contact_sheet_path}")
    print(f"report: {report_path}")


def build_renderer(config: dict[str, Any], ctx: RenderContext) -> BlackboardFormulaRenderer:
    template = config["style"]["template"]
    if template != "blackboard_formula":
        raise ValueError(f"第一版渲染器暂不支持 template={template}")
    return BlackboardFormulaRenderer(config, ctx)


def encode_video(frames_dir: Path, output_path: Path, fps: int) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%05d.jpg"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
