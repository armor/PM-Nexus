# NEXUS-NAV-001: Fix Duplicate Route in Infrastructure Console

**Story ID:** NEXUS-NAV-001
**Epic:** EPIC-1-NEXUS-NAVIGATION
**Points:** 1
**Sprint:** Sprint 1
**Status:** backlog

---

## User Story

**As a** platform user navigating the infrastructure console,
**I want** routes to resolve unambiguously,
**So that** I always land on the intended page without confusion or errors.

---

## Problem Statement

The infrastructure-console router has duplicate route definitions (lines 76-92 in `apps/infrastructure-console/src/router.tsx`) that cause unpredictable navigation behavior. Users may be routed to the wrong component when navigating to overlapping paths.

---

## Acceptance Criteria

- [ ] **AC1:** No duplicate path definitions exist in `infrastructure-console/src/router.tsx`
- [ ] **AC2:** All existing navigation flows continue to work correctly
- [ ] **AC3:** Router unit tests pass with 100% coverage on affected routes
- [ ] **AC4:** E2E test verifies `/infrastructure/assets` routes correctly
- [ ] **AC5:** No console warnings about duplicate routes in dev mode

---

## Technical Context

### Files to Modify
- `apps/infrastructure-console/src/router.tsx` (lines 76-92)

### Dependencies
- None (standalone fix)

### Risk Assessment
- **Low risk** - Isolated change to single file
- **Rollback:** Revert single file

---

## Test Requirements

### Unit Tests
```typescript
describe('infrastructure-console router', () => {
  it('should have no duplicate route paths', () => {
    const paths = routes.map(r => r.path);
    const unique = new Set(paths);
    expect(paths.length).toBe(unique.size);
  });
});
```

### E2E Tests
```typescript
test('infrastructure asset routes resolve correctly', async ({ page }) => {
  await page.goto('/infrastructure/assets');
  await expect(page.locator('[data-testid="asset-list"]')).toBeVisible();

  await page.goto('/infrastructure/assets/123');
  await expect(page.locator('[data-testid="asset-detail"]')).toBeVisible();
});
```

---

## Tasks

| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | Identify and document duplicate routes | 15min |
| task-02 | Remove duplicate route definitions | 15min |
| task-03 | Add unit tests for route uniqueness | 15min |
| task-04 | Add E2E test for navigation flow | 15min |

---

## Definition of Done

- [ ] Code reviewed and approved
- [ ] Unit tests passing
- [ ] E2E tests passing
- [ ] No console warnings
- [ ] PR merged to main

---

*Story owned by Frontend Team. Last updated: 2026-01-04*
