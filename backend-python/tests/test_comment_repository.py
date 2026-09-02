"""Unit tests for CommentRepository against a mocked async session."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.comment import Comment
from repositories.comment_repository import CommentRepository


def comment(comment_id: int, task_id: int = 1) -> Comment:
    return Comment(
        id=comment_id,
        task_id=task_id,
        author="Sam",
        text="Review this",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def session() -> MagicMock:
    mocked_session = MagicMock()
    mocked_session.execute = AsyncMock()
    mocked_session.flush = AsyncMock()
    mocked_session.refresh = AsyncMock()
    mocked_session.delete = AsyncMock()
    return mocked_session


async def test_list_orders_comments_oldest_first(session):
    first = comment(1)
    second = comment(2)
    result = MagicMock()
    result.scalars.return_value.all.return_value = [first, second]
    session.execute.return_value = result

    comments = await CommentRepository(session).list(1)

    assert comments == [first, second]
    assert "ORDER BY task_comments.id" in str(session.execute.call_args.args[0])


async def test_count_returns_comments_for_task(session):
    result = MagicMock()
    result.scalar_one.return_value = 3
    session.execute.return_value = result

    assert await CommentRepository(session).count(1) == 3
    assert "task_comments.task_id" in str(session.execute.call_args.args[0])


async def test_get_scopes_comment_to_task(session):
    expected = comment(7, task_id=2)
    result = MagicMock()
    result.scalar_one_or_none.return_value = expected
    session.execute.return_value = result

    assert await CommentRepository(session).get(2, 7) == expected
    statement = str(session.execute.call_args.args[0])
    assert "task_comments.task_id" in statement
    assert "task_comments.id" in statement


async def test_add_flushes_and_refreshes_comment(session):
    created = comment(1)

    assert await CommentRepository(session).add(created) == created
    session.add.assert_called_once_with(created)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(created)


async def test_delete_flushes_scoped_comment(session):
    existing = comment(1)

    await CommentRepository(session).delete(existing)

    session.delete.assert_awaited_once_with(existing)
    session.flush.assert_awaited_once()