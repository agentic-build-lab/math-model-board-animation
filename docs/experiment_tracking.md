# 实验记录与输出版本约定

## 输出目录

每次渲染必须写入唯一目录：

```text
outputs/renders/<scene_id>/<version>_<config_slug>/
```

示例：

```text
outputs/renders/garch_volatility_memory/v20260705T045000Z_garch_volatility_scene/
```

目录内应包含：

- `<slug>_<version>.mp4`：最终视频。
- `<slug>_<version>_contact_sheet.jpg`：审片接触表。
- `render_report.json`：环境、规格、耗时、输出路径、错误信息。
- `config_snapshot.json`：本次使用的配置快照。
- `changes.md`：本次参数变化、视觉判断和下一步建议。

全局追加索引：`outputs/renders/manifest.jsonl`。旧版本不得覆盖或删除。

## 每次实验最少记录

1. 渲染命令。
2. git commit 或工作区状态。
3. 视频规格：尺寸、fps、时长、帧数。
4. 参数变化：曲线、填充、发光、布局、字幕、数据 seed。
5. 视觉判断：成功点、失败点、是否适合展示版/教学版。
6. 下一步：保留、微调、废弃或作为对照。

## 当前云端阻塞记录

2026-07-05 UTC：默认渲染已生成逐帧 JPG，但环境缺少 `ffmpeg`，apt/pip 均被代理 403 阻断，无法在本轮生成真实 mp4。后续云端托管必须预装 ffmpeg 或提供可用 Python 视频编码依赖。

## 自动生成的 review gate

渲染脚本现在会在每个版本目录写入 `review_notes.md`，用于人工审片。`render_report.json` 的 `environment.ffmpeg_available` 与 `encode_status` 是发布前硬门槛：如果编码失败，contact sheet 只能用于构图初审，不能视为完整样片。

## 2026-07-05 continuation audit: 3D/factor surface milestone

- Branch: `work`.
- Local HEAD before this milestone: `bf6cc38 Add loss surface showcase sample`.
- Working tree at audit start: clean.
- Remote: `origin=https://github.com/agentic-build-lab/math-model-board-animation.git` is configured, but `git push origin HEAD:codex-ko4uhm` fails with `CONNECT tunnel failed, response 403`.
- `gh` CLI is unavailable in this worker; no usable GitHub token is exposed.
- Decision: continue producing reproducible configs, recipes, previews, reports and manifests locally; remote PR sync requires platform/user network credentials.
- Current local mp4 blocker remains missing `ffmpeg`; WebP/HTML/contact sheet are valid draft review artifacts only.
