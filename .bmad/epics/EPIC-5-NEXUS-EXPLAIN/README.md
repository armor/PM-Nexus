# EPIC-5: NEXUS-EXPLAIN

**Status:** Ready for Sprint 4
**Priority:** P0 - Critical
**Owner:** NEXUS
**MVP:** MVP 1
**Total Stories:** 10 | **Total Points:** 35

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | NEXUS-EXP |
| Depends On | NEXUS-VALUE (success states) |
| Blocks | None |

---

## Summary

Add comprehensive explanations for metrics, charts, and data throughout the platform. Every number, graph, and indicator should explain what it means, why it matters, and what action to take.

---

## Business Value

- **Reduce confusion** - Users understand what they're seeing
- **Drive action** - Clear next steps from every metric
- **Build expertise** - Users learn security concepts
- **Reduce support** - Self-service understanding

---

## Acceptance Criteria

- [ ] Every metric has a tooltip explaining meaning
- [ ] Charts show "Why this matters" explanation
- [ ] Drill-through from summary to detail available
- [ ] Technical terms have glossary definitions
- [ ] Role-appropriate explanations (Analyst vs CISO)

---

## Stories

### Metric Explanations (4 stories, 14pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-EXP-001 | Create metric tooltip system | 3pt | Sprint 4 |
| NEXUS-EXP-002 | Add explanations to all dashboard metrics | 5pt | Sprint 4 |
| NEXUS-EXP-003 | Implement "Why this matters" for trends | 3pt | Sprint 4 |
| NEXUS-EXP-004 | Create role-aware metric descriptions | 3pt | Sprint 4 |

### Chart Explanations (3 stories, 11pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-EXP-005 | Add chart legend with explanations | 3pt | Sprint 5 |
| NEXUS-EXP-006 | Implement drill-through navigation | 5pt | Sprint 5 |
| NEXUS-EXP-007 | Create data point tooltips | 3pt | Sprint 5 |

### Glossary & Help (3 stories, 10pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-EXP-008 | Build security glossary | 5pt | Sprint 5 |
| NEXUS-EXP-009 | Add inline term definitions | 3pt | Sprint 5 |
| NEXUS-EXP-010 | Create contextual help system | 2pt | Sprint 5 |

---

## Technical Context

### Critical Files

| Component | Location | Status |
|-----------|----------|--------|
| MetricTooltip | `libs/shared/react-ui/src/lib/components/MetricTooltip/` | **CREATE** |
| ChartExplainer | `libs/shared/react-ui/src/lib/components/ChartExplainer/` | **CREATE** |
| SecurityGlossary | `libs/shared/data/src/lib/glossary.json` | **CREATE** |

### Nx Generator Commands

```bash
# MetricTooltip component
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=MetricTooltip --directory=components/MetricTooltip

# ChartExplainer component
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=ChartExplainer --directory=components/ChartExplainer
```

### Storybook Requirements

**MetricTooltip stories MUST include:**
- Default variant
- All role variants (Analyst, Manager, CISO, Executive)
- Different metric types (score, count, percentage, trend)
- With/without drill-through link

**ChartExplainer stories MUST include:**
- Bar chart explanation
- Line chart explanation
- Pie chart explanation
- Interactive drill-through

### MSW Handlers

Components that fetch metric explanations need handlers:
```typescript
http.get('/api/v1/metrics/:id/explanation', ({ params }) =>
  HttpResponse.json({ explanation: mockExplanations[params.id] })
)
```

### Design System References

- [Tooltip Patterns](../../../docs/shared/design-system.md#tooltips)
- [Data Visualization](../../../docs/shared/component-library.md#charts)

---

## Confluence Documentation

| Document | Link |
|----------|------|
| **Parent Page** | [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5015044104) |
| Extended PRD | [Technical Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077368833) |
| Design System | [UX Standards](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5076942851) |
| Component Library | [Specification](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5075992637) |

---

## Quality Gates

```
EXPLANATION QUALITY GATE
□ Every metric has explanation
□ Explanations are role-appropriate
□ Drill-through works from all summaries
□ Glossary covers all technical terms
□ Help is contextually relevant
```

---

*Epic owned by Product Team. Last updated: 2026-01-04*
