from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "model_video.schema.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight validation for model video JSON configs.")
    parser.add_argument("configs", nargs="+", type=Path, help="Config JSON files to validate.")
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failed = False
    for config_path in args.configs:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            validate_config(config, schema)
        except Exception as exc:  # noqa: BLE001 - command-line validator should print all user-facing errors.
            failed = True
            print(f"FAIL {config_path}: {exc}")
        else:
            print(f"OK   {config_path}")
    if failed:
        sys.exit(1)


def validate_config(config: dict[str, Any], schema: dict[str, Any]) -> None:
    require_keys(config, ["project", "video", "style", "scenes"], "root")
    if not isinstance(config["scenes"], list) or not config["scenes"]:
        raise ValueError("root.scenes must be a non-empty list")

    style_quality = config["style"].get("quality")
    if style_quality is not None:
        assert_enum(style_quality, schema["properties"]["style"]["properties"]["quality"]["enum"], "style.quality")
    assert_enum(config["style"].get("template"), schema["properties"]["style"]["properties"]["template"]["enum"], "style.template")

    for index, scene in enumerate(config["scenes"]):
        path = f"scenes[{index}]"
        require_keys(scene, ["id", "title", "duration", "formula", "chart_type", "animation"], path)
        assert_enum(scene["chart_type"], schema["$defs"]["scene"]["properties"]["chart_type"]["enum"], f"{path}.chart_type")
        require_keys(scene["formula"], ["format", "text"], f"{path}.formula")
        assert_enum(scene["formula"]["format"], schema["$defs"]["formula"]["properties"]["format"]["enum"], f"{path}.formula.format")
        animation = scene["animation"]
        require_keys(animation, ["title", "formula", "chart"], f"{path}.animation")
        animation_schema = schema["$defs"]["animation"]["properties"]
        assert_enum(animation["title"], animation_schema["title"]["enum"], f"{path}.animation.title")
        assert_enum(animation["formula"], animation_schema["formula"]["enum"], f"{path}.animation.formula")
        assert_enum(animation["chart"], animation_schema["chart"]["enum"], f"{path}.animation.chart")
        if "highlight" in animation:
            assert_enum(animation["highlight"], animation_schema["highlight"]["enum"], f"{path}.animation.highlight")


def require_keys(value: dict[str, Any], keys: list[str], path: str) -> None:
    missing = [key for key in keys if key not in value]
    if missing:
        raise ValueError(f"{path} missing required keys: {', '.join(missing)}")


def assert_enum(value: Any, allowed: list[str], path: str) -> None:
    if value not in allowed:
        raise ValueError(f"{path}={value!r} is not one of {allowed}")


if __name__ == "__main__":
    main()
