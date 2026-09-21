-- migrations/001_init.sql
-- Canonical structured state (PostgreSQL dialect; SQLite tests use compatible subset)

CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    event_type      TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    workspace_id    TEXT NOT NULL,
    goal_id         TEXT,
    task_id         TEXT,
    org_unit_id     TEXT,
    principal_id    TEXT,
    occurred_at     TEXT NOT NULL,
    recorded_at     TEXT NOT NULL,
    payload         TEXT NOT NULL,
    causation_id    TEXT,
    correlation_id  TEXT,
    producer        TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    seq             INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_events_seq ON events(seq);
CREATE INDEX IF NOT EXISTS ix_events_goal ON events(goal_id);

CREATE TABLE IF NOT EXISTS goals (
    goal_id         TEXT NOT NULL,
    version         INTEGER NOT NULL,
    tenant_id       TEXT NOT NULL,
    workspace_id    TEXT NOT NULL,
    body            TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    PRIMARY KEY (goal_id, version)
);

CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    run_id          TEXT NOT NULL,
    step_index      INTEGER NOT NULL,
    step_name       TEXT NOT NULL,
    state_json      TEXT NOT NULL,
    status          TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    PRIMARY KEY (run_id, step_index)
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id     TEXT PRIMARY KEY,
    approver        TEXT NOT NULL,
    action_hash     TEXT NOT NULL,
    goal_id         TEXT NOT NULL,
    limits_json     TEXT NOT NULL,
    valid_until     TEXT NOT NULL,
    one_time        INTEGER NOT NULL,
    consumed        INTEGER NOT NULL DEFAULT 0,
    signature       TEXT NOT NULL
);
