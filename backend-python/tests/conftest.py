"""Test fixtures.

These tests never touch PostgreSQL. An in-memory fake repository is injected
in place of the real one, so the router + service + schema stack is exercised
end to end without a database.
"""
from collections.abc import Sequence
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from dependencies import get_task_repository
from main import app
from models.task import Task


class FakeTaskRepository:
    """List-backed stand-in for TaskRepository with the same async surface."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def seed(self, **kwargs) -> Task:
        now = datetime(2026, 1, 1, 12, 0, 0)
        task = Task(
            id=self._next_id,
            title=kwargs.get("title", "Seed task"),
            description=kwargs.get("description"),
            status=kwargs.get("status", "todo"),
            assignee=kwargs.get("assignee"),
            created_at=now,
            updated_at=now,
            deleted_at=kwargs.get("deleted_at"),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    async def list(self, status: str | None = None, deleted: bool = False) -> Sequence[Task]:
        rows = sorted(self._tasks.values(), key=lambda t: t.id)
        return [
            task
            for task in rows
            if (task.deleted_at is not None) == deleted
            and (status is None or task.status == status)
        ]

    async def count(self, status: str | None = None) -> int:
        return len(await self.list(status))

    async def get(self, task_id: int, include_deleted: bool = False) -> Task | None:
        task = self._tasks.get(task_id)
        if task is not None and task.deleted_at is not None and not include_deleted:
            return None
        return task

    async def add(self, task: Task) -> Task:
        task.id = self._next_id
        self._next_id += 1
        now = datetime(2026, 1, 1, 12, 0, 0)
        task.created_at = now
        task.updated_at = now
        self._tasks[task.id] = task
        return task

    async def update(self, task: Task) -> Task:
        task.updated_at = datetime(2026, 1, 2, 12, 0, 0)
        self._tasks[task.id] = task
        return task

    async def delete(self, task: Task, permanent: bool = False) -> None:
        if permanent:
            self._tasks.pop(task.id, None)
        elif task.deleted_at is None:
            task.deleted_at = datetime(2026, 1, 2, 12, 0, 0)

    async def restore(self, task: Task) -> None:
        task.deleted_at = None
        task.updated_at = datetime(2026, 1, 3, 12, 0, 0)


@pytest.fixture
def fake_repo() -> FakeTaskRepository:
    return FakeTaskRepository()


@pytest_asyncio.fixture
async def client(fake_repo: FakeTaskRepository):
    app.dependency_overrides[get_task_repository] = lambda: fake_repo
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
