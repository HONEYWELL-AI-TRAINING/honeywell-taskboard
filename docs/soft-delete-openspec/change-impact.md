# Change-Impact Analysis — Task soft delete

## The change (innermost ring)

Change `DELETE /api/tasks/{id}` in each of the three backend implementations
from physically deleting a task row to marking it deleted. Normal task reads
must exclude marked rows; deleted-task lookup behavior, trash/restore/permanent
delete endpoints, and count semantics must be frozen in the spec before
implementation.

## Blast radius

### Ring 1 — Directly dependent (imports/calls the changed code, or its contract)

| File / module | How it depends | Needs a change? | Needs a new/changed test? |
|---------------|----------------|:---------------:|:-------------------------:|
| `database/schema.sql` | Shared source of truth for the `tasks` table. Must store the soft-delete marker. | Yes | Schema-level validation or DB-backed coverage if available. |
| `backend-python/models/task.py` | SQLAlchemy mapping of `tasks`. | Yes | Model/repository coverage for marker persistence. |
| `backend-python/repositories/task_repository.py` | Implements list, status-filtered list, count, get, and delete queries. These are the Python read/write paths. | Yes | Test list/get/count exclusion and soft-delete persistence. |
| `backend-python/services/task_service.py` | Routes service reads and delete through repository methods; defines missing-task behavior. | Likely; align interface/behavior with repository | Update deletion and hidden-task tests; test service semantics. |
| `backend-python/routers/tasks.py` | Exposes list, count, get, and DELETE HTTP routes. | Only if the approved API adds deleted-task, restore, or permanent-delete routes; existing routes should keep their contract otherwise. | Keep 204/404 behavior covered; add route tests for any approved new API. |
| `backend-python/tests/conftest.py` | Fake repository implements list, count, get, and delete used by API/service tests. | Yes | Fake must model soft deletion and normal-read filtering. |
| `backend-python/tests/test_task_service.py` | `test_delete_then_get_raises` currently expects `TaskNotFound` after delete. | Test remains valid if normal get hides deleted rows; rename/revise to express soft-delete semantics. | Yes: also cover list/count exclusion and retained record/state where feasible. |
| `backend-python/tests/test_tasks_api.py` | `test_delete_task` expects DELETE 204 followed by GET 404; list/count routes are also tested here. | Existing 404 can remain if deleted tasks are hidden; add list/count exclusion tests. | Yes. |
| `backend-dotnet/src/TaskBoard.Api/Models/TaskItem.cs` | Domain/entity mapping needs the soft-delete state. | Yes | Model/repository coverage as available. |
| `backend-dotnet/src/TaskBoard.Api/Data/TaskBoardContext.cs` | EF Core maps entity properties to shared columns. | Yes | Verify mapping/schema behavior. |
| `backend-dotnet/src/TaskBoard.Api/Repositories/ITaskRepository.cs` | Declares list/get/delete operations used by service. | Likely; align operation names/contracts with soft-delete behavior. | Update affected service tests. |
| `backend-dotnet/src/TaskBoard.Api/Repositories/TaskRepository.cs` | Implements list/status filter, get, and delete against `tasks`. | Yes | Add query coverage proving deleted rows are excluded; verify delete marks rather than removes. |
| `backend-dotnet/src/TaskBoard.Api/Services/TaskService.cs` | Loads tasks for get/update/delete and delegates persistence. | Likely; preserve missing-task behavior for deleted rows. | Update service tests and add relevant read-exclusion coverage. |
| `backend-dotnet/src/TaskBoard.Api/Controllers/TasksController.cs` | Exposes current task routes and HTTP status contract. | Only for approved API additions; existing DELETE should remain 204. | Existing status behavior should remain covered. |
| `backend-dotnet/tests/TaskBoard.Api.Tests/TaskServiceTests.cs` | `DeleteAsync_RemovesExistingTask` verifies a repository delete call, not actual row removal. | Yes; revise to assert the soft-delete operation. | Yes. |
| `backend-java/src/main/java/com/honeywell/taskboard/model/TaskItem.java` | JPA mapping of the shared `tasks` table. | Yes | Verify marker mapping. |
| `backend-java/src/main/java/com/honeywell/taskboard/repository/TaskRepository.java` | Custom status-filtered list query and inherited `JpaRepository` query methods. | Yes; custom and inherited normal reads must consistently hide deleted rows. | Add query coverage for list, get, and any exposed inherited reads. |
| `backend-java/src/main/java/com/honeywell/taskboard/service/TaskService.java` | Service contract includes list/get/delete. | Likely; align contract if delete operation changes. | Update service tests. |
| `backend-java/src/main/java/com/honeywell/taskboard/service/TaskServiceImpl.java` | Implements list/get/update/delete; `find` uses inherited `findById`. | Yes; ensure normal lookup hides deleted tasks and delete marks them. | Yes. |
| `backend-java/src/main/java/com/honeywell/taskboard/web/TaskController.java` | Exposes current list/get/delete endpoints. | Only for approved API additions; preserve current 204/404 behavior otherwise. | Keep controller contract tests. |
| `backend-java/src/test/java/com/honeywell/taskboard/service/TaskServiceImplTest.java` | `deleteRemovesExistingTask` verifies a repository delete call, not physical row removal. | Yes; revise to assert soft-delete behavior. | Yes. |
| `backend-java/src/test/java/com/honeywell/taskboard/web/TaskControllerTest.java` | `deleteReturns204` pins the existing DELETE response. | No, if 204 is retained. | Keep as regression test. |

