# Nexus UI Uplift - Epic Portfolio

> **Project:** Nexus UI Uplift
> **Jira Project:** STAGE
> **Status:** Ready for Sprint Planning
> **Last Updated:** 2026-01-04

---

## Overview

This directory contains all epics for the Nexus UI Uplift initiative. The project aims to make Nexus GTM-ready and capable of fully replacing AMP by end of Q1.

| Metric | Value |
|--------|-------|
| **Epics** | 15 |
| **Stories** | 143 |
| **Story Points** | 465pt |
| **Sprints** | 15 |

---

## Epic Structure

Each epic follows this structure:
```
EPIC-N-NEXUS-{NAME}/
├── README.md              # Epic overview, stories, acceptance criteria
└── stories/               # Individual story details (for detailed epics)
    └── NN-{slug}/
        ├── story-NN-{slug}.md
        └── tasks/
            └── task-NN-{name}.md
```

---

## Epic Portfolio by Priority

### P0: Critical (289pt, 87 stories) - MVP 1

| # | Epic | Key | Points | Stories | Focus |
|---|------|-----|--------|---------|-------|
| 1 | [NEXUS-NAVIGATION](./EPIC-1-NEXUS-NAVIGATION/) | NEXUS-NAV | 14pt | 5 | Fix routing, breadcrumbs |
| 2 | [NEXUS-STABILITY](./EPIC-2-NEXUS-STABILITY/) | NEXUS-STAB | 19pt | 5 | Error boundaries, crash fixes |
| 3 | [NEXUS-RESILIENCE](./EPIC-3-NEXUS-RESILIENCE/) | NEXUS-RES | 69pt | 22 | Error recovery, graceful degradation |
| 4 | [NEXUS-ONBOARD](./EPIC-4-NEXUS-ONBOARD/) | NEXUS-ONB | 21pt | 10 | Product tour, 5-min-to-value |
| 5 | [NEXUS-EXPLAIN](./EPIC-5-NEXUS-EXPLAIN/) | NEXUS-EXP | 35pt | 10 | Metric tooltips, drill-through |
| 6 | [NEXUS-VALUE](./EPIC-6-NEXUS-VALUE/) | NEXUS-VAL | 64pt | 20 | Success states, value proof |
| 7 | [NEXUS-UX-FOUNDATION](./EPIC-7-NEXUS-UX-FOUNDATION/) | NEXUS-UXF | 25pt | 8 | Accessibility, usability |
| 8 | [NEXUS-UX-COMPREHENSION](./EPIC-8-NEXUS-UX-COMPREHENSION/) | NEXUS-UXC | 22pt | 7 | Information architecture |

### P1: Efficiency (136pt, 40 stories) - MVP 2

| # | Epic | Key | Points | Stories | Focus |
|---|------|-----|--------|---------|-------|
| 9 | [NEXUS-FLOW](./EPIC-9-NEXUS-FLOW/) | NEXUS-FLO | 42pt | 12 | 2-click navigation, friction reduction |
| 10 | [NEXUS-UX-EFFICIENCY](./EPIC-10-NEXUS-UX-EFFICIENCY/) | NEXUS-UXE | 28pt | 9 | Command palette, shortcuts |
| 11 | [NEXUS-THEME](./EPIC-11-NEXUS-THEME/) | NEXUS-THM | 35pt | 10 | CSS-only theme switching |
| 12 | [NEXUS-COMPONENTS](./EPIC-12-NEXUS-COMPONENTS/) | NEXUS-CMP | 16pt | 5 | Consolidate redundant patterns |

### P2: Polish (39pt, 13 stories) - MVP 3

| # | Epic | Key | Points | Stories | Focus |
|---|------|-----|--------|---------|-------|
| 13 | [NEXUS-UX-DELIGHT](./EPIC-13-NEXUS-UX-DELIGHT/) | NEXUS-UXD | 15pt | 5 | Micro-interactions, animations |
| 14 | [NEXUS-I18N](./EPIC-14-NEXUS-I18N/) | NEXUS-I18N | 11pt | 4 | Internationalization prep |
| 15 | [NEXUS-TYPE-SAFETY](./EPIC-15-NEXUS-TYPE-SAFETY/) | NEXUS-TYP | 13pt | 4 | Remove type assertions |

---

## Dependency Graph

