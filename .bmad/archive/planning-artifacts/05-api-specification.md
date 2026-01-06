# Nexus UI Uplift - API Specification

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Base URL:** `https://api.nexus.armor.com/api/v1`

---

## 1. Overview

This document specifies the API layer for Nexus, which backs all frontend functionality. The API follows RESTful conventions with consistent patterns across all endpoints.

### API Design Principles

1. **RESTful** - Resource-oriented URLs, standard HTTP methods
2. **JSON:API-inspired** - Consistent response envelope
3. **Versioned** - `/api/v1/` prefix for all endpoints
4. **Paginated** - All list endpoints support pagination
5. **Filterable** - Standard query parameters for filtering
6. **Authenticated** - JWT Bearer tokens required
7. **Tenant-isolated** - All data scoped to organization

---

## 2. Authentication

### 2.1 Token Endpoints

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2gg...",
    "expiresIn": 3600,
    "tokenType": "Bearer"
  }
}
```

#### POST /auth/refresh
Refresh access token.

**Request:**
```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2gg..."
}
```

#### POST /auth/logout
Invalidate tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### GET /auth/me
Get current user info.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Smith",
    "role": "analyst",
    "organization": {
      "id": "org_xyz789",
      "name": "Acme Corp"
    },
    "permissions": ["alerts:read", "alerts:write", "assets:read"]
  }
}
```

---

## 3. Standard Response Format

### 3.1 Success Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "totalPages": 8
    }
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

### 3.2 Single Resource Response

```json
{
  "success": true,
  "data": {
    "id": "alert_123",
    "title": "Suspicious login",
    "severity": "high",
    ...
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

### 3.3 Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ]
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

### 3.4 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## 4. Standard Query Parameters

### 4.1 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number |
| `limit` | number | 20 | Items per page (max 100) |

### 4.2 Sorting

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `sort` | string | `createdAt` | Field to sort by |
| `order` | string | `desc` | Sort direction (asc/desc) |

### 4.3 Filtering

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `filter[field]` | string | `filter[severity]=high` | Filter by field value |
| `filter[field][op]` | string | `filter[score][gte]=7` | Filter with operator |
| `search` | string | `search=ransomware` | Full-text search |

**Supported Operators:**
- `eq` - Equal (default)
- `ne` - Not equal
- `gt`, `gte` - Greater than (or equal)
- `lt`, `lte` - Less than (or equal)
- `in` - In array: `filter[status][in]=open,acknowledged`
- `contains` - String contains

### 4.4 Date Range

| Parameter | Type | Example |
|-----------|------|---------|
| `startDate` | ISO 8601 | `2026-01-01T00:00:00Z` |
| `endDate` | ISO 8601 | `2026-01-31T23:59:59Z` |

---

## 5. Alerts API

### 5.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts` | List alerts |
| GET | `/alerts/:id` | Get alert by ID |
| PUT | `/alerts/:id` | Update alert |
| POST | `/alerts/:id/acknowledge` | Acknowledge alert |
| POST | `/alerts/:id/resolve` | Resolve alert |
| GET | `/alerts/stats` | Alert statistics |

### 5.2 Alert Object

```typescript
interface Alert {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "acknowledged" | "resolved" | "closed";
  source: string;
  sourceId: string;
  asset?: {
    id: string;
    name: string;
    type: string;
  };
  assignee?: {
    id: string;
    name: string;
    email: string;
  };
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
}
```

### 5.3 GET /alerts

**Query Parameters:**
```
GET /alerts?page=1&limit=20&sort=createdAt&order=desc
    &filter[severity][in]=critical,high
    &filter[status]=open
    &startDate=2026-01-01T00:00:00Z
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "alert_abc123",
        "title": "Suspicious login from new location",
        "description": "Login detected from IP 192.168.1.100",
        "severity": "high",
        "status": "open",
        "source": "identity-provider",
        "createdAt": "2026-01-03T10:30:00Z",
        "asset": {
          "id": "asset_xyz",
          "name": "user@company.com",
          "type": "user"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "totalPages": 3
    }
  }
}
```

