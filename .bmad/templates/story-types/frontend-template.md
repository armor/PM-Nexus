# Frontend Story Template

> **Template Type:** Frontend (React/TypeScript)
> **Applies To:** UI components, pages, forms, data tables

---

## Pre-filled Sections for Frontend Stories

### Standard Component Structure
```
apps/argus-ui/src/
├── components/
│   └── {{feature}}/
│       ├── {{Component}}.tsx
│       ├── {{Component}}.test.tsx
│       └── index.ts
├── pages/
│   └── {{page}}/
│       └── index.tsx
├── hooks/
│   └── use{{Hook}}.ts
└── api/
    └── {{feature}}.ts
```

### Standard Component Pattern
```typescript
import { FC } from 'react';
import { cn } from '@/lib/utils';

interface {{Component}}Props {
  // props
}

export const {{Component}}: FC<{{Component}}Props> = ({
  // destructured props
}) => {
  return (
    <div className={cn('', className)}>
      {/* component content */}
    </div>
  );
};
```

### Standard API Hook Pattern
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function use{{Feature}}() {
  return useQuery({
    queryKey: ['{{feature}}'],
    queryFn: () => api.get('/api/v1/{{feature}}'),
  });
}

export function useCreate{{Feature}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Create{{Feature}}Request) =>
      api.post('/api/v1/{{feature}}', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{{feature}}'] });
    },
  });
}
```

### Standard Test Pattern (E2E)
```typescript
import { test, expect, Page } from '@playwright/test';

test.describe('{{Feature}}', () => {
  let page: Page;
  const consoleErrors: string[] = [];

  test.beforeEach(async ({ page: p }) => {
    page = p;
    consoleErrors.length = 0;
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
  });

  test.afterEach(async () => {
    expect(consoleErrors).toHaveLength(0);
  });

  test('should {{expected_behavior}}', async () => {
    // Navigate
    await page.goto('/{{route}}');

    // Interact
    await page.getByRole('button', { name: '{{button}}' }).click();

    // Verify API call
    const response = await page.waitForResponse(r =>
      r.url().includes('/api/v1/{{endpoint}}') &&
      r.request().method() === '{{METHOD}}'
    );
    expect(response.status()).toBe(200);

    // Verify persistence
    await page.reload();
    await expect(page.getByText('{{expected_text}}')).toBeVisible();
  });
});
```

### Standard Form Pattern
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  // field validations
});

type FormData = z.infer<typeof schema>;

export function {{Form}}() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    // handle submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* form fields */}
    </form>
  );
}
```

---

## Frontend Story AI Prompt Template

```
IMPLEMENT {{STORY_ID}}: {{STORY_TITLE}}

CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are building {{WHAT}} in the Argus UI.
This component provides {{PURPOSE}} for {{USER_TYPE}}.

DESIGN REFERENCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Figma: {{FIGMA_LINK}}
- Pattern: {{PATTERN_REFERENCE}}
- Similar component: {{SIMILAR_COMPONENT}}

TARGET FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {{FILE_1}}: Component
2. {{FILE_2}}: API hook
3. {{FILE_3}}: Tests

USER INTERACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. User sees: {{INITIAL_STATE}}
2. User action: {{ACTION}}
3. System response: {{RESPONSE}}
4. Final state: {{FINAL_STATE}}

IMPLEMENTATION STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Create component file
2. Add API hook for data fetching
3. Implement UI with Tailwind
4. Add loading/error states
5. Add E2E test with persistence verification
6. Verify console errors = 0

EXACT CODE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{EXACT_CODE}}

E2E TEST (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{E2E_TEST_CODE}}

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
npm run lint
npm run typecheck
npm run test -- {{test_file}}
npm run e2e -- {{e2e_file}}

# All must pass with:
# - 0 lint errors
# - 0 type errors
# - 0 console errors in E2E
# - API calls verified
# - Persistence verified (reload test)

ACCESSIBILITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Keyboard navigable
- [ ] ARIA labels on interactive elements
- [ ] Color contrast passes WCAG AA
- [ ] Focus indicators visible
```
