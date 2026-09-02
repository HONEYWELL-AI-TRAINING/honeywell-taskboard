# Tasks: Task Comments

**Input**: Design documents from `/specs/001-task-comments/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/comments-api.md`, and `quickstart.md`

**Tests**: Tests are required by the feature specification and the project constitution. Write each story's tests before its implementation tasks.

## Phase 1: Setup

**Purpose**: Confirm the existing Python and frontend test harnesses cover the feature work.

- [X] T001 [P] Confirm comment test conventions and fixtures in backend-python/tests/conftest.py and frontend/src/setupTests.js

---

## Phase 2: Foundational

**Purpose**: Establish the persistence and three-layer backend primitives needed by every comment operation.

- [X] T002 Add the task_comments table, cascade foreign key, and task_id index in database/schema.sql
- [X] T003 [P] Add Comment SQLAlchemy mapping and CommentCreate, CommentRead, and CommentCount schemas in backend-python/models/comment.py and backend-python/schemas/comment.py
- [X] T004 Add repository-layer coverage for oldest-first listing, counts, creates, and scoped deletes in backend-python/tests/test_comment_repository.py
- [X] T005 Implement CommentRepository and CommentService validation, missing-resource errors, and dependency providers in backend-python/repositories/comment_repository.py, backend-python/services/comment_service.py, backend-python/services/errors.py, and backend-python/dependencies.py

**Checkpoint**: The database model and backend business layer are ready for HTTP routes.

---

## Phase 3: User Story 1 - Read a task's discussion at a glance (Priority: P1) MVP

**Goal**: Show a comment-count indicator only for cards whose tasks have comments.

**Independent Test**: Seed one task with comments and one without, then verify the first card shows the correct count and the second has no indicator.

- [X] T006 [P] [US1] Add service and API tests for GET /api/tasks/{task_id}/comments/count, including zero counts and a missing task, in backend-python/tests/test_comment_service.py and backend-python/tests/test_comments_api.py
- [X] T007 [P] [US1] Add TaskCard badge tests for positive and zero comment counts in frontend/src/components/__tests__/TaskCard.test.jsx
- [X] T008 [US1] Implement the count endpoint and router registration in backend-python/routers/comments.py and backend-python/main.py, then fetch and render per-task counts through frontend/src/services/commentService.js and frontend/src/components/TaskCard.jsx

**Checkpoint**: A board reload displays accurate comment badges without loading comment text.

---

## Phase 4: User Story 2 - Read and post comments on a task (Priority: P1)

**Goal**: Let users expand an inline oldest-first thread and immediately add a valid comment.

**Independent Test**: Open a task thread, post a valid comment, and verify it appears last with its author and timestamp without navigating away.

- [X] T009 [P] [US2] Add API and service tests for oldest-first GET and validated POST comment operations, including 404 and 422 cases, in backend-python/tests/test_comment_service.py and backend-python/tests/test_comments_api.py
- [X] T010 [P] [US2] Add inline thread, posting, validation, and timestamp rendering tests in frontend/src/components/__tests__/TaskComments.test.jsx
- [X] T011 [US2] Implement GET and POST comment routes in backend-python/routers/comments.py and the inline thread, post form, and immediate local refresh in frontend/src/components/TaskComments.jsx, frontend/src/components/TaskCard.jsx, and frontend/src/services/commentService.js

**Checkpoint**: Users can read and post comments from the board, with the badge and thread updating for the acting user.

---

## Phase 5: User Story 3 - Remove an unwanted comment (Priority: P2)

**Goal**: Allow any user to remove a comment and immediately reconcile the thread and count.

**Independent Test**: Delete a posted comment and verify it disappears from the thread and decrements the task badge.

- [X] T012 [P] [US3] Add service, API, and component tests for deleting comments, missing comment/task 404s, and count removal at zero in backend-python/tests/test_comment_service.py, backend-python/tests/test_comments_api.py, and frontend/src/components/__tests__/TaskComments.test.jsx
- [X] T013 [US3] Implement the DELETE comment route and immediate thread/count update controls in backend-python/routers/comments.py, frontend/src/services/commentService.js, frontend/src/components/TaskComments.jsx, and frontend/src/components/TaskCard.jsx

**Checkpoint**: Any displayed comment can be deleted without a page reload and no stale badge remains.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Run the documented automated and manual feature checks, including cascade deletion.

- [X] T014 Validate all comment scenarios and cascade deletion using specs/001-task-comments/quickstart.md, backend-python/tests/test_comments_api.py, and frontend/src/components/__tests__/TaskComments.test.jsx

---

## Dependencies & Execution Order

- Phase 1 can start immediately.
- Phase 2 depends on Phase 1; T005 depends on T002 through T004 and blocks all user stories.
- US1 depends on Phase 2 and is the MVP.
- US2 depends on Phase 2 and integrates with the US1 card badge work in T008.
- US3 depends on Phase 2 and the shared thread implementation from US2.
- Phase 6 depends on the completed stories being delivered.

## Parallel Opportunities

- T001 and the independent model/schema work in T003 can be prepared alongside schema planning, but T005 must wait for the finalized persistence contract.
- Within US1, T006 and T007 can run in parallel.
- Within US2, T009 and T010 can run in parallel.
- Within US3, T012 can be authored while the delete contract is being finalized; T013 follows its assertions.

## Parallel Example: User Story 2

```text
Task: "Add API and service tests in backend-python/tests/test_comment_service.py and backend-python/tests/test_comments_api.py"
Task: "Add inline thread tests in frontend/src/components/__tests__/TaskComments.test.jsx"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete and verify US1 comment badges.
3. Deliver US2 to provide the core read-and-post discussion workflow.

### Incremental Delivery

1. Persist and validate comments through the shared three-layer Python backend.
2. Add count badges, then thread reading and posting.
3. Add deletion and run the quickstart scenarios, including database cascade deletion.

## Format Validation

All 14 tasks use the required checkbox, sequential task ID, applicable `[P]` marker, user-story label for story work, and exact file path format.

## Phase 7: Convergence

- [X] T015 CRITICAL Implement and test the task comments API contract in backend-dotnet/ and backend-java/ to restore cross-backend parity per Constitution IV / FR-011 (missing)
- [X] T016 Add and run a database-backed task-deletion cascade test that proves associated task_comments are removed per FR-008 / SC-004 (partial)