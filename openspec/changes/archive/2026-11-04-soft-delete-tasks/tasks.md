# Tasks

## 1. Current-behavior regression tests

- [x] 1.1 Add baseline DELETE regression tests: the initial Python test pinned repeat-delete 404 and was updated in 3.2 for idempotent soft-delete 204; .NET and Java DELETE of a missing task remain 404. Baseline verification passed with `cd backend-python && .venv/bin/pytest tests/test_tasks_api.py`, `cd backend-dotnet && dotnet test tests/TaskBoard.Api.Tests/TaskBoard.Api.Tests.csproj --filter FullyQualifiedName~TasksControllerTests`, and JDK 21 with `cd backend-java && ./mvnw -Dtest=TaskControllerTest test`.

## 2. Database schema

- [x] 2.1 Add nullable `deleted_at TIMESTAMP` to `database/schema.sql` and create `database/migrations/002_soft_delete_tasks.sql` without changing migration 001; verify the migration applies after 001 and the canonical schema handles both a fresh and existing database.

## 3. Python backend

- [x] 3.1 Map `deleted_at` and add a single reusable repository query selector for active, deleted-only, and include-deleted reads; implement soft delete, restore, permanent delete, and active-only count; verify with `cd backend-python && .venv/bin/pytest tests/test_task_service.py`.
- [x] 3.2 Update the Python router/service and `FakeTaskRepository` for `deleted=true`, `includeDeleted=true`, restore, and `permanent=true`; update `test_delete_task`, `test_delete_then_get_raises`, `test_count_returns_total`, and `test_count_filters_by_status`, and cover 204/404/422 plus filtering; verify with `cd backend-python && .venv/bin/pytest tests/test_tasks_api.py tests/test_task_service.py`.

## 4. .NET backend

- [ ] 4.1 Map `deleted_at` and implement one reusable repository query selector for active, deleted-only, and include-deleted reads; implement repository soft-delete, restore, and permanent-delete operations; verify with `cd backend-dotnet && dotnet test tests/TaskBoard.Api.Tests/TaskBoard.Api.Tests.csproj`.
- [ ] 4.2 Update .NET service/controller routes and tests for deleted listing, `includeDeleted`, restore, permanent deletion, and active-only reads; replace `DeleteAsync_RemovesExistingTask` with soft-delete assertions and cover status/error parity; verify with `cd backend-dotnet && dotnet test tests/TaskBoard.Api.Tests/TaskBoard.Api.Tests.csproj`.

## 5. Java backend

- [ ] 5.1 Map `deleted_at` and route task API reads through one reusable repository query selector; implement soft-delete, restore, permanent-delete, and active-only count behavior without task-service use of unfiltered inherited reads; verify with `cd backend-java && ./mvnw test`.
- [ ] 5.2 Update Java service/controller routes and tests for deleted listing, `includeDeleted`, restore, permanent deletion, and active-only reads; replace `deleteRemovesExistingTask` with soft-delete assertions and cover status/error parity; verify with `cd backend-java && ./mvnw test`.

## 6. React deleted-task experience

- [x] 6.1 Extend `taskService` for deleted-task listing, explicit deleted lookup, restore, and permanent deletion; update service tests for query parameters and routes; verified with `cd frontend && npm test -- --run` (21 tests passed).
- [x] 6.2 Add a deleted-tasks view and restore/permanent-delete actions with deliberate confirmation, preserving the existing active board behavior; add focused UI tests and verified with `cd frontend && npm test -- --run && npm run build`.

## 7. Cross-backend verification

- [ ] 7.1 Verify equivalent API status codes, response shapes, and task ordering for active/deleted list, GET, soft delete, restore, permanent delete, invalid filters, and count across Python, .NET, and Java; run the focused test suites from groups 3–5 and confirm no stats or comment APIs were added.
