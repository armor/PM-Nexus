# MCP Security Model

## Overview

This diagram documents the security architecture for the Model Context Protocol (MCP) integration, covering authentication, authorization, and data protection for AI assistant access to the Armor platform.

## Security Architecture Overview

```mermaid
graph TB
    subgraph "Threat Surface"
        TS1[Unauthorized Access<br/>Stolen credentials]
        TS2[Data Exfiltration<br/>Sensitive data exposure]
        TS3[Privilege Escalation<br/>Unauthorized operations]
        TS4[API Abuse<br/>Rate limit bypass]
        TS5[Injection Attacks<br/>Malicious tool input]
    end

    subgraph "Defense Layers"
        subgraph "Layer 1: Transport"
            T1[TLS 1.3 Encryption]
            T2[Process Isolation<br/>STDIO]
            T3[Network Segmentation]
        end

        subgraph "Layer 2: Authentication"
            A1[OAuth2 Client Credentials]
            A2[Token Validation<br/>JWT RS256]
            A3[Token Rotation<br/>Short-lived tokens]
        end

        subgraph "Layer 3: Authorization"
            Z1[RBAC Permission Check]
            Z2[Scope Validation]
            Z3[Resource-Level Access]
        end

        subgraph "Layer 4: Input Validation"
            V1[Schema Validation<br/>JSON Schema]
            V2[Parameter Sanitization]
            V3[Query Limits<br/>Max results]
        end

        subgraph "Layer 5: Rate Limiting"
            R1[Per-User Quotas]
            R2[Per-Tool Limits]
            R3[Burst Protection]
        end

        subgraph "Layer 6: Audit"
            AU1[Tool Invocation Logs]
            AU2[Access Audit Trail]
            AU3[Anomaly Detection]
        end
    end

    TS1 --> T1
    TS1 --> A1
    TS2 --> Z1
    TS2 --> AU1
    TS3 --> Z1
    TS3 --> Z2
    TS4 --> R1
    TS5 --> V1

    classDef threat fill:#FEB2B2,stroke:#333
    classDef defense fill:#68D391,stroke:#333

    class TS1,TS2,TS3,TS4,TS5 threat
    class T1,T2,T3,A1,A2,A3,Z1,Z2,Z3,V1,V2,V3,R1,R2,R3,AU1,AU2,AU3 defense
```

<!-- SVG: 03-mcp-security-model-1.svg -->
![Diagram 1](../../diagrams-svg/security/03-mcp-security-model-1.svg)


## Authentication Architecture

```mermaid
sequenceDiagram
    participant Client as MCP Client<br/>(Claude Code)
    participant MCP as MCP Server
    participant Auth as Okta Auth Server
    participant KMS as AWS KMS

    Note over Client,KMS: Initial Authentication

    Client->>Client: Load encrypted credentials<br/>from ~/.armor/credentials
    Client->>KMS: Decrypt client_secret
    KMS-->>Client: Decrypted secret
    Client->>MCP: Connect + auth request

    MCP->>Auth: POST /oauth2/token<br/>grant_type=client_credentials<br/>client_id + client_secret
    Auth->>Auth: Validate credentials
    Auth->>Auth: Check account status
    Auth->>Auth: Generate access_token (JWT)
    Auth-->>MCP: access_token + refresh_token<br/>expires_in=3600

    MCP->>MCP: Validate JWT signature (RS256)
    MCP->>MCP: Extract claims<br/>(account_id, permissions)
    MCP->>MCP: Cache token securely
    MCP-->>Client: Connection authenticated

    Note over Client,KMS: Token never logged or stored in plaintext
```

<!-- SVG: 03-mcp-security-model-2.svg -->
![Diagram 2](../../diagrams-svg/security/03-mcp-security-model-2.svg)


## Permission Model

