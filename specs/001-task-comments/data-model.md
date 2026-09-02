# Phase 1 Data Model: Task Comments

## Entity: Comment

Maps to the new `task_comments` table (owned solely by
`database/schema.sql`, per Single Schema Owner).

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | integer | PK, auto-increment | Mirrors `tasks.id` pattern (`SERIAL PRIMARY KEY`) |
| `task_id` | integer | NOT NULL, FK → `tasks.id`, `ON DELETE CASCADE` | Deleting a task deletes its comments (FR-008) |
| `author` | varchar(100) | NOT NULL, length 1–100 | Whitespace-only accepted (spec Clarifications); empty/missing rejected |
| `text` | varchar(500) | NOT NULL, length 1–500, not whitespace-only | Rejected if blank or all-whitespace (FR-005) |
| `created_at` | timestamp | NOT NULL, `DEFAULT NOW()` | Set by the database only, never by app code (constitution II) |

No `updated_at` — comments are immutable once posted (no editing, per
spec Key Entities); there is nothing to update.

### Relationships

- `Comment` belongs to exactly one `Task` (many-to-one, `task_id` FK).
- `Task` deletion cascades to delete all its `Comment` rows (DB-level
  `ON DELETE CASCADE`, not application code — see research.md).

### Validation rules (enforced in the Service/Schema layer, not the DB)

- `author`: required, 1–100 characters. Whitespace-only strings are valid
  (not trimmed, not rejected).
- `text`: required, 1–500 characters, and must contain at least one
  non-whitespace character (whitespace-only is rejected as if missing).
- `task_id` must reference an existing task, or the operation is rejected
  with 404 (`TaskNotFound`), not 422 — this is a missing-resource
  condition, not a malformed-body condition.
- A comment `id` that does not exist under the given task is rejected with
  404 (`CommentNotFound`) on delete.

### State transitions

None. A comment is created, optionally read, and eventually deleted (either
directly, or implicitly via its parent task's deletion). There is no
in-between state and no edit operation.

## Proposed `database/schema.sql` addition

```sql
CREATE TABLE IF NOT EXISTS task_comments (
    id          SERIAL PRIMARY KEY,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    author      VARCHAR(100) NOT NULL,
    text        VARCHAR(500) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_comments_task_id ON task_comments (task_id);
```

Notes:
- Index on `task_id` supports the two hot-path queries: listing a task's
  comments and counting them.
- No `updated_at` / trigger — comments are immutable, unlike `tasks`.
- Column length limits are a backstop; primary enforcement is in the
  Pydantic schema (see research.md), consistent with how `tasks.title` /
  `tasks.assignee` are handled today.
