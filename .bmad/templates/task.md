# {{STORY_ID}}-T{{TASK_NUM}}: {{TASK_TITLE}}

**Story:** {{STORY_ID}}
**Linked to:** {{AC_ID}}
**Status:** pending

---

## Coordination

| Field | Value |
|-------|-------|
| Requires | {{REQUIRES}} |
| Unlocks | {{UNLOCKS}} |
| Claimed By | |
| Claimed At | |
| JIRA Key | |

---

## Acceptance Criteria

{{AC_CONTENT}}

---

## AI Implementation Prompt

You are implementing **{{STORY_ID}}-T{{TASK_NUM}}: {{TASK_TITLE}}** for the Armor Argus platform.

### Context

{{STORY_STATEMENT}}

### Architecture References

| Document | Relevant Sections |
|----------|-------------------|
| [ARCHITECTURE_OVERVIEW.md](../../../../../docs/ARCHITECTURE_OVERVIEW.md) | {{RELEVANT_ARCH_SECTIONS}} |
| [SECURITY_BOUNDARIES.md](../../../../../docs/SECURITY_BOUNDARIES.md) | {{RELEVANT_SECURITY_SECTIONS}} |
| {{CONTRACT_OR_SCHEMA}} | {{CONTRACT_SECTIONS}} |

### External Dependencies

| Dependency | Story | Status | Interface Used |
|------------|-------|--------|----------------|
| {{EXT_DEP_1}} | {{EXT_STORY_1}} | {{EXT_STATUS_1}} | {{INTERFACE_1}} |

*If status is not "completed", coordinate with that story's owner before proceeding.*

### This Task

Implement {{AC_ID}}: {{TASK_TITLE}}

{{AC_CONTENT}}

---

## Target Files

```
{{TARGET_FILES}}
```

---

## Code Patterns

{{CODE_PATTERNS}}

---

## Anti-Patterns (FORBIDDEN)

| Anti-Pattern | Why It's Wrong | Do Instead |
|--------------|----------------|------------|
| {{ANTI_PATTERN_1}} | {{REASON_1}} | {{ALTERNATIVE_1}} |
| {{ANTI_PATTERN_2}} | {{REASON_2}} | {{ALTERNATIVE_2}} |

---

## Edge Cases

| Edge Case | Expected Behavior | Test |
|-----------|-------------------|------|
| {{EDGE_CASE_1}} | {{BEHAVIOR_1}} | {{TEST_1}} |
| {{EDGE_CASE_2}} | {{BEHAVIOR_2}} | {{TEST_2}} |

---

## Security Considerations

| Threat | Mitigation | Verified |
|--------|------------|----------|
| {{THREAT_1}} | {{MITIGATION_1}} | [ ] |
| {{THREAT_2}} | {{MITIGATION_2}} | [ ] |

---

## Testing Requirements

### Unit Tests

| Component | Test File | Coverage Target |
|-----------|-----------|-----------------|
| {{COMPONENT_1}} | {{TEST_FILE_1}} | 90% |

### Verification Commands

```bash
{{VERIFICATION_COMMANDS}}
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| {{PACKAGE_1}} | {{VERSION_1}} | {{PURPOSE_1}} |

---

## Subtasks

| # | Description | Status |
|---|-------------|--------|
| S1 | {{SUBTASK_1}} | pending |
| S2 | {{SUBTASK_2}} | pending |
| S3 | {{SUBTASK_3}} | pending |

---

## Handoff Notes

*Populated on task completion for next task*

### What Was Built
-

### Files Created/Modified
| File | Action | Notes |
|------|--------|-------|

### Context for Next Task
-

---

## Implementation Learnings

*Populated after code review - feeds back into future task prompts*

| Issue Found | Root Cause | Prevention for Future |
|-------------|------------|----------------------|
| | | |

### Patterns Discovered
-

### Anti-Patterns Discovered
-

---

## Done When

- [ ] {{AC_ID}} acceptance criteria met
- [ ] All subtasks completed
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Security considerations verified
- [ ] Handoff notes written
