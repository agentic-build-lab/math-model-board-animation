# 项目整理摘要

## 已完成

- 将旧项目参考材料导入当前项目 `work/source_materials/quant_factor_style_mimic/`。
- 明确项目定位：从“量化公式视频”升级为“模型可视化表达能力”。
- 梳理视频生成工作流：选题、脚本切片、结构化输入、模板选择、数据生成、时间轴、渲染、审片、归档。
- 抽象 JSON/YAML 输入格式，并提供 GARCH 示例。
- 设计 4 个核心视觉模板：黑板公式风、现代科技风、教学推导风、论文解读风。
- 规划渲染脚本架构：从旧 PIL 脚本迁移到配置化 renderer。
- 规划后续 Codex skill：`math-model-board-animation`。

## 关键判断

这个项目应先做内部高质量生产工具，再考虑内容账号和产品化。自动化不是第一目标，稳定审美质量和可复用表达能力才是第一目标。

## 推荐下一步

1. 从旧脚本抽出背景、标题、坐标轴、公式和基础图表组件。
2. 做 `scripts/render_model_video.py`，先读取 `examples/garch_volatility_scene.json` 输出 3.9 秒样片。
3. 自动生成 contact sheet 和 render report。
4. 用同一架构再做一个非量化样片，验证项目不是只服务金融公式。

## 2026-07-05 样片尝试

已完成第一版最小渲染器：

- 入口：`scripts/render_model_video.py`
- 包：`packages/model_animation/`
- 输入：`examples/garch_volatility_scene.json`
- 输出视频：`outputs/renders/garch_volatility_scene/garch_volatility_scene.mp4`
- 抽帧预览：`outputs/renders/garch_volatility_scene/garch_volatility_scene_contact_sheet.jpg`
- 渲染报告：`outputs/renders/garch_volatility_scene/render_report.json`

本次样片规格：1920 x 1080，60fps，3.9 秒，234 帧。当前只支持 `blackboard_formula` 模板和 `volatility_area` 图表。
