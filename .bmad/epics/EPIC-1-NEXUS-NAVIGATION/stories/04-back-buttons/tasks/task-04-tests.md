# Task 04: Add Unit and E2E Tests for BackButton

**Task ID:** NEXUS-NAV-004-T04
**Story:** NEXUS-NAV-004
**Estimate:** 30 minutes
**Type:** Testing

---

## Objective

Add comprehensive unit and E2E tests for the BackButton component and its state preservation functionality.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-004-T04 for the Nexus UI Uplift project.

CONTEXT:
- Component: BackButton
- Hooks: useNavigationState, useListNavigation
- Goal: Full test coverage for back navigation

CRITICAL REQUIREMENTS (from CLAUDE.md):
- Verify actual navigation, not just UI presence
- Test state preservation round-trip
- Zero console errors

INSTRUCTIONS:
1. Create unit tests:

```typescript
// libs/shared/react-ui/src/lib/components/BackButton/BackButton.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { BackButton } from './BackButton';

describe('BackButton', () => {
  const renderWithRouter = (ui: React.ReactElement, initialPath = '/detail') => {
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/list" element={<div>List Page</div>} />
          <Route path="/detail" element={ui} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('renders with label', () => {
    renderWithRouter(<BackButton to="/list" label="Assets" />);

    expect(screen.getByText('Back to Assets')).toBeInTheDocument();
  });

  it('renders without label', () => {
    renderWithRouter(<BackButton to="/list" />);

    expect(screen.getByText('Back')).toBeInTheDocument();
  });

  it('has correct href', () => {
    renderWithRouter(<BackButton to="/list" label="Assets" />);

    expect(screen.getByRole('link')).toHaveAttribute('href', '/list');
  });

  it('shows arrow icon', () => {
    renderWithRouter(<BackButton to="/list" />);

    expect(screen.getByRole('link').querySelector('svg')).toBeInTheDocument();
  });

  it('has accessible label', () => {
    renderWithRouter(<BackButton to="/list" label="Assets" />);

    expect(screen.getByRole('link')).toHaveAccessibleName('Back to Assets');
  });

  it('accepts custom aria-label', () => {
    renderWithRouter(
      <BackButton to="/list" aria-label="Return to asset list" />
    );

    expect(screen.getByRole('link')).toHaveAccessibleName('Return to asset list');
  });
});

// libs/shared/react-ui/src/lib/hooks/useNavigationState.test.tsx
describe('useNavigationState', () => {
  it('preserves scroll position', async () => {
    // Test implementation
  });

  it('preserves custom state', async () => {
    // Test implementation
  });

  it('falls back to direct navigation without state', async () => {
    // Test implementation
  });
});
```

2. Create E2E tests:

```typescript
// e2e/navigation/back-button.spec.ts
import { test, expect } from '@playwright/test';

test.describe('BackButton', () => {
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

  test('navigates back to list page', async ({ page }) => {
    await page.goto('/infrastructure/assets');
    await page.click('[data-testid="asset-row-1"]');

    await expect(page).toHaveURL(/\/infrastructure\/assets\/\d+/);

    await page.click('[data-testid="back-button"]');

    await expect(page).toHaveURL('/infrastructure/assets');
  });

  test('preserves list filters on return', async ({ page }) => {
    // Set filter
    await page.goto('/infrastructure/assets');
    await page.fill('[data-testid="filter-search"]', 'test-asset');
    await page.click('[data-testid="filter-apply"]');

    // Navigate to detail
    await page.click('[data-testid="asset-row-1"]');

    // Go back
    await page.click('[data-testid="back-button"]');

    // Verify filter preserved
    await expect(page.locator('[data-testid="filter-search"]')).toHaveValue('test-asset');
  });

  test('preserves scroll position on return', async ({ page }) => {
    await page.goto('/infrastructure/assets');

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 500));
    const scrollBefore = await page.evaluate(() => window.scrollY);
    expect(scrollBefore).toBeGreaterThan(0);

    // Navigate to detail
    await page.click('[data-testid="asset-row-10"]');

    // Go back
    await page.click('[data-testid="back-button"]');

    // Verify scroll restored (with some tolerance)
    const scrollAfter = await page.evaluate(() => window.scrollY);
    expect(scrollAfter).toBeCloseTo(scrollBefore, -1);
  });

  test('works when accessing detail directly', async ({ page }) => {
    // Access detail page directly (no navigation state)
    await page.goto('/infrastructure/assets/123');

    await page.click('[data-testid="back-button"]');

    // Should still navigate to list (fallback)
    await expect(page).toHaveURL('/infrastructure/assets');
  });

  test('shows contextual label', async ({ page }) => {
    await page.goto('/infrastructure/assets/123');

    await expect(page.locator('[data-testid="back-button"]')).toContainText('Back to Assets');
  });
});
```

OUTPUT:
- Unit tests created and passing
- E2E tests created and passing
- State preservation verified
```

---

## Checklist

- [ ] BackButton unit tests
- [ ] useNavigationState unit tests
- [ ] E2E navigation tests
- [ ] E2E state preservation tests
- [ ] E2E scroll restoration tests
- [ ] Direct access fallback tested
- [ ] Zero console errors
- [ ] All tests passing

---

## Coverage Targets

| File | Target |
|------|--------|
| BackButton.tsx | >90% |
| useNavigationState.ts | >90% |
| useListNavigation.ts | >90% |