```mermaid
graph TB
    subgraph "Permission Hierarchy"
        subgraph "Account Level"
            ACC[Account Admin<br/>Full MCP access]
        end

        subgraph "Application Scopes"
            AD_W[armor-dash:write<br/>Modify security data]
            AD_R[armor-dash:read<br/>View security data]
            NX_W[nexus:write<br/>Modify platform]
            NX_R[nexus:read<br/>View platform]
        end

        subgraph "Resource Permissions"
            ALERT_R[alerts:read]
            ALERT_W[alerts:write]
            VULN_R[vulnerabilities:read]
            ASSET_R[assets:read]
            ASSET_W[assets:write]
            CONN_R[connectors:read]
            CONN_W[connectors:write]
            USER_R[users:read]
            USER_W[users:write]
        end

        subgraph "Tool Access"
            T_LIST[armor_list_alerts]
            T_ACK[armor_acknowledge_alert]
            T_USERS[nexus_list_users]
            T_SYNC[armor_sync_connector]
        end

        ACC --> AD_W
        ACC --> AD_R
        ACC --> NX_W
        ACC --> NX_R

        AD_R --> ALERT_R
        AD_R --> VULN_R
        AD_R --> ASSET_R
        AD_R --> CONN_R

        AD_W --> ALERT_W
        AD_W --> ASSET_W
        AD_W --> CONN_W

        NX_R --> USER_R
        NX_W --> USER_W

        ALERT_R --> T_LIST
        ALERT_W --> T_ACK
        USER_R --> T_USERS
        CONN_W --> T_SYNC
    end

    classDef acc fill:#DDD6FE
    classDef scope fill:#A5F3FC
    classDef perm fill:#FED7AA
    classDef tool fill:#68D391

    class ACC acc
    class AD_W,AD_R,NX_W,NX_R scope
    class ALERT_R,ALERT_W,VULN_R,ASSET_R,ASSET_W,CONN_R,CONN_W,USER_R,USER_W perm
    class T_LIST,T_ACK,T_USERS,T_SYNC tool
```

<!-- SVG: 03-mcp-security-model-3.svg -->
![Diagram 3](../../diagrams-svg/security/03-mcp-security-model-3.svg)


## Authorization Flow

```mermaid
flowchart TD
    A[Tool Invocation Request] --> B{Token Present?}
    B -->|No| C[Reject: AUTH_REQUIRED]
    B -->|Yes| D{Token Valid?}

    D -->|Expired| E{Refresh Token?}
    E -->|No| C
    E -->|Yes| F[Refresh Access Token]
    F -->|Success| G
    F -->|Failure| C

    D -->|Invalid Signature| C
    D -->|Valid| G{Account Active?}

    G -->|Suspended| H[Reject: ACCOUNT_SUSPENDED]
    G -->|Active| I{Has Required Scope?}

    I -->|No| J[Reject: INSUFFICIENT_SCOPE]
    I -->|Yes| K{Has Resource Permission?}

    K -->|No| L[Reject: PERMISSION_DENIED]
    K -->|Yes| M{Within Rate Limit?}

    M -->|No| N[Reject: RATE_LIMITED<br/>Retry-After header]
    M -->|Yes| O{Input Valid?}

    O -->|No| P[Reject: INVALID_PARAMS]
    O -->|Yes| Q[Execute Tool]

    Q --> R[Log Audit Event]
    R --> S[Return Result]

    style C fill:#FEB2B2
    style H fill:#FEB2B2
    style J fill:#FEB2B2
    style L fill:#FEB2B2
    style N fill:#FED7AA
    style P fill:#FEB2B2
    style S fill:#9AE6B4
```

<!-- SVG: 03-mcp-security-model-4.svg -->
![Diagram 4](../../diagrams-svg/security/03-mcp-security-model-4.svg)


## Input Validation

```mermaid
graph LR
    subgraph "Validation Pipeline"
        I[Raw Input] --> V1[Schema Validation<br/>JSON Schema]
        V1 --> V2[Type Coercion<br/>String → Number]
        V2 --> V3[Range Checks<br/>limit ≤ 100]
        V3 --> V4[Sanitization<br/>Trim, escape]
        V4 --> V5[Business Rules<br/>Valid enum values]
        V5 --> O[Validated Input]
    end

    subgraph "Injection Protection"
        IP1[SQL Injection<br/>Parameterized queries]
        IP2[Command Injection<br/>No shell execution]
        IP3[Path Traversal<br/>Path normalization]
        IP4[XSS<br/>Output encoding]
    end

    V4 --> IP1
    V4 --> IP2
    V4 --> IP3
    V4 --> IP4

    classDef valid fill:#68D391
    classDef protect fill:#A5F3FC

    class V1,V2,V3,V4,V5 valid
    class IP1,IP2,IP3,IP4 protect
```

