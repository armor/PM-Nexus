# API Developer Experience Specification

## Overview

This document defines the comprehensive API developer experience for the Nexus security platform, covering three primary developer touchpoints:

1. **developer.armor.com** - Developer portal with guides, tutorials, and SDKs
2. **api.armor.com** - Interactive API reference and documentation
3. **mcp.armor.com** - MCP (Model Context Protocol) server documentation

---

## 1. Platform API Architecture

### 1.1 API Base Structure

Based on the platform codebase analysis, the API layer consists of multiple specialized microservices:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API Gateway Layer                                  │
│                     (Kong / AWS API Gateway)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Legacy API      │  │  Security API    │  │  Compliance API  │          │
│  │  /api/v1/*       │  │  /api/security/* │  │  /api/compliance/*│          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  MDR API         │  │  Infrastructure  │  │  Agent Mgmt      │          │
│  │  /api/mdr/*      │  │  /api/infra/*    │  │  /api/agents/*   │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Cloud Connect   │  │  Log Management  │  │  MCP Server      │          │
│  │  /api/cloud/*    │  │  /api/logs/*     │  │  /mcp/v1/*       │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 API Base URLs (Environment Variables)

```typescript
const API_BASES = {
  agentManagement: 'VITE_API_BASE_AGENT_MANAGEMENT',
  cloudConnection: 'VITE_API_BASE_CLOUD_CONNECTION',
  compliance: 'VITE_API_BASE_COMPLIANCE',
  compute: 'VITE_API_BASE_COMPUTE_API_URL',
  consoleCms: 'VITE_API_BASE_CONSOLE_CMS',
  hcpTerraform: 'VITE_API_BASE_HCP_TERRAFORM',
  infrastructure: 'VITE_API_BASE_INFRASTRUCTURE_API_URL',
  kb: 'VITE_API_BASE_AMP_KB_URL',
  legacy: 'VITE_API_BASE_LEGACY',
  logmanagement: 'VITE_API_BASE_LOGMANAGEMENT',
  mdr: 'VITE_API_BASE_MDR',
  openCti: 'VITE_API_BASE_OPEN_CTI',
  productCatalog: 'VITE_API_BASE_PRODUCT_CATALOG',
  securityDetections: 'VITE_API_BASE_SECURITY_DETECTIONS',
  secureNotes: 'VITE_API_BASE_SECURE_NOTES',
  support: 'VITE_APP_SUPPORT_URL',
};
```

---

## 2. developer.armor.com - Developer Portal

### 2.1 Portal Structure

```
developer.armor.com/
├── /                          # Landing page with quick start
├── /getting-started/          # Onboarding guides
│   ├── /authentication/       # Auth setup with Okta
│   ├── /first-api-call/       # Hello World tutorial
│   ├── /sdks/                 # SDK installation
│   └── /environments/         # Sandbox vs production
├── /guides/                   # In-depth tutorials
│   ├── /security-detections/  # Working with alerts
│   ├── /vulnerability-mgmt/   # Vulnerability APIs
│   ├── /compliance/           # Compliance reporting
│   ├── /asset-inventory/      # Asset management
│   ├── /connectors/           # Third-party integrations
│   └── /webhooks/             # Event notifications
├── /reference/                # Redirect to api.armor.com
├── /sdks/                     # SDK documentation
│   ├── /javascript/           # @armor/nexus-sdk
│   ├── /python/               # armor-nexus-python
│   ├── /go/                   # go-armor-nexus
│   └── /cli/                  # armor-cli
├── /tools/                    # Developer tools
│   ├── /api-explorer/         # Interactive API testing
│   ├── /webhook-tester/       # Webhook debugging
│   └── /mcp-playground/       # MCP server testing
├── /changelog/                # API version history
├── /status/                   # API status page
└── /support/                  # Developer support
```

### 2.2 Authentication Guide Requirements

The developer portal must document the OAuth 2.0 / OIDC flow:

```markdown
## Authentication

Nexus API uses OAuth 2.0 with Okta as the identity provider.

### Getting Your API Credentials

1. Log into the Nexus console
2. Navigate to Settings → API Access
3. Click "Create API Key"
4. Store your Client ID and Client Secret securely

### Authentication Flow

All API requests require a Bearer token in the Authorization header:

```bash
curl -X GET "https://api.armor.com/v1/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Account-Context: YOUR_ACCOUNT_ID"
```

### Token Refresh

Access tokens expire after 1 hour. Use the refresh token to obtain new access tokens:

```bash
curl -X POST "https://auth.armor.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID"
```
```

### 2.3 SDK Documentation Requirements

Each SDK must include:

1. **Installation Guide**
   ```bash
   # JavaScript/TypeScript
   npm install @armor/nexus-sdk

   # Python
   pip install armor-nexus

   # Go
   go get github.com/armor/nexus-go
   ```

2. **Quick Start Example**
   ```typescript
   import { NexusClient } from '@armor/nexus-sdk';

   const client = new NexusClient({
     clientId: process.env.ARMOR_CLIENT_ID,
     clientSecret: process.env.ARMOR_CLIENT_SECRET,
     accountId: process.env.ARMOR_ACCOUNT_ID,
   });

   // Get security score
   const score = await client.metrics.getSecurityScore();
   console.log(`Security Score: ${score.value}/100`);

   // List recent alerts
   const alerts = await client.alerts.list({
     severity: ['critical', 'high'],
     status: 'open',
     limit: 10,
   });
   ```

3. **Type Definitions** (for TypeScript)
   ```typescript
   interface Alert {
     id: string;
     title: string;
     severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
     status: 'open' | 'acknowledged' | 'resolved' | 'dismissed';
     source: string;
     createdAt: Date;
     assets: Asset[];
   }
   ```

### 2.4 Content Requirements

| Section | Requirements |
|---------|--------------|
| Getting Started | < 5 min to first API call |
| Authentication | Step-by-step with code samples |
| Tutorials | Real-world scenarios with full code |
| Error Handling | All error codes documented |
| Rate Limits | Clear limits per endpoint |
| Changelog | Semantic versioning, deprecation notices |

---

## 3. api.armor.com - API Reference

### 3.1 Reference Structure

```
api.armor.com/
├── /                          # API overview + search
├── /v1/                       # Version 1 endpoints
│   ├── /authentication/       # Auth endpoints
│   │   ├── /token/
│   │   ├── /refresh/
│   │   └── /revoke/
│   ├── /me/                   # Current user
│   ├── /accounts/             # Account management
│   │   ├── /{accountId}/
│   │   ├── /children/
│   │   └── /settings/
│   ├── /alerts/               # Security alerts
│   │   ├── /list/
│   │   ├── /{alertId}/
│   │   └── /bulk/
│   ├── /findings/             # Security findings
│   ├── /assets/               # Asset inventory
│   ├── /vulnerabilities/      # Vulnerability data
│   ├── /compliance/           # Compliance status
│   ├── /connectors/           # Integration connectors
│   ├── /reports/              # Report generation
│   └── /webhooks/             # Webhook management
├── /v2/                       # Version 2 endpoints
│   └── /security-detections/  # Enhanced detections
└── /schemas/                  # JSON Schema definitions
```

### 3.2 Endpoint Documentation Template

Each endpoint must include:

```yaml
# Example: GET /v1/alerts/{alertId}

endpoint:
  method: GET
  path: /v1/alerts/{alertId}
  summary: Get alert details
  description: |
    Retrieves detailed information about a specific security alert,
    including associated findings, affected assets, and timeline.

authentication:
  required: true
  scopes:
    - alerts:read

parameters:
  path:
    - name: alertId
      type: string
      required: true
      description: Unique identifier of the alert
      example: "alert_123abc"

  headers:
    - name: Authorization
      type: string
      required: true
      description: Bearer token
      example: "Bearer eyJhbGciOi..."

    - name: X-Account-Context
      type: string
      required: true
      description: Account ID for multi-tenant access
      example: "1000"

responses:
  200:
    description: Alert retrieved successfully
    schema: AlertDetailResponse
    example:
      id: "alert_123abc"
      title: "Critical vulnerability detected"
      severity: "critical"
      status: "open"
      source: "CrowdStrike"
      createdAt: "2024-01-15T10:30:00Z"
      findings: [...]
      assets: [...]

  401:
    description: Unauthorized - invalid or expired token

  403:
    description: Forbidden - insufficient permissions

  404:
    description: Alert not found

rate_limit:
  requests: 100
  window: "1 minute"

code_samples:
  curl: |
    curl -X GET "https://api.armor.com/v1/alerts/alert_123abc" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-Account-Context: 1000"

  javascript: |
    const alert = await client.alerts.get('alert_123abc');

  python: |
    alert = client.alerts.get('alert_123abc')
```

### 3.3 Interactive API Explorer Requirements

The API reference must include:

1. **Try It Now** - Interactive request builder
2. **Request/Response Examples** - Real payloads
3. **Schema Viewer** - Expandable type definitions
4. **Code Generation** - Copy snippets in multiple languages
5. **Authentication Helper** - Token input and auto-injection

### 3.4 Error Response Standard

All API errors must follow this structure:

```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable message
    details?: object;       // Additional context
    requestId: string;      // For support debugging
    documentation?: string; // Link to docs
  };
}

// Example error codes
const ERROR_CODES = {
  // Authentication (401)
  'auth/invalid-token': 'The access token is invalid or expired',
  'auth/missing-token': 'No authorization header provided',

  // Authorization (403)
  'auth/insufficient-scope': 'Token lacks required permissions',
  'auth/account-access-denied': 'No access to this account',

  // Validation (400)
  'validation/invalid-parameter': 'Request parameter validation failed',
  'validation/missing-required': 'Required field is missing',

  // Rate Limiting (429)
  'rate-limit/exceeded': 'Too many requests',

  // Server Errors (500)
  'server/internal-error': 'An unexpected error occurred',
  'server/service-unavailable': 'Service temporarily unavailable',
};
```

### 3.5 Pagination Standard

All list endpoints must support cursor-based pagination:

```typescript
// Request
GET /v1/alerts?limit=25&after=cursor_abc123

// Response
interface PaginatedResponse<T> {
  data: T[];
  paging: {
    before: string | null;  // Previous page cursor
    after: string | null;   // Next page cursor
    total?: number;         // Total count (optional, expensive)
  };
  meta: {
    requestId: string;
    timestamp: string;
  };
}
```

### 3.6 Filtering & Sorting Standard

```typescript
// Query parameters for filtering
GET /v1/alerts?
  severity=critical,high&           // Multi-value filter
  status=open&                       // Single value filter
  source=CrowdStrike&               // Exact match
  createdAt[gte]=2024-01-01&        // Range filter (gte, lte, gt, lt)
  createdAt[lte]=2024-01-31&
  sort=-createdAt,severity&         // Sort (- prefix = descending)
  limit=25&
  after=cursor_xyz

// Filter operators
interface FilterOperators {
  eq: 'Equals (default)';
  neq: 'Not equals';
  gt: 'Greater than';
  gte: 'Greater than or equal';
  lt: 'Less than';
  lte: 'Less than or equal';
  contains: 'String contains';
  startsWith: 'String starts with';
  in: 'Value in array';
  notIn: 'Value not in array';
}
```

---

## 4. mcp.armor.com - MCP Server Documentation

### 4.1 MCP Server Overview

The Nexus MCP (Model Context Protocol) Server enables AI assistants like Claude to interact with the security platform.

```
mcp.armor.com/
├── /                          # MCP overview
├── /getting-started/          # Quick start guide
├── /tools/                    # Available MCP tools
│   ├── /alerts/               # Alert management tools
│   ├── /queries/              # Data query tools
│   ├── /actions/              # Remediation actions
│   └── /reports/              # Report generation
├── /resources/                # MCP resources
├── /prompts/                  # Pre-built prompts
├── /authentication/           # Auth for MCP
├── /examples/                 # Usage examples
└── /sdk/                      # MCP SDK integration
```

### 4.2 MCP Tools Specification

Based on the platform capabilities, the MCP server should expose:

```typescript
// Tool Categories

interface MCPToolRegistry {
  // Read Operations (Queries)
  queries: {
    getSecurityScore: Tool;
    listAlerts: Tool;
    getAlertDetails: Tool;
    listFindings: Tool;
    listAssets: Tool;
    getVulnerabilityTrend: Tool;
    getComplianceStatus: Tool;
    getConnectorHealth: Tool;
  };

  // Write Operations (Actions)
  actions: {
    acknowledgeAlert: Tool;
    resolveAlert: Tool;
    createTicket: Tool;
    runScan: Tool;
    updateAssetTags: Tool;
  };

  // Report Generation
  reports: {
    generateSecurityReport: Tool;
    generateComplianceReport: Tool;
    exportFindings: Tool;
  };

  // Natural Language Queries
  nlq: {
    askSecurityQuestion: Tool;  // RAG-powered Q&A
    explainFinding: Tool;       // Contextualized explanations
    suggestRemediation: Tool;   // AI-powered recommendations
  };
}
```

### 4.3 MCP Tool Schema Examples

```typescript
// Example Tool: listAlerts
const listAlertsTool: MCPTool = {
  name: 'nexus_list_alerts',
  description: 'List security alerts with optional filtering by severity, status, source, and date range',
  inputSchema: {
    type: 'object',
    properties: {
      severity: {
        type: 'array',
        items: {
          type: 'string',
          enum: ['critical', 'high', 'medium', 'low', 'info']
        },
        description: 'Filter by severity levels'
      },
      status: {
        type: 'string',
        enum: ['open', 'acknowledged', 'resolved', 'dismissed'],
        description: 'Filter by alert status'
      },
      source: {
        type: 'string',
        description: 'Filter by connector source (e.g., CrowdStrike, Tenable)'
      },
      since: {
        type: 'string',
        format: 'date-time',
        description: 'Filter alerts created after this timestamp'
      },
      limit: {
        type: 'number',
        default: 25,
        maximum: 100,
        description: 'Maximum number of alerts to return'
      }
    }
  },
  handler: async (params) => {
    // Implementation calls internal API
  }
};

// Example Tool: getSecurityScore
const getSecurityScoreTool: MCPTool = {
  name: 'nexus_get_security_score',
  description: 'Get the current security posture score (0-100) with breakdown by category',
  inputSchema: {
    type: 'object',
    properties: {
      includeBreakdown: {
        type: 'boolean',
        default: true,
        description: 'Include category-level score breakdown'
      },
      includeTrend: {
        type: 'boolean',
        default: false,
        description: 'Include historical trend data'
      }
    }
  }
};

// Example Tool: acknowledgeAlert
const acknowledgeAlertTool: MCPTool = {
  name: 'nexus_acknowledge_alert',
  description: 'Acknowledge a security alert, indicating it is being investigated',
  inputSchema: {
    type: 'object',
    required: ['alertId'],
    properties: {
      alertId: {
        type: 'string',
        description: 'The unique identifier of the alert to acknowledge'
      },
      note: {
        type: 'string',
        description: 'Optional note about the acknowledgment'
      },
      assignee: {
        type: 'string',
        description: 'Email of the user to assign the alert to'
      }
    }
  }
};
```

### 4.4 MCP Resources

```typescript
// Static resources available via MCP
const mcpResources: MCPResource[] = [
  {
    uri: 'nexus://dashboard/overview',
    name: 'Dashboard Overview',
    description: 'Current security dashboard state',
    mimeType: 'application/json'
  },
  {
    uri: 'nexus://connectors/status',
    name: 'Connector Status',
    description: 'Health status of all configured connectors',
    mimeType: 'application/json'
  },
  {
    uri: 'nexus://compliance/frameworks',
    name: 'Compliance Frameworks',
    description: 'Configured compliance frameworks and their status',
    mimeType: 'application/json'
  }
];
```

### 4.5 MCP Authentication

```markdown
## MCP Authentication

The Nexus MCP Server uses the same OAuth 2.0 authentication as the REST API.

### Configuration

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "nexus": {
      "command": "npx",
      "args": ["@armor/nexus-mcp-server"],
      "env": {
        "ARMOR_CLIENT_ID": "${ARMOR_CLIENT_ID}",
        "ARMOR_CLIENT_SECRET": "${ARMOR_CLIENT_SECRET}",
        "ARMOR_ACCOUNT_ID": "${ARMOR_ACCOUNT_ID}"
      }
    }
  }
}
```

### Permission Scopes

MCP tools require the same permissions as their REST API equivalents:

| Tool | Required Scope |
|------|----------------|
| nexus_list_alerts | alerts:read |
| nexus_acknowledge_alert | alerts:write |
| nexus_get_security_score | metrics:read |
| nexus_create_ticket | tickets:write |
```

---

## 5. API Hook Patterns (Frontend SDK)

Based on platform codebase analysis, document these patterns for SDK developers:

### 5.1 TanStack Query Integration

```typescript
// Standard query hook pattern
export function useAlerts(filters: AlertFilters) {
  return useQuery<AlertsResponse, AxiosError>({
    queryKey: ['alerts', filters],
    queryFn: async () => {
      const res = await axios.get(apiUrl('alerts'), { params: filters });
      return res.data;
    },
    staleTime: 30 * 1000,        // 30 seconds
    refetchInterval: 30 * 1000,  // Auto-refresh
    placeholderData: {           // Optimistic UI skeleton
      data: [],
      paging: { before: null, after: null }
    }
  });
}

// Standard mutation hook pattern
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  return useMutation<void, AxiosError, { alertId: string; note?: string }>({
    mutationFn: async ({ alertId, note }) => {
      await axios.post(apiUrl(`alerts/${alertId}/acknowledge`), { note });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
    onSuccess: () => {
      enqueueSnackbar('Alert acknowledged', { variant: 'success' });
    },
    onError: (error) => {
      enqueueSnackbar(
        error.response?.data?.message || 'Failed to acknowledge alert',
        { variant: 'error' }
      );
    }
  });
}
```

### 5.2 Query Key Conventions

```typescript
// Naming convention: [entity, ...params]
const QUERY_KEYS = {
  // Read operations
  alerts: (filters?: AlertFilters) => ['alerts', filters],
  alertDetail: (id: string) => ['alerts', id],

  // Metrics
  securityScore: () => ['metrics', 'security-score'],
  vulnerabilityTrend: (days: number) => ['metrics', 'vulnerability-trend', days],

  // Assets
  assets: (filters?: AssetFilters) => ['assets', filters],
  assetDetail: (id: string) => ['assets', id],

  // Connectors
  connectors: () => ['connectors'],
  connectorHealth: () => ['connectors', 'health'],
};
```

### 5.3 Cache Invalidation Patterns

```typescript
// After mutation, invalidate related queries
onSettled: () => {
  // Invalidate list queries
  queryClient.invalidateQueries({ queryKey: ['alerts'] });

  // Invalidate specific detail query
  queryClient.invalidateQueries({ queryKey: ['alerts', alertId] });

  // Invalidate metrics that depend on alerts
  queryClient.invalidateQueries({ queryKey: ['metrics', 'security-score'] });
};
```

---

## 6. API Versioning Strategy

### 6.1 Version Policy

```markdown
## API Versioning

Nexus API uses URL-based versioning with a 24-month support window.

### Version Lifecycle

| Phase | Duration | Description |
|-------|----------|-------------|
| Active | 12 months | Full support, new features |
| Maintenance | 12 months | Bug fixes only, no new features |
| Deprecated | 6 months | Warning headers, migration guide |
| Sunset | - | Returns 410 Gone |

### Breaking Changes

The following are considered breaking changes:
- Removing an endpoint
- Removing a required parameter
- Changing response structure
- Changing authentication requirements

### Deprecation Headers

Deprecated endpoints return headers:
```http
Deprecation: true
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: <https://developer.armor.com/migration/v1-to-v2>; rel="successor-version"
```
```

### 6.2 Version Headers

```http
# Request version preference
Accept: application/json; version=1

# Response includes version info
X-API-Version: 1.5.0
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1705312800
```

---

## 7. Rate Limiting

### 7.1 Rate Limit Tiers

| Tier | Requests/min | Requests/hour | Burst |
|------|--------------|---------------|-------|
| Free | 60 | 1,000 | 10 |
| Professional | 300 | 10,000 | 50 |
| Enterprise | 1,000 | 100,000 | 200 |
| Unlimited | Custom | Custom | Custom |

### 7.2 Rate Limit Headers

```http
X-Rate-Limit-Limit: 300
X-Rate-Limit-Remaining: 295
X-Rate-Limit-Reset: 1705312800
Retry-After: 30  # Only on 429 responses
```

### 7.3 Rate Limit Response

```json
{
  "error": {
    "code": "rate-limit/exceeded",
    "message": "Rate limit exceeded. Retry after 30 seconds.",
    "details": {
      "limit": 300,
      "remaining": 0,
      "resetAt": "2024-01-15T10:30:00Z"
    },
    "requestId": "req_abc123"
  }
}
```

---

## 8. Webhook Documentation

### 8.1 Webhook Events

```typescript
type WebhookEvent =
  | 'alert.created'
  | 'alert.updated'
  | 'alert.resolved'
  | 'finding.created'
  | 'finding.resolved'
  | 'asset.discovered'
  | 'asset.removed'
  | 'connector.connected'
  | 'connector.disconnected'
  | 'connector.error'
  | 'compliance.status_changed'
  | 'vulnerability.discovered'
  | 'vulnerability.remediated';

interface WebhookPayload<T = unknown> {
  id: string;
  type: WebhookEvent;
  timestamp: string;
  data: T;
  signature: string;
}
```

### 8.2 Webhook Security

```typescript
// Verify webhook signature
import crypto from 'crypto';

function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${expected}`)
  );
}
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (MVP)
- [ ] OpenAPI 3.1 specification generated from platform code
- [ ] api.armor.com with Stoplight/Redoc
- [ ] Basic authentication documentation
- [ ] Core endpoint documentation (alerts, findings, assets)

### Phase 2: Developer Portal
- [ ] developer.armor.com with Docusaurus
- [ ] Getting started guides
- [ ] JavaScript SDK (@armor/nexus-sdk)
- [ ] Interactive API explorer

### Phase 3: MCP Integration
- [ ] mcp.armor.com documentation
- [ ] MCP server package (@armor/nexus-mcp)
- [ ] Claude Code integration guide
- [ ] MCP tool reference

### Phase 4: Advanced Features
- [ ] Python SDK
- [ ] Go SDK
- [ ] CLI tool
- [ ] Webhook management UI
- [ ] API playground with saved examples

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to First API Call | < 5 minutes | Analytics tracking |
| Documentation Coverage | 100% endpoints | Automated check |
| SDK Adoption | 50% of API users | SDK telemetry |
| Developer Satisfaction | > 4.5/5 | Quarterly survey |
| Support Tickets | < 10/month | Ticket system |
| API Uptime | 99.9% | Status page |

---

## Appendix A: Header Reference

| Header | Direction | Description | Required |
|--------|-----------|-------------|----------|
| Authorization | Request | Bearer token | Yes |
| X-Account-Context | Request | Account ID for multi-tenant | Yes |
| X-Pagination-Token | Request | Cursor for pagination | No |
| X-Request-Id | Request | Client correlation ID | No |
| X-API-Version | Response | Current API version | - |
| X-Rate-Limit-* | Response | Rate limit info | - |
| X-Request-Id | Response | Server correlation ID | - |

## Appendix B: Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST creating resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource state conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary outage |
