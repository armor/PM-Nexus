# Task 02: Implement State Preservation Logic

**Task ID:** NEXUS-NAV-004-T02
**Story:** NEXUS-NAV-004
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Implement logic to preserve list state (filters, pagination, scroll position) when navigating back from detail pages.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-004-T02 for the Nexus UI Uplift project.

CONTEXT:
- Component: BackButton (created in task-01)
- Goal: Preserve list filters and scroll when returning
- Challenge: State lost when navigating to detail page

INSTRUCTIONS:
1. Create navigation state hook:

```typescript
// libs/shared/react-ui/src/lib/hooks/useNavigationState.ts
import { useLocation, useNavigate } from 'react-router-dom';
import { useCallback, useEffect } from 'react';

interface NavigationState {
  /** Scroll position of the source page */
  scrollY?: number;
  /** Any preserved state (filters, pagination, etc.) */
  preservedState?: Record<string, unknown>;
  /** The path we came from */
  fromPath?: string;
}

/**
 * Hook to preserve and restore navigation state
 */
export function useNavigationState() {
  const location = useLocation();
  const navigate = useNavigate();

  // Get state passed from previous navigation
  const navigationState = location.state as NavigationState | undefined;

  /**
   * Navigate while preserving current state for return
   */
  const navigateWithState = useCallback(
    (to: string, stateToPreserve?: Record<string, unknown>) => {
      const state: NavigationState = {
        scrollY: window.scrollY,
        preservedState: stateToPreserve,
        fromPath: location.pathname,
      };
      navigate(to, { state });
    },
    [navigate, location.pathname]
  );

  /**
   * Navigate back and restore state
   */
  const navigateBack = useCallback(
    (fallbackPath: string) => {
      if (navigationState?.fromPath) {
        navigate(navigationState.fromPath, {
          state: navigationState.preservedState,
        });
      } else {
        navigate(fallbackPath);
      }
    },
    [navigate, navigationState]
  );

  // Restore scroll position if available
  useEffect(() => {
    if (navigationState?.scrollY !== undefined) {
      // Small delay to let page render
      requestAnimationFrame(() => {
        window.scrollTo(0, navigationState.scrollY!);
      });
    }
  }, [navigationState?.scrollY]);

  return {
    navigationState,
    navigateWithState,
    navigateBack,
    preservedState: navigationState?.preservedState,
  };
}
```

2. Update BackButton to use state preservation:

```typescript
// Update BackButton.tsx
import { useNavigationState } from '../../hooks/useNavigationState';

export function BackButton({
  to,
  label,
  preserveState = true,
  ...props
}: BackButtonProps) {
  const { navigateBack, navigationState } = useNavigationState();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (preserveState && navigationState?.fromPath) {
      navigateBack(to);
    } else {
      navigate(to);
    }
  };

  // ...
}
```

3. Create wrapper for list navigation:

```typescript
// libs/shared/react-ui/src/lib/hooks/useListNavigation.ts

interface ListState {
  filters?: Record<string, string>;
  page?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export function useListNavigation<T extends ListState>(initialState: T) {
  const { navigateWithState, preservedState } = useNavigationState();
  const [listState, setListState] = useState<T>(
    (preservedState as T) || initialState
  );

  const navigateToDetail = useCallback(
    (detailPath: string) => {
      navigateWithState(detailPath, listState);
    },
    [navigateWithState, listState]
  );

  return {
    listState,
    setListState,
    navigateToDetail,
  };
}
```

OUTPUT:
- useNavigationState hook created
- useListNavigation hook created
- BackButton updated to use state
- Scroll restoration working
```

---

## Checklist

- [ ] useNavigationState hook created
- [ ] useListNavigation hook created
- [ ] BackButton updated
- [ ] Scroll restoration working
- [ ] Filter preservation working
- [ ] Exported from library

---

## Usage Example

```typescript
// In list page
function AssetList() {
  const { listState, setListState, navigateToDetail } = useListNavigation({
    filters: {},
    page: 1,
    sortBy: 'name',
  });

  return (
    <DataTable
      onRowClick={(asset) => navigateToDetail(`/infrastructure/assets/${asset.id}`)}
      {...listState}
      onStateChange={setListState}
    />
  );
}

// In detail page
function AssetDetail() {
  return (
    <PageHeader>
      <BackButton to="/infrastructure/assets" label="Assets" preserveState />
    </PageHeader>
  );
}
```
