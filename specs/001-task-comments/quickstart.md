# Quickstart: Validate Task Comments (Python backend + frontend)

## Prerequisites

- Postgres running with `database/schema.sql` (including the new
  `task_comments` table from [data-model.md](./data-model.md)) applied.
- `backend-python/` deps installed (`pip install -r requirements.txt`).
- `frontend/` deps installed (`npm install`).

## Apply schema

```bash
psql -U postgres -d taskboard -f database/schema.sql
```

## Run the backend

```bash
cd backend-python
uvicorn main:app --reload
```

## Run the frontend

```bash
cd frontend
npm run dev
```

## Validation scenarios (map to spec User Stories)

1. **Comment count badge (US1)**
   - Create a task via the board.
   - `POST /api/tasks/{id}/comments` with a valid author/text twice.
   - Reload the board: the task's card shows a comment indicator with
     count 2. A task with no comments shows no indicator.

2. **Read & post a thread (US2)**
   - Expand the comment thread on a task with existing comments; confirm
     they render oldest-first with author and timestamp.
   - Submit the inline form with an author and text; confirm the new
     comment appears at the bottom immediately (no full page reload).
   - Attempt to submit with a blank author or blank/whitespace-only text;
     confirm the request is rejected (422) and nothing is added.

3. **Delete a comment (US3)**
   - Delete an existing comment from the thread; confirm it disappears
     and the board's comment count for that task decreases by one.

4. **Cascade delete (Edge Case)**
   - Delete a task that has comments; confirm subsequent
     `GET /api/tasks/{id}/comments` for that id returns 404 (task gone),
     and no orphaned rows remain in `task_comments` (verify via `psql`
     if desired).

## Automated verification

- Backend: `cd backend-python && pytest`
- Frontend: `cd frontend && npm test -- --run`

See [contracts/comments-api.md](./contracts/comments-api.md) for exact
request/response shapes and [data-model.md](./data-model.md) for the
schema.
