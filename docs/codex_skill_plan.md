# Codex skill 规划：math-model-board-animation

## 是否应该做成 skill

应该做，但不要现在立刻做成全局 skill。当前阶段先把工作流、输入格式、模板和渲染脚本沉淀在项目里，等连续 2-3 个样片达到稳定质量后，再整理成 skill。

原因：

- skill 适合固化稳定方法，不适合承载还在快速变化的审美实验。
- 现在最重要的是确定模板质量边界。
- 过早 skill 化会让流程看似自动，实际画面质量不可控。

## 触发场景

未来 skill 触发条件：

- 用户要求制作数学公式动画。
- 用户要求量化因子/统计模型/AI 模型可视化视频。
- 用户要求论文模型讲解动画。
- 用户提供公式、图表数据、课程讲稿，希望生成板书式视频。

## skill 能力范围

应该覆盖：

- 读取模型视频配置。
- 生成或完善 scene JSON/YAML。
- 选择视觉模板。
- 规划时间轴。
- 调用渲染脚本。
- 生成 contact sheet。
- 输出审片清单。
- 根据审片意见迭代配置。

不应该覆盖：

- 直接发布到平台。
- 跳过人工 review。
- 自动保证复杂公式的数学正确性。
- 未授权复刻具体账号包装。

## skill 输入

最小输入：

- 模型名称。
- 公式。
- 解释目标。
- 视频时长。
- 目标模板。

增强输入：

- 旁白稿。
- CSV 数据。
- 参考论文。
- 品牌色。
- 平台规格。
- 目标受众。

## skill 输出

每次执行应输出：

- `model_video_config.json`。
- `rendered_video.mp4`。
- `contact_sheet.jpg`。
- `render_report.json`。
- `review_notes.md`。

## SKILL.md 草案结构

```text
# math-model-board-animation

Use when the user asks to create high-quality board-style animations for mathematical models, formulas, quantitative factors, statistical models, physics models, AI models, economics models, or paper model explanations.

Workflow:
1. Clarify model, audience, duration, and template.
2. Create or update structured JSON/YAML input.
3. Choose a visual template.
4. Render a draft video.
5. Generate a contact sheet.
6. Review formula correctness, readability, layout, and motion rhythm.
7. Iterate until the output is publishable.

Quality rule:
Do not sacrifice visual quality for automation. Always preserve a manual review gate before final delivery.
```

## 打包前验收标准

- 黑板公式风至少 3 条稳定样片。
- 教学推导风至少 2 条稳定样片。
- 输入 schema 覆盖常见字段。
- 渲染脚本能从配置文件产出视频。
- contact sheet 自动生成。
- 公式校对和审片清单稳定。
- skill 文档能指导 Codex 不从零开始。

## 推荐时间点

在以下条件满足后创建 skill：

1. `scripts/render_model_video.py` 可以读取 JSON 并输出视频。
2. 至少两个模板跑通。
3. 项目内已有 5 条以上样片记录。
4. 审片意见主要集中在内容，而不是基础视觉崩坏。
