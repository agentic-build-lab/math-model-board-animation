# GitHub 发布计划

## 推荐仓库设置

- 仓库名：`math-model-board-animation`
- 可见性：先用 private。
- 后续如果要展示，再整理一个 public demo repo 或公开当前 repo。

## 为什么先 private

GitHub 支持个人 private repository，不需要公开。public repo 可以改回 private，也可以删除，但公开期间别人可能已经 fork、clone、截图或被搜索引擎缓存，所以公开不等于可完全收回。

## 建议纳入 git 的内容

- `readme.md`
- `docs/`
- `examples/`
- `schemas/`
- `scripts/`
- `packages/`
- `requirements.txt`
- `.gitignore`
- 少量最终样片可以后续用 `git add -f` 单独纳入

## 不建议纳入 git 的内容

- `work/source_materials/` 中的参考视频、抽帧和复刻素材。
- 中间诊断图、帧序列、临时分析文件。
- 大体积媒体输出。

## 后续协作方式

可以用多个 Codex 窗口/线程分别做：

- `math-model-board-animation`：数学模型板书动画。
- `ai-video-production-pipeline`：AI 素材收集、脚本、剪辑和视频生产流程。

每个方向使用独立分支或独立仓库，避免互相污染。