```
NEXUS-NAV ──┬──> NEXUS-FLOW
            │
            └──> NEXUS-UXF ──> NEXUS-UXE ──> NEXUS-UXD
                    │
                    └──> NEXUS-UXC

NEXUS-STAB ──> NEXUS-RES

NEXUS-VALUE ──> NEXUS-EXPLAIN

NEXUS-THM ──> NEXUS-CMP

(Independent: NEXUS-ONBOARD, NEXUS-I18N, NEXUS-TYP)
```

---

## Sprint Allocation

| Sprint | Epics | Points |
|--------|-------|--------|
| Sprint 1 | NEXUS-NAV | 14pt |
| Sprint 2 | NEXUS-STAB | 19pt |
| Sprint 3 | NEXUS-RES (1/3), NEXUS-ONB (1/2), NEXUS-UXF (1/2) | ~33pt |
| Sprint 4 | NEXUS-RES (2/3), NEXUS-ONB (2/2), NEXUS-EXP (1/2) | ~35pt |
| Sprint 5 | NEXUS-RES (3/3), NEXUS-EXP (2/2), NEXUS-VAL (1/3) | ~35pt |
| Sprint 6 | NEXUS-VAL (2/3), NEXUS-UXC, NEXUS-FLO (1/2) | ~35pt |
| Sprint 7 | NEXUS-VAL (3/3), NEXUS-FLO (2/2), NEXUS-UXE (1/2) | ~32pt |
| Sprint 8 | NEXUS-UXE (2/2), NEXUS-THM (1/2) | ~30pt |
| Sprint 9 | NEXUS-THM (2/2), NEXUS-CMP (1/2) | ~28pt |
| Sprint 10 | NEXUS-CMP (2/2) | ~8pt |
| Sprint 11 | NEXUS-UXD (1/2) | ~8pt |
| Sprint 12 | NEXUS-UXD (2/2), NEXUS-I18N (1/2) | ~10pt |
| Sprint 13 | NEXUS-I18N (2/2), NEXUS-TYP (1/2) | ~8pt |
| Sprint 14 | NEXUS-TYP (2/2) | ~5pt |
| Sprint 15 | Buffer / Bug Fixes | ~10pt |

---

## File Index

### Detailed Epics (with story/task files)

- [EPIC-1-NEXUS-NAVIGATION/](./EPIC-1-NEXUS-NAVIGATION/) - Full story breakdown with tasks
- [EPIC-2-NEXUS-STABILITY/](./EPIC-2-NEXUS-STABILITY/) - Full story breakdown with tasks

### Epic READMEs (story summaries)

- [EPIC-3-NEXUS-RESILIENCE/](./EPIC-3-NEXUS-RESILIENCE/)
- [EPIC-4-NEXUS-ONBOARD/](./EPIC-4-NEXUS-ONBOARD/)
- [EPIC-5-NEXUS-EXPLAIN/](./EPIC-5-NEXUS-EXPLAIN/)
- [EPIC-6-NEXUS-VALUE/](./EPIC-6-NEXUS-VALUE/)
- [EPIC-7-NEXUS-UX-FOUNDATION/](./EPIC-7-NEXUS-UX-FOUNDATION/)
- [EPIC-8-NEXUS-UX-COMPREHENSION/](./EPIC-8-NEXUS-UX-COMPREHENSION/)
- [EPIC-9-NEXUS-FLOW/](./EPIC-9-NEXUS-FLOW/)
- [EPIC-10-NEXUS-UX-EFFICIENCY/](./EPIC-10-NEXUS-UX-EFFICIENCY/)
- [EPIC-11-NEXUS-THEME/](./EPIC-11-NEXUS-THEME/)
- [EPIC-12-NEXUS-COMPONENTS/](./EPIC-12-NEXUS-COMPONENTS/)
- [EPIC-13-NEXUS-UX-DELIGHT/](./EPIC-13-NEXUS-UX-DELIGHT/)
- [EPIC-14-NEXUS-I18N/](./EPIC-14-NEXUS-I18N/)
- [EPIC-15-NEXUS-TYPE-SAFETY/](./EPIC-15-NEXUS-TYPE-SAFETY/)

---

## Definition of Done (Component Checklist)

**ALL component stories MUST satisfy these requirements before completion:**

### Platform Generator Requirements (MANDATORY)

