# Nexus UI Uplift - Extended PRD

> **Extended From:** [Confluence - PDM Space](https://armor-defense.atlassian.net/wiki/spaces/PDM/pages/5015044104/Nexus+UI+Uplift)
> **Version:** 2.0 (Extended)
> **Last Updated:** 2026-01-03
> **Status:** Draft

---

## Document Suite Overview

This extended PRD is part of a comprehensive document suite:

| Document | Purpose | Status |
|----------|---------|--------|
| **Extended PRD** (this document) | Product requirements with technical depth | In Progress |
| Architecture Document | AWS/K8s infrastructure, API layer design | Pending |
| UX/Design Specifications | Component library, design system | Pending |
| GTM Strategy | Launch, adoption, AMP sunset execution | Pending |
| Training Materials | User guides, admin docs, video scripts | Pending |

---

## 1. Executive Summary

Nexus UI Uplift is a platform-wide initiative to make Nexus **GTM-ready and capable of fully replacing AMP** as Armor's primary customer platform by the end of Q1.

### Critical Extension: POC to Production

**The current Armor-Dash codebase is a Proof of Concept (POC).** This extended PRD addresses the transformation required to deliver a production-grade platform:

- **Frontend Layer**: Evolved from Armor-Dash POC patterns (Next.js 15, TypeScript, Tailwind)
- **API Layer**: New production-grade backend services (required)
- **Infrastructure**: AWS/Kubernetes deployment with enterprise SLAs
- **Data Layer**: Proper persistence, caching, and security

This initiative focuses on **stability, consistency, usability, and enterprise-grade presentation**, ensuring Nexus clearly communicates security risk, compliance posture, and Armor-delivered value to both operational users and executives.

---

## 2. Vision and North Star

**Nexus functions as the single, trusted platform customers rely on daily**, replacing AMP without loss of capability, clarity, or confidence.

### Technical North Star

- **API-First Architecture**: All frontend features backed by versioned, documented APIs
- **Cloud-Native**: Fully containerized, Kubernetes-orchestrated, AWS-hosted
- **Observable**: Full telemetry, tracing, and monitoring from day one
- **Secure by Design**: Zero-trust architecture, proper AuthN/AuthZ
- **Scalable**: Handle enterprise customer loads without degradation

### Product North Star

- Nexus must be stable, predictable, and usable at scale
- Metrics must be explainable, consistent, and defensible
- Executive-level value must be immediately visible
- Operational detail must roll up cleanly into business outcomes
- The platform must look and behave like an enterprise product
- Nexus must communicate **outcomes and value**, not just activity

---

## 3. Problem Statement

### Current State Analysis

**Armor-Dash POC Gaps:**

| Area | POC State | Production Required |
|------|-----------|---------------------|
| **API Layer** | Direct frontend calls, mock data | Dedicated backend services |
| **Authentication** | Supabase-only | Enterprise SSO, RBAC, MFA |
| **Data Persistence** | Prisma/Supabase direct | API-mediated with caching |
| **Infrastructure** | Local/dev deployment | AWS/K8s production cluster |
| **Observability** | Console logging | APM, tracing, structured logs |
| **Security** | Basic validation | WAF, secrets management, scanning |

**UX Gaps (from original PRD):**

- Inconsistent navigation and fragmented interactions
- Unclear metric context and visual maturity
- MVP-level presentation vs enterprise expectations
- Executives cannot quickly answer fundamental questions

### Risk Statement

With AMP scheduled for sunset in Q1, any lack of readiness, clarity, or stability in Nexus presents material risk to customer adoption, confidence, and renewals.

---

## 4. Objectives

### Product Objectives (Original)

1. Make Nexus GTM-ready and capable of fully replacing AMP
2. Establish Nexus as the trusted system of record for security risk and value
3. Enable executives to quickly understand ROI, risk posture, and outcomes
4. Ensure platform-wide consistency in behavior, navigation, and components
5. Improve usability so customers can self-serve without guidance
6. Support AMP sunset with equal or greater value delivered in Nexus
7. Align Nexus presentation with Armor's enterprise positioning
8. Support renewals and upsell by clearly communicating value

### Technical Objectives (Extended)

1. **API Layer**: Implement production backend services for all frontend features
2. **Infrastructure**: Deploy on AWS/K8s with proper CI/CD, scaling, monitoring
3. **Data Architecture**: Design proper data flow with caching, persistence, APIs
4. **Security**: Implement enterprise-grade AuthN/AuthZ, secrets management
5. **Observability**: Full APM, distributed tracing, alerting
6. **Performance**: Meet enterprise SLAs (<200ms P95 API response times)
7. **Reliability**: 99.9% uptime target with proper failover

---

## 5. Scope

### In Scope (Q1)

#### Product Scope (Original)
- Platform stability and removal of high-severity UX and functional bugs
- Navigation consistency and predictable routing
- Standardized component usage and interaction patterns
- Usability improvements across core Nexus workflows
- Executive-friendly metrics and value communication
- Look and feel updates aligned with Armor's enterprise brand
- Metric clarity, definitions, and context (not net-new analytics)
- Fully functional demo accounts with guardrails

#### Technical Scope (Extended)

**API Layer Development:**
- RESTful API services for all 7 dashboards
- API gateway with rate limiting, authentication
- Service-to-service communication patterns
- API versioning strategy (v1 launch)

**Infrastructure:**
- AWS EKS cluster configuration
- Helm charts for all services
- CI/CD pipelines (GitHub Actions → AWS)
- Environment promotion (dev → staging → prod)

**Data Layer:**
- API contracts for 45+ data connectors
- Caching strategy (Redis/ElastiCache)
- Database schema finalization
- Data migration from POC patterns

**Security:**
- AWS IAM policies and roles
- Kubernetes RBAC
- Secrets management (AWS Secrets Manager)
- Network policies and security groups

**Observability:**
- CloudWatch/Datadog integration
- Distributed tracing (X-Ray or Jaeger)
- Custom metrics and dashboards
- Alerting rules and runbooks

### Out of Scope (Q1)

- New security detection, prevention, or SOC capabilities
- Major backend architectural refactors beyond API layer
- Net-new data sources
- Fully customizable reporting or AI-driven UX
- Deep automation or action frameworks
- Multi-region deployment
- Self-service infrastructure provisioning

---

## 6. Technical Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                                  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Amazon EKS Cluster                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │   Nexus     │  │    API      │  │   Worker    │          │   │
│  │  │  Frontend   │  │  Services   │  │  Services   │          │   │
│  │  │  (Next.js)  │  │  (Node/Go)  │  │  (Jobs)     │          │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │   │
│  │         │                │                │                  │   │
│  │         └────────────────┼────────────────┘                  │   │
│  │                          │                                   │   │
│  │  ┌───────────────────────▼───────────────────────────┐      │   │
│  │  │              API Gateway / Ingress                 │      │   │
│  │  └───────────────────────┬───────────────────────────┘      │   │
│  └──────────────────────────┼───────────────────────────────────┘   │
│                             │                                        │
│  ┌──────────────────────────▼───────────────────────────────────┐   │
│  │                    Data Layer                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │
│  │  │    RDS      │  │ ElastiCache │  │     S3      │           │   │
│  │  │ (PostgreSQL)│  │   (Redis)   │  │  (Storage)  │           │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              External Integrations (45+ Connectors)           │   │
│  │  AWS Services │ Azure │ GCP │ Security Tools │ Compliance     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| **Frontend** | Next.js 15, React 19, TypeScript | From Armor-Dash patterns |
| **UI Framework** | Tailwind CSS, shadcn/ui | Component library |
| **API Gateway** | Kong / AWS API Gateway | Rate limiting, auth |
| **Backend Services** | Node.js / Go | Service-specific choice |
| **Database** | PostgreSQL (RDS) | Primary data store |
| **Cache** | Redis (ElastiCache) | Session, query caching |
| **Search** | OpenSearch | Log and security search |
| **Queue** | SQS / SNS | Async job processing |
| **Storage** | S3 | Reports, exports, assets |
| **Container** | Docker | Standardized packaging |
| **Orchestration** | Kubernetes (EKS) | Production workloads |
| **CI/CD** | GitHub Actions | Pipeline automation |
| **Monitoring** | CloudWatch + Datadog | Full observability |
| **Secrets** | AWS Secrets Manager | Credential management |

---

## 7. Dashboard Requirements

Based on Armor-Dash POC analysis, the following dashboards require API backing:

### 7.1 Main Dashboard (Executive View)
- **Purpose**: High-level security posture, key metrics
- **API Requirements**: Aggregated metrics, trend data, alert summaries
- **Data Sources**: All security tools, compliance engines

### 7.2 Attack Surface Discovery
- **Purpose**: External attack surface visibility
- **API Requirements**: Asset enumeration, risk scoring, change detection
- **Data Sources**: External scanners, DNS, certificate transparency

### 7.3 Security Operations (SecOps)
- **Purpose**: SOC workflow, incident management
- **API Requirements**: Alert ingestion, case management, response actions
- **Data Sources**: SIEM, EDR, ticketing systems

### 7.4 Security Posture Management
- **Purpose**: Cloud security posture, misconfigurations
- **API Requirements**: Cloud asset inventory, policy violations, remediation
- **Data Sources**: AWS, Azure, GCP security APIs

### 7.5 Vulnerability Management
- **Purpose**: Vulnerability tracking and prioritization
- **API Requirements**: Scan results, CVSS enrichment, SLA tracking
- **Data Sources**: Vulnerability scanners, asset inventory

### 7.6 Compliance Management
- **Purpose**: Compliance framework tracking
- **API Requirements**: Control mapping, evidence collection, gap analysis
- **Data Sources**: Policy engines, audit logs, documentation

### 7.7 Armor Assist
- **Purpose**: AI-powered security assistance
- **API Requirements**: Conversational AI, context retrieval, action execution
- **Data Sources**: All platform data, knowledge base

---

## 8. API Layer Specification

### 8.1 API Design Principles

1. **RESTful conventions** with consistent resource naming
2. **Versioned endpoints** (`/api/v1/...`)
3. **JSON:API or similar** standard response format
4. **Pagination** for all list endpoints
5. **Filtering and sorting** standardized parameters
6. **Rate limiting** per tenant and globally
7. **Idempotency** for all mutating operations

### 8.2 Core API Domains

| Domain | Endpoints | Priority |
|--------|-----------|----------|
| **Auth** | `/api/v1/auth/*` | P0 |
| **Users** | `/api/v1/users/*` | P0 |
| **Organizations** | `/api/v1/orgs/*` | P0 |
| **Assets** | `/api/v1/assets/*` | P1 |
| **Alerts** | `/api/v1/alerts/*` | P1 |
| **Vulnerabilities** | `/api/v1/vulns/*` | P1 |
| **Compliance** | `/api/v1/compliance/*` | P1 |
| **Reports** | `/api/v1/reports/*` | P2 |
| **Integrations** | `/api/v1/integrations/*` | P2 |
| **Metrics** | `/api/v1/metrics/*` | P1 |

### 8.3 Authentication & Authorization

- **Primary**: JWT tokens with refresh mechanism
- **Enterprise**: SAML/OIDC SSO integration
- **RBAC**: Role-based access with tenant isolation
- **API Keys**: For programmatic access
- **MFA**: Required for admin operations

---

## 9. Phasing

### Phase 1: Foundation (Weeks 1-4)
- AWS/EKS infrastructure setup
- CI/CD pipeline establishment
- Core API framework and auth
- Database and cache provisioning
- Observability stack deployment

### Phase 2: Core APIs (Weeks 5-8)
- Auth and user management APIs
- Organization and tenant APIs
- Asset management APIs
- Alert and incident APIs
- Frontend integration with new APIs

### Phase 3: Dashboard APIs (Weeks 9-12)
- Dashboard-specific API endpoints
- Metrics aggregation services
- Compliance and reporting APIs
- Performance optimization
- Load testing and tuning

### Phase 4: Hardening (Weeks 13-14)
- Security audit and remediation
- Performance optimization
- Documentation completion
- Demo environment finalization
- AMP sunset preparation

---

## 10. Success Criteria

### Primary
- **AMP usage drops to zero by end of Q1**

### Technical Success Criteria
- All 7 dashboards fully backed by production APIs
- P95 API response time < 200ms
- 99.9% uptime over trailing 30 days
- Zero critical security findings in audit
- Full observability with <5 min MTTD

### Product Success Criteria
- Nexus achieves full functional parity with AMP
- Demo accounts fully functional for sales
- Sales and CS can demo without scripts
- Customer NPS maintained or improved
- Zero escalations due to platform instability

---

## 11. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API development takes longer than planned | Medium | High | Start API work immediately, parallel tracks |
| Infrastructure complexity delays | Medium | Medium | Use proven patterns, avoid over-engineering |
| Data migration issues | Low | High | Early testing, rollback procedures |
| Performance doesn't meet SLAs | Medium | High | Performance testing from week 1 |
| Security vulnerabilities discovered late | Low | Critical | Continuous security scanning, early audits |
| Team bandwidth constraints | Medium | High | Clear prioritization, scope management |

---

## 12. Dependencies

### Internal Dependencies
- DevOps team for AWS/K8s infrastructure
- Security team for compliance and audit
- Data team for connector APIs
- Design team for UX specifications

### External Dependencies
- AWS account and permissions
- Third-party API access (45+ integrations)
- SSO provider configuration (customer-specific)

---

## 13. Open Questions

1. **API Technology Choice**: Node.js vs Go for backend services?
2. **Database Strategy**: Single DB or service-specific databases?
3. **Cache Strategy**: Where to implement caching (API vs gateway)?
4. **Feature Flags**: How to manage gradual rollout?
5. **Multi-tenancy**: Logical or physical isolation?

---

## Appendix A: Armor-Dash POC Analysis Summary

The Armor-Dash POC provides valuable patterns to evolve:

**Strengths to Preserve:**
- Component architecture (shadcn/ui, Tailwind)
- Dashboard layout patterns
- Chart and visualization components (Recharts)
- TypeScript type definitions
- Responsive design patterns

**Gaps to Address:**
- Replace direct database calls with API layer
- Implement proper authentication flow
- Add error handling and retry logic
- Implement proper state management
- Add loading states and optimistic updates

---

## Appendix B: Related Documents

- [Original Confluence PRD](https://armor-defense.atlassian.net/wiki/spaces/PDM/pages/5015044104/Nexus+UI+Uplift)
- Architecture Document (pending)
- UX/Design Specifications (pending)
- GTM Strategy (pending)
- Training Materials (pending)

---

*This document is maintained by Product and Engineering. For questions, contact the Nexus UI Uplift project team.*
