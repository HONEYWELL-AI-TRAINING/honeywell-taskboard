-- Migration 002 — add soft-delete state to tasks.
-- NULL means the task is active; a timestamp means it has been deleted.

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