<!-- SVG: 03-mcp-security-model-5.svg -->
![Diagram 5](../../diagrams-svg/security/03-mcp-security-model-5.svg)


## Data Protection

```mermaid
graph TB
    subgraph "Sensitive Data Handling"
        subgraph "Classification"
            C1[PII<br/>Names, emails]
            C2[Credentials<br/>API keys, tokens]
            C3[Security Data<br/>Vulnerabilities]
            C4[Financial<br/>Billing info]
        end

        subgraph "Protection Measures"
            P1[Encryption at Rest<br/>AES-256]
            P2[Encryption in Transit<br/>TLS 1.3]
            P3[Field-Level Encryption<br/>Sensitive fields]
            P4[Tokenization<br/>Replace with tokens]
        end

        subgraph "Access Controls"
            A1[Role-Based Access]
            A2[Need-to-Know]
            A3[Data Minimization]
            A4[Audit Logging]
        end

        subgraph "Output Filtering"
            O1[Redact Secrets<br/>**** masking]
            O2[Limit Fields<br/>Projection]
            O3[Aggregate Only<br/>No raw data]
        end

        C1 --> P1
        C2 --> P3
        C3 --> A1
        C4 --> P3

        P1 --> A2
        P3 --> O1
        A1 --> O2
    end

    classDef sensitive fill:#FEB2B2
    classDef protect fill:#68D391
    classDef control fill:#A5F3FC
    classDef output fill:#FED7AA

    class C1,C2,C3,C4 sensitive
    class P1,P2,P3,P4 protect
    class A1,A2,A3,A4 control
    class O1,O2,O3 output
```

<!-- SVG: 03-mcp-security-model-6.svg -->
![Diagram 6](../../diagrams-svg/security/03-mcp-security-model-6.svg)


## Rate Limiting Architecture

```mermaid
graph TB
    subgraph "Rate Limit Tiers"
        subgraph "Account Limits"
            AL1[Free: 60/min]
            AL2[Pro: 300/min]
            AL3[Enterprise: 1000/min]
        end

        subgraph "Tool-Specific Limits"
            TL1[Read Operations<br/>10/sec]
            TL2[Write Operations<br/>2/sec]
            TL3[Sync Operations<br/>1/min]
        end

        subgraph "Burst Protection"
            BP1[Token Bucket<br/>Smooth traffic]
            BP2[Sliding Window<br/>Fair distribution]
        end
    end

    subgraph "Enforcement"
        E1[Redis Counter<br/>Distributed tracking]
        E2[429 Response<br/>Retry-After header]
        E3[Backoff Strategy<br/>Exponential]
    end

    AL1 --> E1
    AL2 --> E1
    AL3 --> E1
    TL1 --> BP1
    TL2 --> BP2
    TL3 --> E1
    E1 --> E2
    E2 --> E3

    classDef tier fill:#A5F3FC
    classDef enforce fill:#FED7AA

    class AL1,AL2,AL3,TL1,TL2,TL3,BP1,BP2 tier
    class E1,E2,E3 enforce
```

<!-- SVG: 03-mcp-security-model-7.svg -->
![Diagram 7](../../diagrams-svg/security/03-mcp-security-model-7.svg)


## Audit Trail

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant MCP as MCP Server
    participant Log as Audit Logger
    participant SIEM as SIEM/SigNoz
    participant Alert as Alert System

    Note over Client,Alert: Every tool invocation is logged

    Client->>MCP: CallTool(armor_list_alerts)
    MCP->>Log: Log request<br/>{timestamp, user, tool, params, ip}
    MCP->>MCP: Execute tool
    MCP->>Log: Log response<br/>{status, duration, result_count}
    Log->>SIEM: Forward to SIEM
    MCP-->>Client: Tool result

    Note over Client,Alert: Anomaly Detection

    SIEM->>SIEM: Analyze patterns
    SIEM->>SIEM: Detect anomaly<br/>(unusual volume, time, tool)
    SIEM->>Alert: Trigger alert
    Alert->>Alert: Notify security team

    Note over Client,Alert: Audit Log Contents

    Note right of Log: - Timestamp (ISO 8601)<br/>- Request ID (UUID)<br/>- User ID / Service Account<br/>- Account ID<br/>- Tool name<br/>- Parameters (sanitized)<br/>- Source IP<br/>- User Agent<br/>- Response status<br/>- Duration (ms)<br/>- Error details (if any)
