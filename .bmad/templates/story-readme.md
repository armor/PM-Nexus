# {{STORY_ID}}: {{STORY_TITLE}}

**Epic:** {{EPIC_ID}} | **Points:** {{POINTS}} | **Priority:** {{PRIORITY}} | **Sprint:** {{SPRINT}}
**Status:** {{STATUS}}

---

## Coordination

| Field | Value |
|-------|-------|
| Worktree | `worktrees/{{REPO}}-{{STORY_SLUG}}` |
| Branch | `{{STORY_SLUG}}` |
| Depends On | {{DEPENDS_ON}} |
| Blocks | {{BLOCKS}} |
| JIRA Key | |

### Task Execution Order

```
{{TASK_ORDER}}
```
*Example: T1 → (T2, T3 parallel) → T4*

---

## Story

As a {{ROLE}}, I want {{ACTION}}, so that {{BENEFIT}}.

---

## Business Value

**Value Statement:** {{VALUE_STATEMENT}}
**Success Metric:** {{SUCCESS_METRIC}}

---

## Acceptance Criteria

### AC1: {{AC_1_TITLE}}

**GIVEN** {{CONTEXT}}
**WHEN** {{ACTION}}
**THEN** {{RESULT}}

### AC2: {{AC_2_TITLE}}

**GIVEN** {{CONTEXT}}
**WHEN** {{ACTION}}
**THEN** {{RESULT}}

### AC3: {{AC_3_TITLE}}

**GIVEN** {{CONTEXT}}
**WHEN** {{ACTION}}
**THEN** {{RESULT}}

---

## Tasks

| # | Task File | Title | Linked AC | Status |
|---|-----------|-------|-----------|--------|
| T1 | [task-01-{{TASK_1_SLUG}}.md](./tasks/task-01-{{TASK_1_SLUG}}.md) | {{TASK_1_TITLE}} | AC1 | pending |
| T2 | [task-02-{{TASK_2_SLUG}}.md](./tasks/task-02-{{TASK_2_SLUG}}.md) | {{TASK_2_TITLE}} | AC2 | pending |
| T3 | [task-03-{{TASK_3_SLUG}}.md](./tasks/task-03-{{TASK_3_SLUG}}.md) | {{TASK_3_TITLE}} | AC3 | pending |

---

## Technical Notes

{{BRIEF_TECHNICAL_CONTEXT}}

### Key Files

- `{{FILE_PATH_1}}` - {{PURPOSE}}
- `{{FILE_PATH_2}}` - {{PURPOSE}}

### Dependencies

- {{DEPENDENCY_1}}
- {{DEPENDENCY_2}}

---

## References

- Epic: {{EPIC_ID}}
- Architecture: {{ARCHITECTURE_DOC}}
