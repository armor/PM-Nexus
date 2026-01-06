# Task 03: Fix Relative Paths in All Console Apps

**Task ID:** NEXUS-NAV-003-T03
**Story:** NEXUS-NAV-003
**Estimate:** 1 hour
**Type:** Implementation

---

## Objective

Update all relative paths identified in the audit (task-01) to use absolute paths, leveraging the new path utilities (task-02).

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-003-T03 for the Nexus UI Uplift project.

CONTEXT:
- Audit report from task-01 lists all relative paths
- Path utilities from task-02 available
- Goal: Convert all relative paths to absolute

INSTRUCTIONS:
1. Work through audit report systematically by console app

2. For each relative path, convert using one of these patterns:

```typescript
// Pattern A: Use path utility (preferred)
// Before
<Link to="./details">Details</Link>
// After
import { paths } from '@armor/utils';
<Link to={paths.infrastructure.assetDetails(assetId)}>Details</Link>

// Pattern B: Template literal with base path
// Before
<Link to="../list">Back</Link>
// After
<Link to={`/infrastructure/assets`}>Back</Link>

// Pattern C: Navigate function
// Before
navigate('./edit');
// After
navigate(paths.infrastructure.assetEdit(id));
```

3. Handle dynamic segments properly:

```typescript
// Before - relative with param
<Link to={`./items/${itemId}`}>Item</Link>

// After - absolute with param
<Link to={`/infrastructure/assets/${assetId}/items/${itemId}`}>Item</Link>

// Or better - use path utility
<Link to={paths.infrastructure.assetItem(assetId, itemId)}>Item</Link>
```

4. Update router navigate calls:

```typescript
// Before
const navigate = useNavigate();
navigate('./details');

// After
const { toAssetDetails } = useTypedNavigate();
toAssetDetails(assetId);

// Or
navigate(paths.infrastructure.assetDetails(assetId));
```

5. After each console app is updated:
   - Run `npm run lint` to verify no syntax errors
   - Run `npm run typecheck` to verify types
   - Quick manual test of navigation flows

PROCESS:
- Update one console app at a time
- Commit after each console is complete
- Document any edge cases encountered

OUTPUT:
- All relative paths converted to absolute
- Each console app compiles cleanly
- Brief summary of changes per console
```

---

## Checklist by Console

- [ ] infrastructure-console
- [ ] threat-management
- [ ] compliance-console
- [ ] identity-console
- [ ] cloud-console
- [ ] endpoint-console
- [ ] network-console
- [ ] reporting-console
- [ ] admin-console

---

## Verification

After each console:
```bash
cd apps/{console-name}
npm run lint
npm run typecheck
npm run test -- --testPathPattern=navigation
```
