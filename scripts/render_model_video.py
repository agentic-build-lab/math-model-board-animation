from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = REPO_ROOT / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from model_animation.config_loader import load_video_config
from model_animation.media.contact_sheet import make_contact_sheet
from PIL import Image
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
    environment = inspect_environment()

    slug = config_path.stem
    version = datetime.now(timezone.utc).strftime("v%Y%m%dT%H%M%SZ")
    scene_id = str(config["scenes"][0].get("id", slug))
    output_dir = (args.output_dir or REPO_ROOT / "outputs" / "renders" / scene_id / f"{version}_{slug}").resolve()
    frames_dir = REPO_ROOT / "work" / "rendered_frames" / scene_id / f"{version}_{slug}"
    video_path = output_dir / f"{slug}_{version}.mp4"
    contact_sheet_path = output_dir / f"{slug}_{version}_contact_sheet.jpg"
    preview_path = output_dir / f"{slug}_{version}_preview.webp"
    html_preview_path = output_dir / "preview.html"
    report_path = output_dir / "render_report.json"

    output_dir.mkdir(parents=True, exist_ok=False)
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

    make_contact_sheet(frames_dir, contact_sheet_path)
    preview_status, preview_error = make_preview_webp(frames_dir, preview_path, ctx.fps)
    write_html_preview(html_preview_path, contact_sheet_path, preview_path if preview_status == "success" else None)
    encode_status = "success"
    encode_error = None
    try:
        encode_video(frames_dir, video_path, ctx.fps)
    except FileNotFoundError as exc:
        encode_status = "failed"
        encode_error = f"{exc}; ffmpeg is required to create mp4"
        video_path = None
    except subprocess.CalledProcessError as exc:
        encode_status = "failed"
        encode_error = str(exc)
        video_path = None
    elapsed = time.perf_counter() - started

    report = {
        "version": version,
        "slug": slug,
        "scene_id": scene_id,
        "config_path": str(config_path),
        "video_path": str(video_path) if video_path else None,
        "encode_status": encode_status,
        "encode_error": encode_error,
        "contact_sheet_path": str(contact_sheet_path),
        "preview_path": str(preview_path) if preview_status == "success" else None,
        "preview_status": preview_status,
        "preview_error": preview_error,
        "html_preview_path": str(html_preview_path),
        "frames_dir": str(frames_dir),
        "width": ctx.width,
        "height": ctx.height,
        "fps": ctx.fps,
        "duration": renderer.duration,
        "frame_count": frame_count,
        "elapsed_seconds": round(elapsed, 3),
        "template": config["style"]["template"],
        "chart_types": [scene["chart_type"] for scene in config["scenes"]],
        "environment": environment,
    }
    config_snapshot_path = output_dir / "config_snapshot.json"
    config_snapshot_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    notes_path = output_dir / "changes.md"
    review_path = output_dir / "review_notes.md"
    notes_path.write_text(
        f"# Render {version}\n\n- Source config: `{config_path}`\n- Template: `{config['style']['template']}`\n- Chart types: `{[scene['chart_type'] for scene in config['scenes']]}`\n- Change note: automated render snapshot; review visual quality from video and contact sheet.\n",
        encoding="utf-8",
    )
    review_path.write_text(
        "# Review notes\n\n"
        "## Gate checklist\n\n"
        "- [ ] Formula is mathematically correct and legible.\n"
        "- [ ] Subject curve/structure is readable at video speed.\n"
        "- [ ] Fill, glow, and particles feel premium rather than noisy.\n"
        "- [ ] Captions do not collide with formula or chart.\n"
        "- [ ] `render_report.json` has `encode_status: success` before publishing.\n"
        "- [ ] If mp4 is blocked, `preview.webp` / `preview.html` is sufficient only for draft motion review.\n",
        encoding="utf-8",
    )
    report["config_snapshot_path"] = str(config_snapshot_path)
    report["changes_path"] = str(notes_path)
    report["review_notes_path"] = str(review_path)
    append_manifest(report)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.keep_frames:
        shutil.rmtree(frames_dir)
        report["frames_dir"] = None
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"version: {version}")
    print(f"output_dir: {output_dir}")
    print(f"video: {video_path}")
    print(f"contact_sheet: {contact_sheet_path}")
    print(f"preview: {preview_path if preview_status == 'success' else None}")
    print(f"html_preview: {html_preview_path}")
    print(f"report: {report_path}")


def make_preview_webp(frames_dir: Path, output_path: Path, fps: int) -> tuple[str, str | None]:
    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_paths:
        return "failed", "no frames available"

    sample_step = max(1, round(fps / 8))
    sampled = frame_paths[::sample_step]
    duration_ms = max(60, round(1000 * sample_step / fps))
    try:
        frames = [Image.open(path).convert("RGB").resize((480, 270), Image.Resampling.LANCZOS) for path in sampled]
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            quality=82,
            method=4,
        )
    except Exception as exc:  # noqa: BLE001 - preview is best-effort and should not fail render reports.
        return "failed", str(exc)
    return "success", None


def write_html_preview(html_path: Path, contact_sheet_path: Path, preview_path: Path | None) -> None:
    preview_markup = (
        f'<h2>Motion preview</h2><img src="{preview_path.name}" alt="animated preview" />'
        if preview_path is not None
        else "<p>Animated preview unavailable; inspect render_report.json.</p>"
    )
    html_path.write_text(
        "<!doctype html>\n"
        "<meta charset=\"utf-8\">\n"
        "<title>Render Preview</title>\n"
        "<style>body{background:#050505;color:#e8ece9;font-family:Arial,sans-serif;margin:32px;}img{max-width:100%;height:auto;border:1px solid #28302e;}code{color:#2addca;}</style>\n"
        "<h1>Render Preview</h1>\n"
        f"{preview_markup}\n"
        f'<h2>Contact sheet</h2><img src="{contact_sheet_path.name}" alt="contact sheet" />\n'
        "<p>Draft preview only. Publish gate still requires a successful mp4 encode.</p>\n",
        encoding="utf-8",
    )


def inspect_environment() -> dict[str, Any]:
    ffmpeg_path = shutil.which("ffmpeg")
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "ffmpeg_path": ffmpeg_path,
        "ffmpeg_available": ffmpeg_path is not None,
    }


def append_manifest(report: dict[str, Any]) -> None:
    manifest_path = REPO_ROOT / "outputs" / "renders" / "manifest.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False) + "\n")


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
