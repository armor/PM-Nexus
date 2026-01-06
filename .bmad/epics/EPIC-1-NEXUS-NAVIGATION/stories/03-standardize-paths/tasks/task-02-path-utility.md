# Task 02: Create Path Standardization Utility

**Task ID:** NEXUS-NAV-003-T02
**Story:** NEXUS-NAV-003
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Create a shared utility that helps construct consistent absolute paths for navigation, reducing errors and enforcing the standard.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-003-T02 for the Nexus UI Uplift project.

CONTEXT:
- Library: libs/shared/utils/
- Goal: Type-safe path construction utilities
- Pattern: Absolute paths always

INSTRUCTIONS:
1. Create path construction utilities:

```typescript
// libs/shared/utils/src/lib/navigation/paths.ts

/**
 * Base paths for all console applications
 */
export const CONSOLE_PATHS = {
  infrastructure: '/infrastructure',
  threats: '/threats',
  compliance: '/compliance',
  identity: '/identity',
  cloud: '/cloud',
  endpoint: '/endpoint',
  network: '/network',
  reporting: '/reporting',
  admin: '/admin',
} as const;

/**
 * Constructs an absolute path, ensuring leading slash
 * and proper segment joining
 */
export function buildPath(...segments: (string | number | undefined)[]): string {
  const filtered = segments.filter(Boolean);
  const path = filtered.join('/');
  return path.startsWith('/') ? path : `/${path}`;
}

/**
 * Type-safe path builders for common navigation patterns
 */
export const paths = {
  infrastructure: {
    root: () => CONSOLE_PATHS.infrastructure,
    assets: () => buildPath(CONSOLE_PATHS.infrastructure, 'assets'),
    asset: (id: string) => buildPath(CONSOLE_PATHS.infrastructure, 'assets', id),
    assetDetails: (id: string) => buildPath(CONSOLE_PATHS.infrastructure, 'assets', id, 'details'),
  },
  threats: {
    root: () => CONSOLE_PATHS.threats,
    incidents: () => buildPath(CONSOLE_PATHS.threats, 'incidents'),
    incident: (id: string) => buildPath(CONSOLE_PATHS.threats, 'incidents', id),
  },
  // ... other consoles
} as const;

/**
 * Hook for type-safe navigation
 */
export function useTypedNavigate() {
  const navigate = useNavigate();

  return {
    toAsset: (id: string) => navigate(paths.infrastructure.asset(id)),
    toIncident: (id: string) => navigate(paths.threats.incident(id)),
    // ... other typed navigations
  };
}
```

2. Add validation helper:

```typescript
/**
 * Validates that a path is absolute (starts with /)
 * Throws in development, logs warning in production
 */
export function assertAbsolutePath(path: string, context?: string): void {
  if (!path.startsWith('/')) {
    const message = `Relative path detected: "${path}"${context ? ` in ${context}` : ''}`;
    if (process.env.NODE_ENV === 'development') {
      throw new Error(message);
    }
    console.warn(message);
  }
}
```

3. Export from library index

4. Add unit tests

OUTPUT:
- Path utility module created
- Type definitions exported
- Unit tests passing
```

---

## Checklist

- [ ] buildPath utility created
- [ ] CONSOLE_PATHS constants defined
- [ ] Type-safe paths object created
- [ ] assertAbsolutePath validation added
- [ ] Exported from library
- [ ] Unit tests added
- [ ] Documentation added

---

## Usage Example

```typescript
// Before (bad)
<Link to={`./assets/${id}/details`}>Details</Link>

// After (good)
import { paths } from '@armor/utils';
<Link to={paths.infrastructure.assetDetails(id)}>Details</Link>
```
