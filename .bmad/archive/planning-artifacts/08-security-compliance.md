# Nexus UI Uplift - Security & Compliance

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Compliance Targets:** SOC 2 Type II, ISO 27001

---

## 1. Overview

This document defines the security architecture and compliance controls for the Nexus platform.

### Key References

- [OWASP Top 10 2021](https://owasp.org/Top10/) - Web Application Security Risks
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) (2025)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/) (2025)
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework) (2024)

---

## 2. Security Principles

1. **Defense in Depth** - Multiple layers of security controls
2. **Least Privilege** - Minimal access required for function
3. **Zero Trust** - Never trust, always verify
4. **Secure by Default** - Secure configuration out of the box
5. **Fail Secure** - Deny access on failure
6. **Audit Everything** - Comprehensive logging and monitoring

---

## 3. Authentication & Authorization

### 3.1 Authentication Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Okta/     │────▶│   Nexus     │
│             │     │   IdP       │     │   Auth      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │            JWT Token                  │
       ◀───────────────────────────────────────┘
       │
       │  Bearer Token
       ▼
┌─────────────┐     ┌─────────────┐
│   API       │────▶│   Services  │
│   Gateway   │     │             │
└─────────────┘     └─────────────┘
```

### 3.2 Token Management

| Token Type | Lifetime | Storage | Refresh |
|------------|----------|---------|---------|
| Access Token | 1 hour | Memory | Via refresh token |
| Refresh Token | 7 days | HttpOnly cookie | Re-authenticate |
| API Key | 1 year | Secrets Manager | Manual rotation |

### 3.3 JWT Claims

```json
{
  "sub": "user_abc123",
  "iss": "https://auth.nexus.armor.com",
  "aud": "nexus-api",
  "iat": 1704286800,
  "exp": 1704290400,
  "org_id": "org_xyz789",
  "role": "analyst",
  "permissions": ["alerts:read", "alerts:write", "assets:read"]
}
```

### 3.4 Role-Based Access Control

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Organization administrator | Full access |
| **Manager** | Team manager | Read/write, user management |
| **Analyst** | Security analyst | Read/write security data |
| **Viewer** | Read-only access | View only |
| **API** | Programmatic access | Configurable |

### 3.5 Permission Matrix

| Resource | Admin | Manager | Analyst | Viewer |
|----------|-------|---------|---------|--------|
| Users | CRUD | R, Update | R | - |
| Settings | CRUD | R | - | - |
| Alerts | CRUD | CRUD | CRUD | R |
| Assets | CRUD | CRUD | R | R |
| Vulns | CRUD | CRUD | CRUD | R |
| Compliance | CRUD | CRUD | R, Update | R |
| Reports | CRUD | CRUD | Create, R | R |

---

## 4. Data Security

### 4.1 Encryption Standards

| Data State | Algorithm | Key Management |
|------------|-----------|----------------|
| At Rest | AES-256 | AWS KMS CMK |
| In Transit | TLS 1.3 | ACM certificates |
| Database | AES-256 | RDS encryption |
| Backups | AES-256 | Separate CMK |

### 4.2 Data Classification

| Classification | Examples | Controls |
|----------------|----------|----------|
| **Confidential** | Customer data, credentials | Encrypted, access logged |
| **Internal** | Configuration, logs | Encrypted, role-based access |
| **Public** | Documentation | Standard protection |

### 4.3 Secrets Management

```yaml
# External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: nexus-secrets
  namespace: nexus-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: nexus-secrets
  data:
  - secretKey: database-url
    remoteRef:
      key: nexus/prod/database
      property: url
```

### 4.4 Data Retention

| Data Type | Retention | Disposal |
|-----------|-----------|----------|
| Audit Logs | 2 years | Secure delete |
| Security Alerts | 1 year | Archive then delete |
| User Sessions | 30 days | Automatic purge |
| API Logs | 90 days | Archive then delete |

---

## 5. Network Security

### 5.1 Network Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│           AWS WAF                    │
│  (Rate limiting, SQL injection)      │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│      Application Load Balancer       │
│         (Public Subnet)              │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│          EKS Ingress                 │
│      (Private Subnet)                │
│                                      │
│  ┌─────────────────────────────────┐│
│  │     Network Policies            ││
│  │   (Pod-to-pod restrictions)     ││
│  └─────────────────────────────────┘│
└──────────────────────────────────────┘
```

