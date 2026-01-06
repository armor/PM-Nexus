# NEXUS-NAV-003: Standardize Path Formatting (Relative vs Absolute)

**Story ID:** NEXUS-NAV-003
**Epic:** EPIC-1-NEXUS-NAVIGATION
**Points:** 3
**Sprint:** Sprint 1
**Status:** backlog

---

## User Story

**As a** developer maintaining the platform,
**I want** consistent path formatting across all navigation,
**So that** links work predictably regardless of the current URL context.

---

## Problem Statement

The platform mixes relative and absolute paths inconsistently. Some components use `./details` while others use `/infrastructure/assets/123/details`. This causes navigation issues when the current URL context changes, leading to broken links and 404 errors.

---

## Acceptance Criteria

- [ ] **AC1:** All internal navigation paths use absolute format (`/path/to/resource`)
- [ ] **AC2:** No relative paths (`./`, `../`) exist in navigation code
- [ ] **AC3:** Link components consistently use absolute paths
- [ ] **AC4:** Router configurations use consistent path patterns
- [ ] **AC5:** E2E tests verify navigation from any page context
- [ ] **AC6:** Linting rule prevents relative paths in navigation

---

## Technical Context

### Files to Modify
- All Link/NavLink components across 9 console apps
- Router configurations in all apps
- Navigation utility functions

### Dependencies
- Depends on: NEXUS-NAV-001 (clean routes)
- Depends on: NEXUS-NAV-002 (breadcrumbs working)

### Pattern Reference
```typescript
// BAD - relative path
<Link to="./details">View Details</Link>
<Link to="../list">Back to List</Link>

// GOOD - absolute path
<Link to={`/infrastructure/assets/${assetId}/details`}>View Details</Link>
<Link to="/infrastructure/assets">Back to List</Link>
```

---

## Test Requirements

### Unit Tests
```typescript
describe('Navigation paths', () => {
  it('all Link components use absolute paths', () => {
    // AST scan for Link/NavLink components
    // Assert all 'to' props start with '/'
  });
});
```

### E2E Tests
```typescript
test('navigation works from any context', async ({ page }) => {
  // Navigate to page via different routes
  // Verify same action leads to same destination
});
```

---

## Tasks

| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | Audit all navigation paths across codebase | 1h |
| task-02 | Create path standardization utility | 30min |
| task-03 | Fix relative paths in all console apps | 1h |
| task-04 | Add ESLint rule for absolute paths | 30min |
| task-05 | Add E2E tests for cross-context navigation | 30min |

---

## Definition of Done

- [ ] No relative paths in navigation code
- [ ] ESLint rule added and passing
- [ ] E2E tests verify navigation consistency
- [ ] All console apps updated
- [ ] PR merged to main

---

*Story owned by Frontend Team. Last updated: 2026-01-04*
