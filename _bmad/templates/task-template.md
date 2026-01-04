# Task {STORY-ID}.{N}: {Task Title}

**Status:** pending | in-progress | blocked | complete
**Parent Story:** {STORY-ID} ({Story Title})
**Acceptance Criteria Coverage:** AC{N}, AC{M}
**Estimated Hours:** {4-16}
**Actual Hours:** {filled on completion}
**Assigned To:** {agent or developer}

---

## Task Description

{Minimum 100 words. Describe what this task accomplishes, why it's needed, and how it contributes to the parent story's acceptance criteria.}

---

## Worktree Context

### Parent Story Worktree
| Field | Value |
|-------|-------|
| Story ID | {STORY-ID} |
| Worktree Path | `worktrees/{repo}-{STORY-ID}/` |
| Branch | `{STORY-ID}-{kebab-title}` |
| Worktree Status | pending | active | - |

### File Reservations
| File | Reserved By | Lock Status | Lock Acquired |
|------|-------------|-------------|---------------|
| {file path} | Task {N} | available / locked | {timestamp} |
| {file path} | Task {N} | available / locked | {timestamp} |

### Parallel Execution Safety
- [ ] Worktree verified active before starting
- [ ] No conflicting file locks held by other tasks
- [ ] Parent story is in-progress

---

## Pre-Conditions

- [ ] Parent story status is `in-progress`
- [ ] Worktree exists and is clean (`git status` shows no changes)
- [ ] Dependencies completed: {list task dependencies}
- [ ] Required context read: {list files/docs to read first}
- [ ] Base tests passing before starting

---

## Subtasks

### Subtask {STORY-ID}.{N}.1: {Subtask Title}
**File:** `_bmad/implementation-artifacts/{STORY-ID}-{N}-1-subtask.md`
**Status:** pending | in-progress | done
**Hours:** {1-4}
**Files:** `{file1}`, `{file2}`

### Subtask {STORY-ID}.{N}.2: {Subtask Title}
**File:** `_bmad/implementation-artifacts/{STORY-ID}-{N}-2-subtask.md`
**Status:** pending | in-progress | done
**Hours:** {1-4}
**Files:** `{file1}`, `{file2}`

---

## Technical Approach

### Implementation Strategy
{Describe the technical approach for this task}

### Key Files to Modify
| File | Purpose | Estimated Changes |
|------|---------|-------------------|
| {path} | {what changes} | {lines added/modified} |

### Key Functions/Components
| Function/Component | Action | Signature |
|--------------------|--------|-----------|
| {name} | create / modify | {signature if known} |

---

## Testing Requirements

### Tests to Create
| Test File | Test Cases | Coverage |
|-----------|------------|----------|
| {file} | {cases} | {what it covers} |

### Tests That Must Pass
| Test | Command | Current Status |
|------|---------|----------------|
| Unit | `cargo test {module}` | |
| Integration | `cargo test --test {name}` | |

---

## Verification Commands

```bash
# Before starting
git status  # must be clean
cargo test  # baseline must pass

# After each subtask
cargo fmt --check
cargo clippy -- -D warnings
cargo test

# On task completion
cargo test --all-features
```

---

## Done Criteria

- [ ] All subtasks marked complete
- [ ] All tests pass
- [ ] No new lint warnings
- [ ] Code committed with proper message format
- [ ] File locks released
- [ ] Task marked complete in parent story

---

## Dependencies

### Task Dependencies (within story)
| Task | Status | Notes |
|------|--------|-------|
| Task {N} | {status} | {blocking reason if any} |

### External Dependencies
| Dependency | Status |
|------------|--------|
| {dep} | {status} |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| {risk} | {mitigation} |

---

## Agent Review Log

### Task Validation
| Agent | Model | Timestamp | Decision | Confidence |
|-------|-------|-----------|----------|------------|
| | | | | |

### Subtask Completion Verification
| Subtask | Verified By | Timestamp | Tests Pass | Lint Clean |
|---------|-------------|-----------|------------|------------|
| {N}.1 | | | | |
| {N}.2 | | | | |

---

## Execution Audit Trail

| Action | Timestamp | Actor | Actor Type | Notes |
|--------|-----------|-------|------------|-------|
| Task started | | | | |
| File lock acquired | | | | |
| Subtask {N}.1 complete | | | | |
| Subtask {N}.2 complete | | | | |
| File lock released | | | | |
| Task complete | | | | |

---

## Notes

{Implementation notes, gotchas discovered, decisions made}

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| {YYYY-MM-DD} | Task created | {author} |
