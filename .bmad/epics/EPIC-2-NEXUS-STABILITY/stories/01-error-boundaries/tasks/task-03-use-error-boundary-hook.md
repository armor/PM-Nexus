# Task 03: Create useErrorBoundary Hook

**Task ID:** NEXUS-STAB-001-T03
**Story:** NEXUS-STAB-001
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Create a hook that allows programmatic control of error boundaries, including throwing errors to be caught by the nearest boundary.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-001-T03 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/react-ui/src/lib/components/ErrorBoundary/
- Goal: Programmatic error handling for async operations
- Use case: Catch async errors and propagate to boundary

INSTRUCTIONS:
1. Create useErrorBoundary hook:

```typescript
// libs/shared/react-ui/src/lib/components/ErrorBoundary/useErrorBoundary.ts
import { useState, useCallback, useContext, createContext } from 'react';

// Context for error boundary state
interface ErrorBoundaryContextValue {
  showBoundary: (error: Error) => void;
  resetBoundary: () => void;
}

export const ErrorBoundaryContext = createContext<ErrorBoundaryContextValue | null>(null);

/**
 * Hook to programmatically trigger error boundary
 * Use this to catch async errors and display them via ErrorBoundary
 */
export function useErrorBoundary() {
  const context = useContext(ErrorBoundaryContext);
  const [error, setError] = useState<Error | null>(null);

  // Throw error to be caught by error boundary
  const showBoundary = useCallback((error: Error) => {
    if (context) {
      context.showBoundary(error);
    } else {
      // Fallback: trigger re-render with error state
      setError(error);
    }
  }, [context]);

  // Reset the error state
  const resetBoundary = useCallback(() => {
    if (context) {
      context.resetBoundary();
    }
    setError(null);
  }, [context]);

  // If error is set, throw it to be caught by boundary
  if (error) {
    throw error;
  }

  return { showBoundary, resetBoundary };
}

/**
 * Hook for wrapping async operations with error boundary support
 */
export function useAsyncBoundary<T>() {
  const { showBoundary } = useErrorBoundary();
  const [isLoading, setIsLoading] = useState(false);

  const execute = useCallback(
    async (asyncFn: () => Promise<T>): Promise<T | undefined> => {
      setIsLoading(true);
      try {
        const result = await asyncFn();
        return result;
      } catch (error) {
        showBoundary(error instanceof Error ? error : new Error(String(error)));
        return undefined;
      } finally {
        setIsLoading(false);
      }
    },
    [showBoundary]
  );

  return { execute, isLoading };
}

/**
 * Hook for catching and handling errors with fallback
 */
export function useCatchError<T>(fallbackValue: T) {
  const { showBoundary } = useErrorBoundary();

  const catchError = useCallback(
    (fn: () => T): T => {
      try {
        return fn();
      } catch (error) {
        showBoundary(error instanceof Error ? error : new Error(String(error)));
        return fallbackValue;
      }
    },
    [showBoundary, fallbackValue]
  );

  const catchErrorAsync = useCallback(
    async (fn: () => Promise<T>): Promise<T> => {
      try {
        return await fn();
      } catch (error) {
        showBoundary(error instanceof Error ? error : new Error(String(error)));
        return fallbackValue;
      }
    },
    [showBoundary, fallbackValue]
  );

  return { catchError, catchErrorAsync };
}
```

2. Update ErrorBoundary to provide context:

```typescript
// Update ErrorBoundary.tsx
export class ErrorBoundary extends Component<ErrorBoundaryProps, State> {
  // ... existing code ...

  showBoundary = (error: Error) => {
    this.setState({
      hasError: true,
      error,
      errorInfo: null,
    });
  };

  render() {
    const contextValue: ErrorBoundaryContextValue = {
      showBoundary: this.showBoundary,
      resetBoundary: this.resetErrorBoundary,
    };

    if (this.state.hasError) {
      // ... fallback rendering ...
    }

    return (
      <ErrorBoundaryContext.Provider value={contextValue}>
        {this.props.children}
      </ErrorBoundaryContext.Provider>
    );
  }
}
```

3. Export from index:

```typescript
export { useErrorBoundary, useAsyncBoundary, useCatchError } from './useErrorBoundary';
```

OUTPUT:
- useErrorBoundary hook created
- useAsyncBoundary hook for async operations
- useCatchError hook for try-catch with boundary
- Context provider in ErrorBoundary
```

---

## Checklist

- [ ] useErrorBoundary hook created
- [ ] useAsyncBoundary hook created
- [ ] useCatchError hook created
- [ ] ErrorBoundary provides context
- [ ] Hooks exported
- [ ] Documentation added

---

## Usage Examples

```typescript
// Example 1: Catch async error
function DataLoader() {
  const { showBoundary } = useErrorBoundary();

  useEffect(() => {
    fetchData().catch(error => {
      showBoundary(error);
    });
  }, []);
}

// Example 2: Wrap async operation
function AsyncComponent() {
  const { execute, isLoading } = useAsyncBoundary<Data>();

  const handleClick = () => {
    execute(async () => {
      const data = await riskyAsyncOperation();
      return data;
    });
  };
}

// Example 3: Catch with fallback
function RiskyComponent() {
  const { catchError } = useCatchError([]);

  const items = catchError(() => parseRiskyData(rawData));
}
```
