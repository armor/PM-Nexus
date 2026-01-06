# Getting Started with UI-Uplift

> **Goal:** Get you productive in 20 minutes as a PM using BMAD + Jira.

---

## What You'll Set Up

| Step | Time | What You Get |
|------|------|--------------|
| 1. Clone Repo | 2 min | Local copy of all epics, docs, and BMAD |
| 2. Jira API Token | 3 min | Ability to sync to Jira/Confluence |
| 3. Configure MCP | 5 min | Claude can push to Jira for you |
| 4. Learn BMAD Basics | 10 min | Invoke agents, run workflows |

---

## Step 1: Clone the Repository (2 min)

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd UI-Uplift

# Or if already cloned
git submodule update --init --recursive
```

**What you get (BMAD is pre-installed):**

| Directory | Contents |
|-----------|----------|
| `_bmad/` | BMAD framework v6.0.0 (core, bmm, bmb, cis modules) |
| `.bmad/epics/` | 15 epics with 143 stories ready to sync |
| `docs/` | PRDs, architecture, design system |

**No separate BMAD installation needed** - it's included in the repo.

---

## Step 2: Get Your Jira API Token (3 min)

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it: `Claude Code - UI-Uplift`
4. Click **"Create"**
5. **Copy the token immediately** (you won't see it again!)

---

## Step 3: Configure Environment (5 min)

### Create your .env file

```bash
cp .env.example .env
```

### Edit .env with your credentials

```env
JIRA_HOST=your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=<paste-your-token-here>
JIRA_DEFAULT_PROJECT=STAGE
```

### Build the Jira MCP Server

```bash
cd submodules/jira-mcp
npm install
cp ../../.env .env
npm run build
```

### Add to Claude Code MCP Config

Edit `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "node",
      "args": ["/full/path/to/UI-Uplift/submodules/jira-mcp/dist/index.js"],
      "env": {
        "JIRA_HOST": "your-company.atlassian.net",
        "JIRA_EMAIL": "your.email@company.com",
        "JIRA_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Restart Claude Code** to pick up the new MCP server.

---

## Step 4: Learn BMAD Basics (10 min)

### What is BMAD?

BMAD = Business Model Agile Delivery. It's a framework with AI agents that help you:

```
Phase 1: ANALYSIS      → Understand the problem
Phase 2: PLANNING      → Define what to build (PRD)
Phase 3: SOLUTIONING   → Design how to build it (Architecture, Epics)
Phase 4: IMPLEMENTATION → Build it (Sprint Planning, Dev)
```

### Your Main Agents

| Agent | Name | What They Do |
|-------|------|--------------|
| **PM** | John | Create PRDs, Epics & Stories |
| **Architect** | Winston | Design system architecture |
| **SM** | Bob | Sprint planning, story prep |
| **UX Designer** | Sally | UX patterns and design |

### How to Invoke an Agent

**Option 1: Natural Language**
```
Load the PM agent
```

**Option 2: Skill Command**
```
/bmad:bmm:agents:pm
```

The agent greets you with a menu:

```
Hello Boles! I'm John, your Product Manager.

[MH] Redisplay Menu Help
[CH] Chat with the Agent
[PR] Create Product Requirements Document (PRD)
[ES] Create Epics and User Stories from PRD
[IR] Implementation Readiness Review
[PM] Start Party Mode
[DA] Dismiss Agent

What would you like to do?
```

Type a number or shortcut (e.g., `PR` or `2`) to run that workflow.

---

## Quick Reference: Common Tasks

### Sync Epics to Jira

```
Sync .bmad/epics to Jira project STAGE
```

### Create a New Epic

```
1. Create folder: .bmad/epics/EPIC-16-{NAME}/
2. Create README.md using the template
3. Ask Claude: "Sync EPIC-16 to Jira"
```

### Create a PRD

```
1. Load the PM agent
2. Select [PR] Create PRD
3. Answer the discovery questions
4. PRD saved to .bmad/planning-artifacts/
```

### Create Epics from PRD

```
1. Load the PM agent (with completed PRD + Architecture)
2. Select [ES] Create Epics and Stories
3. Review and approve
4. Epics saved to .bmad/epics/
```

### Push to Confluence

```
Create a Confluence page for EPIC-1 in the Nexus UI Uplift space
```

### Check What's Out of Sync

```
Compare .bmad/epics with Jira project STAGE
```

---

## Project Structure at a Glance

```
UI-Uplift/
├── GETTING_STARTED.md     # You are here
├── README.md              # Full reference guide
├── .env.example           # Environment template
│
├── .bmad/                 # YOUR WORK GOES HERE
│   ├── epics/             # Epic/Story/Task definitions
│   │   ├── README.md      # Portfolio overview (15 epics, 143 stories)
│   │   ├── EPIC-1-NEXUS-NAVIGATION/
│   │   └── ...
│   └── planning-artifacts/ # PRDs, Architecture docs
│
├── docs/                  # Documentation
│   ├── BMAD_GUIDE.md      # Full BMAD reference
│   ├── shared/            # Design system, testing strategy
│   └── nexus-ui-uplift/   # Project-specific docs
│
├── _bmad/                 # BMAD Framework (don't edit)
│   ├── bmm/agents/        # PM, Architect, Dev, etc.
│   └── bmm/workflows/     # PRD, Architecture, etc.
│
└── submodules/
    └── jira-mcp/          # Jira sync server
```

---

## Epic File Structure

Every epic in `.bmad/epics/` follows this pattern:

```
EPIC-{N}-{NAME}/
├── README.md              # Epic overview (required)
└── stories/               # Optional detailed breakdown
    └── {NN}-{slug}/
        ├── story-{NN}.md
        └── tasks/
            └── task-{NN}.md
```

### Minimal Epic README

```markdown
# EPIC-{N}: {Title}

**Status:** Ready for Sprint X
**Priority:** P0 | P1 | P2
**Total Stories:** X | **Total Points:** Xpt

## Summary
What this epic delivers.

## Business Value
- Why it matters

## Acceptance Criteria
- [ ] What must be true when done

## Stories
| ID | Title | Points |
|----|-------|--------|
| {NAME}-001 | Story title | 3pt |
```

---

## Troubleshooting

### "Jira returns 401 Unauthorized"

- Verify email matches your Atlassian account
- Regenerate API token
- Check .env has no extra spaces

### "MCP server not connecting"

- Use absolute path in mcp.json
- Rebuild: `cd submodules/jira-mcp && npm run build`
- Restart Claude Code

### "Agent won't load"

- Check `_bmad/core/config.yaml` exists
- Verify BMAD modules installed: `cat _bmad/_config/manifest.yaml`

---

## Next Steps

1. **Explore the portfolio:** Open `.bmad/epics/README.md`
2. **Try an agent:** Type "Load the PM agent"
3. **Sync to Jira:** "Sync EPIC-1 to Jira project STAGE"
4. **Read full guides:**
   - [README.md](README.md) - Complete reference
   - [docs/BMAD_GUIDE.md](docs/BMAD_GUIDE.md) - All agents & workflows

---

## Quick Command Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    PM QUICK REFERENCE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LOAD AGENTS                                                     │
│  ───────────                                                     │
│  "Load the PM agent"       → PRDs, Epics & Stories              │
│  "Load the Architect"      → Architecture docs                  │
│  "Load the SM agent"       → Sprint planning                    │
│                                                                  │
│  JIRA SYNC                                                       │
│  ─────────                                                       │
│  "Sync .bmad/epics to Jira project STAGE"                       │
│  "Compare .bmad/epics with STAGE"                               │
│  "Update STAGE-16 description from BMAD"                        │
│                                                                  │
│  CONFLUENCE                                                      │
│  ──────────                                                      │
│  "Create Confluence page for EPIC-1"                            │
│  "Push docs/shared/design-system.md to Confluence"              │
│                                                                  │
│  KEY LOCATIONS                                                   │
│  ─────────────                                                   │
│  .bmad/epics/           Your epic definitions                   │
│  .bmad/planning-artifacts/   PRDs, Architecture                 │
│  docs/BMAD_GUIDE.md     Full BMAD reference                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

*Get stuck? Ask Claude: "How do I [task] in this project?"*
