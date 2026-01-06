# Nexus UI Uplift - Integration Playbook

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Connectors:** 45+ integrations

---

## 1. Overview

This playbook defines the integration architecture, connector catalog, and implementation patterns for the Nexus platform.

### Key References

- [AWS Security Hub Integration](https://docs.aws.amazon.com/securityhub/) (2025)
- [Microsoft Graph Security API](https://learn.microsoft.com/en-us/graph/security-concept-overview) (2025)
- [Crowdstrike Falcon API](https://falcon.crowdstrike.com/documentation/) (2025)

---

## 2. Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  External Systems                            │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐           │
│  │ AWS │ │Azure│ │ GCP │ │Crowd│ │ Okta│ │Jira │  ...      │
│  │     │ │     │ │     │ │Strike│ │     │ │     │           │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘           │
└─────┼───────┼───────┼───────┼───────┼───────┼───────────────┘
      │       │       │       │       │       │
      └───────┴───────┴───┬───┴───────┴───────┘
                          │
      ┌───────────────────▼───────────────────┐
      │         Connector Service              │
      │  ┌─────────────────────────────────┐  │
      │  │     Connector Manager           │  │
      │  │  - Scheduling                   │  │
      │  │  - Rate Limiting                │  │
      │  │  - Retry Logic                  │  │
      │  │  - Error Handling               │  │
      │  └─────────────────────────────────┘  │
      │  ┌─────────────────────────────────┐  │
      │  │     Data Transformer            │  │
      │  │  - Normalization                │  │
      │  │  - Deduplication                │  │
      │  │  - Enrichment                   │  │
      │  └─────────────────────────────────┘  │
      └───────────────────┬───────────────────┘
                          │
      ┌───────────────────▼───────────────────┐
      │            Message Queue               │
      │              (SQS)                     │
      └───────────────────┬───────────────────┘
                          │
      ┌───────────────────▼───────────────────┐
      │         Data Ingestion Service         │
      │  - Validation                          │
      │  - Storage                             │
      │  - Alerting                            │
      └───────────────────────────────────────┘
```

---

## 3. Connector Categories

### 3.1 Cloud Security

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| AWS Security Hub | Cloud | Findings, resources | 15 min |
| AWS GuardDuty | Cloud | Threats | 5 min |
| AWS Inspector | Cloud | Vulnerabilities | 1 hour |
| AWS Config | Cloud | Compliance | 15 min |
| Azure Defender | Cloud | Alerts, vulns | 15 min |
| Azure Sentinel | Cloud | Incidents | 5 min |
| GCP Security Command | Cloud | Findings | 15 min |

### 3.2 Endpoint Security

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| CrowdStrike Falcon | EDR | Detections, devices | 5 min |
| Microsoft Defender | EDR | Alerts, devices | 5 min |
| SentinelOne | EDR | Threats, agents | 5 min |
| Carbon Black | EDR | Alerts, devices | 5 min |

### 3.3 Vulnerability Management

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| Qualys | Vulnerability | Vulns, assets | 1 hour |
| Tenable | Vulnerability | Vulns, assets | 1 hour |
| Rapid7 InsightVM | Vulnerability | Vulns, assets | 1 hour |
| Nessus | Vulnerability | Scan results | On-demand |

### 3.4 Identity & Access

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| Okta | Identity | Users, events | 5 min |
| Azure AD | Identity | Users, sign-ins | 5 min |
| Google Workspace | Identity | Users, events | 15 min |
| CyberArk | PAM | Sessions, accounts | 15 min |

### 3.5 SIEM & Log Management

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| Splunk | SIEM | Alerts | 5 min |
| Sumo Logic | SIEM | Alerts | 5 min |
| Elastic SIEM | SIEM | Alerts | 5 min |
| LogRhythm | SIEM | Alarms | 5 min |

### 3.6 Ticketing & Workflow

| Connector | Category | Data Types | Sync Frequency |
|-----------|----------|------------|----------------|
| Jira | Ticketing | Issues | 15 min |
| ServiceNow | ITSM | Incidents | 15 min |
| PagerDuty | Incident | Incidents | 5 min |

---

## 4. Connector Implementation

### 4.1 Connector Structure

```typescript
// src/connectors/aws-security-hub/index.ts

import { BaseConnector, ConnectorConfig, SyncResult } from "../base";

export class AWSSecurityHubConnector extends BaseConnector {
  readonly type = "aws-security-hub";
  readonly category = "cloud";
  readonly supportedDataTypes = ["findings", "resources"];

  constructor(config: ConnectorConfig) {
    super(config);
    this.validateConfig();
  }

  async testConnection(): Promise<boolean> {
    try {
      const client = this.getClient();
      await client.send(new GetFindingsCommand({ MaxResults: 1 }));
      return true;
    } catch (error) {
      this.logger.error("Connection test failed", error);
      return false;
    }
  }

  async sync(): Promise<SyncResult> {
    const startTime = Date.now();
    let itemsProcessed = 0;

    try {
      // Fetch findings since last sync
      const findings = await this.fetchFindings();

      // Transform to normalized format
      const normalizedAlerts = findings.map((f) =>
        this.transformFinding(f)
      );

      // Send to ingestion queue
      await this.publishToQueue(normalizedAlerts);

      itemsProcessed = normalizedAlerts.length;

      return {
        success: true,
        itemsProcessed,
        duration: Date.now() - startTime,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        duration: Date.now() - startTime,
      };
    }
  }

  private transformFinding(finding: Finding): NormalizedAlert {
    return {
      externalId: finding.Id,
      title: finding.Title,
      description: finding.Description,
      severity: this.mapSeverity(finding.Severity.Label),
      source: "aws-security-hub",
      sourceId: finding.Id,
      metadata: {
        awsAccountId: finding.AwsAccountId,
        region: finding.Region,
        resourceType: finding.Resources[0]?.Type,
        compliance: finding.Compliance,
      },
      createdAt: new Date(finding.CreatedAt),
    };
  }

  private mapSeverity(label: string): Severity {
    const mapping: Record<string, Severity> = {
      CRITICAL: "critical",
      HIGH: "high",
      MEDIUM: "medium",
      LOW: "low",
      INFORMATIONAL: "low",
    };
    return mapping[label] || "medium";
  }
}
```

### 4.2 Base Connector Class

```typescript
// src/connectors/base.ts

export abstract class BaseConnector {
  protected config: ConnectorConfig;
  protected logger: Logger;
  protected rateLimiter: RateLimiter;

  abstract readonly type: string;
  abstract readonly category: string;

  constructor(config: ConnectorConfig) {
    this.config = config;
    this.logger = new Logger(`connector:${this.type}`);
    this.rateLimiter = new RateLimiter(config.rateLimit);
  }

  abstract testConnection(): Promise<boolean>;
  abstract sync(): Promise<SyncResult>;

  protected async publishToQueue(items: NormalizedItem[]): Promise<void> {
    const batches = chunk(items, 10);
    for (const batch of batches) {
      await this.rateLimiter.acquire();
      await sqsClient.send(
        new SendMessageBatchCommand({
          QueueUrl: process.env.INGESTION_QUEUE_URL,
          Entries: batch.map((item, i) => ({
            Id: `${i}`,
            MessageBody: JSON.stringify(item),
          })),
        })
      );
    }
  }

  protected validateConfig(): void {
    const schema = this.getConfigSchema();
    const result = schema.safeParse(this.config);
    if (!result.success) {
      throw new ConfigurationError(result.error.message);
    }
  }

  protected abstract getConfigSchema(): z.ZodSchema;
}
```

### 4.3 Rate Limiting

```typescript
// src/connectors/rate-limiter.ts

export class RateLimiter {
  private tokens: number;
  private lastRefill: number;
  private readonly maxTokens: number;
  private readonly refillRate: number; // tokens per second

  constructor(config: RateLimitConfig) {
    this.maxTokens = config.maxRequests;
    this.refillRate = config.maxRequests / config.windowSeconds;
    this.tokens = this.maxTokens;
    this.lastRefill = Date.now();
  }

  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens < 1) {
      const waitTime = (1 - this.tokens) / this.refillRate * 1000;
      await sleep(waitTime);
      this.refill();
    }

    this.tokens -= 1;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(
      this.maxTokens,
      this.tokens + elapsed * this.refillRate
    );
    this.lastRefill = now;
  }
}
```

---

## 5. Data Normalization

### 5.1 Normalized Alert Schema

```typescript
interface NormalizedAlert {
  externalId: string;           // Unique ID from source
  title: string;                // Alert title
  description?: string;         // Detailed description
  severity: "critical" | "high" | "medium" | "low";
  source: string;               // Connector type
  sourceId: string;             // ID in source system
  asset?: {
    externalId: string;
    name: string;
    type: string;
  };
  metadata: Record<string, unknown>; // Source-specific data
  createdAt: Date;
  updatedAt?: Date;
}
```

### 5.2 Normalized Asset Schema

```typescript
interface NormalizedAsset {
  externalId: string;
  type: "server" | "endpoint" | "user" | "application" | "cloud_resource";
  name: string;
  hostname?: string;
  ipAddresses?: string[];
  operatingSystem?: string;
  source: string;
  sourceId: string;
  metadata: Record<string, unknown>;
  lastSeenAt: Date;
}
```

### 5.3 Normalized Vulnerability Schema

```typescript
interface NormalizedVulnerability {
  externalId: string;
  cveId?: string;
  title: string;
  description?: string;
  severity: "critical" | "high" | "medium" | "low";
  cvssScore?: number;
  cvssVector?: string;
  asset: {
    externalId: string;
    name: string;
  };
  affectedSoftware?: string;
  affectedVersion?: string;
  fixedVersion?: string;
  remediation?: string;
  source: string;
  sourceId: string;
  discoveredAt: Date;
}
```

---

## 6. Error Handling

### 6.1 Retry Strategy

```typescript
const retryConfig = {
  maxRetries: 3,
  initialDelay: 1000,    // 1 second
  maxDelay: 30000,       // 30 seconds
  backoffMultiplier: 2,
  retryableErrors: [
    "ECONNRESET",
    "ETIMEDOUT",
    "RATE_LIMIT_EXCEEDED",
    "SERVICE_UNAVAILABLE",
  ],
};

async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  let lastError: Error;
  let delay = config.initialDelay;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (!isRetryable(error, config.retryableErrors)) {
        throw error;
      }

      if (attempt < config.maxRetries) {
        await sleep(delay);
        delay = Math.min(delay * config.backoffMultiplier, config.maxDelay);
      }
    }
  }

  throw lastError;
}
```

### 6.2 Error Classification

| Error Type | Action | Alert |
|------------|--------|-------|
| Authentication | Disable connector | Yes |
| Rate Limit | Backoff | No |
| Network | Retry | After 3 failures |
| Data Format | Log and skip | No |
| API Error (4xx) | Log and continue | After 10 failures |
| API Error (5xx) | Retry | After 3 failures |

---

## 7. Configuration Management

### 7.1 Connector Configuration

```typescript
interface ConnectorConfig {
  id: string;
  organizationId: string;
  type: string;
  name: string;
  enabled: boolean;
  credentials: EncryptedCredentials;
  settings: {
    syncFrequencyMinutes: number;
    dataTypes: string[];
    filters?: Record<string, unknown>;
  };
  rateLimit: {
    maxRequests: number;
    windowSeconds: number;
  };
}
```

### 7.2 Credential Encryption

```typescript
// Credentials encrypted with AWS KMS
async function encryptCredentials(
  credentials: Record<string, string>
): Promise<EncryptedCredentials> {
  const response = await kmsClient.send(
    new EncryptCommand({
      KeyId: process.env.KMS_KEY_ID,
      Plaintext: Buffer.from(JSON.stringify(credentials)),
    })
  );

  return {
    encryptedData: response.CiphertextBlob.toString("base64"),
    keyId: process.env.KMS_KEY_ID,
  };
}

