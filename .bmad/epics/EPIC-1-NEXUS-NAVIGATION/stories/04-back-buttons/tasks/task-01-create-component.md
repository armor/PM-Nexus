# Task 01: Create BackButton Component

**Task ID:** NEXUS-NAV-004-T01
**Story:** NEXUS-NAV-004
**Estimate:** 30 minutes
**Type:** Implementation

---

## Critical Files

| File | Status |
|------|--------|
| `libs/shared/react-ui/src/lib/components/BackButton/` | **CREATE NEW** |
| `libs/shared/react-ui/src/lib/components/BackButton/BackButton.stories.tsx` | **CREATE** |
| `libs/shared/react-ui/src/lib/components/BackButton/BackButton.spec.tsx` | **CREATE** |

---

## Nx Generator Command (MANDATORY)

```bash
nx g @platform/armor-nx-plugin:react-component \
  --name=BackButton \
  --project=shared-react-ui \
  --directory=components/BackButton \
  --export=true
```

> **IMPORTANT:** Never create components manually. Always use the Nx generator first.

---

## Objective

Create a reusable BackButton component that provides consistent, contextual back navigation across the platform.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-004-T01 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/react-ui/src/lib/components/
- Goal: Reusable back button with contextual label
- Design: Left arrow icon + "Back to {Label}"

INSTRUCTIONS:
1. Create BackButton component:

```typescript
// libs/shared/react-ui/src/lib/components/BackButton/BackButton.tsx
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

export interface BackButtonProps {
  /** Target path for navigation (absolute path) */
  to: string;
  /** Label shown after "Back to" (e.g., "Assets") */
  label?: string;
  /** Use browser history instead of direct navigation */
  useHistory?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Accessible description override */
  'aria-label'?: string;
}

export function BackButton({
  to,
  label,
  useHistory = false,
  className,
  'aria-label': ariaLabel,
}: BackButtonProps) {
  const navigate = useNavigate();

  const handleClick = (e: React.MouseEvent) => {
    if (useHistory) {
      e.preventDefault();
      navigate(-1);
    }
  };

  const displayLabel = label ? `Back to ${label}` : 'Back';

  return (
    <Link
      to={to}
      onClick={handleClick}
      className={cn(
        'inline-flex items-center gap-2',
        'text-sm font-medium',
        'text-secondary hover:text-primary',
        'transition-colors duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-interactive',
        className
      )}
      aria-label={ariaLabel || displayLabel}
    >
      <ArrowLeftIcon className="h-4 w-4" aria-hidden="true" />
      <span>{displayLabel}</span>
    </Link>
  );
}
```

2. Create index file:

```typescript
// libs/shared/react-ui/src/lib/components/BackButton/index.ts
export { BackButton } from './BackButton';
export type { BackButtonProps } from './BackButton';
```

3. Export from library:

```typescript
// libs/shared/react-ui/src/index.ts
export * from './lib/components/BackButton';
```

4. Add to Storybook:

```typescript
// libs/shared/react-ui/src/lib/components/BackButton/BackButton.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { BackButton } from './BackButton';

const meta: Meta<typeof BackButton> = {
  component: BackButton,
  title: 'Navigation/BackButton',
};

export default meta;
type Story = StoryObj<typeof BackButton>;

export const Default: Story = {
  args: {
    to: '/infrastructure/assets',
    label: 'Assets',
  },
};

export const WithoutLabel: Story = {
  args: {
    to: '/infrastructure',
  },
};

export const UseHistory: Story = {
  args: {
    to: '/infrastructure/assets',
    label: 'Assets',
    useHistory: true,
  },
};
```

OUTPUT:
- BackButton component created
- Types exported
- Storybook stories added
- Component compiles cleanly
```

---

## Checklist

- [ ] Component created
- [ ] Props interface defined
- [ ] Styling applied per design system
- [ ] Exported from library
- [ ] Storybook stories added
- [ ] Component compiles

---

## Design System Tokens

| Token | Usage |
|-------|-------|
| `--color-text-secondary` | Default text color |
| `--color-text-primary` | Hover text color |
| `--color-interactive` | Focus ring |
| `--spacing-xs` | Gap between icon and text |
| `--font-size-sm` | Text size |

---

## Component Checklist (DoD)

Before marking this task complete, verify all items from `docs/shared/component-library.md#10-component-checklist`:

- [ ] Created with Nx generator (see command above)
- [ ] TypeScript interfaces defined
- [ ] MUI sx props used (no styled-components)
- [ ] Unit tests written and passing
- [ ] **Storybook stories** for all variants (Default, WithoutLabel, UseHistory)
- [ ] Loading state implemented (N/A for this component)
- [ ] Error state implemented (N/A for this component)
- [ ] Accessibility audit passed (focus ring, aria-label)
- [ ] data-testid attributes added
- [ ] Documentation written
- [ ] Code review completed
- [ ] Visual regression baseline captured
