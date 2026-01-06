# Task 01: Create ErrorBoundary Class Component

**Task ID:** NEXUS-STAB-001-T01
**Story:** NEXUS-STAB-001
**Estimate:** 1 hour
**Type:** Implementation

---

## Critical Files

| File | Status |
|------|--------|
| `libs/shared/react-ui/src/lib/components/ErrorBoundary/` | **CREATE NEW** |
| `libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.stories.tsx` | **CREATE** |
| `libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.spec.tsx` | **CREATE** |

---

## Nx Generator Command (MANDATORY)

```bash
nx g @platform/armor-nx-plugin:react-component \
  --name=ErrorBoundary \
  --project=shared-react-ui \
  --directory=components/ErrorBoundary \
  --export=true
```

> **IMPORTANT:** Never create components manually. Always use the Nx generator first.

---

## Objective

Create a reusable ErrorBoundary component that catches JavaScript errors in child components and displays a fallback UI.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-001-T01 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/react-ui/src/lib/components/
- Goal: Catch render errors, display fallback, enable recovery
- React: Must use class component (error boundaries require lifecycle methods)

INSTRUCTIONS:
1. Create ErrorBoundary class component:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

export interface ErrorBoundaryProps {
  /** Children to wrap */
  children: ReactNode;
  /** Custom fallback component */
  fallback?: ReactNode | ((props: FallbackProps) => ReactNode);
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Callback when reset is triggered */
  onReset?: () => void;
  /** Key to reset error boundary when changed */
  resetKeys?: unknown[];
  /** Level for nested boundaries */
  level?: 'app' | 'section' | 'component';
}

export interface FallbackProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  resetErrorBoundary: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, State> {
  static defaultProps = {
    level: 'component',
  };

  state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });

    // Log error for debugging
    console.error('ErrorBoundary caught error:', {
      error,
      componentStack: errorInfo.componentStack,
      level: this.props.level,
    });

    // Call optional error callback
    this.props.onError?.(error, errorInfo);

    // Report to error tracking service
    this.reportError(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    // Reset if resetKeys changed
    if (this.state.hasError && this.props.resetKeys) {
      const hasResetKeyChanged = this.props.resetKeys.some(
        (key, index) => key !== prevProps.resetKeys?.[index]
      );
      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  resetErrorBoundary = () => {
    this.props.onReset?.();
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  reportError(error: Error, errorInfo: ErrorInfo) {
    // TODO: Integrate with error tracking service (Sentry, etc.)
    // For now, log to console in a structured format
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking
    }
  }

  render() {
    if (this.state.hasError) {
      const fallbackProps: FallbackProps = {
        error: this.state.error!,
        errorInfo: this.state.errorInfo,
        resetErrorBoundary: this.resetErrorBoundary,
      };

      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(fallbackProps);
      }

      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback
      return <DefaultErrorFallback {...fallbackProps} />;
    }

    return this.props.children;
  }
}
```

2. Create types file:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/types.ts
export interface ErrorBoundaryProps { /* ... */ }
export interface FallbackProps { /* ... */ }
```

3. Export from index:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/index.ts
export { ErrorBoundary } from './ErrorBoundary';
export type { ErrorBoundaryProps, FallbackProps } from './types';
```

OUTPUT:
- ErrorBoundary class component created
- Types exported
- Basic fallback included
- Error logging integrated
```

---

## Checklist

- [ ] ErrorBoundary class component created
- [ ] getDerivedStateFromError implemented
- [ ] componentDidCatch implemented
- [ ] Reset functionality working
- [ ] Error callback support
- [ ] Types exported

---

## Component Checklist (DoD)

Before marking this task complete, verify all items from `docs/shared/component-library.md#10-component-checklist`:

- [ ] Created with Nx generator (see command above)
- [ ] TypeScript interfaces defined
- [ ] MUI sx props used (no styled-components)
- [ ] Unit tests written and passing
- [ ] **Storybook stories** for all variants (see Task 05)
- [ ] Error state implemented (inherent to component)
- [ ] Accessibility audit passed (role="alert")
- [ ] data-testid attributes added
- [ ] Documentation written
- [ ] Code review completed
