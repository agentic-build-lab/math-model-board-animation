from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from model_animation.easing import clamp, ease_out, lerp
from model_animation.charts.surface import project_loss_surface
from model_animation.render_context import (
    RenderContext,
    draw_centered_text,
    rgba,
    text_size,
)


BLACK = (0, 0, 0)
WHITE = (226, 230, 226)
DIM = (118, 126, 122)
AXIS = (198, 204, 201)
TEAL = (42, 221, 202)
RED_LINE = (240, 130, 124)
RED_LINE_CORE = (255, 164, 157)
RED_FILL = (135, 48, 38)
GOLD = (227, 196, 96)

REFERENCE_GARCH_PROFILE = [
    (0.0000, 0.1061), (0.0125, 0.1061), (0.0255, 0.0980), (0.0380, 0.1138),
    (0.0505, 0.0949), (0.0634, 0.0694), (0.0760, 0.0640), (0.0885, 0.1124),
    (0.1014, 0.1052), (0.1140, 0.0704), (0.1265, 0.1117), (0.1391, 0.0787),
    (0.1520, 0.1016), (0.1645, 0.0884), (0.1771, 0.0923), (0.1900, 0.1087),
    (0.2025, 0.1268), (0.2150, 0.1087), (0.2280, 0.0628), (0.2405, 0.1082),
    (0.2530, 0.1050), (0.2660, 0.1872), (0.2785, 0.1534), (0.2910, 0.1259),
    (0.3039, 0.1169), (0.3165, 0.0963), (0.3290, 0.1596), (0.3419, 0.1135),
    (0.3545, 0.1283), (0.3670, 0.0776), (0.3796, 0.1500), (0.3925, 0.0520),
    (0.4050, 0.0180), (0.4176, 0.0260), (0.4305, 0.0440), (0.4430, 0.0640),
    (0.4556, 0.0860), (0.4685, 0.1111), (0.4810, 0.1585), (0.4935, 0.2817),
    (0.5065, 0.2852), (0.5190, 0.4138), (0.5315, 0.3427), (0.5444, 0.2271),
    (0.5570, 0.1895), (0.5695, 0.1579), (0.5824, 0.0421), (0.5950, 0.0577),
    (0.6075, 0.0957), (0.6204, 0.0328), (0.6330, 0.1053), (0.6455, 0.1020),
    (0.6581, 0.2113), (0.6710, 0.1471), (0.6835, 0.0598), (0.6961, 0.1443),
    (0.7090, 0.1322), (0.7215, 0.0537), (0.7340, 0.1257), (0.7470, 0.0929),
    (0.7595, 0.1135), (0.7720, 0.1063), (0.7850, 0.1040), (0.7975, 0.0300),
    (0.8100, 0.0849), (0.8229, 0.0745), (0.8355, 0.1363), (0.8480, 0.0747),
    (0.8609, 0.0904), (0.8735, 0.1395), (0.8860, 0.0837), (0.8986, 0.1299),
    (0.9115, 0.0849), (0.9240, 0.0966), (0.9366, 0.1059), (0.9495, 0.0805),
    (0.9620, 0.0944), (0.9745, 0.0921), (0.9875, 0.1123), (1.0000, 0.1123),
]


