from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages"))

from model_animation.charts.surface import project_loss_surface


class SurfaceProjectionTest(unittest.TestCase):
    def test_project_loss_surface_grid_and_peak_are_stable(self) -> None:
        surface = project_loss_surface(center_x=960, center_y=540, scale=240, z_scale=110, angle=0.2, grid_size=25)
        self.assertEqual(len(surface.points), 25)
        self.assertEqual(len(surface.points[0]), 25)
        peak_x, peak_y, peak_z = surface.peak
        self.assertGreater(peak_z, 1.0)
        self.assertGreater(peak_x, 800)
        self.assertLess(peak_x, 1120)
        self.assertGreater(peak_y, 300)
        self.assertLess(peak_y, 560)


if __name__ == "__main__":
    unittest.main()
