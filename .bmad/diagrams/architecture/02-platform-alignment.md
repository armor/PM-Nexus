# Platform Alignment Diagram

## POC to Platform Migration

```mermaid
graph LR
    subgraph "Current POC Architecture"
        A1[Next.js Frontend]
        A2[Server Actions]
        A3[Prisma Direct]
        A4[Supabase Auth]
        A5[Supabase DB]

        A1 --> A2
        A2 --> A3
        A3 --> A5
        A1 --> A4
    end

    subgraph "Target Platform Architecture"
        B1[Next.js Frontend]
        B2[TanStack Query Hooks]
        B3[API Layer - Fastify]
        B4[Okta OAuth2]
        B5[PostgreSQL RDS]
        B6[Redis Cache]

        B1 --> B2
        B2 --> B3
        B3 --> B5
        B3 --> B6
        B1 --> B4
        B4 --> B3
    end

    A1 -.->|Migrate| B1
    A2 -.->|Replace| B2
    A3 -.->|API Layer| B3
    A4 -.->|Replace| B4
    A5 -.->|Migrate| B5

    style A1 fill:#FEB2B2
    style A2 fill:#FEB2B2
    style A3 fill:#FEB2B2
    style A4 fill:#FEB2B2
    style A5 fill:#FEB2B2

    style B1 fill:#9AE6B4
    style B2 fill:#9AE6B4
    style B3 fill:#9AE6B4
    style B4 fill:#9AE6B4
    style B5 fill:#9AE6B4
    style B6 fill:#9AE6B4
```

<!-- SVG: 02-platform-alignment-1.svg -->
![Diagram 1](../../diagrams-svg/architecture/02-platform-alignment-1.svg)


## Data Fetching Migration

```mermaid
sequenceDiagram
    participant UI as React Component
    participant SA as Server Action (POC)
    participant Hook as TanStack Query Hook
    participant API as API Layer
    participant DB as Database

    Note over UI,DB: POC Pattern (Direct)
    UI->>SA: Call server action
    SA->>DB: Prisma query
    DB-->>SA: Data
    SA-->>UI: Return data

    Note over UI,DB: Platform Pattern (API)
    UI->>Hook: useAlerts()
    Hook->>API: GET /api/v1/alerts
    API->>DB: Query via service
    DB-->>API: Data
    API-->>Hook: JSON response
    Hook-->>UI: Typed data + state
```

<!-- SVG: 02-platform-alignment-2.svg -->
![Diagram 2](../../diagrams-svg/architecture/02-platform-alignment-2.svg)


## Component Library Alignment

```mermaid
graph TB
    subgraph "POC Components"
        P1[shadcn/ui]
        P2[Tailwind CSS]
        P3[Recharts]
        P4[Custom Components]
    end

    subgraph "Platform Components"
        L1["@platform/react-ui"]
        L2[MUI v7 + Tailwind]
        L3[Recharts + D3]
        L4[Design Tokens]
    end

    subgraph "Shared Patterns"
        S1[Component Props Interface]
        S2[sx Props Pattern]
        S3[Storybook Stories]
        S4[MSW Handlers]
        S5[Vitest Tests]
    end

    P1 --> L1
    P2 --> L2
    P3 --> L3
    P4 --> L1

    L1 --> S1
    L1 --> S2
    L1 --> S3
    L1 --> S4
    L1 --> S5
```

<!-- SVG: 02-platform-alignment-3.svg -->
![Diagram 3](../../diagrams-svg/architecture/02-platform-alignment-3.svg)


## Migration Checklist

| Layer | POC | Platform | Status |
|-------|-----|----------|--------|
| Auth | Supabase | Okta OAuth2 | Required |
| Database | Supabase DB | RDS PostgreSQL | Required |
| API | Server Actions | Fastify REST | Required |
| Data Fetching | Direct Prisma | TanStack Query | Required |
| State | Context/Local | TanStack Query | Required |
| Components | shadcn/ui | @platform/react-ui | Aligned |
| Styling | Tailwind | MUI + Tailwind | Aligned |
| Testing | Basic | Deep E2E | Required |
| MCP | None | Nexus + Jira | New |
