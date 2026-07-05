from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import ImageDraw, ImageFont


FONT_CN_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
FONT_CN_BOLD_CANDIDATES = [
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
FONT_MATH_CANDIDATES = [
    Path("C:/Windows/Fonts/cambriai.ttf"),
    Path("C:/Windows/Fonts/cambria.ttc"),
    Path("C:/Windows/Fonts/times.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
FONT_MATH_BOLD_CANDIDATES = [
    Path("C:/Windows/Fonts/cambriab.ttf"),
    Path("C:/Windows/Fonts/cambria.ttc"),
    Path("C:/Windows/Fonts/timesbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]


@dataclass(frozen=True)
class RenderContext:
    width: int
    height: int
    fps: int
    fonts: dict[str, ImageFont.FreeTypeFont]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RenderContext":
        video = config["video"]
        width = int(video.get("width", 1920))
        height = int(video.get("height", 1080))
        fps = int(video.get("fps", 60))
        return cls(
            width=width,
            height=height,
            fps=fps,
            fonts={
                "title": load_first_font(FONT_CN_BOLD_CANDIDATES, 44),
                "subtitle": load_first_font(FONT_CN_CANDIDATES, 22),
                "caption": load_first_font(FONT_CN_BOLD_CANDIDATES, 30),
                "small": load_first_font(FONT_CN_CANDIDATES, 20),
                "formula": load_first_font(FONT_MATH_CANDIDATES, 58),
                "formula_small": load_first_font(FONT_MATH_CANDIDATES, 44),
                "formula_bold": load_first_font(FONT_MATH_BOLD_CANDIDATES, 46),
            },
        )


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def load_first_font(paths: list[Path], size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        if path.exists():
            return load_font(path, size)
    return ImageFont.load_default()


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], max(0, min(255, alpha))


def text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    ctx: RenderContext,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    alpha: int = 255,
) -> None:
    width, _ = text_size(draw, text, font)
    draw.text(((ctx.width - width) / 2, y), text, font=font, fill=rgba(fill, alpha))
