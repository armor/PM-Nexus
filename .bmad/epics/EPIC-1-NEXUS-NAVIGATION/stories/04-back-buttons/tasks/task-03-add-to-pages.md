# Task 03: Add BackButton to All Detail Pages

**Task ID:** NEXUS-NAV-004-T03
**Story:** NEXUS-NAV-004
**Estimate:** 1.5 hours
**Type:** Implementation

---

## Objective

Add the BackButton component to all detail page headers across all 9 console applications.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-004-T03 for the Nexus UI Uplift project.

CONTEXT:
- Component: BackButton from libs/shared/react-ui
- Target: All detail pages across 9 console apps
- Goal: Consistent back navigation everywhere

DETAIL PAGES TO UPDATE:

1. **infrastructure-console**
   - AssetDetail → "Back to Assets"
   - VulnerabilityDetail → "Back to Vulnerabilities"
   - ConfigurationDetail → "Back to Configurations"

2. **threat-management**
   - IncidentDetail → "Back to Incidents"
   - AlertDetail → "Back to Alerts"
   - ThreatDetail → "Back to Threats"

3. **compliance-console**
   - FrameworkDetail → "Back to Frameworks"
   - ControlDetail → "Back to Controls"
   - EvidenceDetail → "Back to Evidence"

4. **identity-console**
   - UserDetail → "Back to Users"
   - GroupDetail → "Back to Groups"
   - RoleDetail → "Back to Roles"

5. **cloud-console**
   - ProviderDetail → "Back to Providers"
   - ResourceDetail → "Back to Resources"
   - PolicyDetail → "Back to Policies"

6. **endpoint-console**
   - DeviceDetail → "Back to Devices"
   - AgentDetail → "Back to Agents"
   - PolicyDetail → "Back to Policies"

7. **network-console**
   - FlowDetail → "Back to Flows"
   - DeviceDetail → "Back to Devices"
   - SegmentDetail → "Back to Segments"

8. **reporting-console**
   - ReportDetail → "Back to Reports"
   - ScheduleDetail → "Back to Schedules"

9. **admin-console**
   - UserDetail → "Back to Users"
   - TeamDetail → "Back to Teams"
   - IntegrationDetail → "Back to Integrations"

INSTRUCTIONS:
1. For each detail page:
   a. Import BackButton
   b. Add to page header (after breadcrumbs, before title)
   c. Configure with appropriate path and label

2. Standard placement pattern:

```tsx
import { BackButton } from '@armor/react-ui';
import { paths } from '@armor/utils';

function AssetDetail({ assetId }: { assetId: string }) {
  return (
    <div className="page-detail">
      <header className="page-header">
        <BackButton
          to={paths.infrastructure.assets()}
          label="Assets"
          preserveState
        />
        <h1>Asset Details</h1>
      </header>
      {/* ... */}
    </div>
  );
}
```

3. Handle nested detail pages:

```tsx
// For deeply nested pages, back goes to immediate parent
function VulnerabilityDetail({ assetId, vulnId }) {
  return (
    <BackButton
      to={paths.infrastructure.asset(assetId)}
      label="Asset"
    />
  );
}
```

4. After each console:
   - Verify back buttons render
   - Test navigation works
   - Check state preservation

OUTPUT:
- All detail pages updated
- Consistent back button placement
- State preservation working
```

---

## Checklist by Console

- [ ] infrastructure-console (3 pages)
- [ ] threat-management (3 pages)
- [ ] compliance-console (3 pages)
- [ ] identity-console (3 pages)
- [ ] cloud-console (3 pages)
- [ ] endpoint-console (3 pages)
- [ ] network-console (3 pages)
- [ ] reporting-console (2 pages)
- [ ] admin-console (3 pages)

---

## Page Inventory

| Console | Page | Path | Back Label |
|---------|------|------|------------|
| infrastructure | AssetDetail | /infrastructure/assets/:id | Assets |
| infrastructure | VulnDetail | /infrastructure/assets/:id/vulns/:vid | Asset |
| threats | IncidentDetail | /threats/incidents/:id | Incidents |
| threats | AlertDetail | /threats/alerts/:id | Alerts |
| compliance | FrameworkDetail | /compliance/frameworks/:id | Frameworks |
| compliance | ControlDetail | /compliance/frameworks/:fid/controls/:cid | Framework |
| ... | ... | ... | ... |

---

## Verification

After each console:
1. Navigate to detail page from list
2. Verify back button visible
3. Click back button
4. Verify return to list
5. Verify filters/scroll preserved
