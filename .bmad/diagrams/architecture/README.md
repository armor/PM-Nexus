# Architecture Diagrams - Nexus UI Platform

This directory contains high-level architecture diagrams showing the overall system design and technology alignment strategy for the Nexus UI security platform.

## Diagram Index

### 1. [System Architecture](./01-system-architecture.md)
**Purpose:** Understand the complete platform architecture from client to data layer

**Scope:** Client Layer → CDN/Edge → Load Balancing → Kubernetes Services → Data Layer → External Integrations

**Key Components:**
- **Client Layer:** Web browser, mobile browser, MCP clients (Claude Code)
- **CDN & Edge:** CloudFront CDN, WAF/DDoS protection
- **Kubernetes (EKS):** Kong Gateway, Frontend (Next.js 15), API services (Fastify), Workers, MCP servers
- **Data Layer:** PostgreSQL (RDS), Redis (ElastiCache), OpenSearch, S3
- **Integrations:** 45+ security connectors, cloud providers, identity providers

**Use Cases:**
- Understanding full system topology
- Planning capacity and scaling
- Debugging cross-service issues
- Onboarding new team members

---

### 2. [Platform Alignment](./02-platform-alignment.md)
**Purpose:** Visualize the migration path from POC (Armor-Dash) to production Platform

**Scope:** Current POC state → Migration strategy → Target production architecture

**Key Concepts:**
- Component reusability strategy
- Technology stack alignment
- Data migration approach
- Feature parity tracking

**Use Cases:**
- Planning migration sprints
- Identifying reusable components
- Tracking alignment progress
- Stakeholder communication

---

### 3. [MCP Integration Architecture](./03-mcp-integration.md)
**Purpose:** Document the Model Context Protocol integration for AI assistant access

**Scope:** AI Clients → MCP Server → Authentication → Tools/Resources/Prompts → Platform APIs

**Key Components:**
- **AI Clients:** Claude Code, Claude Web, Custom Agents
- **MCP Server:** Protocol handler, tool registry, resource registry
- **Authentication:** OAuth2 client credentials, RBAC
- **Tools:** 35+ tools across Armor-Dash, Nexus, and shared categories
- **Resources:** Dashboards, configuration, documentation
- **Prompts:** Security analysis, remediation, reporting templates

**Use Cases:**
- Understanding MCP integration architecture
- Implementing new MCP tools
- Debugging AI assistant issues
- Security review of MCP access

---

## Architecture Principles

### Design Principles

| Principle | Description |
|-----------|-------------|
| **12-Factor App** | Stateless services, config in environment, disposable processes |
| **Microservices** | Independent deployment, bounded contexts, API contracts |
| **Infrastructure as Code** | Terraform for AWS, Helm for Kubernetes |
| **Defense in Depth** | Multiple security layers (WAF, Auth, RBAC, encryption) |
| **Observability First** | SigNoz for traces, logs, metrics in one platform |

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | Next.js 15, React 19 | SSR, RSC, Platform alignment |
| API | Fastify, Node.js | Performance, TypeScript support |
| Gateway | Kong | Rate limiting, auth, plugins |
| Database | PostgreSQL | ACID compliance, JSON support |
| Cache | Redis | Session, query cache, pub/sub |
| Search | OpenSearch | Log aggregation, full-text |
| Queue | SQS/SNS | Managed, scalable, reliable |
| Container | EKS | Managed Kubernetes, AWS native |

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Data Flows | [Dashboard Request](../data-flows/01-dashboard-request.md) | Shows request flow through architecture |
| Data Flows | [Connector Sync](../data-flows/02-connector-sync.md) | Shows integration layer in action |
| Security | [Auth Flow](../security/01-auth-flow.md) | Details authentication within architecture |
| Components | [Dashboard Hierarchy](../components/01-dashboard-hierarchy.md) | Frontend component structure |

---

## Related Documentation

- [Architecture Document](../../planning-artifacts/nexus-architecture-document.md) - Detailed architecture decisions
- [POC Migration](../../planning-artifacts/15-poc-migration-architecture.md) - Migration strategy
- [Operations Runbook](../../planning-artifacts/09-operations-runbook.md) - Operational procedures

---

Last Updated: 2026-01-04
Maintained By: Architecture Team
