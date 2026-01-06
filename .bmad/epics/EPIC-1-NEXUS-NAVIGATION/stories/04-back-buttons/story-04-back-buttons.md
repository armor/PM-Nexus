# NEXUS-NAV-004: Add Missing Back Buttons with Contextual Return

**Story ID:** NEXUS-NAV-004
**Epic:** EPIC-1-NEXUS-NAVIGATION
**Points:** 3
**Sprint:** Sprint 1
**Status:** backlog

---

## User Story

**As a** platform user viewing a detail page,
**I want** a contextual back button that returns me to my previous location,
**So that** I can continue my workflow without losing context.

---

## Problem Statement

Many detail pages lack back navigation, forcing users to rely on browser back (which may navigate away from the app) or breadcrumbs (which don't preserve list filters/scroll position). Users need consistent, contextual back navigation that preserves their workflow state.

---

## Acceptance Criteria

- [ ] **AC1:** Every detail page has a back button in the header area
- [ ] **AC2:** Back button returns to the logical parent (e.g., asset detail → asset list)
- [ ] **AC3:** Back button preserves list filters and scroll position when possible
- [ ] **AC4:** Back button shows contextual label (e.g., "Back to Assets" not just "Back")
- [ ] **AC5:** Back button uses left-arrow icon per design system
- [ ] **AC6:** Back button works correctly even when detail page is accessed directly via URL

---

## Technical Context

### Files to Modify
- Create: `libs/shared/react-ui/src/lib/components/BackButton/`
- Update: All detail page headers across 9 console apps

### Dependencies
- Uses: NEXUS-NAV-003 (absolute paths working)
- Uses: React Router navigation

### Design Pattern
```typescript
interface BackButtonProps {
  /** Target path (absolute) */
  to: string;
  /** Label shown next to icon */
  label?: string;
  /** Preserve navigation state (filters, scroll) */
  preserveState?: boolean;
}

// Usage
<BackButton to="/infrastructure/assets" label="Assets" />
```

---

## Test Requirements

### Unit Tests
```typescript
describe('BackButton', () => {
  it('navigates to specified path on click', () => {});
  it('shows contextual label', () => {});
  it('renders accessible button', () => {});
  it('preserves state when configured', () => {});
});
```

### E2E Tests
```typescript
test('back button returns to list', async ({ page }) => {
  await page.goto('/infrastructure/assets');
  await page.click('[data-testid="asset-row-1"]');
  await page.click('[data-testid="back-button"]');
  await expect(page).toHaveURL('/infrastructure/assets');
});
```

---

## Tasks

| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | Create BackButton component | 30min |
| task-02 | Implement state preservation logic | 30min |
| task-03 | Add to all detail pages across consoles | 1.5h |
| task-04 | Add unit and E2E tests | 30min |

---

## Definition of Done

- [ ] BackButton component created
- [ ] All detail pages have back button
- [ ] State preservation working
- [ ] Unit tests passing
- [ ] E2E tests passing
- [ ] Accessibility verified
- [ ] PR merged to main

---

*Story owned by Frontend Team. Last updated: 2026-01-04*