async function decryptCredentials(
  encrypted: EncryptedCredentials
): Promise<Record<string, string>> {
  const response = await kmsClient.send(
    new DecryptCommand({
      CiphertextBlob: Buffer.from(encrypted.encryptedData, "base64"),
    })
  );

  return JSON.parse(response.Plaintext.toString());
}
```

---

## 8. Monitoring & Observability

### 8.1 Connector Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `connector.sync.duration` | Sync duration | > 5 min |
| `connector.sync.items` | Items processed | N/A |
| `connector.sync.errors` | Sync errors | > 0 |
| `connector.api.requests` | API calls made | Rate limit warning |
| `connector.api.latency` | API latency | > 5 sec |
| `connector.queue.size` | Queue depth | > 10000 |

### 8.2 Health Check Endpoint

```typescript
// GET /api/v1/integrations/connectors/:id/health

interface ConnectorHealth {
  id: string;
  status: "healthy" | "degraded" | "unhealthy";
  lastSync: {
    timestamp: string;
    success: boolean;
    itemsProcessed: number;
    duration: number;
  };
  nextSync: string;
  errors: {
    count: number;
    lastError?: string;
  };
  metrics: {
    itemsLast24h: number;
    averageSyncDuration: number;
    successRate: number;
  };
}
```

---

## 9. Adding New Connectors

### 9.1 Implementation Checklist

- [ ] Create connector class extending `BaseConnector`
- [ ] Implement `testConnection()` method
- [ ] Implement `sync()` method
- [ ] Define config schema (Zod)
- [ ] Add data transformers
- [ ] Add rate limiting config
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add to connector registry
- [ ] Document configuration
- [ ] Add to admin UI

### 9.2 Connector Template

```typescript
// src/connectors/new-connector/index.ts

