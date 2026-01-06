# EPIC-4: NEXUS-ONBOARD

**Status:** Ready for Sprint 3
**Priority:** P0 - Critical
**Owner:** NEXUS
**MVP:** MVP 1
**Total Stories:** 10 | **Total Points:** 21

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | NEXUS-ONB |
| Depends On | NEXUS-NAV |
| Blocks | None |

---

## Summary

Implement a comprehensive onboarding experience that gets users to value within 5 minutes. Include a product tour, contextual tips, and guided setup for new users and new features.

---

## Business Value

- **Accelerate adoption** - Users see value in first session
- **Reduce churn** - Confused users don't leave
- **Lower support costs** - Self-service onboarding
- **Drive feature discovery** - Highlight key capabilities

---

## Acceptance Criteria

- [ ] First-time users complete guided tour
- [ ] Time to first value < 5 minutes
- [ ] Contextual tips appear on new features
- [ ] Progress tracked and resumable
- [ ] Skip option for experienced users

---

## Stories

### Product Tour (4 stories, 10pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-ONB-001 | Create product tour framework | 3pt | Sprint 3 |
| NEXUS-ONB-002 | Build welcome and overview tour | 2pt | Sprint 3 |
| NEXUS-ONB-003 | Implement feature spotlight tours | 3pt | Sprint 3 |
| NEXUS-ONB-004 | Add tour progress persistence | 2pt | Sprint 3 |

### Contextual Help (3 stories, 6pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-ONB-005 | Create tooltip hint system | 2pt | Sprint 3 |
| NEXUS-ONB-006 | Implement "What's New" announcements | 2pt | Sprint 3 |
| NEXUS-ONB-007 | Add help drawer with contextual content | 2pt | Sprint 3 |

### User Setup (3 stories, 5pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-ONB-008 | Create user preferences wizard | 2pt | Sprint 4 |
| NEXUS-ONB-009 | Build dashboard customization guide | 2pt | Sprint 4 |
| NEXUS-ONB-010 | Implement role-based onboarding paths | 1pt | Sprint 4 |

---

## Technical Context

### Critical Files

| Component | Location | Status |
|-----------|----------|--------|
| Tour | `libs/shared/react-ui/src/lib/components/Tour/` | **CREATE** |
| TourStep | `libs/shared/react-ui/src/lib/components/Tour/TourStep.tsx` | **CREATE** |
| Hint | `libs/shared/react-ui/src/lib/components/Tooltip/Hint.tsx` | **CREATE** |
| WhatsNew | `libs/shared/react-ui/src/lib/components/WhatsNew/` | **CREATE** |

### Nx Generator Commands

```bash
# Tour framework components
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=Tour --directory=components/Tour
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=TourStep --directory=components/Tour

# Hint tooltip component
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=Hint --directory=components/Tooltip

# What's New announcements
nx g @platform/armor-nx-plugin:react-component --project=shared-react-ui --name=WhatsNew --directory=components/WhatsNew
```

### Storybook Requirements

**Tour stories MUST include:**
- Default tour flow
- Single step spotlight
- Multi-step sequence
- With/without progress indicator
- Skip functionality
- Keyboard navigation

**Accessibility Requirements:**
- Focus management during tour
- Screen reader announcements
- Keyboard-only navigation
- Escape to close

### Design System References

- [Onboarding Patterns](../../../docs/shared/design-system.md#onboarding)

---

## Confluence Documentation

| Document | Link |
|----------|------|
| **Parent Page** | [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5015044104) |
| Extended PRD | [Technical Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077368833) |
| Design System | [UX Standards](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5076942851) |
| GTM Strategy | [AMP Sunset Plan](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077434369) |
| Component Library | [Specification](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5075992637) |

---

## Quality Gates

```
ONBOARDING QUALITY GATE
□ Tour completes without errors
□ Time to value < 5 minutes measured
□ Skip option available at every step
□ Progress saves on exit
□ Accessible to screen readers
```

---

*Epic owned by Product Team. Last updated: 2026-01-04*
