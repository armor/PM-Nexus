# Story Template - 8-AC Format

**Version:** 2.0
**Reference:** All stories in all epics must satisfy these criteria categories.

---

## Story Header Format

```markdown
#### {STORY-ID}: {Title}
**Points:** {1-5} | **Wave:** {1-10} | **Sprint:** {N} | **Priority:** {P0|P1|P2} | **MVP:** {1|2}
**Interface:** {Contract name if applicable}
**Team:** ARGUS-{TEAM}
**Worktree:** team-{team}

{One-line description of the story}
```

---

## Required Acceptance Criteria (All 8 Categories)

Every story MUST include all 8 categories. Use `N/A` only when a category genuinely doesn't apply (e.g., UI Testing for backend-only stories).

### Category 1: Functional (FUNC)
What the code must do.

```markdown
**Functional Requirements:**
- [ ] FUNC-1: {Primary functionality works}
- [ ] FUNC-2: {Secondary functionality works}
- [ ] FUNC-3: {Edge cases handled}
```

### Category 2: Code Quality (CQ)
Code standards and cleanliness.

```markdown
**Code Quality:**
- [ ] CQ-1: No clippy warnings (`cargo clippy -- -D warnings`)
- [ ] CQ-2: Code formatted (`cargo fmt --check`)
- [ ] CQ-3: No TODO/FIXME without linked issue
- [ ] CQ-4: Functions < 50 lines
- [ ] CQ-5: Cyclomatic complexity < 10
```

### Category 3: Security (SEC)
Security requirements and validations.

```markdown
**Security:**
- [ ] SEC-1: No hardcoded secrets (gitleaks passes)
- [ ] SEC-2: Input validation on external inputs
- [ ] SEC-3: SQL/injection prevention
- [ ] SEC-4: Auth required for endpoints
- [ ] SEC-5: Authorization check before data access
- [ ] SEC-6: Sensitive data not logged
```

### Category 4: Interface Adherence (INT)
Contract compliance for cross-team work.

```markdown
**Interface Adherence:**
- [ ] INT-1: Implements contract trait exactly
- [ ] INT-2: Error types match contract spec
- [ ] INT-3: No extra public methods beyond contract
- [ ] INT-4: Contract version documented
- [ ] INT-5: Breaking changes via RFC
```

### Category 5: Unit Testing (UT)
Unit test requirements.

```markdown
**Unit Testing:**
- [ ] UT-1: All public functions have unit tests
- [ ] UT-2: Coverage > 80% for new code
- [ ] UT-3: Edge cases tested (empty, null, max)
- [ ] UT-4: Error paths tested
- [ ] UT-5: Mocks for external dependencies
- [ ] UT-6: No skipped tests (`#[ignore]` forbidden)
```

### Category 6: Integration Testing (IT)
Integration test requirements.

```markdown
**Integration Testing:**
- [ ] IT-1: API endpoint tested with real HTTP
- [ ] IT-2: Database ops tested with test DB
- [ ] IT-3: Cross-service calls tested
- [ ] IT-4: Circuit breaker behavior tested
- [ ] IT-5: Retry logic tested
- [ ] IT-6: No skipped tests
```

### Category 7: E2E Testing (E2E)
End-to-end test requirements.

```markdown
**E2E Testing:**
- [ ] E2E-1: Happy path scenario automated
- [ ] E2E-2: API response verified (status + body)
- [ ] E2E-3: Data persistence verified (reload test)
- [ ] E2E-4: Console errors captured (must be zero)
- [ ] E2E-5: Performance within SLA (< 500ms p95)
- [ ] E2E-6: No skipped tests
```

### Category 8a: UI Testing (UI) - Frontend Only
UI-specific test requirements.

```markdown
**UI Testing:**
- [ ] UI-1: Component renders without errors
- [ ] UI-2: Responsive at 320px, 768px, 1024px, 1440px
- [ ] UI-3: Keyboard navigation works
- [ ] UI-4: Screen reader compatible (ARIA)
- [ ] UI-5: Loading/error/empty states render
- [ ] UI-6: Visual regression baseline captured
- [ ] UI-7: No skipped tests
```

### Category 8b: UX Testing (UX) - Frontend Only
User experience requirements.

```markdown
**UX Testing:**
- [ ] UX-1: Matches approved design
- [ ] UX-2: Flow completes in < 3 clicks
- [ ] UX-3: Error messages actionable
- [ ] UX-4: Success feedback visible
- [ ] UX-5: No dead ends in flow
- [ ] UX-6: Undo for destructive actions
```

---

## Verification Section

Every story must include a verification command or procedure.

```markdown
**Verification:**
- Command: `{shell command to verify}`
- Expected: `{expected output or behavior}`
- E2E Test: `{test file name}`
```

---

## Story Size Reference

| Points | Complexity | Testing Effort | Example |
|--------|------------|----------------|---------|
| 1 | Single file, trivial | 1-2 unit tests | Add log statement |
| 2 | 2-3 files, simple | 3-5 unit, 1 integration | Add API field |
| 3 | Interface + impl | 5-10 unit, 2-3 integration, 1 E2E | New API endpoint |
| 5 | Multi-component | 10+ unit, 5+ integration, 2+ E2E | New feature |

**Max 5 points per story. Larger stories must be split.**

---

## Example: Complete Story

```markdown
#### PLAT-015: JWT Token Validation Middleware
**Points:** 3 | **Wave:** 1 | **Sprint:** 2 | **Priority:** P0 | **MVP:** 1
**Interface:** AuthService (v1.0.0)
**Team:** ARGUS-PLATFORM
**Worktree:** team-platform

