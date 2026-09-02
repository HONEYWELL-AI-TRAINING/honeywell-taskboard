"""End-to-end tests for /api/tasks/{task_id}/comments endpoints."""
import pytest


async def test_count_returns_comments_for_existing_task(client, fake_repo, fake_comment_repo):
    task = fake_repo.seed()
    fake_comment_repo.seed(task.id, text="One")
    fake_comment_repo.seed(task.id, text="Two")

    response = await client.get(f"/api/tasks/{task.id}/comments/count")

    assert response.status_code == 200
    assert response.json() == {"count": 2}


async def test_count_returns_zero_for_existing_task(client, fake_repo):
    task = fake_repo.seed()

    response = await client.get(f"/api/tasks/{task.id}/comments/count")

    assert response.status_code == 200
    assert response.json() == {"count": 0}


async def test_count_missing_task_returns_404(client):
    response = await client.get("/api/tasks/999/comments/count")

    assert response.status_code == 404


async def test_list_returns_comments_oldest_first(client, fake_repo, fake_comment_repo):
    task = fake_repo.seed()
    fake_comment_repo.seed(task.id, author="Sam", text="First")
    fake_comment_repo.seed(task.id, author="Priya", text="Second")

    response = await client.get(f"/api/tasks/{task.id}/comments")

    assert response.status_code == 200
    assert [comment["text"] for comment in response.json()] == ["First", "Second"]


async def test_post_returns_created_comment(client, fake_repo):
    task = fake_repo.seed()

    response = await client.post(
        f"/api/tasks/{task.id}/comments",
        json={"author": "Priya", "text": "Please review"},
    )

    assert response.status_code == 201
    assert response.json()["author"] == "Priya"
    assert response.json()["text"] == "Please review"


async def test_post_missing_task_returns_404(client):
    response = await client.post(
        "/api/tasks/999/comments", json={"author": "Priya", "text": "Note"}
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"text": "Note"},
        {"author": "Priya", "text": "   "},
        {"author": "P" * 101, "text": "Note"},
        {"author": "Priya", "text": "N" * 501},
    ],
)
async def test_post_rejects_invalid_comment(client, fake_repo, payload):
    task = fake_repo.seed()

    response = await client.post(f"/api/tasks/{task.id}/comments", json=payload)

    assert response.status_code == 422


async def test_delete_removes_comment(client, fake_repo, fake_comment_repo):
    task = fake_repo.seed()
    comment = fake_comment_repo.seed(task.id)

    response = await client.delete(f"/api/tasks/{task.id}/comments/{comment.id}")

    assert response.status_code == 204
    assert await fake_comment_repo.count(task.id) == 0


async def test_delete_missing_comment_returns_404(client, fake_repo):
    task = fake_repo.seed()

    response = await client.delete(f"/api/tasks/{task.id}/comments/999")

    assert response.status_code == 404


async def test_delete_comment_on_missing_task_returns_404(client):
    response = await client.delete("/api/tasks/999/comments/1")

    assert response.status_code == 404