### Ring 2 — Indirectly affected (depends on Ring 1, or shares state/schema/contract)

| File / area | Path of impact | Risk if ignored |
|-------------|----------------|-----------------|
| `frontend/src/services/taskService.js` and `frontend/src/pages/BoardPage.jsx` | The current service sends DELETE and the board reloads/displays normal task-list data. The endpoint/method can remain unchanged, but backend list results must omit soft-deleted tasks. | Deleted tasks could remain visible or frontend behavior could diverge if response semantics change without coordination. |
| `frontend/src/services/__tests__/taskService.test.js` | Tests the HTTP wrapper, including DELETE request behavior. | A changed route or response contract could break the UI contract; likely unchanged for a simple soft-delete implementation. |
| `database/seed.sql` and test fixtures | Seeded tasks and fakes may need the new marker's default/initial value. | Existing tasks may be misclassified or fixtures may not reflect the database default. |
| Python `GET /api/tasks/count` path: `routers/tasks.py`, `services/task_service.py`, `repositories/task_repository.py` | Count is a task read and must exclude deleted rows if it represents active/normal tasks. | Counts disagree with the normal list. The inspected .NET and Java task APIs have no count endpoint. |
| Java inherited `JpaRepository` reads | `findByOptionalStatus` is custom, but inherited `findAll`, `findAllById`, `findById`, `existsById`, and `count` are additional query surfaces. | Direct/inadvertent repository use could expose deleted rows or report inconsistent counts. |
| `docs/feature-task-comments.md` and future `task_comments` relation | The comments brief says physical task deletion should cascade to comments. Soft deletion must not trigger physical cascade; comments should remain available on restore. | A later implementation could erase comments or hide them inconsistently. No comments table, FK, cascade implementation, or comment tests exist in the current schema/code. |
| `docs/feature-soft-delete.md` | The brief also requests a deleted-task view, restore, and a deliberate permanent delete, and raises questions about deleted-task GET, count, and comment behavior. | Implementing only the marker while assuming these unresolved contracts could lead to incomplete or incompatible APIs. These decisions need a scoped spec before implementation. |

### Ring 3 — Believed unaffected (protected by regression tests)

| Area | Why it should be safe | Which existing test proves it |
|------|-----------------------|-------------------------------|
| Successful DELETE HTTP response | Soft delete can preserve the current 204 contract. | Java `TaskControllerTest.deleteReturns204`; Python `test_tasks_api.py::test_delete_task`. There is no equivalent .NET controller DELETE test in the inspected suite. |
| Missing-ID DELETE response | A task that never existed should still be reported as missing. | Python `test_tasks_api.py::test_delete_missing_task_returns_404`; .NET `TaskServiceTests.DeleteAsync_ThrowsWhenMissing`; Java `TaskServiceImplTest.deleteThrowsWhenMissing`. |
| Task creation and ordinary status validation | Soft-delete filtering is separate from task field validation and creation. | Existing create/status tests in `backend-python/tests/test_tasks_api.py`, `backend-python/tests/test_task_service.py`, `backend-dotnet/tests/TaskBoard.Api.Tests/TaskServiceTests.cs`, and `backend-java/src/test/java/com/honeywell/taskboard/service/TaskServiceImplTest.java`. |
| Normal list status filtering for non-deleted tasks | Existing status behavior should remain unchanged while adding a deleted-row predicate. | Python `test_list_filters_by_status`; .NET `TaskServiceTests.ListAsync_PassesStatusFilterToRepository`; Java `TaskServiceImplTest.listPassesStatusFilterThrough`. Add assertions with deleted fixtures to close the new gap. |