class BlackboardFormulaRenderer:
    def __init__(self, config: dict[str, Any], ctx: RenderContext) -> None:
        self.config = config
        self.ctx = ctx
        self.scenes = config["scenes"]
        self.timeline = self._build_timeline()
        self.star_points = self._make_star_points()

    @property
    def duration(self) -> float:
        return self.timeline[-1][1]

    def render_frame(self, frame_index: int) -> Image.Image:
        t = frame_index / self.ctx.fps
        image = Image.new("RGBA", (self.ctx.width, self.ctx.height), BLACK)
        self._draw_background(image, t)
        draw = ImageDraw.Draw(image, "RGBA")

        scene, scene_t = self._scene_at(t)
        if scene["chart_type"] == "volatility_area":
            self._draw_volatility_area_scene(image, draw, scene, scene_t)
        elif scene["chart_type"] == "scatter_regression":
            self._draw_scatter_regression_scene(image, draw, scene, scene_t)
        elif scene["chart_type"] == "rotating_surface":
            self._draw_rotating_surface_scene(image, draw, scene, scene_t)
        else:
            raise ValueError(f"黑板模板暂不支持 chart_type={scene['chart_type']}")
        return image.convert("RGB")

    def _build_timeline(self) -> list[tuple[float, float, dict[str, Any]]]:
        cursor = 0.0
        timeline = []
        for scene in self.scenes:
            duration = float(scene["duration"])
            timeline.append((cursor, cursor + duration, scene))
            cursor += duration
        return timeline

    def _scene_at(self, t: float) -> tuple[dict[str, Any], float]:
        for start, end, scene in self.timeline:
            if t < end:
                return scene, t - start
        start, _, scene = self.timeline[-1]
        return scene, max(0.0, t - start)

    def _make_star_points(self) -> list[tuple[float, float, float, float]]:
        rng = np.random.default_rng(20260705)
        width = self.ctx.width
        height = self.ctx.height
        return [
            (
                float(rng.uniform(20, width - 20)),
                float(rng.uniform(35, height - 35)),
                float(rng.uniform(0, math.tau)),
                float(rng.uniform(0.65, 1.45)),
            )
            for _ in range(64)
        ]

    def _draw_background(self, image: Image.Image, t: float) -> None:
        image.paste(BLACK, (0, 0, self.ctx.width, self.ctx.height))
        draw = ImageDraw.Draw(image, "RGBA")

        for x0, y0, phase, radius in self.star_points:
            x = x0 + math.sin(t * 0.08 + phase) * 2.2
            y = y0 + math.cos(t * 0.07 + phase) * 1.8
            alpha = 8 + int(15 * (0.5 + 0.5 * math.sin(t * 0.42 + phase)))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, alpha))

        vignette = Image.new("RGBA", image.size, (0, 0, 0, 0))
        vd = ImageDraw.Draw(vignette, "RGBA")
        for inset in range(0, 420, 34):
            alpha = int(4 + inset / 12)
            vd.rectangle(
                (inset, inset, self.ctx.width - inset, self.ctx.height - inset),
                outline=(0, 0, 0, alpha),
                width=34,
            )
        image.alpha_composite(vignette)

    def _draw_volatility_area_scene(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        t: float,
    ) -> None:
        title_alpha = int(255 * ease_out(t / 0.55))
        draw_centered_text(draw, self.ctx, 73, scene["title"], self.ctx.fonts["title"], TEAL, title_alpha)
        if scene.get("subtitle"):
            draw_centered_text(draw, self.ctx, 132, scene["subtitle"], self.ctx.fonts["subtitle"], DIM, title_alpha)

        axis_alpha = int(205 * ease_out((t - 0.12) / 0.35))
        box = self._draw_axis(draw, alpha=axis_alpha)

        mapped_points = self._reference_garch_points(box)
        values = np.array([box[3] - y for _, y in mapped_points], dtype=float)
        is_teaching = scene.get("animation", {}).get("chart") == "staged_volatility_teaching"
        chart_start = 4.0 if is_teaching else 0.45
        chart_span = 8.5 if is_teaching else 2.2
        chart_progress = ease_out((t - chart_start) / chart_span)
        points = partial_points(mapped_points, chart_progress)
        self._fill_under_curve(image, points, box[3], RED_FILL, alpha_low=42, alpha_high=108)
        self._line(
            image,
            points,
            RED_LINE,
            width=4,
            alpha=255,
            core_color=RED_LINE_CORE,
            core_alpha=255,
            glow_color=RED_LINE_CORE,
            glow_alpha=105,
            glow_width=9,
            glow_radius=1.25,
        )

        formula_text = scene["formula"]["text"]
        formula_start = 2.0 if is_teaching else 0.9
        formula_alpha = int(255 * ease_out((t - formula_start) / 0.55))
        self._draw_formula(draw, formula_text, round(self.ctx.height * 0.755), formula_alpha)

        if scene.get("emphasis"):
            self._draw_emphasis(image, draw, scene, values, box, t, mapped_points)
        if is_teaching:
            self._draw_teaching_stage_notes(draw, scene, t, box)
        self._draw_active_caption(draw, scene, t)


    def _draw_teaching_stage_notes(
        self,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        t: float,
        box: tuple[int, int, int, int],
    ) -> None:
        if t < 6.0:
            return
        left, top, right, bottom = box
        stages = [
            (6.0, 10.0, "calm", "低波动基线"),
            (10.0, 14.0, "shock", "冲击抬升风险"),
            (14.0, 18.5, "clustering", "波动聚集持续"),
            (18.5, 22.5, "decay", "冲击影响缓慢衰减"),
        ]
        active = None
        for start, end, key, label in stages:
            if start <= t < end:
                active = (start, end, key, label)
                break
        if active is None:
            return
        start, end, key, label = active
        alpha = int(180 * min(ease_out((t - start) / 0.45), ease_out((end - t) / 0.45)))
        x = left + (right - left) * {"calm": 0.18, "shock": 0.50, "clustering": 0.62, "decay": 0.78}[key]
        y = top + 26
        draw.text((x - 58, y), label, font=self.ctx.fonts["small"], fill=rgba(GOLD, alpha))
        draw.line((x, y + 28, x, bottom - 22), fill=rgba(GOLD, int(alpha * 0.45)), width=1)

    def _draw_scatter_regression_scene(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        t: float,
    ) -> None:
        title_alpha = int(255 * ease_out(t / 0.55))
        draw_centered_text(draw, self.ctx, 73, scene["title"], self.ctx.fonts["title"], TEAL, title_alpha)
        if scene.get("subtitle"):
            draw_centered_text(draw, self.ctx, 132, scene["subtitle"], self.ctx.fonts["subtitle"], DIM, title_alpha)

        axis_alpha = int(205 * ease_out((t - 0.12) / 0.35))
        box = self._draw_axis(draw, alpha=axis_alpha)
        left, top, right, bottom = box
        rng = np.random.default_rng(int(scene.get("data_source", {}).get("seed", 20260705)))
        beta = float(scene.get("parameters", {}).get("beta", 1.18))
        alpha = float(scene.get("parameters", {}).get("alpha", 0.02))
        x = np.linspace(-1, 1, 70)
        y = alpha + beta * x + rng.normal(0, 0.22, len(x))
        x_norm = (x - x.min()) / (x.max() - x.min())
        y_norm = (y - y.min()) / (y.max() - y.min())
        points = [(left + float(xx) * (right - left), bottom - (0.10 + float(yy) * 0.78) * (bottom - top)) for xx, yy in zip(x_norm, y_norm)]
        point_progress = ease_out((t - 0.42) / 1.2)
        visible = int(len(points) * point_progress)
        for i, (px, py) in enumerate(points[:visible]):
            pulse = 0.75 + 0.25 * math.sin(t * 2.0 + i * 0.7)
            r = 4.2
            draw.ellipse((px - r, py - r, px + r, py + r), fill=rgba(TEAL, int(150 * pulse)))
        line_progress = ease_out((t - 1.15) / 1.35)
        y1 = alpha + beta * x.min()
        y2 = alpha + beta * x.max()
        yn1 = (y1 - y.min()) / (y.max() - y.min())
        yn2 = (y2 - y.min()) / (y.max() - y.min())
        line = [(left, bottom - (0.10 + yn1 * 0.78) * (bottom - top)), (right, bottom - (0.10 + yn2 * 0.78) * (bottom - top))]
        self._line(image, partial_points(line, line_progress), GOLD, width=4, alpha=int(235 * line_progress), core_color=WHITE, core_alpha=int(115 * line_progress), glow_color=GOLD, glow_alpha=int(85 * line_progress), glow_width=10, glow_radius=1.4)
        formula_start = 6.0 if is_showcase else 0.9
        formula_alpha = int(255 * ease_out((t - formula_start) / 0.65))
        self._draw_formula(draw, scene["formula"]["text"], round(self.ctx.height * 0.755), formula_alpha)
        self._draw_active_caption(draw, scene, t)

    def _draw_rotating_surface_scene(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        t: float,
    ) -> None:
        title_alpha = int(255 * ease_out(t / 0.55))
        draw_centered_text(draw, self.ctx, 73, scene["title"], self.ctx.fonts["title"], TEAL, title_alpha)
        if scene.get("subtitle"):
            draw_centered_text(draw, self.ctx, 132, scene["subtitle"], self.ctx.fonts["subtitle"], DIM, title_alpha)

        is_showcase = scene.get("animation", {}).get("chart") == "surface_showcase_orbit"
        progress = ease_out((t - (1.6 if is_showcase else 0.32)) / (6.0 if is_showcase else 1.35))
        cx = self.ctx.width * 0.50
        cy = self.ctx.height * 0.47
        scale = self.ctx.width * 0.135
        z_scale = self.ctx.height * 0.105
        angle_speed = 0.24 if is_showcase else 0.72
        angle = -0.65 + 0.55 * math.sin(t * angle_speed)
        surface = project_loss_surface(
            center_x=cx,
            center_y=cy,
            scale=scale,
            z_scale=z_scale,
            angle=angle,
            grid_size=25,
        )
        projected = surface.points

        line_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_layer, "RGBA")
        visible_cols = max(2, int(len(projected) * progress))
        for row in projected[:visible_cols]:
            self._surface_polyline(line_draw, row[:visible_cols], TEAL, int(92 * progress), 2)
        for col in range(visible_cols):
            self._surface_polyline(line_draw, [projected[row][col] for row in range(visible_cols)], TEAL, int(70 * progress), 2)
        glow = line_layer.filter(ImageFilter.GaussianBlur(1.3))
        image.alpha_composite(glow)
        image.alpha_composite(line_layer)

        minimum = surface.minimum
        minimum_alpha = int(235 * ease_out((t - 1.15) / 0.75))
        r = 7 + 2 * math.sin(t * 3.0)
        draw.ellipse((minimum[0] - r, minimum[1] - r, minimum[0] + r, minimum[1] + r), fill=rgba(GOLD, minimum_alpha))
        draw.line((minimum[0], minimum[1] + 10, minimum[0], minimum[1] + 78), fill=rgba(GOLD, int(120 * progress)), width=2)

        label_alpha = int(150 * progress)
        draw.text((cx - scale * 1.8, cy + scale * 0.92), "θ₁", font=self.ctx.fonts["small"], fill=rgba(AXIS, label_alpha))
        draw.text((cx + scale * 1.48, cy + scale * 0.68), "θ₂", font=self.ctx.fonts["small"], fill=rgba(AXIS, label_alpha))
        draw.text((minimum[0] + 16, minimum[1] - 28), "min L(θ)", font=self.ctx.fonts["small"], fill=rgba(GOLD, int(190 * progress)))

        formula_start = 6.0 if is_showcase else 0.9
        formula_alpha = int(255 * ease_out((t - formula_start) / 0.65))
        self._draw_formula(draw, scene["formula"]["text"], round(self.ctx.height * 0.755), formula_alpha)
        self._draw_active_caption(draw, scene, t)

    def _surface_polyline(
        self,
        draw: ImageDraw.ImageDraw,
        points_3d: list[tuple[float, float, float]],
        color: tuple[int, int, int],
        alpha: int,
        width: int,
    ) -> None:
        if len(points_3d) < 2:
            return
        points = [(x, y) for x, y, _ in points_3d]
        avg_z = sum(z for _, _, z in points_3d) / len(points_3d)
        depth_alpha = int(alpha * clamp((avg_z + 1.0) / 2.3, 0.28, 1.0))
        draw.line(points, fill=rgba(color, depth_alpha), width=width, joint="curve")

    def _draw_axis(
        self,
        draw: ImageDraw.ImageDraw,
        alpha: int,
        ticks_x: int = 9,
        ticks_y: int = 5,
    ) -> tuple[int, int, int, int]:
        box = (
            round(self.ctx.width * (294 / 1920)),
            round(self.ctx.height * (225 / 1080)),
            round(self.ctx.width * (1650 / 1920)),
            round(self.ctx.height * (750 / 1080)),
        )
        left, top, right, bottom = box
        draw.line((left, bottom, right, bottom), fill=rgba(AXIS, alpha), width=3)
        draw.line((left, bottom, left, top), fill=rgba(AXIS, alpha), width=3)
        draw.polygon([(right, bottom), (right - 24, bottom - 13), (right - 24, bottom + 13)], fill=rgba(AXIS, alpha))
        draw.polygon([(left, top), (left - 13, top + 24), (left + 13, top + 24)], fill=rgba(AXIS, alpha))

        tick_alpha = min(alpha, 125)
        for i in range(1, ticks_x + 1):
            x = left + (right - left) * i / (ticks_x + 1)
            draw.line((x, bottom - 10, x, bottom + 10), fill=rgba(AXIS, tick_alpha), width=2)
        for i in range(1, ticks_y + 1):
            y = bottom - (bottom - top) * i / (ticks_y + 1)
            draw.line((left - 10, y, left + 10, y), fill=rgba(AXIS, tick_alpha), width=2)
        return box

    def _synthetic_volatility_values(self, scene: dict[str, Any]) -> np.ndarray:
        data_source = scene.get("data_source", {})
        seed = int(data_source.get("seed", 20260705))
        rng = np.random.default_rng(seed)
        x = np.linspace(0, 1, 240)
        values = 0.25 + 0.025 * np.sin(x * 58 * math.pi)
        values += 0.01 * rng.normal(0, 1, len(x))
        values += -0.15 * np.exp(-((x - 0.39) ** 2) / 0.0009)
        values += 0.36 * np.exp(-((x - 0.515) ** 2) / 0.0015)
        values += 0.19 * np.exp(-((x - 0.548) ** 2) / 0.00042)
        values += 0.15 * np.exp(-((x - 0.645) ** 2) / 0.0017)
        values += 0.08 * np.exp(-((x - 0.705) ** 2) / 0.0008)
        return values

    def _reference_garch_points(self, box: tuple[int, int, int, int], count: int = 240) -> list[tuple[float, float]]:
        left, top, right, bottom = box
        xs = np.array([point[0] for point in REFERENCE_GARCH_PROFILE], dtype=float)
        ys = np.array([point[1] for point in REFERENCE_GARCH_PROFILE], dtype=float)
        x_norm = np.linspace(0, 1, count)
        y_norm = np.interp(x_norm, xs, ys)
        y_norm = 0.10 + y_norm * 0.76
        return [
            (
                left + float(x) * (right - left),
                bottom - float(y) * (bottom - top),
            )
            for x, y in zip(x_norm, y_norm)
        ]

    def _draw_formula(self, draw: ImageDraw.ImageDraw, text: str, y: int, alpha: int) -> None:
        font = self.ctx.fonts["formula"]
        width, _ = text_size(draw, text, font)
        x = (self.ctx.width - width) / 2
        draw.text((x, y), text, font=font, fill=rgba(WHITE, alpha))

    def _fill_under_curve(
        self,
        image: Image.Image,
        points: list[tuple[float, float]],
        bottom: int,
        color: tuple[int, int, int],
        alpha_low: int,
        alpha_high: int,
    ) -> None:
        if len(points) < 2:
            return
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        polygon = [(points[0][0], bottom)] + points + [(points[-1][0], bottom)]
        draw.polygon(polygon, fill=255)

        top = max(0, int(min(y for _, y in points)))
        alpha_gradient = Image.new("L", image.size, 0)
        gradient_draw = ImageDraw.Draw(alpha_gradient)
        span = max(1, bottom - top)
        for y in range(top, min(image.height, bottom + 1)):
            progress = (bottom - y) / span
            alpha = round(alpha_low + (alpha_high - alpha_low) * progress)
            gradient_draw.line((0, y, image.width, y), fill=alpha)

        fill_alpha = ImageChops.multiply(mask, alpha_gradient)
        fill_layer = Image.new("RGBA", image.size, color + (0,))
        fill_layer.putalpha(fill_alpha)
        image.alpha_composite(fill_layer)

    def _line(
        self,
        image: Image.Image,
        points: list[tuple[float, float]],
        color: tuple[int, int, int],
        width: int,
        alpha: int,
        core_color: tuple[int, int, int] | None = None,
        core_alpha: int = 0,
        glow_color: tuple[int, int, int] | None = None,
        glow_alpha: int = 0,
        glow_width: int = 0,
        glow_radius: float = 0.0,
    ) -> None:
        if len(points) < 2:
            return
        if glow_color is not None and glow_alpha > 0 and glow_width > 0:
            glow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer, "RGBA")
            glow_draw.line(points, fill=rgba(glow_color, glow_alpha), width=glow_width, joint="curve")
            if glow_radius > 0:
                glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow_radius))
            image.alpha_composite(glow_layer)

        draw = ImageDraw.Draw(image, "RGBA")
        draw.line(points, fill=rgba(color, alpha), width=width, joint="curve")
        if core_color is not None and core_alpha > 0:
            draw.line(points, fill=rgba(core_color, core_alpha), width=1, joint="curve")

    def _draw_emphasis(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        values: np.ndarray,
        box: tuple[int, int, int, int],
        t: float,
        points: list[tuple[float, float]],
    ) -> None:
        if not scene.get("emphasis"):
            return
        emphasis = scene["emphasis"][0]
        start, end = emphasis.get("time", [2.4, 3.4])
        progress = clamp((t - float(start)) / max(0.001, float(end) - float(start)))
        if progress <= 0:
            return

        peak_index = int(np.argmax(values))
        peak_x, peak_y = points[peak_index]
        alpha = int(135 * clamp(progress / 0.35) * clamp((1.2 - progress) / 0.35))
        if alpha <= 0:
            return

        tick_height = 18
        draw.line(
            (peak_x, peak_y - tick_height, peak_x, peak_y - 5),
            fill=rgba(GOLD, alpha),
            width=1,
        )
        dot_radius = 3
        draw.ellipse(
            (peak_x - dot_radius, peak_y - dot_radius, peak_x + dot_radius, peak_y + dot_radius),
            fill=rgba(GOLD, alpha),
        )


    def _draw_active_caption(
        self,
        draw: ImageDraw.ImageDraw,
        scene: dict[str, Any],
        t: float,
    ) -> None:
        captions = scene.get("captions", [])
        active_caption = None
        for caption in captions:
            start, end = caption["time"]
            if float(start) <= t <= float(end):
                active_caption = caption
                break
        if active_caption is None and captions:
            active_caption = captions[-1]

        if not active_caption:
            return

        start, end = active_caption["time"]
        fade_in = clamp((t - float(start)) / 0.25)
        fade_out = clamp((float(end) - t) / 0.25)
        alpha = int(238 * min(ease_out(fade_in), ease_out(fade_out)))
        draw_centered_text(
            draw,
            self.ctx,
            round(self.ctx.height * 0.91),
            active_caption["text"],
            self.ctx.fonts["caption"],
            GOLD,
            alpha,
        )


def map_points(
    values: np.ndarray,
    box: tuple[int, int, int, int],
    low: float = 0.06,
    high: float = 0.94,
) -> list[tuple[float, float]]:
    left, top, right, bottom = box
    vmin = float(values.min())
    vmax = float(values.max())
    span = max(1e-6, vmax - vmin)
    points: list[tuple[float, float]] = []
    for index, value in enumerate(values):
        x = left + (right - left) * index / max(1, len(values) - 1)
        norm = (float(value) - vmin) / span
        norm = low + norm * (high - low)
        y = bottom - norm * (bottom - top)
        points.append((x, y))
    return points


def partial_points(points: list[tuple[float, float]], progress: float) -> list[tuple[float, float]]:
    if len(points) < 2:
        return points
    progress = clamp(progress)
    limit = progress * (len(points) - 1)
    whole = int(limit)
    fraction = limit - whole
    result = points[: whole + 1]
    if whole < len(points) - 1:
        x1, y1 = points[whole]
        x2, y2 = points[whole + 1]
        result.append((lerp(x1, x2, fraction), lerp(y1, y2, fraction)))
    return result
