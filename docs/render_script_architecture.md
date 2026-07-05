# 渲染脚本架构规划

## 旧项目脚本观察

已导入参考脚本：

`work/source_materials/quant_factor_style_mimic/render_quant_factor_close_study.py`

这个脚本已经证明了基础路线可行：

- PIL 逐帧绘制。
- numpy 生成曲线和散点数据。
- 全局常量控制画幅、字体、颜色、帧率。
- 每个场景一个函数。
- `render_frame(index)` 根据时间选择 scene。
- 输出 frame 序列，再用 ffmpeg 合成视频。

主要问题：

- 内容、样式和渲染逻辑混在同一个脚本。
- scene 函数无法配置化复用。
- 公式渲染依赖字体和字符串，复杂公式不够稳定。
- 缺少输入 schema、质量检查和 contact sheet 自动化接口。
- 没有清晰的数据源接口。

## 目标架构

第一阶段保持 Python 本地渲染，不急于引入复杂服务。

建议结构：

```text
scripts/
  render_model_video.py
  make_contact_sheet.py
  validate_model_video_input.py

packages/
  model_animation/
    __init__.py
    config_loader.py
    schema.py
    timing.py
    render_context.py
    fonts.py
    colors.py
    easing.py
    output_paths.py

    styles/
      blackboard_formula.py
      modern_tech.py
      teaching_derivation.py
      paper_explainer.py

    charts/
      axis.py
      curve.py
      volatility_area.py
      scatter_regression.py
      efficient_frontier.py
      regime_band.py
      neural_network.py
      matrix_heatmap.py

    scenes/
      model_scene.py
      derivation_scene.py
      paper_scene.py

    formula/
      text_formula.py
      mathtext_formula.py
      latex_formula.py

    media/
      audio_timeline.py
      subtitles.py
      ffmpeg_encode.py
      contact_sheet.py
```

## 核心模块职责

### `config_loader.py`

读取 JSON/YAML，做基本结构校验，转换成内部对象。

### `schema.py`

定义 VideoConfig、SceneConfig、FormulaConfig、AnimationConfig 等类型。第一阶段可用 dataclass；后续再考虑 Pydantic。

### `render_context.py`

集中管理画幅、fps、字体、颜色、随机种子、输出路径和当前时间。

### `styles/`

模板层。模板负责决定：

- 背景。
- 布局。
- 标题位置。
- 公式区位置。
- 坐标轴样式。
- 颜色选择。
- 安全留白。
- 默认动画节奏。

### `charts/`

图表组件层。每个图表组件只关心数据到图形的转换，不直接决定整屏布局。

### `formula/`

公式渲染层。阶段路线：

1. `text_formula`：沿用 Cambria/微软雅黑，适合短公式和样片。
2. `mathtext_formula`：用 matplotlib mathtext 输出透明 PNG，适合更标准公式。
3. `latex_formula`：后续支持 LaTeX 到 SVG/PNG，适合论文级公式。

### `media/`

输出层。负责：

- 帧序列。
- ffmpeg 合成。
- 音频对齐。
- 字幕烧录或外挂。
- contact sheet。
- 渲染日志。

## 渲染流程

1. 读取配置。
2. 校验 schema。
3. 解析模板。
4. 为每个 scene 创建 scene renderer。
5. 建立总时间轴。
6. 逐帧调用 scene renderer。
7. 写入 frame。
8. ffmpeg 编码。
9. 生成 contact sheet。
10. 输出配置快照和渲染报告。

## 质量控制接口

每次渲染后生成：

- `render_report.json`：配置、帧率、时长、字体、依赖版本。
- `contact_sheet.jpg`：抽帧预览。
- `keyframes/`：每个 scene 起点、中点、终点。
- `review_notes.md`：人工审片备注模板。

检查项：

- 文字边界是否超出安全区。
- 字幕是否遮挡公式。
- 字体文件是否缺失。
- 公式渲染是否 fallback。
- 输出时长是否匹配配置。
- 场景总时长是否匹配视频总时长。

## 依赖策略

第一阶段：

- Python 标准库。
- Pillow。
- numpy。
- ffmpeg。

谨慎增加：

- matplotlib：用于 mathtext 和部分图形计算。
- pydantic：schema 稳定后再加。
- PyYAML：需要正式支持 YAML 时再加。

暂不优先：

- Manim：适合复杂数学动画，但初始引入成本高，且当前复刻路线用 PIL 更容易精控短视频审美。
- WebGL/Three.js：等需要 3D 模型可视化时再评估。

## 从旧脚本迁移的顺序

1. 抽出颜色、字体、缓动函数。
2. 抽出背景、标题、坐标轴、公式绘制。
3. 抽出曲线、散点、面积、网络图组件。
4. 把 scene 函数改成读取 SceneConfig。
5. 加入 JSON 输入和 contact sheet 输出。
6. 再做第二个模板，验证架构不是只服务量化场景。

## 关键取舍

自动化必须服务质量。第一版 renderer 应允许人工 override：

- scene 时长。
- 公式显示方式。
- 强调点。
- 图表数据。
- 模板选择。

但不开放过多低层样式，否则会快速变成难维护的“参数地狱”。

## 2026-07-05 validation note

A lightweight built-in validator now lives at `scripts/validate_model_video_input.py`. It intentionally avoids adding `jsonschema` as a dependency in the constrained cloud environment, but checks the schema-driven enum fields that most often drift during rapid prototype work: template, quality level, chart type, formula format, animation chart mode, and highlight mode.
