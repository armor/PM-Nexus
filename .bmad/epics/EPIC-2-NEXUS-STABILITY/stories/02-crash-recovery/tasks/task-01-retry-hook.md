# Task 01: Create useRetry Hook with Exponential Backoff

**Task ID:** NEXUS-STAB-002-T01
**Story:** NEXUS-STAB-002
**Estimate:** 45 minutes
**Type:** Implementation

---

## Objective

Create a hook that enables automatic retry of failed operations with configurable exponential backoff.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-002-T01 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/react-ui/src/lib/hooks/
- Goal: Retry failed operations with backoff
- Use cases: API calls, component rendering, async operations

INSTRUCTIONS:
1. Create useRetry hook:

```typescript
// libs/shared/react-ui/src/lib/hooks/useRetry.ts
import { useState, useCallback, useRef, useEffect } from 'react';

interface RetryConfig {
  /** Maximum number of retry attempts */
  maxAttempts?: number;
  /** Base delay in milliseconds */
  baseDelay?: number;
  /** Maximum delay in milliseconds */
  maxDelay?: number;
  /** Multiplier for exponential backoff */
  backoffMultiplier?: number;
  /** Whether to retry automatically */
  autoRetry?: boolean;
  /** Callback on each retry attempt */
  onRetry?: (attempt: number, error: Error) => void;
  /** Callback when all retries exhausted */
  onExhausted?: (error: Error) => void;
}

interface RetryState {
  attempt: number;
  isRetrying: boolean;
  lastError: Error | null;
  nextRetryAt: number | null;
}

export function useRetry<T>(
  operation: () => Promise<T>,
  config: RetryConfig = {}
) {
  const {
    maxAttempts = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    autoRetry = false,
    onRetry,
    onExhausted,
  } = config;

  const [state, setState] = useState<RetryState>({
    attempt: 0,
    isRetrying: false,
    lastError: null,
    nextRetryAt: null,
  });

  const [result, setResult] = useState<T | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Calculate delay for current attempt
  const calculateDelay = useCallback(
    (attempt: number) => {
      const delay = baseDelay * Math.pow(backoffMultiplier, attempt - 1);
      // Add jitter (±10%)
      const jitter = delay * 0.1 * (Math.random() * 2 - 1);
      return Math.min(delay + jitter, maxDelay);
    },
    [baseDelay, backoffMultiplier, maxDelay]
  );

  // Execute operation with retry logic
  const execute = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      isRetrying: true,
      attempt: prev.attempt + 1,
    }));

    try {
      const data = await operation();
      if (mountedRef.current) {
        setResult(data);
        setState({
          attempt: 0,
          isRetrying: false,
          lastError: null,
          nextRetryAt: null,
        });
      }
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));

      if (mountedRef.current) {
        setState((prev) => {
          const newAttempt = prev.attempt;
          const hasMoreAttempts = newAttempt < maxAttempts;

          if (hasMoreAttempts && autoRetry) {
            const delay = calculateDelay(newAttempt);
            const nextRetryAt = Date.now() + delay;

            // Schedule retry
            timeoutRef.current = setTimeout(() => {
              if (mountedRef.current) {
                execute();
              }
            }, delay);

            return {
              ...prev,
              isRetrying: false,
              lastError: err,
              nextRetryAt,
            };
          }

          if (!hasMoreAttempts) {
            onExhausted?.(err);
          }

          return {
            ...prev,
            isRetrying: false,
            lastError: err,
            nextRetryAt: null,
          };
        });

        onRetry?.(state.attempt, err);
      }
      throw err;
    }
  }, [operation, maxAttempts, autoRetry, calculateDelay, onRetry, onExhausted]);

  // Manual retry trigger
  const retry = useCallback(() => {
    if (state.attempt < maxAttempts) {
      execute();
    }
  }, [execute, state.attempt, maxAttempts]);

  // Reset state
  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setState({
      attempt: 0,
      isRetrying: false,
      lastError: null,
      nextRetryAt: null,
    });
    setResult(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    execute,
    retry,
    reset,
    result,
    ...state,
    canRetry: state.attempt < maxAttempts,
    attemptsRemaining: maxAttempts - state.attempt,
  };
}
```

OUTPUT:
- useRetry hook created
- Exponential backoff implemented
- Auto-retry option
- Manual retry support
- Cleanup on unmount
```

---

## Checklist

- [ ] useRetry hook created
- [ ] Exponential backoff working
- [ ] Jitter added to prevent thundering herd
- [ ] Auto-retry option
- [ ] Manual retry trigger
- [ ] Cleanup on unmount
- [ ] Unit tests added
