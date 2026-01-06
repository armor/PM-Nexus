# Nexus UI Uplift - Visual Diagrams

> **Format:** Mermaid diagrams (GitHub/Confluence compatible)
> **Last Updated:** 2026-01-04
> **Status:** Active
> **Owner:** Engineering Team

---

## Directory Structure

```
diagrams/
├── README.md                           # This file (index + tracker)
├── architecture/
│   ├── 01-system-architecture.md       # ✅ Overall system design
│   ├── 02-platform-alignment.md        # ✅ POC to Platform migration
│   └── 03-mcp-integration.md           # ✅ MCP server architecture
├── data-flows/
│   ├── README.md                       # ✅ Section index
│   ├── 01-dashboard-request.md         # ✅ Dashboard data request cycle
│   ├── 02-connector-sync.md            # ✅ Connector sync flow
│   ├── 03-multi-connector.md           # ✅ Multi-connector aggregation
│   ├── 04-ai-assistant.md              # ✅ AI question answering
│   └── 05-real-time-updates.md         # ✅ WebSocket/SSE updates
├── components/
│   ├── 01-dashboard-hierarchy.md       # ✅ Dashboard component tree
│   └── 02-widget-dependencies.md       # ✅ Widget data dependencies
├── integrations/
│   └── 01-connector-catalog.md         # ✅ All 46 connectors
└── security/
    ├── 01-auth-flow.md                 # ✅ Authentication flow
    ├── 02-rbac-model.md                # ✅ Role-based access control
    └── 03-mcp-security-model.md        # ✅ MCP security architecture
```

---

## Viewing Diagrams

### GitHub
Mermaid diagrams render automatically in GitHub markdown files.

### VS Code
Install the "Markdown Preview Mermaid Support" extension.

### Confluence
Use the Mermaid macro or paste into draw.io.

### CLI
```bash
npx @mermaid-js/mermaid-cli -i diagram.md -o diagram.svg
```

---

## Diagram Update Tracker

| Diagram | Status | Owner | Last Updated | Referenced In |
|---------|--------|-------|--------------|---------------|
| 01-system-architecture | ✅ Current | Eng | 2026-01-03 | 15-poc-migration-architecture.md |
| 02-platform-alignment | ✅ Current | Eng | 2026-01-03 | nexus-architecture-document.md |
| 01-dashboard-request | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 02-connector-sync | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 03-multi-connector | ✅ Current | Eng | 2026-01-04 | 14-integration-playbook.md |
| 04-ai-assistant | ✅ Current | Eng | 2026-01-04 | 17-ux-requirements.md |
| 05-real-time-updates | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 01-dashboard-hierarchy | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 02-widget-dependencies | ✅ Current | Eng | 2026-01-04 | 04-component-library.md |
| 01-connector-catalog | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 01-auth-flow | ✅ Current | Eng | 2026-01-04 | 21-armor-dash-productionalization.md |
| 02-rbac-model | ✅ Current | Eng | 2026-01-04 | 08-security-compliance.md |
| 03-mcp-integration | ✅ Current | Eng | 2026-01-04 | 20-mcp-server-specification.md |
| 03-mcp-security-model | ✅ Current | Eng | 2026-01-04 | 08-security-compliance.md |

---

## Planned Diagrams

| Diagram | Priority | Target Doc | Status |
|---------|----------|------------|--------|
| 03-aws-infrastructure | HIGH | 09-operations-runbook.md | Planned |
| 03-form-patterns | MEDIUM | 04-component-library.md | Planned |
| 04-navigation-flow | MEDIUM | 17-ux-requirements.md | Planned |
| 02-data-normalization | MEDIUM | 14-integration-playbook.md | Planned |
| 03-external-apis | MEDIUM | 18-api-developer-experience.md | Planned |
| 03-data-access | LOW | 08-security-compliance.md | Planned |

---

## Diagram Index

| Category | Diagram | Description | Link |
|----------|---------|-------------|------|
| Architecture | System Architecture | Full system with all layers | [View](./architecture/01-system-architecture.md) |
| Architecture | Platform Alignment | POC to Platform migration path | [View](./architecture/02-platform-alignment.md) |
| Data Flows | Dashboard Request | User → API → Data → UI | [View](./data-flows/01-dashboard-request.md) |
| Data Flows | Connector Sync | External system data sync | [View](./data-flows/02-connector-sync.md) |
| Data Flows | Multi-Connector | Aggregation and dedup | [View](./data-flows/03-multi-connector.md) |
| Data Flows | AI Assistant | Question → Intent → Answer | [View](./data-flows/04-ai-assistant.md) |
| Data Flows | Real-time Updates | WebSocket/SSE patterns | [View](./data-flows/05-real-time-updates.md) |
| Components | Dashboard Hierarchy | Component tree structure | [View](./components/01-dashboard-hierarchy.md) |
| Components | Widget Dependencies | Data source mappings | [View](./components/02-widget-dependencies.md) |
| Integrations | Connector Catalog | All 46 integrations | [View](./integrations/01-connector-catalog.md) |
| Security | Auth Flow | Login/logout/session | [View](./security/01-auth-flow.md) |
| Security | RBAC Model | Roles and permissions | [View](./security/02-rbac-model.md) |
| Security | MCP Security Model | AI assistant security | [View](./security/03-mcp-security-model.md) |
| Architecture | MCP Integration | AI assistant architecture | [View](./architecture/03-mcp-integration.md) |

---

## Related Documentation

- [Planning Artifacts](../planning-artifacts/README.md) - All planning documents
- [Productionalization Doc](../planning-artifacts/21-armor-dash-productionalization.md) - Master analysis with embedded diagrams
- [Connector Documentation](../planning-artifacts/21-armor-dash-productionalization.md#4-connector-implementation-status) - Connector status details
