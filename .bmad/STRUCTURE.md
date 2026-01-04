# BMAD Directory Structure

> **Source of Truth** for all BMAD artifacts

## Directory Layout

```
.bmad/
├── STRUCTURE.md                        # THIS FILE - Structure definition
├── epics/                              # All epic and story content
│   └── {EPIC-ID}/                      # e.g., EPIC-AUTH-001/
│       ├── README.md                   # Epic summary (~30 lines) → JIRA Epic
│       ├── DOCUMENTATION.md            # Full docs (500+ lines) → Confluence
│       └── stories/
│           └── {NN}-{slug}/            # e.g., 01-api-key-schema/, 02a-secrets-provider/
│               ├── story-{NN}-{slug}.md  # Story definition (~100 lines) → JIRA Story
│               └── tasks/
│                   ├── task-01-{slug}.md  # Full AI prompt (~280 lines) → JIRA Task
│                   ├── task-02-{slug}.md
│                   └── ...
│
├── patterns/                           # Centralized code patterns
│   ├── index.md                        # Pattern registry
│   ├── rust-error-handling.md          # Error handling pattern
│   ├── rust-api-key.md                 # API key generation
│   ├── clickhouse-schema.md            # ClickHouse patterns
│   └── ...                             # Add patterns as discovered
│
├── templates/                          # File templates
│   ├── epic-summary.md                 # Epic summary (~30 lines) → JIRA
│   ├── story-readme.md                 # Story README (~100 lines) → JIRA
│   └── task.md                         # Task file (~280 lines) → JIRA
│
├── data/                               # Runtime data and handoffs
│   ├── jira-sync-state.yaml            # JIRA sync tracking
│   ├── jira-mappings.yaml              # Local ID → JIRA key mappings
│   └── HANDOFF-*.md                    # Session handoff documents
│
├── sprints/                            # Sprint tracking
│   ├── current.yaml                    # Current sprint status
│   └── archive/                        # Completed sprints
│
├── archive/                            # Archived content
│   ├── generated-stories/              # Original story files (pre-migration)
│   └── implementation-artifacts/       # Hand-crafted artifacts
│
└── config/                             # Configuration
    └── atlassian-integration.yaml      # JIRA/Confluence settings
```

---

## File Specifications

### Epic README.md (~30 lines) → JIRA Epic

```markdown
# {EPIC-ID}: {Epic Title}

**Status:** {status}
**Priority:** {priority}
**Owner:** {team}
**Stories:** {count} | **Points:** {total}

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | |
| Depends On | {EPIC-IDs} |
| Blocks | {EPIC-IDs} |

### Story Execution Order
```
{S1 → S2 → (S3, S4 parallel) → S5}
```

---

## Summary
{2-3 sentences}

## Business Value
- {value 1}
- {value 2}

## Acceptance Criteria
- [ ] {AC 1}
- [ ] {AC 2}

## Stories
| # | Story | Title | Pts | Sprint | Depends On | Status |
|---|-------|-------|-----|--------|------------|--------|
| 01 | [S1](./stories/01-slug/) | {title} | {pts} | {sprint} | - | pending |
| 02 | [S2](./stories/02-slug/) | {title} | {pts} | {sprint} | S1 | pending |
```

### Epic DOCUMENTATION.md (500+ lines) → Confluence

Full documentation including:
- Executive summary
- Problem statement
- Architecture decisions
- Technical constraints
- Risk assessment
- Implementation patterns
- Testing strategy
- AI implementation guide

### Story story-{NN}-{slug}.md (~50-100 lines) → JIRA Story

