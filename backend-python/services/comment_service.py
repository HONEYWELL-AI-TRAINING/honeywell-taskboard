"""Business logic for task comments."""
from collections.abc import Sequence
from typing import Protocol

from models.comment import Comment
from models.task import Task
from schemas.comment import CommentCreate
from services.errors import CommentNotFound, TaskNotFound


class TaskLookupProtocol(Protocol):
    async def get(self, task_id: int) -> Task | None: ...


class CommentRepositoryProtocol(Protocol):
    async def list(self, task_id: int) -> Sequence[Comment]: ...
    async def count(self, task_id: int) -> int: ...
    async def get(self, task_id: int, comment_id: int) -> Comment | None: ...
    async def add(self, comment: Comment) -> Comment: ...
    async def delete(self, comment: Comment) -> None: ...


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepositoryProtocol,
        task_repository: TaskLookupProtocol,
    ) -> None:
        self._comments = comment_repository
        self._tasks = task_repository

    async def _get_task(self, task_id: int) -> Task:
        task = await self._tasks.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    async def list_comments(self, task_id: int) -> Sequence[Comment]:
        await self._get_task(task_id)
        return await self._comments.list(task_id)

    async def count_comments(self, task_id: int) -> int:
        await self._get_task(task_id)
        return await self._comments.count(task_id)

    async def create_comment(self, task_id: int, data: CommentCreate) -> Comment:
        await self._get_task(task_id)
        return await self._comments.add(
            Comment(task_id=task_id, author=data.author, text=data.text)
        )

    async def delete_comment(self, task_id: int, comment_id: int) -> None:
        await self._get_task(task_id)
        comment = await self._comments.get(task_id, comment_id)
        if comment is None:
            raise CommentNotFound(comment_id)
        await self._comments.delete(comment)