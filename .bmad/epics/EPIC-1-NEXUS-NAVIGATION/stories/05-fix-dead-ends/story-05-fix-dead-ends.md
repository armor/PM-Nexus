# NEXUS-NAV-005: Fix Navigation Dead-Ends in Threat Management

**Story ID:** NEXUS-NAV-005
**Epic:** EPIC-1-NEXUS-NAVIGATION
**Points:** 2
**Sprint:** Sprint 1
**Status:** backlog

---

## User Story

**As a** security analyst using threat management,
**I want** to always have a path forward or backward from any page,
**So that** I never get stuck in a navigation dead-end.

---

## Problem Statement

The threat-management console has several navigation dead-ends where users can reach a state with no clear way to continue or return. This includes:
- Incident detail pages with no related navigation
- Alert drill-downs that don't link back to parent incidents
- Threat detail pages that don't connect to response actions
- Modal flows that close to unexpected destinations

---

## Acceptance Criteria

- [ ] **AC1:** Every page in threat-management has at least one navigation option
- [ ] **AC2:** Incident detail pages link to related alerts and response actions
- [ ] **AC3:** Alert pages link back to parent incident if applicable
- [ ] **AC4:** Modal closures return to the expected parent page
- [ ] **AC5:** All navigation paths are documented in sitemap
- [ ] **AC6:** E2E tests verify no dead-ends exist

---

## Technical Context

### Files to Modify
- `apps/threat-management/src/pages/` (multiple pages)
- `apps/threat-management/src/components/` (navigation components)

### Dependencies
- Depends on: NEXUS-NAV-003 (absolute paths)
- Depends on: NEXUS-NAV-004 (back buttons)

### Known Dead-Ends
1. `/threats/incidents/:id/timeline` - No forward navigation
2. `/threats/alerts/:id` - Missing link to parent incident
3. `/threats/responses/:id` - No related threats link
4. Modal close on `/threats/incidents/:id/assign` returns to dashboard

---

## Test Requirements

### Unit Tests
```typescript
describe('threat-management navigation', () => {
  it('incident detail has navigation options', () => {});
  it('alert links to parent incident', () => {});
  it('modal closes to correct page', () => {});
});
```

### E2E Tests
```typescript
test('no navigation dead-ends', async ({ page }) => {
  // Visit every page in threat-management
  // Assert at least one navigation link exists
  // Assert back button or breadcrumbs exist
});
```

---

## Tasks

| Task | Description | Estimate |
|------|-------------|----------|
| task-01 | Audit all threat-management pages for dead-ends | 30min |
| task-02 | Fix incident detail navigation gaps | 30min |
| task-03 | Fix alert-to-incident linking | 30min |
| task-04 | Fix modal close destinations | 15min |
| task-05 | Add E2E dead-end detection tests | 15min |

---

## Definition of Done

- [ ] All dead-ends identified and fixed
- [ ] Every page has navigation options
- [ ] Modal flows return correctly
- [ ] E2E tests verify no dead-ends
- [ ] PR merged to main

---

*Story owned by Frontend Team. Last updated: 2026-01-04*
