# BMAD User Guide

> **BMAD** = Business Model Agile Delivery
> A framework for AI-assisted product development from ideation to implementation.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding BMAD](#understanding-bmad)
3. [Available Agents](#available-agents)
4. [Key Workflows](#key-workflows)
5. [The BMAD Method Flow](#the-bmad-method-flow)
6. [Working with Agents](#working-with-agents)
7. [Templates](#templates)
8. [Jira Integration](#jira-integration)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Invoke an Agent

Tell Claude to load an agent:

```
Load the PM agent
```

or use the skill command:

```
/bmad:bmm:agents:pm
```

The agent will greet you with a menu of available actions.

### Run a Workflow

Once an agent is active, select a menu option:

```
Agent: Hello Boles! I'm John, your Product Manager. Here's what I can help with:

[MH] Redisplay Menu Help
[CH] Chat with the Agent about anything
[WS] Get workflow status
[PR] Create Product Requirements Document (PRD)
[ES] Create Epics and User Stories from PRD
[IR] Implementation Readiness Review
[CC] Course Correction Analysis
[PM] Start Party Mode
[DA] Dismiss Agent

What would you like to do?

You: PR
```

---

## Understanding BMAD

### What is BMAD?

BMAD is a structured framework that uses AI agents to guide you through the product development lifecycle:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BMAD METHOD FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Phase 1          Phase 2          Phase 3          Phase 4        │
│   ANALYSIS         PLANNING         SOLUTIONING      IMPLEMENTATION │
│   ─────────        ────────         ───────────      ──────────────  │
│                                                                      │
│   Product Brief    PRD              Architecture     Sprint Planning │
│   Research         UX Design        Epics & Stories  Dev Story      │
│                                     Readiness Check  Code Review    │
│                                                                      │
│   ↓                ↓                ↓                ↓              │
│   Understand       Plan What        Design How       Build It       │
│   the Problem      to Build         to Build                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Installed Modules

Your BMAD installation includes these modules:

| Module | Purpose | Agents | Workflows |
|--------|---------|--------|-----------|
| **core** | Base framework | BMad Master | Party Mode, Brainstorming |
| **bmm** | Business Model Management | PM, Architect, SM, Dev, UX Designer, Tea, Analyst | PRD, Architecture, Epics, Sprint Planning |
| **bmb** | BMad Builder | Agent Builder, Module Builder | Create Agent, Create Workflow |
| **cis** | Creative Innovation System | Brainstorming Coach, Design Thinking Coach, Storyteller | Problem Solving, Innovation Strategy |

---

## Available Agents

### Core Agents

| Agent | Name | Role | When to Use |
|-------|------|------|-------------|
| `bmad-master` | BMad Master | Orchestrator | List all tasks/workflows, Party Mode |

### BMM Agents (Business Model Management)

| Agent | Name | Role | Key Workflows |
|-------|------|------|---------------|
| `pm` | John | Product Manager | PRD, Epics & Stories |
| `architect` | Winston | System Architect | Architecture Document |
| `sm` | Bob | Scrum Master | Sprint Planning, Story Prep |
| `dev` | Amelia | Developer | Dev Story, Code Implementation |
| `ux-designer` | Sally | UX Designer | UX Design Document |
| `tea` | Murat | Test Architect | Test Framework, Test Design |
| `analyst` | Alex | Business Analyst | Product Brief, Research |
| `tech-writer` | — | Technical Writer | Documentation |
| `quick-flow-solo-dev` | Barry | Solo Developer | Quick Tech Spec + Implementation |

### CIS Agents (Creative Innovation System)

| Agent | Name | Role | When to Use |
|-------|------|------|-------------|
| `brainstorming-coach` | — | Ideation Facilitator | Generate ideas using creative techniques |
| `design-thinking-coach` | — | Design Thinking | Empathy mapping, user-centered design |
| `creative-problem-solver` | — | Problem Solver | Root cause analysis, solution generation |
| `innovation-strategist` | — | Innovation | Market disruption, business model innovation |
| `storyteller` | — | Narrative | Pitch decks, compelling narratives |
| `presentation-master` | — | Presentation | Slide design, visual communication |

### How to Invoke Agents

**Method 1: Natural Language**
```
Load the PM agent
```

**Method 2: Skill Command**
```
/bmad:bmm:agents:pm
/bmad:bmm:agents:architect
/bmad:cis:agents:brainstorming-coach
```

**Method 3: Direct File Reference**
```
Load and activate the agent at _bmad/bmm/agents/pm.md
```

---

## Key Workflows

### Phase 1: Analysis

| Workflow | Description | Output |
|----------|-------------|--------|
| `create-product-brief` | Collaborative discovery to understand the problem | Product Brief |
| `research` | Market, technical, or domain research | Research Report |

### Phase 2: Planning

| Workflow | Description | Output |
|----------|-------------|--------|
| `create-prd` | Step-by-step PRD creation with PM agent | PRD Document |
| `create-ux-design` | UX patterns, look and feel | UX Design Document |

### Phase 3: Solutioning

| Workflow | Description | Output |
|----------|-------------|--------|
| `create-architecture` | Technical architecture decisions | Architecture Document |
| `create-epics-and-stories` | PRD → Epics → Stories breakdown | Epic/Story files |
| `check-implementation-readiness` | Validate all docs before dev | Readiness Report |

### Phase 4: Implementation

| Workflow | Description | Output |
|----------|-------------|--------|
| `sprint-planning` | Extract stories, create sprint plan | sprint-status.yaml |
| `create-story` | Detailed story with tasks/subtasks | Story file |
| `dev-story` | Implement a story | Working code |
| `code-review` | Adversarial code review | Review findings |
| `retrospective` | Post-epic lessons learned | Retro document |

### Testing Workflows

| Workflow | Description | Output |
|----------|-------------|--------|
| `testarch-framework` | Initialize test framework | Test setup |
| `testarch-test-design` | Create test scenarios | Test cases |
| `testarch-automate` | Generate automated tests | Test code |
| `testarch-trace` | Requirements → Tests traceability | Trace matrix |

### Quick Flow (Bypass Full Process)

| Workflow | Description | When to Use |
|----------|-------------|-------------|
| `create-tech-spec` | Conversational spec engineering | Small features |
| `quick-dev` | Direct implementation | Bug fixes, small changes |

### Special Workflows

| Workflow | Description | When to Use |
|----------|-------------|-------------|
| `party-mode` | Multi-agent discussion | Complex decisions, brainstorming |
| `brainstorming` | Structured ideation | Generate ideas |
| `jira-sync` | Sync epics/stories to Jira | After creating epics |

---

## The BMAD Method Flow

### Standard Flow (New Projects)

```
1. Product Brief (Analyst)
   ↓
2. PRD (PM)
   ↓
3. UX Design (UX Designer) [if UI exists]
   ↓
4. Architecture (Architect)
   ↓
5. Epics & Stories (PM)
   ↓
6. Implementation Readiness Check (PM/Architect)
   ↓
7. Sprint Planning (SM)
   ↓
8. Dev Story (Dev) ←→ Code Review (Dev)
   ↓
9. Retrospective (SM)
```

### Minimal Flow (Small Features)

```
1. create-tech-spec (Quick Flow Solo Dev)
   ↓
2. quick-dev (Quick Flow Solo Dev)
   ↓
3. code-review (Dev)
```

### When to Use Each Phase

| Scenario | Start At | Skip |
|----------|----------|------|
| **New Product** | Product Brief | Nothing |
| **New Feature (large)** | PRD | Product Brief |
| **New Feature (small)** | Tech Spec | PRD, Architecture |
| **Bug Fix** | quick-dev | Everything |
| **Architecture Change** | Architecture | PRD |
| **Existing PRD** | Epics & Stories | Phases 1-2 |

---

## Working with Agents

### Agent Activation

When you load an agent, it:

1. Reads its persona file
2. Loads `_bmad/core/config.yaml` for settings
3. Greets you by name
4. Displays its menu

### Agent Menu Commands

Every agent supports these standard commands:

| Command | Shortcut | Action |
|---------|----------|--------|
| Menu Help | `MH` | Redisplay menu |
| Chat | `CH` | Free-form conversation |
| Dismiss Agent | `DA` | Exit agent mode |

### Switching Agents

To switch agents during a session:

```
Dismiss this agent and load the Architect
```

### Party Mode (Multi-Agent Discussion)

Get multiple agents to discuss a topic:

```
You: Start Party Mode

Agent: Party Mode! Select agents to participate:
1. PM (John)
2. Architect (Winston)
3. Dev (Amelia)
4. UX Designer (Sally)
5. SM (Bob)

You: 1, 2, 3

Agent: Topic for discussion?

You: Should we use GraphQL or REST for the new API?

[Agents discuss and reach consensus]
```

---

## Templates

BMAD provides templates for consistent document structure.

### Epic Templates

| Template | Use For |
|----------|---------|
| `epic-template.md` | Standard epic README |
| `epic-full-template.md` | Full documentation epic |
| `epic-summary-template.md` | JIRA-sync summary |

### Story/Task Templates

| Template | Use For |
|----------|---------|
| `story-template.md` | Story with acceptance criteria |
| `task-template.md` | Developer task |
| `subtask-template.md` | Atomic subtask |

### Using Templates

Templates are auto-applied during workflows. To use manually:

```
Create a new epic using the template at _bmad/templates/epic-template.md
```

---

## Jira Integration

### Sync Epics to Jira

After creating epics in `.bmad/epics/`, sync to Jira:

```
Sync .bmad/epics to Jira project STAGE
```

### What Syncs

| BMAD Element | JIRA Type |
|--------------|-----------|
| Epic README | Epic |
| Story file | Story |
| Task section | Task |
| Subtask row | Sub-task |

### Sync Commands

```
# Full sync
Sync all epics and stories from .bmad/epics to STAGE

# Single epic
Sync EPIC-1-NEXUS-NAVIGATION to Jira

# Update descriptions
Update STAGE-16 description from the BMAD story file

# Check sync status
Compare .bmad/epics with Jira project STAGE
```

### Confluence Integration

Push documentation to Confluence:

```
Create a Confluence page for EPIC-1 in the Nexus UI Uplift space
```

---

## Common Tasks

### Create a PRD

```
1. Load the PM agent
2. Select [PR] Create PRD
3. Answer discovery questions
4. Review and approve each section
5. PRD saved to .bmad/planning-artifacts/
```

### Create Epics from PRD

```
1. Load the PM agent (with completed PRD + Architecture)
2. Select [ES] Create Epics and Stories
3. Review epic breakdown
4. Approve story list per epic
5. Epics saved to .bmad/epics/
```

### Implement a Story

```
1. Load the Dev agent
2. Provide story ID or file path
3. Agent implements task by task
4. Review code changes
5. Agent updates story status
```

### Run Code Review

```
1. Load the Dev agent
2. Select [CR] Code Review
3. Provide files/story to review
4. Agent finds 3-10 issues minimum
5. Approve auto-fixes or address manually
```

### Brainstorm Ideas

```
1. Load the Brainstorming Coach agent
2. Define the challenge
3. Select ideation technique:
   - SCAMPER
   - Six Thinking Hats
   - Mind Mapping
   - Random Word Association
4. Generate and organize ideas
```

---

## File Organization

### Where Things Live

```
_bmad/                          # Framework (don't edit)
├── core/                       # Core module
│   ├── config.yaml             # Your settings
│   ├── agents/                 # Core agents
│   └── workflows/              # Core workflows
├── bmm/                        # Business Model Management
│   ├── agents/                 # PM, Architect, Dev, etc.
│   └── workflows/              # PRD, Architecture, etc.
├── cis/                        # Creative Innovation System
│   ├── agents/                 # Brainstorming, Design Thinking
│   └── workflows/              # Problem Solving, Innovation
├── templates/                  # Document templates
└── _config/                    # Manifests and registry

.bmad/                          # Your work (editable)
├── epics/                      # Epic/Story/Task definitions
├── planning-artifacts/         # PRDs, Architecture docs
├── implementation-artifacts/   # Sprint status, generated stories
└── diagrams/                   # Architecture diagrams
```

### Output Folder

All BMAD outputs go to `.bmad/` (configured in `_bmad/core/config.yaml`):

```yaml
output_folder: "{project-root}/.bmad"
```

---

## Troubleshooting

### Agent Won't Load

**Symptom:** Agent doesn't respond or shows errors

**Fix:**
```
# Check config exists
cat _bmad/core/config.yaml

# Verify module installed
cat _bmad/_config/manifest.yaml
```

### Workflow Fails Mid-Step

**Symptom:** Workflow stops unexpectedly

**Fix:**
```
# Check workflow status
Load the PM agent, select [WS] Workflow Status

# Resume from last step
Continue the workflow from step X
```

### Output Goes to Wrong Folder

**Symptom:** Files saved in unexpected location

**Fix:** Check `_bmad/core/config.yaml`:
```yaml
output_folder: "{project-root}/.bmad"
```

### Agent Doesn't Know Project Context

**Symptom:** Agent asks basic questions already answered

**Fix:** Create or update `project-context.md`:
```
Run the generate-project-context workflow
```

### Party Mode Agents Conflict

**Symptom:** Agents give contradictory advice

**Fix:** This is intentional! Party Mode surfaces disagreements. Use the synthesis to make a decision:
```
Summarize the consensus and disagreements from this discussion
```

---

## Configuration Reference

### Core Config (`_bmad/core/config.yaml`)

```yaml
user_name: Your Name          # How agents address you
communication_language: English
document_output_language: English
output_folder: "{project-root}/.bmad"
```

### Module Manifest (`_bmad/_config/manifest.yaml`)

```yaml
installation:
  version: 6.0.0-alpha.22
modules:
  - core
  - bmb
  - bmm
  - cis
```

---

## Next Steps

1. **Try an Agent:** Load the PM agent and explore the menu
2. **Run a Workflow:** Create a small PRD to learn the flow
3. **Check Party Mode:** Get multiple agents discussing a decision
4. **Sync to Jira:** Push your epics to Jira

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                     BMAD QUICK REFERENCE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AGENTS                                                              │
│  ───────                                                             │
│  /bmad:bmm:agents:pm          Product Manager (John)                │
│  /bmad:bmm:agents:architect   System Architect (Winston)            │
│  /bmad:bmm:agents:dev         Developer (Amelia)                    │
│  /bmad:bmm:agents:sm          Scrum Master (Bob)                    │
│  /bmad:bmm:agents:ux-designer UX Designer (Sally)                   │
│  /bmad:bmm:agents:tea         Test Architect (Murat)                │
│                                                                      │
│  KEY WORKFLOWS                                                       │
│  ─────────────                                                       │
│  [PR] Create PRD              [CA] Create Architecture              │
│  [ES] Create Epics & Stories  [IR] Implementation Readiness         │
│  [SP] Sprint Planning         [DS] Dev Story                        │
│  [CR] Code Review             [PM] Party Mode                       │
│                                                                      │
│  MENU SHORTCUTS                                                      │
│  ──────────────                                                      │
│  MH = Menu Help    CH = Chat    DA = Dismiss Agent                  │
│                                                                      │
│  OUTPUT LOCATIONS                                                    │
│  ────────────────                                                    │
│  PRDs, Architecture    .bmad/planning-artifacts/                    │
│  Epics & Stories       .bmad/epics/                                 │
│  Sprint Status         .bmad/implementation-artifacts/              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

*Last updated: 2026-01-05*
