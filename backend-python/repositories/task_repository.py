"""Data-access layer for tasks. Knows about SQLAlchemy; knows nothing about HTTP."""
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _task_query(*, deleted: bool | None) -> Select[tuple[Task]]:
        stmt = select(Task)
        if deleted is True:
            return stmt.where(Task.deleted_at.is_not(None))
        if deleted is False:
            return stmt.where(Task.deleted_at.is_(None))
        return stmt

    async def list(
        self, status: str | None = None, deleted: bool = False
    ) -> Sequence[Task]:
        stmt = self._task_query(deleted=deleted).order_by(Task.id)
        if status:
            stmt = stmt.where(Task.status == status)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count(self, status: str | None = None) -> int:
        tasks = self._task_query(deleted=False)
        if status:
            tasks = tasks.where(Task.status == status)
        stmt = select(func.count()).select_from(tasks.subquery())
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get(self, task_id: int, include_deleted: bool = False) -> Task | None:
        deleted = None if include_deleted else False
        stmt = self._task_query(deleted=deleted).where(Task.id == task_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def add(self, task: Task) -> Task:
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def update(self, task: Task) -> Task:
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def delete(self, task: Task, permanent: bool = False) -> None:
        if permanent:
            await self._session.delete(task)
        elif task.deleted_at is None:
            task.deleted_at = datetime.now()
        await self._session.flush()
        if not permanent:
            await self._session.refresh(task)

    async def restore(self, task: Task) -> None:
        task.deleted_at = None
        await self._session.flush()
        await self._session.refresh(task)
