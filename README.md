# Module 01: AI Champions Kick-off & Enterprise Context — Hands-On Lab

## Overview

Module 01 sets the frame for the whole programme: the shift **from isolated AI
experimentation to disciplined enterprise adoption**, the AI Champion role by
function, the risks of unmanaged AI usage, the end-to-end AI-assisted
engineering lifecycle, and Agent Prism as the monitoring lens.

This lab makes that concrete. You stand up the **Engineering Task Board** — a
small full-stack app (PostgreSQL + a React board + your choice of a .NET,
Python, or Java/Spring Boot backend, all behind the same API contract) — and
use it to run the Module 01 workshop against real code: map the
current-state workflow, identify greenfield vs brownfield work, and record the
**baseline success metrics** every later module is measured against.

It is also the application you keep building. Module 02 layers GitHub Copilot's
enterprise customization (instructions, prompts, agents, skills, MCP, coding
agent, code review) onto it, Module 03 adds search and analytics, Module 04
rebuilds the next feature spec-first — all on this codebase.

## Concepts Covered

Traced from `presentations/Module01_AI_Champions_Kickoff_Enterprise_Context.pdf`:

| Concept (from the deck) | Where it shows up in this lab |
|-------------------------|-------------------------------|
| Isolated experimentation → disciplined adoption | Exercise 2 contrasts an ad-hoc "prompt-only" change with a context-first, tested one |
| The AI Champion role, by function | [Role lenses](#role-lenses) — each role inspects a different part of the codebase |
| Business & engineering risks of unmanaged AI usage | Exercise 3 risk note: which risks a change to this code could trigger, and how tests guard them |
| The AI-assisted software engineering lifecycle (end to end) | The [layered architecture](usecase.md#architecture) is the "Copilot Foundations → … → Observe" pipeline in miniature |
| Agent Prism: the monitoring lens | [Metrics worksheet](#baseline-metrics-worksheet) records traces of your own workflow: cycle time, quality, review effort, token/AI cost |
| Workshop: current-state vs target-state workflow | Exercise 1 produces both, grounded in a real change to this app |

## Prerequisites

- [Prerequisites — tools & versions](../setup/prerequisites.md) (macOS, Linux, and Windows)
- [PostgreSQL setup](../setup/database-setup.md)
- Backend setup — you only need one:
  [.NET](../setup/dotnet-setup.md) · [Python](../setup/python-setup.md) · [Java](../setup/java-setup.md)

This is the first module — there is no earlier lab to complete.

> **Shells.** Command blocks below are given for **macOS / Linux (bash/zsh)**
> and **Windows (PowerShell)**. Run the pair that matches your machine; WSL2
> users follow the macOS / Linux side.

## Use Case

The **Engineering Task Board**: a Kanban-style task list with three columns
(To Do / In Progress / Done), full CRUD, and status filtering. Full detail,
data model, and API contract are in **[usecase.md](usecase.md)**.

## Configuration

**macOS / Linux**

```bash
cd labs/module-01
cp .env.example .env        # then fill in the placeholder passwords
```

**Windows (PowerShell)**

```powershell
cd labs/module-01
Copy-Item .env.example .env  # then fill in the placeholder passwords
```

`.env` is git-ignored. Making the copy and filling it in yourself is part of
the lesson — no credentials live in source. The backends read their config
from environment variables (set them in your shell, or use a tool like
`direnv` / `dotenv`); `.env` is your reference copy of what to set.

| Variable | Used by | Notes |
|----------|---------|-------|
| `ConnectionStrings__DefaultConnection` | .NET backend | ADO-style connection string |
| `DATABASE_URL` | Python backend | SQLAlchemy async URL (`postgresql+asyncpg://…`) |
| `SPRING_DATASOURCE_URL` / `_USERNAME` / `_PASSWORD` | Java backend | JDBC URL + credentials (Spring binds these automatically) |
| `FRONTEND_ORIGIN` | Python & Java backends | CORS allow-list (defaults to the Vite dev server) |
| `VITE_API_BASE_URL` | frontend | `http://localhost:8000` (Python), `http://localhost:5088` (.NET), or `http://localhost:8080` (Java) |

## Data Model

```sql
CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    status      VARCHAR(50) NOT NULL DEFAULT 'todo'
                CHECK (status IN ('todo', 'in-progress', 'done')),
    assignee    VARCHAR(100),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

`database/schema.sql` is authoritative. No backend creates or migrates schema
— no EF migrations, no `create_all()`, `spring.jpa.hibernate.ddl-auto=none`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks (optional `?status=` filter) |
| GET | `/api/tasks/{id}` | Get a single task |
| POST | `/api/tasks` | Create a task |
| PUT | `/api/tasks/{id}` | Update a task |
| DELETE | `/api/tasks/{id}` | Delete a task |
| GET | `/health` | Liveness check |

Error contract: `404` for a missing id, `422` for a missing title or an
unknown status. See [usecase.md](usecase.md#api-contract).

## Running the Lab

All commands are run from `labs/module-01/` (or the noted sub-folder). Full
platform detail for each piece is in the [setup guides](../setup/).

### 1. Database

Start PostgreSQL (local install or Docker — see
[database-setup.md](../setup/database-setup.md)), then apply the schema.

**With a local `psql` (any platform)**

```
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/schema.sql
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/seed.sql
```

**Docker container, macOS / Linux**

```bash
docker exec -i taskboard-db psql -U postgres -d taskboard < database/schema.sql
docker exec -i taskboard-db psql -U postgres -d taskboard < database/seed.sql
```

**Docker container, Windows (PowerShell)**

```powershell
Get-Content database/schema.sql | docker exec -i taskboard-db psql -U postgres -d taskboard
Get-Content database/seed.sql   | docker exec -i taskboard-db psql -U postgres -d taskboard
```

### 2. Pick ONE backend

Each exposes the same API. Interactive docs: **.NET** → `/swagger`,
**Python** → `/docs`, **Java** → `/swagger-ui.html`.

Each `cd` is from `labs/module-01/`. Steps that are identical on every OS are
shown once; only the environment-variable line changes between shells.

#### Option A — Python (FastAPI), port 8000

```bash
cd backend-python
python3 -m venv .venv && source .venv/bin/activate   # Windows: python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set the database URL, then start:

```bash
# macOS / Linux
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```
```powershell
# Windows (PowerShell)
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```
```
uvicorn main:app --reload
```

#### Option B — .NET (ASP.NET Core), port 5088

```bash
cd backend-dotnet
```
```bash
# macOS / Linux
export ConnectionStrings__DefaultConnection="Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
```
```powershell
# Windows (PowerShell)
$env:ConnectionStrings__DefaultConnection = "Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
```
```
dotnet run --project src/TaskBoard.Api
```

#### Option C — Java (Spring Boot), port 8080

```bash
cd backend-java
```
```bash
# macOS / Linux
export SPRING_DATASOURCE_URL="jdbc:postgresql://localhost:5432/taskboard"
export SPRING_DATASOURCE_USERNAME=postgres
export SPRING_DATASOURCE_PASSWORD=postgres
./mvnw spring-boot:run
```
```powershell
# Windows (PowerShell)
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://localhost:5432/taskboard"
$env:SPRING_DATASOURCE_USERNAME = "postgres"
$env:SPRING_DATASOURCE_PASSWORD = "postgres"
.\mvnw.cmd spring-boot:run
```

(`./mvnw` / `mvnw.cmd` is the bundled Maven wrapper — use `mvn` directly if
you have it installed.)

### 3. Frontend

```
cd frontend
npm install
npm run dev            # http://localhost:5173
```

Point it at the backend you started by creating `frontend/.env.local`:

**macOS / Linux**

```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

**Windows (PowerShell)** — force UTF-8 so Vite reads it correctly:

```powershell
Set-Content -Encoding utf8 .env.local "VITE_API_BASE_URL=http://localhost:8000"
```

Use `:5088` for .NET or `:8080` for Java instead of `:8000`.

## Exercises

The exercises run the Module 01 workshop on this codebase. Copilot is optional
in Module 01 — if it is enabled, use it and record the extra metrics; if not,
do the same steps by hand and note where AI *would* have helped.

### Exercise 1 — Guided: run it, read it, map the current state

1. Bring up the database, one backend, and the frontend (steps above). Confirm
   the board shows the six seeded tasks and that you can create, move, and
   delete a task.
2. Run the tests for the backend you chose and for the frontend
   (see [Verification](#verification)). Note how long a full run takes.
3. Walk the codebase against [the layered architecture](usecase.md#architecture).
   For **`POST /api/tasks`**, trace the call from the React `TaskForm` all the
   way to the `tasks` table and back. Write down every file it passes through.
4. Fill in the **current-state** column of the
   [workflow map](#current-state-vs-target-state) for the change you will make
   in Exercise 2: *"add a way to see the most recently updated tasks first."*
5. Fill in the starting values of the [baseline metrics worksheet](#baseline-metrics-worksheet).

### Exercise 2 — Semi-guided: make one change, two ways

Goal: add **sorting** to the task list — `GET /api/tasks?sort=-updated_at`
returns newest-updated first (default stays id-ascending), with a matching
control in the UI.

Do it **twice** and compare:

- **Pass A — prompt-only / ad hoc.** Make the change with the smallest possible
  context: no reading of neighbouring code, one-line request, accept the first
  result. Run the tests.
- **Pass B — context-first.** Start from `usecase.md`, the existing
  repository/service/router layering, and the existing tests. Decide where the
  sort belongs (repository query, not the controller), add or update a test
  first, then implement. Run the tests.

For each pass record: wall-clock time, number of test files touched, whether
the tests passed on the first try, and — if using Copilot — rough prompt/token
count. Put the numbers in the worksheet.

> This is the deck's core contrast in miniature: *inconsistent results when
> teams rely on prompts alone* vs *specification-led, validated change*.

### Exercise 3 — Independent challenge

1. **Port the change.** Implement the same `sort` feature in a second backend
   (a different language from your Pass B). Make both return byte-identical
   JSON for the same request.
2. **Write a risk note (½ page).** From the deck's *Business & Engineering
   Risks* slide, pick the two risks your change is closest to (e.g. *AI-
   generated changes disrupting existing patterns*, *manual/inconsistent
   review*). For each: how could this specific change have gone wrong, and
   which test would have caught it?
3. **Draft the target-state workflow.** Complete the target column of the
   [workflow map](#current-state-vs-target-state): what should the disciplined
   version of "add a small API + UI change" look like by the end of the
   programme (spec, context, tests-first, PR gate, observability)?

## Current-state vs target-state

Fill this in during Exercises 1 and 3.

| Workflow stage | Current state (today) | Target state (end of programme) |
|----------------|-----------------------|---------------------------------|
| Framing the change | | |
| Gathering context for the AI | | |
| Implementation | | |
| Testing | | |
| Review / PR | | |
| Observability (traces, cost, quality) | | |

## Baseline metrics worksheet

The six measures the deck names. Capture them for the Exercise 2 change so
later modules have a baseline to improve on.

| Metric | Pass A (prompt-only) | Pass B (context-first) |
|--------|----------------------|------------------------|
| Implementation cycle time (min) | | |
| Quality / regression risk (tests passed first try? bugs found after?) | | |
| Review effort (min to review the diff; # review comments) | | |
| Testing effort (# test files touched; min to write) | | |
| Token usage (approx, if using Copilot) | | |
| AI cost signal (prompts / retries needed) | | |

## Role lenses

Same lab, different focus depending on your function (from the deck's *AI
Champion Role, By Function* slide):

- **Architects / Eng leads** — audit the layering: does business logic ever
  leak into a controller or a repository? Is the `tasks` schema owned in
  exactly one place?
- **Developers / Testers** — you own Exercise 2 and 3 in depth. Drive the
  tests-first loop; make the backends agree byte-for-byte on the same request.
- **DevOps / SRE** — sketch what a CI job for this repo runs (build, test,
  schema-load check) and where Agent Prism-style telemetry would attach.
- **Product / Program / Design** — write the one-paragraph spec for the
  Exercise 2 change *before* anyone codes it; check the UI change against it.

## Verification

Run each block from its folder under `labs/module-01/`. The commands
themselves are identical on every OS — only shell grouping differs, so they
are shown one folder at a time.

```
# .NET backend  — in backend-dotnet/
dotnet build
dotnet test

# Python backend  — in backend-python/ (virtualenv activated)
pip install -r requirements.txt
pytest

# Java backend  — in backend-java/
./mvnw -B test            # Windows: .\mvnw.cmd -B test

# Frontend  — in frontend/
npm install
npm run build
npm test -- --run
```

Schema loads into a clean database (Docker example):

**macOS / Linux**

```bash
docker exec -i taskboard-db psql -U postgres -d postgres -c "CREATE DATABASE taskboard_check;"
docker exec -i taskboard-db psql -U postgres -d taskboard_check < database/schema.sql
docker exec -i taskboard-db psql -U postgres -d taskboard_check < database/seed.sql
docker exec -i taskboard-db psql -U postgres -d postgres -c "DROP DATABASE taskboard_check;"
```

**Windows (PowerShell)**

```powershell
docker exec -i taskboard-db psql -U postgres -d postgres -c "CREATE DATABASE taskboard_check;"
Get-Content database/schema.sql | docker exec -i taskboard-db psql -U postgres -d taskboard_check
Get-Content database/seed.sql   | docker exec -i taskboard-db psql -U postgres -d taskboard_check
docker exec -i taskboard-db psql -U postgres -d postgres -c "DROP DATABASE taskboard_check;"
```

- [ ] `dotnet build` and `dotnet test` pass (14 tests)
- [ ] `pytest` passes (19 tests)
- [ ] `mvn test` passes (16 tests)
- [ ] `npm run build` succeeds and `npm test -- --run` passes (12 tests)
- [ ] `schema.sql` + `seed.sql` load into a clean database without error
- [ ] The board renders the seeded tasks and CRUD works against a live backend
- [ ] `.env` is created from `.env.example`; no secret is committed

## Next Steps

Proceed to [Module 02](../module-02/README.md). It keeps **this** codebase as
the base — no new app — and layers GitHub Copilot's advanced enterprise
capabilities on top of it through guided exercises: repository and path-specific
custom instructions, reusable prompt files, custom chat modes / agents, agent
skills, agent mode with MCP tools, the Copilot coding agent on GitHub.com,
automated Copilot code review, and the Copilot CLI. Every command is given for
both macOS / Linux and Windows.