## Cross-cutting checks

- [x] Database schema: `database/schema.sql` must change to add the soft-delete marker. There is no runtime migration framework; schema changes must be applied through the repository's documented SQL workflow and existing databases need an explicit compatible schema update.
- [x] The other two backends: .NET, Python, and Java all map to the shared task table; implement equivalent marker behavior and normal-read filtering in all three.
- [ ] Existing seed data / fixtures: verify `database/seed.sql` and Python's `FakeTaskRepository` defaults remain active by default; update fixtures and tests to cover deleted rows.
- [ ] Existing API contract: no `usecase.md` was identified in the inspected repository paths. Keep current DELETE 204 and missing-resource 404 unless the approved specification explicitly changes them; define behavior for GET of soft-deleted tasks.
- [ ] Downstream features: comments are documented but not implemented; preserve comments on soft delete/restore when that feature exists. Python has `GET /api/tasks/count`, which must be defined as active-only or all-task count. The inspected task APIs do not currently expose `/api/tasks/stats`.
- [ ] Frontend: current DELETE service contract need not change for a marker-only implementation. Verify board/list behavior uses the normal filtered task list; assess separate UI work only if deleted-task viewing, restore, or permanent delete are approved.

## Regression protection plan

| Existing behaviour that must be preserved | Existing test that guards it | Gap? add a test |
|-------------------------------------------|------------------------------|-----------------|
| DELETE of an existing task returns 204. | Python `test_tasks_api.py::test_delete_task`; Java `TaskControllerTest.deleteReturns204`. | .NET controller has no corresponding DELETE status test in the inspected tests; add one if maintaining parity. |
| DELETE of a nonexistent task returns 404. | Python `test_tasks_api.py::test_delete_missing_task_returns_404`; .NET `TaskServiceTests.DeleteAsync_ThrowsWhenMissing`; Java `TaskServiceImplTest.deleteThrowsWhenMissing`. | No additional gap for missing IDs; also test repeated DELETE semantics once specified. |
| Soft-deleted task is hidden from normal GET. | Python `test_tasks_api.py::test_delete_task` GET-after-DELETE assertion and `test_task_service.py::test_delete_then_get_raises`. | Add equivalent .NET and Java service/API coverage. |
| Soft-deleted tasks are omitted from normal list and count queries, with status filters still applied. | Existing tests cover status filtering/counts only for active fixtures. | Yes, add deleted fixtures for each implemented list/filter/count surface, including Java inherited query surfaces as applicable. |
| Soft delete preserves the task row and its associated comments. | No current test; comments are not yet implemented. | Yes, add persistence coverage; add comment-retention coverage with the comments feature. |

## Change-impact summary (carry forward to the plan)

- Files in scope (Ring 1 + necessary Ring 2), total count: approximately 20–25 implementation, schema, and test files, depending on whether service/controller interfaces need changes. Minimum scope includes the shared schema; task model/repository/service and tests in all three backends; Python fake repository/tests; and frontend contract verification.
- Files explicitly **out** of scope (and why): frontend delete-service route/signature changes, comment implementation, and restore/trash/permanent-delete endpoints are out of the marker-and-default-read change until the spec resolves their API and UI behavior. The future comments relation must nevertheless be preserved by not physically deleting rows.
- New regression tests to add before implementing: deleted tasks excluded from list/status-filtered list/get/count where available; task row remains persisted after DELETE; parity for .NET and Java; and .NET controller DELETE 204 coverage. Add restore, permanent-delete, deleted-list, and comment-retention tests if those behaviors are included in the approved scope.
- The single riskiest part of this change, and how it's mitigated: inconsistent filtering across repository query surfaces, especially Java inherited JPA methods and Python count, can leak deleted tasks or produce mismatched totals. Inventory and test every exposed read path in each backend, and define the intended count/GET semantics in the spec before implementation.
