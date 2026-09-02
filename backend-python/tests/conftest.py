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
from models.comment import Comment
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
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    async def list(self, status: str | None = None) -> Sequence[Task]:
        rows = sorted(self._tasks.values(), key=lambda t: t.id)
        return [t for t in rows if status is None or t.status == status]

    async def count(self, status: str | None = None) -> int:
        return len(await self.list(status))

    async def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

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

    async def delete(self, task: Task) -> None:
        self._tasks.pop(task.id, None)


class FakeCommentRepository:
    """List-backed stand-in for CommentRepository with the same async surface."""

    def __init__(self) -> None:
        self._comments: dict[int, Comment] = {}
        self._next_id = 1

    def seed(self, task_id: int, **kwargs) -> Comment:
        comment = Comment(
            id=self._next_id,
            task_id=task_id,
            author=kwargs.get("author", "Sam"),
            text=kwargs.get("text", "Seed comment"),
            created_at=kwargs.get("created_at", datetime(2026, 1, 1, 12, 0, 0)),
        )
        self._comments[comment.id] = comment
        self._next_id += 1
        return comment

    async def list(self, task_id: int) -> Sequence[Comment]:
        return [
            comment
            for comment in sorted(self._comments.values(), key=lambda item: item.id)
            if comment.task_id == task_id
        ]

    async def count(self, task_id: int) -> int:
        return len(await self.list(task_id))

    async def get(self, task_id: int, comment_id: int) -> Comment | None:
        comment = self._comments.get(comment_id)
        return comment if comment and comment.task_id == task_id else None

    async def add(self, comment: Comment) -> Comment:
        comment.id = self._next_id
        comment.created_at = datetime(2026, 1, 1, 12, 0, 0)
        self._comments[comment.id] = comment
        self._next_id += 1
        return comment

    async def delete(self, comment: Comment) -> None:
        self._comments.pop(comment.id, None)


@pytest.fixture
def fake_repo() -> FakeTaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def fake_comment_repo() -> FakeCommentRepository:
    return FakeCommentRepository()


@pytest_asyncio.fixture
async def client(fake_repo: FakeTaskRepository, fake_comment_repo: FakeCommentRepository):
    from dependencies import get_comment_repository

    app.dependency_overrides[get_task_repository] = lambda: fake_repo
    app.dependency_overrides[get_comment_repository] = lambda: fake_comment_repo
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
