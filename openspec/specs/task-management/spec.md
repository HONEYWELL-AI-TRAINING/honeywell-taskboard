# Task Management

## Purpose

Describe the current behavior of the Python task API, including its task
operations and the current routing behavior for stats and task comments.

## Requirements

### Requirement: List tasks with an optional status filter

The API SHALL return tasks from `GET /api/tasks` as a JSON array ordered by
ascending task ID. When a valid `status` query parameter is supplied, the API
SHALL return only tasks with that status. Valid statuses are `todo`,
`in-progress`, and `done`. A successful request SHALL return HTTP 200; an
invalid status SHALL return HTTP 422.

#### Scenario: List all tasks

- WHEN a client sends `GET /api/tasks` without a status parameter
- THEN the API returns HTTP 200 with all tasks ordered by ascending ID

#### Scenario: List tasks for a status

- WHEN a client sends `GET /api/tasks?status=done`
- THEN the API returns HTTP 200 with only `done` tasks, ordered by ascending ID

#### Scenario: Reject an unknown status

- WHEN a client sends `GET /api/tasks?status=archived`
- THEN the API returns HTTP 422

### Requirement: Get one task

The API SHALL return a task from `GET /api/tasks/{task_id}` with HTTP 200 when
that task exists. The response includes `id`, `title`, `description`, `status`,
`assignee`, `created_at`, and `updated_at`. When the task does not exist, the
API SHALL return HTTP 404.

#### Scenario: Get an existing task

- WHEN a client sends `GET /api/tasks/{task_id}` for an existing task
- THEN the API returns HTTP 200 with that task

#### Scenario: Get a missing task

- WHEN a client sends `GET /api/tasks/{task_id}` for a nonexistent task
- THEN the API returns HTTP 404

### Requirement: Create a task

The API SHALL create a task through `POST /api/tasks` and return HTTP 201 with
the created task. `title` is required and must contain 1 to 255 characters;
`description` is optional; `assignee` is optional and limited to 100
characters; and `status` defaults to `todo` and accepts `todo`, `in-progress`,
or `done`. Invalid request data SHALL return HTTP 422.

#### Scenario: Create a task with the default status

- WHEN a client sends a valid `POST /api/tasks` body with a title and no status
- THEN the API returns HTTP 201 with the created task whose status is `todo`

#### Scenario: Reject invalid create data

- WHEN a client sends `POST /api/tasks` without a title or with an invalid status
- THEN the API returns HTTP 422

### Requirement: Update a task

The API SHALL update a task through `PUT /api/tasks/{task_id}` and return HTTP
200 with the updated task. The body requires a `title` of 1 to 255 characters;
`description` is optional; `assignee` is optional and limited to 100
characters; and `status` defaults to `todo` and accepts `todo`, `in-progress`,
or `done`. The API SHALL return HTTP 404 when the task does not exist and HTTP
422 when the request body or status is invalid.

#### Scenario: Update an existing task

- WHEN a client sends a valid `PUT /api/tasks/{task_id}` body for an existing task
- THEN the API returns HTTP 200 with the updated task

#### Scenario: Update a missing task

- WHEN a client sends `PUT /api/tasks/{task_id}` for a nonexistent task with a valid body
- THEN the API returns HTTP 404

#### Scenario: Reject invalid update data

- WHEN a client sends `PUT /api/tasks/{task_id}` with invalid request data
- THEN the API returns HTTP 422

### Requirement: Delete a task

The API SHALL physically delete an existing task through
`DELETE /api/tasks/{task_id}` and return HTTP 204 with no response body. It
SHALL return HTTP 404 when the task does not exist. After deletion, a GET for
that task returns HTTP 404. The Python API has no task-comment model, table,
repository, or comment routes, so deleting a task removes the task row and
there are no task comments in this implementation to cascade or preserve.

#### Scenario: Delete an existing task

- WHEN a client sends `DELETE /api/tasks/{task_id}` for an existing task
- THEN the API physically deletes the task and returns HTTP 204 with no body
- AND a subsequent `GET /api/tasks/{task_id}` returns HTTP 404

#### Scenario: Delete a missing task

- WHEN a client sends `DELETE /api/tasks/{task_id}` for a nonexistent task
- THEN the API returns HTTP 404

### Requirement: Request task statistics

The Python API SHALL return HTTP 422 for `GET /api/tasks/stats` because it has
no stats route and the path is interpreted as the integer `task_id` parameter
of `GET /api/tasks/{task_id}`. The API has a separate `GET /api/tasks/count`
route, which returns HTTP 200 with a `count` field and accepts the same
optional status filter as task listing.

#### Scenario: Request the unimplemented stats path

- WHEN a client sends `GET /api/tasks/stats`
- THEN the API returns HTTP 422 because `stats` cannot be parsed as an integer task ID

#### Scenario: Request the implemented task count

- WHEN a client sends `GET /api/tasks/count` with no status, or with a valid status
- THEN the API returns HTTP 200 with the matching task count

#### Scenario: Reject an invalid task-count status

- WHEN a client sends `GET /api/tasks/count?status=archived`
- THEN the API returns HTTP 422

### Requirement: List and post task comments

The Python API SHALL return HTTP 404 for requests to list or post comments at
`/api/tasks/{task_id}/comments`, because no comment endpoints are registered.
The current implementation has no task-comment persistence or response
behavior.

#### Scenario: List comments for a task

- WHEN a client sends `GET /api/tasks/{task_id}/comments`
- THEN the API returns HTTP 404

#### Scenario: Post a comment to a task

- WHEN a client sends `POST /api/tasks/{task_id}/comments`
- THEN the API returns HTTP 404
