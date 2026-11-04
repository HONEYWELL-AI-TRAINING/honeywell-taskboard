# Proposal

## Why

Tasks can currently be removed only by physically deleting their rows, so an
accidental delete cannot be undone. Soft deletion will make tasks recoverable
while preserving a deliberate permanent-delete path.

## What Changes

- Add nullable `deleted_at TIMESTAMP` to the canonical schema and a new numbered
  migration; do not modify migration 001.
- Change task DELETE to set `deleted_at` and keep returning 204. Support
  explicit permanent deletion through `?permanent=true`.
- Exclude deleted tasks from normal reads through one shared repository-level
  predicate per backend; allow deleted-task listing with `deleted=true` and
  deleted single-task retrieval with `includeDeleted=true`.
- Add restore behavior and a deleted-tasks view/action in the React UI.
- Keep error responses within the established 404/422 contract and behavior
  consistent across Python, .NET, and Java.
- Keep stats and task-comment implementations out of scope because neither API
  exists in the current codebase. Record their agreed deleted-row behavior as
  integration constraints; preserve comments on soft delete/restore and allow
  cascade only on permanent deletion when comments are implemented.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `task-management`: Change deletion from physical to soft deletion, add
  deleted-task listing/retrieval, restore and permanent deletion, and exclude
  deleted tasks from normal task counts.

## Impact

- Shared PostgreSQL schema, with a new numbered migration and an updated
  `database/schema.sql`; task models and repository query methods in all three
  backends.
- Python, .NET, and Java task services/controllers and tests, including
  Python's existing `/api/tasks/count` behavior.
- React task service, board/trash UI, and tests; current frontend supports only
  listing and deleting tasks.
- Existing DELETE/GONE test expectations need to be updated to assert retained
  data and hidden-by-default behavior. Restore, listing, and permanent-delete
  paths need new coverage.
- No `/api/tasks/stats` or task-comment endpoint/model exists in the inspected
  code. This change does not add either capability; their specified behavior is
  a future integration constraint.
