# Task 03: Add Unit Tests for Route Uniqueness

**Task ID:** NEXUS-NAV-001-T03
**Story:** NEXUS-NAV-001
**Estimate:** 15 minutes
**Type:** Testing

---

## Objective

Add unit tests that ensure no duplicate route paths exist in the router configuration. This prevents future regressions.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-001-T03 for the Nexus UI Uplift project.

CONTEXT:
- Router: apps/infrastructure-console/src/router.tsx
- Test location: apps/infrastructure-console/src/__tests__/router.test.tsx
- Goal: Prevent duplicate routes via automated testing

INSTRUCTIONS:
1. Create or update the router test file
2. Import the routes configuration from router.tsx
3. Implement tests for:
   - No duplicate path strings
   - All required routes are defined
   - Route hierarchy is valid

TEST REQUIREMENTS:
```typescript
import { routes } from '../router';

describe('infrastructure-console router', () => {
  it('should have no duplicate route paths', () => {
    const extractPaths = (routes: RouteObject[], prefix = ''): string[] => {
      return routes.flatMap(route => {
        const fullPath = `${prefix}/${route.path || ''}`.replace(/\/+/g, '/');
        const childPaths = route.children
          ? extractPaths(route.children, fullPath)
          : [];
        return route.path ? [fullPath, ...childPaths] : childPaths;
      });
    };

    const paths = extractPaths(routes);
    const unique = new Set(paths);
    expect(paths.length).toBe(unique.size);
  });

  it('should define all required infrastructure routes', () => {
    const pathExists = (path: string) => {
      // Implementation to check route exists
    };

    expect(pathExists('/infrastructure')).toBe(true);
    expect(pathExists('/infrastructure/assets')).toBe(true);
    expect(pathExists('/infrastructure/assets/:id')).toBe(true);
  });
});
```

4. Run tests: `npm run test -- --testPathPattern=router`
5. Verify all tests pass

OUTPUT:
- New/updated test file
- Test execution results (all green)
```

---

## Checklist

- [ ] Test file created/updated
- [ ] Duplicate path detection test added
- [ ] Required routes test added
- [ ] All tests passing
- [ ] Coverage report generated

---

## Test Execution

```bash
cd apps/infrastructure-console
npm run test -- --testPathPattern=router --coverage
```
