# Task 02: Create ErrorFallback UI Component

**Task ID:** NEXUS-STAB-001-T02
**Story:** NEXUS-STAB-001
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Create an ErrorFallback component that displays a user-friendly error message with retry and report options, following the design system.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-001-T02 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/react-ui/src/lib/components/ErrorBoundary/
- Goal: User-friendly fallback UI with actions
- Design: Match design system error patterns

INSTRUCTIONS:
1. Create ErrorFallback component:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/ErrorFallback.tsx
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Button } from '../Button';
import { FallbackProps } from './types';

interface ErrorFallbackProps extends FallbackProps {
  /** Title to display */
  title?: string;
  /** Description to display */
  description?: string;
  /** Show error details (dev only) */
  showDetails?: boolean;
  /** Additional actions */
  actions?: React.ReactNode;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

export function ErrorFallback({
  error,
  errorInfo,
  resetErrorBoundary,
  title = 'Something went wrong',
  description = 'An unexpected error occurred. Please try again.',
  showDetails = process.env.NODE_ENV === 'development',
  actions,
  size = 'md',
}: ErrorFallbackProps) {
  const handleReport = () => {
    // Open support dialog or email
    const subject = encodeURIComponent(`Error Report: ${error.message}`);
    const body = encodeURIComponent(
      `Error: ${error.message}\n\nStack: ${error.stack}\n\nComponent Stack: ${errorInfo?.componentStack}`
    );
    window.open(`mailto:support@armor.com?subject=${subject}&body=${body}`);
  };

  return (
    <div
      className={cn(
        'error-fallback',
        'flex flex-col items-center justify-center',
        'bg-surface-secondary rounded-lg border border-error-subtle',
        'text-center',
        {
          'p-4 gap-3': size === 'sm',
          'p-8 gap-4': size === 'md',
          'p-12 gap-6': size === 'lg',
        }
      )}
      role="alert"
      aria-live="assertive"
    >
      {/* Icon */}
      <div
        className={cn(
          'rounded-full bg-error-subtle flex items-center justify-center',
          {
            'p-2': size === 'sm',
            'p-3': size === 'md',
            'p-4': size === 'lg',
          }
        )}
      >
        <ExclamationTriangleIcon
          className={cn('text-error', {
            'h-5 w-5': size === 'sm',
            'h-8 w-8': size === 'md',
            'h-12 w-12': size === 'lg',
          })}
        />
      </div>

      {/* Content */}
      <div className="space-y-2">
        <h3
          className={cn('font-semibold text-primary', {
            'text-sm': size === 'sm',
            'text-lg': size === 'md',
            'text-xl': size === 'lg',
          })}
        >
          {title}
        </h3>
        <p
          className={cn('text-secondary', {
            'text-xs': size === 'sm',
            'text-sm': size === 'md',
            'text-base': size === 'lg',
          })}
        >
          {description}
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          onClick={resetErrorBoundary}
          variant="primary"
          size={size === 'lg' ? 'md' : 'sm'}
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Try Again
        </Button>
        <Button
          onClick={handleReport}
          variant="secondary"
          size={size === 'lg' ? 'md' : 'sm'}
        >
          Report Issue
        </Button>
        {actions}
      </div>

      {/* Error Details (dev only) */}
      {showDetails && (
        <details className="mt-4 w-full text-left">
          <summary className="cursor-pointer text-xs text-secondary hover:text-primary">
            Error Details
          </summary>
          <pre className="mt-2 p-3 bg-surface-tertiary rounded text-xs overflow-auto max-h-48">
            <code>
              {error.message}
              {'\n\n'}
              {error.stack}
              {errorInfo?.componentStack && (
                <>
                  {'\n\nComponent Stack:'}
                  {errorInfo.componentStack}
                </>
              )}
            </code>
          </pre>
        </details>
      )}
    </div>
  );
}
```

2. Create size variants for different boundary levels:

```typescript
// App-level fallback (full page)
export function AppErrorFallback(props: FallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <ErrorFallback
        {...props}
        size="lg"
        title="Application Error"
        description="The application encountered an error. Please refresh the page or contact support."
        actions={
          <Button onClick={() => window.location.reload()} variant="ghost">
            Refresh Page
          </Button>
        }
      />
    </div>
  );
}

// Section-level fallback (card-sized)
export function SectionErrorFallback(props: FallbackProps) {
  return (
    <ErrorFallback
      {...props}
      size="md"
      title="Section Error"
      description="This section encountered an error. Other parts of the page are still available."
    />
  );
}

// Component-level fallback (inline)
export function ComponentErrorFallback(props: FallbackProps) {
  return (
    <ErrorFallback
      {...props}
      size="sm"
      title="Error"
      description="Unable to load this component."
    />
  );
}
```

OUTPUT:
- ErrorFallback component created
- Size variants for app/section/component levels
- Retry and report actions
- Dev-only error details
- Accessible and styled
```

---

## Checklist

- [ ] ErrorFallback component created
- [ ] Three size variants (sm/md/lg)
- [ ] Retry button working
- [ ] Report button working
- [ ] Error details toggle (dev only)
- [ ] Accessibility attributes added
- [ ] Design system tokens used
