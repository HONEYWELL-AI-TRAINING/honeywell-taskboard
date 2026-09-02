# Implementation Plan: Task Comments

**Branch**: `001-task-comments` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-task-comments/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a comment thread to each task: a `task_comments` table owned by
`database/schema.sql`; a Python backend slice (repository → service →
router) exposing list/create/delete under `/api/tasks/{task_id}/comments`;
and a frontend slice (a `TaskComments` thread + form, wired from `TaskCard`
via `commentService`) that shows a comment count, expands an inline
oldest-first thread, and lets any user post or delete a comment — all
without a full page reload for the acting user. This plan targets the
Python backend only, per Lab 02 scope; `.NET`/Java parity is Lab 03.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript/JSX with React 18 (frontend) — both match existing `backend-python/` and `frontend/`.

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x async, Pydantic v2, asyncpg (backend, all already in `requirements.txt`); React, axios, Vite (frontend, already in `package.json`).

**Storage**: PostgreSQL, via the shared `database/schema.sql`. New `task_comments` table, FK to `tasks`.

**Testing**: pytest + pytest-asyncio + httpx `AsyncClient` against the fake in-memory repository (backend, matches `backend-python/tests/`); Vitest + React Testing Library (frontend, matches `frontend/src/components/__tests__/`).

**Target Platform**: Existing local dev stack — Python backend served by uvicorn, Vite dev server for the frontend, shared Postgres instance.

**Project Type**: Web application (existing `backend-python/` + `frontend/` split already in the repo).

**Performance Goals**: No new performance targets beyond the existing app's expectations (single-digit-ms local queries; this is a training/demo app, not a scale target).

**Constraints**: Must preserve the existing error contract (404 / 422 only), the three-layer architecture, and cross-backend parity expectations (this backend's request/response shape must be portable to `.NET`/Java later, even though they are out of scope here). No live cross-user sync (per spec Clarifications) — the acting user's own view updates immediately via local state refresh; no polling/websocket infrastructure is introduced.

**Scale/Scope**: One new table, ~3 new endpoints, ~2 new frontend components, no changes to existing task CRUD behavior.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Layered Architecture | New `CommentRepository` (all SQL), `CommentService` (validation), `comments` router (HTTP↔domain only); frontend adds `commentService.js` (HTTP), a `TaskComments` container-ish component that calls it, presentational sub-parts stay dumb | PASS |
| II. Single Schema Owner | `task_comments` table added only to `database/schema.sql`; no SQLAlchemy auto-create, no migrations | PASS |
| III. Error Contract | Reuses 404 (missing task/comment) and 422 (missing/blank author or text, oversized author/text) only | PASS |
| IV. Cross-Backend Parity | Endpoint shapes documented in `contracts/` so `.NET`/Java (Lab 03) can match byte-for-byte; this plan does not implement those backends | PASS (deferred work tracked, not a violation) |
| V. Tests-First-Class | Repository/service/router tests (backend) and component/service tests (frontend) planned per layer in this doc; `/speckit-tasks` will sequence them before "done" | PASS |
| VI. Spec Is Source of Truth | This plan derives directly from `spec.md`; no undocumented behavior introduced | PASS |
| VII. Scoped Context | N/A — no `.github/prompts/context-brief.prompt.md` exists yet in this repo; not blocking | PASS (no violation) |

No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-comments/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── comments-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend-python/
├── models/
│   └── comment.py                 # NEW — SQLAlchemy mapping for task_comments
├── schemas/
│   └── comment.py                 # NEW — CommentCreate / CommentRead / CommentCount (Pydantic)
├── repositories/
│   └── comment_repository.py      # NEW — all comment SQL access
├── services/
│   ├── comment_service.py         # NEW — validation + orchestration
│   └── errors.py                  # EXTEND — add CommentNotFound
├── routers/
│   └── comments.py                # NEW — /api/tasks/{task_id}/comments routes
├── dependencies.py                # EXTEND — get_comment_repository / get_comment_service
├── main.py                        # EXTEND — include_router(comments.router)
└── tests/
    ├── test_comment_service.py    # NEW
    ├── test_comments_api.py       # NEW
    └── conftest.py                # EXTEND — FakeCommentRepository, seed helpers

frontend/
├── src/
│   ├── components/
│   │   ├── TaskCard.jsx           # EXTEND — shows comment count, toggles thread
│   │   ├── TaskComments.jsx       # NEW — thread list + post form, per task
│   │   └── __tests__/
│   │       └── TaskComments.test.jsx   # NEW
│   ├── pages/
│   │   └── BoardPage.jsx          # EXTEND — passes comment counts/handlers down if needed
│   └── services/
│       └── commentService.js      # NEW — thin axios wrapper, mirrors taskService.js

database/
└── schema.sql                     # EXTEND — add task_comments table + index
```

**Structure Decision**: Reuses the existing web-application split
(`backend-python/` three-layer stack + `frontend/`
components/pages/services stack). No new top-level directories; every new
file lands beside its existing counterpart (e.g., `comment_repository.py`
next to `task_repository.py`).

## Complexity Tracking

> No Constitution Check violations — table intentionally omitted.
