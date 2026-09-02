# API Contract: Task Comments

Base path: `/api/tasks/{task_id}/comments` (nested under an existing task,
mirroring `.../tasks/{task_id}` conventions already in `routers/tasks.py`).
This contract is authoritative for the Python backend and is written so it
can be ported byte-for-byte to `.NET`/Java in Lab 03 (Cross-Backend Parity).

## `GET /api/tasks/{task_id}/comments`

- **Purpose**: List all comments for a task, oldest-first.
- **Success**: `200 OK`, body: `list[CommentRead]` (empty list `[]` if the
  task exists but has no comments — not a 404).
- **Errors**: `404` if `task_id` does not reference an existing task.

`CommentRead`:
```json
{
  "id": 1,
  "task_id": 42,
  "author": "Priya",
  "text": "Should we split this into two tasks?",
  "created_at": "2026-09-02T10:15:00"
}
```

## `GET /api/tasks/{task_id}/comments/count`

- **Purpose**: Lightweight count for the board's comment-count badge,
  without fetching comment bodies. Declared before the (nonexistent) path
  param route to avoid ambiguity, mirroring the existing
  `/api/tasks/count` vs `/api/tasks/{task_id}` ordering.
- **Success**: `200 OK`, body: `CommentCount`.
- **Errors**: `404` if `task_id` does not reference an existing task.

`CommentCount`:
```json
{ "count": 3 }
```

## `POST /api/tasks/{task_id}/comments`

- **Purpose**: Post a new comment to a task.
- **Request body** (`CommentCreate`):
  ```json
  { "author": "Priya", "text": "Should we split this into two tasks?" }
  ```
- **Success**: `201 Created`, body: the created `CommentRead` (not the
  whole thread).
- **Errors**:
  - `404` if `task_id` does not reference an existing task.
  - `422` if `author` is missing/empty, or > 100 characters.
  - `422` if `text` is missing, empty, whitespace-only, or > 500
    characters.

## `DELETE /api/tasks/{task_id}/comments/{comment_id}`

- **Purpose**: Delete a single comment.
- **Success**: `204 No Content`.
- **Errors**:
  - `404` if `task_id` does not reference an existing task.
  - `404` if `comment_id` does not reference an existing comment under
    that task.

## Cross-cutting

- No new status codes beyond the existing `404` / `422` contract
  (constitution III).
- No authentication/authorization — any caller may post or delete any
  comment (spec: no auth exists in this app).
- Deleting a task (existing `DELETE /api/tasks/{task_id}`) cascades to
  delete its comments; no separate client call is required or expected.
