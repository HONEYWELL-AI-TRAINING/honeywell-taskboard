AI Champions - Hands-On Lab with Taskboard

## Overview

This lab is about the shift **from isolated AI experimentation to disciplined,
measurable AI-assisted engineering**: knowing where AI helps, where it adds
risk, and how to tell the difference with evidence.

You stand up the **Engineering Task Board** — a small full-stack app
(PostgreSQL + a React board + your choice of a .NET, Python, or Java/Spring
Boot backend, all behind the same API contract) — and use it to practise on
real code: map the current-state workflow, identify greenfield vs brownfield
work, and record **baseline success metrics** you can measure later changes
against.

The app is small enough to read end to end, layered the same way in all three
backends, and covered by tests, so it is a good base to keep extending. The
feature briefs in [`docs/`](docs/) are ready-made follow-on changes.

## Concepts Covered

| Concept | Where it shows up in this lab |
|---------|-------------------------------|
| Isolated experimentation → disciplined adoption | Exercise 2 contrasts an ad-hoc "prompt-only" change with a context-first, tested one |
| The AI Champion role, by function | [Role lenses](#role-lenses) — each role inspects a different part of the codebase |
| Business & engineering risks of unmanaged AI usage | Exercise 3 risk note: which risks a change to this code could trigger, and how tests guard them |
| The AI-assisted engineering workflow, end to end | The exercises take one small change from framing through context, implementation, testing and review; the [layered architecture](docs/base-taskboard.md#architecture) shows where each concern lives |
| Measuring AI-assisted work | The [metrics worksheet](#baseline-metrics-worksheet) records cycle time, quality, review effort and token/AI cost for your own workflow |
| Current-state vs target-state workflow | Exercise 1 produces both, grounded in a real change to this app |

## Prerequisites

This README is self-contained: it installs, configures and runs everything
(database, backend, frontend) on **macOS, Ubuntu and Windows** — every piece
runs directly on your machine.

> **Shells.** Command blocks are given for **macOS / Ubuntu (bash/zsh)** and
> **Windows (PowerShell)**. Run the one that matches your machine. Other Linux
> distributions: use the Ubuntu commands with your package manager. WSL2 users
> follow the Ubuntu side.

### What you need

| Tool | Version | Needed for |
|------|---------|------------|
| Git | any recent | getting the code |
| PostgreSQL | 14+ (16+ recommended) | the database; includes the `psql` client |
| Node.js + npm | 20.19+, 22.13+ or 24+ | the frontend (Vite 8 refuses older Node) |
| **One** backend toolchain: | | |
| — Python | 3.11+ | Option A (FastAPI) |
| — .NET SDK | 8.x | Option B (ASP.NET Core) |
| — JDK | 21 | Option C (Spring Boot). Maven is bundled via `mvnw` — don't install it |

### Install the tools

**macOS** — needs [Homebrew](https://brew.sh)

```bash
brew install git node postgresql@17

# postgresql@17 is "keg-only": put psql on your PATH
echo 'export PATH="$(brew --prefix postgresql@17)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Backend toolchain — install only the one you will use
brew install python                  # Option A — Python
brew install --cask dotnet-sdk@8     # Option B — .NET
brew install --cask temurin@21       # Option C — Java
```

**Ubuntu (22.04 / 24.04)**

```bash
sudo apt update
sudo apt install -y git curl postgresql

# Node.js: Ubuntu's own nodejs package is too old for Vite 8, so use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
# ...open a NEW terminal, then:
nvm install --lts

# Backend toolchain — install only the one you will use
sudo apt install -y python3 python3-venv python3-pip   # Option A — Python
sudo apt install -y dotnet-sdk-8.0                     # Option B — .NET
sudo apt install -y openjdk-21-jdk                     # Option C — Java
```

> Ubuntu 22.04 ships Python 3.10, which is too old for Option A. Use Ubuntu
> 24.04 (Python 3.12), pick Option B or C, or install Python 3.11+ from the
> [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).

**Windows 10 / 11** — PowerShell (`winget` ships with Windows)

```powershell
winget install -e --id Git.Git
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id PostgreSQL.PostgreSQL.17 --interactive   # the wizard asks for a "postgres" password: use postgres

# Backend toolchain — install only the one you will use
winget install -e --id Python.Python.3.13            # Option A — Python
winget install -e --id Microsoft.DotNet.SDK.8        # Option B — .NET
winget install -e --id EclipseAdoptium.Temurin.21.JDK  # Option C — Java
```

**Close and reopen PowerShell** afterwards so the new tools are on your `PATH`.
The PostgreSQL installer does not add `psql` to the `PATH`, so add it:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"   # this terminal only
```

To make that permanent: Start menu → *Edit environment variables for your
account* → `Path` → *New* → `C:\Program Files\PostgreSQL\17\bin`.

### Check the tools

**macOS / Ubuntu**

```bash
git --version && node --version && npm --version && psql --version
python3 --version      # Option A (3.11+)
dotnet --version       # Option B (8.x)
java -version          # Option C (21)
```

**Windows (PowerShell)**

```powershell
git --version; node --version; npm --version; psql --version
py -3 --version        # Option A (3.11+)
dotnet --version       # Option B (8.x)
java -version          # Option C (21)
```

## Use Case

The **Engineering Task Board**: a Kanban-style task list with three columns
(To Do / In Progress / Done), full CRUD, and status filtering. Full detail,
data model, and API contract are in **[docs/base-taskboard.md](docs/base-taskboard.md)**.

### Repository layout

```
.
├── database/         schema.sql (authoritative), seed.sql, migrations/
├── backend-python/   FastAPI          — port 8000
├── backend-dotnet/   ASP.NET Core     — port 5088
├── backend-java/     Spring Boot      — port 8080
├── frontend/         React + Vite     — port 5173
└── docs/             use case, API contract, feature specs
```

Every command below is run from the **repository root** (the folder containing
`database/` and `frontend/`) unless a `cd` says otherwise.

## Configuration

There is no `.env` file to copy. Nothing secret is committed (`.gitignore`
excludes `.env*`), and each stack reads its settings from **environment
variables**, falling back to built-in defaults. With the local setup used in
this README (user `postgres`, password `postgres`, `localhost:5432`, database
`taskboard`):

- **Python and Java need no configuration** — their defaults already match.
- **.NET needs one variable** — its connection string has no default.
- **The frontend needs one setting only if you don't use the Python backend.**

| Setting | Used by | Default | Notes |
|---------|---------|---------|-------|
| `DATABASE_URL` | Python backend | `postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard` | SQLAlchemy async URL. Can also live in `backend-python/.env` |
| `ConnectionStrings__DefaultConnection` | .NET backend | **none — required** | Npgsql connection string |
| `SPRING_DATASOURCE_URL` / `_USERNAME` / `_PASSWORD` | Java backend | `jdbc:postgresql://localhost:5432/taskboard` / `postgres` / `postgres` | Spring binds these automatically |
| `FRONTEND_ORIGIN` | Python & Java backends | `http://localhost:5173` | CORS allow-list — must equal the URL the browser uses |
| `Frontend__Origin` | .NET backend | `http://localhost:5173` | Same CORS setting, .NET's name for it |
| `VITE_API_BASE_URL` | frontend (`frontend/.env.local`) | `http://localhost:8000` | Python `:8000`, .NET `:5088`, Java `:8080` |

**Setting an environment variable** (applies to the current terminal only — set
it again in every new terminal):

```bash
# macOS / Ubuntu
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```
```powershell
# Windows (PowerShell)
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```

> **Passwords.** `postgres` / `postgres` is a throwaway local-development
> credential. If you chose another password, use it everywhere below, and
> percent-encode special characters in URLs (`@` → `%40`).

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
| GET | `/health` | Liveness check (does **not** touch the database) |

Error contract: `404` for a missing id, `422` for a missing title or an
unknown status. See [docs/base-taskboard.md](docs/base-taskboard.md#api-contract).

## Running the Lab

You will have three things running: **PostgreSQL** (a background service),
**one backend**, and the **frontend**. Use one terminal for the backend and a
second for the frontend.

### 1. Database

**a. Start PostgreSQL** and confirm it is accepting connections.

```bash
# macOS
brew services start postgresql@17
pg_isready                          # expect: accepting connections

# Ubuntu
sudo systemctl enable --now postgresql
pg_isready                          # expect: accepting connections
```
```powershell
# Windows — the installer registered a service that starts automatically
Get-Service postgresql*             # expect: Running
```

**b. Make sure a `postgres` user exists with the password `postgres`.**

```bash
# macOS — Homebrew creates a superuser named after your macOS account,
# not "postgres", so create it:
psql -d postgres -c "CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';"

# Ubuntu — the user exists but has no password yet:
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```
```powershell
# Windows — nothing to do if you used "postgres" in the installer wizard.
# Otherwise use your password in every URL/connection string below.
```

**c. Create the database, then load the schema and seed data.** Identical on
every OS:

```
psql "postgresql://postgres:postgres@localhost:5432/postgres" -c "CREATE DATABASE taskboard;"
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/schema.sql
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/seed.sql
```

**d. Check it.**

```
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -c "SELECT id, title, status FROM tasks ORDER BY id;"
```

You should see six rows (two `done`, two `in-progress`, two `todo`).

> `schema.sql` is safe to re-run. `seed.sql` **wipes the `tasks` table** and
> reloads the six sample rows, so don't re-run it on data you want to keep.
> Use `schema.sql` alone for setup — the files in `database/migrations/` are
> the history of how it was built, not an extra step.

### 2. Pick ONE backend

Each exposes the same API. Interactive docs: **Python** → `/docs`,
**.NET** → `/swagger`, **Java** → `/swagger-ui.html`.

After starting one, **check the database connection** by listing the tasks —
`/health` only proves the process is up, not that it can reach PostgreSQL:

```bash
# macOS / Ubuntu
curl -s http://localhost:8000/api/tasks
```
```powershell
# Windows (PowerShell)
Invoke-RestMethod http://localhost:8000/api/tasks
```

(Replace `8000` with `5088` for .NET or `8080` for Java.) You should get the
six seeded tasks back as JSON.

#### Option A — Python (FastAPI), port 8000

**macOS / Ubuntu**

```bash
cd backend-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Windows (PowerShell)**

```powershell
cd backend-python
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The default database URL already matches this README. To use something else,
set `DATABASE_URL` first (see [Configuration](#configuration)) or put it in
`backend-python/.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/taskboard
```

#### Option B — .NET (ASP.NET Core), port 5088

The connection string is **required** — .NET has no default for it.

**macOS / Ubuntu**

```bash
cd backend-dotnet
export ConnectionStrings__DefaultConnection="Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
dotnet run --project src/TaskBoard.Api
```

**Windows (PowerShell)**

```powershell
cd backend-dotnet
$env:ConnectionStrings__DefaultConnection = "Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
dotnet run --project src/TaskBoard.Api
```

#### Option C — Java (Spring Boot), port 8080

PostgreSQL must already be running — unlike the other two, Spring connects at
startup and exits if it can't. The defaults in `application.yml` match this
README; set the `SPRING_DATASOURCE_*` variables only if yours differ.

**macOS / Ubuntu**

```bash
cd backend-java
./mvnw spring-boot:run
```

**Windows (PowerShell)**

```powershell
cd backend-java
.\mvnw.cmd spring-boot:run
```

`mvnw` / `mvnw.cmd` is the bundled Maven wrapper; the first run downloads Maven
and the dependencies, so it needs internet access and takes a minute. (Use
`mvn` directly if you already have it installed.)

### 3. Frontend

In a **second terminal**, from the repository root:

**macOS / Ubuntu**

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:5088" > .env.local   # skip for Python; use :8080 for Java
npm run dev
```

**Windows (PowerShell)**

```powershell
cd frontend
npm install
Set-Content -Encoding ascii .env.local "VITE_API_BASE_URL=http://localhost:5088"   # skip for Python; use :8080 for Java
npm run dev
```

Open **http://localhost:5173**.

- `frontend/.env.local` is git-ignored. The frontend defaults to the Python
  backend (`http://localhost:8000`), so the file is only needed for .NET or Java.
- The `ascii` encoding matters on Windows: PowerShell's default encodings can
  add a byte-order mark that stops Vite from reading the first variable.
- Vite reads `.env.local` at startup — **restart `npm run dev`** after changing it.

### 4. Smoke test

With the database, one backend and the frontend running, the board at
http://localhost:5173 should show the six seeded tasks in their columns. Create
a task, move it between columns, and delete it.

### Stopping

Press `Ctrl+C` in the backend and frontend terminals. PostgreSQL can keep
running; to stop it:

```bash
brew services stop postgresql@17      # macOS
sudo systemctl stop postgresql        # Ubuntu
```
```powershell
Stop-Service postgresql-x64-17        # Windows (run PowerShell as Administrator)
```

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| `psql: command not found` / `'psql' is not recognized` | `psql` isn't on your `PATH`. macOS and Windows: do the `PATH` step under [Install the tools](#install-the-tools). Ubuntu: `sudo apt install postgresql`. Then open a new terminal |
| Command not found right after a `winget install` | Close and reopen PowerShell so it picks up the new `PATH` |
| `connection refused` on port 5432 | PostgreSQL isn't running — step 1a. Java exits at startup with `Connection to localhost:5432 refused` |
| `role "postgres" does not exist` | macOS/Homebrew only — run the `CREATE ROLE` command in step 1b |
| `password authentication failed for user "postgres"` | The password differs from the one in your URL or connection string. Reset it: `ALTER USER postgres PASSWORD 'postgres';` (see step 1b) |
| `database "taskboard" does not exist` | Run the `CREATE DATABASE` command in step 1c |
| `relation "tasks" does not exist` | Schema not applied — run `schema.sql` (step 1c). No backend creates tables |
| .NET: `/health` is OK but `/api/tasks` returns 500 — *"The ConnectionString property has not been initialized"* | `ConnectionStrings__DefaultConnection` isn't set **in this terminal** — set it, then restart `dotnet run` |
| Ubuntu: `ensurepip is not available` when creating the venv | `sudo apt install python3-venv` |
| Windows: `Activate.ps1 cannot be loaded because running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again |
| `npm run dev` fails or warns about the Node version | Node is too old (Vite 8 needs 20.19+, 22.13+ or 24+). Ubuntu: `nvm install --lts`. macOS/Windows: reinstall Node |
| Port already in use (8000 / 5088 / 8080 / 5173) | Find the process — macOS/Ubuntu: `lsof -i :8000`; Windows: `Get-NetTCPConnection -LocalPort 8000` — and stop it |
| Board is empty or shows a network/CORS error | Backend not running, or `VITE_API_BASE_URL` points at a different backend than the one you started (restart `npm run dev` after editing). If Vite printed a port other than 5173 (because 5173 was busy), the backend's CORS check fails: free port 5173, or set `FRONTEND_ORIGIN` (`Frontend__Origin` for .NET) to the URL Vite printed |
| `./mvnw: Permission denied` | The execute bit was lost (e.g. a zip download): `chmod +x backend-java/mvnw` |

**Start over with a clean database:**

```
psql "postgresql://postgres:postgres@localhost:5432/postgres" -c "DROP DATABASE taskboard;"
```

then repeat steps 1c–1d.

## Exercises

The exercises run a hands-on workshop on this codebase. An AI coding assistant
such as GitHub Copilot is optional — if you have one, use it and record the
extra metrics; if not, do the same steps by hand and note where AI *would* have
helped.

### Exercise 1 — Guided: run it, read it, map the current state

1. Bring up the database, one backend, and the frontend (steps above). Confirm
   the board shows the six seeded tasks and that you can create, move, and
   delete a task.
2. Run the tests for the backend you chose and for the frontend
   (see [Verification](#verification)). Note how long a full run takes.
3. Walk the codebase against [the layered architecture](docs/base-taskboard.md#architecture).
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
- **Pass B — context-first.** Start from `docs/base-taskboard.md`, the existing
  repository/service/router layering, and the existing tests. Decide where the
  sort belongs (repository query, not the controller), add or update a test
  first, then implement. Run the tests.

For each pass record: wall-clock time, number of test files touched, whether
the tests passed on the first try, and — if using Copilot — rough prompt/token
count. Put the numbers in the worksheet.

> This is the core contrast in miniature: *inconsistent results when
> teams rely on prompts alone* vs *specification-led, validated change*.

### Exercise 3 — Independent challenge

1. **Port the change.** Implement the same `sort` feature in a second backend
   (a different language from your Pass B). Make both return byte-identical
   JSON for the same request.
2. **Write a risk note (½ page).** Pick the two risks from the list below that
   your change is closest to. For each: how could this specific change have
   gone wrong, and which test would have caught it?
   - AI-generated changes that disrupt existing patterns or layering
   - Manual, inconsistent review of AI-generated code
   - Inconsistent results when a team relies on ad-hoc prompts
   - Sensitive data or secrets leaking into prompts or code
   - Changes shipping with weak or missing tests
   - AI cost and quality going unmeasured
3. **Draft the target-state workflow.** Complete the target column of the
   [workflow map](#current-state-vs-target-state): what should the disciplined
   version of "add a small API + UI change" look like once your team has
   adopted it (spec, context, tests-first, PR gate, observability)?

## Current-state vs target-state

Fill this in during Exercises 1 and 3.

| Workflow stage | Current state (today) | Target state (disciplined workflow) |
|----------------|-----------------------|-------------------------------------|
| Framing the change | | |
| Gathering context for the AI | | |
| Implementation | | |
| Testing | | |
| Review / PR | | |
| Observability (traces, cost, quality) | | |

## Baseline metrics worksheet

Six measures to track. Capture them for the Exercise 2 change so you have a
baseline to improve on in later work.

| Metric | Pass A (prompt-only) | Pass B (context-first) |
|--------|----------------------|------------------------|
| Implementation cycle time (min) | | |
| Quality / regression risk (tests passed first try? bugs found after?) | | |
| Review effort (min to review the diff; # review comments) | | |
| Testing effort (# test files touched; min to write) | | |
| Token usage (approx, if using Copilot) | | |
| AI cost signal (prompts / retries needed) | | |

## Role lenses

Same lab, different focus depending on your function:

- **Architects / Eng leads** — audit the layering: does business logic ever
  leak into a controller or a repository? Is the `tasks` schema owned in
  exactly one place?
- **Developers / Testers** — you own Exercise 2 and 3 in depth. Drive the
  tests-first loop; make the backends agree byte-for-byte on the same request.
- **DevOps / SRE** — sketch what a CI job for this repo runs (build, test,
  schema-load check) and where telemetry (traces, cost, quality) would attach.
- **Product / Program / Design** — write the one-paragraph spec for the
  Exercise 2 change *before* anyone codes it; check the UI change against it.

## Verification

None of the test suites need a running database or backend — the backends use
fakes or mocks and the frontend mocks HTTP. Run each block from its folder
under the repository root. The commands are identical on every OS apart from
the two marked lines.

```
# .NET backend  — in backend-dotnet/
dotnet build
dotnet test

# Python backend  — in backend-python/ (virtualenv activated, see Option A)
pip install -r requirements.txt
pytest

# Java backend  — in backend-java/
./mvnw -B test            # Windows: .\mvnw.cmd -B test

# Frontend  — in frontend/
npm install
npm run build
npm test -- --run
```

The schema and seed files load into a clean database (this one **does** need
PostgreSQL running). Identical on every OS, from the repository root:

```
psql "postgresql://postgres:postgres@localhost:5432/postgres" -c "CREATE DATABASE taskboard_check;"
psql "postgresql://postgres:postgres@localhost:5432/taskboard_check" -f database/schema.sql
psql "postgresql://postgres:postgres@localhost:5432/taskboard_check" -f database/seed.sql
psql "postgresql://postgres:postgres@localhost:5432/postgres" -c "DROP DATABASE taskboard_check;"
```

- [ ] `dotnet build` and `dotnet test` pass (14 tests)
- [ ] `pytest` passes (25 tests)
- [ ] `./mvnw test` passes (16 tests)
- [ ] `npm run build` succeeds and `npm test -- --run` passes (12 tests)
- [ ] `schema.sql` + `seed.sql` load into a clean database without error
- [ ] The board renders the seeded tasks and CRUD works against a live backend
- [ ] No secrets are committed (`git status` shows no `.env*` files)

## Next Steps

You now have a running, tested baseline you can measure against. Ways to keep
going on this same codebase:

- **Build a feature from a brief.** [`docs/`](docs/) has plain-English briefs for
  [task comments](docs/feature-task-comments.md),
  [task search](docs/feature-task-search.md) and a
  [board UI refresh](docs/feature-ui-refresh.md). Take one from brief to merged
  change, record the same six metrics, and compare them with your baseline.
- **Customize your AI assistant for this repo.** `.github/` holds example GitHub
  Copilot customization: path-specific instructions
  (`.github/instructions/`), SDLC agents (`.github/agents/`) and an
  architecture-review skill (`.github/skills/`). Try them on the same change
  and compare the metrics.
