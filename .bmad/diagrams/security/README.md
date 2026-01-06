# Security Diagrams - Nexus UI Platform

This directory contains security architecture diagrams covering authentication, authorization, and access control for the Nexus UI platform.

## Diagram Index

### 1. [Authentication Flow](./01-auth-flow.md)
**Purpose:** Document OAuth 2.0 / OIDC login, session management, and logout flows

**Scope:** Login → Token exchange → Session creation → Token refresh → Logout

**Key Flows:**
- **Login:** User → Okta → Authorization code → Token exchange → Session JWT → Cookie
- **Token Refresh:** Background refresh before expiry, transparent to user
- **Session Validation:** JWT validation → Permission check → Request processing
- **Logout:** Session deletion → Okta logout → Cookie clearing → Redirect

**Security Controls:**
| Control | Implementation | Status |
|---------|----------------|--------|
| HTTPS Only | HSTS header, redirect | Required |
| JWT Signing | RS256 asymmetric | Required |
| Token Expiry | 1h access, 7d refresh | Required |
| Session Storage | Redis with encryption | Required |
| CSRF Protection | SameSite cookies | Required |
| Rate Limiting | Kong Gateway | Required |
| MFA | Okta Verify / TOTP | Required |

**Cookie Attributes:**
- `HttpOnly` - No JavaScript access
- `Secure` - HTTPS only
- `SameSite=Strict` - CSRF protection
- `Path=/` - Application-wide
- `Max-Age=3600` - 1 hour expiry

**Use Cases:**
- Debugging authentication issues
- Implementing new auth features
- Security audits
- Compliance documentation

---

### 2. [RBAC Model](./02-rbac-model.md)
**Purpose:** Document role-based access control and permission structure

**Scope:** Roles → Permissions → Resources → Access decisions

**Role Hierarchy:**
| Role | Description | Scope |
|------|-------------|-------|
| Super Admin | Full system access | Global |
| Org Admin | Organization management | Organization |
| Security Admin | Security operations | Organization |
| Analyst | View and investigate | Assigned teams |
| Viewer | Read-only access | Assigned resources |

**Permission Types:**
| Category | Permissions |
|----------|-------------|
| Dashboards | view, create, edit, delete, share |
| Alerts | view, acknowledge, assign, close, create |
| Assets | view, edit, tag, delete, export |
| Connectors | view, configure, test, sync, delete |
| Reports | view, create, schedule, export |
| Settings | view, edit (org, team, personal) |
| Users | view, invite, edit, deactivate |

**Access Decision Flow:**
```
Request → Extract User → Get Roles → Check Permissions → Resource Check → Allow/Deny
```

**Use Cases:**
- Implementing new permissions
- Debugging access issues
- Compliance audits (SOC2, ISO27001)
- User provisioning design

---

### 3. [MCP Security Model](./03-mcp-security-model.md)
**Purpose:** Document security architecture for AI assistant (MCP) access to the platform

**Scope:** Threat surface → Defense layers → Authentication → Authorization → Data protection → Audit

**Key Components:**
- **Threat Model:** Credential theft, data exfiltration, privilege escalation, API abuse, injection attacks
- **Defense Layers:** Transport, authentication, authorization, input validation, rate limiting, audit
- **Authentication:** OAuth2 client credentials, JWT RS256, token rotation
- **Authorization:** RBAC, scopes, resource-level permissions
- **Data Protection:** Encryption, field-level protection, redaction, minimization
- **Rate Limiting:** Account quotas, tool limits, burst protection
- **Audit:** Tool invocation logging, SIEM integration, anomaly detection

**Use Cases:**
- Security review of MCP integration
- Implementing MCP authentication
- Compliance audits
- Threat modeling

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Edge (CloudFront + WAF)                            │
│   - DDoS protection                                         │
│   - Geo-blocking                                            │
│   - Bot detection                                           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: API Gateway (Kong)                                 │
│   - Rate limiting                                           │
│   - Request validation                                      │
│   - API key validation                                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Authentication (Okta + JWT)                        │
│   - OAuth 2.0 / OIDC                                        │
│   - MFA enforcement                                         │
│   - Session management                                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Authorization (RBAC)                               │
│   - Role-based permissions                                  │
│   - Resource-level access                                   │
│   - Team/Org scoping                                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Data Protection                                    │
│   - Encryption at rest (AES-256)                            │
│   - Encryption in transit (TLS 1.3)                         │
│   - Field-level encryption (PII)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' ...` | XSS protection |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing protection |
| `X-Frame-Options` | `DENY` | Clickjacking protection |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referrer control |

---

## Audit Logging

### Events Logged

| Event Type | Details Captured |
|------------|------------------|
| Login | User, IP, device, success/failure, MFA method |
| Logout | User, session duration, logout type |
| Permission Change | User, role, changed by, old/new values |
| Data Access | User, resource type, resource ID, action |
| Config Change | User, setting, old/new value |
| Failed Auth | IP, username attempted, failure reason |

### Retention

- Security events: 2 years
- Access logs: 1 year
- Debug logs: 30 days

---

## Compliance Mapping

| Framework | Relevant Controls |
|-----------|-------------------|
| SOC 2 | CC6.1, CC6.2, CC6.3, CC6.6, CC6.7 |
| ISO 27001 | A.9.1, A.9.2, A.9.4, A.10.1 |
| NIST 800-53 | AC-2, AC-3, AC-6, IA-2, IA-5 |
| GDPR | Art. 32 (Security of processing) |

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Architecture | [System Architecture](../architecture/01-system-architecture.md) | Security within architecture |
| Data Flows | [Dashboard Request](../data-flows/01-dashboard-request.md) | Auth in request flow |
| Integrations | [Connector Catalog](../integrations/01-connector-catalog.md) | Credential management |

---

## Related Documentation

- [Security & Compliance](../../planning-artifacts/08-security-compliance.md) - Full security requirements
- [Operations Runbook](../../planning-artifacts/09-operations-runbook.md) - Security incident response
- [API Specification](../../planning-artifacts/05-api-specification.md) - API security details

---

Last Updated: 2026-01-04
Maintained By: Security Team
