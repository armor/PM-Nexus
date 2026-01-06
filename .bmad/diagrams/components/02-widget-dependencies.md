# Widget Data Dependencies

## Widget to API Mapping

```mermaid
graph TB
    subgraph "Dashboard Widgets"
        W1[Security Score Card]
        W2[Vulnerability Trend]
        W3[Compliance Status]
        W4[Active Alerts]
        W5[Asset Distribution]
        W6[Risk Heatmap]
        W7[Top Findings]
        W8[Connector Health]
    end

    subgraph "TanStack Query Hooks"
        H1[useSecurityScore]
        H2[useVulnerabilityTrend]
        H3[useComplianceStatus]
        H4[useAlerts]
        H5[useAssets]
        H6[useRiskMetrics]
        H7[useFindings]
        H8[useConnectorHealth]
    end

    subgraph "API Endpoints"
        A1[/api/v1/metrics/security-score]
        A2[/api/v1/vulnerabilities/trend]
        A3[/api/v1/compliance/status]
        A4[/api/v1/alerts]
        A5[/api/v1/assets]
        A6[/api/v1/risk/heatmap]
        A7[/api/v1/findings]
        A8[/api/v1/connectors/health]
    end

    subgraph "Data Sources"
        D1[(Metrics Aggregation)]
        D2[(Vulnerability DB)]
        D3[(Compliance Engine)]
        D4[(Alert Store)]
        D5[(Asset Inventory)]
        D6[(Risk Calculator)]
        D7[(Finding Store)]
        D8[(Connector Registry)]
    end

    W1 --> H1 --> A1 --> D1
    W2 --> H2 --> A2 --> D2
    W3 --> H3 --> A3 --> D3
    W4 --> H4 --> A4 --> D4
    W5 --> H5 --> A5 --> D5
    W6 --> H6 --> A6 --> D6
    W7 --> H7 --> A7 --> D7
    W8 --> H8 --> A8 --> D8

    classDef widget fill:#86EFAC,stroke:#333
    classDef hook fill:#93C5FD,stroke:#333
    classDef api fill:#FCD34D,stroke:#333
    classDef data fill:#F9A8D4,stroke:#333

    class W1,W2,W3,W4,W5,W6,W7,W8 widget
    class H1,H2,H3,H4,H5,H6,H7,H8 hook
    class A1,A2,A3,A4,A5,A6,A7,A8 api
    class D1,D2,D3,D4,D5,D6,D7,D8 data
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant UI as Widget Component
    participant Hook as TanStack Query Hook
    participant Cache as Query Cache
    participant API as API Layer
    participant Redis as Redis Cache
    participant DB as PostgreSQL

    Note over UI,DB: Initial Load
    UI->>Hook: useVulnerabilityTrend({ days: 30 })
    Hook->>Cache: Check cache
    Cache-->>Hook: Cache miss
    Hook->>API: GET /api/v1/vulnerabilities/trend?days=30
    API->>Redis: Check Redis cache
    Redis-->>API: Cache miss
    API->>DB: Query vulnerability_metrics
    DB-->>API: Raw data
    API->>Redis: Cache result (5 min TTL)
    API-->>Hook: Trend data
    Hook->>Cache: Update cache
    Hook-->>UI: { data, isLoading: false }

    Note over UI,DB: Subsequent Load (within TTL)
    UI->>Hook: useVulnerabilityTrend({ days: 30 })
    Hook->>Cache: Check cache
    Cache-->>Hook: Cache hit
    Hook-->>UI: { data, isLoading: false }
```

<!-- SVG: 02-widget-dependencies-2.svg -->
![Diagram 2](../../diagrams-svg/components/02-widget-dependencies-2.svg)


## Widget Refresh Strategy

| Widget | Stale Time | Refetch Interval | Refetch on Focus |
|--------|------------|------------------|------------------|
| Security Score | 5 min | 5 min | Yes |
| Alert Count | 30 sec | 30 sec | Yes |
| Vulnerability Trend | 10 min | 10 min | No |
| Compliance Status | 15 min | 15 min | No |
| Connector Health | 1 min | 1 min | Yes |
| Risk Heatmap | 30 min | 30 min | No |

## Shared Query Keys

```mermaid
graph LR
    subgraph "Query Key Structure"
        K1["['alerts', filters]"]
        K2["['vulnerabilities', 'trend', { days }]"]
        K3["['compliance', 'status', orgId]"]
        K4["['connectors', 'health']"]
        K5["['metrics', 'security-score']"]
    end

    subgraph "Dependent Queries"
        D1[AlertBadge]
        D2[AlertTable]
        D3[AlertChart]
    end

    K1 --> D1
    K1 --> D2
    K1 --> D3

    Note1[Same query key = shared cache]

    style Note1 fill:#FEF3C7,stroke:#333
```

<!-- SVG: 02-widget-dependencies-3.svg -->
![Diagram 3](../../diagrams-svg/components/02-widget-dependencies-3.svg)


## Error Handling

```mermaid
flowchart TD
    A[API Request] --> B{Response}
    B -->|200 OK| C[Update Cache]
    B -->|401 Unauthorized| D[Redirect to Login]
    B -->|403 Forbidden| E[Show Access Denied]
    B -->|404 Not Found| F[Show Empty State]
    B -->|429 Rate Limited| G[Retry with Backoff]
    B -->|500 Server Error| H[Show Error + Retry]
    B -->|Network Error| I[Show Offline State]

    C --> J[Render Widget]
    F --> K[Render Empty Widget]
    H --> L[Render Error Widget]
    I --> M[Render Cached Data]
```

<!-- SVG: 02-widget-dependencies-4.svg -->
![Diagram 4](../../diagrams-svg/components/02-widget-dependencies-4.svg)


## Placeholder Data Pattern

```typescript
// REQUIRED: Always provide placeholderData for loading states
export function useSecurityScore() {
  return useQuery({
    queryKey: ['metrics', 'security-score'],
    queryFn: fetchSecurityScore,
    placeholderData: {
      score: 0,
      trend: 'neutral',
      breakdown: {
        vulnerabilities: 0,
        compliance: 0,
        alerts: 0
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000
  });
}
```
