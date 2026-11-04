# Design

## Context

See `proposal.md` for motivation. The task table is shared by the Python,
.NET, and Java APIs; schema changes are managed through SQL files, not ORM
migrations. All three repositories currently physically delete tasks and read
tasks without a deletion predicate. The React board only displays the normal
task list. The current task-management capability records Python's existing
API behavior.

The change-impact analysis scopes the work to the shared task schema, all
three task backends, their affected tests, and the React task view/service.
There is no stats endpoint or task-comment model, table, or endpoint in the
current codebase.

## Goals / Non-Goals

**Goals:**

- Keep a task row recoverable after normal DELETE and restore its prior task
  content and associations.
- Provide active and deleted task retrieval, restoration, and deliberate
  permanent deletion with matching behavior in all backends.
- Centralize the deleted-row selection in each backend's repository layer.
- Keep the existing 204 DELETE success response and the 404/422 error contract.

**Non-Goals:**

- Add a stats endpoint or implement task comments in this change.
- Auto-purge, retention periods, bulk operations, or deletion attribution.
- Change task create/update validation or task status semantics.

## Decisions

### Store deletion state as a nullable timestamp

Add `deleted_at TIMESTAMP NULL` to `tasks`; `NULL` means active and a timestamp
means deleted. Use migration `002_soft_delete_tasks.sql` after migration 001.
Do not edit migration 001. Keep `database/schema.sql` as the cumulative schema
and include the column in the table definition plus an additive
`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statement so applying the canonical
schema also upgrades an existing database.

All three task models map the nullable timestamp. The existing database
`updated_at` trigger will update `updated_at` when `deleted_at` changes. Restore
returns the task's original business fields and associations; `updated_at`
continues to reflect the restore operation under the existing trigger
contract.

**Alternative considered:** a boolean marker. A timestamp gives the required
active/deleted distinction while also recording when deletion occurred without
adding a separate audit field.

### Put deleted-row selection in a shared repository query path

Each backend repository will own one reusable task-query selector that accepts
the requested view (active by default, deleted-only for `deleted=true`, or
include-all for an explicit lookup) and applies the `deleted_at` predicate.
List, status-filtered list, count, and ID lookup paths will build on that
selector rather than repeat independent deletion conditions. Services and
controllers will pass the intent but will not implement SQL filtering.

In Java, task API reads must use repository methods backed by the common
selector rather than bypassing it through inherited `JpaRepository` reads.
This keeps deleted rows from leaking through the actual API query paths.

**Alternative considered:** add a filter separately to each query. That risks
omitting a read path and makes list/count/get behavior diverge.

### Keep the task API defaults active-only and make deleted access explicit

- `GET /api/tasks` lists active tasks; `deleted=true` selects deleted tasks.
  Existing `status` filtering composes with the selected view.
- `GET /api/tasks/{id}` hides a deleted task with 404 unless
  `includeDeleted=true`; the explicit option returns either active or deleted
  tasks.
- `PUT` uses the normal active-only lookup, so a deleted task returns 404
  until restored.
- `GET /api/tasks/count` counts active tasks only. Any stats/aggregate query
  added in the future must use the active-only repository selector.
- Invalid status or boolean query input returns 422 in each backend.

### Make restore and permanent delete explicit state transitions

Normal `DELETE` sets `deleted_at` and returns 204. Repeating it on an already
deleted row is idempotent: return 204 and retain the original deletion state.
`POST /api/tasks/{id}/restore` clears `deleted_at` and returns 204; an unknown
or already-active ID returns 404. `DELETE ...?permanent=true` physically
removes an existing active or deleted task and returns 204; a missing ID
returns 404.

These idempotency and success-code details resolve unspecified edge behavior
using the existing 204/404 contract. The permanent-delete UI action must be
visibly separate from ordinary delete and require deliberate confirmation.

**Alternative considered:** use one endpoint with a request body to select the
transition. The explicit route/query choices from the user keep the ordinary
DELETE safe and make permanent removal deliberate without changing its
existing response contract.

### Treat stats and comments as integration constraints, not new APIs

The inspected code has no `/api/tasks/stats` route. Python's `/api/tasks/count`
is the only current count endpoint, and it will count active tasks only.
Do not add stats routes as part of this change. If a stats endpoint is added
later, its task aggregates must exclude deleted rows.

No task-comment model/table/routes currently exist, so do not add comment
functionality here. When comments are introduced, GET/POST comments for a
deleted task must return 404; soft delete and restore must preserve comment
rows so they are visible after restore; physical cascade may occur only on
permanent task deletion. Soft deletion itself does not issue a physical delete
and therefore must not trigger that future cascade.

## Existing Tests to Update

- Python `backend-python/tests/test_tasks_api.py::test_delete_task`: retain
  the 204 and default GET 404 assertions; also verify the task is retrievable
  with `includeDeleted=true` and excluded from normal list/count results.
- Python `backend-python/tests/test_task_service.py::test_delete_then_get_raises`:
  continue asserting that default service lookup hides the task, and verify
  retained deleted state through the explicit deleted lookup.
- Python `backend-python/tests/conftest.py::FakeTaskRepository`: replace
  physical removal with a deletion timestamp and implement active/deleted
  filtering so tests model repository behavior.
- Python `backend-python/tests/test_tasks_api.py::test_count_returns_total`
  and `test_count_filters_by_status`: extend with deleted tasks and assert
  counts include only active tasks.
- .NET `backend-dotnet/tests/TaskBoard.Api.Tests/TaskServiceTests.cs::DeleteAsync_RemovesExistingTask`:
  replace the physical `DeleteAsync`
  expectation with the repository soft-delete operation and assert the
  timestamp/state transition.
- Java
  `backend-java/src/test/java/com/honeywell/taskboard/service/TaskServiceImplTest.java::deleteRemovesExistingTask`:
  replace `repository.delete` verification with the repository soft-delete
  operation and state assertion.
- Existing Python/Java 204 controller tests remain regression tests; add .NET
  controller coverage for DELETE 204 and all backends' tests for list/get,
  restore, permanent delete, and deleted count behavior.
- Frontend
  `frontend/src/services/__tests__/taskService.test.js::deletes by id` should
  remain valid for normal deletion; add service/UI coverage for listing
  deleted tasks, restore, and confirmed permanent deletion. There is no
  existing board-page test asserting the seeded-task count in the inspected
  frontend test tree.

## Risks / Trade-offs

- [A repository path omits the deleted predicate] -> Route every task API
  read, including count and explicit lookups, through the shared repository
  selector and add deleted fixtures to each backend's tests.
- [A migration is applied inconsistently with the canonical schema] -> Add
  migration 002 and update `schema.sql` together; verify both fresh and
  already-created database paths without modifying migration 001.
- [Java inherited repository reads bypass the selector] -> Keep service/API
  operations on the repository's filtered methods and cover those methods;
  do not call inherited broad reads from task services.
- [Frontend normal and deleted views become mixed] -> Keep the board's default
  request active-only and use an explicit deleted view with dedicated restore
  and permanent-delete actions.
- [Future comment cascade removes data too early] -> Soft-delete only updates
  `deleted_at`; reserve physical row deletion (and any FK cascade) for
  `permanent=true`.

## Migration Plan

1. Apply migration 002 after migration 001 to add nullable `deleted_at`.
2. Deploy compatible backend versions that use the shared repository
   selector; active existing rows remain active because the new column is
   `NULL`.
3. Deploy the React deleted-task view/actions against the agreed routes.
4. If rolling back application code, retain the additive column. Do not drop
   `deleted_at` as a rollback step because that would discard deletion state
   needed for recovery.

## Open Questions

None. Stats and comments scope was resolved as future integration constraints,
not new endpoints or models in this change.
