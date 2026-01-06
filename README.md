# UI-Uplift: Product Management Command Center

> **Get up and running in 20 minutes.** This repo is your single source of truth for product requirements, epics, stories, and tasks—synced to Jira and Confluence.

---

## Quick Start (20 Minutes)

### Step 1: Clone & Setup (5 min)

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd UI-Uplift

# Or if already cloned:
git submodule update --init --recursive
```

### Step 2: Setup Jira MCP Server (10 min)

The Jira MCP server lets Claude sync your work to Jira/Confluence automatically.

#### Get Your Jira API Token First

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it: `Claude Code - UI-Uplift`
4. Click **"Create"**
5. **Copy the token immediately** (you can't see it again!)

#### Configure the Server

```bash
# Create your .env from the template
cp .env.example .env
```

Edit `.env` with your credentials:

```env
JIRA_HOST=your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=<paste-your-token-here>
JIRA_DEFAULT_PROJECT=STAGE
```

> See [.env.example](.env.example) for detailed instructions and troubleshooting.

#### Build the Jira Server

```bash
# Navigate to jira-mcp
cd submodules/jira-mcp

# Install dependencies
npm install

# Also create .env here (or symlink to root)
cp ../../.env .env

# Build the server
npm run build

# Test it works
npm start
# Should see: "Armor Jira MCP Server running on stdio"
# Press Ctrl+C to stop
```

### Step 3: Configure Claude Code (5 min)

Add to your `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "node",
      "args": ["/path/to/UI-Uplift/submodules/jira-mcp/dist/index.js"],
      "env": {
        "JIRA_HOST": "your-company.atlassian.net",
        "JIRA_EMAIL": "your.email@company.com",
        "JIRA_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Done!** You can now ask Claude to sync epics/stories to Jira.

---

## What This Repo Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI-UPLIFT COMMAND CENTER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   .bmad/epics/          docs/              Jira + Confluence    │
│   ┌──────────┐         ┌──────────┐        ┌──────────┐         │
│   │ Epics    │ ──────> │ PRDs     │ ─────> │ Projects │         │
│   │ Stories  │         │ Specs    │        │ Boards   │         │
│   │ Tasks    │         │ Design   │        │ Pages    │         │
│   └──────────┘         └──────────┘        └──────────┘         │
│        │                    │                   │                │
│        └────────────────────┴───────────────────┘                │
│                    SINGLE SOURCE OF TRUTH                        │
└─────────────────────────────────────────────────────────────────┘
```

| Component | Purpose | You Write Here |
|-----------|---------|----------------|
| `.bmad/epics/` | Epic/Story/Task definitions | Yes |
| `docs/` | PRDs, specs, architecture | Yes |
| Jira | Sprint boards, tracking | Auto-synced |
| Confluence | Published documentation | Auto-synced |

---

## Project Structure

```
UI-Uplift/
├── README.md                 # You are here
├── CLAUDE.md                 # Claude Code instructions
│
├── .bmad/                    # YOUR WORK GOES HERE
│   ├── epics/                # Epic portfolio (15 epics)
│   │   ├── README.md         # Portfolio overview
│   │   ├── EPIC-1-NEXUS-NAVIGATION/
│   │   │   ├── README.md     # Epic overview
│   │   │   └── stories/      # Story details
│   │   │       └── 01-fix-duplicate-route/
│   │   │           ├── story-01-*.md
│   │   │           └── tasks/
│   │   │               └── task-01-*.md
│   │   └── EPIC-2-NEXUS-STABILITY/
│   │       └── ...
│   ├── diagrams/             # Mermaid/Excalidraw source
│   ├── diagrams-svg/         # Rendered SVG exports
│   └── implementation-artifacts/
│       └── jira-sync-state.yaml
│
├── docs/                     # DOCUMENTATION
│   ├── nexus-ui-uplift/      # Platform project docs
│   │   ├── product/          # PRDs, gap analysis
│   │   ├── architecture/     # System design
│   │   └── design/           # UX specs
│   ├── armor-dash/           # Dashboard project docs
│   └── shared/               # Cross-project standards
│       ├── design-system.md  # Colors, typography, spacing
│       ├── component-library.md
│       └── testing-strategy.md
│
├── _bmad/                    # BMAD Framework (don't edit)
│   ├── agents/               # AI agent definitions
│   ├── templates/            # Document templates
│   └── core/config.yaml      # Your settings
│
├── submodules/               # Git submodules
│   ├── platform/             # Main codebase
│   ├── Armor-Dash/           # Dashboard codebase
│   └── jira-mcp/             # Jira sync server
│
└── scripts/                  # Automation scripts
```

---

## The .bmad/epics Structure

This is where you define **what gets built**. Everything here syncs to Jira.

### Epic Hierarchy

```
EPIC (Jira Epic)
└── STORY (Jira Story)
    └── TASK (Jira Sub-task)
```

### File Naming Convention

```
.bmad/epics/
├── EPIC-{N}-{NAME}/
│   ├── README.md                          # Epic overview (required)
│   └── stories/                           # Optional: detailed breakdown
│       └── {NN}-{slug}/
│           ├── story-{NN}-{slug}.md       # Story details
│           └── tasks/
│               └── task-{NN}-{name}.md    # Task details
```

### Epic README Template

Every epic needs a `README.md` with this structure:

```markdown
# EPIC-{N}: {NAME}

**Status:** Ready for Sprint X
**Priority:** P0 - Critical | P1 - High | P2 - Medium
**Owner:** Team Name
**MVP:** MVP 1 | MVP 2 | MVP 3
**Total Stories:** X | **Total Points:** Xpt

---

## Summary
What this epic delivers (2-3 sentences).

---

## Business Value
- **Benefit 1** - Why it matters
- **Benefit 2** - Why it matters

---

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---

## Stories

| ID | Title | Points | Sprint |
|----|-------|--------|--------|
| {NAME}-001 | Story title | 3pt | Sprint 1 |
| {NAME}-002 | Story title | 2pt | Sprint 1 |

---

## Technical Context
Key files, dependencies, design system references.

---

## Confluence Documentation
| Document | Link |
|----------|------|
| Parent Page | [Link](https://...) |
| PRD | [Link](https://...) |
```

### Story File Template

```markdown
# {EPIC}-{NNN}: {Title}

**Story ID:** {EPIC}-{NNN}
**Epic:** EPIC-{N}-{NAME}
**Points:** X
**Sprint:** Sprint X

---

## User Story
**As a** [user type],
**I want** [goal],
**So that** [benefit].

---

## Acceptance Criteria
- [ ] **AC1:** Specific, testable criterion
- [ ] **AC2:** Specific, testable criterion

---

## Technical Context
Files to modify, dependencies, patterns to follow.

---

## Tasks
| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | What to do | 30min |
| task-02 | What to do | 1h |
```

---

## Common PM Tasks

### Create a New Epic

1. Create folder: `.bmad/epics/EPIC-{N}-{NAME}/`
2. Create `README.md` using template above
3. Ask Claude: *"Sync EPIC-{N} to Jira project STAGE"*

### Add Stories to an Epic

1. Create folder: `.bmad/epics/EPIC-{N}-{NAME}/stories/{NN}-{slug}/`
2. Create `story-{NN}-{slug}.md`
3. Ask Claude: *"Sync stories for EPIC-{N} to Jira"*

### Sync Everything to Jira

Ask Claude:
```
Sync .bmad/epics to Jira project STAGE.
Create any missing epics, stories, and subtasks.
Update descriptions from the markdown files.
```

### Push Documentation to Confluence

Ask Claude:
```
Create a Confluence page for EPIC-{N} under the Nexus UI Uplift space.
Include the full epic README content.
```

### Check Sync Status

Ask Claude:
```
Compare .bmad/epics with Jira project STAGE.
Show me what's missing or out of sync.
```

---

## Jira MCP Commands Reference

Once configured, Claude can use these Jira tools:

| Action | What It Does |
|--------|--------------|
| `search_issues` | Query Jira with JQL |
| `get_issue` | Get full issue details |
| `update_issue` | Update description (accepts Markdown) |
| `add_comment` | Add comment (accepts Markdown) |
| `create_issue_link` | Link issues (Blocks, Relates) |
| `set_epic_link` | Link story to epic |
| `create_subtask` | Add subtask to story |
| `create_remote_link` | Add web link to issue |
| `get_confluence_spaces` | List Confluence spaces |
| `create_confluence_page` | Create page (accepts Markdown) |
| `update_confluence_page` | Update page content |

### Example Prompts

```
"Create epic STAGE-100 with title 'New Feature' and description from .bmad/epics/EPIC-16/README.md"

"Add a 'Blocks' link from STAGE-16 to STAGE-18"

"Get all stories under epic STAGE-1"

"Create subtasks for STAGE-16 based on the tasks in the story file"

"Create a Confluence page titled 'EPIC-1 Overview' with content from the epic README"
```

---

## Documentation Standards

### docs/ Directory Structure

```
docs/
├── {project}/
│   ├── product/              # Business docs
│   │   ├── {name}-prd.md     # Product requirements
│   │   ├── gap-analysis.md   # Current vs desired state
│   │   └── roadmap.md        # Timeline
│   │
│   ├── architecture/         # Technical docs
│   │   ├── system-design.md  # High-level architecture
│   │   ├── data-model.md     # Database schemas
│   │   └── api-design.md     # API contracts
│   │
│   ├── design/               # UX docs
│   │   ├── ux-requirements.md
│   │   ├── wireframes/       # Low-fi designs
│   │   └── mockups/          # High-fi designs
│   │
│   └── testing/              # QA docs
│       └── test-strategy.md
│
└── shared/                   # Cross-project standards
    ├── design-system.md      # Colors, typography, spacing
    ├── component-library.md  # Shared components
    └── testing-strategy.md   # Testing patterns
```

### Document Naming

| Type | Pattern | Example |
|------|---------|---------|
| PRD | `{project}-prd.md` | `nexus-prd.md` |
| Architecture | `{topic}-architecture.md` | `auth-architecture.md` |
| Spec | `{feature}-spec.md` | `dashboard-spec.md` |
| Guide | `{topic}-guide.md` | `onboarding-guide.md` |

### Markdown Standards

1. **Front Matter** - Always include metadata at top:
   ```markdown
   # Document Title

   > **Version:** 1.0
   > **Last Updated:** 2026-01-05
   > **Status:** Draft | Review | Approved
   > **Owner:** Name
   ```

2. **Headers** - Use consistent hierarchy:
   - `#` - Document title (one per doc)
   - `##` - Major sections
   - `###` - Subsections
   - `####` - Details (use sparingly)

3. **Tables** - Use for structured data:
   ```markdown
   | Column 1 | Column 2 |
   |----------|----------|
   | Data | Data |
   ```

4. **Diagrams** - Store in `.bmad/diagrams/`, export SVG to `.bmad/diagrams-svg/`

---

## BMAD Framework Overview

BMAD (Business Model Agile Delivery) provides the structure for this repo.

### Installed Modules

| Module | Purpose |
|--------|---------|
| `core` | Base configuration |
| `bmb` | Business Model Builder |
| `bmm` | Business Model Management |
| `cis` | Creative Innovation System |

### Configuration

Your settings in `_bmad/core/config.yaml`:

```yaml
user_name: Your Name
communication_language: English
document_output_language: English
output_folder: "{project-root}/.bmad"
```

### Available Agents

BMAD provides AI agents you can invoke:

| Agent | Role | When to Use |
|-------|------|-------------|
| `pm` (John) | Product Manager | Creating PRDs, requirements |
| `architect` (Winston) | System Architect | Technical design |
| `sm` (Bob) | Scrum Master | Sprint planning, story prep |
| `ux-designer` (Sally) | UX Designer | UI/UX patterns |
| `dev` (Amelia) | Developer | Implementation guidance |

---

## Current Portfolio

| Metric | Value |
|--------|-------|
| **Epics** | 15 |
| **Stories** | 143 |
| **Story Points** | 465pt |
| **Sprints** | 15 |

### Priority Breakdown

| Priority | Epics | Points | MVP |
|----------|-------|--------|-----|
| P0 Critical | 8 | 289pt | MVP 1 |
| P1 High | 4 | 136pt | MVP 2 |
| P2 Medium | 3 | 39pt | MVP 3 |

See [.bmad/epics/README.md](.bmad/epics/README.md) for full portfolio details.

---

## Troubleshooting

### "Jira API returns 401 Unauthorized"

1. Verify email matches your Atlassian account
2. Regenerate API token at https://id.atlassian.com/manage-profile/security/api-tokens
3. Check `.env` has no extra spaces

### "Epic Link field not found"

Different Jira instances use different field names. Ask Claude:
```
List all custom fields in Jira project STAGE
```

### "Can't create subtasks"

Your project may use a different subtask type name. Ask Claude:
```
What issue types are available in project STAGE?
```

### "MCP server not connecting"

1. Verify path in `~/.claude/mcp.json` is absolute
2. Rebuild: `cd submodules/jira-mcp && npm run build`
3. Restart Claude Code

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                     PM QUICK REFERENCE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CREATE EPIC        .bmad/epics/EPIC-N-NAME/README.md           │
│  ADD STORY          .bmad/epics/EPIC-N/stories/NN-slug/         │
│  VIEW PORTFOLIO     .bmad/epics/README.md                       │
│  CHECK DOCS         docs/{project}/{category}/                   │
│  DESIGN SYSTEM      docs/shared/design-system.md                │
│                                                                  │
│  SYNC TO JIRA       "Sync .bmad/epics to Jira project STAGE"    │
│  CHECK STATUS       "Compare .bmad/epics with STAGE project"    │
│  CREATE PAGE        "Push EPIC-N README to Confluence"          │
│                                                                  │
│  JIRA PROJECT       STAGE                                        │
│  CONFLUENCE         armor-defense.atlassian.net/wiki            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Getting Help

- **This README** - Start here
- **[CLAUDE.md](CLAUDE.md)** - Claude Code configuration
- **[docs/README.md](docs/README.md)** - Documentation index
- **[.bmad/epics/README.md](.bmad/epics/README.md)** - Epic portfolio

Questions? Ask Claude: *"How do I [task] in this project?"*

---

*Last updated: 2026-01-05*
