# Role-Based Access Control (RBAC) Model

## Permission Hierarchy

```mermaid
graph TB
    subgraph "Roles"
        R1[Super Admin]
        R2[Organization Admin]
        R3[Security Manager]
        R4[Security Analyst]
        R5[Viewer]
        R6[Connector Admin]
    end

    subgraph "Permission Groups"
        P1[Full Access]
        P2[Admin Access]
        P3[Manager Access]
        P4[Analyst Access]
        P5[Read Only]
        P6[Connector Mgmt]
    end

    subgraph "Resources"
        RS1[Dashboards]
        RS2[Alerts]
        RS3[Connectors]
        RS4[Reports]
        RS5[Settings]
        RS6[Users]
        RS7[Audit Logs]
    end

    R1 --> P1
    R2 --> P2
    R3 --> P3
    R4 --> P4
    R5 --> P5
    R6 --> P6

    P1 --> RS1 & RS2 & RS3 & RS4 & RS5 & RS6 & RS7
    P2 --> RS1 & RS2 & RS3 & RS4 & RS5 & RS6
    P3 --> RS1 & RS2 & RS4 & RS5
    P4 --> RS1 & RS2 & RS4
    P5 --> RS1 & RS4
    P6 --> RS3

    classDef admin fill:#FEB2B2,stroke:#333
    classDef manager fill:#FED7AA,stroke:#333
    classDef analyst fill:#FEF08A,stroke:#333
    classDef viewer fill:#BBF7D0,stroke:#333

    class R1,R2 admin
    class R3,R6 manager
    class R4 analyst
    class R5 viewer
```

<!-- SVG: 02-rbac-model-1.svg -->
![Diagram 1](../../diagrams-svg/security/02-rbac-model-1.svg)


## Permission Matrix

```mermaid
graph LR
    subgraph "CRUD Operations"
        C[Create]
        R[Read]
        U[Update]
        D[Delete]
    end

    subgraph "Super Admin"
        SA_C[All Create]
        SA_R[All Read]
        SA_U[All Update]
        SA_D[All Delete]
    end

    subgraph "Security Analyst"
        A_C[Create Alerts, Tickets]
        A_R[Read Dashboards, Alerts]
        A_U[Update Alert Status]
        A_D[None]
    end

    subgraph "Viewer"
        V_C[None]
        V_R[Read Dashboards, Reports]
        V_U[None]
        V_D[None]
    end
```

<!-- SVG: 02-rbac-model-2.svg -->
![Diagram 2](../../diagrams-svg/security/02-rbac-model-2.svg)


## Role Definitions

| Role | Description | Scope |
|------|-------------|-------|
| Super Admin | Platform-wide administration | All organizations |
| Organization Admin | Full org control | Single organization |
| Security Manager | Manages analysts, workflows | Assigned teams |
| Security Analyst | Day-to-day operations | Assigned dashboards |
| Viewer | Read-only dashboards | Assigned dashboards |
| Connector Admin | Manage integrations | Connector resources |

## Organization Hierarchy

```mermaid
graph TB
    subgraph "Multi-Tenant Structure"
        T[Platform Tenant]
        T --> O1[Organization A]
        T --> O2[Organization B]
        T --> O3[Organization C]

        O1 --> Team1A[Security Team]
        O1 --> Team1B[Compliance Team]

        O2 --> Team2A[SOC Team]
        O2 --> Team2B[IT Ops]

        Team1A --> U1[User 1]
        Team1A --> U2[User 2]
        Team1B --> U3[User 3]
    end
```

<!-- SVG: 02-rbac-model-3.svg -->
![Diagram 3](../../diagrams-svg/security/02-rbac-model-3.svg)


## Permission Resolution

```mermaid
flowchart TD
    A[User Request] --> B{Get User Roles}
    B --> C{Get Role Permissions}
    C --> D{Check Resource Permission}
    D -->|Allowed| E{Check Data Scope}
    D -->|Denied| F[403 Forbidden]

    E -->|Organization| G{User Org = Resource Org?}
    E -->|Team| H{User in Team?}
    E -->|Personal| I{User = Owner?}

    G -->|Yes| J[Allow Access]
    G -->|No| F
    H -->|Yes| J
    H -->|No| F
    I -->|Yes| J
    I -->|No| F
```

<!-- SVG: 02-rbac-model-4.svg -->
![Diagram 4](../../diagrams-svg/security/02-rbac-model-4.svg)


## API Authorization

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant GW as API Gateway
    participant Auth as Auth Service
    participant API as Resource API
    participant DB as Database

    Client->>GW: GET /api/v1/alerts
    GW->>Auth: Validate JWT + Extract claims
    Auth-->>GW: { userId, roles, orgId }
    GW->>API: Request + Auth Context
    API->>API: Check permission: alerts.read
    API->>DB: Query with org scope filter
    DB-->>API: Filtered results
    API-->>Client: 200 OK + alerts[]
```

<!-- SVG: 02-rbac-model-5.svg -->
![Diagram 5](../../diagrams-svg/security/02-rbac-model-5.svg)


## Permission Definitions

```typescript
// Permission structure
interface Permission {
  resource: 'alerts' | 'dashboards' | 'connectors' | 'users' | 'settings';
  action: 'create' | 'read' | 'update' | 'delete' | 'manage';
  scope?: 'own' | 'team' | 'organization' | 'platform';
}

// Role mappings
const ROLES = {
  'super-admin': ['*:*:platform'],
  'org-admin': ['*:*:organization'],
  'security-manager': [
    'alerts:*:team',
    'dashboards:*:team',
    'reports:*:team',
    'users:read:team'
  ],
  'security-analyst': [
    'alerts:read:team',
    'alerts:update:own',
    'dashboards:read:team',
    'reports:read:team'
  ],
  'viewer': [
    'dashboards:read:own',
    'reports:read:own'
  ]
};
```

## Audit Trail

| Event | Logged Data | Retention |
|-------|-------------|-----------|
| Login | userId, IP, timestamp, success | 1 year |
| Permission denied | userId, resource, action, reason | 1 year |
| Role change | userId, oldRole, newRole, changedBy | 3 years |
| Data export | userId, dataType, recordCount | 3 years |
| Setting change | userId, setting, oldValue, newValue | 3 years |
