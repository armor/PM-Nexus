# Task 04: Wrap All 9 Console Apps with Error Boundaries

**Task ID:** NEXUS-STAB-001-T04
**Story:** NEXUS-STAB-001
**Estimate:** 2 hours
**Type:** Implementation

---

## Objective

Add error boundaries to all 9 console applications at the app, section, and critical component levels.

---

## AI Implementation Prompt

```
You are implementing NEXUS-STAB-001-T04 for the Nexus UI Uplift project.

CONTEXT:
- Component: ErrorBoundary from libs/shared/react-ui
- Target: All 9 console apps
- Strategy: Three-level error boundary hierarchy

BOUNDARY HIERARCHY:
```
App Level (catches everything, shows full-page error)
└── Layout Level (catches layout errors)
    └── Section Level (header, sidebar, main content separate)
        └── Component Level (critical widgets isolated)
```

INSTRUCTIONS:
1. Add app-level boundary in each console's entry:

```tsx
// apps/infrastructure-console/src/main.tsx
import { ErrorBoundary, AppErrorFallback } from '@armor/react-ui';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary
      level="app"
      fallback={(props) => <AppErrorFallback {...props} />}
      onError={(error, info) => {
        // Log to error tracking
        console.error('App-level error:', error);
      }}
    >
      <App />
    </ErrorBoundary>
  </StrictMode>
);
```

2. Add section-level boundaries in layout:

```tsx
// apps/infrastructure-console/src/layouts/AppLayout.tsx
import { ErrorBoundary, SectionErrorFallback } from '@armor/react-ui';

function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-layout">
      {/* Header is isolated */}
      <ErrorBoundary level="section" fallback={<SectionErrorFallback />}>
        <Header />
      </ErrorBoundary>

      <div className="app-body">
        {/* Sidebar is isolated */}
        <ErrorBoundary level="section" fallback={<SectionErrorFallback />}>
          <Sidebar />
        </ErrorBoundary>

        {/* Main content is isolated */}
        <main className="main-content">
          <ErrorBoundary level="section" fallback={<SectionErrorFallback />}>
            {children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
```

3. Add component-level boundaries for critical widgets:

```tsx
// Example: Dashboard with isolated widgets
function Dashboard() {
  return (
    <div className="dashboard-grid">
      <ErrorBoundary level="component">
        <MetricsWidget />
      </ErrorBoundary>

      <ErrorBoundary level="component">
        <AlertsWidget />
      </ErrorBoundary>

      <ErrorBoundary level="component">
        <IncidentsWidget />
      </ErrorBoundary>

      <ErrorBoundary level="component">
        <ComplianceWidget />
      </ErrorBoundary>
    </div>
  );
}
```

4. Apply to all 9 consoles:
   - infrastructure-console
   - threat-management
   - compliance-console
   - identity-console
   - cloud-console
   - endpoint-console
   - network-console
   - reporting-console
   - admin-console

5. For each console:
   - Add app-level boundary in main.tsx
   - Add section boundaries in layout
   - Identify and wrap critical widgets

OUTPUT:
- All console apps have app-level boundary
- All layouts have section boundaries
- Critical widgets isolated
- Error propagation tested
```

---

## Checklist by Console

### infrastructure-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### threat-management
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### compliance-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### identity-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### cloud-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### endpoint-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### network-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### reporting-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

### admin-console
- [ ] App-level boundary added
- [ ] Layout sections wrapped
- [ ] Dashboard widgets wrapped

---

## Verification

For each console, verify:
1. Throw error in a widget → only widget shows error
2. Throw error in main content → only main shows error
3. Throw error in sidebar → only sidebar shows error
4. Reset works from each fallback
