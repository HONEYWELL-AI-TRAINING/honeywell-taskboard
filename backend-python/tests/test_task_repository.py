"""Unit tests for task query selection and persistence operations."""
from datetime import datetime

from sqlalchemy.dialects import postgresql

from models.task import Task
from repositories.task_repository import TaskRepository


class FakeResult:
    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def scalar_one(self):
        return 0


class FakeSession:
    def __init__(self):
        self.statements = []
        self.flushed = False
        self.deleted = []

    async def execute(self, statement):
        self.statements.append(statement)
        return FakeResult()

    async def flush(self):
        self.flushed = True

    async def refresh(self, task):
        return None

    async def delete(self, task):
        self.deleted.append(task)


def statement_sql(statement):
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def sample_task():
    return Task(
        id=1,
        title="Sample",
        status="todo",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )


def test_task_maps_nullable_deleted_at():
    assert Task.__table__.c.deleted_at.nullable


async def test_list_uses_deleted_selection_and_status_filter():
    session = FakeSession()
    repository = TaskRepository(session)

    await repository.list(status="done", deleted=True)

    sql = statement_sql(session.statements[-1])
    assert "deleted_at IS NOT NULL" in sql
    assert "status = 'done'" in sql


async def test_list_defaults_to_active_tasks():
    session = FakeSession()
    repository = TaskRepository(session)

    await repository.list()

    assert "deleted_at IS NULL" in statement_sql(session.statements[-1])


async def test_count_excludes_deleted_tasks():
    session = FakeSession()
    repository = TaskRepository(session)

    await repository.count(status="done")

    sql = statement_sql(session.statements[-1])
    assert "deleted_at IS NULL" in sql
    assert "status = 'done'" in sql


async def test_get_can_include_deleted_tasks_explicitly():
    session = FakeSession()
    repository = TaskRepository(session)

    await repository.get(1, include_deleted=True)

    assert "deleted_at IS NULL" not in statement_sql(session.statements[-1])


async def test_soft_delete_and_restore_update_timestamp_without_removing_row():
    session = FakeSession()
    repository = TaskRepository(session)
    task = sample_task()

    await repository.delete(task)
    assert task.deleted_at is not None
    assert session.deleted == []
    assert session.flushed

    session.flushed = False
    await repository.restore(task)
    assert task.deleted_at is None
    assert session.deleted == []
    assert session.flushed


async def test_permanent_delete_removes_row():
    session = FakeSession()
    repository = TaskRepository(session)
    task = sample_task()

    await repository.delete(task, permanent=True)

    assert session.deleted == [task]
    assert session.flushed
