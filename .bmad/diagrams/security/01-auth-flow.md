# Authentication Flow

## OAuth 2.0 / OIDC Login Flow

```mermaid
sequenceDiagram
    participant User as User Browser
    participant App as Nexus Frontend
    participant API as API Gateway
    participant Okta as Okta IdP
    participant DB as User Database

    Note over User,DB: Initial Login Flow
    User->>App: Navigate to /login
    App->>App: Check local session
    App-->>User: Redirect to Okta
    User->>Okta: /authorize request
    Okta-->>User: Login page
    User->>Okta: Enter credentials
    Okta->>Okta: Validate credentials
    Okta-->>User: Redirect with auth code
    User->>App: /callback?code=xxx
    App->>API: POST /auth/token (code)
    API->>Okta: Exchange code for tokens
    Okta-->>API: Access + Refresh tokens
    API->>DB: Fetch user permissions
    DB-->>API: User roles + permissions
    API->>API: Generate session JWT
    API-->>App: JWT + user profile
    App->>App: Store in httpOnly cookie
    App-->>User: Redirect to /dashboard
```

<!-- SVG: 01-auth-flow-1.svg -->
![Diagram 1](../../diagrams-svg/security/01-auth-flow-1.svg)


## Token Refresh Flow

```mermaid
sequenceDiagram
    participant App as Frontend
    participant API as API Gateway
    participant Okta as Okta IdP

    Note over App,Okta: Access Token About to Expire
    App->>API: Request with JWT
    API->>API: Validate JWT
    API->>API: Token expires in < 5 min
    API-->>App: 200 OK + X-Token-Refresh: true

    Note over App,Okta: Background Refresh
    App->>API: POST /auth/refresh
    API->>Okta: Refresh token grant
    Okta-->>API: New access token
    API->>API: Generate new session JWT
    API-->>App: New JWT in Set-Cookie
    App->>App: Cookie automatically updated
```

<!-- SVG: 01-auth-flow-2.svg -->
![Diagram 2](../../diagrams-svg/security/01-auth-flow-2.svg)


## Session Validation

```mermaid
flowchart TD
    A[Incoming Request] --> B{Has JWT Cookie?}
    B -->|No| C[401 Unauthorized]
    B -->|Yes| D{Validate JWT}
    D -->|Invalid Signature| C
    D -->|Expired| E{Has Refresh Token?}
    D -->|Valid| F{Check Permissions}
    E -->|No| C
    E -->|Yes| G[Refresh Token]
    G -->|Success| F
    G -->|Failure| C
    F -->|Insufficient| H[403 Forbidden]
    F -->|Sufficient| I[Process Request]

    style C fill:#FEB2B2
    style H fill:#FED7AA
    style I fill:#9AE6B4
```

<!-- SVG: 01-auth-flow-3.svg -->
![Diagram 3](../../diagrams-svg/security/01-auth-flow-3.svg)


## Logout Flow

```mermaid
sequenceDiagram
    participant User as User
    participant App as Frontend
    participant API as API Gateway
    participant Okta as Okta IdP
    participant Redis as Session Store

    User->>App: Click Logout
    App->>API: POST /auth/logout
    API->>Redis: Delete session
    API->>Okta: POST /logout (optional SSO logout)
    Okta-->>API: OK
    API-->>App: Clear cookies
    App->>App: Clear local state
    App-->>User: Redirect to /login
```

<!-- SVG: 01-auth-flow-4.svg -->
![Diagram 4](../../diagrams-svg/security/01-auth-flow-4.svg)


## Security Headers

```mermaid
graph LR
    subgraph "Response Headers"
        H1[Strict-Transport-Security]
        H2[Content-Security-Policy]
        H3[X-Content-Type-Options]
        H4[X-Frame-Options]
        H5[X-XSS-Protection]
        H6[Referrer-Policy]
    end

    subgraph "Cookie Attributes"
        C1[HttpOnly]
        C2[Secure]
        C3[SameSite=Strict]
        C4[Path=/]
        C5["Max-Age=3600"]
    end
```

<!-- SVG: 01-auth-flow-5.svg -->
![Diagram 5](../../diagrams-svg/security/01-auth-flow-5.svg)


## Multi-Factor Authentication

```mermaid
sequenceDiagram
    participant User as User
    participant Okta as Okta IdP
    participant MFA as MFA Provider

    User->>Okta: Primary authentication
    Okta->>Okta: Check MFA policy
    Okta-->>User: MFA required

    alt TOTP (Authenticator App)
        User->>User: Open authenticator app
        User->>Okta: Enter 6-digit code
        Okta->>Okta: Validate TOTP
    else Push Notification
        Okta->>MFA: Send push to device
        MFA-->>User: Push notification
        User->>MFA: Approve
        MFA-->>Okta: Approval confirmed
    else SMS/Email
        Okta->>MFA: Send OTP
        MFA-->>User: SMS/Email with code
        User->>Okta: Enter OTP
        Okta->>Okta: Validate OTP
    end

    Okta-->>User: Authentication complete
```

<!-- SVG: 01-auth-flow-6.svg -->
![Diagram 6](../../diagrams-svg/security/01-auth-flow-6.svg)


## Security Controls Summary

| Control | Implementation | Status |
|---------|----------------|--------|
| HTTPS Only | HSTS header, redirect | Required |
| JWT Signing | RS256 asymmetric | Required |
| Token Expiry | 1 hour access, 7 day refresh | Required |
| Session Storage | Redis with encryption | Required |
| CSRF Protection | SameSite cookies | Required |
| Rate Limiting | Kong Gateway | Required |
| MFA | Okta Verify / TOTP | Required |
| SSO | SAML 2.0 / OIDC | Supported |
