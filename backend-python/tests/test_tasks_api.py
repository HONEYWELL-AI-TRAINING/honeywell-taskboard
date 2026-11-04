"""End-to-end tests for every /api/tasks endpoint (via the ASGI app)."""
from datetime import datetime


def mark_deleted(task):
    task.deleted_at = datetime(2026, 1, 2, 12, 0, 0)


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_list_empty(client):
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_filters_by_status(client, fake_repo):
    fake_repo.seed(title="A", status="todo")
    fake_repo.seed(title="B", status="done")
    fake_repo.seed(title="C", status="done")

    resp = await client.get("/api/tasks", params={"status": "done"})
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["B", "C"]


async def test_list_excludes_deleted_tasks_by_default(client, fake_repo):
    active = fake_repo.seed(title="Active")
    deleted = fake_repo.seed(title="Deleted")
    mark_deleted(deleted)

    resp = await client.get("/api/tasks")

    assert resp.status_code == 200
    assert [task["id"] for task in resp.json()] == [active.id]


async def test_list_deleted_tasks_with_status_filter(client, fake_repo):
    fake_repo.seed(title="Active done", status="done")
    deleted_done = fake_repo.seed(title="Deleted done", status="done")
    mark_deleted(deleted_done)
    deleted_todo = fake_repo.seed(title="Deleted todo", status="todo")
    mark_deleted(deleted_todo)

    resp = await client.get("/api/tasks", params={"deleted": "true", "status": "done"})

    assert resp.status_code == 200
    assert [task["id"] for task in resp.json()] == [deleted_done.id]


async def test_list_rejects_invalid_deleted_filter(client):
    resp = await client.get("/api/tasks", params={"deleted": "sometimes"})
    assert resp.status_code == 422


async def test_list_rejects_unknown_status(client):
    resp = await client.get("/api/tasks", params={"status": "archived"})
    assert resp.status_code == 422


