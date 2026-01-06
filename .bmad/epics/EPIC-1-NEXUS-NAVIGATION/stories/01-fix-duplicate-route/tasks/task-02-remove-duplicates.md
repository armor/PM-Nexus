# Task 02: Remove Duplicate Route Definitions

**Task ID:** NEXUS-NAV-001-T02
**Story:** NEXUS-NAV-001
**Estimate:** 15 minutes
**Type:** Implementation

---

## Objective

Remove the duplicate route definitions identified in task-01, keeping the correct/most-specific definitions.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-001-T02 for the Nexus UI Uplift project.

CONTEXT:
- File: apps/infrastructure-console/src/router.tsx
- Previous task identified duplicate routes
- Goal: Remove duplicates, keeping most specific definitions

INSTRUCTIONS:
1. Read apps/infrastructure-console/src/router.tsx
2. Locate the duplicate route definitions (lines 76-92 area)
3. Remove the duplicate entries, keeping:
   - More specific paths over generic ones
   - The definition with the correct component mapping
4. Ensure route order follows React Router best practices:
   - More specific routes before generic catch-alls
   - Index routes appropriately placed
5. Run `npm run lint` to verify no syntax errors

CONSTRAINTS:
- Do NOT change route paths (only remove duplicates)
- Do NOT change component imports
- Do NOT modify other parts of the router

OUTPUT:
- Modified router.tsx with duplicates removed
- Brief summary of changes made
```

---

## Checklist

- [ ] Duplicate routes removed
- [ ] Route order verified (specific before generic)
- [ ] Lint passes
- [ ] App compiles without errors

---

## Rollback Plan

```bash
git checkout apps/infrastructure-console/src/router.tsx
```
