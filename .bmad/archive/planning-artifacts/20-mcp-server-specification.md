# MCP Server Specification - Armor Platform Suite

## Overview

The Armor MCP (Model Context Protocol) Server enables AI assistants like Claude to interact with the complete Armor platform suite, which consists of three primary applications accessible via a unified app switcher (pizza menu):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Armor Platform Suite                                  │
│                     (Pizza Menu App Switcher)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   Armor-Dash     │  │     Nexus        │  │    Legacy AMP    │          │
│  │  (New Security   │  │   (Platform)     │  │  (Legacy Apps)   │          │
│  │   Dashboard)     │  │                  │  │                  │          │
│  │                  │  │                  │  │                  │          │
│  │  - Security      │  │  - Account Mgmt  │  │  - Existing      │          │
│  │  - Vuln Mgmt     │  │  - User Mgmt     │  │    Features      │          │
│  │  - Compliance    │  │  - Billing       │  │  - Migrations    │          │
│  │  - Connectors    │  │  - Settings      │  │  - Legacy APIs   │          │
│  │  - AI Assistant  │  │  - Teams         │  │                  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│                         Shared Services Layer                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Auth (Okta) │ API Gateway │ MCP Server │ Connectors │ Data Layer     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. MCP Server Architecture

### 1.1 Server Components

```typescript
// MCP Server Structure
@armor/mcp-server/
├── src/
│   ├── index.ts                 // Server entry point
│   ├── server.ts                // MCP protocol handler
│   ├── auth/
│   │   ├── authenticator.ts     // OAuth token validation
│   │   └── permissions.ts       // Permission checking
│   ├── tools/
│   │   ├── index.ts             // Tool registry
│   │   ├── armor-dash/          // armor-dash tools
│   │   │   ├── alerts.ts
│   │   │   ├── findings.ts
│   │   │   ├── vulnerabilities.ts
│   │   │   ├── compliance.ts
│   │   │   ├── connectors.ts
│   │   │   └── metrics.ts
│   │   ├── nexus/               // Nexus platform tools
│   │   │   ├── accounts.ts
│   │   │   ├── users.ts
│   │   │   ├── teams.ts
│   │   │   └── settings.ts
│   │   └── shared/              // Cross-app tools
│   │       ├── search.ts
│   │       ├── reports.ts
│   │       └── ai-assistant.ts
│   ├── resources/
│   │   ├── index.ts             // Resource registry
│   │   ├── dashboards.ts
│   │   └── config.ts
│   ├── prompts/
│   │   ├── index.ts             // Prompt registry
│   │   ├── security-analysis.ts
│   │   └── remediation.ts
│   └── utils/
│       ├── api-client.ts        // Internal API client
│       ├── rate-limiter.ts
│       └── logger.ts
├── package.json
├── tsconfig.json
└── README.md
```

### 1.2 Multi-Application Context

The MCP server maintains application context for proper routing:

```typescript
interface MCPContext {
  // Authentication
  auth: {
    accessToken: string;
    accountId: string;
    userId: string;
    permissions: string[];
  };

  // Active application context
  application: {
    current: 'armor-dash' | 'nexus' | 'legacy-amp';
    available: ApplicationInfo[];
  };

  // Session state
  session: {
    id: string;
    startedAt: Date;
    lastActivity: Date;
  };
}

interface ApplicationInfo {
  id: 'armor-dash' | 'nexus' | 'legacy-amp';
  name: string;
  description: string;
  baseUrl: string;
  features: string[];
  icon: string;
}
```

---

## 2. MCP Protocol Implementation

