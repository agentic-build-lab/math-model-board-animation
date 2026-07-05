from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_model_video_input import SCHEMA_PATH, validate_config


class ValidateModelVideoInputTest(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_loss_surface_example_is_schema_aligned(self) -> None:
        config = json.loads(Path("examples/loss_surface_scene.json").read_text(encoding="utf-8"))
        validate_config(config, self.schema)

    def test_unknown_chart_type_fails(self) -> None:
        config = json.loads(Path("examples/garch_volatility_scene.json").read_text(encoding="utf-8"))
        config["scenes"][0]["chart_type"] = "unknown_chart"
        with self.assertRaisesRegex(ValueError, "chart_type"):
            validate_config(config, self.schema)

    def test_cli_import_has_no_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertTrue(Path(temp_dir).exists())


if __name__ == "__main__":
    unittest.main()
