# Subtask {STORY-ID}.{TASK#}.{SUBTASK#}: {Subtask Title}

**Status:** pending | in-progress | blocked | done
**Parent Task:** {STORY-ID}.{TASK#} ({Task Title})
**Parent Story:** {STORY-ID} ({Story Title})
**Assigned To:** {agent identifier}
**Estimated Hours:** {1-4}
**Actual Hours:** {filled on completion}
**Complexity:** trivial | simple | moderate

---

## Description

{Minimum 50 words. One clear description of exactly what needs to happen. Be specific about the outcome.}

---

## Worktree & File Lock Context

### Worktree Binding
| Field | Value |
|-------|-------|
| Story Worktree | `worktrees/{repo}-{STORY-ID}/` |
| Branch | `{STORY-ID}-{kebab-title}` |
| Worktree Status | active | - |
| Verified At | {timestamp} |

### File Locks Required
| File | Lines | Lock Type | Status |
|------|-------|-----------|--------|
| `{file path}` | {start}-{end} or all | exclusive | pending / acquired |
| `{file path}` | {start}-{end} or all | exclusive | pending / acquired |

### Parallel Safety Checklist
- [ ] Worktree exists and is active
- [ ] Parent task is in-progress
- [ ] No other subtask holds locks on my files
- [ ] File locks acquired before execution
- [ ] File locks released after completion

---

## Pre-Conditions

- [ ] Parent task status is `in-progress`
- [ ] Worktree is clean (no uncommitted changes)
- [ ] Previous subtask in sequence complete: {STORY-ID}.{TASK#}.{N-1}
- [ ] Required files exist: {list files}
- [ ] Required functions exist: {list functions}
- [ ] Tests passing before starting: `cargo test {module}`

---

## In-Scope

**Files to Create:**
- `{file path}` - {purpose}

**Files to Modify:**
- `{file path}:{line range}` - {what changes}

**Functions to Create:**
| Function | File | Signature |
|----------|------|-----------|
| `{name}` | `{file}` | `fn {name}({params}) -> {return}` |

**Functions to Modify:**
| Function | File | Change |
|----------|------|--------|
| `{name}` | `{file}` | {what changes} |

**Tests to Create:**
- `{test file}::{test_name}` - {what it tests}

---

## Out-of-Scope

- {Explicitly excluded item 1}
- {Explicitly excluded item 2}
- {Defer to subtask {N}: reason}

---

## Implementation Details

### Behavior Specification
**Input:** {what the function/component receives}
**Processing:** {what it does with the input}
**Output:** {what it returns or produces}

### Example Input/Output
```
Input:  {example input}
Output: {expected output}
```

### Error Cases
| Condition | Expected Behavior | Error Type |
|-----------|-------------------|------------|
| {condition} | {behavior} | {error} |

### Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| {case} | {behavior} |

---

## Done Criteria

- [ ] File created/modified as specified
- [ ] Function signature matches specification
- [ ] All test cases pass
- [ ] No new lint warnings (`cargo clippy`)
- [ ] Code formatted (`cargo fmt`)
- [ ] Committed with message: `{type}({scope}): {desc} ({STORY-ID})`
- [ ] File locks released
- [ ] Subtask marked done in parent task

---

## Verification Commands

```bash
# Before starting
git status  # verify clean
cargo test {module}  # baseline

# After implementation
cargo fmt
cargo clippy -- -D warnings
cargo test {module}::{test_name}

# Full verification
cargo test
```

---

## Commit Specification

**Message Format:** `{type}({scope}): {description} ({STORY-ID})`

**Example:**
```
feat(auth): Add timestamp validation to HMAC verifier (AUTH-001.2)
```

**Files to Include:**
- `{file1}`
- `{file2}`
- `{test file}`

---

## Agent Signoff

### Execution Agent
| Field | Value |
|-------|-------|
| Agent | {agent name} |
| Model | {model identifier} |
| Session | {session id} |
| Started | {timestamp} |
| Completed | {timestamp} |
| Duration | {minutes} |

### Verification Signoff
| Check | Agent | Timestamp | Pass | Confidence |
|-------|-------|-----------|------|------------|
| Tests Pass | | | | |
| Lint Clean | | | | |
| Done Criteria | | | | |

### Signoff Decision
| Field | Value |
|-------|-------|
| Decision | approved / needs-changes / blocked |
| Confidence | {0.0-1.0} |
| Reasoning | {explanation} |
| Concerns | {any flags raised} |

---

## Execution Audit Trail

| Action | Timestamp | Actor | Notes |
|--------|-----------|-------|-------|
| Subtask assigned | | | |
| File lock requested | | | |
| File lock acquired | | | |
| Execution started | | | |
| Implementation complete | | | |
| Tests verified | | | |
| Committed | | {commit hash} |
| File lock released | | | |
| Subtask marked done | | | |

---

## Artifacts Produced

### Files Created
| File | Lines | Purpose |
|------|-------|---------|
| | | |

### Files Modified
| File | Lines Changed | Summary |
|------|---------------|---------|
| | | |

### Tests Added
| Test File | Test Name | Coverage |
|-----------|-----------|----------|
| | | |

### Commit
| Field | Value |
|-------|-------|
| Hash | |
| Message | |
| Files | |

---

## Notes

{Implementation notes, gotchas discovered, decisions made during execution}

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| {YYYY-MM-DD} | Subtask created | {author} |
