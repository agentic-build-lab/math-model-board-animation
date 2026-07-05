# SQL Schema 方案草案

```sql
CREATE TABLE projects (id TEXT PRIMARY KEY, title TEXT NOT NULL, domain TEXT, created_at TEXT NOT NULL);
CREATE TABLE scene_configs (id TEXT PRIMARY KEY, project_id TEXT REFERENCES projects(id), slug TEXT NOT NULL, config_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE render_runs (id TEXT PRIMARY KEY, scene_config_id TEXT REFERENCES scene_configs(id), version TEXT NOT NULL, command TEXT, width INTEGER, height INTEGER, fps INTEGER, duration REAL, status TEXT, report_path TEXT, created_at TEXT NOT NULL);
CREATE TABLE visual_versions (id TEXT PRIMARY KEY, render_run_id TEXT REFERENCES render_runs(id), route TEXT, summary TEXT, video_path TEXT, contact_sheet_path TEXT, git_commit TEXT);
CREATE TABLE assets (id TEXT PRIMARY KEY, project_id TEXT REFERENCES projects(id), kind TEXT, path TEXT NOT NULL, sha256 TEXT, license_note TEXT);
CREATE TABLE quality_reviews (id TEXT PRIMARY KEY, visual_version_id TEXT REFERENCES visual_versions(id), reviewer TEXT, score INTEGER, decision TEXT, notes TEXT, created_at TEXT NOT NULL);
CREATE TABLE parameters (id TEXT PRIMARY KEY, render_run_id TEXT REFERENCES render_runs(id), name TEXT NOT NULL, value TEXT NOT NULL, unit TEXT);
CREATE TABLE decision_logs (id TEXT PRIMARY KEY, project_id TEXT REFERENCES projects(id), decision TEXT NOT NULL, reason TEXT, alternatives TEXT, created_at TEXT NOT NULL);
```

## 设计原则

- `scene_configs` 保存完整配置快照，保证可重放。
- `render_runs` 记录一次执行事实和环境状态。
- `visual_versions` 记录审美版本，不等同于每次命令运行。
- `quality_reviews` 允许人工审片 gate。
- `parameters` 便于横向比较线宽、透明度、seed、节奏等。
- `decision_logs` 记录为什么保留或放弃某条路线。