### 5.2 Security Groups

| Component | Inbound | Outbound |
|-----------|---------|----------|
| ALB | 443 (Internet) | EKS nodes (80/443) |
| EKS Nodes | ALB (80/443) | RDS, ElastiCache, S3 |
| RDS | EKS nodes (5432) | None |
| ElastiCache | EKS nodes (6379) | None |

### 5.3 Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
  namespace: nexus-prod
spec:
  podSelector:
    matchLabels:
      app: nexus-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nexus-gateway
    ports:
    - port: 3000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: nexus-prod
    ports:
    - port: 5432  # PostgreSQL
    - port: 6379  # Redis
```

---

## 6. Application Security

### 6.1 OWASP Top 10 Mitigations

| Risk | Mitigation |
|------|------------|
| **A01 Broken Access Control** | RBAC, tenant isolation, authorization checks |
| **A02 Cryptographic Failures** | TLS 1.3, AES-256, key rotation |
| **A03 Injection** | Parameterized queries, input validation |
| **A04 Insecure Design** | Threat modeling, security reviews |
| **A05 Security Misconfiguration** | Hardened defaults, config scanning |
| **A06 Vulnerable Components** | Dependency scanning, patching |
| **A07 Auth Failures** | MFA, secure sessions, lockout |
| **A08 Data Integrity Failures** | Signed artifacts, SBOM |
| **A09 Logging Failures** | Comprehensive audit logs |
| **A10 SSRF** | Allowlists, network isolation |

### 6.2 Input Validation

```typescript
// Zod schema for input validation
const alertSchema = z.object({
  title: z.string().min(1).max(500),
  severity: z.enum(["critical", "high", "medium", "low"]),
  description: z.string().max(10000).optional(),
  metadata: z.record(z.unknown()).optional(),
});

// Validate before processing
const result = alertSchema.safeParse(input);
if (!result.success) {
  throw new ValidationError(result.error.issues);
}
```

### 6.3 Output Encoding

```typescript
// React automatically escapes in JSX
<Typography>{userInput}</Typography>

