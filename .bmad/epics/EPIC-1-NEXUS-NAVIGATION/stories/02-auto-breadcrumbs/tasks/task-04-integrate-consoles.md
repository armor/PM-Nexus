# Task 04: Integrate AutoBreadcrumbs into All 9 Console Layouts

**Task ID:** NEXUS-NAV-002-T04
**Story:** NEXUS-NAV-002
**Estimate:** 2 hours
**Type:** Implementation

---

## Objective

Add the enhanced AutoBreadcrumbs component to the layout of all 9 console applications.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-002-T04 for the Nexus UI Uplift project.

CONTEXT:
- Component: AutoBreadcrumbs from libs/shared/react-ui
- Target: All 9 console app layouts
- Goal: Consistent breadcrumb navigation across platform

CONSOLE APPS TO UPDATE:
1. apps/infrastructure-console/src/layouts/
2. apps/threat-management/src/layouts/
3. apps/compliance-console/src/layouts/
4. apps/identity-console/src/layouts/
5. apps/cloud-console/src/layouts/
6. apps/endpoint-console/src/layouts/
7. apps/network-console/src/layouts/
8. apps/reporting-console/src/layouts/
9. apps/admin-console/src/layouts/

INSTRUCTIONS:
1. For each console app:
   a. Identify the main layout component (usually AppLayout, MainLayout, or similar)
   b. Import AutoBreadcrumbs from shared library
   c. Add to layout below header, above main content

2. Standard placement pattern:

```tsx
import { AutoBreadcrumbs } from '@armor/react-ui';

function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-layout">
      <Header />
      <Sidebar />
      <main className="main-content">
        <AutoBreadcrumbs
          customLabels={{
            // Console-specific label overrides
            'infrastructure': 'Infrastructure',
            'assets': 'Assets',
          }}
        />
        {children}
      </main>
    </div>
  );
}
```

3. Configure console-specific labels:
   - Each console may need custom labels for its routes
   - Dynamic params should show meaningful names (not UUIDs)

4. Handle console-specific edge cases:
   - Dashboard pages may hide breadcrumbs (top level)
   - Modal/dialog routes shouldn't affect breadcrumbs
   - External links should be excluded

CONSTRAINTS:
- Do NOT modify component behavior (only integrate)
- Consistent placement across all apps
- Match existing layout patterns

OUTPUT:
For each console:
- Modified layout component
- Custom labels configuration
- Verification screenshot
```

---

## Console Checklist

- [ ] infrastructure-console integrated
- [ ] threat-management integrated
- [ ] compliance-console integrated
- [ ] identity-console integrated
- [ ] cloud-console integrated
- [ ] endpoint-console integrated
- [ ] network-console integrated
- [ ] reporting-console integrated
- [ ] admin-console integrated

---

## Custom Labels by Console

| Console | Route | Custom Label |
|---------|-------|--------------|
| infrastructure | /assets | Assets |
| infrastructure | /assets/:id | {asset.name} |
| threat-management | /incidents | Incidents |
| threat-management | /incidents/:id | INC-{id} |
| compliance | /frameworks | Frameworks |
| compliance | /frameworks/:id | {framework.name} |
| ... | ... | ... |

---

## Verification

After each integration:
1. Navigate to deepest route in console
2. Verify breadcrumbs show correct hierarchy
3. Click each breadcrumb segment
4. Verify navigation works
5. Check mobile truncation