import { z } from "zod";
import { BaseConnector, ConnectorConfig, SyncResult } from "../base";

const configSchema = z.object({
  apiKey: z.string().min(1),
  baseUrl: z.string().url(),
  // Add connector-specific fields
});

export class NewConnector extends BaseConnector {
  readonly type = "new-connector";
  readonly category = "security";
  readonly supportedDataTypes = ["alerts"];

  protected getConfigSchema() {
    return configSchema;
  }

  async testConnection(): Promise<boolean> {
    // Implement connection test
  }

  async sync(): Promise<SyncResult> {
    // Implement sync logic
  }
}
```

---

## 10. Troubleshooting

### 10.1 Common Issues

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Auth failure | 401 errors | Verify credentials, check expiry |
| Rate limiting | 429 errors | Reduce sync frequency |
| Timeout | ETIMEDOUT | Check network, increase timeout |
| Data mismatch | Missing data | Check API version, field mapping |
| Queue backup | High latency | Scale ingestion workers |

### 10.2 Debug Mode

```bash
# Enable debug logging for specific connector
DEBUG=connector:aws-security-hub npm run sync

# View connector logs
kubectl logs -n nexus-prod -l app=nexus-connector-service --tail=100

# Check queue depth
aws sqs get-queue-attributes \
  --queue-url $INGESTION_QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages
