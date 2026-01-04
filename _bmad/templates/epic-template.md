# EPIC-{N}: {Epic Title}

**Epic ID:** ARGUS-EPIC-{N}
**Team:** ARGUS-{TEAM}
**Status:** {Backlog | Ready for Sprint N | In Progress | Complete}
**MVP Scope:** MVP {1 | 2 | 3}
**Total Stories:** {count} | **Total Points:** {points}
**Git Worktree:** `team-{team}`
**Code Ownership:** `{comma-separated list of submodule paths}`

---

## Story Template Reference

All stories in this epic must satisfy the acceptance criteria defined in:
**[STORY-TEMPLATE.md](../STORY-TEMPLATE.md)**

Each story must have all 8 AC categories (or N/A with justification).

---

## Summary

{2-4 sentence description of the epic's purpose and scope. What problem does this solve? What value does it deliver?}

---

## Business Value

- {Value point 1}
- {Value point 2}
- {Value point 3}

---

## Epic Acceptance Criteria

1. {Epic-level acceptance criterion}
2. {Epic-level acceptance criterion}
3. {Epic-level acceptance criterion}
4. **E2E tests passing at 100% - ZERO SKIPPED**
5. {Additional criteria}

---

## Wave Assignments

| Wave | Sprints | Stories | Focus |
|------|---------|---------|-------|
| Wave 1 | 1-2 | {STORY-ID} to {STORY-ID} | {Theme} |
| Wave 2 | 3-4 | {STORY-ID} to {STORY-ID} | {Theme} |
| Wave 3 | 5-6 | {STORY-ID} to {STORY-ID} | {Theme} |

---

## Testing Requirements (NON-NEGOTIABLE)

Every story in this epic must satisfy:

1. **100% Test Pass Rate** - Zero failing tests allowed
2. **Zero Skipped Tests** - No `#[ignore]`, no `.skip()`, no `.todo()`
3. **E2E Coverage** - Every API endpoint has E2E test
4. **E2E Persistence Verification** - Data survives page reload
5. **E2E Console Error Capture** - Must be zero errors
6. **Coverage >= 80%** - For all new code

---

## Interface Contracts Provided

| Contract | Version | Status | Consumers |
|----------|---------|--------|-----------|
| {ContractName} | 1.0.0 | {Wave N} | {Teams} |

---

## MVP {N} Stories (Sprints {X-Y}) - {N} Stories, {N} Points

---

## WAVE 1: {Wave Theme} (Sprints 1-2)

### {Section Theme} (Sprint 1)

#### {STORY-ID}: {Story Title}
**Points:** {1-5} | **Wave:** 1 | **Sprint:** 1 | **Priority:** P0 | **MVP:** 1
**Interface:** {Contract Name or N/A}
**Team:** ARGUS-{TEAM}
**Worktree:** team-{team}

{One-line description}

**Functional Requirements:**
- [ ] FUNC-1: {Requirement}
- [ ] FUNC-2: {Requirement}
- [ ] FUNC-3: {Requirement}

**Code Quality:**
- [ ] CQ-1: No clippy warnings (`cargo clippy -- -D warnings`)
- [ ] CQ-2: Code formatted (`cargo fmt --check`)
- [ ] CQ-3: No TODO/FIXME without linked issue
- [ ] CQ-4: Functions < 50 lines
- [ ] CQ-5: Cyclomatic complexity < 10

**Security:**
- [ ] SEC-1: No hardcoded secrets (gitleaks passes)
- [ ] SEC-2: Input validation on external inputs
- [ ] SEC-3: SQL/injection prevention
- [ ] SEC-4: Auth required for endpoints
- [ ] SEC-5: Authorization check before data access
- [ ] SEC-6: Sensitive data not logged

**Interface Adherence:**
- [ ] INT-1: {N/A or contract requirement}

**Unit Testing:**
- [ ] UT-1: All public functions have unit tests
- [ ] UT-2: Coverage > 80% for new code
- [ ] UT-3: Edge cases tested (empty, null, max)
- [ ] UT-4: Error paths tested
- [ ] UT-5: Mocks for external dependencies
- [ ] UT-6: No skipped tests (`#[ignore]` forbidden)

**Integration Testing:**
- [ ] IT-1: API endpoint tested with real HTTP
- [ ] IT-2: Database ops tested with test DB
- [ ] IT-3: Cross-service calls tested
- [ ] IT-4: Circuit breaker behavior tested
- [ ] IT-5: Retry logic tested
- [ ] IT-6: No skipped tests

**E2E Testing:**
- [ ] E2E-1: Happy path scenario automated
- [ ] E2E-2: API response verified (status + body)
- [ ] E2E-3: Data persistence verified (reload test)
- [ ] E2E-4: Console errors captured (must be zero)
- [ ] E2E-5: Performance within SLA (< 500ms p95)
- [ ] E2E-6: No skipped tests

**UI Testing:** N/A (backend story)

**UX Testing:** N/A (backend story)

**Verification:**
- Command: `{verification command}`
- Expected: `{expected result}`
- E2E Test: `{test file path}`

---

<!-- Repeat story format for each story in the epic -->

---

## Wave Validation Stories

### {EPIC-N}-VAL-1: Wave 1 Automated Validation
**Points:** 2 | **Wave:** 1 | **Sprint:** 2 | **Priority:** P0 | **MVP:** 1
**Team:** ALL
**Type:** Validation

Run all automated validation checks for Wave 1.

**Validation Checklist:**
- [ ] All unit tests pass (100%)
- [ ] All integration tests pass (100%)
- [ ] All E2E tests pass (100%)
- [ ] Zero skipped tests
- [ ] Security scan passes
- [ ] Coverage >= 80%
- [ ] Contract tests pass

**Verification:**
- Command: `./scripts/validation-pass-1.sh`
- Expected: All checks pass
- Output: `validation-reports/wave-1-pass-1.json`

---

## Dependencies

### External Dependencies
| Dependency | Owner | Status | Risk |
|------------|-------|--------|------|
| {dependency} | {team} | {status} | H/M/L |

### Cross-Epic Dependencies
- This epic depends on: {EPIC-X}
- Epics depending on this: {EPIC-Y, EPIC-Z}

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {risk} | H/M/L | H/M/L | {mitigation} |

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| {YYYY-MM-DD} | Epic created | {author} |
