# JIRA Sync Workflow

## The Two-Phase Approach

Syncing BMAD to JIRA requires two phases to handle circular and cross-epic dependencies reliably.

### The Problem

- EPIC-AUTH-001 might depend on EPIC-1-PLATFORM
- EPIC-1-PLATFORM might depend on EPIC-AUTH-001 (circular)
- Story A might block Story B, which depends on Story A
- Cross-epic refs can't be converted until the target epic exists in JIRA

### The Solution

**Phase 1: Create All Issues (No Cross-Epic Refs)**
```bash
# Sync ALL epics to JIRA first
python scripts/jira-sync-all.py --epic all
```

This creates all issues but leaves cross-epic references unconverted (e.g., `EPIC-1-PLATFORM` remains as-is).

**Phase 2: Fix All References**
```bash
# Now that all issues exist, convert ALL refs to JIRA keys
python scripts/jira-post-import-fix.py
```

This:
1. Builds complete mapping of ALL issues → JIRA keys
2. Converts ALL remaining references to JIRA keys
3. Updates JIRA descriptions with corrected content
4. Creates missing dependency links

## Commands

### Full Fresh Sync (Clean Start)
```bash
# 1. Reset local files and clean JIRA
python scripts/jira-sync-all.py --epic all --reset --clean-jira

# 2. Fix any remaining cross-epic refs
python scripts/jira-post-import-fix.py
```

### Incremental Sync (Resume Failed)
```bash
# Resume where it left off
python scripts/jira-sync-all.py --epic all --resume

# Fix refs
python scripts/jira-post-import-fix.py
```

### Validate Only (No Changes)
```bash
# Check current state
python scripts/jira-post-import-fix.py --validate-only
```

### Dry Run (Preview Changes)
```bash
python scripts/jira-post-import-fix.py --dry-run
```

### Fix Local Only (No JIRA API Calls)
```bash
python scripts/jira-post-import-fix.py --no-jira-update
```

### Create Missing Links
```bash
python scripts/jira-post-import-fix.py --create-links
```

## Rule: ALL References Must Be JIRA Keys

After Phase 2, EVERY reference in JIRA must be a JIRA key:

| Field | Before | After |
|-------|--------|-------|
| Epic Depends On | EPIC-1-PLATFORM | ARGUS-1450 |
| Epic Blocks | EPIC-6 | ARGUS-1500 |
| Story Depends On | S1, S2a | ARGUS-1339, ARGUS-1345 |
| Story Blocks | S2b, S2c | ARGUS-1346, ARGUS-1347 |
| Task Requires | T1 | ARGUS-1360 |
| Task Unlocks | T3 | ARGUS-1362 |

## Error Handling

### "Non-JIRA references remaining"

This means some target epics haven't been synced yet. Run:
```bash
# See what's missing
python scripts/jira-post-import-fix.py --validate-only

# Sync missing epics
python scripts/jira-sync-all.py --epic EPIC-1-PLATFORM

# Fix refs again
python scripts/jira-post-import-fix.py
```

### "Duplicate epics in JIRA"

Clean up with:
```bash
python scripts/jira-sync-all.py --epic EPIC-AUTH-001 --clean-jira
```

### Circular Reference Detection

The post-import fix handles circular refs automatically because:
1. All issues are created FIRST (Phase 1)
2. Refs are converted SECOND (Phase 2)
3. Both issues exist before refs are updated

## Files

| Script | Purpose |
|--------|---------|
| `jira-sync-all.py` | Phase 1: Create issues, convert intra-epic refs |
| `jira-post-import-fix.py` | Phase 2: Convert ALL refs, update JIRA |
| `markdown_to_adf.py` | Convert markdown to Atlassian Document Format |

## Configuration

Set in `.env`:
```
ATLASSIAN_SITE=armor-defense.atlassian.net
ATLASSIAN_EMAIL=your@email.com
ATLASSIAN_API_TOKEN=your-token
JIRA_PROJECT_KEY=ARGUS
```
