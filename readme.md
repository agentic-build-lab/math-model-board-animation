# 数学模型板书动画项目

这个项目用于沉淀一套高质量的“模型可视化表达能力”：用板书式动画解释数学公式、量化因子、统计模型、物理模型、AI 模型、经济学模型和论文模型。

它不是单纯的“量化公式视频”项目，而是一个可复用的视频高级组件方向。短期目标是内部可用的高质量生产工具；中期可以作为内容账号方向持续生产；如果市场验证成立，再进一步产品化给老师、知识博主、金融培训、AI 课程、论文解读和企业培训使用。

## 当前阶段

当前阶段先做工作流和视觉规范，不急于全自动化。已有复刻材料说明：黑底弱颗粒、顶部章节标题、主体图形生长、底部公式/字幕区这套结构有较强复用价值，但也暴露出一个关键原则：生成系统必须保留人工审美决策空间，不能只靠配置文件机械排版。

## 项目结构

- `docs/project_positioning.md`：产品/内容定位。
- `docs/video_generation_workflow.md`：视频生成工作流。
- `docs/input_format_spec.md`：JSON/YAML 输入格式抽象。
- `docs/visual_templates.md`：四类核心视觉模板。
- `docs/render_script_architecture.md`：渲染脚本架构规划。
- `docs/codex_skill_plan.md`：后续整理成 Codex skill 的计划。
- `docs/source_materials_inventory.md`：旧项目材料导入记录。
- `schemas/model_video.schema.json`：模型视频输入 schema 草案。
- `examples/garch_volatility_scene.json`：GARCH 场景 JSON 示例。
- `examples/garch_volatility_scene.yaml`：GARCH 场景 YAML 示例。
- `work/source_materials/quant_factor_style_mimic/`：从旧项目导入的参考材料。
- `outputs/project_setup_summary.md`：本次项目整理摘要。

## 近期目标

1. 基于已有 PIL 逐帧渲染脚本抽象出稳定的场景、图表、公式、时间轴和风格模块。
2. 先支持 4 个高质量模板：黑板公式风、现代科技风、教学推导风、论文解读风。
3. 每个模板先做 2-3 条人工审美认可的样片，再考虑固化为 `math-model-board-animation` Codex skill。
4. 渲染系统默认启用人工 review gate，内部生产稳定后再提高自动化程度。

## 当前可运行样片

第一版渲染入口：

```powershell
python scripts\render_model_video.py --config examples\garch_volatility_scene.json
```

输出位置：

- `outputs/renders/garch_volatility_scene/garch_volatility_scene.mp4`
- `outputs/renders/garch_volatility_scene/garch_volatility_scene_contact_sheet.jpg`
- `outputs/renders/garch_volatility_scene/render_report.json`

当前能力范围：`blackboard_formula` 模板 + `volatility_area` 图表。后续再扩展到更多 chart_type 和模板。

## Content Experiment Engine

This repository also contains a reusable content experiment module under
`packages/content_experiment_engine`. It can capture public video snapshots,
normalize topic candidates, score them with a starter rubric, generate workflow
briefs, and write queryable experiment data to SQLite.

See:

- `docs/content_experiment_module.md`
- `docs/cheat_on_content_upstream_audit.md`
- `docs/content_experiment_engine_integration_plan.md`
