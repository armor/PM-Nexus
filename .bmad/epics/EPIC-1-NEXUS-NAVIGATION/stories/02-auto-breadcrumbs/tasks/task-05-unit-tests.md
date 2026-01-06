# Task 05: Add Unit Tests for AutoBreadcrumbs Component

**Task ID:** NEXUS-NAV-002-T05
**Story:** NEXUS-NAV-002
**Estimate:** 30 minutes
**Type:** Testing

---

## Objective

Add comprehensive unit tests for the enhanced AutoBreadcrumbs component to ensure reliability and prevent regressions.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-002-T05 for the Nexus UI Uplift project.

CONTEXT:
- Component: libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/
- Test framework: Vitest + React Testing Library
- Goal: >90% code coverage

INSTRUCTIONS:
1. Create comprehensive test suite:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AutoBreadcrumbs } from './AutoBreadcrumbs';

describe('AutoBreadcrumbs', () => {
  const renderWithRouter = (initialPath: string) => {
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/" element={<AutoBreadcrumbs />}>
            <Route path="infrastructure">
              <Route path="assets">
                <Route path=":id" element={<div>Asset Detail</div>} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </MemoryRouter>
    );
  };

  describe('Breadcrumb Generation', () => {
    it('renders breadcrumbs from route hierarchy', () => {
      renderWithRouter('/infrastructure/assets/123');

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Infrastructure')).toBeInTheDocument();
      expect(screen.getByText('Assets')).toBeInTheDocument();
      expect(screen.getByText('123')).toBeInTheDocument();
    });

    it('applies custom labels when provided', () => {
      render(
        <MemoryRouter initialEntries={['/infrastructure']}>
          <AutoBreadcrumbs customLabels={{ infrastructure: 'Infra' }} />
        </MemoryRouter>
      );

      expect(screen.getByText('Infra')).toBeInTheDocument();
    });

    it('hides root when hideRoot is true', () => {
      render(
        <MemoryRouter initialEntries={['/infrastructure']}>
          <AutoBreadcrumbs hideRoot />
        </MemoryRouter>
      );

      expect(screen.queryByText('Home')).not.toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('each segment except last is clickable', () => {
      renderWithRouter('/infrastructure/assets/123');

      const links = screen.getAllByRole('link');
      expect(links).toHaveLength(3); // Home, Infrastructure, Assets (not 123)
    });

    it('last segment is not a link (current page)', () => {
      renderWithRouter('/infrastructure/assets/123');

      const current = screen.getByText('123');
      expect(current.tagName).not.toBe('A');
      expect(current).toHaveAttribute('aria-current', 'page');
    });
  });

  describe('Mobile Truncation', () => {
    it('truncates when segments exceed maxSegments', () => {
      render(
        <MemoryRouter initialEntries={['/a/b/c/d/e']}>
          <AutoBreadcrumbs maxSegments={3} />
        </MemoryRouter>
      );

      expect(screen.getByLabelText(/show.*more/i)).toBeInTheDocument();
    });

    it('ellipsis dropdown shows hidden segments', () => {
      render(
        <MemoryRouter initialEntries={['/a/b/c/d/e']}>
          <AutoBreadcrumbs maxSegments={3} />
        </MemoryRouter>
      );

      fireEvent.click(screen.getByLabelText(/show.*more/i));
      expect(screen.getByRole('menu')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has nav landmark with aria-label', () => {
      renderWithRouter('/infrastructure');

      const nav = screen.getByRole('navigation', { name: /breadcrumb/i });
      expect(nav).toBeInTheDocument();
    });

    it('uses semantic list structure', () => {
      renderWithRouter('/infrastructure/assets');

      expect(screen.getByRole('list')).toBeInTheDocument();
      expect(screen.getAllByRole('listitem')).toHaveLength(3);
    });
  });
});
```

2. Run tests with coverage:
```bash
npx vitest run --coverage
```

3. Ensure >90% coverage on:
   - AutoBreadcrumbs.tsx
   - useAutoBreadcrumbs.ts
   - BreadcrumbEllipsis.tsx

OUTPUT:
- Test file created
- All tests passing
- Coverage report showing >90%
```

---

## Checklist

- [ ] Breadcrumb generation tests
- [ ] Navigation tests
- [ ] Mobile truncation tests
- [ ] Accessibility tests
- [ ] Custom labels tests
- [ ] Coverage >90%

---

## Coverage Targets

| File | Target |
|------|--------|
| AutoBreadcrumbs.tsx | >90% |
| useAutoBreadcrumbs.ts | >90% |
| BreadcrumbEllipsis.tsx | >90% |