// For HTML content, use sanitization
import DOMPurify from "dompurify";
const clean = DOMPurify.sanitize(htmlContent);
```

### 6.4 Security Headers

```typescript
// Response headers
{
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Content-Security-Policy": "default-src 'self'; script-src 'self'",
  "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

---

## 7. Infrastructure Security

### 7.1 AWS Security Controls

| Control | Implementation |
|---------|----------------|
| IAM | Least privilege policies, no root access |
| VPC | Private subnets, NAT gateways |
| Security Groups | Minimal ingress rules |
| KMS | Customer-managed keys |
| CloudTrail | All API calls logged |
| GuardDuty | Threat detection enabled |
| Config | Compliance rules |

### 7.2 Kubernetes Security

| Control | Implementation |
|---------|----------------|
| RBAC | Role-based access to K8s API |
| Pod Security | Restricted security context |
| Network Policies | Pod-level firewalls |
| Secrets | External Secrets Operator |
| Admission Control | OPA Gatekeeper policies |
| Runtime | Falco anomaly detection |

### 7.3 Container Security

```yaml
# Pod security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

---

## 8. Security Operations

### 8.1 Vulnerability Management

| Stage | Tool | Frequency |
|-------|------|-----------|
| Source Code | Snyk | Every PR |
| Dependencies | Snyk | Daily |
| Container Images | Trivy | Every build |
| Infrastructure | AWS Inspector | Weekly |
| Penetration Testing | External vendor | Quarterly |

### 8.2 Security Monitoring

| Data Source | Tool | Retention |
|-------------|------|-----------|
| Application Logs | Datadog | 30 days |
| Audit Logs | CloudWatch | 2 years |
| CloudTrail | S3 | 7 years |
| WAF Logs | S3 | 90 days |
| VPC Flow Logs | CloudWatch | 30 days |

### 8.3 Incident Response

```
1. Detection
   └── Alert from monitoring or user report

2. Triage (< 15 minutes)
   └── Assess severity, scope, impact

3. Containment (< 1 hour)
   └── Isolate affected systems

4. Eradication
   └── Remove threat, patch vulnerabilities

5. Recovery
   └── Restore services, verify integrity

6. Post-Incident
   └── Root cause analysis, lessons learned
```

### 8.4 Security Contacts

| Role | Responsibility | Contact |
|------|----------------|---------|
| Security Lead | Overall security | security@armor.com |
| On-Call Engineer | Incident response | PagerDuty |
| DPO | Data protection | privacy@armor.com |

---

## 9. Compliance

### 9.1 SOC 2 Type II Controls

| Trust Principle | Controls |
|-----------------|----------|
| **Security** | Access control, encryption, monitoring |
| **Availability** | High availability, DR, backups |
| **Processing Integrity** | Input validation, error handling |
| **Confidentiality** | Data classification, encryption |
| **Privacy** | Data minimization, consent |

### 9.2 ISO 27001 Domains

| Domain | Controls |
|--------|----------|
| A.5 | Information security policies |
| A.6 | Organization of information security |
| A.7 | Human resource security |
| A.8 | Asset management |
| A.9 | Access control |
| A.10 | Cryptography |
| A.11 | Physical and environmental security |
| A.12 | Operations security |
| A.13 | Communications security |
| A.14 | System acquisition and development |
| A.15 | Supplier relationships |
| A.16 | Incident management |
| A.17 | Business continuity |
| A.18 | Compliance |

### 9.3 Audit Evidence

| Control Area | Evidence Type | Location |
|--------------|---------------|----------|
| Access Control | IAM policies, RBAC config | Git, AWS |
| Encryption | KMS keys, TLS config | AWS, K8s |
| Logging | Log samples, retention policies | CloudWatch |
| Change Management | Git commits, PR reviews | GitHub |
| Incident Response | Runbooks, post-mortems | Confluence |

---

## 10. Security Checklist

### Pre-Development
- [ ] Threat model completed
- [ ] Security requirements defined
- [ ] Secure design review

### Development
- [ ] Secure coding guidelines followed
- [ ] Dependency vulnerabilities addressed
- [ ] Secrets not in code
- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] Authentication/authorization tested

### Pre-Release
- [ ] Security scanning passed
- [ ] Penetration test (if major release)
- [ ] Security review approved
- [ ] Compliance controls verified

### Post-Release
- [ ] Monitoring configured
- [ ] Incident response ready
- [ ] Security documentation updated

---

## 11. References

### External Standards
- [OWASP Top 10 2021](https://owasp.org/Top10/) (2021)
- [NIST CSF 2.0](https://www.nist.gov/cyberframework) (2024)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) (2025)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) (2025)

### Internal Documentation
- Platform Security Guidelines
- Incident Response Playbook
- Data Classification Policy

---

## 12. Related Diagrams

### Figure 1: Authentication Flow
*OAuth 2.0 / OIDC login, session management, and logout flows.*

> **Diagram:** [Authentication Flow](../diagrams/security/01-auth-flow.md)
>
> Covers:
> - Login flow (User → Okta → Token exchange → Session)
> - Token refresh (Background refresh before expiry)
> - Session validation (JWT → Permissions → Request)
> - Logout flow (Session deletion → Cookie clearing)
> - MFA options (TOTP, Push, SMS)

### Figure 2: RBAC Model
*Role-based access control and permission structure.*

> **Diagram:** [RBAC Model](../diagrams/security/02-rbac-model.md)
>
> Documents:
> - Role hierarchy (Super Admin → Viewer)
> - Permission types by resource
> - Access decision flow
> - Team/Organization scoping

### Figure 3: MCP Security Model
*Security architecture for AI assistant (MCP) access.*

> **Diagram:** [MCP Security Model](../diagrams/security/03-mcp-security-model.md)
>
> Comprehensive MCP security including:
> - Threat surface and defense layers
> - OAuth2 authentication flow
> - Permission model and authorization
> - Input validation and injection protection
> - Rate limiting architecture
> - Audit trail and anomaly detection
> - Secret management

---

*This document is maintained by the Security team. Annual review required.*
