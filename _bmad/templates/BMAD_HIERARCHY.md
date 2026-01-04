# BMAD Hierarchy Definition

## Overview

This document defines the BMAD (BMad Agile Development) hierarchy and how it maps to JIRA issue types.

## Hierarchy Levels

```
Epic (JIRA Epic)
├── Story (JIRA Story)
│   ├── Task (JIRA Task)
│   │   ├── Subtask (JIRA Sub-task)
│   │   ├── Subtask
│   │   └── ...
│   ├── Task
│   └── ...
├── Story
└── ...
```

## Level Definitions

| Level | JIRA Type | Purpose | Size Target | Contains |
|-------|-----------|---------|-------------|----------|
| **Epic** | Epic | Business capability / Feature set | ~30 lines (JIRA) + 500+ lines (Docs) | Goals, success metrics, story list |
| **Story** | Story | User value delivery | ~50-100 lines | User story, acceptance criteria, tasks |
| **Task** | Task | Developer work unit | ~30-50 lines | Technical spec, files, patterns, done checklist |
| **Subtask** | Sub-task | Atomic implementation | ~10-20 lines | Single file/function change |

---

## Epic Structure

Epics have a **dual-file system**:

### 1. JIRA Summary (`epic-summary.md`) - ~30 lines

For JIRA sync - contains only essential metadata:

```markdown
# EPIC-{ID}: {Epic Title}

**Status:** {status}
**Priority:** {priority}
**Owner:** {team}
**Total Stories:** {count}
**Total Points:** {points}

## Summary
{2-3 sentences}

## Business Value
- {bullet 1}
- {bullet 2}

## Acceptance Criteria
- [ ] {AC-1}
- [ ] {AC-2}

## Stories
- [ ] {STORY-ID}: {Story Title} ({points} pts)
```

### 2. Full Documentation (`epic-full.md`) - 500+ lines

For humans/AI - contains complete context:

- Complete problem statement
- Architecture decisions and rationale
- Technical constraints and dependencies
- Risk assessment and mitigation
- All acceptance criteria with detailed scenarios
- Implementation patterns and anti-patterns
- Reference documentation links
- AI implementation prompts
- Testing strategy
- Security considerations
- Performance requirements

### 3. Confluence Page (Optional)

Use `/confluence-sync` to push `epic-full.md` to Confluence as living documentation.

---

## Story Structure (~50-100 lines)

Stories are single files in `.bmad/implementation-artifacts/`:

```markdown
# Story {STORY-ID}: {Story Title}

**Epic:** {EPIC-ID} | **Points:** {points} | **Priority:** {priority} | **Sprint:** {sprint}
**Status:** {status}

## Story
As a {role}, I want {action}, so that {benefit}.

## Acceptance Criteria
### AC-1: {title}
GIVEN {context} WHEN {action} THEN {result}

### AC-2: {title}
...

## Tasks
<!-- JIRA SYNC: Each ### becomes a JIRA Task, each table row becomes a Sub-task -->

### {STORY-ID}-T1: {Task Title}
**Linked to:** AC-1
**Estimated:** {hours} hours

| Subtask | Description | Status |
|---------|-------------|--------|
| T1-S1 | {description} | pending |
| T1-S2 | Write unit tests | pending |

### {STORY-ID}-T2: {Task Title}
...

## Technical Notes
{Architecture constraints, target files, dependencies}

## Dev Agent Record
{Agent model, execution context, files modified}
```

---

## Task Naming Convention

| Level | Naming Pattern | Example |
|-------|----------------|---------|
| Epic | `EPIC-{PROJECT}-{NUM}` | `EPIC-AUTH-001` |
| Story | `{EPIC-ID}.{NUM}` or `{EPIC-ID}-{NUM}` | `AUTH-001.1` or `AUTH-001-1` |
| Task | `{STORY-ID}-T{NUM}` | `AUTH-001-1-T1` |
| Subtask | `T{NUM}-S{NUM}` | `T1-S1` |

---

## File Organization

```
.bmad/
├── planning-artifacts/
│   └── epics/
│       ├── EPIC-{ID}.md              # Epic summary for JIRA (~30 lines)
│       └── EPIC-{ID}-full.md         # Full documentation (500+ lines)
│
├── implementation-artifacts/
│   ├── {story-id}.md                  # Story files with tasks
│   └── sprint-status.yaml             # Sprint tracking
│
└── generated-stories/                 # AI-enhanced verbose stories
    └── {epic-name}/
        └── {story-file}.md
```

---

## JIRA Sync Rules

### What Syncs to JIRA

| BMAD Element | JIRA Issue Type | Source |
|--------------|-----------------|--------|
| `# EPIC-{ID}:` | Epic | `epics/EPIC-{ID}.md` |
| `# Story {ID}:` | Story | `implementation-artifacts/{story}.md` |
| `### {STORY}-T{N}:` | Task | Embedded in story |
| Table row `\| T{N}-S{M} \|` | Sub-task | Embedded in task |

### What Does NOT Sync to JIRA

- Full epic documentation (`*-full.md`)
- AI implementation prompts
- Technical notes and references
- Dev agent records
- Historical audit trails

---

## Task Count Guidelines

| Story Points | Recommended Tasks | Max Subtasks per Task |
|--------------|-------------------|----------------------|
| 1-2 pts | 2-3 tasks | 3-4 subtasks |
| 3-5 pts | 3-5 tasks | 4-5 subtasks |
| 8+ pts | 5-8 tasks | 5-6 subtasks |

**If a story needs more than 8 tasks, consider splitting into multiple stories.**

---

## Confluence Integration

### Automatic Sync

Epic full documentation can be synced to Confluence:

```bash
/confluence-sync .bmad/planning-artifacts/epics/EPIC-AUTH-001-full.md
```

### Configuration

In `_bmad/config/atlassian-integration.yaml`:

```yaml
confluence:
  space_key: ARGUS
  epic_parent_page: "Epics Documentation"

document_mapping:
  .bmad/planning-artifacts/epics/*-full.md: "Epics/"
```

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-02 | Initial hierarchy definition | Claude Opus 4.5 |
