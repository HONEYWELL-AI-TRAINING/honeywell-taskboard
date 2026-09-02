"""Unit tests for CommentService against in-memory repositories."""
import pytest

from schemas.comment import CommentCreate
from services.comment_service import CommentService
from services.errors import CommentNotFound, TaskNotFound
from tests.conftest import FakeCommentRepository, FakeTaskRepository


@pytest.fixture
def service() -> CommentService:
    return CommentService(FakeCommentRepository(), FakeTaskRepository())


async def test_count_returns_comments_for_existing_task(service):
    task = service._tasks.seed()
    service._comments.seed(task_id=task.id, text="One")
    service._comments.seed(task_id=task.id, text="Two")

    assert await service.count_comments(task.id) == 2


async def test_count_missing_task_raises(service):
    with pytest.raises(TaskNotFound):
        await service.count_comments(999)


async def test_list_returns_comments_oldest_first(service):
    task = service._tasks.seed()
    first = service._comments.seed(task.id, text="First")
    second = service._comments.seed(task.id, text="Second")

    assert await service.list_comments(task.id) == [first, second]


async def test_create_adds_comment_to_existing_task(service):
    task = service._tasks.seed()

    created = await service.create_comment(
        task.id, CommentCreate(author="Priya", text="Please review")
    )

    assert created.author == "Priya"
    assert created.text == "Please review"
    assert await service.count_comments(task.id) == 1


async def test_create_missing_task_raises(service):
    with pytest.raises(TaskNotFound):
        await service.create_comment(999, CommentCreate(author="Priya", text="Note"))


async def test_delete_removes_comment(service):
    task = service._tasks.seed()
    comment = service._comments.seed(task.id)

    await service.delete_comment(task.id, comment.id)

    assert await service.count_comments(task.id) == 0


async def test_delete_missing_comment_raises(service):
    task = service._tasks.seed()

    with pytest.raises(CommentNotFound):
        await service.delete_comment(task.id, 999)


async def test_delete_comment_on_missing_task_raises(service):
    with pytest.raises(TaskNotFound):
        await service.delete_comment(999, 1)