```markdown
# {STORY-ID}: {Story Title}

**Epic:** {EPIC-ID} | **Points:** {pts} | **Priority:** {priority} | **Sprint:** {sprint}
**Status:** {status}

---

## Coordination

| Field | Value |
|-------|-------|
| Worktree | `worktrees/{repo}-{story-slug}` |
| Branch | `{story-slug}` |
| Depends On | {STORY-IDs} |
| Blocks | {STORY-IDs} |
| JIRA Key | |

### Task Execution Order
```
{T1 → (T2, T3 parallel) → T4}
```

---

## Story
As a {role}, I want {action}, so that {benefit}.

## Business Value
**Value Statement:** {value statement}
**Success Metric:** {measurable metric}

## Acceptance Criteria

### AC1: {title}
**GIVEN** {context}
**WHEN** {action}
**THEN** {result}

### AC2: {title}
**GIVEN** {context}
**WHEN** {action}
**THEN** {result}

---

## Tasks

| # | Task File | Title | Linked AC | Status |
|---|-----------|-------|-----------|--------|
| T1 | [task-01-{slug}.md](./tasks/task-01-{slug}.md) | {title} | AC1 | pending |
| T2 | [task-02-{slug}.md](./tasks/task-02-{slug}.md) | {title} | AC2 | pending |

---

## Technical Notes
{Brief technical context}

### Key Files
- `{file_path_1}` - {purpose}
- `{file_path_2}` - {purpose}
```

### Task task-{NN}-{slug}.md (~280 lines) → JIRA Task

> **Note:** Tasks contain full AI Implementation Prompts for Claude execution.

```markdown
# {STORY-ID}-T{N}: {Task Title}

**Story:** {STORY-ID}
**Linked to:** {AC-N}
**Status:** pending

---

## Coordination

| Field | Value |
|-------|-------|
| Requires | {T1, T2 or "none"} |
| Unlocks | {T3, T4 or "none"} |
| Claimed By | |
| Claimed At | |
| JIRA Key | |

---

## Acceptance Criteria
{Full AC content in GIVEN/WHEN/THEN format}

---

## AI Implementation Prompt

You are implementing **{STORY-ID}-T{N}: {Task Title}** for the Armor Argus platform.

### Context
{Story statement}

### This Task
Implement {AC-N}: {Task Title}
{AC content}

---

## Target Files
```
{exact file paths}
```

---

## Code Patterns
{Code patterns with actual examples}

---

## Anti-Patterns (FORBIDDEN)

| Anti-Pattern | Why It's Wrong | Do Instead |
|--------------|----------------|------------|
| {anti-pattern} | {reason} | {alternative} |

---

## Edge Cases

| Edge Case | Expected Behavior | Test |
|-----------|-------------------|------|
| {edge case} | {behavior} | {test} |

---

## Security Considerations

| Threat | Mitigation | Verified |
|--------|------------|----------|
| {threat} | {mitigation} | [ ] |

---

## Testing Requirements

### Unit Tests
| Component | Test File | Coverage Target |
|-----------|-----------|-----------------|
| {component} | {test file} | 90% |

### Verification Commands
```bash
{commands to verify implementation}
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| {package} | {version} | {purpose} |

---

## Subtasks

| # | Description | Status |
|---|-------------|--------|
| S1 | {subtask 1} | pending |
| S2 | {subtask 2} | pending |
| S3 | {subtask 3} | pending |

---

## Handoff Notes

*Populated on task completion for next task*

### What Was Built
-

### Files Created/Modified
| File | Action | Notes |
|------|--------|-------|

### Context for Next Task
-

---

## Done When

