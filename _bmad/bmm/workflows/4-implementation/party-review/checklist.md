# Party Review Checklist

## Pre-Review Requirements

- [ ] Story file loaded with complete context
- [ ] All files in scope identified (File List + git diff)
- [ ] Project context loaded for standards reference
- [ ] All required reviewers available

## Review Board Composition

### Required Reviewers (All Must Approve)

- [ ] **Code Reviewer** - Code quality focus
  - [ ] DRY violations checked
  - [ ] SOLID principles verified
  - [ ] No nested conditionals
  - [ ] No hardcoded values
  - [ ] Type safety confirmed
  - [ ] Error handling reviewed
  - [ ] Resource management checked

- [ ] **Security Reviewer** - OWASP focus (BLOCKING)
  - [ ] Injection vulnerabilities checked
  - [ ] Authentication reviewed
  - [ ] Authorization verified
  - [ ] Data exposure scanned
  - [ ] Cryptography assessed
  - [ ] XSS/CSRF checked
  - [ ] Input validation reviewed

- [ ] **QA Auditor** - Test coverage focus
  - [ ] All ACs have implementation
  - [ ] All ACs have tests
  - [ ] Edge cases covered
  - [ ] Error scenarios tested
  - [ ] Test quality verified
  - [ ] No placeholder assertions

- [ ] **Architect** - Architecture focus
  - [ ] Follows documented patterns
  - [ ] Layer separation correct
  - [ ] API design compliant
  - [ ] Database schema followed
  - [ ] Service boundaries respected
  - [ ] Scalability considered

### Optional Reviewers

- [ ] **Tech Writer** (if enabled)
  - [ ] API docs updated
  - [ ] Inline comments present
  - [ ] README updated
  - [ ] Architecture docs current

## Verdict Requirements

| Condition | Result |
|-----------|--------|
| All APPROVE | APPROVED |
| Security REJECT | REJECTED (VETO) |
| Any other REJECT | REJECTED |

## Review Outcome

### Verdicts

| Reviewer | Verdict | Findings Count |
|----------|---------|----------------|
| Code Reviewer | _____ | _____ |
| Security Reviewer | _____ | _____ |
| QA Auditor | _____ | _____ |
| Architect | _____ | _____ |
| Tech Writer | _____ | _____ |

### Final Decision

- [ ] **APPROVED** - All reviewers approved, ready for merge
- [ ] **REJECTED** - One or more reviewers rejected

### If Rejected

Consolidated remediation items:
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**Next Action:** Address findings, then run `/story-party` to reconvene.

---

## Party Mode Principles

1. **Parallel Execution** - All reviewers run simultaneously
2. **Domain Focus** - Each reviewer stays in their lane
3. **Unanimous Required** - One rejection blocks the story
4. **Security Veto** - Security can block regardless of others
5. **Consolidated Feedback** - All findings merged into one remediation list
