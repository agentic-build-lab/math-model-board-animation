# 源材料导入记录

## 来源

旧项目路径：

`<local-user>\Documents\New project 6`

当前项目导入路径：

`work/source_materials/quant_factor_style_mimic/`

## 已导入文件

| 文件 | 用途 |
| --- | --- |
| `math_model_board_animation_workflow.md` | 旧项目工作流文档 |
| `quant_factor_douyin_style_notes.md` | 抖音参考风格拆解记录 |
| `render_quant_factor_close_study.py` | 近似复刻渲染脚本 |
| `quant_factor_close_style_study.mp4` | 近似复刻成片 |
| `quant_factor_close_style_contact_sheet.jpg` | 近似复刻预览图 |
| `reference_quant_video.mp4` | 参考视频 |
| `reference_contact_sheet.jpg` | 参考视频抽帧预览 |

## 媒体元数据

### 近似复刻成片

- 文件：`quant_factor_close_style_study.mp4`
- 编码：H.264 + AAC
- 尺寸：1920 x 1080
- 帧率：60 fps
- 时长：43.000 秒
- 大小：1,227,999 bytes
- SHA256：`B2F0CB02CE0495CD0198432D73BD5C579D1C238CF67BE305E12FE3967BFBEDA7`

### 参考视频

- 文件：`reference_quant_video.mp4`
- 编码：HEVC + AAC
- 尺寸：3840 x 2160
- 帧率：60 fps
- 时长：43.419 秒
- 大小：2,667,398 bytes
- SHA256：`1447DAC80B140A1AE720E053710ADE3316B51CFD502418B5A91CF46231D7DA44`

## 已确认的可复用经验

- 43 秒左右的横屏 60fps 节奏适合 10 个模型快速闪讲。
- 黑底弱颗粒比强网格更高级，也更利于公式和曲线可读性。
- 顶部标题、中部图形、底部公式的结构稳定。
- 坐标轴保留箭头和短刻度即可，不需要复杂网格。
- 曲线生长、散点渐入、区域渐显是最可复用的动效。
- 公式逐字出现适合复刻风格，但模型闪讲里可改为更快的整体淡入。
- GARCH 这类面积图必须控制填充透明度，边界线要更清楚。

## 需要避免的风险

- 不复制参考账号的头像、水印、固定包装和专属文案。
- 不把复刻风格误认为唯一风格。
- 不让“量化金融”限制项目边界。
- 不为了批量生成牺牲字体、留白、颜色和公式清晰度。
