# MCP Integration Architecture

## Overview

This diagram shows the Model Context Protocol (MCP) integration architecture, enabling AI assistants like Claude to interact with the Armor platform suite.

## MCP Server Architecture

```mermaid
graph TB
    subgraph "AI Clients"
        CC[Claude Code<br/>CLI/IDE]
        CW[Claude Web<br/>API Client]
        CA[Custom Agent<br/>Agent SDK]
    end

    subgraph "MCP Transport Layer"
        STDIO[STDIO Transport<br/>Local Process]
        HTTP[HTTP/SSE Transport<br/>Remote Server]
    end

    subgraph "Armor MCP Server"
        MS[MCP Protocol Handler<br/>@modelcontextprotocol/sdk]

        subgraph "Authentication"
            AUTH[Authenticator<br/>OAuth2 Client Credentials]
            PERM[Permission Checker<br/>RBAC Validation]
        end

        subgraph "Registries"
            TR[Tool Registry<br/>35+ Tools]
            RR[Resource Registry<br/>Dashboards, Config]
            PR[Prompt Registry<br/>Analysis Templates]
        end

        subgraph "Context Manager"
            CTX[Session Context<br/>Account, User, App]
            CACHE[Response Cache<br/>TTL-based]
        end
    end

    subgraph "Internal Services"
        AC[API Client<br/>Fastify Backend]
        RL[Rate Limiter<br/>Per-User Quotas]
        LOG[Logger<br/>Audit Trail]
    end

    subgraph "Armor Platform APIs"
        AD[Armor-Dash API<br/>Security Operations]
        NX[Nexus API<br/>Platform Management]
        LA[Legacy AMP API<br/>Existing Features]
    end

    CC --> STDIO
    CW --> HTTP
    CA --> HTTP
    STDIO --> MS
    HTTP --> MS

    MS --> AUTH
    AUTH --> PERM
    PERM --> TR
    PERM --> RR
    PERM --> PR

    MS --> CTX
    CTX --> CACHE

    TR --> AC
    RR --> AC
    PR --> AC

    AC --> RL
    RL --> LOG
    LOG --> AD
    LOG --> NX
    LOG --> LA

    classDef client fill:#61DAFB,stroke:#333
    classDef transport fill:#A5F3FC,stroke:#333
    classDef mcp fill:#F687B3,stroke:#333
    classDef internal fill:#FED7AA,stroke:#333
    classDef api fill:#68D391,stroke:#333

    class CC,CW,CA client
    class STDIO,HTTP transport
    class MS,AUTH,PERM,TR,RR,PR,CTX,CACHE mcp
    class AC,RL,LOG internal
    class AD,NX,LA api
```

<!-- SVG: 03-mcp-integration-1.svg -->
![Diagram 1](../../diagrams-svg/architecture/03-mcp-integration-1.svg)


## Tool Categories

```mermaid
graph LR
    subgraph "Armor-Dash Tools (Security)"
        AD1[armor_list_alerts]
        AD2[armor_get_alert]
        AD3[armor_acknowledge_alert]
        AD4[armor_resolve_alert]
        AD5[armor_list_vulnerabilities]
        AD6[armor_get_vulnerability]
        AD7[armor_list_assets]
        AD8[armor_get_asset]
        AD9[armor_get_compliance_status]
        AD10[armor_list_connectors]
        AD11[armor_get_metrics]
    end

    subgraph "Nexus Tools (Platform)"
        NX1[nexus_list_accounts]
        NX2[nexus_get_account]
        NX3[nexus_list_users]
        NX4[nexus_get_user]
        NX5[nexus_list_teams]
        NX6[nexus_get_settings]
        NX7[nexus_update_settings]
    end

    subgraph "Shared Tools"
        SH1[armor_search<br/>Cross-app search]
        SH2[armor_generate_report<br/>PDF/CSV export]
        SH3[armor_ask_assistant<br/>AI Q&A]
        SH4[armor_switch_application<br/>App context switch]
    end

    classDef security fill:#FEB2B2
    classDef platform fill:#BBF7D0
    classDef shared fill:#DDD6FE

    class AD1,AD2,AD3,AD4,AD5,AD6,AD7,AD8,AD9,AD10,AD11 security
    class NX1,NX2,NX3,NX4,NX5,NX6,NX7 platform
    class SH1,SH2,SH3,SH4 shared
```

<!-- SVG: 03-mcp-integration-2.svg -->
![Diagram 2](../../diagrams-svg/architecture/03-mcp-integration-2.svg)


## Authentication Flow

