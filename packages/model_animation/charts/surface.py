from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SurfaceProjection:
    points: list[list[tuple[float, float, float]]]
    peak: tuple[float, float, float]


def project_loss_surface(
    *,
    center_x: float,
    center_y: float,
    scale: float,
    z_scale: float,
    angle: float,
    grid_size: int = 25,
) -> SurfaceProjection:
    """Project a smooth pseudo-3D loss surface into 2D screen coordinates."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    grid = np.linspace(-1.5, 1.5, grid_size)
    projected: list[list[tuple[float, float, float]]] = []
    peak = (center_x, center_y, float("-inf"))

    for gx in grid:
        row = []
        for gy in grid:
            radius2 = gx * gx + gy * gy
            z = math.exp(-radius2 * 0.75) * 1.25 - 0.22 * radius2
            xr = gx * cos_a - gy * sin_a
            yr = gx * sin_a + gy * cos_a
            sx = center_x + (xr - yr) * scale
            sy = center_y + (xr + yr) * scale * 0.42 - z * z_scale
            point = (sx, sy, z)
            row.append(point)
            if z > peak[2]:
                peak = point
        projected.append(row)

    return SurfaceProjection(points=projected, peak=peak)
