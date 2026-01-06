# Nexus Platform Architecture Document

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Related PRD:** [Nexus UI Uplift Extended PRD](./nexus-ui-uplift-extended-prd.md)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [System Architecture](#3-system-architecture)
4. [AWS Infrastructure](#4-aws-infrastructure)
5. [Kubernetes Architecture](#5-kubernetes-architecture)
6. [API Layer Design](#6-api-layer-design)
7. [Data Architecture](#7-data-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Observability](#9-observability)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Disaster Recovery](#11-disaster-recovery)
12. [Performance Requirements](#12-performance-requirements)
13. [Migration Strategy](#13-migration-strategy)

---

## 1. Overview

### 1.1 Purpose

This document defines the technical architecture for the Nexus platform, transitioning from the Armor-Dash POC to a production-grade system deployed on AWS with Kubernetes orchestration.

### 1.2 Scope

- Frontend application (Next.js)
- API layer (backend services)
- Data persistence and caching
- Authentication and authorization
- Infrastructure and deployment
- Monitoring and observability
- Security controls

### 1.3 Key Stakeholders

- Engineering Team
- DevOps/Platform Team
- Security Team
- Product Team

---

## 2. Architecture Principles

### 2.1 Core Principles

| Principle | Description |
|-----------|-------------|
| **API-First** | All data access through versioned APIs; no direct database access from frontend |
| **Cloud-Native** | Designed for Kubernetes; stateless services with external state management |
| **Security by Design** | Zero-trust networking; defense in depth; encrypted everything |
| **Observable** | Full telemetry from day one; every request traceable end-to-end |
| **Scalable** | Horizontal scaling for all services; no single points of failure |
| **Maintainable** | Clear boundaries; consistent patterns; comprehensive documentation |

### 2.2 Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Container Orchestration | AWS EKS | Managed Kubernetes reduces operational burden |
| API Framework | Node.js (Fastify) | Team expertise, TypeScript consistency with frontend |
| Primary Database | PostgreSQL (RDS) | ACID compliance, JSON support, familiar tooling |
| Cache Layer | Redis (ElastiCache) | Session management, query caching, pub/sub |
| Message Queue | Amazon SQS | Managed, scalable, integrates with AWS ecosystem |
| API Gateway | Kong on EKS | Feature-rich, Kubernetes-native, extensible |
| Secrets Management | AWS Secrets Manager | Native integration, rotation support |
| Observability | Datadog | Unified APM, logs, metrics, traces |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
                                    ┌──────────────────────┐
                                    │   CloudFront CDN     │
                                    │   (Static Assets)    │
                                    └──────────┬───────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    │              AWS VPC (Production)                   │
                    │                          │                          │
                    │     ┌────────────────────▼───────────────────┐     │
                    │     │         Application Load Balancer       │     │
                    │     │              (Public Subnet)            │     │
                    │     └────────────────────┬───────────────────┘     │
                    │                          │                          │
                    │ ┌────────────────────────▼────────────────────────┐│
                    │ │                 EKS Cluster                     ││
                    │ │  ┌─────────────────────────────────────────┐   ││
                    │ │  │            Ingress (Kong)                │   ││
                    │ │  └─────────────────┬───────────────────────┘   ││
                    │ │                    │                            ││
                    │ │  ┌─────────────────▼───────────────────────┐   ││
                    │ │  │              API Gateway                 │   ││
                    │ │  │  (Rate Limiting, Auth, Routing)          │   ││
                    │ │  └─────────────────┬───────────────────────┘   ││
                    │ │                    │                            ││
                    │ │  ┌─────────────────┼───────────────────────┐   ││
                    │ │  │                 │                       │   ││
                    │ │  ▼                 ▼                       ▼   ││
                    │ │ ┌────────┐   ┌──────────┐   ┌──────────────┐   ││
                    │ │ │Frontend│   │   API    │   │   Worker     │   ││
                    │ │ │Service │   │ Services │   │   Services   │   ││
                    │ │ │(Next.js│   │(Node.js) │   │ (Background) │   ││
                    │ │ └───┬────┘   └────┬─────┘   └──────┬───────┘   ││
                    │ │     │             │                │           ││
                    │ └─────┼─────────────┼────────────────┼───────────┘│
                    │       │             │                │            │
                    │ ┌─────▼─────────────▼────────────────▼───────────┐│
                    │ │              Private Subnet                     ││
                    │ │  ┌─────────┐  ┌─────────────┐  ┌─────────────┐ ││
                    │ │  │   RDS   │  │ ElastiCache │  │ OpenSearch  │ ││
                    │ │  │PostgreSQL│  │   (Redis)   │  │  (Logs)    │ ││
                    │ │  └─────────┘  └─────────────┘  └─────────────┘ ││
                    │ └────────────────────────────────────────────────┘│
                    │                                                    │
                    └────────────────────────────────────────────────────┘
```

### 3.2 Service Catalog

| Service | Type | Technology | Replicas | Purpose |
|---------|------|------------|----------|---------|
| nexus-frontend | Web | Next.js 15 | 2-4 | Server-side rendered UI |
| nexus-api-gateway | Gateway | Kong | 2 | Auth, rate limiting, routing |
| nexus-auth-service | API | Node.js/Fastify | 2-3 | Authentication, authorization |
| nexus-core-api | API | Node.js/Fastify | 3-5 | Core platform APIs |
| nexus-metrics-api | API | Node.js/Fastify | 2-3 | Metrics aggregation |
| nexus-connector-service | Worker | Node.js | 2-4 | External integrations |
| nexus-job-runner | Worker | Node.js | 2 | Scheduled tasks |

---

## 4. AWS Infrastructure

### 4.1 AWS Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **EKS** | Kubernetes orchestration | v1.28+, managed node groups |
| **RDS** | PostgreSQL database | Multi-AZ, r6g.large |
| **ElastiCache** | Redis caching | Cluster mode, r6g.large |
| **S3** | Object storage | Standard, versioning enabled |
| **CloudFront** | CDN | Global edge locations |
| **ALB** | Load balancing | Application load balancer |
| **Route 53** | DNS | Health checks, failover |
| **ACM** | TLS certificates | Auto-renewal |
| **Secrets Manager** | Secrets | Rotation enabled |
| **KMS** | Encryption keys | CMK for data encryption |
| **SQS** | Message queue | Standard queues |
| **SNS** | Notifications | Alert distribution |
| **CloudWatch** | Logging/Metrics | Retention 30 days |
| **X-Ray** | Distributed tracing | Sampling 10% |

### 4.2 VPC Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VPC: 10.0.0.0/16                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Availability Zone A                       ││
│  │  ┌─────────────────┐  ┌─────────────────┐                   ││
│  │  │ Public Subnet   │  │ Private Subnet  │                   ││
│  │  │ 10.0.1.0/24     │  │ 10.0.11.0/24    │                   ││
│  │  │                 │  │                 │                   ││
│  │  │ - NAT Gateway   │  │ - EKS Nodes     │                   ││
│  │  │ - ALB           │  │ - RDS Primary   │                   ││
│  │  │                 │  │ - ElastiCache   │                   ││
│  │  └─────────────────┘  └─────────────────┘                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Availability Zone B                       ││
│  │  ┌─────────────────┐  ┌─────────────────┐                   ││
│  │  │ Public Subnet   │  │ Private Subnet  │                   ││
│  │  │ 10.0.2.0/24     │  │ 10.0.12.0/24    │                   ││
│  │  │                 │  │                 │                   ││
│  │  │ - NAT Gateway   │  │ - EKS Nodes     │                   ││
│  │  │ - ALB           │  │ - RDS Standby   │                   ││
│  │  │                 │  │ - ElastiCache   │                   ││
│  │  └─────────────────┘  └─────────────────┘                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Availability Zone C                       ││
│  │  ┌─────────────────┐  ┌─────────────────┐                   ││
│  │  │ Public Subnet   │  │ Private Subnet  │                   ││
│  │  │ 10.0.3.0/24     │  │ 10.0.13.0/24    │                   ││
│  │  │                 │  │                 │                   ││
│  │  │ - NAT Gateway   │  │ - EKS Nodes     │                   ││
│  │  │                 │  │                 │                   ││
│  │  └─────────────────┘  └─────────────────┘                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Resource Sizing (Initial)

| Resource | Environment | Size | Notes |
|----------|-------------|------|-------|
| EKS Nodes | Production | m6i.xlarge (4 vCPU, 16GB) | 3-6 nodes |
| EKS Nodes | Staging | m6i.large (2 vCPU, 8GB) | 2-3 nodes |
| RDS | Production | db.r6g.large | Multi-AZ |
| RDS | Staging | db.t4g.medium | Single-AZ |
| ElastiCache | Production | cache.r6g.large | 2 nodes |
| ElastiCache | Staging | cache.t4g.medium | 1 node |

---

## 5. Kubernetes Architecture

### 5.1 Namespace Strategy

```
├── nexus-prod          # Production workloads
├── nexus-staging       # Staging environment
├── nexus-system        # Platform components (ingress, monitoring)
├── cert-manager        # TLS certificate management
└── monitoring          # Datadog, Prometheus
```

### 5.2 Deployment Patterns

**Standard Service Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-core-api
  namespace: nexus-prod
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: nexus-core-api
        image: nexus/core-api:v1.0.0
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health/live
            port: 3000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nexus-secrets
              key: database-url
```

### 5.3 Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexus-core-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nexus-core-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 5.4 Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nexus-api-policy
  namespace: nexus-prod
spec:
  podSelector:
    matchLabels:
      app: nexus-core-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nexus-api-gateway
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: nexus-postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## 6. API Layer Design

### 6.1 API Structure

```
/api/v1/
├── auth/
│   ├── POST   /login
│   ├── POST   /logout
│   ├── POST   /refresh
│   └── GET    /me
├── users/
│   ├── GET    /
│   ├── GET    /:id
│   ├── POST   /
│   ├── PUT    /:id
│   └── DELETE /:id
├── organizations/
│   ├── GET    /
│   ├── GET    /:id
│   └── PUT    /:id
├── assets/
│   ├── GET    /
│   ├── GET    /:id
│   ├── GET    /search
│   └── GET    /stats
├── alerts/
│   ├── GET    /
│   ├── GET    /:id
│   ├── PUT    /:id/status
│   ├── POST   /:id/acknowledge
│   └── GET    /stats
├── vulnerabilities/
│   ├── GET    /
│   ├── GET    /:id
│   └── GET    /stats
├── compliance/
│   ├── GET    /frameworks
│   ├── GET    /controls
│   └── GET    /posture
├── metrics/
│   ├── GET    /dashboard
│   ├── GET    /trends
│   └── GET    /custom
├── reports/
│   ├── GET    /
│   ├── POST   /generate
│   └── GET    /:id/download
└── integrations/
    ├── GET    /connectors
    ├── GET    /:id/status
    └── POST   /:id/sync
```

### 6.2 Request/Response Format

**Standard Request Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Request-ID: <uuid>
X-Tenant-ID: <tenant_id>
```

**Standard Response Format:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5
    }
  },
  "meta": {
    "requestId": "uuid",
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "requestId": "uuid",
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

### 6.3 Rate Limiting

| Tier | Requests/Minute | Burst |
|------|-----------------|-------|
| Standard | 1000 | 100 |
| Enterprise | 5000 | 500 |
| Internal | Unlimited | N/A |

---

## 7. Data Architecture

### 7.1 Database Schema (Core Tables)

```sql
-- Organizations (Tenants)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    settings JSONB DEFAULT '{}',
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, email)
);

-- Assets
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    external_id VARCHAR(255),
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    risk_score INTEGER,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    asset_id UUID REFERENCES assets(id),
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Vulnerabilities
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    asset_id UUID REFERENCES assets(id),
    cve_id VARCHAR(50),
    severity VARCHAR(20) NOT NULL,
    cvss_score DECIMAL(3,1),
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    remediation TEXT,
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_assets_org ON assets(organization_id);
CREATE INDEX idx_assets_type ON assets(organization_id, type);
CREATE INDEX idx_alerts_org_status ON alerts(organization_id, status);
CREATE INDEX idx_alerts_severity ON alerts(organization_id, severity);
CREATE INDEX idx_vulns_org_status ON vulnerabilities(organization_id, status);
CREATE INDEX idx_vulns_severity ON vulnerabilities(organization_id, severity);
```

### 7.2 Caching Strategy

| Cache Type | TTL | Use Case |
|------------|-----|----------|
| Session | 24h | User sessions, JWT validation |
| Query | 5m | Dashboard aggregations |
| Reference | 1h | Dropdown values, configurations |
| Rate Limit | 1m | API rate limit counters |

**Redis Key Patterns:**
```
session:{user_id}                    # User session data
cache:dashboard:{org_id}:{widget}    # Dashboard widget data
cache:metrics:{org_id}:{date}        # Daily metrics cache
ratelimit:{api_key}:{endpoint}       # Rate limit counters
```

### 7.3 Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   External  │────▶│  Connector  │────▶│     SQS     │
│   Systems   │     │   Service   │     │    Queue    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │◀───▶│   Core API  │────▶│  PostgreSQL │
│   (Next.js) │     │   Service   │     │     RDS     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │ (Cache/Pub) │
                    └─────────────┘
```

---

## 8. Security Architecture

### 8.1 Authentication Flow

```
┌──────────┐  1. Login Request   ┌─────────────┐
│  Client  │────────────────────▶│ Auth Service│
└────┬─────┘                     └──────┬──────┘
     │                                  │
     │  4. JWT + Refresh Token          │ 2. Validate
     │◀─────────────────────────────────│    Credentials
     │                                  │
     │                                  ▼
     │                           ┌─────────────┐
     │                           │  Identity   │
     │                           │  Provider   │
     │                           │ (SSO/Local) │
     │                           └──────┬──────┘
     │                                  │
     │  5. API Requests                 │ 3. Auth Success
     │     (Bearer Token)               │
     ▼                                  ▼
┌──────────┐                     ┌─────────────┐
│   API    │────────────────────▶│   Session   │
│  Gateway │  6. Validate Token  │    Store    │
└──────────┘                     │   (Redis)   │
                                 └─────────────┘
```

### 8.2 Authorization Model

**Role-Based Access Control (RBAC):**

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all resources |
| **Manager** | Read/write access, user management |
| **Analyst** | Read/write access to security data |
| **Viewer** | Read-only access |
| **API** | Programmatic access (configurable) |

**Permission Structure:**
```json
{
  "role": "analyst",
  "permissions": [
    "alerts:read",
    "alerts:write",
    "assets:read",
    "vulnerabilities:read",
    "vulnerabilities:write",
    "reports:read",
    "reports:create"
  ]
}
```

### 8.3 Security Controls

| Control | Implementation |
|---------|----------------|
| **TLS Everywhere** | ACM certificates, TLS 1.3 |
| **Encryption at Rest** | RDS encryption, S3 SSE-KMS |
| **Network Isolation** | VPC, security groups, NACLs |
| **WAF** | AWS WAF on ALB |
| **Secrets Management** | AWS Secrets Manager |
| **Audit Logging** | CloudTrail, application logs |
| **Vulnerability Scanning** | Trivy, Snyk |
| **Penetration Testing** | Quarterly assessments |

---

## 9. Observability

### 9.1 Observability Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      Datadog Platform                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    APM      │  │    Logs     │  │   Metrics   │         │
│  │  (Traces)   │  │ (Structured)│  │  (Custom)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│              ┌───────────▼───────────┐                     │
│              │      Dashboards       │                     │
│              │      Alerting         │                     │
│              │      SLO Tracking     │                     │
│              └───────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───┴───┐           ┌─────┴─────┐         ┌────┴────┐
│Frontend│           │   API     │         │ Workers │
│Service │           │ Services  │         │         │
└────────┘           └───────────┘         └─────────┘
```

### 9.2 Key Metrics

**Service Level Indicators (SLIs):**

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API Availability | 99.9% | < 99.5% |
| API Latency (P95) | < 200ms | > 500ms |
| Error Rate | < 0.1% | > 1% |
| Apdex Score | > 0.95 | < 0.90 |

**Business Metrics:**

| Metric | Description |
|--------|-------------|
| Active Users (DAU/MAU) | Platform engagement |
| Alert Response Time | Time to acknowledge |
| Vulnerability Age | Days open by severity |
| Connector Health | Integration status |

### 9.3 Alerting Rules

```yaml
# Critical Alert: API Down
- name: nexus-api-down
  condition: avg(api.availability) < 0.99
  duration: 5m
  severity: critical
  notification:
    - pagerduty
    - slack:#nexus-alerts

# Warning: High Latency
- name: nexus-api-slow
  condition: p95(api.latency) > 500ms
  duration: 10m
  severity: warning
  notification:
    - slack:#nexus-alerts

# Error Rate Spike
- name: nexus-error-rate
  condition: avg(api.error_rate) > 0.01
  duration: 5m
  severity: warning
  notification:
    - slack:#nexus-alerts
```

---

## 10. CI/CD Pipeline

### 10.1 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                                │
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│  │   Lint   │──▶│   Test   │──▶│  Build   │──▶│   Scan   │         │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘         │
│                                                      │               │
│                                                      ▼               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Deploy Pipeline                            │   │
│  │                                                               │   │
│  │   ┌─────────┐     ┌─────────────┐     ┌─────────────┐        │   │
│  │   │   Dev   │────▶│   Staging   │────▶│ Production  │        │   │
│  │   │  (Auto) │     │ (Auto+Test) │     │  (Manual)   │        │   │
│  │   └─────────┘     └─────────────┘     └─────────────┘        │   │
│  │                                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Pipeline Stages

**Stage 1: Validate**
```yaml
- name: Lint
  run: npm run lint
- name: Type Check
  run: npm run typecheck
- name: Unit Tests
  run: npm run test:unit
```

**Stage 2: Build**
```yaml
- name: Build Application
  run: npm run build
- name: Build Docker Image
  run: docker build -t nexus-api:${{ github.sha }}
- name: Push to ECR
  run: docker push $ECR_REPO:${{ github.sha }}
```

**Stage 3: Security Scan**
```yaml
- name: Trivy Scan
  run: trivy image nexus-api:${{ github.sha }}
- name: Snyk Test
  run: snyk test
```

**Stage 4: Deploy**
```yaml
- name: Deploy to Staging
  run: helm upgrade nexus-api ./charts/nexus-api
       --namespace nexus-staging
       --set image.tag=${{ github.sha }}
- name: Integration Tests
  run: npm run test:integration
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: helm upgrade nexus-api ./charts/nexus-api
       --namespace nexus-prod
       --set image.tag=${{ github.sha }}
```

### 10.3 Environment Promotion

| Environment | Trigger | Approval | Tests |
|-------------|---------|----------|-------|
| Development | Push to feature branch | Automatic | Unit |
| Staging | Merge to develop | Automatic | Unit + Integration |
| Production | Merge to main | Manual approval | Full suite |

---

## 11. Disaster Recovery

### 11.1 Backup Strategy

| Resource | Frequency | Retention | Method |
|----------|-----------|-----------|--------|
| RDS Database | Daily | 30 days | Automated snapshots |
| RDS (Point-in-Time) | Continuous | 7 days | Transaction logs |
| S3 Objects | Continuous | Versioned | Cross-region replication |
| Kubernetes Config | Every deploy | 90 days | Git history |
| Secrets | On change | Versioned | Secrets Manager |

### 11.2 Recovery Objectives

| Metric | Target |
|--------|--------|
| **RTO** (Recovery Time Objective) | < 1 hour |
| **RPO** (Recovery Point Objective) | < 15 minutes |

### 11.3 Failover Procedures

**Database Failover:**
1. RDS Multi-AZ automatic failover (< 60 seconds)
2. Application retries with exponential backoff
3. No manual intervention required

**Region Failover (Future):**
1. Route 53 health check failure detected
2. DNS failover to secondary region
3. RDS read replica promoted to primary
4. Application deployed to secondary EKS cluster

---

## 12. Performance Requirements

### 12.1 Response Time SLAs

| Endpoint Type | P50 | P95 | P99 |
|---------------|-----|-----|-----|
| Dashboard API | 50ms | 200ms | 500ms |
| List APIs | 100ms | 300ms | 800ms |
| Search APIs | 150ms | 500ms | 1000ms |
| Report Generation | 2s | 5s | 10s |

### 12.2 Capacity Planning

| Metric | Initial | 6 Months | 12 Months |
|--------|---------|----------|-----------|
| Concurrent Users | 100 | 500 | 1000 |
| API Requests/min | 1000 | 5000 | 10000 |
| Database Size | 50GB | 150GB | 300GB |
| Cache Size | 5GB | 15GB | 30GB |

### 12.3 Load Testing

**Test Scenarios:**
1. Baseline: 100 concurrent users, 5 minute duration
2. Peak: 500 concurrent users, 15 minute duration
3. Stress: Ramp to 1000 users until failure

**Tools:**
- k6 for load testing
- Grafana for visualization
- Automated tests in CI pipeline (staging only)

---

## 13. Migration Strategy

### 13.1 POC to Production Migration

**Phase 1: Infrastructure (Week 1-2)**
- Provision AWS resources (VPC, EKS, RDS)
- Configure networking and security groups
- Deploy base Kubernetes resources
- Set up CI/CD pipelines

**Phase 2: Data Migration (Week 3-4)**
- Create production database schema
- Migrate reference data
- Set up data sync from POC (if applicable)
- Validate data integrity

**Phase 3: Application Migration (Week 5-8)**
- Deploy backend API services
- Migrate frontend to new API layer
- Implement feature flags for gradual rollout
- Run parallel systems during transition

**Phase 4: Cutover (Week 9-10)**
- Final data sync
- DNS cutover
- Decommission POC environment
- Post-migration validation

### 13.2 Rollback Plan

**Criteria for Rollback:**
- Critical functionality broken
- Data integrity issues
- Performance degradation > 50%
- Security vulnerability discovered

**Rollback Steps:**
1. Revert DNS to previous environment
2. Restore database from snapshot
3. Re-deploy previous application version
4. Notify stakeholders

---

## Appendix A: Technology Decision Records

### ADR-001: API Framework Selection

**Decision**: Use Fastify (Node.js) for API services

**Context**: Need to choose between Node.js (Express/Fastify), Go, or Python for backend

**Options Considered**:
1. Express.js - Mature, large ecosystem
2. Fastify - Modern, performant, TypeScript-first
3. Go - High performance, compiled
4. Python/FastAPI - Data science ecosystem

**Decision**: Fastify
- Team has TypeScript expertise (consistent with frontend)
- Excellent performance benchmarks
- Schema-based validation (similar to Zod)
- Easy onboarding for frontend developers

### ADR-002: Database Selection

**Decision**: PostgreSQL on RDS

**Context**: Need reliable, scalable database for platform data

**Options Considered**:
1. PostgreSQL (RDS)
2. MySQL (RDS)
3. DynamoDB
4. CockroachDB

**Decision**: PostgreSQL
- Team experience
- JSONB support for flexible metadata
- Strong ecosystem (Prisma, TypeORM)
- Multi-AZ support on RDS

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **EKS** | Elastic Kubernetes Service |
| **RDS** | Relational Database Service |
| **ALB** | Application Load Balancer |
| **VPC** | Virtual Private Cloud |
| **RBAC** | Role-Based Access Control |
| **APM** | Application Performance Monitoring |
| **SLI/SLO** | Service Level Indicator/Objective |
| **RTO/RPO** | Recovery Time/Point Objective |

---

## Appendix C: Related Diagrams

### Figure 1: System Architecture
*Complete platform architecture from client to data layer.*

> **Diagram:** [System Architecture](../diagrams/architecture/01-system-architecture.md)
>
> Comprehensive view of:
> - Client Layer (Web, Mobile, MCP clients)
> - CDN & Edge (CloudFront, WAF)
> - Kubernetes Services (EKS cluster)
> - Data Layer (PostgreSQL, Redis, OpenSearch)
> - External Integrations

### Figure 2: Platform Alignment
*POC to Platform migration architecture.*

> **Diagram:** [Platform Alignment](../diagrams/architecture/02-platform-alignment.md)
>
> Shows migration path from Armor-Dash POC to Platform-aligned architecture.

### Figure 3: Data Flow Patterns
*Request-response and real-time update flows.*

> **Diagrams:**
> - [Dashboard Request](../diagrams/data-flows/01-dashboard-request.md) - User request lifecycle
> - [Real-Time Updates](../diagrams/data-flows/05-real-time-updates.md) - WebSocket/SSE patterns

---

*This document is maintained by the Platform Engineering team. For questions, contact platform-team@armor.com*
