# EPIC-11: NEXUS-THEME

**Status:** Ready for Sprint 8
**Priority:** P1 - Efficiency
**Owner:** NEXUS
**MVP:** MVP 2
**Total Stories:** 10 | **Total Points:** 35

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | NEXUS-THM |
| Depends On | None |
| Blocks | None |

---

## Summary

Implement CSS-only theme switching with dark mode, light mode, and high contrast options. Theming should work without JavaScript and persist across sessions.

---

## Business Value

- **User preference** - Dark mode highly requested
- **Accessibility** - High contrast for visibility
- **Eye strain reduction** - Comfortable night use
- **Modern expectations** - Users expect dark mode

---

## Acceptance Criteria

- [ ] Theme switches via data-theme attribute (no JS required)
- [ ] Dark, light, and high-contrast themes
- [ ] System preference respected by default
- [ ] Theme persists across sessions
- [ ] All components theme-aware

---

## Stories

### Theme Infrastructure (3 stories, 11pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-THM-001 | Create CSS custom property theme system | 5pt | Sprint 8 |
| NEXUS-THM-002 | Implement theme toggle component | 3pt | Sprint 8 |
| NEXUS-THM-003 | Add system preference detection | 3pt | Sprint 8 |

### Theme Variants (4 stories, 14pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-THM-004 | Create dark theme color tokens | 3pt | Sprint 8 |
| NEXUS-THM-005 | Create high contrast theme | 3pt | Sprint 9 |
| NEXUS-THM-006 | Update all components for theming | 5pt | Sprint 9 |
| NEXUS-THM-007 | Create theme preview in settings | 3pt | Sprint 9 |

### Theme Polish (3 stories, 10pt)

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-THM-008 | Add smooth theme transitions | 3pt | Sprint 10 |
| NEXUS-THM-009 | Implement theme-aware charts | 5pt | Sprint 10 |
| NEXUS-THM-010 | Create print-friendly theme | 2pt | Sprint 10 |

---

## Technical Context

### Critical Files

- Update: `libs/shared/tokens/` - Theme tokens
- Create: Theme toggle component
- Update: All component stylesheets

### References

- [Design System Tokens](../../docs/shared/design-system.md#tokens)
- [Color System](../../docs/shared/design-system.md#colors)

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
THEME QUALITY GATE
□ No JS required for theme switching
□ All components render correctly in all themes
□ Charts readable in dark mode
□ High contrast meets WCAG AAA
□ No flash of wrong theme on load
```

---

*Epic owned by Frontend Team. Last updated: 2026-01-04*
