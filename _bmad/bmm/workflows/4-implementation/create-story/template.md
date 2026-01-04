# {{story_id}}: {{story_title}}

**Epic:** {{epic_id}} | **Points:** {{points}} | **Priority:** {{priority}} | **Sprint:** {{sprint}}
**Status:** ready-for-dev

<!--
FILE LOCATION: .bmad/epics/{{epic_id}}/stories/{{story_folder}}/story-{{story_folder}}.md
JIRA Hierarchy: Epic → Story → Task → Sub-task
This story syncs to JIRA. Tasks in ./tasks/ become JIRA Tasks, subtask rows become Sub-tasks.
Per .bmad/STRUCTURE.md - Story folder format: {NN}-{slug}/ (e.g., 01-api-key-schema/)
-->

---

## Story

As a {{role}},
I want {{action}},
so that {{benefit}}.

---

## Acceptance Criteria

<!-- BDD format from epic. Each AC maps to one or more Tasks. -->

### AC-1: {{ac1_title}}
```gherkin
GIVEN {{given}}
WHEN {{when}}
THEN {{then}}
```

### AC-2: {{ac2_title}}
```gherkin
GIVEN {{given}}
WHEN {{when}}
THEN {{then}}
```

---

## Tasks

<!--
NEW STRUCTURE (per .bmad/STRUCTURE.md):
Tasks are now separate files in ./tasks/ directory.
Each task file is ~30 lines and syncs to JIRA as a Task.
Subtask rows in task files sync as JIRA Sub-tasks.

Task files: ./tasks/task-{NN}-{slug}.md
  - task-01-create-migration.md
  - task-02-implement-hmac.md
  - task-03-verification.md
-->

| # | Task File | Title | Linked AC | Est | Status |
|---|-----------|-------|-----------|-----|--------|
| T1 | [task-01-{{task1_slug}}.md](./tasks/task-01-{{task1_slug}}.md) | {{task1_title}} | AC-1 | {{hours}}h | pending |
| T2 | [task-02-{{task2_slug}}.md](./tasks/task-02-{{task2_slug}}.md) | {{task2_title}} | AC-2 | {{hours}}h | pending |
| T3 | [task-03-verification.md](./tasks/task-03-verification.md) | Verification & Documentation | All | 1h | pending |

<!--
Each task file contains:
- Task description
- Target files to create/modify
- Subtask table (rows → JIRA Sub-tasks)
- Done criteria
- AI implementation prompt
-->

---

## Technical Notes

### Architecture Compliance
- Relevant patterns from architecture docs
- Constraints and requirements

### Target Files
```
Primary:
  - path/to/file.rs

Tests:
  - tests/path/to/test.rs
```

### Dependencies
- External crates/packages with versions
- Internal modules to import

---

## Dev Notes

### Implementation Hints
- Code patterns to follow
- Anti-patterns to avoid
- Reference implementations

### Project Structure Notes
- Alignment with unified project structure
- Detected conflicts or variances

### References
- [Source: docs/ARCHITECTURE_OVERVIEW.md#Section]
- [Source: contracts/openapi/spec.yaml]

---

## Dev Agent Record

### Agent Model Used
{{agent_model_name_version}}

### Execution Context
| Field | Value |
|-------|-------|
| Session ID | |
| Start Time | |
| End Time | |

### Debug Log References
N/A

### Completion Notes
- Notes added during implementation

### Files Created/Modified
| File | Action | Lines |
|------|--------|-------|
| path/to/file | Created | 0 |
