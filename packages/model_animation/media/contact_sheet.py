from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def make_contact_sheet(
    frames_dir: Path,
    output_path: Path,
    columns: int = 4,
    rows: int = 3,
    thumb_width: int = 480,
) -> None:
    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_paths:
        raise FileNotFoundError(f"未找到帧文件：{frames_dir}")

    total = len(frame_paths)
    sample_count = min(columns * rows, total)
    indices = [
        round(i * (total - 1) / max(1, sample_count - 1))
        for i in range(sample_count)
    ]

    first = Image.open(frame_paths[0])
    thumb_height = round(first.height * thumb_width / first.width)
    label_height = 30
    sheet = Image.new(
        "RGB",
        (columns * thumb_width, rows * (thumb_height + label_height)),
        (0, 0, 0),
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)

    for slot, frame_index in enumerate(indices):
        image = Image.open(frame_paths[frame_index]).convert("RGB")
        image = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = (slot % columns) * thumb_width
        y = (slot // columns) * (thumb_height + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 10, y + thumb_height + 4), f"frame {frame_index}", font=font, fill=(190, 195, 192))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=92)
