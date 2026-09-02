<!--
Sync Impact Report
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: n/a (initial adoption)
Added sections:
  - Core Principles I–VII (Layered Architecture, Single Schema Owner,
    Error Contract, Cross-Backend Parity, Tests-First-Class, Spec Is
    Source of Truth, Scoped Context)
  - Additional Constraints
  - Development Workflow & Quality Gates
  - Governance
Removed sections: n/a (initial adoption from template placeholders)
Templates requiring updates:
  - .specify/templates/plan-template.md ⚠ pending manual check (verify
    Constitution Check gate references these principles)
  - .specify/templates/spec-template.md ⚠ pending manual check
  - .specify/templates/tasks-template.md ⚠ pending manual check
Follow-up TODOs:
  - TODO(RATIFICATION_DATE): original adoption date unknown; set to
    today's date (2026-09-02) since this is the first ratified version.
  - Deferred non-governance intent: creation of
    .github/prompts/context-brief.prompt.md (referenced by Principle
    VII) does not exist yet — see Next Actions.
-->

# Engineering Task Board Constitution

## Core Principles

### I. Layered Architecture (NON-NEGOTIABLE)
Every backend (`.NET`, Python, Java) MUST follow the same three layers:
Controller/Router → Service → Repository. The Controller/Router layer
translates HTTP to/from domain calls and maps errors to status codes; it
MUST NOT contain business rules or SQL. The Service layer owns validation
and business rules; it MUST NOT perform HTTP concerns or SQL. The
Repository layer owns ALL database access and ALL aggregation queries; it
MUST NOT perform validation or HTTP concerns. The React frontend mirrors
this separation: `components/` (presentational) → `pages/` (state + data
fetching) → `services/` (all HTTP in one place). Layer-skipping (e.g., a
controller issuing SQL, or a component calling `fetch` directly) is a
constitution violation regardless of language.
Rationale: A shared layering contract keeps three independently
implemented backends comparable, reviewable, and swappable without
hidden coupling.

### II. Single Schema Owner
`database/schema.sql` is the only authoritative definition of the
database schema. Schema changes MUST be made as reviewed edits to that
file. No backend may introduce its own migration tooling, ORM
auto-migration (e.g., EF Core migrations, SQLAlchemy
`Base.metadata.create_all()`, Hibernate `ddl-auto` values other than
`none`), or shadow schema definitions. `created_at` and `updated_at`
columns are set by the database (defaults/triggers), never by
application code.
Rationale: One schema owner eliminates drift between three backends
sharing a single database and removes an entire class of "which backend
last changed the schema" bugs.

### III. Error Contract
CRUD endpoints MUST return exactly: `404` when the referenced resource
id does not exist, and `422` when the request body is invalid (missing
title, or `status` outside `todo` / `in-progress` / `done`). No other
status codes are introduced for these conditions. This contract is
identical across all three backends.
Rationale: A minimal, fixed error contract lets the frontend and tests
treat all three backends interchangeably.

### IV. Cross-Backend Parity
`.NET`, Python, and Java MUST expose every feature identically and
return byte-identical JSON response bodies, aside from acceptable
timestamp key casing differences dictated by each framework's default
serializer. A feature is not complete until it has been implemented (or
explicitly deferred with a tracked follow-up) in a way that preserves
this parity; a change to one backend's request/response shape MUST be
portable to the other two without altering the contract.
Rationale: The project's value is demonstrating disciplined, comparable
full-stack change across stacks; parity is the measure of that
discipline.

### V. Tests-First-Class (NON-NEGOTIABLE)
No task — endpoint, service method, repository query, or UI change — is
considered done until it has a test in the same layer, and that test
passes. Tests MUST be added or updated before a change is marked
complete, not deferred to a follow-up task.
Rationale: Small, well-tested layers are what make three parallel
backends maintainable; skipping tests compounds drift risk immediately.

### VI. Spec Is the Source of Truth
Any code change that alters a requirement, contract, or behavior MUST
start with a spec change (via the Spec Kit workflow: specify → clarify →
plan → tasks → implement). Ad hoc requirement changes made only in chat
or directly in the editor, without an accompanying spec update, are not
permitted for anything beyond trivial bug fixes that do not change
behavior.
Rationale: Keeping the spec authoritative prevents the three backends
and the frontend from silently diverging from an agreed contract.

### VII. Scoped Context
Implementation work MUST use a compressed, task-scoped context brief
(see `.github/prompts/context-brief.prompt.md`) rather than whole-repo
context dumps. Agents and contributors should load only the
instructions, files, and prior decisions relevant to the current task.
Rationale: Scoped context keeps changes precise and auditable, and
avoids irrelevant context steering an implementation away from the
layering and parity rules above.

## Additional Constraints

- `status` is exactly one of: `todo`, `in-progress`, `done`. No other
  values are valid at any layer.
- Secrets, `.env*` files (except `.env.example`), and environment
  variables MUST NOT be read or hard-coded by agents or contributors;
  use each framework's configuration system.
- Match the existing style of the file being edited; do not reformat
  untouched lines.

## Development Workflow & Quality Gates

- Verification commands per backend/frontend:
  - .NET: `dotnet test` in `backend-dotnet/`
  - Python: `pytest` in `backend-python/`
  - Java: `./mvnw -B test` in `backend-java/`
  - Frontend: `npm test -- --run` in `frontend/`
- A pull request MUST NOT be considered mergeable if it violates Layered
  Architecture, Single Schema Owner, the Error Contract, or
  Tests-First-Class.
- Reviewers MUST check Cross-Backend Parity whenever a change touches
  more than one backend's shared contract.

## Governance

This constitution supersedes conflicting guidance in other instruction
files for matters of architecture, schema ownership, error contracts,
parity, and process. `.github/copilot-instructions.md` and `AGENTS.md`
remain the operational quick-reference and MUST stay consistent with
this document; where they conflict, this constitution wins and the
other files must be updated to match.

Amendments are made via edits to this file plus an updated Sync Impact
Report. Versioning follows semantic versioning:
- MAJOR: backward-incompatible principle removal or redefinition.
- MINOR: a new principle or materially expanded section is added.
- PATCH: clarifications, wording, or typo fixes with no semantic change.

All PRs and code reviews MUST verify compliance with the Core
Principles above. Any exception must be justified in the PR description
and, if recurring, folded back into this constitution via an amendment.

**Version**: 1.0.0 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-02
