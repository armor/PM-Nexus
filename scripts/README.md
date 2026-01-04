# BMAD-JIRA Sync Scripts

Scripts for synchronizing the BMAD project structure (`.bmad/epics/`) to JIRA.

## Prerequisites

### Environment Variables

All scripts require Atlassian credentials:

```bash
export ATLASSIAN_EMAIL="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-api-token"
export ATLASSIAN_SITE="your-site.atlassian.net"  # optional, defaults to armor-defense.atlassian.net
export JIRA_PROJECT_KEY="ARGUS"                   # optional, defaults to ARGUS
```

### Getting an API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and set it as `ATLASSIAN_API_TOKEN`

### Python Dependencies

```bash
pip install requests pyyaml
```

---

## Main Scripts

### `jira-sync-comprehensive.py` (Primary)

Comprehensive sync script for BMAD Structure v3.0. Creates epics, stories, tasks, and dependency links.

**Features:**
- 4-phase sync: Epics → Stories → Tasks → Links
- Automatic dependency link creation ("Blocks" relationships)
- Local JIRA key updates in markdown files
- Resume capability with state tracking
- Rate limiting to avoid API throttling

**Usage:**

```bash
# Dry run - show what would be created
python scripts/jira-sync-comprehensive.py --dry-run

# Full sync of all epics
python scripts/jira-sync-comprehensive.py

# Sync specific epic only
python scripts/jira-sync-comprehensive.py --epic EPIC-1-PLATFORM

# Only create dependency links (after issues exist)
python scripts/jira-sync-comprehensive.py --links-only

# Resume interrupted sync (skip existing JIRA keys)
python scripts/jira-sync-comprehensive.py --resume
```

**Output:**
- Creates JIRA issues maintaining hierarchy
- Updates local `.md` files with JIRA keys
- Saves state to `.bmad/data/jira-sync-state.json`

---

### `jira-create-links.py`

Creates JIRA issue links directly via REST API.

**Features:**
- Create "Blocks" links between issues
- Set Epic Link on stories/tasks
- Sync links from BMAD coordination fields

**Usage:**

```bash
# Create a single "Blocks" link
python scripts/jira-create-links.py --from ARGUS-100 --to ARGUS-101 --type Blocks

# Set Epic Link on a story
python scripts/jira-create-links.py --story ARGUS-101 --epic ARGUS-100

# List available link types
python scripts/jira-create-links.py --list-types

# Sync all links from BMAD task files
python scripts/jira-create-links.py --sync-from-bmad
```

---

### `jira-field-discovery.py`

Discovers custom field IDs for your JIRA instance.

**Features:**
- Finds Epic Link, Sprint, Story Points fields
- Lists available issue link types
- Saves configuration to `_bmad/config/jira-fields.yaml`

**Usage:**

```bash
python scripts/jira-field-discovery.py
```

**Output:**
```yaml
site: armor-defense.atlassian.net
project_key: ARGUS
custom_fields:
  epic_link:
    id: customfield_10014
    name: Epic Link
  story_points:
    id: customfield_10016
    name: Story Points
link_types:
  blocks:
    id: "10000"
    name: Blocks
    inward: is blocked by
    outward: blocks
```

---

## BMAD Structure

The sync scripts expect the following directory structure:

```
.bmad/epics/
├── EPIC-1-PLATFORM/
│   ├── epic.md                          # Epic definition
│   └── stories/
│       ├── 01-api-gateway/
│       │   ├── story.md                 # Story definition
│       │   └── tasks/
│       │       ├── task-01-setup.md     # Task files
│       │       ├── task-02-auth.md
│       │       └── ...
│       └── 02-data-layer/
│           └── ...
├── EPIC-2-GRAPH/
│   └── ...
└── ...
```

### Coordination Fields

Stories and tasks include coordination sections that define dependencies:

**Story Coordination:**
```markdown
| Field | Value |
|-------|-------|
| Depends On | PLAT-001, PLAT-002 |
| Blocks | PLAT-010 |
| JIRA Key | ARGUS-123 |
```

**Task Coordination:**
```markdown
| Field | Value |
|-------|-------|
| Requires | T1, T2 |
| Unlocks | T4, T5 |
| JIRA Key | ARGUS-124 |
```

These fields are synced to JIRA as "Blocks" link relationships.

---

## JIRA Field Mappings

| BMAD Field | JIRA Field | Link Direction |
|------------|------------|----------------|
| Story "Depends On" | Blocks link | Story is blocked by dependency |
| Story "Blocks" | Blocks link | Story blocks downstream |
| Task "Requires" | Blocks link | Task is blocked by dependency |
| Task "Unlocks" | Blocks link | Task blocks downstream |
| Story → Epic | Epic Link / Parent | Uses multiple field methods |

### Epic Link Methods

The scripts try multiple methods to link stories to epics (JIRA instances vary):

1. `parent` field (team-managed projects)
2. `customfield_10015` (Parent Link)
3. `customfield_10014` (Epic Link)
4. `customfield_10013` (fallback)

---

## Priority Mapping

| BMAD Priority | JIRA Priority |
|---------------|---------------|
| P0 | Critical |
| P1 | High |
| P2 | Medium |
| P3 | Low |
| P4 | Low |

---

## Troubleshooting

### "customfield_XXXXX cannot be set"

The Epic Link field ID varies by JIRA instance. Run `jira-field-discovery.py` to find the correct field ID for your instance.

### Rate Limiting

If you hit rate limits, increase `RATE_LIMIT_DELAY` in the script (default: 0.25 seconds).

### Resume Interrupted Sync

If the sync is interrupted, run with `--resume` to skip already-created issues:

```bash
python scripts/jira-sync-comprehensive.py --resume
```

The script tracks state in `.bmad/data/jira-sync-state.json`.

---

## MCP Server Alternative

For Claude Code integration, use the custom MCP server at `submodules/argus-jira-mcp/`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "node",
      "args": ["./submodules/argus-jira-mcp/dist/index.js"],
      "env": {
        "JIRA_HOST": "armor-defense.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Available MCP tools:
- `list_link_types` - List available link types
- `create_issue_link` - Create Blocks/Relates links
- `set_epic_link` - Link story to epic
- `bulk_create_links` - Create up to 100 links at once
- `get_epic_children` - Get stories/tasks under an epic
- `search_issues` - JQL search
- And more...

---

## Related Documentation

- [BMAD Structure v3.0](../.bmad/STRUCTURE.md)
- [Handoff Document](../.bmad/data/HANDOFF-2026-01-03-jira-mcp-complete.md)
- [MCP Server README](../submodules/argus-jira-mcp/README.md)
