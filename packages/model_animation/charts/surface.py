from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SurfaceProjection:
    points: list[list[tuple[float, float, float]]]
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]


def project_loss_surface(
    *,
    center_x: float,
    center_y: float,
    scale: float,
    z_scale: float,
    angle: float,
    grid_size: int = 25,
) -> SurfaceProjection:
    """Project a smooth pseudo-3D loss basin into 2D screen coordinates.

    The third coordinate is loss height. Lower z means a better objective value,
    so `minimum` is the point to highlight for optimization scenes.
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    grid = np.linspace(-1.5, 1.5, grid_size)
    projected: list[list[tuple[float, float, float]]] = []
    minimum = (center_x, center_y, float("inf"))
    maximum = (center_x, center_y, float("-inf"))

    for gx in grid:
        row = []
        for gy in grid:
            radius2 = gx * gx + gy * gy
            z = 0.28 * radius2 - 1.15 * math.exp(-radius2 * 0.82)
            xr = gx * cos_a - gy * sin_a
            yr = gx * sin_a + gy * cos_a
            sx = center_x + (xr - yr) * scale
            sy = center_y + (xr + yr) * scale * 0.42 - z * z_scale
            point = (sx, sy, z)
            row.append(point)
            if z < minimum[2]:
                minimum = point
            if z > maximum[2]:
                maximum = point
        projected.append(row)

    return SurfaceProjection(points=projected, minimum=minimum, maximum=maximum)
