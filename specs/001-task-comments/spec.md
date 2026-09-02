# Feature Specification: Task Comments

**Feature Branch**: `[001-task-comments]`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Build the feature described in docs/feature-task-comments.md — a task comment thread on the Engineering Task Board. Honour the constitution. Do not decide implementation details (framework, table columns beyond the obvious) — that is for /speckit.plan."

## Clarifications

### Session 2026-09-02

- Q: When another engineer posts or deletes a comment on a task, must the board and thread update for everyone currently viewing it, or is it enough that the acting user's own screen updates immediately (others see it next time they load/refresh)? → A: Self-only: the acting user's screen updates immediately; other users see changes on their next normal data refresh (e.g., page load). No live-sync (polling/websocket) mechanism is required.
- Q: Should a comment's author name be rejected when it's only whitespace, the same way whitespace-only comment text is rejected? → A: No — only a missing/empty author is rejected; a whitespace-only author name is accepted as-is (no trimming or extra validation beyond presence).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a task's discussion at a glance (Priority: P1)

An engineer looks at the board and wants to know, without opening anything,
whether a task has an active discussion. Each task card shows a comment
count indicator when the task has one or more comments; cards with no
comments show no indicator.

**Why this priority**: This is the passive, always-on signal that makes the
rest of the feature discoverable. Without it, nobody knows a thread exists.

**Independent Test**: Seed one task with comments and one without. Confirm
the card with comments shows a count matching the number of comments, and
the other card shows no indicator.

**Acceptance Scenarios**:

1. **Given** a task with 3 comments, **When** the board is viewed, **Then**
   its card shows a comment indicator with count 3.
2. **Given** a task with 0 comments, **When** the board is viewed, **Then**
   its card shows no comment indicator.
3. **Given** a task with comments, **When** a comment is deleted such that
   0 remain, **Then** the indicator is removed from the card.

---

### User Story 2 - Read and post comments on a task (Priority: P1)

An engineer clicks a task's comment indicator (or an affordance to open
comments when there are none yet) to expand an inline thread showing
existing comments oldest-first, each with its author and roughly when it
was posted. Below the thread, the engineer types their name and a short
comment and posts it, and it appears in the thread immediately.

**Why this priority**: This is the core value of the feature — discussing a
task without leaving the board. It is the reason the feature exists.

**Independent Test**: Open a task's thread, post a comment with an author
and text, and confirm it appears at the bottom of the thread with the
correct author and a recent timestamp, without navigating away from the
board.

**Acceptance Scenarios**:

1. **Given** a task with existing comments, **When** its thread is
   expanded, **Then** comments are shown oldest-first, each showing author
   and an approximate posted time.
2. **Given** an expanded thread, **When** the engineer enters an author and
   comment text and posts, **Then** the new comment appears at the bottom
   of the thread with that author and text.
3. **Given** an expanded thread, **When** the engineer tries to post with a
   missing author or missing text, **Then** the comment is rejected and no
   new comment is added.

---

### User Story 3 - Remove an unwanted comment (Priority: P2)

Any engineer viewing a thread can delete any comment in it (no ownership
check — this app has no authentication), removing it from the thread
immediately.

**Why this priority**: Keeps threads clean of mistakes or noise, but the
board is still useful without it, so it ranks below reading/posting.

**Independent Test**: Post a comment, delete it, and confirm it no longer
appears in the thread and the card's comment count decreases accordingly.

**Acceptance Scenarios**:

1. **Given** a thread with a comment, **When** any engineer deletes that
   comment, **Then** it is removed from the thread and the board's comment
   count for that task decreases by one.

---

### Edge Cases

- Deleting a task deletes all of its comments along with it.
- Posting a comment to a task that no longer exists (e.g., deleted by
  another user moments earlier) is rejected as a missing-resource error,
  not silently accepted.
- Deleting a comment that no longer exists (e.g., already deleted) is
  rejected as a missing-resource error.
- A comment consisting only of whitespace is treated as missing text and
  rejected.
- Very long author names or comment text beyond the defined limits are
  rejected rather than silently truncated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The board MUST show a comment count indicator on each task
  card whose task has one or more comments, and MUST show no indicator on
  a task with zero comments.
- **FR-002**: Users MUST be able to expand an inline comment thread for any
  task directly from the board, without navigating to a separate page.
- **FR-003**: The thread MUST display existing comments ordered oldest to
  newest, each showing its author and an approximate posted time.
- **FR-004**: Users MUST be able to post a new comment to a task by
  supplying an author name and comment text.
- **FR-005**: The system MUST reject a comment submission that is missing
  an author, missing comment text, or whose comment text is only
  whitespace. An author name containing only whitespace is accepted (only
  a missing/empty author is rejected).
- **FR-006**: The system MUST reject a comment author name or comment text
  that exceeds the defined length limits (see Assumptions).
- **FR-007**: Users MUST be able to delete any existing comment; deletion
  is not restricted to the comment's original author (no authentication
  exists in this app).
- **FR-008**: Deleting a task MUST also delete all of its comments.
- **FR-009**: Posting a comment to, or deleting a comment from, a task that
  does not exist MUST be rejected as a missing-resource error rather than
  silently succeeding or failing ambiguously.
- **FR-010**: Deleting a comment id that does not exist MUST be rejected as
  a missing-resource error.
- **FR-011**: The comment thread feature MUST behave identically (same
  triggering conditions, same validation rules, same ordering) regardless
  of which backend serves the request.

### Key Entities *(include if feature involves data)*

- **Comment**: Belongs to exactly one task. Has an author name, comment
  text, and a creation time. Comments are immutable once posted (no
  editing) and can only be removed, never modified, and are permanently
  removed when their parent task is removed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from viewing the board to posting a comment on
  any task in under 15 seconds, without leaving the board view.
- **SC-002**: 100% of the time, the acting user sees the board's comment
  count and thread reflect their own posts and deletes immediately,
  without a full page reload. Other users see the update on their next
  normal data refresh (e.g., page load); no live cross-user sync is
  required.
- **SC-003**: Attempting to post a comment with a missing author or empty
  text is rejected 100% of the time, with no partial/invalid comment ever
  saved.
- **SC-004**: Deleting a task removes 100% of its associated comments,
  leaving no orphaned comment data.

## Assumptions

- "Short" comment text is capped at 500 characters; this is a hard limit,
  not a UI hint. Submissions beyond it are rejected (FR-006).
- Author name is capped at 100 characters, rejected beyond that.
- There is no maximum number of comments per task.
- Comments are returned oldest-first by the API, matching the display
  order in the thread (no separate client-side re-sorting requirement).
- A `GET` for a task's comments returns an empty list (not a 404) when the
  task exists but has no comments; a 404 applies only when the task itself
  does not exist.
- The response body for posting a comment is the newly created comment
  (not the whole thread), consistent with how other single-resource
  creates behave in this API.
- "Roughly when" a comment was posted is satisfied by returning the exact
  creation timestamp from the database (as with `created_at` elsewhere in
  this app); the frontend may choose to render it relatively, but that is
  a display concern, not an API concern.
- No authentication or authorization exists in this app; any user can
  delete any comment, consistent with the rest of the app's current trust
  model.
- Editing, replies, rich text, attachments, and notifications are out of
  scope, per the feature brief.