```bash
# For NEW components (NEVER create manually):
nx g @platform/armor-nx-plugin:react-component --project=<lib> --name=<Name> --directory=<path>

# For forms:
nx g @platform/armor-nx-plugin:react-form --project=<lib> --name=<Name>

# For data tables:
nx g @platform/armor-nx-plugin:react-data-table --project=<lib> --name=<Name>

# For API hooks:
nx g @platform/armor-nx-plugin:api-hook --project=<lib> --name=<name> --hookName=use<Name>
```

### Component Checklist (14 items)

- [ ] Created with Nx generator (never manual)
- [ ] TypeScript interfaces defined
- [ ] MUI sx props used (no styled-components)
- [ ] Unit tests written and passing
- [ ] **Storybook stories** for all variants (Default, Loading, Error, Empty)
- [ ] **MSW handlers** for API-connected components
- [ ] Loading state implemented
- [ ] Error state implemented
- [ ] Empty state implemented
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] data-testid attributes added
- [ ] Documentation written
- [ ] Code review completed
- [ ] Visual regression baseline captured

### Storybook Story Requirements

Every component story MUST include:
1. Default story
2. All variant stories
3. Interactive stories (with actions)
4. Loading state story
5. Error state story
6. **MSW handlers** using `parameters.msw.handlers`

```typescript
// Example MSW handler in story
import { http, HttpResponse } from 'msw';

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/v1/endpoint', () => HttpResponse.json({ data }))
      ]
    }
  }
};
```

### Page Development Rules

- Page titles go in **router handle ONLY**, never in page components
- Use `ConsolePageTitle` in router handle
- Wrap pages in `PageErrorBoundary`
- Use Card components for consistent styling

### Existing Component Modification

When modifying EXISTING components:
- [ ] Check for existing Storybook stories
- [ ] Update stories if props/variants change
- [ ] Ensure existing tests pass
- [ ] Document breaking changes

> **Reference:** `submodules/platform/llm/specifications/implement/components/`

---

## Related Documents

### Confluence Documentation (Official)

| Document | Confluence Link |
|----------|-----------------|
| **Parent Page** | [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5015044104) |
| Extended PRD | [Extended PRD - Technical Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077368833) |
| Architecture | [Architecture Document](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077139460) |
| GTM Strategy | [GTM Strategy - AMP Sunset Plan](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077434369) |
| Component Library | [Component Library Specification](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5075992637) |
| Testing Strategy | [Testing Strategy - Deep E2E Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077467137) |
| Design System | [Design System - UX Standards](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5076942851) |
| Security | [Security & Compliance Architecture](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077073927) |
| Migration | [POC to Platform Migration Architecture](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077467156) |
| API Spec | [API Specification](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077336066) |

### Local Repository Documents

#### Nexus UI Uplift
- [PRD](../../docs/nexus-ui-uplift/product/nexus-prd.md)
- [Extended PRD](../../docs/nexus-ui-uplift/product/extended-prd.md)
- [Gap Analysis](../../docs/nexus-ui-uplift/product/gap-analysis.md)
- [Architecture](../../docs/nexus-ui-uplift/architecture/nexus-architecture.md)
- [Success States](../../docs/nexus-ui-uplift/design/success-states-specification.md)
- [UX Requirements](../../docs/nexus-ui-uplift/design/ux-requirements.md)
- [MDR Competitive Analysis](../../docs/nexus-ui-uplift/product/mdr-competitive-analysis.md)

#### Armor-Dash
- [POC Migration](../../docs/armor-dash/architecture/poc-migration.md)
- [API Specification](../../docs/armor-dash/api/api-specification.md)
- [Data Dictionary](../../docs/armor-dash/architecture/data-dictionary.md)

#### Shared
- [Design System](../../docs/shared/design-system.md)
- [Component Library](../../docs/shared/component-library.md)
- [Testing Strategy](../../docs/shared/testing-strategy.md)
- [Security & Compliance](../../docs/shared/security-compliance.md)
- [GTM Strategy](../../docs/shared/gtm-strategy.md)
- [Integration Playbook](../../docs/shared/integration-playbook.md)

#### Platform Reference
- [Platform Component Development](../../submodules/platform/llm/specifications/implement/components/component-development.md)
- [Platform Generators](../../submodules/platform/llm/specifications/implement/generators.md)

---

*Portfolio owned by Product Team. Contact: pm@armor.com*