```

<!-- SVG: 03-mcp-security-model-8.svg -->
![Diagram 8](../../diagrams-svg/security/03-mcp-security-model-8.svg)


## Secret Management

```mermaid
graph TB
    subgraph "Secrets Lifecycle"
        subgraph "Storage"
            S1[AWS Secrets Manager<br/>Encrypted at rest]
            S2[Environment Variables<br/>Runtime injection]
            S3[Credential File<br/>Local encrypted]
        end

        subgraph "Rotation"
            R1[Automatic Rotation<br/>90-day policy]
            R2[Emergency Rotation<br/>Compromise response]
            R3[Version History<br/>Audit trail]
        end

        subgraph "Access Control"
            A1[IAM Roles<br/>Least privilege]
            A2[Service Accounts<br/>Dedicated identity]
            A3[No Human Access<br/>Programmatic only]
        end

        subgraph "Never Allowed"
            N1[Hard-coded secrets]
            N2[Logged credentials]
            N3[Unencrypted storage]
            N4[Shared credentials]
        end

        S1 --> R1
        S1 --> A1
        S2 --> A2
        S3 --> A2

        R1 --> R3
        R2 --> R3
    end

    classDef store fill:#68D391
    classDef rotate fill:#A5F3FC
    classDef access fill:#FED7AA
    classDef never fill:#FEB2B2

    class S1,S2,S3 store
    class R1,R2,R3 rotate
    class A1,A2,A3 access
    class N1,N2,N3,N4 never
```

<!-- SVG: 03-mcp-security-model-9.svg -->
![Diagram 9](../../diagrams-svg/security/03-mcp-security-model-9.svg)


## Threat Mitigation Matrix

| Threat | Mitigation | Control |
|--------|------------|---------|
| **Credential Theft** | Client credentials grant, short-lived tokens | OAuth2 |
| **Token Replay** | JWT expiry (1 hour), single-use refresh | Token validation |
| **Privilege Escalation** | RBAC, scope validation, resource-level checks | Authorization |
| **Data Exfiltration** | Field-level access, result limits, audit logging | Data protection |
| **API Abuse** | Rate limiting, burst protection, anomaly detection | Rate limiting |
| **Injection Attacks** | Schema validation, parameterized queries, sanitization | Input validation |
| **Man-in-the-Middle** | TLS 1.3, certificate pinning | Transport security |
| **Insider Threat** | Least privilege, audit trail, anomaly detection | Access control |

## Security Requirements Checklist

### Authentication
- [ ] OAuth2 client credentials flow implemented
- [ ] JWT validation with RS256 signature
- [ ] Token refresh before expiry
- [ ] Secure credential storage (encrypted)
- [ ] No credentials in logs

### Authorization
- [ ] RBAC permission model
- [ ] Scope-based access control
- [ ] Resource-level permissions
- [ ] Permission caching with invalidation

### Input Validation
- [ ] JSON Schema validation for all tools
- [ ] Parameter sanitization
- [ ] Query result limits
- [ ] Injection protection

### Rate Limiting
- [ ] Per-account quotas
- [ ] Per-tool limits
- [ ] Burst protection
- [ ] Retry-After headers

### Audit & Monitoring
- [ ] All tool invocations logged
- [ ] Log forwarding to SIEM
- [ ] Anomaly detection rules
- [ ] Alerting on suspicious activity

### Data Protection
- [ ] Encryption at rest
- [ ] Encryption in transit (TLS 1.3)
- [ ] Sensitive field redaction
- [ ] Data minimization in responses

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Architecture | [MCP Integration](../architecture/03-mcp-integration.md) | MCP architecture overview |
| Security | [Auth Flow](./01-auth-flow.md) | OAuth2/OIDC details |
| Security | [RBAC Model](./02-rbac-model.md) | Permission structure |

---

## Related Documentation

- [MCP Server Specification](../../planning-artifacts/20-mcp-server-specification.md) - Full MCP implementation
- [Security & Compliance](../../planning-artifacts/08-security-compliance.md) - Platform security requirements
- [API Developer Experience](../../planning-artifacts/18-api-developer-experience.md) - API security

---

Last Updated: 2026-01-04
Maintained By: Security Team
