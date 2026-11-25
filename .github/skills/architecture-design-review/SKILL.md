---
name: "architecture-design-review"
description: "Run an architecture design review for a Task Board feature before implementation. Use when reviewing a feature plan, validating REST or database contracts, checking controller-service-repository boundaries, comparing .NET/Python/Java behavior, or freezing implementation decisions."
compatibility: "Requires a Task Board repository with docs or specs for the feature and the repository architecture instructions."
metadata:
  author: "Engineering Task Board"
  source: "workspace workflow"
---

# Architecture Design Review

## User Input

```text
$ARGUMENTS
```

Treat the user input as the feature name, feature slug, or review focus. If it is empty, infer the feature from the newest requirements or plan artifact and state that assumption.

## Goal

Validate the proposed design before implementation and freeze the smallest complete contract that all affected stacks can implement consistently. This review is architecture-focused: it may update design artifacts, but it must not implement application code, tests, migrations, or frontend behavior.

## Required Inputs

Locate the feature artifacts using this order:

1. A path explicitly supplied in `$ARGUMENTS`.
2. `docs/<feature>/requirements.md` and `docs/<feature>/plan.md`.
3. `specs/<feature>/spec.md`, `plan.md`, and any existing contract artifacts.

Read the repository's authoritative instructions before reviewing. If requirements or a plan cannot be found, stop and report the missing prerequisite instead of inventing a design.

## Review Workflow

### 1. Establish the Feature Boundary

Extract:

- User-visible behavior and acceptance criteria.
- Affected endpoints, screens, entities, and persistence operations.
- Explicit out-of-scope behavior.
- Open questions and assumptions.

Write a short boundary summary in the review output. Do not expand scope to unrelated cleanup.

### 2. Check Architectural Ownership

For every proposed behavior, assign one owner:

| Layer | Owns | Must not do |
|---|---|---|
| Controller / Router | HTTP parsing, response mapping, status codes | Business rules or SQL |
| Service | Validation and business rules | HTTP concerns or SQL |
| Repository | All database access and query construction | Validation or HTTP concerns |
| React components | Presentation and user interaction | Data fetching or business rules |
| React pages | Screen state and data fetching | Direct database or duplicated HTTP calls |
| React services | All HTTP calls | Rendering or screen state |

Flag any design that crosses these boundaries. For each finding, name the owning layer and the smallest correction.

### 3. Validate the REST Contract

Define or verify:

- HTTP method and route.
- Query and path parameters, including omission and whitespace rules.
- Request and response shapes.
- Success status and every permitted error status.
- Validation rules and error payload shape.
- Compatibility with existing endpoints and clients.
- Required tests at controller/router, service, and repository layers.

Use the repository's existing error contract. Do not introduce a new status code or response shape without an explicit approved requirement.

### 4. Validate the Data Contract

Check whether the feature needs a schema change. Prefer existing columns and indexes when they satisfy the requirements.

If persistence changes are needed, document:

- The exact change in `database/schema.sql`.
- Constraints, nullability, indexes, and ownership of timestamps.
- Read/write effects on existing endpoints.
- Whether seed data or backfill is required.
- Why the change is compatible across .NET, Python, and Java.

Do not create framework-specific migrations or runtime schema creation. If no schema change is needed, state that explicitly.

### 5. Check Cross-Backend Parity

Compare the design for .NET, Python, and Java. They must expose the same request parameters, response JSON, validation rules, error statuses, and observable behavior.

Record any stack-specific implementation note only when it preserves the shared contract. A backend that cannot implement the contract without changing it is a design blocker.

### 6. Check Frontend Integration

Confirm the design follows `components/` -> `pages/` -> `services/`.

Review:

- Loading, empty, error, and retry states.
- Existing filters and interactions that combine with the feature.
- Accessibility and keyboard behavior for new controls.
- Stale request or race handling where requests can overlap.
- Whether URL state, local state, or server state is authoritative.

Keep UI behavior aligned with the frozen API contract. Do not redesign unrelated screens.

### 7. Review Risks and Decisions

Classify findings:

- **BLOCKER**: violates an architecture MUST, leaves the contract ambiguous, or prevents backend parity.
- **HIGH**: likely causes incompatible behavior, data loss, security exposure, or an untestable requirement.
- **MEDIUM**: missing edge case, test, performance consideration, or UI state.
- **LOW**: wording or maintainability improvement.

For each finding include the artifact location, impact, recommendation, and whether user approval is required.

## Outputs

When the design passes with no blockers:

1. Update or create `<feature-dir>/contract.md` with the frozen REST, data, error, parity, and frontend integration contract.
2. Update `<feature-dir>/plan.md` only when needed to align it with the approved contract.
3. Produce a concise review report with:
   - Decision: `APPROVED` or `APPROVED WITH CONDITIONS`.
   - Contract artifact path.
   - Architecture decisions.
   - Required implementation and test slices.
   - Remaining non-blocking risks.

When blockers or unresolved decisions remain:

1. Do not create or claim an approved contract.
2. Produce a report with decision `CHANGES REQUIRED`.
3. List the minimum decisions or artifact changes needed to rerun the review.

## Completion Checks

Before reporting completion, verify:

- Every requirement has an owning layer.
- Every new or changed endpoint has a same-layer test requirement.
- REST behavior and errors are explicit.
- Database ownership remains in `database/schema.sql`.
- The three backends have one shared observable contract.
- Frontend responsibilities follow the repository layering.
- No application code was changed during the review.
- The decision and unresolved risks are plainly stated.
