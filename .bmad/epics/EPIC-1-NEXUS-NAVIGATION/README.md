# EPIC-1: NEXUS-NAVIGATION

**Status:** Ready for Sprint 1
**Priority:** P0 - Critical
**Owner:** NEXUS
**MVP:** MVP 1
**Total Stories:** 5 | **Total Points:** 14

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | NEXUS-NAV |
| Depends On | None |
| Blocks | NEXUS-FLOW, NEXUS-UX-FOUNDATION |

### Story Execution Order

```
NEXUS-NAV-001 (1pt) ─┐
                     ├─> NEXUS-NAV-003 (3pt) ─┐
NEXUS-NAV-002 (5pt) ─┘                        ├─> NEXUS-NAV-005 (2pt)
                     NEXUS-NAV-004 (3pt) ─────┘
```

---

## Summary

Fix critical routing issues and implement consistent navigation patterns across all 9 console apps. The platform currently has duplicate routes, missing breadcrumbs, inconsistent path formatting, and navigation dead-ends that trap users.

---

## Business Value

- **Reduce user frustration** - Eliminate navigation dead-ends and confusing routes
- **Improve task completion** - Users can navigate predictably to complete workflows
- **Enable support efficiency** - Consistent URLs make troubleshooting easier
- **Foundation for NEXUS-FLOW** - Required before implementing 2-click navigation

---

## Acceptance Criteria

- [ ] No duplicate routes in any console app router
- [ ] AutoBreadcrumbs component renders on all pages
- [ ] All internal paths use consistent formatting (absolute)
- [ ] Every detail page has a contextual back button
- [ ] No navigation dead-ends (user can always return)
- [ ] E2E tests verify navigation flows

---

## Stories

| ID | Title | Pts | Sprint | Status |
|----|-------|-----|--------|--------|
| NEXUS-NAV-001 | Fix duplicate route in infrastructure-console | 1pt | Sprint 1 | backlog |
| NEXUS-NAV-002 | Implement AutoBreadcrumbs across all 9 console apps | 5pt | Sprint 1 | backlog |
| NEXUS-NAV-003 | Standardize path formatting (relative vs absolute) | 3pt | Sprint 1 | backlog |
| NEXUS-NAV-004 | Add missing back buttons with contextual return | 3pt | Sprint 1 | backlog |
| NEXUS-NAV-005 | Fix navigation dead-ends in threat-management | 2pt | Sprint 1 | backlog |

---

## Technical Context

### Critical Files

- `apps/infrastructure-console/src/router.tsx` (duplicate route lines 76-92)
- `libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/` (exists, unused)
- All console app router files

### Related Diagrams

- [Dashboard Hierarchy](../../docs/diagrams/components/01-dashboard-hierarchy-1.svg)
- [System Architecture](../../docs/diagrams/architecture/01-system-architecture-1.svg)

### Design System References

- [Navigation Patterns](../../docs/shared/design-system.md#10-navigation)
- [Breadcrumbs Component](../../docs/shared/component-library.md)

---

## Confluence Documentation

| Document | Link |
|----------|------|
| **Parent Page** | [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5015044104) |
| Extended PRD | [Technical Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077368833) |
| Architecture | [Architecture Document](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077139460) |
| Design System | [UX Standards](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5076942851) |
| Component Library | [Specification](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5075992637) |

---

## Quality Gates

```
NAVIGATION QUALITY GATE
□ Every page reachable via URL and navigation
□ Breadcrumbs reflect actual path hierarchy
□ Back button preserves previous context
□ No console errors during navigation
□ E2E tests pass for all navigation flows
```

---

*Epic owned by Frontend Team. Last updated: 2026-01-04*