### 5.4 GET /alerts/stats

**Query Parameters:**
```
GET /alerts/stats?startDate=2026-01-01&endDate=2026-01-31
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "bySeverity": {
      "critical": 5,
      "high": 25,
      "medium": 70,
      "low": 50
    },
    "byStatus": {
      "open": 45,
      "acknowledged": 30,
      "resolved": 75
    },
    "trend": [
      { "date": "2026-01-01", "count": 12 },
      { "date": "2026-01-02", "count": 8 }
    ],
    "mttr": {
      "average": 14400,
      "median": 7200
    }
  }
}
```

---

## 6. Assets API

### 6.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets` | List assets |
| GET | `/assets/:id` | Get asset by ID |
| GET | `/assets/search` | Search assets |
| GET | `/assets/stats` | Asset statistics |

### 6.2 Asset Object

```typescript
interface Asset {
  id: string;
  externalId: string;
  type: "server" | "endpoint" | "user" | "application" | "cloud_resource";
  name: string;
  hostname?: string;
  ipAddresses: string[];
  operatingSystem?: string;
  riskScore: number;
  criticality: "critical" | "high" | "medium" | "low";
  tags: string[];
  metadata: Record<string, unknown>;
  lastSeenAt: string;
  createdAt: string;
  updatedAt: string;
  vulnerabilityCount: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}
```

### 6.3 GET /assets

**Query Parameters:**
```
GET /assets?page=1&limit=20
    &filter[type]=server
    &filter[riskScore][gte]=7
    &filter[criticality][in]=critical,high
```

---

## 7. Vulnerabilities API

### 7.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vulnerabilities` | List vulnerabilities |
| GET | `/vulnerabilities/:id` | Get vulnerability |
| PUT | `/vulnerabilities/:id` | Update vulnerability |
| POST | `/vulnerabilities/:id/remediate` | Mark remediated |
| GET | `/vulnerabilities/stats` | Statistics |

### 7.2 Vulnerability Object

```typescript
interface Vulnerability {
  id: string;
  cveId?: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  cvssScore: number;
  cvssVector: string;
  status: "open" | "in_progress" | "remediated" | "accepted";
  asset: {
    id: string;
    name: string;
    type: string;
  };
  affectedSoftware: string;
  affectedVersion: string;
  fixedVersion?: string;
  remediation: string;
  references: string[];
  exploitAvailable: boolean;
  dueDate?: string;
  discoveredAt: string;
  updatedAt: string;
  remediatedAt?: string;
}
```

---

## 8. Compliance API

### 8.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/compliance/frameworks` | List frameworks |
| GET | `/compliance/frameworks/:id` | Get framework details |
| GET | `/compliance/controls` | List controls |
| GET | `/compliance/controls/:id` | Get control details |
| PUT | `/compliance/controls/:id` | Update control status |
| GET | `/compliance/posture` | Overall posture |

### 8.2 Framework Object

```typescript
interface ComplianceFramework {
  id: string;
  name: string;
  description: string;
  version: string;
  controlCount: number;
  status: {
    compliant: number;
    nonCompliant: number;
    notApplicable: number;
    inProgress: number;
  };
  score: number;
  lastAssessedAt: string;
}
```

### 8.3 Control Object

```typescript
interface ComplianceControl {
  id: string;
  frameworkId: string;
  controlId: string;
  title: string;
  description: string;
  category: string;
  status: "compliant" | "non_compliant" | "not_applicable" | "in_progress";
  evidence: Evidence[];
  owner?: {
    id: string;
    name: string;
  };
  dueDate?: string;
  lastAssessedAt: string;
}
```

---

## 9. Metrics API

### 9.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics/dashboard` | Dashboard metrics |
| GET | `/metrics/trends` | Trend data |
| GET | `/metrics/executive` | Executive summary |

### 9.2 GET /metrics/dashboard

