# Connector Catalog

## Connector Categories

```mermaid
graph TB
    subgraph "Security Connectors"
        direction TB

        subgraph "EDR/XDR"
            E1[CrowdStrike Falcon]
            E2[Microsoft Defender]
            E3[SentinelOne]
            E4[Carbon Black]
            E5[Cortex XDR]
        end

        subgraph "SIEM/SOAR"
            S1[Splunk]
            S2[Microsoft Sentinel]
            S3[IBM QRadar]
            S4[Sumo Logic]
            S5[Elastic SIEM]
        end

        subgraph "Vulnerability"
            V1[Tenable.io]
            V2[Qualys]
            V3[Rapid7 InsightVM]
            V4[Nessus]
            V5[Snyk]
        end

        subgraph "Cloud Security"
            C1[AWS Security Hub]
            C2[Azure Security Center]
            C3[GCP Security Command]
            C4[Prisma Cloud]
            C5[Wiz]
        end

        subgraph "Identity"
            I1[Okta]
            I2[Azure AD]
            I3[OneLogin]
            I4[Ping Identity]
            I5[CyberArk]
        end

        subgraph "Compliance"
            CO1[ServiceNow GRC]
            CO2[OneTrust]
            CO3[Vanta]
            CO4[Drata]
            CO5[Tugboat Logic]
        end
    end

    classDef edr fill:#FEB2B2
    classDef siem fill:#FED7AA
    classDef vuln fill:#FEF08A
    classDef cloud fill:#BBF7D0
    classDef identity fill:#A5F3FC
    classDef compliance fill:#DDD6FE

    class E1,E2,E3,E4,E5 edr
    class S1,S2,S3,S4,S5 siem
    class V1,V2,V3,V4,V5 vuln
    class C1,C2,C3,C4,C5 cloud
    class I1,I2,I3,I4,I5 identity
    class CO1,CO2,CO3,CO4,CO5 compliance
```

<!-- SVG: 01-connector-catalog-1.svg -->
![Diagram 1](../../diagrams-svg/integrations/01-connector-catalog-1.svg)


## Connector Architecture

```mermaid
flowchart LR
    subgraph "External Systems"
        EXT1[CrowdStrike API]
        EXT2[Tenable API]
        EXT3[AWS API]
    end

    subgraph "Connector Service"
        CS[Connector Manager]

        subgraph "Adapters"
            A1[CrowdStrike Adapter]
            A2[Tenable Adapter]
            A3[AWS Adapter]
        end

        subgraph "Processing"
            NM[Normalizer]
            DD[Deduplicator]
            EN[Enricher]
        end
    end

    subgraph "Data Layer"
        Q[(Message Queue)]
        DB[(PostgreSQL)]
        CACHE[(Redis)]
    end

    EXT1 --> A1
    EXT2 --> A2
    EXT3 --> A3

    A1 --> NM
    A2 --> NM
    A3 --> NM

    NM --> DD --> EN --> Q
    Q --> DB
    EN --> CACHE
```

<!-- SVG: 01-connector-catalog-2.svg -->
![Diagram 2](../../diagrams-svg/integrations/01-connector-catalog-2.svg)


## Connector Data Flow

```mermaid
sequenceDiagram
    participant Sched as Scheduler
    participant CM as Connector Manager
    participant Adapter as API Adapter
    participant Ext as External API
    participant Norm as Normalizer
    participant Queue as SQS
    participant Worker as Data Worker
    participant DB as PostgreSQL

    Note over Sched,DB: Scheduled Sync (Every 5 min)
    Sched->>CM: Trigger sync
    CM->>Adapter: Fetch new data
    Adapter->>Ext: GET /alerts?since=lastSync
    Ext-->>Adapter: Raw findings[]
    Adapter->>Norm: Normalize data
    Norm->>Norm: Map to unified schema
    Norm->>Queue: Enqueue batch
    Queue-->>Worker: Dequeue batch
    Worker->>DB: Upsert findings
    Worker->>CM: Update sync status
```

<!-- SVG: 01-connector-catalog-3.svg -->
![Diagram 3](../../diagrams-svg/integrations/01-connector-catalog-3.svg)


## Unified Data Model

```mermaid
classDiagram
    class Finding {
        +UUID id
        +String externalId
        +String source
        +String severity
        +String title
        +String description
        +String[] assets
        +DateTime firstSeen
        +DateTime lastSeen
        +JSON rawData
    }

    class Asset {
        +UUID id
        +String hostname
        +String ipAddress
        +String[] tags
        +String type
        +String os
        +DateTime lastSeen
    }

    class Alert {
        +UUID id
        +String source
        +String severity
        +String status
        +Finding[] findings
        +Asset[] assets
        +DateTime createdAt
    }

    Finding --> Asset : affects
    Alert --> Finding : aggregates
    Alert --> Asset : relates
```

<!-- SVG: 01-connector-catalog-4.svg -->
![Diagram 4](../../diagrams-svg/integrations/01-connector-catalog-4.svg)


## Connector Status Dashboard

| Connector | Sync Frequency | Last Sync | Status | Findings |
|-----------|----------------|-----------|--------|----------|
| CrowdStrike | 5 min | 2 min ago | ✅ Active | 1,234 |
| Tenable.io | 15 min | 5 min ago | ✅ Active | 45,678 |
| AWS Security Hub | 10 min | 3 min ago | ✅ Active | 892 |
| Splunk | 5 min | 1 min ago | ✅ Active | 23,456 |
| Okta | 30 min | 10 min ago | ⚠️ Rate Limited | 156 |
| Azure AD | 60 min | 45 min ago | ✅ Active | 2,341 |

## Error Handling

```mermaid
flowchart TD
    A[API Call] --> B{Response}
    B -->|200 OK| C[Process Data]
    B -->|401 Unauthorized| D[Refresh Token]
    D -->|Success| A
    D -->|Failure| E[Alert Admin]
    B -->|429 Rate Limited| F[Exponential Backoff]
    F --> A
    B -->|500 Server Error| G[Retry 3x]
    G -->|Still Failing| H[Mark Unhealthy]
    B -->|Timeout| G

    C --> I[Update Sync Status]
    H --> I
```

<!-- SVG: 01-connector-catalog-5.svg -->
![Diagram 5](../../diagrams-svg/integrations/01-connector-catalog-5.svg)


## Connector Configuration

```typescript
interface ConnectorConfig {
  id: string;
  type: 'crowdstrike' | 'tenable' | 'aws' | 'splunk' | /* ... */;
  name: string;
  credentials: {
    type: 'api_key' | 'oauth2' | 'aws_role';
    // Encrypted storage
  };
  sync: {
    frequency: number; // minutes
    fullSyncFrequency: number; // hours
    batchSize: number;
    timeout: number;
  };
  filters: {
    severity?: string[];
    assetTags?: string[];
    dateRange?: { start: Date; end: Date };
  };
  mapping: {
    severityMap: Record<string, string>;
    statusMap: Record<string, string>;
    customFields: Record<string, string>;
  };
}
```