```mermaid
sequenceDiagram
    participant AI as Claude/AI Client
    participant MCP as MCP Server
    participant Auth as Okta Auth
    participant API as Platform API

    Note over AI,API: Initial Authentication
    AI->>MCP: Connect (STDIO/HTTP)
    MCP->>MCP: Load ARMOR_CLIENT_ID/SECRET
    MCP->>Auth: POST /oauth2/token<br/>client_credentials grant
    Auth-->>MCP: access_token + refresh_token
    MCP->>MCP: Cache token (expires_in)
    MCP-->>AI: Connection ready

    Note over AI,API: Tool Invocation
    AI->>MCP: CallTool(armor_list_alerts)
    MCP->>MCP: Validate token
    MCP->>MCP: Check permissions
    MCP->>API: GET /api/v1/alerts<br/>Authorization: Bearer {token}
    API-->>MCP: alerts[]
    MCP->>MCP: Format response
    MCP-->>AI: Tool result

    Note over AI,API: Token Refresh
    AI->>MCP: CallTool(armor_list_assets)
    MCP->>MCP: Token expired?
    MCP->>Auth: POST /oauth2/token<br/>refresh_token grant
    Auth-->>MCP: New access_token
    MCP->>API: GET /api/v1/assets
    API-->>MCP: assets[]
    MCP-->>AI: Tool result
```

<!-- SVG: 03-mcp-integration-3.svg -->
![Diagram 3](../../diagrams-svg/architecture/03-mcp-integration-3.svg)


## Resource Types

```mermaid
graph TB
    subgraph "MCP Resources"
        subgraph "Dashboards"
            D1[armor://dashboards/overview<br/>Security overview metrics]
            D2[armor://dashboards/risk<br/>Risk posture]
            D3[armor://dashboards/compliance<br/>Compliance status]
            D4[armor://dashboards/operations<br/>SOC metrics]
        end

        subgraph "Configuration"
            C1[armor://config/connectors<br/>Active integrations]
            C2[armor://config/alerts<br/>Alert rules]
            C3[armor://config/users<br/>Team members]
        end

        subgraph "Documentation"
            DOC1[armor://docs/api<br/>API reference]
            DOC2[armor://docs/runbooks<br/>Response procedures]
            DOC3[armor://docs/policies<br/>Security policies]
        end
    end

    classDef dashboard fill:#A5F3FC
    classDef config fill:#FED7AA
    classDef docs fill:#BBF7D0

    class D1,D2,D3,D4 dashboard
    class C1,C2,C3 config
    class DOC1,DOC2,DOC3 docs
```

<!-- SVG: 03-mcp-integration-4.svg -->
![Diagram 4](../../diagrams-svg/architecture/03-mcp-integration-4.svg)


## Prompt Templates

```mermaid
graph LR
    subgraph "Security Analysis Prompts"
        P1[security_analysis<br/>Analyze security posture]
        P2[threat_assessment<br/>Assess threat landscape]
        P3[incident_response<br/>Guide incident response]
    end

    subgraph "Remediation Prompts"
        R1[vulnerability_remediation<br/>Patch guidance]
        R2[compliance_gap<br/>Fix compliance issues]
        R3[risk_mitigation<br/>Risk reduction steps]
    end

    subgraph "Report Prompts"
        REP1[executive_summary<br/>C-level report]
        REP2[technical_report<br/>SOC team report]
        REP3[compliance_report<br/>Audit preparation]
    end

    classDef analysis fill:#FEB2B2
    classDef remediation fill:#FEF08A
    classDef report fill:#DDD6FE

    class P1,P2,P3 analysis
    class R1,R2,R3 remediation
    class REP1,REP2,REP3 report
```

<!-- SVG: 03-mcp-integration-5.svg -->
![Diagram 5](../../diagrams-svg/architecture/03-mcp-integration-5.svg)


## Multi-Application Context

```mermaid
stateDiagram-v2
    [*] --> ArmorDash: Default app

    ArmorDash --> Nexus: armor_switch_application("nexus")
    Nexus --> ArmorDash: armor_switch_application("armor-dash")
    ArmorDash --> LegacyAMP: armor_switch_application("legacy-amp")
    LegacyAMP --> ArmorDash: armor_switch_application("armor-dash")
    Nexus --> LegacyAMP: armor_switch_application("legacy-amp")
    LegacyAMP --> Nexus: armor_switch_application("nexus")

    state ArmorDash {
        [*] --> SecurityOps
        SecurityOps: Alerts, Vulns, Assets
        SecurityOps --> Compliance
        Compliance: Controls, Frameworks
        Compliance --> Connectors
        Connectors: 45+ Integrations
    }

    state Nexus {
        [*] --> AccountMgmt
        AccountMgmt: Accounts, Billing
        AccountMgmt --> UserMgmt
        UserMgmt: Users, Teams, Roles
        UserMgmt --> Settings
        Settings: Configuration
    }

    state LegacyAMP {
        [*] --> LegacyFeatures
        LegacyFeatures: Existing Apps
        LegacyFeatures --> Migration
        Migration: Data Migration
    }
```

