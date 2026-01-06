# Integration Diagrams - Nexus UI Platform

This directory contains diagrams documenting the 45+ external security tool integrations (connectors) for the Nexus UI platform.

## Diagram Index

### 1. [Connector Catalog](./01-connector-catalog.md)
**Purpose:** Document all available connectors and their data flow patterns

**Scope:** Connector categories → Architecture → Data flow → Unified data model → Error handling

**Connector Categories:**

| Category | Count | Key Vendors |
|----------|-------|-------------|
| EDR/XDR | 5 | CrowdStrike, Defender, SentinelOne, Carbon Black, Cortex XDR |
| SIEM/SOAR | 5 | Splunk, Sentinel, QRadar, Sumo Logic, Elastic SIEM |
| Vulnerability | 5 | Tenable, Qualys, Rapid7, Nessus, Snyk |
| Cloud Security | 5 | AWS Security Hub, Azure Security, GCP, Prisma, Wiz |
| Identity | 5 | Okta, Azure AD, OneLogin, Ping Identity, CyberArk |
| Compliance | 5 | ServiceNow GRC, OneTrust, Vanta, Drata, Tugboat |
| + Others | 15+ | Network, email, endpoint, threat intel, etc. |

**Key Concepts:**
- **Adapters:** Vendor-specific API integration modules
- **Normalizer:** Transforms vendor data to unified schema
- **Deduplicator:** Prevents duplicate records across sources
- **Enricher:** Adds context (geo, threat intel, risk scores)
- **Queue (SQS):** Async processing for reliability

**Sync Configuration:**
| Setting | Default | Description |
|---------|---------|-------------|
| frequency | 5 min | Incremental sync interval |
| fullSyncFrequency | 24 hours | Complete data refresh |
| batchSize | 1000 | Records per batch |
| timeout | 60s | API call timeout |

**Error Handling:**
- 401 → Refresh token, retry
- 429 → Exponential backoff
- 500 → Retry 3x, then mark unhealthy
- Timeout → Retry with longer timeout

**Use Cases:**
- Adding new connector types
- Debugging sync failures
- Understanding data normalization
- Planning connector capacity

---

## Connector Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                          │
│  CrowdStrike │ Tenable │ AWS │ Splunk │ Okta │ ... (45+)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST/GraphQL APIs
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Connector Service                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Adapter Layer                           │    │
│  │  CrowdStrike │ Tenable │ AWS │ ... (per-vendor)     │    │
│  └──────────────────────────┬──────────────────────────┘    │
│                             ▼                                │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  Normalizer  │ Deduplicator │   Enricher   │             │
│  │  (Schema)    │   (Hash)     │  (Context)   │             │
│  └──────────────┴──────────────┴──────────────┘             │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│     SQS Queue → PostgreSQL → Redis Cache → ClickHouse       │
└─────────────────────────────────────────────────────────────┘
```

---

## Unified Data Model

### Core Entities

| Entity | Description | Key Fields |
|--------|-------------|------------|
| Finding | Security issue from any source | id, source, severity, title, assets, timestamps |
| Asset | Device/resource being monitored | id, hostname, ip, tags, type, os |
| Alert | Aggregated findings requiring action | id, source, severity, status, findings[], assets[] |

### Normalization Rules

| Vendor Severity | Normalized |
|-----------------|------------|
| Critical, P1, Urgent | CRITICAL |
| High, P2, Important | HIGH |
| Medium, P3, Moderate | MEDIUM |
| Low, P4, Minor | LOW |
| Info, P5, Note | INFO |

---

## Monitoring

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Sync Success Rate | >95% | <90% |
| Sync Duration | <60s | >120s |
| Records/Sync | Varies | Sudden drop >50% |
| Error Rate | <5% | >10% |
| Queue Depth | <1000 | >5000 |

### Dashboard Widgets

- Connector status overview (healthy/unhealthy)
- Sync timeline with success/failure
- Records ingested per connector
- Error breakdown by type

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Data Flows | [Connector Sync](../data-flows/02-connector-sync.md) | Detailed sync flow |
| Data Flows | [Multi-Connector](../data-flows/03-multi-connector.md) | Aggregation across connectors |
| Architecture | [System Architecture](../architecture/01-system-architecture.md) | Where connectors fit |

---

## Related Documentation

- [Integration Playbook](../../planning-artifacts/14-integration-playbook.md) - Adding new connectors
- [Productionalization](../../planning-artifacts/21-armor-dash-productionalization.md) - Connector status details
- [API Specification](../../planning-artifacts/05-api-specification.md) - Connector API endpoints

---

Last Updated: 2026-01-04
Maintained By: Integration Team
