# Task 03: Fix Alert-to-Incident Linking

**Task ID:** NEXUS-NAV-005-T03
**Story:** NEXUS-NAV-005
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Add proper linking between alerts and their parent incidents to provide context and navigation continuity.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-005-T03 for the Nexus UI Uplift project.

CONTEXT:
- Console: apps/threat-management/
- Issue: Alert detail pages don't link to parent incident
- Goal: Bidirectional linking between alerts and incidents

INSTRUCTIONS:
1. Update alert detail page with incident context:

```tsx
// apps/threat-management/src/pages/AlertDetail/AlertDetail.tsx

function AlertDetail({ alertId }: { alertId: string }) {
  const { alert, parentIncident } = useAlertData(alertId);

  return (
    <div className="alert-detail">
      {/* Contextual back navigation */}
      <BackButton to="/threats/alerts" label="Alerts" />

      {/* Parent Incident Context - FIXES DEAD-END */}
      {parentIncident && (
        <ParentIncidentCard incident={parentIncident}>
          <Link to={`/threats/incidents/${parentIncident.id}`}>
            View Incident: {parentIncident.title}
          </Link>
        </ParentIncidentCard>
      )}

      {/* Alert content */}
      <AlertHeader alert={alert} />
      <AlertDetails alert={alert} />

      {/* Related Navigation */}
      <RelatedNavigation>
        {parentIncident && (
          <NavCard
            to={`/threats/incidents/${parentIncident.id}`}
            title="Parent Incident"
            subtitle={parentIncident.title}
            icon={<IncidentIcon />}
          />
        )}
        {alert.relatedAlerts?.map((related) => (
          <NavCard
            key={related.id}
            to={`/threats/alerts/${related.id}`}
            title="Related Alert"
            subtitle={related.title}
            icon={<AlertIcon />}
          />
        ))}
      </RelatedNavigation>
    </div>
  );
}
```

2. Create ParentIncidentCard component:

```tsx
// apps/threat-management/src/components/ParentIncidentCard/ParentIncidentCard.tsx

interface ParentIncidentCardProps {
  incident: {
    id: string;
    title: string;
    status: string;
    severity: string;
  };
}

export function ParentIncidentCard({ incident }: ParentIncidentCardProps) {
  return (
    <div className="parent-incident-card">
      <div className="card-header">
        <span className="label">Part of Incident</span>
        <StatusBadge status={incident.status} />
        <SeverityBadge severity={incident.severity} />
      </div>
      <Link
        to={`/threats/incidents/${incident.id}`}
        className="incident-link"
      >
        <span className="incident-title">{incident.title}</span>
        <ChevronRightIcon className="h-4 w-4" />
      </Link>
    </div>
  );
}
```

3. Create RelatedNavigation component:

```tsx
// libs/shared/react-ui/src/lib/components/RelatedNavigation/RelatedNavigation.tsx

interface NavCardProps {
  to: string;
  title: string;
  subtitle?: string;
  icon?: ReactNode;
}

export function NavCard({ to, title, subtitle, icon }: NavCardProps) {
  return (
    <Link to={to} className="nav-card">
      {icon && <div className="nav-card-icon">{icon}</div>}
      <div className="nav-card-content">
        <span className="nav-card-title">{title}</span>
        {subtitle && <span className="nav-card-subtitle">{subtitle}</span>}
      </div>
      <ChevronRightIcon className="h-4 w-4" />
    </Link>
  );
}

export function RelatedNavigation({ children }: { children: ReactNode }) {
  if (!children || Children.count(children) === 0) return null;

  return (
    <section className="related-navigation">
      <h3>Related</h3>
      <div className="nav-card-grid">{children}</div>
    </section>
  );
}
```

4. Ensure alert data includes parent incident:

```typescript
// Update API query or data fetching hook
function useAlertData(alertId: string) {
  return useQuery(['alert', alertId], async () => {
    const alert = await api.getAlert(alertId);
    const parentIncident = alert.incidentId
      ? await api.getIncident(alert.incidentId)
      : null;
    return { alert, parentIncident };
  });
}
```

OUTPUT:
- Alert detail shows parent incident context
- ParentIncidentCard component created
- RelatedNavigation component created
- Bidirectional linking established
```

---

## Checklist

- [ ] Alert detail shows parent incident
- [ ] ParentIncidentCard component created
- [ ] RelatedNavigation component created
- [ ] Data fetching includes parent incident
- [ ] Styling matches design system
- [ ] Tested with and without parent incident

---

## Navigation Flow

```
Alerts List
    ↓
Alert Detail ←────────────────┐
    │                         │
    └→ Parent Incident ───────┘
           (if applicable)
```