<!-- SVG: 03-mcp-integration-6.svg -->
![Diagram 6](../../diagrams-svg/architecture/03-mcp-integration-6.svg)


## Deployment Architecture

```mermaid
graph TB
    subgraph "Local Development"
        DEV[Claude Code<br/>Developer Machine]
        LOCAL[MCP Server<br/>STDIO Transport]
        DEV --> LOCAL
        LOCAL -->|Direct API| DEVAPI[Dev API<br/>localhost:3000]
    end

    subgraph "Production"
        subgraph "AI Clients"
            PROD_CC[Claude Code<br/>Remote Connection]
            PROD_API[API Clients<br/>Programmatic]
        end

        subgraph "MCP Infrastructure"
            LB[Load Balancer<br/>ALB]
            MCP1[MCP Server Pod 1]
            MCP2[MCP Server Pod 2]
            MCP3[MCP Server Pod 3]
        end

        subgraph "Platform Services"
            KONG[Kong Gateway<br/>Rate Limiting]
            PRODAPI[Platform APIs<br/>Fastify]
        end

        PROD_CC --> LB
        PROD_API --> LB
        LB --> MCP1
        LB --> MCP2
        LB --> MCP3
        MCP1 --> KONG
        MCP2 --> KONG
        MCP3 --> KONG
        KONG --> PRODAPI
    end

    classDef dev fill:#FEF08A
    classDef prod fill:#68D391
    classDef infra fill:#A5F3FC

    class DEV,LOCAL,DEVAPI dev
    class PROD_CC,PROD_API,LB,MCP1,MCP2,MCP3,KONG,PRODAPI prod
```

<!-- SVG: 03-mcp-integration-7.svg -->
![Diagram 7](../../diagrams-svg/architecture/03-mcp-integration-7.svg)


## Error Handling

```mermaid
flowchart TD
    A[Tool Invocation] --> B{Auth Valid?}
    B -->|No| C[MCPError: AUTH_REQUIRED]
    B -->|Yes| D{Permission?}
    D -->|No| E[MCPError: PERMISSION_DENIED]
    D -->|Yes| F{Rate Limited?}
    F -->|Yes| G[MCPError: RATE_LIMITED<br/>Retry-After header]
    F -->|No| H[Call API]
    H --> I{API Response}
    I -->|200 OK| J[Return Result]
    I -->|400 Bad Request| K[MCPError: INVALID_PARAMS]
    I -->|404 Not Found| L[MCPError: NOT_FOUND]
    I -->|500 Error| M[MCPError: INTERNAL_ERROR]
    I -->|Timeout| N[MCPError: TIMEOUT<br/>Suggest retry]

    style C fill:#FEB2B2
    style E fill:#FEB2B2
    style G fill:#FED7AA
    style K fill:#FEB2B2
    style L fill:#FEB2B2
    style M fill:#FEB2B2
    style N fill:#FED7AA
    style J fill:#9AE6B4
```

<!-- SVG: 03-mcp-integration-8.svg -->
![Diagram 8](../../diagrams-svg/architecture/03-mcp-integration-8.svg)


## Key Specifications

### Performance Targets

| Metric | Target | Description |
|--------|--------|-------------|
| Tool Response Time | <2s (P95) | Most tool invocations |
| Auth Token Refresh | <500ms | Background refresh |
| Resource Read | <1s | Dashboard/config access |
| Concurrent Clients | 100+ | Per MCP server pod |

### Rate Limits

| Tier | Requests/min | Burst | Notes |
|------|--------------|-------|-------|
| Free | 60 | 10 | Per account |
| Pro | 300 | 50 | Per account |
| Enterprise | 1000 | 100 | Custom limits |

### Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | OAuth2 client credentials |
| Authorization | RBAC permission checks |
| Transport Security | TLS 1.3 (HTTP), Process isolation (STDIO) |
| Audit Logging | All tool invocations logged |
| Token Storage | Encrypted, never logged |
| Secrets | AWS Secrets Manager |

---

## Related Documentation

- [MCP Server Specification](../../planning-artifacts/20-mcp-server-specification.md) - Full tool specifications
- [System Architecture](./01-system-architecture.md) - Overall platform architecture
- [Authentication Flow](../security/01-auth-flow.md) - OAuth2/OIDC details
- [API Developer Experience](../../planning-artifacts/18-api-developer-experience.md) - API design

---

Last Updated: 2026-01-04
Maintained By: Platform Engineering Team
