# Git Worktree Pattern for Argus Development

## Overview

All Argus submodules use git worktrees to enable parallel development across stories/features. This pattern is **MANDATORY** for all development work.

## Directory Structure

```
armor-argus/
├── submodules/                    # Main branches (always main/master)
│   ├── argus-common/              # main branch
│   ├── argus-api/                 # main branch
│   ├── argus-ingest/              # main branch
│   └── ...
│
└── worktrees/                     # Feature branches (story-named)
    ├── argus-common-auth-001-2a/  # branch: auth-001-2a-secrets-provider-abstraction
    ├── argus-api-auth-001-2/      # branch: auth-001-2-auth-gateway-service
    └── ...
```

## Naming Convention

**CRITICAL:** Worktree directories and branches MUST match story IDs from sprint-status.yaml

| Story ID | Worktree Directory | Branch Name |
|----------|-------------------|-------------|
| auth-001-2a-secrets-provider-abstraction | `argus-common-auth-001-2a` | `auth-001-2a-secrets-provider-abstraction` |
| auth-001-2-auth-gateway-service | `argus-api-auth-001-2` | `auth-001-2-auth-gateway-service` |

### Pattern
```
worktrees/{repo}-{story-prefix}/
branch: {full-story-id}
```

## Commands

### Create a Worktree for a Story

```bash
# From within the submodule directory
cd submodules/argus-common

# Create worktree with story branch
git worktree add /path/to/armor-argus/worktrees/{repo}-{story-prefix} -b {full-story-id}

# Example for auth-001-2a
git worktree add ../../worktrees/argus-common-auth-001-2a -b auth-001-2a-secrets-provider-abstraction
```

### List Worktrees

```bash
cd submodules/argus-common
git worktree list
```

### Remove Worktree (after story complete and merged)

```bash
git worktree remove /path/to/worktrees/argus-common-auth-001-2a
git branch -d auth-001-2a-secrets-provider-abstraction  # if merged
```

## Workflow

### Starting a New Story

1. Check sprint-status.yaml for the story ID
2. Identify which submodule(s) the story affects
3. Create worktree for each affected submodule:
   ```bash
   cd submodules/{repo}
   git worktree add ../../worktrees/{repo}-{story-prefix} -b {full-story-id}
   ```
4. Work in the worktree directory, NOT in submodules/

### During Development

- **submodules/{repo}/** = main branch (stable, for reference)
- **worktrees/{repo}-{story}/** = feature branch (active development)

### After Story Complete

1. Push feature branch
2. Create PR
3. After merge, clean up:
   ```bash
   git worktree remove ../../worktrees/{repo}-{story-prefix}
   git branch -d {full-story-id}
   ```

## Multi-Repo Stories

When a story spans multiple repos (e.g., auth-001-2 needs changes in argus-common AND argus-api):

```bash
# Create worktrees in both repos with SAME story ID
cd submodules/argus-common
git worktree add ../../worktrees/argus-common-auth-001-2 -b auth-001-2-auth-gateway-service

cd ../argus-api
git worktree add ../../worktrees/argus-api-auth-001-2 -b auth-001-2-auth-gateway-service
```

This keeps all related changes traceable by story ID.

## Current Worktrees

| Repo | Story | Worktree Path | Branch |
|------|-------|---------------|--------|
| argus-common | auth-001-2a | worktrees/argus-common-auth-001-2a | auth-001-2a-secrets-provider-abstraction |

## Agent Instructions

**All BMAD agents MUST:**

1. Check for existing worktrees before starting work: `git worktree list`
2. Create worktrees using the naming pattern above
3. Work in worktrees/ for feature development, NOT in submodules/
4. Never commit feature work directly to main in submodules/
5. Update this table when creating/removing worktrees
