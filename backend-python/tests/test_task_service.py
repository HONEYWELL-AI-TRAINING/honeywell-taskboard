"""Unit tests for TaskService against the in-memory fake repository."""
from datetime import datetime

import pytest

from schemas.task import TaskCreate, TaskUpdate
from services.errors import InvalidStatus, TaskNotFound
from services.task_service import TaskService
from tests.conftest import FakeTaskRepository


@pytest.fixture
def service() -> TaskService:
    return TaskService(FakeTaskRepository())


async def test_create_defaults_to_todo(service):
    task = await service.create_task(TaskCreate(title="X"))
    assert task.status == "todo"
    assert task.id == 1


async def test_create_rejects_invalid_status(service):
    with pytest.raises(InvalidStatus):
        await service.create_task(TaskCreate(title="X", status="blocked"))


async def test_list_with_invalid_status_raises(service):
    with pytest.raises(InvalidStatus):
        await service.list_tasks("blocked")


async def test_get_missing_raises(service):
    with pytest.raises(TaskNotFound):
        await service.get_task(42)


async def test_update_changes_fields(service):
    created = await service.create_task(TaskCreate(title="Old"))
    updated = await service.update_task(
        created.id, TaskUpdate(title="New", status="done", assignee="Ana")
    )
    assert updated.title == "New"
    assert updated.status == "done"
    assert updated.assignee == "Ana"


async def test_delete_then_get_raises(service):
    created = await service.create_task(TaskCreate(title="Temp"))
    await service.delete_task(created.id)
    with pytest.raises(TaskNotFound):
        await service.get_task(created.id)
    retained = await service.get_task(created.id, include_deleted=True)
    assert retained.deleted_at is not None


async def test_delete_is_idempotent(service):
    created = await service.create_task(TaskCreate(title="Temp"))
    await service.delete_task(created.id)
    await service.delete_task(created.id)
    assert (await service.get_task(created.id, include_deleted=True)).deleted_at is not None


async def test_list_tasks_excludes_deleted_by_default(service):
    active = await service.create_task(TaskCreate(title="Active"))
    deleted = await service.create_task(TaskCreate(title="Deleted"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)

    tasks = await service.list_tasks()

    assert [task.id for task in tasks] == [active.id]


async def test_list_tasks_can_select_deleted(service):
    active = await service.create_task(TaskCreate(title="Active"))
    deleted = await service.create_task(TaskCreate(title="Deleted"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)

    tasks = await service.list_tasks(deleted=True)

    assert [task.id for task in tasks] == [deleted.id]
    assert active.id not in [task.id for task in tasks]


async def test_get_deleted_can_be_explicitly_included(service):
    deleted = await service.create_task(TaskCreate(title="Deleted"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)
    with pytest.raises(TaskNotFound):
        await service.get_task(deleted.id)

    assert await service.get_task(deleted.id, include_deleted=True) is deleted


async def test_update_deleted_task_raises(service):
    deleted = await service.create_task(TaskCreate(title="Deleted"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)

    with pytest.raises(TaskNotFound):
        await service.update_task(
            deleted.id, TaskUpdate(title="Changed", status="todo")
        )


async def test_restore_clears_deleted_timestamp(service):
    deleted = await service.create_task(TaskCreate(title="Deleted"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)

    await service.restore_task(deleted.id)

    assert deleted.deleted_at is None
    assert await service.get_task(deleted.id) is deleted


async def test_restore_active_or_missing_raises(service):
    active = await service.create_task(TaskCreate(title="Active"))
    with pytest.raises(TaskNotFound):
        await service.restore_task(active.id)
    with pytest.raises(TaskNotFound):
        await service.restore_task(999)


async def test_permanent_delete_removes_task(service):
    task = await service.create_task(TaskCreate(title="Permanent"))

    await service.delete_task(task.id, permanent=True)

    with pytest.raises(TaskNotFound):
        await service.get_task(task.id, include_deleted=True)


async def test_count_returns_total(service):
    await service.create_task(TaskCreate(title="A"))
    await service.create_task(TaskCreate(title="B", status="done"))
    deleted = await service.create_task(TaskCreate(title="Deleted", status="done"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)
    assert await service.count_tasks() == 2


async def test_count_filters_by_status(service):
    await service.create_task(TaskCreate(title="A"))
    await service.create_task(TaskCreate(title="B", status="done"))
    deleted = await service.create_task(TaskCreate(title="Deleted", status="done"))
    deleted.deleted_at = datetime(2026, 1, 2, 12, 0, 0)
    assert await service.count_tasks("done") == 1


async def test_count_rejects_invalid_status(service):
    with pytest.raises(InvalidStatus):
        await service.count_tasks("blocked")
