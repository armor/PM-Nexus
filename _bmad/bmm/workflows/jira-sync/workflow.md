# JIRA Integration Workflows

> **Structure Reference:** `.bmad/STRUCTURE.md`

## File Structure Mapping (NEW)

```
.bmad/epics/                          → JIRA
├── {EPIC-ID}/
│   ├── README.md                     → Epic (summary, ~30 lines)
│   ├── DOCUMENTATION.md              → Confluence page (500+ lines)
│   └── stories/
│       └── {NN}-{slug}/              → Story folder
│           ├── story-{NN}-{slug}.md  → Story (~50 lines)
│           └── tasks/
│               └── task-{NN}-{slug}.md → Task (~30 lines, subtasks in table)
```

**Naming Convention:**
- Epic folders: `EPIC-AUTH-001`, `EPIC-1-PLATFORM`
- Story folders: `01-api-key-schema`, `02a-secrets-provider`
- Story files: `story-01-api-key-schema.md`, `story-02a-secrets-provider.md`
- Task files: `task-01-create-migration.md`, `task-02-implement-hmac.md`

## Components

| Command | Type | Purpose |
|---------|------|---------|
| `/jira-sync` | Manual | Bidirectional sync |
| `jira-watcher` | Background | Watch for new JIRA issues |
| `/jira-inbox` | Manual | List pending stories |
| `/jira-approve` | Manual | Approve story to epic |
| `/jira-reject` | Manual | Reject with feedback |

---

## 1. Manual Sync (`/jira-sync`)

Bidirectional sync between BMAD and JIRA.

```bash
/jira-sync                    # Sync all epics in .bmad/epics/
/jira-sync EPIC-AUTH-001      # Sync one epic
/jira-sync --dry-run          # Preview
/jira-sync --force-push       # BMAD wins
/jira-sync --force-pull       # JIRA wins
```

---

## 2. Watcher Process

Polls JIRA every 5 minutes for new issues.

```bash
./scripts/jira-watcher.sh start   # Start
./scripts/jira-watcher.sh stop    # Stop
./scripts/jira-watcher.sh status  # Check
```

New issues are standardized and staged in `_bmad/inbox/`.

---

## 3. Inbox Review (`/jira-inbox`)

List pending stories awaiting approval.

```bash
/jira-inbox
```

Output:
```
Pending (3):
  ARGUS-150  Add user login       P1  3pts  2h ago
  ARGUS-151  Password reset       P2  2pts  1h ago
  ARGUS-152  OAuth integration    P1  5pts  30m ago
```

---

## 4. Approve Story (`/jira-approve`)

Move story from inbox to epic, creating proper folder structure.

```bash
/jira-approve ARGUS-150 --epic EPIC-AUTH-001
```

Actions:
1. Validates acceptance criteria filled
2. Creates story folder: `.bmad/epics/EPIC-AUTH-001/stories/{NN}-{slug}/`
3. Creates `story-{NN}-{slug}.md` from `.bmad/templates/story-readme.md`
4. Creates `tasks/` directory with task files (`task-{NN}-{slug}.md`) from `.bmad/templates/task.md`
5. Updates JIRA with standardized format
6. Removes from inbox

**Folder Naming:**
- Determines next story number (e.g., `05`)
- Converts title to kebab-case slug
- Result: `05-add-user-login/`

---

## 5. Reject Story (`/jira-reject`)

Send back to PM with feedback.

```bash
/jira-reject ARGUS-150 --reason "Needs acceptance criteria"
```

Actions:
1. Comments on JIRA issue
2. Adds label: `needs-refinement`
3. Archives to `_bmad/rejected/`

---

## Story Template (Inbox)

When watcher detects new JIRA issue, it creates in `_bmad/inbox/`:

