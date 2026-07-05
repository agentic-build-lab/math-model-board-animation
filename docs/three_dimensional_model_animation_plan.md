# 3D / 伪 3D 模型动画计划

## 可行路线

1. 旋转曲面：用 numpy 生成网格，PIL 做等距投影或后续接 matplotlib/Blender；适合损失函数、概率密度、效用曲面。
2. 立体公式：公式保持 2D 可读，叠加轻微阴影、深度偏移和镜面高光，不做真实透视扭曲。
3. 粒子点云：用 3D 坐标投影到 2D，深度控制大小和透明度；适合 embedding、聚类、状态空间。
4. 模型结构图：Transformer、神经网络、因子图可用分层节点 + 边流动 + Z 轴错层伪 3D。
5. 动态 3D 视频：复杂场景再接 Blender 或 Manim，PIL 渲染器只保留轻量原型。

## 质量约束

- 3D 不能牺牲公式可读性。
- 镜头运动要慢，避免眩晕。
- 点云和曲面必须有明确主体，不做廉价科技背景。
- 3D 原型应作为单独样片，不影响 GARCH 主线稳定。

## 低成本 prototype 建议

先做 `rotating_surface` chart_type：30x30 网格、等距投影、青绿色网格线、金色最优点；输出 3 秒 contact sheet 后再决定是否投入真实 3D 管线。

## 2026-07-05 prototype 进展

已新增最小 `rotating_surface` chart prototype：用 numpy 网格生成光滑曲面，PIL 做等距投影，使用青绿色网格和金色关注点。该 prototype 目标只是验证 3D 方向的视觉潜力，不替代未来 Blender/Manim 管线。

示例配置：`examples/loss_surface_scene.json`。
