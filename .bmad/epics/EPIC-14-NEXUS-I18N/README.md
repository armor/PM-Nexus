# EPIC-14: NEXUS-I18N

**Status:** Ready for Sprint 12
**Priority:** P2 - Polish
**Owner:** NEXUS
**MVP:** MVP 3
**Total Stories:** 4 | **Total Points:** 11

---

## Coordination

| Field | Value |
|-------|-------|
| JIRA Key | NEXUS-I18N |
| Depends On | None |
| Blocks | None |

---

## Summary

Prepare the platform for internationalization by extracting strings, implementing i18n framework, and establishing localization workflow.

---

## Business Value

- **Market expansion** - Ready for global customers
- **Future-proofing** - Infrastructure in place
- **Maintainability** - Centralized string management
- **Consistency** - Same terms everywhere

---

## Acceptance Criteria

- [ ] All user-facing strings extracted to translation files
- [ ] i18n framework integrated (react-i18next)
- [ ] Date/number formatting localized
- [ ] RTL layout support prepared
- [ ] Translation workflow documented

---

## Stories

| ID | Title | Pts | Sprint |
|----|-------|-----|--------|
| NEXUS-I18N-001 | Set up i18n framework | 3pt | Sprint 12 |
| NEXUS-I18N-002 | Extract strings from all consoles | 5pt | Sprint 12 |
| NEXUS-I18N-003 | Implement locale-aware formatting | 2pt | Sprint 13 |
| NEXUS-I18N-004 | Prepare RTL layout foundation | 1pt | Sprint 13 |

---

## Technical Context

### Critical Files

- Create: `libs/shared/i18n/` - i18n utilities
- Create: Translation files (en.json)
- Update: All components to use t() function

### References

- [react-i18next](https://react.i18next.com/)
- [Locale formatting](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)

---

## Confluence Documentation

| Document | Link |
|----------|------|
| **Parent Page** | [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5015044104) |
| Extended PRD | [Technical Requirements](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077368833) |
| Design System | [UX Standards](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5076942851) |
| GTM Strategy | [AMP Sunset Plan](https://armor-defense.atlassian.net/wiki/pages/viewpage.action?pageId=5077434369) |

---

## Quality Gates

```
I18N QUALITY GATE
□ No hardcoded strings in components
□ All strings in translation files
□ Date/number formatting works per locale
□ Translation keys consistent
□ Workflow documented
```

---

*Epic owned by Frontend Team. Last updated: 2026-01-04*
