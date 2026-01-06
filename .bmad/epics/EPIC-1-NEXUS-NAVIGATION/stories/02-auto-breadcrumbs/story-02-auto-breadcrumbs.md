# NEXUS-NAV-002: Implement AutoBreadcrumbs Across All 9 Console Apps

**Story ID:** NEXUS-NAV-002
**Epic:** EPIC-1-NEXUS-NAVIGATION
**Points:** 5
**Sprint:** Sprint 1
**Status:** backlog

---

## User Story

**As a** platform user navigating deep into console hierarchies,
**I want** breadcrumbs that automatically reflect my location,
**So that** I always know where I am and can navigate back easily.

---

## Problem Statement

The platform has an `AutoBreadcrumbs` component in `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/` that exists but is unused. Users currently have no consistent way to understand their location within the 9 console apps or navigate back through the hierarchy.

---

## Acceptance Criteria

- [ ] **AC1:** AutoBreadcrumbs component renders on all pages across 9 console apps
- [ ] **AC2:** Breadcrumbs accurately reflect the current route hierarchy
- [ ] **AC3:** Each breadcrumb segment is clickable and navigates to that level
- [ ] **AC4:** Breadcrumbs truncate gracefully on mobile (show first + last with ellipsis)
- [ ] **AC5:** Component follows design system specs (spacing, typography, colors)
- [ ] **AC6:** E2E tests verify breadcrumb functionality in each console app

---

## Technical Context

### Files to Modify
- `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/` (enhance existing)
- All 9 console app layout components:
  - `apps/infrastructure-console/src/layouts/`
  - `apps/threat-management/src/layouts/`
  - `apps/compliance-console/src/layouts/`
  - `apps/identity-console/src/layouts/`
  - `apps/cloud-console/src/layouts/`
  - `apps/endpoint-console/src/layouts/`
  - `apps/network-console/src/layouts/`
  - `apps/reporting-console/src/layouts/`
  - `apps/admin-console/src/layouts/`

### Dependencies
- Depends on: NEXUS-NAV-001 (clean routes first)
- Uses: React Router, design-system tokens

### Design System Reference
- `docs/shared/design-system.md#10-navigation`
- `docs/shared/component-library.md` - Breadcrumbs component spec

---

## Test Requirements

### Unit Tests
```typescript
describe('AutoBreadcrumbs', () => {
  it('renders breadcrumbs from route hierarchy', () => {});
  it('each segment is clickable', () => {});
  it('truncates on mobile viewport', () => {});
  it('handles deep nesting (5+ levels)', () => {});
});
```

### E2E Tests
```typescript
test('breadcrumbs show correct hierarchy', async ({ page }) => {
  await page.goto('/infrastructure/assets/asset-123/details');

  const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
  await expect(breadcrumbs.locator('a')).toHaveCount(3);
  await expect(breadcrumbs).toContainText('Infrastructure');
  await expect(breadcrumbs).toContainText('Assets');
  await expect(breadcrumbs).toContainText('asset-123');
});
```

---

## Tasks

| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | Audit existing AutoBreadcrumbs component | 30min |
| task-02 | Enhance component with route integration | 1h |
| task-03 | Add mobile truncation behavior | 30min |
| task-04 | Integrate into all 9 console layouts | 2h |
| task-05 | Add unit tests for component | 30min |
| task-06 | Add E2E tests across consoles | 1h |

---

## Definition of Done

- [ ] AutoBreadcrumbs renders on every page
- [ ] Unit tests passing (>90% coverage)
- [ ] E2E tests passing for all 9 consoles
- [ ] Mobile responsiveness verified
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] PR merged to main

---

*Story owned by Frontend Team. Last updated: 2026-01-04*