- [ ] {AC-N} acceptance criteria met
- [ ] All subtasks completed
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Security considerations verified
- [ ] Handoff notes written
```

---

## Naming Conventions

### Epic IDs
- Format: `EPIC-{PREFIX}-{NUM}` or `EPIC-{NUM}-{NAME}`
- Examples: `EPIC-AUTH-001`, `EPIC-1-PLATFORM`, `EPIC-5-UX`

### Story Folders
- Format: `{NN}-{slug}/` where NN is zero-padded sequence
- Use letters for parallel stories: `02a-`, `02b-`
- Slug is kebab-case summary of story
- Examples:
  - `01-api-key-schema/`
  - `02a-secrets-provider-abstraction/`
  - `02b-auth-gateway-service/`
  - `03-scanner-config-ui/`

### Story IDs (derived from folder)
- Format: `{EPIC-PREFIX}-{NUM}` or `{EPIC-PREFIX}-{NUM}{letter}`
- Path: `.bmad/epics/EPIC-AUTH-001/stories/02a-secrets-provider/` → Story ID: `AUTH-001-2a`
- Examples: `AUTH-001-1`, `AUTH-001-2a`, `PLAT-1`, `UX-42`

### Task Files
- Format: `task-{NN}-{slug}.md` where NN is zero-padded sequence
- Slug describes what the task accomplishes
- Examples:
  - `task-01-create-migration.md`
  - `task-02-implement-hmac-verification.md`
  - `task-03-add-audit-logging.md`

### Task IDs (derived from file)
- Format: `{STORY-ID}-T{NUM}`
- Examples: `AUTH-001-2a-T1`, `PLAT-1-T3`

### Subtask IDs
- Format: `T{NUM}-S{NUM}` (embedded in task file tables)
- Examples: `T1-S1`, `T1-S2`, `T2-S1`

---

## JIRA Mapping

| BMAD Path | JIRA Issue Type | Sync Direction |
|-----------|-----------------|----------------|
| `epics/{EPIC}/README.md` | Epic | ↔ Bidirectional |
| `epics/{EPIC}/stories/{NN}-{slug}/story-{NN}-{slug}.md` | Story | ↔ Bidirectional |
| `epics/{EPIC}/stories/{NN}-{slug}/tasks/task-{NN}-{slug}.md` | Task | ↔ Bidirectional |
| Subtask table rows in task files | Sub-task | ↔ Bidirectional |
| `epics/{EPIC}/DOCUMENTATION.md` | N/A | → Confluence only |

### JIRA Link Types for Dependencies

| Local Field | JIRA Link Type | Direction | Example |
|-------------|----------------|-----------|---------|
| Epic `Depends On` | Blocks | Inward | Epic 2 "is blocked by" Epic 1 |
| Epic `Blocks` | Blocks | Outward | Epic 1 "blocks" Epic 2 |
| Story `Depends On` | Blocks | Inward | Story 2 "is blocked by" Story 1 |
| Story `Blocks` | Blocks | Outward | Story 1 "blocks" Story 2 |
| Task `Requires` | Blocks | Inward | T2 "is blocked by" T1 |
| Task `Unlocks` | Blocks | Outward | T1 "blocks" T2 |
| Story → Epic | Epic Link | - | Story belongs to Epic |

---

## Confluence Mapping

| BMAD Path | Confluence Page |
|-----------|-----------------|
| `epics/{EPIC}/DOCUMENTATION.md` | "{EPIC-ID}: {Title}" under "Epic Documentation" |

---

## Multi-Agent Coordination

This structure supports multiple engineers and Claude instances working in parallel.

### Source of Truth

| Data Type | Source of Truth | Sync To |
|-----------|-----------------|---------|
| Content (prompts, code patterns, ACs) | Task files | JIRA description |
| Status (pending, in_progress, done) | JIRA | Task files |
| Dependencies (requires/unlocks) | Task files | JIRA links |
| Claims (who is working on what) | Task files | - |

### Coordination Fields

#### Epic Level
- **Depends On:** List of Epic IDs this epic depends on
- **Blocks:** List of Epic IDs this epic blocks
- **Story Execution Order:** Visual flow showing story sequence

#### Story Level
- **Worktree:** Git worktree path for this story's feature branch
- **Branch:** Git branch name
- **Depends On:** List of Story IDs this story depends on
- **Blocks:** List of Story IDs this story blocks
- **Task Execution Order:** Visual flow showing task sequence

#### Task Level
- **Requires:** List of Task IDs that must complete before this task
- **Unlocks:** List of Task IDs that are waiting for this task
- **Claimed By:** Session ID or engineer name currently working on this
- **Claimed At:** ISO timestamp when claimed
- **JIRA Key:** JIRA issue key for bidirectional sync

### Multi-Agent Execution Protocol

1. **Claim Before Starting**
   - Check `Claimed By` field before starting any task
   - If empty, set to your session ID and current timestamp
   - If already claimed, choose a different task

2. **Respect Dependencies**
   - Check `Requires` field for prerequisite tasks
   - All required tasks must have `status: completed`
   - Do not start blocked tasks

3. **Update On Completion**
   - Mark task status as `completed`
   - Write `Handoff Notes` for next task
   - Clear `Claimed By` field
   - Update dependent tasks' status if now unblocked

4. **Handoff Protocol**
   When completing a task, populate the Handoff Notes section:
   - **What Was Built:** Summary of implementation
   - **Files Created/Modified:** Table of changes
   - **Context for Next Task:** What the next engineer needs to know

### Parallel Execution Rules

| Scenario | Allowed? | Notes |
|----------|----------|-------|
| Two agents on same task | ❌ No | Use claim mechanism |
| Two agents on parallel tasks (no deps) | ✅ Yes | Different worktrees |
| Agent on T2 while T1 incomplete (T2 requires T1) | ❌ No | Respect dependencies |
| Agent on T3 while T2 in progress (T3 requires T2) | ❌ No | Wait for completion |

### Git Worktree Pattern

Each story maps to a dedicated worktree:

```
armor-argus/
├── submodules/           # main branches only
│   ├── argus-common/
│   └── argus-api/
└── worktrees/            # feature branches
    ├── argus-common-auth-001-1/   # branch: auth-001-1-api-key-schema
    └── argus-api-auth-001-2/      # branch: auth-001-2-auth-gateway
