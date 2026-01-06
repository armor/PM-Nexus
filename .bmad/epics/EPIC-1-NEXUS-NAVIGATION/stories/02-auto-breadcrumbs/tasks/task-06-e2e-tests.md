# Task 06: Add E2E Tests Across Console Apps

**Task ID:** NEXUS-NAV-002-T06
**Story:** NEXUS-NAV-002
**Estimate:** 1 hour
**Type:** E2E Testing

---

## Objective

Add E2E tests that verify breadcrumb functionality works correctly across all 9 console applications.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-002-T06 for the Nexus UI Uplift project.

CONTEXT:
- E2E framework: Playwright
- Test location: e2e/navigation/breadcrumbs.spec.ts
- Goal: Verify breadcrumbs work in all 9 consoles

CRITICAL REQUIREMENTS (from CLAUDE.md):
- Tests MUST verify actual navigation, NOT just UI presence
- Capture and assert zero console errors
- Verify each breadcrumb click navigates correctly

INSTRUCTIONS:
1. Create comprehensive E2E test suite:

```typescript
import { test, expect, Page } from '@playwright/test';

const CONSOLES = [
  { name: 'infrastructure', basePath: '/infrastructure', deepPath: '/infrastructure/assets/test-asset' },
  { name: 'threat-management', basePath: '/threats', deepPath: '/threats/incidents/INC-001' },
  { name: 'compliance', basePath: '/compliance', deepPath: '/compliance/frameworks/cis/controls' },
  { name: 'identity', basePath: '/identity', deepPath: '/identity/users/user-123' },
  { name: 'cloud', basePath: '/cloud', deepPath: '/cloud/providers/aws/resources' },
  { name: 'endpoint', basePath: '/endpoint', deepPath: '/endpoint/devices/device-123' },
  { name: 'network', basePath: '/network', deepPath: '/network/flows/flow-123' },
  { name: 'reporting', basePath: '/reporting', deepPath: '/reporting/reports/report-123' },
  { name: 'admin', basePath: '/admin', deepPath: '/admin/users/user-123' },
];

test.describe('AutoBreadcrumbs E2E', () => {
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

  for (const console of CONSOLES) {
    test.describe(`${console.name} console`, () => {
      test('breadcrumbs render on deep navigation', async ({ page }) => {
        await page.goto(console.deepPath);

        const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
        await expect(breadcrumbs).toBeVisible();

        // Should have multiple segments
        const segments = breadcrumbs.locator('li');
        await expect(segments).toHaveCount({ greaterThan: 1 });
      });

      test('clicking breadcrumb navigates correctly', async ({ page }) => {
        await page.goto(console.deepPath);

        // Click second breadcrumb (not home, not current)
        const secondCrumb = page.locator('[data-testid="breadcrumbs"] a').nth(1);
        const expectedPath = await secondCrumb.getAttribute('href');

        await secondCrumb.click();
        await expect(page).toHaveURL(expectedPath!);
      });

      test('current page is not a link', async ({ page }) => {
        await page.goto(console.deepPath);

        const lastCrumb = page.locator('[data-testid="breadcrumbs"] li').last();
        await expect(lastCrumb.locator('a')).toHaveCount(0);
        await expect(lastCrumb).toHaveAttribute('aria-current', 'page');
      });
    });
  }

  test.describe('Mobile Truncation', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('shows ellipsis on mobile with deep paths', async ({ page }) => {
      await page.goto('/infrastructure/assets/asset-123/details/vulnerabilities');

      const ellipsis = page.locator('[data-testid="breadcrumb-ellipsis"]');
      await expect(ellipsis).toBeVisible();
    });

    test('ellipsis dropdown shows hidden items', async ({ page }) => {
      await page.goto('/infrastructure/assets/asset-123/details/vulnerabilities');

      await page.click('[data-testid="breadcrumb-ellipsis"]');

      const dropdown = page.locator('[role="menu"]');
      await expect(dropdown).toBeVisible();
      await expect(dropdown.locator('[role="menuitem"]')).toHaveCount({ greaterThan: 0 });
    });
  });

  test.describe('Accessibility', () => {
    test('breadcrumbs have correct ARIA structure', async ({ page }) => {
      await page.goto('/infrastructure/assets');

      // Check nav landmark
      const nav = page.locator('nav[aria-label*="breadcrumb" i]');
      await expect(nav).toBeVisible();

      // Check list structure
      const list = nav.locator('ol, ul');
      await expect(list).toBeVisible();
    });

    test('keyboard navigation works', async ({ page }) => {
      await page.goto('/infrastructure/assets/asset-123');

      // Tab through breadcrumbs
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      const focused = page.locator(':focus');
      await expect(focused).toHaveAttribute('href');
    });
  });
});
```

2. Run tests:
```bash
npx playwright test breadcrumbs.spec.ts
```

OUTPUT:
- E2E test file created
- All tests passing
- Test report generated
```

---

## Checklist

- [ ] Tests for all 9 consoles
- [ ] Navigation click tests
- [ ] Mobile truncation tests
- [ ] Accessibility tests
- [ ] Keyboard navigation tests
- [ ] Zero console errors
- [ ] All tests passing

---

## Test Matrix

| Console | Renders | Clickable | Mobile | A11y |
|---------|---------|-----------|--------|------|
| infrastructure | | | | |
| threat-management | | | | |
| compliance | | | | |
| identity | | | | |
| cloud | | | | |
| endpoint | | | | |
| network | | | | |
| reporting | | | | |
| admin | | | | |
