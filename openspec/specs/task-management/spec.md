# Task Management

## Purpose

Describe the current behavior of the Python task API, including its task
operations and the current routing behavior for stats and task comments.

## Requirements

### Requirement: List tasks with an optional status filter

The API SHALL return tasks from `GET /api/tasks` as a JSON array ordered by
ascending task ID. By default it SHALL include only active tasks. With
`deleted=true`, it SHALL return only deleted tasks. A valid `status` filter
SHALL work with either selection. Valid statuses are `todo`, `in-progress`,
and `done`; invalid query values SHALL return HTTP 422.

#### Scenario: List all tasks

- WHEN a client sends `GET /api/tasks` without `deleted=true`
- THEN the API returns HTTP 200 with only active tasks ordered by ascending ID

#### Scenario: List deleted tasks

- WHEN a client sends `GET /api/tasks?deleted=true`
- THEN the API returns HTTP 200 with only deleted tasks ordered by ascending ID

#### Scenario: List active tasks for a status

- WHEN a client sends `GET /api/tasks?status=done`
- THEN the API returns HTTP 200 with only active `done` tasks ordered by ascending ID

#### Scenario: List tasks for a status

- WHEN a client sends `GET /api/tasks?deleted=true&status=done`
- THEN the API returns HTTP 200 with only deleted `done` tasks ordered by ascending ID

#### Scenario: Reject an unknown status

- WHEN a client sends `GET /api/tasks?status=archived`
- THEN the API returns HTTP 422

### Requirement: Get one task

The API SHALL return an active task from `GET /api/tasks/{task_id}` with HTTP
200. Deleted tasks SHALL be hidden by default and return HTTP 404. With
`includeDeleted=true`, the API SHALL return either an active or deleted task.
An unknown task SHALL return HTTP 404; an invalid query value SHALL return
HTTP 422. The response includes `id`, `title`, `description`, `status`,
`assignee`, `created_at`, and `updated_at`.

#### Scenario: Get an existing task

- WHEN a client requests an existing active task by ID
- THEN the API returns HTTP 200 with that task

#### Scenario: Hide a deleted task by default

- WHEN a client requests a deleted task without `includeDeleted=true`
- THEN the API returns HTTP 404

#### Scenario: Get a deleted task explicitly

- WHEN a client requests an existing deleted task with `includeDeleted=true`
- THEN the API returns HTTP 200 with that task

#### Scenario: Get a missing task

- WHEN a client requests an ID with no stored task
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
or `done`. The API SHALL return HTTP 404 for a missing or deleted task and HTTP
422 when the request body or status is invalid.

#### Scenario: Update an existing task

- WHEN a client sends a valid `PUT /api/tasks/{task_id}` body for an existing task
- THEN the API returns HTTP 200 with the updated task

#### Scenario: Update a missing or deleted task

- WHEN a client sends an otherwise valid update for a missing or deleted task
- THEN the API returns HTTP 404

#### Scenario: Reject invalid update data

- WHEN a client sends `PUT /api/tasks/{task_id}` with invalid request data
- THEN the API returns HTTP 422

### Requirement: Delete a task

`DELETE /api/tasks/{task_id}` SHALL set `deleted_at` for an existing task
without physically removing it and SHALL return HTTP 204 with no body. A
missing task SHALL return HTTP 404. Repeating soft deletion SHALL remain
successful and SHALL NOT erase the stored task. If task comments exist, soft
deletion SHALL retain them, and they SHALL remain available after restore.

#### Scenario: Soft-delete an existing task

- WHEN a client sends `DELETE /api/tasks/{task_id}` without `permanent=true` for an existing task
- THEN the API sets its `deleted_at` timestamp and returns HTTP 204 with no body
- AND normal task reads no longer return that task

#### Scenario: Repeat soft deletion

- WHEN a client soft-deletes a task that is already deleted
- THEN the API returns HTTP 204 and retains the task row

#### Scenario: Delete a missing task

- WHEN a client soft-deletes an ID with no stored task
- THEN the API returns HTTP 404

### Requirement: Request task statistics

The Python API SHALL return HTTP 422 for `GET /api/tasks/stats` because it has
no stats route and the path is interpreted as the integer `task_id` parameter
of `GET /api/tasks/{task_id}`. Its separate `GET /api/tasks/count` route SHALL
return HTTP 200 with a `count` field counting active tasks only, optionally
filtered by a valid status; an invalid status SHALL return HTTP 422.

#### Scenario: Request the unimplemented stats path

- WHEN a client sends `GET /api/tasks/stats`
- THEN the API returns HTTP 422 because `stats` cannot be parsed as an integer task ID

#### Scenario: Request the implemented active task count

- WHEN a client requests `GET /api/tasks/count`
- THEN the API returns HTTP 200 with the number of active tasks

#### Scenario: Count active tasks by status

- WHEN a client requests `GET /api/tasks/count?status=done`
- THEN the API returns HTTP 200 with the number of active `done` tasks

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

### Requirement: Restore a deleted task

The API SHALL restore a deleted task through `POST /api/tasks/{task_id}/restore`
by clearing `deleted_at` and return HTTP 204 with no body. A missing or active
task SHALL return HTTP 404.

#### Scenario: Restore a deleted task

- WHEN a client restores an existing deleted task
- THEN the API clears `deleted_at` and returns HTTP 204
- AND the task is visible in normal task reads again

#### Scenario: Restore a missing or active task

- WHEN a client restores an ID that is missing or already active
- THEN the API returns HTTP 404

### Requirement: Permanently delete a task

The API SHALL physically remove an existing task when a client sends
`DELETE /api/tasks/{task_id}?permanent=true` and return HTTP 204 with no body.
It SHALL return HTTP 404 when no task with that ID exists. If task comments
exist, the permanent deletion path SHALL be the only path that cascades their
deletion.

#### Scenario: Permanently delete an existing task

- WHEN a client sends `DELETE /api/tasks/{task_id}?permanent=true` for an existing active or deleted task
- THEN the API physically removes the task and returns HTTP 204

#### Scenario: Permanently delete a missing task

- WHEN a client sends permanent delete for an ID with no stored task
- THEN the API returns HTTP 404