### 2.1 Server Initialization

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  {
    name: 'armor-platform',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

// Register handlers
server.setRequestHandler(ListToolsRequestSchema, handleListTools);
server.setRequestHandler(CallToolRequestSchema, handleCallTool);
server.setRequestHandler(ListResourcesRequestSchema, handleListResources);
server.setRequestHandler(ReadResourceRequestSchema, handleReadResource);
server.setRequestHandler(ListPromptsRequestSchema, handleListPrompts);
server.setRequestHandler(GetPromptRequestSchema, handleGetPrompt);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 2.2 Authentication Flow

```typescript
// Environment-based authentication
interface ArmorMCPConfig {
  ARMOR_CLIENT_ID: string;
  ARMOR_CLIENT_SECRET: string;
  ARMOR_ACCOUNT_ID: string;
  ARMOR_ENVIRONMENT?: 'production' | 'staging' | 'sandbox';
  ARMOR_DEFAULT_APP?: 'armor-dash' | 'nexus' | 'legacy-amp';
}

class ArmorAuthenticator {
  private accessToken: string | null = null;
  private tokenExpiry: Date | null = null;

  async authenticate(): Promise<AuthContext> {
    if (this.isTokenValid()) {
      return this.getContext();
    }

    const response = await fetch('https://auth.armor.com/oauth2/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: process.env.ARMOR_CLIENT_ID!,
        client_secret: process.env.ARMOR_CLIENT_SECRET!,
        scope: 'armor-dash:read armor-dash:write nexus:read',
      }),
    });

    const { access_token, expires_in } = await response.json();
    this.accessToken = access_token;
    this.tokenExpiry = new Date(Date.now() + expires_in * 1000);

    return this.getContext();
  }

  private isTokenValid(): boolean {
    return this.accessToken !== null &&
           this.tokenExpiry !== null &&
           this.tokenExpiry > new Date();
  }
}
```

---

## 3. Tool Specifications

### 3.1 Armor-Dash Tools (Security Operations)

#### 3.1.1 Alert Management

```typescript
// Tool: armor_list_alerts
const listAlertsTool: MCPTool = {
  name: 'armor_list_alerts',
  description: `List security alerts from Armor-Dash. Returns alerts from all
    connected security tools (CrowdStrike, Tenable, Splunk, etc.) with optional
    filtering by severity, status, and source.`,
  inputSchema: {
    type: 'object',
    properties: {
      severity: {
        type: 'array',
        items: {
          type: 'string',
          enum: ['critical', 'high', 'medium', 'low', 'info'],
        },
        description: 'Filter by severity levels (e.g., ["critical", "high"])',
      },
      status: {
        type: 'string',
        enum: ['open', 'acknowledged', 'resolved', 'dismissed'],
        description: 'Filter by alert status',
      },
      source: {
        type: 'string',
        description: 'Filter by connector source (e.g., "CrowdStrike", "Tenable")',
      },
      since: {
        type: 'string',
        format: 'date-time',
        description: 'Return alerts created after this timestamp (ISO 8601)',
      },
      limit: {
        type: 'number',
        default: 25,
        maximum: 100,
        description: 'Maximum number of alerts to return',
      },
    },
  },
};

// Tool: armor_get_alert
const getAlertTool: MCPTool = {
  name: 'armor_get_alert',
  description: `Get detailed information about a specific security alert,
    including associated findings, affected assets, and timeline of events.`,
  inputSchema: {
    type: 'object',
    required: ['alertId'],
    properties: {
      alertId: {
        type: 'string',
        description: 'Unique alert identifier',
      },
    },
  },
};

// Tool: armor_acknowledge_alert
const acknowledgeAlertTool: MCPTool = {
  name: 'armor_acknowledge_alert',
  description: `Acknowledge a security alert, marking it as under investigation.
    Optionally assign to a team member and add investigation notes.`,
  inputSchema: {
    type: 'object',
    required: ['alertId'],
    properties: {
      alertId: {
        type: 'string',
        description: 'Unique alert identifier',
      },
      note: {
        type: 'string',
        description: 'Investigation notes or comments',
      },
      assignee: {
        type: 'string',
        format: 'email',
        description: 'Email of team member to assign',
      },
    },
  },
};

// Tool: armor_resolve_alert
const resolveAlertTool: MCPTool = {
  name: 'armor_resolve_alert',
  description: `Resolve a security alert with a resolution type and notes.`,
  inputSchema: {
    type: 'object',
    required: ['alertId', 'resolution'],
    properties: {
      alertId: {
        type: 'string',
        description: 'Unique alert identifier',
      },
      resolution: {
        type: 'string',
        enum: ['fixed', 'false_positive', 'accepted_risk', 'duplicate'],
        description: 'Resolution type',
      },
      note: {
        type: 'string',
        description: 'Resolution notes explaining the decision',
      },
    },
  },
};
```

#### 3.1.2 Vulnerability Management

```typescript
// Tool: armor_list_vulnerabilities
const listVulnerabilitiesTool: MCPTool = {
  name: 'armor_list_vulnerabilities',
  description: `List vulnerabilities discovered across your assets.
    Aggregates data from vulnerability scanners like Tenable, Qualys, and Nessus.`,
  inputSchema: {
    type: 'object',
    properties: {
      severity: {
        type: 'array',
        items: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
      },
      cveId: {
        type: 'string',
        description: 'Filter by specific CVE ID (e.g., "CVE-2024-1234")',
      },
      assetId: {
        type: 'string',
        description: 'Filter vulnerabilities affecting a specific asset',
      },
      hasExploit: {
        type: 'boolean',
        description: 'Filter for vulnerabilities with known exploits',
      },
      limit: {
        type: 'number',
        default: 25,
        maximum: 100,
      },
    },
  },
};

// Tool: armor_get_vulnerability_trend
const getVulnerabilityTrendTool: MCPTool = {
  name: 'armor_get_vulnerability_trend',
  description: `Get vulnerability count trends over time, grouped by severity.
    Useful for tracking security posture improvement.`,
  inputSchema: {
    type: 'object',
    properties: {
      days: {
        type: 'number',
        default: 30,
        minimum: 7,
        maximum: 365,
        description: 'Number of days of trend data',
      },
      groupBy: {
        type: 'string',
        enum: ['day', 'week', 'month'],
        default: 'day',
      },
    },
  },
};
```

#### 3.1.3 Security Metrics

```typescript
// Tool: armor_get_security_score
const getSecurityScoreTool: MCPTool = {
  name: 'armor_get_security_score',
  description: `Get the current security posture score (0-100) with breakdown
    by category: vulnerabilities, compliance, alerts, and configuration.`,
  inputSchema: {
    type: 'object',
    properties: {
      includeBreakdown: {
        type: 'boolean',
        default: true,
        description: 'Include category-level score breakdown',
      },
      includeTrend: {
        type: 'boolean',
        default: false,
        description: 'Include historical trend data',
      },
      trendDays: {
        type: 'number',
        default: 30,
        description: 'Days of trend history if includeTrend is true',
      },
    },
  },
};

// Tool: armor_get_risk_summary
const getRiskSummaryTool: MCPTool = {
  name: 'armor_get_risk_summary',
  description: `Get a summary of current risk exposure across all security
    domains including open alerts, critical vulnerabilities, and compliance gaps.`,
  inputSchema: {
    type: 'object',
    properties: {},
  },
};
```

#### 3.1.4 Compliance

```typescript
// Tool: armor_get_compliance_status
const getComplianceStatusTool: MCPTool = {
  name: 'armor_get_compliance_status',
  description: `Get compliance status across all configured frameworks
    (SOC 2, HIPAA, PCI-DSS, ISO 27001, etc.).`,
  inputSchema: {
    type: 'object',
    properties: {
      frameworkId: {
        type: 'string',
        description: 'Filter by specific framework ID',
      },
    },
  },
};

// Tool: armor_list_compliance_gaps
const listComplianceGapsTool: MCPTool = {
  name: 'armor_list_compliance_gaps',
  description: `List compliance control failures and gaps that need attention.`,
  inputSchema: {
    type: 'object',
    properties: {
      frameworkId: {
        type: 'string',
        description: 'Filter by specific framework',
      },
      severity: {
        type: 'string',
        enum: ['critical', 'high', 'medium', 'low'],
      },
    },
  },
};
```

#### 3.1.5 Connector Management

```typescript
// Tool: armor_list_connectors
const listConnectorsTool: MCPTool = {
  name: 'armor_list_connectors',
  description: `List all configured security tool connectors and their status.`,
  inputSchema: {
    type: 'object',
    properties: {},
  },
};

// Tool: armor_get_connector_health
const getConnectorHealthTool: MCPTool = {
  name: 'armor_get_connector_health',
  description: `Get health and sync status of all connectors.
    Shows last sync time, error counts, and data freshness.`,
  inputSchema: {
    type: 'object',
    properties: {},
  },
};

// Tool: armor_sync_connector
const syncConnectorTool: MCPTool = {
  name: 'armor_sync_connector',
  description: `Manually trigger a data sync for a specific connector.`,
  inputSchema: {
    type: 'object',
    required: ['connectorId'],
    properties: {
      connectorId: {
        type: 'string',
        description: 'Connector identifier',
      },
      fullSync: {
        type: 'boolean',
        default: false,
        description: 'Force full sync instead of incremental',
      },
    },
  },
};
```

### 3.2 Nexus Platform Tools (Account & User Management)

```typescript
// Tool: nexus_get_account
const getAccountTool: MCPTool = {
  name: 'nexus_get_account',
  description: `Get account details from Nexus platform.`,
  inputSchema: {
    type: 'object',
    properties: {
      accountId: {
        type: 'string',
        description: 'Account ID (defaults to current account)',
      },
    },
  },
};

// Tool: nexus_list_users
const listUsersTool: MCPTool = {
  name: 'nexus_list_users',
  description: `List users in the current account.`,
  inputSchema: {
    type: 'object',
    properties: {
      role: {
        type: 'string',
        description: 'Filter by role',
      },
      status: {
        type: 'string',
        enum: ['active', 'inactive', 'pending'],
      },
    },
  },
};

// Tool: nexus_list_teams
const listTeamsTool: MCPTool = {
  name: 'nexus_list_teams',
  description: `List teams in the organization.`,
  inputSchema: {
    type: 'object',
    properties: {},
  },
};
```

### 3.3 AI Assistant Tools (Cross-Application)

```typescript
// Tool: armor_ask_security_question
const askSecurityQuestionTool: MCPTool = {
  name: 'armor_ask_security_question',
  description: `Ask a natural language question about your security posture.
    Uses RAG (Retrieval Augmented Generation) to provide contextual answers
    based on your actual security data.

    Examples:
    - "What are my most critical vulnerabilities?"
    - "How has our security score changed this month?"
    - "Which assets have the most alerts?"
    - "Are we compliant with SOC 2?"`,
  inputSchema: {
    type: 'object',
    required: ['question'],
    properties: {
      question: {
        type: 'string',
        description: 'Natural language security question',
      },
      context: {
        type: 'string',
        description: 'Additional context for the question',
      },
    },
  },
};

// Tool: armor_explain_finding
const explainFindingTool: MCPTool = {
  name: 'armor_explain_finding',
  description: `Get an AI-generated explanation of a security finding,
    including risk context, potential impact, and remediation guidance.`,
  inputSchema: {
    type: 'object',
    required: ['findingId'],
    properties: {
      findingId: {
        type: 'string',
        description: 'Finding identifier',
      },
      includeRemediation: {
        type: 'boolean',
        default: true,
        description: 'Include remediation steps',
      },
    },
  },
};

// Tool: armor_suggest_remediation
const suggestRemediationTool: MCPTool = {
  name: 'armor_suggest_remediation',
  description: `Get AI-powered remediation suggestions for a vulnerability
    or security issue, prioritized by risk and effort.`,
  inputSchema: {
    type: 'object',
    required: ['issueId'],
    properties: {
      issueId: {
        type: 'string',
        description: 'Alert, finding, or vulnerability ID',
      },
      issueType: {
        type: 'string',
        enum: ['alert', 'finding', 'vulnerability'],
        description: 'Type of security issue',
      },
    },
  },
};

// Tool: armor_generate_report
const generateReportTool: MCPTool = {
  name: 'armor_generate_report',
  description: `Generate a security report in various formats.`,
  inputSchema: {
    type: 'object',
    required: ['reportType'],
    properties: {
      reportType: {
        type: 'string',
        enum: ['executive_summary', 'vulnerability_report', 'compliance_report', 'incident_report'],
        description: 'Type of report to generate',
      },
      format: {
        type: 'string',
        enum: ['pdf', 'csv', 'json'],
        default: 'pdf',
      },
      dateRange: {
        type: 'object',
        properties: {
          start: { type: 'string', format: 'date' },
          end: { type: 'string', format: 'date' },
        },
      },
    },
  },
};
```

### 3.4 App Navigation Tool

```typescript
// Tool: armor_switch_application
const switchApplicationTool: MCPTool = {
  name: 'armor_switch_application',
  description: `Switch context to a different application in the Armor suite.
    Available applications: Armor-Dash (security), Nexus (platform), Legacy AMP.`,
  inputSchema: {
    type: 'object',
    required: ['application'],
    properties: {
      application: {
        type: 'string',
        enum: ['armor-dash', 'nexus', 'legacy-amp'],
        description: 'Application to switch to',
      },
    },
  },
};

// Tool: armor_list_applications
const listApplicationsTool: MCPTool = {
  name: 'armor_list_applications',
  description: `List all applications available in the Armor platform suite.`,
  inputSchema: {
    type: 'object',
    properties: {},
  },
};
```

---

## 4. MCP Resources

### 4.1 Resource Definitions

```typescript
const resources: MCPResource[] = [
  // armor-dash Resources
  {
    uri: 'armor://armor-dash/dashboard/overview',
    name: 'Armor-Dash Dashboard Overview',
    description: 'Current security dashboard state with key metrics',
    mimeType: 'application/json',
  },
  {
    uri: 'armor://armor-dash/alerts/summary',
    name: 'Alert Summary',
    description: 'Summary of open alerts by severity and source',
    mimeType: 'application/json',
  },
  {
    uri: 'armor://armor-dash/connectors/status',
    name: 'Connector Status',
    description: 'Health status of all configured connectors',
    mimeType: 'application/json',
  },
  {
    uri: 'armor://armor-dash/compliance/summary',
    name: 'Compliance Summary',
    description: 'Compliance status across all frameworks',
    mimeType: 'application/json',
  },

  // Nexus Resources
  {
    uri: 'armor://nexus/account/current',
    name: 'Current Account',
    description: 'Current account information',
    mimeType: 'application/json',
  },
  {
    uri: 'armor://nexus/users/me',
    name: 'Current User',
    description: 'Current user profile and permissions',
    mimeType: 'application/json',
  },

  // Cross-App Resources
  {
    uri: 'armor://platform/applications',
    name: 'Available Applications',
    description: 'List of applications in the Armor suite',
    mimeType: 'application/json',
  },
];
```

### 4.2 Resource Templates

```typescript
const resourceTemplates: MCPResourceTemplate[] = [
  {
    uriTemplate: 'armor://armor-dash/alerts/{alertId}',
    name: 'Alert Details',
    description: 'Detailed information about a specific alert',
    mimeType: 'application/json',
  },
  {
    uriTemplate: 'armor://armor-dash/assets/{assetId}',
    name: 'Asset Details',
    description: 'Detailed information about a specific asset',
    mimeType: 'application/json',
  },
  {
    uriTemplate: 'armor://armor-dash/vulnerabilities/{vulnId}',
    name: 'Vulnerability Details',
    description: 'Detailed vulnerability information',
    mimeType: 'application/json',
  },
];
```

---

## 5. MCP Prompts

### 5.1 Security Analysis Prompts

```typescript
const prompts: MCPPrompt[] = [
  {
    name: 'security_posture_review',
    description: 'Comprehensive review of current security posture',
    arguments: [
      {
        name: 'focus_area',
        description: 'Specific area to focus on',
        required: false,
      },
    ],
    handler: async (args) => ({
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Please analyze our current security posture${
              args.focus_area ? ` with focus on ${args.focus_area}` : ''
            }. Include:
            1. Current security score and trend
            2. Critical and high severity open alerts
            3. Top vulnerabilities requiring attention
            4. Compliance status across frameworks
            5. Connector health status
            6. Recommended priority actions`,
          },
        },
      ],
    }),
  },
  {
    name: 'incident_triage',
    description: 'Triage and analyze a security incident',
    arguments: [
      {
        name: 'alert_id',
        description: 'Alert ID to triage',
        required: true,
      },
    ],
    handler: async (args) => ({
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Please help me triage alert ${args.alert_id}:
            1. Summarize what this alert is about
            2. Identify affected assets and potential blast radius
            3. Assess severity and urgency
            4. Check for related alerts or findings
            5. Recommend immediate actions
            6. Suggest long-term remediation steps`,
          },
        },
      ],
    }),
  },
  {
    name: 'vulnerability_prioritization',
    description: 'Prioritize vulnerabilities for remediation',
    arguments: [
      {
        name: 'max_items',
        description: 'Maximum vulnerabilities to analyze',
        required: false,
      },
    ],
    handler: async (args) => ({
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Analyze and prioritize vulnerabilities for remediation:
            1. List the top ${args.max_items || 10} vulnerabilities by risk
            2. Consider CVSS score, exploitability, and asset criticality
            3. Group by affected systems or teams
            4. Estimate remediation effort
            5. Suggest a prioritized remediation plan`,
          },
        },
      ],
    }),
  },
  {
    name: 'compliance_gap_analysis',
    description: 'Analyze compliance gaps and remediation',
    arguments: [
      {
        name: 'framework',
        description: 'Specific framework to analyze',
        required: false,
      },
    ],
    handler: async (args) => ({
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Perform a compliance gap analysis${
              args.framework ? ` for ${args.framework}` : ' across all frameworks'
            }:
            1. Identify failing controls
            2. Assess severity and audit risk
            3. Map to technical findings
            4. Recommend remediation steps
            5. Estimate effort and timeline`,
          },
        },
      ],
    }),
  },
];
```

---

## 6. Installation & Configuration

### 6.1 Claude Code Integration

```json
// ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "armor-platform": {
      "command": "npx",
      "args": ["@armor/mcp-server"],
      "env": {
        "ARMOR_CLIENT_ID": "${ARMOR_CLIENT_ID}",
        "ARMOR_CLIENT_SECRET": "${ARMOR_CLIENT_SECRET}",
        "ARMOR_ACCOUNT_ID": "${ARMOR_ACCOUNT_ID}",
        "ARMOR_ENVIRONMENT": "production",
        "ARMOR_DEFAULT_APP": "armor-dash"
      }
    }
  }
}
```

### 6.2 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ARMOR_CLIENT_ID` | Yes | OAuth 2.0 client ID |
| `ARMOR_CLIENT_SECRET` | Yes | OAuth 2.0 client secret |
| `ARMOR_ACCOUNT_ID` | Yes | Default account ID |
| `ARMOR_ENVIRONMENT` | No | `production`, `staging`, `sandbox` |
| `ARMOR_DEFAULT_APP` | No | Default app: `armor-dash`, `nexus`, `legacy-amp` |
| `ARMOR_LOG_LEVEL` | No | `debug`, `info`, `warn`, `error` |

### 6.3 Alternative Installation (npm global)

```bash
# Install globally
npm install -g @armor/mcp-server

# Configure environment
export ARMOR_CLIENT_ID="your-client-id"
export ARMOR_CLIENT_SECRET="your-client-secret"
export ARMOR_ACCOUNT_ID="your-account-id"

# Run server
armor-mcp-server
```

---

## 7. Tool Categories & Permissions

### 7.1 Permission Mapping

| Tool | Required Permission | Application |
|------|---------------------|-------------|
| `armor_list_alerts` | `alerts:read` | Armor-Dash |
| `armor_acknowledge_alert` | `alerts:write` | Armor-Dash |
| `armor_resolve_alert` | `alerts:write` | Armor-Dash |
| `armor_list_vulnerabilities` | `vulnerabilities:read` | Armor-Dash |
| `armor_get_security_score` | `metrics:read` | Armor-Dash |
| `armor_get_compliance_status` | `compliance:read` | Armor-Dash |
| `armor_list_connectors` | `connectors:read` | Armor-Dash |
| `armor_sync_connector` | `connectors:write` | Armor-Dash |
| `armor_generate_report` | `reports:write` | Armor-Dash |
| `nexus_get_account` | `account:read` | Nexus |
| `nexus_list_users` | `users:read` | Nexus |
| `armor_ask_security_question` | `ai:query` | Cross-App |

### 7.2 Rate Limits

| Tool Category | Requests/min | Requests/hour |
|---------------|--------------|---------------|
| Read operations | 60 | 3,000 |
| Write operations | 30 | 500 |
| AI/RAG queries | 20 | 200 |
| Report generation | 5 | 50 |

---

## 8. Error Handling

### 8.1 Error Response Format

```typescript
interface MCPError {
  code: string;
  message: string;
  details?: {
    tool?: string;
    parameter?: string;
    suggestion?: string;
  };
}

// Example errors
const errors = {
  'auth/token_expired': {
    message: 'Access token has expired. Please re-authenticate.',
    suggestion: 'Restart the MCP server to refresh authentication.',
  },
  'permission/insufficient': {
    message: 'Insufficient permissions for this operation.',
    suggestion: 'Contact your administrator to request the required permission.',
  },
  'rate_limit/exceeded': {
    message: 'Rate limit exceeded.',
    suggestion: 'Wait before making more requests.',
  },
  'resource/not_found': {
    message: 'The requested resource was not found.',
    suggestion: 'Verify the resource ID is correct.',
  },
};
```

### 8.2 Graceful Degradation

```typescript
// If a service is unavailable, return partial data
async function handlePartialFailure(tools: ToolCall[]): Promise<ToolResult[]> {
  const results = await Promise.allSettled(
    tools.map(tool => executeToolCall(tool))
  );

  return results.map((result, index) => {
    if (result.status === 'fulfilled') {
      return result.value;
    }
    return {
      toolName: tools[index].name,
      error: {
        code: 'service/partial_failure',
        message: 'Some data may be unavailable',
        details: { originalError: result.reason.message },
      },
      partialData: getCachedData(tools[index]),
    };
  });
}
```

---

## 9. Example Usage Scenarios

### 9.1 Security Review Workflow

```
User: "Give me a security overview"

Claude: I'll analyze your current security posture.

[Calls armor_get_security_score]
[Calls armor_list_alerts with severity: ["critical", "high"]]
[Calls armor_get_connector_health]
[Calls armor_get_compliance_status]

Your security overview:

**Security Score: 72/100** (↓ 3 points from last week)

**Open Alerts:**
- 2 Critical: Ransomware detected on 3 endpoints
- 5 High: Unpatched Exchange vulnerability CVE-2024-1234

**Connector Status:**
- CrowdStrike: ✅ Healthy (synced 2 min ago)
- Tenable: ✅ Healthy (synced 5 min ago)
- Splunk: ⚠️ Rate limited (synced 30 min ago)

**Compliance:**
- SOC 2: 94% compliant
- PCI-DSS: 87% compliant (3 controls failing)

Would you like me to investigate any specific alerts?
```

### 9.2 Incident Response Workflow

```
User: "Triage alert ALT-2024-0042"

Claude: I'll analyze this alert in detail.

[Calls armor_get_alert with alertId: "ALT-2024-0042"]
[Calls armor_list_alerts to find related alerts]
[Calls armor_suggest_remediation]

**Alert Triage: ALT-2024-0042**

**Summary:** Suspected lateral movement detected
**Severity:** Critical
**Source:** CrowdStrike

**Affected Assets:**
- PROD-WEB-01 (Web Server)
- PROD-DB-02 (Database Server)

**Related Alerts:**
- ALT-2024-0039: Initial access via phishing (resolved)
- ALT-2024-0040: Credential harvesting (open)
- ALT-2024-0041: Privilege escalation attempt (open)

**Recommended Immediate Actions:**
1. Isolate affected endpoints from network
2. Reset compromised credentials
3. Review authentication logs

**Long-term Remediation:**
1. Implement network segmentation
2. Deploy MFA for all admin accounts
3. Enable real-time threat detection

Shall I acknowledge this alert and assign it to your SOC team?
```

---

## 10. Development Roadmap

### Phase 1: Core Tools (MVP)
- [ ] Authentication and token management
- [ ] Alert management tools (list, get, acknowledge, resolve)
- [ ] Security score and metrics
- [ ] Connector health monitoring

### Phase 2: Advanced Queries
- [ ] Vulnerability management tools
- [ ] Compliance status tools
- [ ] Asset inventory tools
- [ ] RAG-powered security Q&A

### Phase 3: Actions & Automation
- [ ] Report generation
- [ ] Webhook management
- [ ] Connector sync triggers
- [ ] Bulk operations

### Phase 4: Multi-App Context
- [ ] Application switching
- [ ] Cross-app search
- [ ] Nexus platform tools
- [ ] Legacy AMP integration

---

## Appendix: Complete Tool Registry

```typescript
export const toolRegistry: MCPTool[] = [
  // armor-dash: Alerts
  listAlertsTool,
  getAlertTool,
  acknowledgeAlertTool,
  resolveAlertTool,

  // armor-dash: Vulnerabilities
  listVulnerabilitiesTool,
  getVulnerabilityTrendTool,

  // armor-dash: Metrics
  getSecurityScoreTool,
  getRiskSummaryTool,

  // armor-dash: Compliance
  getComplianceStatusTool,
  listComplianceGapsTool,

  // armor-dash: Connectors
  listConnectorsTool,
  getConnectorHealthTool,
  syncConnectorTool,

  // Nexus: Account & Users
  getAccountTool,
  listUsersTool,
  listTeamsTool,

  // AI Assistant
  askSecurityQuestionTool,
  explainFindingTool,
  suggestRemediationTool,
  generateReportTool,

  // Platform Navigation
  switchApplicationTool,
  listApplicationsTool,
];
```

---

## Related Diagrams

### Figure 1: MCP Integration Architecture
*Complete MCP server architecture from AI clients to platform APIs.*

> **Diagram:** [MCP Integration Architecture](../diagrams/architecture/03-mcp-integration.md)
>
> Shows:
> - AI client connections (Claude Code, Claude Web, Custom Agents)
> - MCP Server components (protocol handler, registries)
> - Authentication flow (OAuth2, RBAC)
> - Tool categories (35+ tools)
> - Resource and prompt registries
> - Deployment architecture

### Figure 2: Authentication Flow
*OAuth2 / OIDC authentication for MCP access.*

> **Diagram:** [Auth Flow](../diagrams/security/01-auth-flow.md)
>
> Covers MCP-relevant authentication including:
> - Client credentials grant for MCP clients
> - Token refresh patterns
> - Permission validation

---

*This specification is maintained by the Platform Engineering team.*
