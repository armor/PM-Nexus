# Task 02: Fix Incident Detail Navigation Gaps

**Task ID:** NEXUS-NAV-005-T02
**Story:** NEXUS-NAV-005
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Add missing navigation elements to incident detail pages to eliminate dead-ends and improve user flow.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-005-T02 for the Nexus UI Uplift project.

CONTEXT:
- Console: apps/threat-management/
- Pages: Incident detail and related pages
- Goal: No dead-ends in incident flow

INSTRUCTIONS:
1. Update incident detail page with related navigation:

```tsx
// apps/threat-management/src/pages/IncidentDetail/IncidentDetail.tsx

function IncidentDetail({ incidentId }: { incidentId: string }) {
  const { incident, relatedAlerts, responses } = useIncidentData(incidentId);

  return (
    <div className="incident-detail">
      {/* Back navigation */}
      <BackButton to="/threats/incidents" label="Incidents" />

      {/* Incident content */}
      <IncidentHeader incident={incident} />
      <IncidentTimeline incident={incident} />

      {/* Related navigation - FIXES DEAD-END */}
      <section className="related-navigation">
        <h2>Related</h2>

        {/* Related Alerts */}
        {relatedAlerts.length > 0 && (
          <RelatedAlertsList
            alerts={relatedAlerts}
            onAlertClick={(alertId) => navigate(`/threats/alerts/${alertId}`)}
          />
        )}

        {/* Response Actions */}
        {responses.length > 0 && (
          <ResponseActionsList
            responses={responses}
            onResponseClick={(responseId) => navigate(`/threats/responses/${responseId}`)}
          />
        )}

        {/* Quick Actions */}
        <QuickActions>
          <Button onClick={() => navigate(`/threats/incidents/${incidentId}/assign`)}>
            Assign Incident
          </Button>
          <Button onClick={() => navigate(`/threats/incidents/${incidentId}/respond`)}>
            Create Response
          </Button>
        </QuickActions>
      </section>
    </div>
  );
}
```

2. Update incident timeline page:

```tsx
// apps/threat-management/src/pages/IncidentTimeline/IncidentTimeline.tsx

function IncidentTimeline({ incidentId }: { incidentId: string }) {
  return (
    <div className="incident-timeline">
      {/* Back to incident detail */}
      <BackButton
        to={`/threats/incidents/${incidentId}`}
        label="Incident Details"
      />

      <Timeline incidentId={incidentId} />

      {/* Forward navigation - FIXES DEAD-END */}
      <footer className="timeline-actions">
        <h3>Next Steps</h3>
        <Button onClick={() => navigate(`/threats/incidents/${incidentId}/respond`)}>
          Create Response Action
        </Button>
        <Button variant="secondary" onClick={() => navigate(`/threats/incidents/${incidentId}`)}>
          Back to Incident
        </Button>
      </footer>
    </div>
  );
}
```

3. Add "where to go next" component for all detail pages:

```tsx
// libs/shared/react-ui/src/lib/components/NextSteps/NextSteps.tsx

interface NextStep {
  label: string;
  description?: string;
  to: string;
  icon?: ReactNode;
  primary?: boolean;
}

interface NextStepsProps {
  title?: string;
  steps: NextStep[];
}

export function NextSteps({ title = 'Next Steps', steps }: NextStepsProps) {
  return (
    <section className="next-steps" aria-labelledby="next-steps-title">
      <h3 id="next-steps-title">{title}</h3>
      <div className="next-steps-grid">
        {steps.map((step) => (
          <Link
            key={step.to}
            to={step.to}
            className={cn('next-step-card', step.primary && 'primary')}
          >
            {step.icon}
            <span className="label">{step.label}</span>
            {step.description && (
              <span className="description">{step.description}</span>
            )}
          </Link>
        ))}
      </div>
    </section>
  );
}
```

OUTPUT:
- Incident detail updated with related navigation
- Incident timeline has forward navigation
- NextSteps component created for reuse
```

---

## Checklist

- [ ] Incident detail has related alerts section
- [ ] Incident detail has response actions section
- [ ] Incident detail has quick actions
- [ ] Incident timeline has next steps
- [ ] NextSteps component created
- [ ] All pages compile cleanly

---

## Navigation Flow

```
Incident List
    ↓
Incident Detail ←→ Related Alerts
    ↓                  ↓
Timeline           Alert Detail
    ↓
Response Actions
```
