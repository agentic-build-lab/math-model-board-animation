# 输入格式抽象

## 设计目标

输入格式描述内容意图，不描述低层像素。原因是这个项目优先保证画面审美，不能让用户或自动生成器把字体、位置、颜色、透明度、线宽全都随意填坏。

配置文件应该回答：

- 这条视频讲什么模型？
- 每个 scene 讲哪个点？
- 公式是什么？
- 图表是什么类型？
- 哪些变量或区域需要强调？
- 动画节奏大概多长？
- 旁白/字幕如何绑定？

模板和 renderer 负责：

- 布局。
- 字体。
- 留白。
- 坐标轴样式。
- 颜色克制。
- 动画缓动。
- 可读性保护。

## 顶层结构

推荐字段：

- `project`：项目和主题信息。
- `video`：画幅、帧率、总时长、语言和输出规格。
- `style`：视觉模板和风格覆盖项。
- `narration`：旁白、字幕和时间轴策略。
- `scenes`：逐场景内容。
- `quality`：人工 review 和质量门槛。

## scene 核心字段

- `id`：稳定场景 ID。
- `title`：章节标题。
- `subtitle`：一行解释。
- `domain`：模型领域，例如 `quant_finance`、`statistics`、`physics`、`machine_learning`。
- `duration`：场景时长，单位秒。
- `formula`：公式内容，支持 unicode、LaTeX 或 plain text。
- `explanation`：该场景要表达的直觉。
- `chart_type`：图表类型。
- `data_source`：数据来源。
- `animation`：动画策略。
- `emphasis`：强调点。
- `captions`：字幕或旁白片段。

## 推荐 chart_type

- `curve`：普通曲线。
- `multi_curve`：多条曲线。
- `volatility_area`：波动率/面积图。
- `scatter_regression`：散点和拟合线。
- `efficient_frontier`：有效前沿。
- `regime_band`：状态分区。
- `neural_network`：神经网络结构。
- `matrix_heatmap`：矩阵/相关性热图。
- `equation_derivation`：公式推导。
- `phase_space`：相图/状态空间。
- `causal_diagram`：因果图/结构方程。

## 推荐 animation

- `title`: `fade_in`、`slide_fade`。
- `formula`: `fade_in`、`write_on`、`step_reveal`。
- `chart`: `draw_curve`、`fade_points`、`grow_area`、`build_network`、`reveal_matrix`。
- `highlight`: `pulse_peak`、`box_region`、`trace_path`、`spotlight_variable`。

## JSON 示例

```json
{
  "project": {
    "title": "GARCH 波动率模型",
    "domain": "quant_finance",
    "audience": "有基础金融知识的短视频观众"
  },
  "video": {
    "aspect_ratio": "16:9",
    "width": 1920,
    "height": 1080,
    "fps": 60,
    "language": "zh-CN"
  },
  "style": {
    "template": "blackboard_formula",
    "palette": "black_teal_red",
    "quality": "publish_review"
  },
  "narration": {
    "mode": "caption_first",
    "subtitle_position": "bottom_safe_area"
  },
  "scenes": [
    {
      "id": "garch_volatility_memory",
      "title": "4. GARCH 波动率模型",
      "subtitle": "捕捉金融市场波动率的记忆性与聚集性",
      "duration": 3.9,
      "formula": {
        "format": "unicode",
        "text": "σₜ² = α₀ + α₁ε²ₜ₋₁ + β₁σ²ₜ₋₁"
      },
      "explanation": "波动率不是随机乱跳，它会在冲击之后持续一段时间。",
      "chart_type": "volatility_area",
      "data_source": {
        "type": "synthetic",
        "shape": "clustered_volatility"
      },
      "animation": {
        "title": "fade_in",
        "formula": "fade_in",
        "chart": "grow_area",
        "highlight": "pulse_peak"
      },
      "emphasis": [
        {
          "target": "volatility_peak",
          "label": "冲击后波动聚集",
          "time": [2.4, 3.4]
        }
      ],
      "captions": [
        {
          "text": "市场的剧烈波动，往往会留下记忆。",
          "time": [0.0, 2.0]
        },
        {
          "text": "GARCH 用上一期冲击和上一期波动率，解释这一期风险。",
          "time": [2.0, 3.9]
        }
      ]
    }
  ],
  "quality": {
    "manual_review_required": true,
    "generate_contact_sheet": true,
    "formula_check_required": true
  }
}
```

## YAML 示例

```yaml
project:
  title: GARCH 波动率模型
  domain: quant_finance
  audience: 有基础金融知识的短视频观众

video:
  aspect_ratio: "16:9"
  width: 1920
  height: 1080
  fps: 60
  language: zh-CN

style:
  template: blackboard_formula
  palette: black_teal_red
  quality: publish_review

narration:
  mode: caption_first
  subtitle_position: bottom_safe_area

scenes:
  - id: garch_volatility_memory
    title: 4. GARCH 波动率模型
    subtitle: 捕捉金融市场波动率的记忆性与聚集性
    duration: 3.9
    formula:
      format: unicode
      text: σₜ² = α₀ + α₁ε²ₜ₋₁ + β₁σ²ₜ₋₁
    explanation: 波动率不是随机乱跳，它会在冲击之后持续一段时间。
    chart_type: volatility_area
    data_source:
      type: synthetic
      shape: clustered_volatility
    animation:
      title: fade_in
      formula: fade_in
      chart: grow_area
      highlight: pulse_peak
    emphasis:
      - target: volatility_peak
        label: 冲击后波动聚集
        time: [2.4, 3.4]
    captions:
      - text: 市场的剧烈波动，往往会留下记忆。
        time: [0.0, 2.0]
      - text: GARCH 用上一期冲击和上一期波动率，解释这一期风险。
        time: [2.0, 3.9]

quality:
  manual_review_required: true
  generate_contact_sheet: true
  formula_check_required: true
```

## 配置边界

允许配置：

- 内容。
- 公式。
- 图表类型。
- 数据来源。
- 时长。
- 强调点。
- 字幕。
- 模板选择。

不建议直接配置：

- 任意像素坐标。
- 任意颜色值。
- 任意字体。
- 任意线宽。
- 任意透明度。
- 每个元素的绝对位置。

这些底层样式应该由模板提供少量安全的 override，而不是开放成无限参数。
