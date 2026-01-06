# Task 05: Add Unit Tests and Storybook Stories

**Task ID:** NEXUS-STAB-001-T05
**Story:** NEXUS-STAB-001
**Estimate:** 1 hour
**Type:** Testing

---

## Critical Files

| File | Status |
|------|--------|
| `libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.spec.tsx` | **CREATE** |
| `libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.stories.tsx` | **CREATE** |

---

## Objective

Add comprehensive unit tests and Storybook documentation for the ErrorBoundary components.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-001-T05 for the Nexus UI Uplift project.

CONTEXT:
- Components: ErrorBoundary, ErrorFallback, hooks
- Test framework: Vitest + React Testing Library
- Docs: Storybook

INSTRUCTIONS:
1. Create unit tests:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary, ErrorFallback } from './index';

// Component that throws error
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
}

describe('ErrorBoundary', () => {
  // Suppress console.error for cleaner test output
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders fallback when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it('renders custom fallback component', () => {
    render(
      <ErrorBoundary fallback={<div>Custom fallback</div>}>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom fallback')).toBeInTheDocument();
  });

  it('renders fallback function with error props', () => {
    render(
      <ErrorBoundary
        fallback={({ error }) => <div>Error: {error.message}</div>}
      >
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error: Test error')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = jest.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({ componentStack: expect.any(String) })
    );
  });

  it('resets when retry is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    // Error state shown
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

    // Click retry
    fireEvent.click(screen.getByText(/try again/i));

    // Re-render without error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('resets when resetKeys change', () => {
    const { rerender } = render(
      <ErrorBoundary resetKeys={['key1']}>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

    // Change reset key
    rerender(
      <ErrorBoundary resetKeys={['key2']}>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });
});

describe('ErrorFallback', () => {
  it('displays error message', () => {
    const error = new Error('Test error message');
    render(
      <ErrorFallback
        error={error}
        errorInfo={null}
        resetErrorBoundary={jest.fn()}
      />
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('calls resetErrorBoundary when retry clicked', () => {
    const reset = jest.fn();
    render(
      <ErrorFallback
        error={new Error('Test')}
        errorInfo={null}
        resetErrorBoundary={reset}
      />
    );

    fireEvent.click(screen.getByText(/try again/i));
    expect(reset).toHaveBeenCalled();
  });

  it('shows error details in development', () => {
    const error = new Error('Test error');
    render(
      <ErrorFallback
        error={error}
        errorInfo={null}
        resetErrorBoundary={jest.fn()}
        showDetails
      />
    );

    const details = screen.getByText(/error details/i);
    fireEvent.click(details);
    expect(screen.getByText(/test error/i)).toBeInTheDocument();
  });
});
```

2. Create Storybook stories:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ErrorBoundary, ErrorFallback, AppErrorFallback, SectionErrorFallback } from './index';

const meta: Meta<typeof ErrorBoundary> = {
  component: ErrorBoundary,
  title: 'Feedback/ErrorBoundary',
  parameters: {
    docs: {
      description: {
        component: 'Catches JavaScript errors in child components and displays a fallback UI.',
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof ErrorBoundary>;

// Story that throws error on demand
function BuggyComponent({ shouldFail }: { shouldFail: boolean }) {
  if (shouldFail) throw new Error('Simulated component error');
  return <div className="p-4 bg-green-100 rounded">Component working correctly</div>;
}

export const Default: Story = {
  render: () => (
    <ErrorBoundary>
      <BuggyComponent shouldFail />
    </ErrorBoundary>
  ),
};

export const NoError: Story = {
  render: () => (
    <ErrorBoundary>
      <BuggyComponent shouldFail={false} />
    </ErrorBoundary>
  ),
};

// Fallback variants
const FallbackMeta: Meta<typeof ErrorFallback> = {
  component: ErrorFallback,
  title: 'Feedback/ErrorFallback',
};

export const SmallFallback: StoryObj<typeof ErrorFallback> = {
  args: {
    error: new Error('Component failed to load'),
    errorInfo: null,
    resetErrorBoundary: () => alert('Reset clicked'),
    size: 'sm',
  },
};

export const MediumFallback: StoryObj<typeof ErrorFallback> = {
  args: {
    error: new Error('Section failed to load'),
    errorInfo: null,
    resetErrorBoundary: () => alert('Reset clicked'),
    size: 'md',
  },
};

export const LargeFallback: StoryObj<typeof ErrorFallback> = {
  args: {
    error: new Error('Application crashed'),
    errorInfo: null,
    resetErrorBoundary: () => alert('Reset clicked'),
    size: 'lg',
  },
};

export const WithErrorDetails: StoryObj<typeof ErrorFallback> = {
  args: {
    error: new Error('Detailed error with stack trace'),
    errorInfo: { componentStack: '\n    at BuggyComponent\n    at ErrorBoundary\n    at App' },
    resetErrorBoundary: () => {},
    showDetails: true,
  },
};
```

OUTPUT:
- Unit tests for ErrorBoundary (>90% coverage)
- Unit tests for ErrorFallback
- Storybook stories for all variants
- Interactive examples
```

---

## Checklist

- [ ] ErrorBoundary unit tests
- [ ] ErrorFallback unit tests
- [ ] Hook unit tests
- [ ] Storybook stories created
- [ ] Interactive error triggering
- [ ] Coverage >90%

---

## Storybook Requirements (DoD)

Per `docs/shared/component-library.md#4-storybook-requirements`:

**Required Stories:**
1. Default story (error caught)
2. NoError story (children render normally)
3. All fallback variants (SmallFallback, MediumFallback, LargeFallback)
4. WithErrorDetails story (development mode)
5. Interactive test stories

**Story Structure:**
```typescript
// ErrorBoundary.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof ErrorBoundary> = {
  title: 'Feedback/ErrorBoundary',
  component: ErrorBoundary,
  tags: ['autodocs'],
};

export default meta;
```

> **Note:** ErrorBoundary is NOT API-connected, so MSW handlers are not required.
