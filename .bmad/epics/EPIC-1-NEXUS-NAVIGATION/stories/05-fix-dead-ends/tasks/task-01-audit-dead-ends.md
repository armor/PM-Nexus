# Task 01: Audit All Threat-Management Pages for Dead-Ends

**Task ID:** NEXUS-NAV-005-T01
**Story:** NEXUS-NAV-005
**Estimate:** 30 minutes
**Type:** Investigation

---

## Objective

Systematically audit every page and modal in the threat-management console to identify navigation dead-ends.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-005-T01 for the Nexus UI Uplift project.

CONTEXT:
- Console: apps/threat-management/
- Goal: Find ALL navigation dead-ends
- Dead-end = Page with no clear forward/backward navigation

INSTRUCTIONS:
1. List all routes in threat-management router:

```bash
rg "path:" apps/threat-management/src/router.tsx
```

2. For each route, analyze the page component:
   - Does it have breadcrumbs?
   - Does it have a back button?
   - Does it have forward navigation (links to related items)?
   - Are there any action buttons that lead somewhere?

3. Identify dead-end patterns:

   **Pattern A: No Back Navigation**
   - Page has no breadcrumbs
   - Page has no back button
   - Only escape is browser back

   **Pattern B: No Forward Navigation**
   - Detail page with no related links
   - No "Next steps" or actions
   - User must navigate away manually

   **Pattern C: Orphan Pages**
   - Pages not linked from anywhere
   - Only accessible via direct URL
   - No context for where to go

   **Pattern D: Modal Dead-Ends**
   - Modal closes to unexpected page
   - Modal has no cancel/close button
   - Modal success goes to wrong destination

4. Document each dead-end:
   - Route path
   - Page component
   - Missing navigation
   - Impact on user flow
   - Recommended fix

OUTPUT FORMAT:
```markdown
## Dead-End Audit Report

### Summary
- Total pages audited: X
- Dead-ends found: Y
- By category:
  - No back navigation: X
  - No forward navigation: X
  - Orphan pages: X
  - Modal issues: X

### Detailed Findings

#### /threats/incidents/:id/timeline
- **Issue:** No forward navigation
- **Missing:** Links to related alerts, response actions
- **Impact:** User stuck at end of timeline
- **Fix:** Add "Related Alerts" and "Take Action" sections

#### /threats/alerts/:id
- **Issue:** No parent incident link
- **Missing:** Link back to incident if alert is part of one
- **Impact:** User loses incident context
- **Fix:** Add "Parent Incident" card if applicable

[Continue for all findings...]
```

DO NOT modify any code in this task - investigation only.
```

---

## Checklist

- [ ] All routes listed
- [ ] Each page analyzed
- [ ] Dead-ends documented
- [ ] Modals audited
- [ ] Fixes recommended
- [ ] Ready for task-02

---

## Page Audit Template

| Route | Has Back | Has Forward | Has Breadcrumbs | Dead-End? |
|-------|----------|-------------|-----------------|-----------|
| /threats | - | ✓ | - | No |
| /threats/incidents | ✓ | ✓ | ✓ | No |
| /threats/incidents/:id | ? | ? | ? | ? |
| /threats/incidents/:id/timeline | ? | ? | ? | ? |
| /threats/alerts | ✓ | ✓ | ✓ | No |
| /threats/alerts/:id | ? | ? | ? | ? |
| ... | ... | ... | ... | ... |
