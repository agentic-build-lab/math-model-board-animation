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

CREATE TABLE IF NOT EXISTS content_candidates (
    candidate_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    snapshot_text TEXT NOT NULL,
    snapshot_at TEXT NOT NULL,
    url TEXT,
    tier TEXT,
    read_status TEXT,
    category TEXT,
    composite_score REAL,
    dimension_scores_json TEXT,
    rubric_version TEXT,
    predicted_bucket TEXT,
    predicted_reason TEXT,
    risk_flags_json TEXT,
    tags_json TEXT,
    raw_json TEXT,
    inserted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_scoring_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    rubric_version TEXT NOT NULL,
    dimension_scores_json TEXT NOT NULL,
    composite_score REAL,
    scored_at TEXT NOT NULL,
    scored_by TEXT,
    note TEXT,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS video_topic_briefs (
    brief_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    target_workflow TEXT NOT NULL,
    title TEXT NOT NULL,
    hook TEXT NOT NULL,
    video_angle TEXT NOT NULL,
    evidence_needed_json TEXT NOT NULL,
    suggested_assets_json TEXT NOT NULL,
    audience_questions_json TEXT NOT NULL,
    risk_notes_json TEXT NOT NULL,
    workflow_inputs_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS content_predictions (
    prediction_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    target_workflow TEXT NOT NULL,
    prediction_basis TEXT NOT NULL,
    blind_status TEXT NOT NULL,
    predicted_bucket TEXT,
    probability_json TEXT,
    reasoning_json TEXT,
    immutable_text_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS content_observations (
    observation_id TEXT PRIMARY KEY,
    candidate_id TEXT,
    source_snapshot_id TEXT,
    observation_type TEXT NOT NULL,
    observation_text TEXT NOT NULL,
    confidence TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id),
    FOREIGN KEY (source_snapshot_id) REFERENCES content_video_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS domain_signal_links (
    link_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    link_reason TEXT,
    validation_status TEXT NOT NULL DEFAULT 'unvalidated',
    created_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES content_candidates(candidate_id)
);
