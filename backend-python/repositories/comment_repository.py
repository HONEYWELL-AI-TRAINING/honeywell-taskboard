"""Data-access layer for task comments. Knows about SQLAlchemy, not HTTP."""
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.comment import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, task_id: int) -> Sequence[Comment]:
        stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count(self, task_id: int) -> int:
        stmt = select(func.count()).select_from(Comment).where(Comment.task_id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get(self, task_id: int, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(
            Comment.task_id == task_id, Comment.id == comment_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, comment: Comment) -> Comment:
        self._session.add(comment)
        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self._session.delete(comment)
        await self._session.flush()