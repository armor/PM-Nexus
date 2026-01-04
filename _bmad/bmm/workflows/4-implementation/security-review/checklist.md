# Security Review Checklist

## Pre-Review Requirements

- [ ] Code-review workflow has PASSED (security-review is second pass)
- [ ] Story file loaded with File List
- [ ] Security-relevant files identified

## OWASP Top 10 Coverage

### A01: Broken Access Control (CRITICAL)
- [ ] All endpoints have authentication checks
- [ ] Authorization verified for every resource access
- [ ] No IDOR vulnerabilities (ownership checks exist)
- [ ] Admin functions protected from regular users
- [ ] No privilege escalation via user-controlled fields

### A02: Cryptographic Failures (HIGH)
- [ ] No weak algorithms (MD5, SHA1, DES, ECB)
- [ ] Passwords use bcrypt/argon2 with proper cost
- [ ] No hardcoded encryption keys/IVs
- [ ] Sensitive data encrypted at rest
- [ ] TLS for data in transit

### A03: Injection (CRITICAL)
- [ ] All SQL queries use parameterization
- [ ] No command injection via user input
- [ ] NoSQL queries properly sanitized
- [ ] No LDAP injection
- [ ] No XPath injection

### A04: Insecure Design (HIGH)
- [ ] Rate limiting on sensitive endpoints
- [ ] Account lockout after failed attempts
- [ ] Proper session management
- [ ] Secure password reset flow

### A05: Security Misconfiguration (MEDIUM)
- [ ] No default credentials
- [ ] Error messages don't leak info
- [ ] Security headers configured
- [ ] Debug mode disabled in production

### A06: Vulnerable Components (HIGH)
- [ ] Dependencies up to date
- [ ] No known vulnerable packages
- [ ] Third-party code reviewed

### A07: Authentication Failures (CRITICAL)
- [ ] Strong password requirements
- [ ] No timing attacks on auth
- [ ] JWT properly verified (not just decoded)
- [ ] Session tokens unpredictable
- [ ] Proper logout/session invalidation

### A08: Data Integrity Failures (HIGH)
- [ ] Code/data from trusted sources only
- [ ] Integrity checks on downloads
- [ ] CI/CD pipeline secured

### A09: Security Logging Failures (MEDIUM)
- [ ] Security events logged
- [ ] Logs don't contain sensitive data
- [ ] Audit trail for admin actions

### A10: SSRF (HIGH)
- [ ] URL inputs validated/allowlisted
- [ ] No user-controlled redirects to internal resources

## Additional Checks

### Secrets Management
- [ ] No hardcoded API keys
- [ ] No hardcoded passwords
- [ ] No hardcoded tokens/secrets
- [ ] Environment variables used for secrets
- [ ] Secrets not in logs

### Input Validation
- [ ] All inputs validated
- [ ] Proper type checking
- [ ] Length limits enforced
- [ ] File uploads sanitized

### XSS Prevention
- [ ] Output encoding applied
- [ ] No innerHTML with user data
- [ ] Content-Security-Policy header

### CSRF Prevention
- [ ] CSRF tokens on state-changing requests
- [ ] SameSite cookie attribute set

## Review Outcome

| Severity | Count | Status |
|----------|-------|--------|
| Critical | _____ | [ ] Fixed |
| High     | _____ | [ ] Fixed |
| Medium   | _____ | [ ] Tracked |
| Low      | _____ | [ ] Noted |

## Final Decision

- [ ] **SECURE** - No vulnerabilities found
- [ ] **VULNERABLE** - Issues found and fixed
- [ ] **BLOCKED** - Critical/High issues remain unfixed

**Reviewer Notes:**
_____________________________________________