```

---

## 11. References

### API Documentation
- [AWS Security Hub API](https://docs.aws.amazon.com/securityhub/1.0/APIReference/) (2025)
- [CrowdStrike Falcon API](https://falcon.crowdstrike.com/documentation/) (2025)
- [Microsoft Graph Security](https://learn.microsoft.com/en-us/graph/api/resources/security-api-overview) (2025)
- [Okta API](https://developer.okta.com/docs/reference/) (2025)

### Internal Documentation
- Architecture Document
- API Specification
- Operations Runbook

---

## 12. Related Diagrams

### Figure 1: Connector Catalog
*All 46 connectors organized by category with data flow patterns.*

> **Diagram:** [Connector Catalog](../diagrams/integrations/01-connector-catalog.md)
>
> Shows:
> - Connector categories (EDR, SIEM, Vulnerability, Cloud, Identity, Compliance)
> - Adapter architecture
> - Unified data model (Finding, Asset, Alert)
> - Error handling patterns

### Figure 2: Connector Sync Flow
*Detailed data synchronization sequence.*

> **Diagram:** [Connector Sync Flow](../diagrams/data-flows/02-connector-sync.md)
>
> Covers:
> - Scheduled sync triggers
> - Credential retrieval
> - Rate limit handling
> - Data normalization
> - Deduplication and enrichment

### Figure 3: Multi-Connector Aggregation
*Cross-source deduplication and correlation.*

> **Diagram:** [Multi-Connector Aggregation](../diagrams/data-flows/03-multi-connector.md)
>
> Documents:
> - Deduplication algorithms (exact, fuzzy, heuristic, graph-based)
> - Correlation engine
> - Cache hierarchy
> - Risk scoring

---

*This playbook is maintained by the Integrations team. New connector requests go through Product.*