**Query Parameters:**
```
GET /metrics/dashboard?startDate=2026-01-01&endDate=2026-01-31
```

**Response:**
```json
{
  "success": true,
  "data": {
    "securityScore": 78,
    "securityScoreTrend": 3.5,
    "alertsSummary": {
      "open": 45,
      "critical": 5,
      "mttr": 14400
    },
    "vulnerabilitiesSummary": {
      "open": 120,
      "critical": 8,
      "overdue": 12
    },
    "assetsSummary": {
      "total": 500,
      "atRisk": 45
    },
    "complianceSummary": {
      "overallScore": 85,
      "frameworks": [
        { "name": "SOC 2", "score": 90 },
        { "name": "ISO 27001", "score": 82 }
      ]
    }
  }
}
```

---

## 10. Reports API

### 10.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports` | List reports |
| POST | `/reports/generate` | Generate report |
| GET | `/reports/:id` | Get report status |
| GET | `/reports/:id/download` | Download report |

### 10.2 POST /reports/generate

**Request:**
```json
{
  "type": "executive_summary",
  "format": "pdf",
  "dateRange": {
    "start": "2026-01-01",
    "end": "2026-01-31"
  },
  "filters": {
    "severity": ["critical", "high"]
  }
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "id": "report_abc123",
    "status": "processing",
    "estimatedCompletionTime": 60
  }
}
```

---

## 11. Integrations API

### 11.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/integrations/connectors` | List connectors |
| GET | `/integrations/connectors/:id` | Connector status |
| POST | `/integrations/connectors/:id/sync` | Trigger sync |
| PUT | `/integrations/connectors/:id/config` | Update config |

### 11.2 Connector Object

```typescript
interface Connector {
  id: string;
  name: string;
  type: string;
  category: "cloud" | "security" | "identity" | "compliance";
  status: "connected" | "disconnected" | "error";
  lastSyncAt?: string;
  nextSyncAt?: string;
  syncFrequency: number;
  itemCount?: number;
  config: Record<string, unknown>;
  error?: {
    code: string;
    message: string;
    occurredAt: string;
  };
}
```

---

## 12. Users API

### 12.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users |
| GET | `/users/:id` | Get user |
| POST | `/users` | Create user |
| PUT | `/users/:id` | Update user |
| DELETE | `/users/:id` | Delete user |
| PUT | `/users/:id/role` | Update role |

---

## 13. Organizations API

### 13.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/organizations/current` | Current org |
| PUT | `/organizations/current` | Update org |
| GET | `/organizations/current/settings` | Get settings |
| PUT | `/organizations/current/settings` | Update settings |

---

## 14. Rate Limiting

### 14.1 Limits

| Tier | Requests/Minute | Burst |
|------|-----------------|-------|
| Standard | 1000 | 100 |
| Enterprise | 5000 | 500 |

### 14.2 Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1609459200
```

### 14.3 Rate Limit Response (429)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "retryAfter": 30
  }
}
```

---

## 15. Webhooks

### 15.1 Webhook Events

| Event | Description |
|-------|-------------|
| `alert.created` | New alert created |
| `alert.updated` | Alert status changed |
| `vulnerability.created` | New vulnerability |
| `vulnerability.remediated` | Vulnerability fixed |
| `compliance.control_updated` | Control status changed |

### 15.2 Webhook Payload

```json
{
  "event": "alert.created",
  "timestamp": "2026-01-03T10:30:00Z",
  "data": {
    "id": "alert_abc123",
    "title": "Suspicious login",
    "severity": "high"
  },
  "signature": "sha256=abc123..."
}
```

---

## 16. API Versioning

### 16.1 Version Format
- URL prefix: `/api/v1/`
- Semantic versioning for breaking changes

### 16.2 Deprecation Policy
- 6-month deprecation notice
- `Sunset` header with deprecation date
- `Deprecation` header with link to docs

---

*This API specification is maintained by the Platform team. Changes require review.*
