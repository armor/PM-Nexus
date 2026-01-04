# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

UI-Uplift is a project focused on uplifting the UI of the Armor platform. It coordinates work across two main repositories via git submodules, with PRDs managed in Jira/Confluence.

## Repository Structure

This is a parent monorepo that coordinates multiple submodules. The parent repo owns BMad workflows, scripts, and deployment configs; submodules are independent repos.

### Key Directories

| Directory | Purpose | Editability |
|-----------|---------|-------------|
| `_bmad/` | BMAD framework (agents, workflows, templates) | Framework config |
| `.bmad/` | BMAD output (PRD, epics, stories, artifacts) | Editable |
| `scripts/` | Jira sync and automation scripts | Editable |
| `submodules/` | Git submodules (platform, Armor-Dash, MCP) | Via worktrees |

### Submodules

| Submodule | Language | Purpose |
|-----------|----------|---------|
| `platform` | TypeScript/React | Main Armor platform UI (github.com/armor/platform) |
| `Armor-Dash` | TypeScript/React | Armor dashboard UI (github.com/frankentini/Armor-Dash) |
| `argus-jira-mcp` | TypeScript | MCP server for Jira integration |

## Git Worktree Pattern (MANDATORY)

**ALL feature development MUST use git worktrees.** This is non-negotiable.

### Directory Structure

```
UI-Uplift/
├── submodules/                    # Main branches ONLY (stable, reference)
│   ├── platform/                  # main branch
│   ├── Armor-Dash/                # main branch
│   └── argus-jira-mcp/            # Jira MCP server
│
└── worktrees/                     # Feature branches (story-named)
    ├── platform-ui-001-2/         # branch: ui-001-2-component-library
    ├── armor-dash-ui-001-3/       # branch: ui-001-3-dashboard-redesign
    └── ...
```

### Rules

1. **NEVER commit feature work directly to main in `submodules/`**
2. **ALWAYS create a worktree for feature/story development**
3. **Worktree names MUST match story IDs from `.bmad/implementation-artifacts/sprint-status.yaml`**

### Commands

```bash
# Create worktree for a story
cd submodules/platform
git worktree add ../../worktrees/platform-{story-prefix} -b {full-story-id}

# List worktrees
git worktree list

# Remove worktree after merge
git worktree remove ../../worktrees/platform-{story-prefix}
```

## Development Commands

### Prerequisites
- Node.js 20+
- Docker & Docker Compose (optional)

### Local Development
```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>

# Or initialize submodules after clone
git submodule update --init --recursive

# Start platform UI (separate terminal)
cd submodules/platform
nvm use
npm install
npm run dev

# Start Armor-Dash (separate terminal)
cd submodules/Armor-Dash
nvm use
npm install
npm run dev
```

### Testing
```bash
# UI unit tests
npm test

# E2E tests
npm run test:e2e
```

## BMad Method Architecture

### Module Configuration
- `_bmad/_config/manifest.yaml` - Installed modules: core, bmb, bmm, cis
- `_bmad/core/config.yaml` - User config (user_name, language, output folder)

### Key Agents (invoke via skill commands)
| Agent | Role | Use When |
|-------|------|----------|
| bmad-master | Workflow orchestrator | Starting any BMad workflow |
| pm (John) | Product Manager | Creating PRDs, requirements |
| architect (Winston) | System Architect | Technical design, architecture docs |
| dev (Amelia) | Developer | Implementing stories |
| sm (Bob) | Scrum Master | Story preparation, sprint planning |
| tea (Murat) | Test Architect | Test strategy, quality gates |
| ux-designer (Sally) | UX Designer | UI/UX design and patterns |
| quick-flow-solo-dev (Barry) | Quick Flow Dev | Fast tech spec + implementation |

### Key Workflows
| Workflow | Purpose |
|----------|---------|
| `create-product-brief` | Initial product analysis |
| `create-prd` | Collaborative PRD creation |
| `create-architecture` | System architecture decisions |
| `create-epics-and-stories` | PRD to actionable stories |
| `dev-story` | Execute story implementation |
| `code-review` | Adversarial code review |
| `jira-sync` | Sync stories with Jira |

## Jira Integration

### MCP Server
The Jira MCP server is located at `submodules/argus-jira-mcp/` and provides:
- Issue creation and updates
- Epic/Story/Task hierarchy management
- Confluence page access

### Sync Scripts
Located in `scripts/`:
- `jira-sync-all.py` - Full bidirectional sync
- `jira-bulk-sync.py` - Bulk operations
- `markdown_to_adf.py` - Convert markdown to Atlassian format

## Definition of Done

A story is complete when:
- Code merged to main with review
- Unit tests passing
- E2E tests passing at 100% (see E2E requirements below)
- No breaking changes without version bump
- Evidence artifacts generated

## E2E Testing Gate (NON-NEGOTIABLE)

> **E2E tests MUST be 100% passing at all times. No exceptions.**

### Required Verification Layers (ALL MANDATORY)

| Layer | What to Verify | How to Verify |
|-------|----------------|---------------|
| **1. Network Requests** | API calls were made with correct data | `page.waitForResponse()`, intercept and inspect |
| **2. HTTP Status** | Requests succeeded (200/201) | Check `response.status()` |
| **3. Persistence** | Data survived a page reload | Reload page, verify data still visible |
| **4. Console Errors** | Zero console.error() calls | Capture with `page.on('console')` |
| **5. Network Errors** | No 4xx/5xx responses | Monitor all responses |

### Deep Testing Patterns (REQUIRED)

```typescript
// BAD - Tests nothing meaningful (FORBIDDEN)
await saveButton.click();
await expect(toast).toContainText('Success'); // LIES!

// GOOD - Proves API was called with correct data
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes('/api/') && r.request().method() === 'PUT'),
  saveButton.click()
]);
expect(response.status()).toBe(200);

// BEST - Proves persistence (data survives reload)
await page.reload();
await expect(page.getByText(savedValue)).toBeVisible();
```

## Key Documentation

| Document | Location |
|----------|----------|
| **Implementation Rules** | `CLAUDE_RULES.md` |
| **BMAD Structure** | `.bmad/STRUCTURE.md` |
| **Git Worktree Pattern** | `.bmad/WORKTREE_PATTERN.md` |
| Sprint Status | `.bmad/implementation-artifacts/sprint-status.yaml` |
| Jira Sync Workflow | `scripts/JIRA_SYNC_WORKFLOW.md` |
