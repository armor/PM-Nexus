# Task 05: Add E2E Tests for Cross-Context Navigation

**Task ID:** NEXUS-NAV-003-T05
**Story:** NEXUS-NAV-003
**Estimate:** 30 minutes
**Type:** E2E Testing

---

## Objective

Add E2E tests that verify navigation works correctly regardless of the page context from which it's initiated.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-003-T05 for the Nexus UI Uplift project.

CONTEXT:
- E2E framework: Playwright
- Goal: Verify absolute paths work from any context
- Key risk: Relative paths break when URL context changes

CRITICAL REQUIREMENTS (from CLAUDE.md):
- Tests MUST verify actual navigation occurs
- Capture and assert zero console errors
- Test same action from multiple starting points

INSTRUCTIONS:
1. Create cross-context navigation tests:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Cross-Context Navigation', () => {
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

  test.describe('Asset Detail Navigation', () => {
    const ASSET_ID = 'test-asset-123';
    const EXPECTED_URL = `/infrastructure/assets/${ASSET_ID}`;

    test('navigates from asset list', async ({ page }) => {
      await page.goto('/infrastructure/assets');
      await page.click(`[data-testid="asset-row-${ASSET_ID}"]`);
      await expect(page).toHaveURL(EXPECTED_URL);
    });

    test('navigates from dashboard search', async ({ page }) => {
      await page.goto('/dashboard');
      await page.fill('[data-testid="global-search"]', ASSET_ID);
      await page.click('[data-testid="search-result-asset"]');
      await expect(page).toHaveURL(EXPECTED_URL);
    });

    test('navigates from incident related assets', async ({ page }) => {
      await page.goto('/threats/incidents/INC-001');
      await page.click(`[data-testid="related-asset-${ASSET_ID}"]`);
      await expect(page).toHaveURL(EXPECTED_URL);
    });

    test('direct URL access works', async ({ page }) => {
      await page.goto(EXPECTED_URL);
      await expect(page.locator('[data-testid="asset-detail"]')).toBeVisible();
    });
  });

  test.describe('Navigation Consistency', () => {
    const testCases = [
      {
        name: 'from root',
        startUrl: '/',
        action: async (page) => page.click('[data-testid="nav-infrastructure"]'),
        expectedUrl: '/infrastructure',
      },
      {
        name: 'from deep nested page',
        startUrl: '/infrastructure/assets/123/details/vulnerabilities',
        action: async (page) => page.click('[data-testid="nav-threats"]'),
        expectedUrl: '/threats',
      },
      {
        name: 'from different console',
        startUrl: '/compliance/frameworks',
        action: async (page) => page.click('[data-testid="nav-infrastructure"]'),
        expectedUrl: '/infrastructure',
      },
    ];

    for (const tc of testCases) {
      test(`navigation works ${tc.name}`, async ({ page }) => {
        await page.goto(tc.startUrl);
        await tc.action(page);
        await expect(page).toHaveURL(tc.expectedUrl);
      });
    }
  });

  test.describe('Back/Forward Navigation', () => {
    test('browser history works correctly', async ({ page }) => {
      // Navigate through multiple pages
      await page.goto('/infrastructure');
      await page.click('[data-testid="nav-assets"]');
      await expect(page).toHaveURL('/infrastructure/assets');

      await page.click('[data-testid="asset-row-1"]');
      await expect(page).toHaveURL('/infrastructure/assets/1');

      // Go back
      await page.goBack();
      await expect(page).toHaveURL('/infrastructure/assets');

      // Go forward
      await page.goForward();
      await expect(page).toHaveURL('/infrastructure/assets/1');
    });
  });

  test.describe('No 404 Errors', () => {
    test('all navigation links resolve', async ({ page }) => {
      const notFoundErrors: string[] = [];

      page.on('response', response => {
        if (response.status() === 404) {
          notFoundErrors.push(response.url());
        }
      });

      // Navigate through common paths
      await page.goto('/infrastructure');
      await page.click('[data-testid="nav-assets"]');
      await page.click('[data-testid="asset-row-1"]');
      await page.click('[data-testid="nav-details-tab"]');

      expect(notFoundErrors).toHaveLength(0);
    });
  });
});
```

OUTPUT:
- E2E test file created
- All tests passing
- Cross-context navigation verified
```

---

## Checklist

- [ ] Cross-context navigation tests
- [ ] Browser history tests
- [ ] No 404 errors tests
- [ ] Console error capture
- [ ] All tests passing

---

## Test Scenarios

| Start Context | Action | Expected Result |
|---------------|--------|-----------------|
| / | Click Infrastructure | /infrastructure |
| /threats/incidents/1 | Click related asset | /infrastructure/assets/{id} |
| /compliance | Global search asset | /infrastructure/assets/{id} |
| Deep nested page | Nav to different console | Correct console root |
