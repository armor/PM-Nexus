# Task 02: Enhance Component with Route Integration

**Task ID:** NEXUS-NAV-002-T02
**Story:** NEXUS-NAV-002
**Estimate:** 1 hour
**Type:** Implementation

---

## Critical Files

| File | Line | Status |
|------|------|--------|
| `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/AutoBreadcrumbs.tsx` | - | **EXISTS - MODIFY** |
| `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/AutoBreadcrumbs.stories.tsx` | - | **UPDATE REQUIRED** |
| `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/AutoBreadcrumbs.spec.tsx` | - | Update if exists |

> **IMPORTANT:** This modifies an EXISTING component. If Storybook stories exist, they MUST be updated to reflect new props/variants.

---

## Objective

Enhance the AutoBreadcrumbs component to automatically derive breadcrumbs from the current route hierarchy using React Router.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-002-T02 for the Nexus UI Uplift project.

CONTEXT:
- Component: libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/
- Router: React Router v6
- Goal: Auto-generate breadcrumbs from current route

INSTRUCTIONS:
1. Read the current AutoBreadcrumbs implementation
2. Enhance to support:

```typescript
interface AutoBreadcrumbsProps {
  /** Override auto-generated labels */
  customLabels?: Record<string, string>;
  /** Additional segments to append */
  append?: BreadcrumbSegment[];
  /** Hide home/root segment */
  hideRoot?: boolean;
  /** Maximum segments before truncation */
  maxSegments?: number;
  /** Separator between segments */
  separator?: ReactNode;
}

interface BreadcrumbSegment {
  label: string;
  path: string;
  icon?: ReactNode;
}
```

3. Implement route-based breadcrumb generation:

```typescript
import { useLocation, useMatches } from 'react-router-dom';

export function useAutoBreadcrumbs(customLabels?: Record<string, string>) {
  const location = useLocation();
  const matches = useMatches();

  return useMemo(() => {
    // Generate segments from route matches
    // Apply customLabels overrides
    // Handle dynamic segments (:id -> actual value)
  }, [location, matches, customLabels]);
}
```

4. Apply design system tokens:
   - Use colors from design-system.md
   - Apply typography scale
   - Use spacing tokens

5. Ensure accessibility:
   - <nav aria-label="Breadcrumb">
   - aria-current="page" on last item
   - Semantic <ol> list structure

CONSTRAINTS:
- Must work with all 9 console app routers
- Must support dynamic route params
- Must not break existing usage (if any)

OUTPUT:
- Enhanced AutoBreadcrumbs component
- Updated types/interfaces
- Hook for breadcrumb generation
```

---

## Checklist

- [ ] Route integration implemented
- [ ] useAutoBreadcrumbs hook created
- [ ] Design tokens applied
- [ ] Accessibility attributes added
- [ ] TypeScript types updated
- [ ] Component compiles without errors

---

## Design System Compliance

Reference: `docs/shared/design-system.md#10-navigation`

| Token | Usage |
|-------|-------|
| `--color-text-secondary` | Breadcrumb text |
| `--color-text-primary` | Current page text |
| `--color-interactive` | Hover state |
| `--spacing-xs` | Gap between items |
| `--font-size-sm` | Breadcrumb text size |

---

## Component Checklist (DoD)

Before marking this task complete, verify:

- [ ] TypeScript interfaces updated
- [ ] MUI sx props used (no styled-components)
- [ ] Unit tests updated and passing
- [ ] **Storybook stories updated** for all new props/variants
- [ ] Loading state implemented (if applicable)
- [ ] Error state implemented (if applicable)
- [ ] Accessibility audit passed (ARIA landmarks, semantic nav)
- [ ] data-testid attributes added
- [ ] Existing stories still work with changes

> Reference: `docs/shared/component-library.md#10-component-checklist`