```

Story files specify:
- `Worktree: worktrees/{repo}-{story-slug}`
- `Branch: {story-slug}`

---

## Workflow Integration

### Creating an Epic
1. Create folder: `.bmad/epics/EPIC-{ID}/`
2. Create `README.md` from template (`.bmad/templates/epic-readme.md`)
3. Create `DOCUMENTATION.md` from template (`.bmad/templates/epic-documentation.md`)
4. Create `stories/` folder
5. Run `/jira-sync` to create Epic in JIRA

### Creating a Story
1. Determine next story number and create folder: `.bmad/epics/{EPIC}/stories/{NN}-{slug}/`
2. Create `story-{NN}-{slug}.md` from template (`.bmad/templates/story-readme.md`)
3. Create `tasks/` folder
4. Create task files: `tasks/task-01-{slug}.md`, `tasks/task-02-{slug}.md`, etc. from template
5. Run `/jira-sync` to create Story + Tasks + Sub-tasks in JIRA

### Updating Progress
1. Update status in relevant files
2. Run `/jira-sync` to push changes
3. Update sprint tracking in `.bmad/sprints/current.yaml`

### Workflows That Use This Structure
- `_bmad/bmm/workflows/3-solutioning/create-epics-and-stories/` - Epic & story creation
- `_bmad/bmm/workflows/4-implementation/create-story/` - Individual story creation
- `_bmad/bmm/workflows/4-implementation/dev-story/` - Story development
- `_bmad/bmm/workflows/4-implementation/sprint-planning/` - Sprint assignment
- `_bmad/bmm/workflows/jira-sync/` - JIRA synchronization

---

## Migration from Old Structure

Old locations → New locations:
- `.bmad/planning-artifacts/epics/EPIC-*-summary.md` → `.bmad/epics/{EPIC}/README.md`
- `.bmad/planning-artifacts/epics/EPIC-*-full.md` → `.bmad/epics/{EPIC}/DOCUMENTATION.md`
- `.bmad/implementation-artifacts/{story}.md` → `.bmad/epics/{EPIC}/stories/{NN}-{slug}/story-{NN}-{slug}.md`
- Inline tasks in story files → `.bmad/epics/{EPIC}/stories/{NN}-{slug}/tasks/task-{NN}-{slug}.md`

### Migration Script
Run `scripts/migrate-to-new-structure.py` to automatically migrate existing content.

---

## Version

**Structure Version:** 3.0
**Last Updated:** 2026-01-02
**Author:** Claude Opus 4.5

### Changelog

- **v3.0** (2026-01-02): Added multi-agent coordination (requires/unlocks, claim mechanism, handoff protocol), JIRA link type mapping, execution order fields
- **v2.0** (2026-01-02): Renamed files (story-{slug}.md, task-{slug}.md), migrated to full AI prompts in tasks
- **v1.0** (2026-01-01): Initial structure with epics, stories, tasks hierarchy
