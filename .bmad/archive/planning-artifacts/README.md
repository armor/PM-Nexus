# UI-Uplift Planning Artifacts

**Status**: Active
**Owner**: Product Engineering Team
**Last Updated**: January 2026

---

## Purpose

This directory contains all planning artifacts for the UI-Uplift project, which is productionalizing the Armor-Dash POC and integrating it with the Nexus platform via a pizza menu architecture.

---

## Contents

| Document | Description | Priority |
|----------|-------------|----------|
| [17-ux-requirements.md](./17-ux-requirements.md) | UX requirements including onboarding tours, tooltips, drill-through | HIGH |
| [18-api-developer-experience.md](./18-api-developer-experience.md) | API DX spec for developer.armor.com, api.armor.com, mcp.armor.com | HIGH |
| [19-openapi-specification.md](./19-openapi-specification.md) | Complete OpenAPI 3.1 specification for Armor Platform API | HIGH |
| [20-mcp-server-specification.md](./20-mcp-server-specification.md) | MCP server specification with multi-app pizza menu architecture | HIGH |
| [21-armor-dash-productionalization.md](./21-armor-dash-productionalization.md) | **MASTER DOC** - Complete code analysis and productionalization requirements | CRITICAL |

---

## Key Findings Summary

### Armor-Dash POC Statistics

| Metric | Value |
|--------|-------|
| Source Files | 235 |
| API Endpoints | 40 |
| Database Models | 12 |
| Connectors | 46 |
| Dashboard Types | 7 |
| Widget Types | 9 |
| Technology | Next.js 15, React 19, TypeScript |

### Critical Mock Data (Must Replace)

| File | Lines | Priority |
|------|-------|----------|
| `lib/mock-data.ts` | 643 | CRITICAL |
| `prisma/seed.ts` | 408 | CRITICAL |
| `lib/data-governance-mock.ts` | 569 | CRITICAL |

### Connector Status

| Status | Count |
|--------|-------|
| Complete | 12 |
| Partial | 20 |
| Stub | 6 |
| Generic Base | 8 |

---

## Diagrams

### Architecture Diagrams (Mermaid)

All diagrams are embedded inline in [21-armor-dash-productionalization.md](./21-armor-dash-productionalization.md):

| Diagram | Type | Purpose |
|---------|------|---------|
| Data Flow | Flowchart | Shows data fetching from UI to connectors |
| Component Hierarchy | Flowchart | Complete React component tree |
| Connector Integration | Sequence | Smart routing between connector and mock data |
| Authentication | Flowchart | Login and session management flow |

### Connector Catalog (Referenced)

See [01-connector-catalog.md](../diagrams/integrations/01-connector-catalog.md) for full connector architecture diagrams.

---

## Related Sections

- [Diagrams](../diagrams/) - Mermaid and architecture diagrams
- [Armor-Dash Submodule](../../submodules/armor-dash/) - POC codebase
- [Platform Submodule](../../submodules/platform/) - Nexus platform

---

## Mapping to Argus Documentation Standards

When restructuring to full Argus compliance, map these artifacts as follows:

| Current Artifact | Argus Location | Argus Section |
|-----------------|----------------|---------------|
| 17-ux-requirements.md | `docs/10-design/ux-requirements.md` | Design & UX |
| 18-api-developer-experience.md | `docs/05-api/developer-experience.md` | API Reference |
| 19-openapi-specification.md | `docs/05-api/openapi-spec.yaml` | API Reference |
| 20-mcp-server-specification.md | `docs/04-components/mcp-server.md` | Components |
| 21-armor-dash-productionalization.md | `docs/03-architecture/armor-dash-analysis.md` | Architecture |

---

## Next Steps

1. **Security (BLOCKING)**: Remove hardcoded password `Armor@2025!`
2. **Data Integration**: Replace mock data with connector routing
3. **Infrastructure**: Implement background job queue for sync
4. **Documentation**: Restructure per Argus numbered directory pattern

See [21-armor-dash-productionalization.md](./21-armor-dash-productionalization.md) Section 7 for complete productionalization checklist.