async def test_get_single_task(client, fake_repo):
    task = fake_repo.seed(title="Wire endpoint")
    resp = await client.get(f"/api/tasks/{task.id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Wire endpoint"


async def test_get_missing_task_returns_404(client):
    resp = await client.get("/api/tasks/999")
    assert resp.status_code == 404


async def test_get_deleted_task_is_hidden_by_default(client, fake_repo):
    task = fake_repo.seed(title="Deleted")
    mark_deleted(task)

    resp = await client.get(f"/api/tasks/{task.id}")

    assert resp.status_code == 404


async def test_get_deleted_task_when_explicitly_included(client, fake_repo):
    task = fake_repo.seed(title="Deleted")
    mark_deleted(task)

    resp = await client.get(f"/api/tasks/{task.id}", params={"includeDeleted": "true"})

    assert resp.status_code == 200
    assert resp.json()["id"] == task.id


async def test_get_rejects_invalid_include_deleted_filter(client):
    resp = await client.get("/api/tasks/1", params={"includeDeleted": "sometimes"})
    assert resp.status_code == 422


async def test_create_task(client):
    resp = await client.post(
        "/api/tasks",
        json={"title": "New task", "description": "desc", "assignee": "Sam"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["status"] == "todo"
    assert body["assignee"] == "Sam"


async def test_create_task_requires_title(client):
    resp = await client.post("/api/tasks", json={"description": "no title"})
    assert resp.status_code == 422


async def test_create_task_rejects_bad_status(client):
    resp = await client.post("/api/tasks", json={"title": "x", "status": "nope"})
    assert resp.status_code == 422


async def test_update_task(client, fake_repo):
    task = fake_repo.seed(title="Old", status="todo")
    resp = await client.put(
        f"/api/tasks/{task.id}",
        json={"title": "Updated", "status": "in-progress"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Updated"
    assert body["status"] == "in-progress"


async def test_update_missing_task_returns_404(client):
    resp = await client.put("/api/tasks/999", json={"title": "x", "status": "todo"})
    assert resp.status_code == 404


async def test_update_deleted_task_returns_404(client, fake_repo):
    task = fake_repo.seed(title="Deleted")
    mark_deleted(task)

    resp = await client.put(
        f"/api/tasks/{task.id}",
        json={"title": "Changed", "status": "todo"},
    )

    assert resp.status_code == 404


async def test_delete_task(client, fake_repo):
    task = fake_repo.seed()
    resp = await client.delete(f"/api/tasks/{task.id}")
    assert resp.status_code == 204

    follow_up = await client.get(f"/api/tasks/{task.id}")
    assert follow_up.status_code == 404
    included = await client.get(f"/api/tasks/{task.id}", params={"includeDeleted": "true"})
    assert included.status_code == 200
    assert included.json()["id"] == task.id

    normal_list = await client.get("/api/tasks")
    deleted_list = await client.get("/api/tasks", params={"deleted": "true"})
    assert task.id not in [item["id"] for item in normal_list.json()]
    assert task.id in [item["id"] for item in deleted_list.json()]


async def test_delete_missing_task_returns_404(client):
    resp = await client.delete("/api/tasks/999")
    assert resp.status_code == 404


async def test_delete_again_returns_204(client, fake_repo):
    task = fake_repo.seed()

    first_delete = await client.delete(f"/api/tasks/{task.id}")
    second_delete = await client.delete(f"/api/tasks/{task.id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 204


async def test_restore_deleted_task(client, fake_repo):
    task = fake_repo.seed(title="Deleted")
    mark_deleted(task)

    resp = await client.post(f"/api/tasks/{task.id}/restore")

    assert resp.status_code == 204
    follow_up = await client.get(f"/api/tasks/{task.id}")
    assert follow_up.status_code == 200


async def test_restore_active_or_missing_task_returns_404(client, fake_repo):
    active = fake_repo.seed(title="Active")

    active_response = await client.post(f"/api/tasks/{active.id}/restore")
    missing_response = await client.post("/api/tasks/999/restore")

    assert active_response.status_code == 404
    assert missing_response.status_code == 404


async def test_permanent_delete_removes_existing_task(client, fake_repo):
    task = fake_repo.seed(title="Permanent")

    resp = await client.delete(f"/api/tasks/{task.id}", params={"permanent": "true"})

    assert resp.status_code == 204
    assert (await client.get(f"/api/tasks/{task.id}", params={"includeDeleted": "true"})).status_code == 404


async def test_permanent_delete_removes_soft_deleted_task(client, fake_repo):
    task = fake_repo.seed(title="Deleted")
    mark_deleted(task)

    resp = await client.delete(f"/api/tasks/{task.id}", params={"permanent": "true"})

    assert resp.status_code == 204
    assert (await client.get(f"/api/tasks/{task.id}", params={"includeDeleted": "true"})).status_code == 404


async def test_permanent_delete_missing_task_returns_404(client):
    resp = await client.delete("/api/tasks/999", params={"permanent": "true"})
    assert resp.status_code == 404


async def test_delete_rejects_invalid_permanent_filter(client):
    resp = await client.delete("/api/tasks/1", params={"permanent": "sometimes"})
    assert resp.status_code == 422


async def test_count_returns_total(client, fake_repo):
    fake_repo.seed(title="A", status="todo")
    fake_repo.seed(title="B", status="done")
    deleted = fake_repo.seed(title="Deleted", status="done")
    mark_deleted(deleted)

    resp = await client.get("/api/tasks/count")
    assert resp.status_code == 200
    assert resp.json() == {"count": 2}


async def test_count_filters_by_status(client, fake_repo):
    fake_repo.seed(title="A", status="todo")
    fake_repo.seed(title="B", status="done")
    deleted = fake_repo.seed(title="Deleted", status="done")
    mark_deleted(deleted)

    resp = await client.get("/api/tasks/count", params={"status": "done"})
    assert resp.status_code == 200
    assert resp.json() == {"count": 1}


async def test_count_rejects_unknown_status(client):
    resp = await client.get("/api/tasks/count", params={"status": "archived"})
    assert resp.status_code == 422
