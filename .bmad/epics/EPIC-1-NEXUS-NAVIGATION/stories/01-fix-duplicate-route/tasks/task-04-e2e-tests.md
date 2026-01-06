# Task 04: Add E2E Test for Navigation Flow

**Task ID:** NEXUS-NAV-001-T04
**Story:** NEXUS-NAV-001
**Estimate:** 15 minutes
**Type:** E2E Testing

---

## Objective

Add E2E tests that verify the infrastructure routes resolve correctly after duplicate removal.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-001-T04 for the Nexus UI Uplift project.

CONTEXT:
- E2E framework: Playwright
- Test location: apps/infrastructure-console/e2e/navigation.spec.ts
- Goal: Verify routes work correctly in real browser

CRITICAL REQUIREMENTS (from CLAUDE.md):
- Tests MUST verify actual system behavior, NOT just UI feedback
- Intercept network requests to prove API calls happen
- Reload page to verify persistence where applicable
- Capture and assert zero console errors

INSTRUCTIONS:
1. Create E2E test file for infrastructure navigation
2. Implement tests that:
   - Navigate to /infrastructure/assets
   - Verify correct component renders (not just any content)
   - Navigate to /infrastructure/assets/:id
   - Verify detail view renders
   - Check for zero console errors throughout

TEST IMPLEMENTATION:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Infrastructure Console Navigation', () => {
  let consoleErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', err => consoleErrors.push(err.message));
  });

  test.afterEach(async () => {
    expect(consoleErrors).toHaveLength(0);
  });

  test('asset list route resolves correctly', async ({ page }) => {
    // Navigate and verify API call
    const [response] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/assets') && r.status() === 200),
      page.goto('/infrastructure/assets')
    ]);

    expect(response.status()).toBe(200);
    await expect(page.locator('[data-testid="asset-list"]')).toBeVisible();
  });

  test('asset detail route resolves correctly', async ({ page }) => {
    await page.goto('/infrastructure/assets/test-asset-123');

    await expect(page.locator('[data-testid="asset-detail"]')).toBeVisible();
    await expect(page.locator('[data-testid="asset-id"]')).toContainText('test-asset-123');
  });

  test('no route conflicts between list and detail', async ({ page }) => {
    // Start at list
    await page.goto('/infrastructure/assets');
    await expect(page.locator('[data-testid="asset-list"]')).toBeVisible();

    // Navigate to detail
    await page.click('[data-testid="asset-row"]:first-child');
    await expect(page.locator('[data-testid="asset-detail"]')).toBeVisible();

    // Navigate back to list
    await page.goBack();
    await expect(page.locator('[data-testid="asset-list"]')).toBeVisible();
  });
});
```

3. Run: `npx playwright test navigation.spec.ts`

OUTPUT:
- E2E test file created
- All tests passing
- Screenshot evidence of test execution
```

---

## Checklist

- [ ] E2E test file created
- [ ] List route test passing
- [ ] Detail route test passing
- [ ] Navigation flow test passing
- [ ] Zero console errors verified
- [ ] Screenshots captured

---

## Evidence Requirements

After test execution, capture:
- Test output showing all green
- Screenshots of each navigation state
- Network log showing correct API calls
