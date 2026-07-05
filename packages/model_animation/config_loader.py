from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a model video config is missing required structure."""


def load_video_config(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise ConfigError("第一版渲染器先支持 JSON；YAML 会在 schema 稳定后接入。")

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    _require_object(config, "root")
    for key in ("project", "video", "style", "scenes"):
        if key not in config:
            raise ConfigError(f"配置缺少必填字段：{key}")

    scenes = config["scenes"]
    if not isinstance(scenes, list) or not scenes:
        raise ConfigError("配置字段 scenes 必须是非空数组。")

    for index, scene in enumerate(scenes):
        _require_object(scene, f"scenes[{index}]")
        for key in ("id", "title", "duration", "formula", "chart_type", "animation"):
            if key not in scene:
                raise ConfigError(f"scenes[{index}] 缺少必填字段：{key}")

    return config


def _require_object(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} 必须是 JSON object。")
