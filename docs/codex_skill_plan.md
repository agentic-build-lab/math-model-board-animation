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

## 2026-07-05 本轮沉淀

### 成功参数

- GARCH 面积图垂直映射使用 10%-86% 区间，比贴顶曲线更舒服。
- 面积填充建议 `alpha_low=42`、`alpha_high=108`，保持红色存在感但避免廉价大红块。
- 主曲线 4 px + 低透明度外发光，比 3 px 强光更清晰且更高级。
- 第二样片 CAPM 使用散点先出现、拟合线后生长，验证模板不只适用于 GARCH。

### 弯路和环境限制

- 云端镜像缺少 Windows 中文字体时必须有 Linux/DejaVu fallback，否则默认渲染会在加载字体时失败。
- 云端镜像缺少 `ffmpeg` 时无法生成真实 mp4；apt/pip 在本轮被代理 403 阻断。未来 skill 的环境检查必须把 `ffmpeg -version` 作为硬门槛。
- contact sheet 也不能依赖 Windows 字体路径。

### 质量检查清单补充

- 渲染前：检查字体、ffmpeg、numpy、PIL。
- 渲染后：检查 `render_report.json` 的 `encode_status` 必须为 `success` 才能发布。
- 审片：同时看 mp4 和 contact sheet；如果只有 contact sheet，只能做构图初审，不能确认运动节奏。
- 归档：每次输出必须有 version、config snapshot、changes、manifest 记录。

## 2026-07-05 cloud continuation素材

### 输入输出约定

- 输入：JSON/YAML config，必须先通过 `scripts/validate_model_video_input.py`。
- 输出：versioned render directory with `config_snapshot.json`, `changes.md`, `review_notes.md`, `render_report.json`, contact sheet, optional `preview.webp`, optional `preview.html`, and mp4 when `ffmpeg` exists.
- Manifest：append-only `outputs/renders/manifest.jsonl`; 不覆盖旧版本。

### fallback 策略

- 没有 `ffmpeg`：继续生成 frames、contact sheet、report、review notes、config snapshot、manifest、WebP/HTML draft preview；不得假装 mp4 成功。
- 没有 CJK 字体：允许流程验证，但最终中文样片必须安装 Noto CJK 或授权品牌字体。
- 网络代理阻塞：使用 devcontainer / GitHub Actions 声明依赖，或改用预构建 runner image。

### 视觉基线补充

- GARCH：浅红填充、明亮细轮廓、峰值有空间余量。
- CAPM：点云透明但不虚，拟合线为视觉主线，字幕解释 beta。
- Loss surface：网格应服务曲面结构，不做廉价 HUD；金色控制点是唯一强强调。