```markdown
# ARGUS-150: Add user login

**JIRA:** [ARGUS-150](https://site.atlassian.net/browse/ARGUS-150)
**Status:** To Do | **Priority:** P1 | **Points:** 3
**Reporter:** pm@company.com | **Created:** 2026-01-01

---

## Description (from JIRA)

[Original JIRA description here]

---

## Acceptance Criteria (REQUIRED)

### AC-1: _Fill in title_
```gherkin
GIVEN _context_
WHEN _action_
THEN _result_
```

### AC-2: _Fill in title_
```gherkin
GIVEN _context_
WHEN _action_
THEN _result_
```

---

## Technical Notes

_Add after approval_

---

## Approval Checklist

- [ ] Acceptance criteria complete (GHERKIN format)
- [ ] Epic assigned
- [ ] Tasks identified
- [ ] Reviewed

`/jira-approve ARGUS-150 --epic EPIC-AUTH-001`
```

**After Approval**, files are created:
- `.bmad/epics/EPIC-AUTH-001/stories/05-add-user-login/story-05-add-user-login.md`
- `.bmad/epics/EPIC-AUTH-001/stories/05-add-user-login/tasks/task-01-*.md`

---

## 6. Dependency Sync

When syncing epics, stories, and tasks, the workflow MUST also sync dependency links to JIRA.

### JIRA Link Types

| Local Field | JIRA Link Type | Direction | Example |
|-------------|----------------|-----------|---------|
| Epic `Depends On` | Blocks | Inward | Epic 2 "is blocked by" Epic 1 |
| Epic `Blocks` | Blocks | Outward | Epic 1 "blocks" Epic 2 |
| Story `Depends On` | Blocks | Inward | Story 2 "is blocked by" Story 1 |
| Story `Blocks` | Blocks | Outward | Story 1 "blocks" Story 2 |
| Task `Requires` | Blocks | Inward | T2 "is blocked by" T1 |
| Task `Unlocks` | Blocks | Outward | T1 "blocks" T2 |
| Story → Epic | Epic Link | - | Story belongs to Epic |

### Dependency Sync Process

1. **Parse coordination section** from each file:
   - Epic: `Depends On`, `Blocks` fields
   - Story: `Depends On`, `Blocks` fields
   - Task: `Requires`, `Unlocks` fields

2. **Resolve local IDs to JIRA keys**:
   - `T1` → look up JIRA key in `task-01-*.md` Coordination table
   - `S2` → look up JIRA key in `story-02-*.md` Coordination table
   - Store mappings in `.bmad/data/jira-mappings.yaml`

3. **Create JIRA links using Atlassian MCP**:
   ```
   For "Requires: T1" in task-02:
     - Find JIRA key for T1 (e.g., ARGUS-201)
     - Find JIRA key for T2 (e.g., ARGUS-202)
     - Create link: ARGUS-202 "is blocked by" ARGUS-201

   For "Unlocks: T3, T4" in task-02:
     - Create link: ARGUS-202 "blocks" ARGUS-203
     - Create link: ARGUS-202 "blocks" ARGUS-204
   ```

4. **Handle missing JIRA keys**:
   - If referenced item has no JIRA key, create the issue first
   - Then create the link
   - Update local file with new JIRA key

### Atlassian MCP API for Links

The Atlassian MCP server supports creating issue links via the REST API:

```
POST /rest/api/3/issueLink
{
  "type": { "name": "Blocks" },
  "inwardIssue": { "key": "ARGUS-201" },   // The blocker
  "outwardIssue": { "key": "ARGUS-202" }   // The blocked
}
```

**Important:** The inward/outward terminology:
- `inwardIssue` = the blocker (T1 blocks T2, so T1 is inward)
- `outwardIssue` = the blocked (T2 is blocked by T1, so T2 is outward)

### Link Validation

During sync, validate:
1. All dependency links in JIRA match local coordination fields
2. No orphan links (links to deleted issues)
3. No circular dependencies (A blocks B blocks A)

Report discrepancies:
```
LINK MISMATCH:
  Local: task-02 requires T1
  JIRA: ARGUS-202 has no "is blocked by" link to ARGUS-201
  Action: Creating missing link
```

---

## Configuration

See `_bmad/config/atlassian-integration.yaml`

**MCP Server:** https://github.com/atlassian/atlassian-mcp-server
