from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages"))

from model_animation.charts.surface import project_loss_surface


class SurfaceProjectionTest(unittest.TestCase):
    def test_project_loss_surface_grid_and_minimum_are_stable(self) -> None:
        surface = project_loss_surface(center_x=960, center_y=540, scale=240, z_scale=110, angle=0.2, grid_size=25)
        self.assertEqual(len(surface.points), 25)
        self.assertEqual(len(surface.points[0]), 25)
        min_x, min_y, min_z = surface.minimum
        max_x, max_y, max_z = surface.maximum
        self.assertLess(min_z, max_z)
        self.assertGreater(min_x, 800)
        self.assertLess(min_x, 1120)
        self.assertGreater(min_y, 500)
        self.assertLess(min_y, 720)
        self.assertNotEqual((min_x, min_y), (max_x, max_y))


if __name__ == "__main__":
    unittest.main()
