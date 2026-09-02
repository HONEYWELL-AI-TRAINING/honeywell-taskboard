# Phase 0 Research: Task Comments

All items below were resolved from the existing codebase (no external
research needed — this feature reuses established patterns) or from the
spec's Clarifications/Assumptions. No `NEEDS CLARIFICATION` markers remain.

## Decision: Comment ownership & cascade delete

- **Decision**: `task_comments.task_id` is a foreign key to `tasks.id` with
  `ON DELETE CASCADE`.
- **Rationale**: Spec FR-008 requires deleting a task to delete its
  comments. Doing this at the database level (rather than in application
  code) guarantees it holds even if a comment is deleted out-of-band, and
  matches "Single Schema Owner" — the constraint lives once, in
  `database/schema.sql`, not duplicated as app-level cleanup logic in three
  backends.
- **Alternatives considered**: Application-level cascade (service deletes
  comments before deleting the task) — rejected because it would need to be
  reimplemented identically in `.NET` and Java (Lab 03) and is one more way
  for parity to drift; the DB constraint is enforced once for all three.

## Decision: Comment ordering

- **Decision**: Comments are returned oldest-first (`ORDER BY id` /
  `ORDER BY created_at`), matching thread display order exactly.
- **Rationale**: Spec Assumptions state the API returns oldest-first with
  no client re-sort needed; matches the existing `TaskRepository.list`
  pattern of ordering by `id` in the repository layer.
- **Alternatives considered**: Newest-first with client-side reverse —
  rejected, adds unnecessary frontend logic for no benefit.

## Decision: Length limits enforced in the Pydantic schema, not the DB CHECK

- **Decision**: `author` capped at 100 chars, `text` capped at 500 chars,
  enforced via Pydantic `Field(min_length=1, max_length=...)` in
  `schemas/comment.py`, mirroring `TaskBase.assignee` /
  `TaskBase.title` limits already in `schemas/task.py`. The database
  columns are sized generously (`VARCHAR(100)` / `VARCHAR(500)`) as a
  backstop, not the primary enforcement point.
- **Rationale**: Existing task schema already validates length in Pydantic
  (e.g. `title: str = Field(min_length=1, max_length=255)`), and the
  Service layer is where "business rules" live per the constitution — HTTP
  422s are naturally produced by Pydantic validation errors already
  surfaced as 422 by FastAPI's default handler, consistent with existing
  behavior (see `test_create_task_requires_title`).
- **Alternatives considered**: DB-only `CHECK (length(text) <= 500)` —
  rejected as the sole mechanism because it would surface as a raw DB
  error rather than a clean 422 without extra service-layer catching;
  keeping it in Pydantic matches the existing task pattern exactly.

## Decision: Whitespace-only validation

- **Decision**: `text` is rejected if empty or whitespace-only (via a
  Pydantic validator, since `min_length=1` alone does not catch
  `"   "`). `author` is rejected only if empty/missing — whitespace-only
  author values are accepted as-is, per spec Clarifications.
- **Rationale**: Directly encodes the two clarified answers from
  `spec.md`.
- **Alternatives considered**: Trimming/stripping author server-side —
  rejected; spec clarification explicitly says no extra validation beyond
  presence for author.

## Decision: Response body shape for POST

- **Decision**: `POST /api/tasks/{task_id}/comments` returns the newly
  created `CommentRead` object (not the whole thread), with `201 Created`,
  mirroring `POST /api/tasks` today.
- **Rationale**: Spec Assumptions state this explicitly; consistent with
  existing single-resource create behavior in `routers/tasks.py`.

## Decision: No live cross-user sync

- **Decision**: No polling or websocket is introduced. The frontend
  refetches comments/counts for the acting user's own view after a
  post/delete, the same way `BoardPage.refresh()` already does after task
  mutations.
- **Rationale**: Spec Clarifications explicitly scope this to self-only
  updates; matches the existing app's request/response-only pattern (no
  other real-time feature exists to be consistent with).

## Decision: Comment count delivery

- **Decision**: Comment count per task is delivered via a `comment_count`
  field returned alongside each task's own comments summary — sourced by
  the frontend calling `GET /api/tasks/{task_id}/comments` on demand when
  a thread is expanded, and a lightweight `GET
  /api/tasks/{task_id}/comments/count` (mirroring the existing
  `/api/tasks/count` pattern) used to populate the badge on the board
  without fetching full comment bodies up front.
- **Rationale**: Keeps the board's initial task list payload unchanged
  (no join needed on the hot path `GET /api/tasks`), reuses the existing
  `.../count` sibling-endpoint convention already established by
  `GET /api/tasks/count`, and avoids over-fetching comment text just to
  render a badge.
- **Alternatives considered**: Embedding `comment_count` directly on the
  `TaskRead` DTO via a join — rejected for this plan because it would
  change the existing, stable `TaskRead` shape and its parity contract
  across three backends; a separate count endpoint is additive and
  backend-parity-safe. This can be revisited later if per-task list
  performance becomes a concern (out of scope here).
