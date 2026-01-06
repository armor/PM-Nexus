# Nexus UI Uplift - POC to Platform Migration Architecture

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Critical:** Aligns Armor-Dash POC to Platform Architecture

---

## 1. Overview

This document details the architecture migration from the Armor-Dash POC to the Platform-aligned production architecture.

### Key Alignment Target

```
Platform Architecture Pattern:
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   UI (React/Next.js)                                        │
│        ↓                                                     │
│   AUTH (Okta OAuth2)                                         │
│        ↓                                                     │
│   API Layer (REST/GraphQL)                                   │
│        ↓                                                     │
│   Data Layer (PostgreSQL, Redis, External APIs)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Requirements

1. **Follow Platform patterns** - Same architecture as existing platform monorepo
2. **Include MCP Server** - Claude Code integration for AI-assisted operations
3. **Carry forward integrations** - All 45+ Armor-Dash connectors
4. **Nx monorepo structure** - Apps as shells, libraries contain logic

---

## 2. Current State (Armor-Dash POC)

### 2.1 POC Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Armor-Dash POC (Current State)                             │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 Next.js Frontend                     │   │
│   │  - Direct Prisma/Supabase calls                      │   │
│   │  - Server Actions for mutations                      │   │
│   │  - No separate API layer                             │   │
│   │  - Auth via Supabase only                            │   │
│   └──────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│                      ▼                                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            Supabase (Direct Access)                  │   │
│   │  - PostgreSQL                                        │   │
│   │  - Auth                                              │   │
│   │  - Realtime                                          │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 POC Gaps vs Platform

| Area | POC State | Platform Standard | Gap |
|------|-----------|-------------------|-----|
| **API Layer** | None (direct DB) | RESTful services | Critical |
| **Authentication** | Supabase only | Okta OAuth2 + RBAC | Critical |
| **Authorization** | Basic | RBAC with permissions | Critical |
| **API Hooks** | Direct Prisma | TanStack Query + Axios | Major |
| **State Management** | Local/context | TanStack Query | Major |
| **Error Handling** | Ad-hoc | Centralized | Major |
| **Caching** | None | Redis | Major |
| **Observability** | Console logs | Datadog APM | Major |
| **MCP Integration** | None | Required | New |

---

## 3. Target State (Platform-Aligned)

### 3.1 Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Nexus Platform (Target State)                               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    UI Layer                           │   │
│  │  - Next.js 15 (Server Components)                    │   │
│  │  - React 19                                          │   │
│  │  - TanStack Query hooks                              │   │
│  │  - Platform component library (@platform/react-ui)   │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │                   Auth Layer                          │   │
│  │  - Okta OAuth2/OIDC                                  │   │
│  │  - JWT tokens                                        │   │
│  │  - RBAC permissions                                  │   │
│  │  - SSO support                                       │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │                   API Layer                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │ Core API  │  │ Auth API  │  │Metrics API│        │   │
│  │  │ (Node.js) │  │ (Node.js) │  │ (Node.js) │        │   │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘        │   │
│  │        │              │              │               │   │
│  │  ┌───────────────────────────────────────────┐      │   │
│  │  │           MCP Server Integration           │      │   │
│  │  │  - Claude Code tools                       │      │   │
│  │  │  - AI-assisted operations                  │      │   │
│  │  │  - Jira/Confluence integration             │      │   │
│  │  └───────────────────────────────────────────┘      │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │                  Data Layer                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │  │PostgreSQL │  │   Redis   │  │ External  │        │   │
│  │  │   (RDS)   │  │  (Cache)  │  │   APIs    │        │   │
│  │  └───────────┘  └───────────┘  └───────────┘        │   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────┐      │   │
│  │  │        Connector Service (45+ APIs)        │      │   │
│  │  │  AWS │ Azure │ CrowdStrike │ Okta │ etc   │      │   │
│  │  └───────────────────────────────────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. MCP Server Integration

### 4.1 MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code / AI Tooling                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   MCP Client                         │    │
│  │  (Claude Code, Cursor, VS Code, etc.)                │    │
│  └───────────────────────┬─────────────────────────────┘    │
│                          │ stdio/HTTP                        │
│  ┌───────────────────────▼─────────────────────────────┐    │
│  │               Armor MCP Server                       │    │
│  │                                                      │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │              Jira Tools                      │    │    │
│  │  │  - create_issue_link                         │    │    │
│  │  │  - set_epic_link                             │    │    │
│  │  │  - search_issues                             │    │    │
│  │  │  - get_issue                                 │    │    │
│  │  │  - bulk_create_links                         │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                      │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │           Confluence Tools                   │    │    │
│  │  │  - get_confluence_page                       │    │    │
│  │  │  - create_confluence_page                    │    │    │
│  │  │  - update_confluence_page                    │    │    │
│  │  │  - search_confluence_pages                   │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                      │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │          Nexus Platform Tools (NEW)          │    │    │
│  │  │  - get_security_posture                      │    │    │
│  │  │  - search_alerts                             │    │    │
│  │  │  - get_vulnerability_summary                 │    │    │
│  │  │  - generate_compliance_report                │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                   │
│  ┌───────────────────────▼─────────────────────────────┐    │
│  │               External Services                      │    │
│  │  - Jira Cloud API                                   │    │
│  │  - Confluence Cloud API                             │    │
│  │  - Nexus Platform API                               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 MCP Server Configuration

```json
// .mcp.json
{
  "mcpServers": {
    "armor-jira-mcp": {
      "command": "node",
      "args": ["/path/to/jira-mcp/dist/index.js"],
      "env": {
        "JIRA_HOST": "${JIRA_HOST}",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    },
    "nexus-mcp": {
      "command": "node",
      "args": ["/path/to/nexus-mcp/dist/index.js"],
      "env": {
        "NEXUS_API_URL": "https://api.nexus.armor.com",
        "NEXUS_API_KEY": "${NEXUS_API_KEY}"
      }
    }
  }
}
```

### 4.3 Nexus MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_security_posture` | Get org security score | `org_id?` |
| `search_alerts` | Search alerts with filters | `severity`, `status`, `query` |
| `get_alert_details` | Get full alert info | `alert_id` |
| `acknowledge_alert` | Acknowledge an alert | `alert_id`, `note?` |
| `get_vulnerability_summary` | Vuln stats | `org_id?`, `severity?` |
| `search_vulnerabilities` | Search vulns | `cve?`, `severity?`, `status?` |
| `get_compliance_status` | Compliance posture | `framework?` |
| `generate_report` | Generate PDF report | `type`, `date_range` |
| `get_asset_inventory` | Asset list | `type?`, `risk_score?` |

---

## 5. Integration Migration

### 5.1 Armor-Dash Integrations to Carry Forward

Based on Armor-Dash POC analysis, these integrations must be migrated:

#### Cloud Security (9 integrations)
- AWS Security Hub
- AWS GuardDuty
- AWS Inspector
- AWS Config
- AWS CloudTrail
- Azure Defender
- Azure Sentinel
- GCP Security Command Center
- GCP Cloud Armor

#### Endpoint Security (5 integrations)
- CrowdStrike Falcon
- Microsoft Defender for Endpoint
- SentinelOne
- Carbon Black
- Sophos

#### Vulnerability Management (4 integrations)
- Qualys
- Tenable.io
- Rapid7 InsightVM
- Nessus

#### Identity & Access (6 integrations)
- Okta
- Azure AD / Entra ID
- Google Workspace
- CyberArk
- Duo Security
- OneLogin

#### SIEM & Log (5 integrations)
- Splunk
- Sumo Logic
- Elastic SIEM
- LogRhythm
- Datadog SIEM

#### Network Security (4 integrations)
- Palo Alto Networks
- Cisco Umbrella
- Zscaler
- Cloudflare

#### Email Security (3 integrations)
- Proofpoint
- Mimecast
- Microsoft Defender for Office 365

#### Ticketing & Workflow (4 integrations)
- Jira
- ServiceNow
- PagerDuty
- Slack

#### Compliance (3 integrations)
- Drata
- Vanta
- OneTrust

#### Other (2 integrations)
- GitHub Advanced Security
- Snyk

### 5.2 Connector Migration Strategy

```typescript
// Before (POC - Direct API calls)
async function fetchCrowdStrikeAlerts() {
  const response = await fetch("https://api.crowdstrike.com/...", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  // Direct database insert
  await prisma.alert.createMany({ data: transformAlerts(data) });
}

// After (Platform - API Layer)
// 1. Connector Service handles fetching
// 2. Data normalized to standard schema
// 3. Sent to SQS queue
// 4. Ingestion service persists
// 5. API layer serves to frontend
```

---

## 6. Migration Phases

### Phase 1: API Layer Foundation (Weeks 1-4)

| Task | Description | Priority |
|------|-------------|----------|
| Create API service scaffold | Node.js/Fastify base | P0 |
| Implement auth middleware | JWT validation | P0 |
| Create core API routes | CRUD for main entities | P0 |
| Set up database connection | PostgreSQL via Prisma | P0 |
| Implement caching layer | Redis integration | P1 |

### Phase 2: Frontend Migration (Weeks 5-8)

| Task | Description | Priority |
|------|-------------|----------|
| Create API hooks library | TanStack Query hooks | P0 |
| Migrate data fetching | Replace direct calls | P0 |
| Implement MSW mocking | All API endpoints | P0 |
| Update components | Use new hooks | P0 |
| Add loading/error states | Standard patterns | P1 |

### Phase 3: Connector Migration (Weeks 9-12)

| Task | Description | Priority |
|------|-------------|----------|
| Create connector framework | Base class, queue | P0 |
| Migrate cloud connectors | AWS, Azure, GCP | P0 |
| Migrate security connectors | EDR, Vuln | P0 |
| Migrate identity connectors | Okta, Azure AD | P1 |
| Migrate remaining | SIEM, ticketing | P1 |

### Phase 4: MCP & Polish (Weeks 13-14)

| Task | Description | Priority |
|------|-------------|----------|
| Create Nexus MCP server | Claude Code tools | P1 |
| Integration testing | All connectors | P0 |
| Performance optimization | Caching, queries | P1 |
| Documentation | API docs, guides | P1 |

---

## 7. Code Migration Patterns

### 7.1 Data Fetching Migration

```typescript
// BEFORE (POC - Direct Prisma)
// components/AlertList.tsx
import { prisma } from "@/lib/prisma";

async function AlertList() {
  const alerts = await prisma.alert.findMany({
    where: { status: "open" },
    orderBy: { createdAt: "desc" },
  });

  return <AlertTable alerts={alerts} />;
}

// AFTER (Platform - API Hook)
// libs/nexus/react-api-nexus/src/lib/useAlerts/useAlerts.ts
import { useQuery } from "@tanstack/react-query";
import { axios } from "@platform/react-api-base";

export function useAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: ["alerts", filters],
    queryFn: async () => {
      const res = await axios.get("/api/v1/alerts", { params: filters });
      return res.data.data.items;
    },
    placeholderData: [], // Required for loading states
  });
}

// libs/nexus/react-ui-nexus/src/lib/components/AlertList/AlertList.tsx
import { useAlerts } from "@platform/react-api-nexus";

export function AlertList({ filters }: AlertListProps) {
  const { data: alerts, isLoading, error } = useAlerts(filters);

  if (isLoading) return <AlertListSkeleton />;
  if (error) return <ErrorState error={error} />;
  if (!alerts.length) return <EmptyState message="No alerts found" />;

  return <AlertTable alerts={alerts} />;
}
```

### 7.2 Authentication Migration

```typescript
// BEFORE (POC - Supabase Auth)
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(url, key);

async function login(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return data.session;
}

// AFTER (Platform - Okta OAuth2)
import { useOktaAuth } from "@platform/react-api-auth";

export function useAuth() {
  const { authState, oktaAuth } = useOktaAuth();

  const login = async () => {
    await oktaAuth.signInWithRedirect();
  };

  const logout = async () => {
    await oktaAuth.signOut();
  };

  return {
    isAuthenticated: authState?.isAuthenticated,
    user: authState?.idToken?.claims,
    login,
    logout,
  };
}
```

### 7.3 Server Action to API Migration

```typescript
// BEFORE (POC - Server Action)
// app/actions/alerts.ts
"use server";
import { prisma } from "@/lib/prisma";

export async function acknowledgeAlert(alertId: string) {
  await prisma.alert.update({
    where: { id: alertId },
    data: {
      status: "acknowledged",
      acknowledgedAt: new Date(),
    },
  });
}

// AFTER (Platform - API + Hook)
// API: services/nexus-api/src/routes/alerts.ts
app.post("/api/v1/alerts/:id/acknowledge", async (req, res) => {
  const { id } = req.params;
  const { userId } = req.auth;

  const alert = await alertService.acknowledge(id, userId);

  return res.json({ success: true, data: alert });
});

// Hook: libs/nexus/react-api-nexus/src/lib/useAlerts/useAcknowledgeAlert.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (alertId: string) => {
      const res = await axios.post(`/api/v1/alerts/${alertId}/acknowledge`);
      return res.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}
```

---

## 8. Library Structure

### 8.1 Nx Library Organization

```
libs/
├── nexus/                              # Domain: Nexus Platform
│   ├── react-api-nexus/               # API hooks for Nexus
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── useAlerts/
│   │   │   │   │   ├── useAlerts.ts
│   │   │   │   │   ├── useAlerts.mock.ts
│   │   │   │   │   └── useAlerts.spec.tsx
│   │   │   │   ├── useAssets/
│   │   │   │   ├── useVulnerabilities/
│   │   │   │   ├── useCompliance/
│   │   │   │   └── useMetrics/
│   │   │   └── index.ts
│   │   └── project.json
│   │
│   ├── react-ui-nexus/                # UI components for Nexus
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── components/
│   │   │   │   │   ├── AlertCard/
│   │   │   │   │   ├── AlertList/
│   │   │   │   │   ├── AssetTable/
│   │   │   │   │   └── ...
│   │   │   │   └── pages/
│   │   │   │       ├── DashboardPage/
│   │   │   │       ├── AlertsPage/
│   │   │   │       └── ...
│   │   │   └── index.ts
│   │   └── project.json
│   │
│   └── data-nexus/                    # Shared types/utils
│       ├── src/
│       │   ├── lib/
│       │   │   ├── types/
│       │   │   ├── schemas/
│       │   │   └── utils/
│       │   └── index.ts
│       └── project.json
│
├── shared/                             # Cross-domain shared
│   ├── react-ui/                      # Base components
│   ├── react-api-base/                # API utilities
│   └── react-api-auth/                # Auth hooks
│
└── services/                           # Backend services
    ├── nexus-api/                     # Core API service
    ├── nexus-auth/                    # Auth service
    ├── nexus-connector/               # Connector service
    └── nexus-mcp/                     # MCP server
```

---

## 9. Testing Requirements

### 9.1 Migration Testing Checklist

For each migrated component/feature:

- [ ] Unit tests passing
- [ ] MSW handlers created
- [ ] Storybook stories work
- [ ] E2E tests verify API calls (not just UI)
- [ ] E2E tests verify persistence after reload
- [ ] Error states handled
- [ ] Loading states implemented
- [ ] Accessibility verified

### 9.2 Integration Testing

```typescript
// E2E test for migrated alert acknowledgement
test("acknowledges alert via API", async ({ page }) => {
  // Capture console errors
  const consoleErrors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });

  // Navigate to alert
  await page.goto("/alerts/alert-123");

  // Click acknowledge and intercept API
  const [response] = await Promise.all([
    page.waitForResponse((r) =>
      r.url().includes("/api/v1/alerts/alert-123/acknowledge") &&
      r.request().method() === "POST"
    ),
    page.getByRole("button", { name: "Acknowledge" }).click(),
  ]);

  // Verify API accepted
  expect(response.status()).toBe(200);

  // Verify persistence
  await page.reload();
  await expect(page.getByText("Acknowledged")).toBeVisible();

  // Verify no console errors
  expect(consoleErrors).toHaveLength(0);
});
```

---

## 10. Success Criteria

### 10.1 Migration Complete When

- [ ] All POC features work through API layer
- [ ] Authentication via Okta (not Supabase)
- [ ] All 45+ connectors migrated and tested
- [ ] MCP server operational with Nexus tools
- [ ] E2E tests pass for all critical paths
- [ ] Performance meets SLAs (P95 < 200ms)
- [ ] No direct database access from frontend
- [ ] All API hooks have MSW handlers
- [ ] Storybook works for all components

### 10.2 Technical Debt Eliminated

- [ ] No Prisma calls in frontend code
- [ ] No Supabase auth dependencies
- [ ] No server actions (replaced with API)
- [ ] Proper error handling throughout
- [ ] Consistent loading states
- [ ] Type-safe API contracts

---

## 11. Related Diagrams

### Figure 1: System Architecture
*Complete platform architecture showing all layers from client to data.*

> **Diagram:** [System Architecture](../diagrams/architecture/01-system-architecture.md)
>
> Shows the full Kubernetes-based architecture including:
> - Client Layer (Web, Mobile, MCP)
> - CDN & Edge (CloudFront, WAF)
> - EKS Services (Frontend, API, Workers, MCP)
> - Data Layer (PostgreSQL, Redis, OpenSearch, S3)
> - External Integrations (45+ connectors)

### Figure 2: Platform Alignment
*Migration path from POC to production architecture.*

> **Diagram:** [Platform Alignment](../diagrams/architecture/02-platform-alignment.md)
>
> Visualizes the migration strategy and technology alignment between Armor-Dash POC and Platform standards.

---

*This migration architecture is critical for platform alignment. All changes must follow these patterns.*