Implement JWT validation middleware for Axum that extracts user context.

**Functional Requirements:**
- [ ] FUNC-1: Valid JWT extracts UserContext
- [ ] FUNC-2: Expired JWT returns 401
- [ ] FUNC-3: Malformed JWT returns 401
- [ ] FUNC-4: Missing JWT returns 401
- [ ] FUNC-5: User context available in handlers

**Code Quality:**
- [ ] CQ-1: No clippy warnings
- [ ] CQ-2: Code formatted
- [ ] CQ-3: No TODO/FIXME
- [ ] CQ-4: Functions < 50 lines
- [ ] CQ-5: Complexity < 10

**Security:**
- [ ] SEC-1: No hardcoded secrets
- [ ] SEC-2: Token signature verified
- [ ] SEC-3: Expiry enforced
- [ ] SEC-4: Claims validated
- [ ] SEC-5: Audit log on auth failure
- [ ] SEC-6: Token not logged

**Interface Adherence:**
- [ ] INT-1: Implements AuthService trait
- [ ] INT-2: Returns AuthError types
- [ ] INT-3: No extra public methods
- [ ] INT-4: Version 1.0.0 documented
- [ ] INT-5: N/A (new interface)

**Unit Testing:**
- [ ] UT-1: test_valid_token_extracts_user
- [ ] UT-2: test_expired_token_rejected
- [ ] UT-3: test_malformed_token_rejected
- [ ] UT-4: test_missing_token_rejected
- [ ] UT-5: Mocks for clock (expiry testing)
- [ ] UT-6: No #[ignore] tests

**Integration Testing:**
- [ ] IT-1: POST /api/login returns JWT
- [ ] IT-2: Protected endpoint requires JWT
- [ ] IT-3: Refresh token flow works
- [ ] IT-4: Rate limiting after 5 failures
- [ ] IT-5: N/A
- [ ] IT-6: No skipped tests

**E2E Testing:**
- [ ] E2E-1: Login -> protected page -> logout
- [ ] E2E-2: 401 verified for expired token
- [ ] E2E-3: Session persists after reload
- [ ] E2E-4: Console errors = 0
- [ ] E2E-5: Auth < 100ms p95
- [ ] E2E-6: No skipped tests

**UI Testing:** N/A (backend story)

**UX Testing:** N/A (backend story)

**Verification:**
- Command: `cargo test auth:: --features integration`
- Expected: All tests pass, 0 skipped
- E2E Test: `tests/e2e/auth.spec.ts`
```

---

## Validation Story Template

At the end of each wave, include validation stories:

```markdown
#### {WAVE}-VAL-1: Wave {N} Automated Validation
**Points:** 2 | **Wave:** {N} | **Sprint:** {last sprint of wave} | **Priority:** P0 | **MVP:** {1|2}
**Team:** ALL
**Type:** Validation

Run all automated validation checks for Wave {N}.

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
- Output: `validation-reports/wave-{N}-pass-1.json`
```

---

## Interface Contract Story Template

For stories that define or implement contracts:

```markdown
#### {TEAM}-CONTRACT-{N}: {Contract Name} Interface Definition
**Points:** 3 | **Wave:** 1 | **Sprint:** 1 | **Priority:** P0 | **MVP:** 1
**Interface:** {Contract Name} (v1.0.0)
**Team:** ARGUS-{TEAM}
**Type:** Contract

Define the {Contract Name} interface contract.

**Functional Requirements:**
- [ ] FUNC-1: Trait defined in contracts/traits/
- [ ] FUNC-2: All methods documented
- [ ] FUNC-3: Error types defined
- [ ] FUNC-4: Request/response types defined

**Contract Definition:**
- [ ] Trait signature finalized
- [ ] Error enum complete
- [ ] DTO structs defined
- [ ] Version: 1.0.0

**Contract Tests:**
- [ ] Contract test suite created
- [ ] Happy path tests
- [ ] Error case tests
- [ ] Consumer expectations documented

**Verification:**
- Command: `cargo test --package contracts`
- Expected: Contract tests pass
- File: `contracts/traits/{name}.rs`
```
