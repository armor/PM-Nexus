# Task 01: Audit All Navigation Paths Across Codebase

**Task ID:** NEXUS-NAV-003-T01
**Story:** NEXUS-NAV-003
**Estimate:** 1 hour
**Type:** Investigation

---

## Objective

Scan the entire codebase to identify all instances of relative path usage in navigation components and document them for remediation.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-003-T01 for the Nexus UI Uplift project.

CONTEXT:
- Codebase: submodules/platform/
- Goal: Find ALL relative paths in navigation code
- Output: Detailed audit report for fixing

INSTRUCTIONS:
1. Search for relative path patterns in Link/NavLink components:

```bash
# Find relative paths starting with ./
rg "to=[\"'\`]\./" --type tsx --type ts

# Find relative paths starting with ../
rg "to=[\"'\`]\.\." --type tsx --type ts

# Find navigate() calls with relative paths
rg "navigate\([\"'\`]\./" --type tsx --type ts

# Find useNavigate with relative
rg "useNavigate.*\./" --type tsx --type ts
```

2. Search for relative paths in router configs:

```bash
# Find path definitions without leading /
rg "path:\s*[\"'\`][^/]" --type tsx --type ts
```

3. For each finding, document:
   - File path
   - Line number
   - Current relative path
   - Recommended absolute path
   - Context (what page/component)

4. Categorize findings by console app

OUTPUT FORMAT:
```markdown
## Path Audit Report

### Summary
- Total relative paths found: X
- By console:
  - infrastructure-console: X
  - threat-management: X
  - ...

### Detailed Findings

#### infrastructure-console

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| src/components/AssetList.tsx | 45 | ./details | /infrastructure/assets/{id}/details |
| ... | ... | ... | ... |

#### threat-management
...
```

DO NOT modify any code in this task - investigation only.
```

---

## Checklist

- [ ] Link components audited
- [ ] NavLink components audited
- [ ] navigate() calls audited
- [ ] Router configs audited
- [ ] All 9 consoles covered
- [ ] Audit report generated
- [ ] Ready for task-02

---

## Search Commands Reference

```bash
# All relative navigation patterns
rg "(to|href)=[\"'\`]\.\.?\/" apps/ libs/

# Navigate calls
rg "navigate\([\"'\`][^/]" apps/ libs/

# Router path without leading slash
rg "path:\s*[\"'\`][a-zA-Z]" apps/ libs/
```
