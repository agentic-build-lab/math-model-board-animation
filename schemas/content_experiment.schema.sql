CREATE TABLE IF NOT EXISTS content_video_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    adapter TEXT NOT NULL,
    source_url TEXT NOT NULL,
    resolved_url TEXT,
    platform_video_id TEXT,
    fetched_at TEXT NOT NULL,
    title TEXT,
    description TEXT,
    author TEXT,
    created_at TEXT,
    duration_ms INTEGER,
    play_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    collect_count INTEGER,
    screenshot_path TEXT,
    raw_response_path TEXT,
    snapshot_json TEXT NOT NULL,
    inserted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_video_comments (
    snapshot_id TEXT NOT NULL,
    comment_id TEXT NOT NULL,
    text TEXT NOT NULL,
    like_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    user_name TEXT,
    ip_label TEXT,
    inserted_at TEXT NOT NULL,
    PRIMARY KEY (snapshot_id, comment_id, text),
    FOREIGN KEY (snapshot_id) REFERENCES content_video_snapshots(snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_content_video_snapshots_platform_id
ON content_video_snapshots(platform, platform_video_id);

CREATE INDEX IF NOT EXISTS idx_content_video_comments_likes
ON content_video_comments(snapshot_id, like_count DESC);
