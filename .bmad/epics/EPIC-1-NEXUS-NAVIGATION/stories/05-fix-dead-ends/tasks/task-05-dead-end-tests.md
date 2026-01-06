# Task 05: Add E2E Dead-End Detection Tests

**Task ID:** NEXUS-NAV-005-T05
**Story:** NEXUS-NAV-005
**Estimate:** 15 minutes
**Type:** E2E Testing

---

## Objective

Add E2E tests that automatically detect navigation dead-ends to prevent regressions.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-005-T05 for the Nexus UI Uplift project.

CONTEXT:
- E2E framework: Playwright
- Goal: Automated dead-end detection
- Scope: threat-management console

CRITICAL REQUIREMENTS (from CLAUDE.md):
- Tests MUST verify actual navigation works
- Capture and assert zero console errors
- Test should be generic enough to catch future dead-ends

INSTRUCTIONS:
1. Create dead-end detection utility:

```typescript
// e2e/utils/dead-end-detector.ts

interface NavigationAuditResult {
  path: string;
  hasBackNav: boolean;
  hasForwardNav: boolean;
  hasBreadcrumbs: boolean;
  navigationLinks: string[];
  isDeadEnd: boolean;
}

export async function auditPageNavigation(page: Page): Promise<NavigationAuditResult> {
  const path = new URL(page.url()).pathname;

  // Check for back navigation
  const hasBackButton = await page.locator('[data-testid="back-button"]').count() > 0;
  const hasBreadcrumbs = await page.locator('[data-testid="breadcrumbs"]').count() > 0;
  const hasBackNav = hasBackButton || hasBreadcrumbs;

  // Check for forward navigation
  const forwardLinks = await page.locator('a[href^="/threats"]').all();
  const hasForwardNav = forwardLinks.length > 0;

  // Collect navigation links
  const navigationLinks: string[] = [];
  for (const link of forwardLinks) {
    const href = await link.getAttribute('href');
    if (href) navigationLinks.push(href);
  }

  // A page is a dead-end if it has no way to navigate
  const isDeadEnd = !hasBackNav && !hasForwardNav;

  return {
    path,
    hasBackNav,
    hasForwardNav,
    hasBreadcrumbs,
    navigationLinks,
    isDeadEnd,
  };
}
```

2. Create dead-end detection tests:

```typescript
// e2e/navigation/dead-end-detection.spec.ts
import { test, expect } from '@playwright/test';
import { auditPageNavigation } from '../utils/dead-end-detector';

const THREAT_MANAGEMENT_ROUTES = [
  '/threats',
  '/threats/incidents',
  '/threats/incidents/INC-001',
  '/threats/incidents/INC-001/timeline',
  '/threats/alerts',
  '/threats/alerts/ALT-001',
  '/threats/responses',
  '/threats/responses/RSP-001',
];

test.describe('Navigation Dead-End Detection', () => {
  let consoleErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
  });

  test.afterEach(async () => {
    expect(consoleErrors).toHaveLength(0);
  });

  for (const route of THREAT_MANAGEMENT_ROUTES) {
    test(`${route} is not a dead-end`, async ({ page }) => {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      const audit = await auditPageNavigation(page);

      // Every page must have some navigation
      expect(audit.isDeadEnd).toBe(false);

      // Log for debugging
      if (audit.isDeadEnd) {
        console.log(`Dead-end detected at ${route}:`, audit);
      }
    });
  }

  test('can navigate through entire threat flow without dead-ends', async ({ page }) => {
    const visitedPaths: string[] = [];

    // Start at incidents list
    await page.goto('/threats/incidents');

    // Navigate to incident detail
    await page.click('[data-testid="incident-row-1"]');
    visitedPaths.push(page.url());
    let audit = await auditPageNavigation(page);
    expect(audit.isDeadEnd).toBe(false);

    // Navigate to timeline
    await page.click('[data-testid="view-timeline"]');
    visitedPaths.push(page.url());
    audit = await auditPageNavigation(page);
    expect(audit.isDeadEnd).toBe(false);

    // Navigate to related alert
    await page.click('[data-testid="related-alert-1"]');
    visitedPaths.push(page.url());
    audit = await auditPageNavigation(page);
    expect(audit.isDeadEnd).toBe(false);

    // Should be able to get back to incident
    const parentIncidentLink = page.locator('[data-testid="parent-incident-link"]');
    if (await parentIncidentLink.count() > 0) {
      await parentIncidentLink.click();
      visitedPaths.push(page.url());
      audit = await auditPageNavigation(page);
      expect(audit.isDeadEnd).toBe(false);
    }

    // All paths should be reachable
    expect(visitedPaths.length).toBeGreaterThan(2);
  });

  test('modal close returns to correct page', async ({ page }) => {
    // Navigate to incident
    await page.goto('/threats/incidents/INC-001');
    const beforeUrl = page.url();

    // Open assign modal
    await page.click('[data-testid="assign-button"]');
    await expect(page.locator('[data-testid="assign-modal"]')).toBeVisible();

    // Close modal
    await page.click('[data-testid="modal-cancel"]');

    // Should be on same page
    expect(page.url()).toBe(beforeUrl);
  });
});
```

OUTPUT:
- Dead-end detector utility created
- Tests for all threat-management routes
- Flow-through test for common paths
- Modal navigation test
```

---

## Checklist

- [ ] Dead-end detector utility created
- [ ] Tests for all routes
- [ ] Flow-through test created
- [ ] Modal test created
- [ ] Zero console errors
- [ ] All tests passing

---

## Test Coverage Matrix

| Route | Has Back | Has Forward | Dead-End |
|-------|----------|-------------|----------|
| /threats | - | ✓ | No |
| /threats/incidents | ✓ | ✓ | No |
| /threats/incidents/:id | ✓ | ✓ | No |
| /threats/incidents/:id/timeline | ✓ | ✓ | No |
| /threats/alerts | ✓ | ✓ | No |
| /threats/alerts/:id | ✓ | ✓ | No |
| /threats/responses | ✓ | ✓ | No |
| /threats/responses/:id | ✓ | ✓ | No |
