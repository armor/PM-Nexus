# Data Flow Diagrams - Nexus UI Platform

This directory contains comprehensive data flow diagrams illustrating how data moves through the Nexus UI security platform, from user requests through various processing pipelines to real-time updates delivered to multiple clients.

## Diagram Index

### 1. [Dashboard Request Cycle](./01-dashboard-request.md)
**Purpose:** Understand how dashboard data is fetched, cached, and rendered

**Scope:** User request → TanStack Query → Fastify API → Authentication → Database → Cache → UI Rendering

**Key Concepts:**
- TanStack Query caching and synchronization
- Fastify middleware pipeline
- Okta JWT authentication
- Redis cache strategy
- PostgreSQL query optimization
- React Virtual DOM rendering

**Performance Targets:**
- API Response: 50-200ms (cache hit), <500ms (cache miss)
- First Contentful Paint: <1.5s
- Largest Contentful Paint: <2.5s

**Use Cases:**
- Troubleshooting slow dashboard loads
- Understanding cache hit rates
- Optimizing database queries
- Debugging authentication issues

---

### 2. [Connector Sync Flow](./02-connector-sync.md)
**Purpose:** Understand how data from 45+ external connectors is collected, normalized, and stored

**Scope:** Scheduled sync jobs → Credential retrieval → Parallel API calls → Data normalization → Deduplication → Database storage → Event notification

**Connector Types (45+):**
- EDR: CrowdStrike, Microsoft Defender, Cybereason, Carbon Black, Palo Alto Cortex XDR, SentinelOne
- SIEM: Splunk, IBM QRadar, ArcSight, Elastic Security, Exabeam
- Cloud: AWS, Azure, Google Cloud, Wiz, Lacework
- Vulnerability: Qualys, Tenable, Rapid7, Acunetix, OpenVAS
- Identity: Okta, Azure AD, Ping Identity, AWS IAM
- Compliance: ServiceNow, Jira, Vault, CyberArk
- Plus 7+ additional categories

**Key Concepts:**
- SQS job queuing
- AWS Secrets Manager credential rotation
- Rate limit handling and exponential backoff
- Data normalization and schema mapping
- Hash-based deduplication
- Batch inserts and upserts
- ClickHouse archival

**Performance Targets:**
- Total sync cycle: <5 minutes (all 45+ connectors)
- Per-connector sync: <1 minute
- Success rate: >95%
- Normalization: <10ms per record
- Database writes: <100ms per 1000 records

**Use Cases:**
- Troubleshooting failed connector syncs
- Understanding data ingestion pipeline
- Optimizing sync frequency
- Debugging data quality issues

---

### 3. [Multi-Connector Data Aggregation](./03-multi-connector.md)
**Purpose:** Understand how data from multiple disparate sources is deduplicated, correlated, and unified into a single view

**Scope:** Multi-source queries → Deduplication → Correlation → Enrichment → Unified response generation

**Key Algorithms:**
- **Exact Matching:** Direct key match, IP address, serial number
- **Fuzzy Matching:** Levenshtein distance, normalized hostname
- **Heuristic Matching:** Multi-factor scoring (OS, IP, MAC, creation time)
- **Graph-Based Matching:** Entity resolution with transitive closure
- **Temporal Correlation:** Time-window based event matching
- **Spatial Correlation:** Network proximity and geographic patterns
- **Causal Correlation:** Cause-effect chain detection

**Key Concepts:**
- Cache hierarchy (browser → Redis → database)
- Deduplication graph algorithms
- Correlation engine for detecting relationships
- Risk scoring and anomaly detection
- Enrichment pipelines with ML models
- Unified data schema
- Response caching

**Performance Targets:**
- Deduplication (1000 records): <100ms
- Correlation computation: <2000ms
- Total aggregation: <5000ms (cache miss)
- Cache lookup: <10ms

**Use Cases:**
- Finding the same device across multiple systems
- Detecting correlated security incidents
- Computing risk scores across data sources
- Debugging duplicate asset records

---

### 4. [AI Assistant Question Answering](./04-ai-assistant.md)
**Purpose:** Understand how natural language questions are processed and answered using RAG and LLM

**Scope:** Question input → Intent classification → Context retrieval → MCP tool invocation → LLM processing → Response generation with citations

**Key Features:**
- Intent classification with multi-label scoring
- Retrieval Augmented Generation (RAG) with vector search
- OpenAI-compatible MCP (Model Context Protocol) for tool execution
- Claude LLM for reasoning and response generation
- Citation and source attribution
- Conversation context management

**Available Tools (8):**
- `get_vulnerabilities` - Query vulnerabilities
- `get_assets` - Query assets with filters
- `analyze_risk` - Compute risk scores
- `get_compliance_status` - Compliance framework status
- `search_assets` - Full-text search
- `get_threat_context` - Threat intelligence
- `correlate_incidents` - Related incidents
- `search_documentation` - Knowledge base search

**Key Concepts:**
- Intent classification (VULNERABILITY_QUERY, ASSET_QUERY, RISK_ASSESSMENT, etc)
- Embedding-based semantic search
- Hybrid search (vector + keyword BM25)
- Token budget management
- Multi-turn conversation context
- Tool use with parameters
- Response formatting with Markdown

**Performance Targets:**
- Intent classification: <100ms
- Context retrieval: <500ms
- Total response time: <5000ms
- Cache hit serving: <200ms
- Answer accuracy: >92%

**Use Cases:**
- Answering "What are my critical vulnerabilities?"
- Providing remediation steps
- Explaining incident chains
- Suggesting risk mitigation

---

### 5. [Real-Time Updates (WebSocket/SSE)](./05-real-time-updates.md)
**Purpose:** Understand how real-time security updates are delivered to connected browsers using WebSocket and Server-Sent Events

**Scope:** Connection establishment → Subscription → Event routing → State synchronization → Reconnection resilience

**Connection Types:**
- **Primary:** WebSocket (full duplex, low latency)
- **Fallback 1:** Server-Sent Events/SSE (HTTP, unidirectional)
- **Fallback 2:** Long polling (HTTP POST, high overhead)
- **Last Resort:** Manual refresh

**Event Types:**
- `alert.created` - New security alert
- `asset.updated` - Asset changes
- `vulnerability.published` - New vulnerability
- `sync.completed` - Connector sync completed

**Key Concepts:**
- WebSocket handshake and upgrade
- Topic-based pub/sub subscriptions
- Permission-based event filtering
- Message batching and debouncing
- Exponential backoff reconnection
- Catch-up logic for missed events
- BroadcastChannel API for multi-tab sync
- Zustand state management

**Performance Targets:**
- Connection establishment: <500ms
- Message latency: <100ms (P95)
- Reconnect time: <2000ms
- Message throughput: >1000/sec per server
- Memory per connection: <100KB

**Use Cases:**
- Receiving real-time alerts
- Seeing asset changes immediately
- Multi-device state synchronization
- Network disconnection recovery

---

## Data Flow Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│ Presentation Layer (React Components)            │
│ └─ TanStack Query, Zustand, Tailwind CSS        │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ API Gateway Layer                               │
│ ├─ Fastify routing & middleware                 │
│ ├─ WebSocket server (Socket.io/ws)              │
│ ├─ Auth middleware (Okta validation)            │
│ └─ Request/Response processing                  │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ Application Logic Layer                         │
│ ├─ Aggregation service (dedup, correlate)       │
│ ├─ AI assistant (intent, RAG, LLM)              │
│ ├─ Sync service (connector orchestration)       │
│ └─ Analytics & enrichment                       │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ Data Layer                                      │
│ ├─ PostgreSQL (transactional data)              │
│ ├─ Redis (caching, pub/sub, sessions)           │
│ ├─ ClickHouse (analytics, archival)             │
│ ├─ ChromaDB (vector embeddings)                 │
│ └─ Elasticsearch (full-text search)             │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ Integration Layer                               │
│ ├─ 45+ external connectors                      │
│ ├─ Webhook receivers                            │
│ ├─ SQS job queue                                │
│ └─ External APIs (Claude, Okta, etc)            │
└─────────────────────────────────────────────────┘
```

## Data Flow Patterns

### Pattern 1: Request-Response Cycle
**Used by:** Dashboard, Asset queries, Compliance checks

```
User Request
    ↓
Request validation
    ↓
Permission check
    ↓
Cache check (Redis)
    ├─ HIT → Return cached data (fast)
    └─ MISS → Query database
         ↓
     Database query
         ↓
     Response aggregation
         ↓
     Cache storage (TTL)
    ↓
Response formatting
    ↓
User receives response
```

**Performance:** 50ms-2s depending on cache effectiveness

---

### Pattern 2: Scheduled Ingestion
**Used by:** Connector syncs, Data import

```
Scheduler triggers job
    ↓
Job queued in SQS
    ↓
Sync service processes
    ├─ Fetch credentials from Secrets Manager
    ├─ Authenticate to external system
    ├─ Fetch data with rate limiting
    ├─ Normalize to unified schema
    └─ Deduplication & upsert
    ↓
Store results in database
    ↓
Archive to analytics store
    ↓
Emit completion event
    ↓
Notify subscribers
```

**Performance:** 5-300s depending on connector complexity

---

### Pattern 3: Real-Time Streaming
**Used by:** Live alerts, Status updates

```
Event generated in external system
    ↓
Webhook received / Polling detected change
    ↓
Event normalized
    ↓
Published to Redis Pub/Sub
    ↓
Connected clients receive event
    ├─ WebSocket (low latency)
    ├─ SSE (HTTP fallback)
    └─ Polling (last resort)
    ↓
Client updates state (Zustand)
    ↓
React components re-render
    ↓
User sees update in UI
```

**Performance:** 100-500ms end-to-end latency

---

### Pattern 4: AI-Assisted Analysis
**Used by:** Question answering, Threat analysis

```
User submits question
    ↓
Intent classification (ML model)
    ↓
Context retrieval (vector search + keyword)
    ↓
Check response cache
    ├─ HIT → Return previous answer
    └─ MISS → Continue
    ↓
Prepare tools (MCP definitions)
    ↓
Send to Claude LLM
    ↓
LLM decides if tools needed
    ├─ YES → Call tool(s), get results, loop
    └─ NO → Generate response
    ↓
Format with citations
    ↓
Cache response
    ↓
Return to user
```

**Performance:** 2-5s for new questions, <200ms for cached

---

## Cross-Diagram Relationships

### Data Dependencies

```
01-Dashboard Request
    ↓
02-Connector Sync (provides data to query)
    ├─ Aggregates into unified database
    └─ Enables multi-source views
    ↓
03-Multi-Connector Aggregation
    ├─ Queries data from 01 + 02
    ├─ Returns deduplicated view
    └─ Feeds into 01 responses
    ↓
04-AI Assistant
    ├─ Uses context from 03
    ├─ Invokes tools for 02/03 queries
    └─ Generates insights from data
    ↓
05-Real-Time Updates
    ├─ Notifies about changes from 02
    ├─ Updates based on 03 correlation
    ├─ Streams AI analysis results
    └─ Refreshes cached views from 01
```

### Component Dependencies

```
Frontend Components
├─ Dashboard (01 - fetching)
│  └─ Subscribed to updates (05)
├─ Asset List (01/03 - querying)
│  └─ Real-time updates (05)
├─ AI Chat (04 - asking questions)
│  └─ Uses context from 01/02/03
└─ Alert Timeline (02/05 - streaming)
   └─ History from database

Backend Services
├─ Sync Service (02 - ingestion)
├─ Aggregation Service (03 - fusion)
├─ AI Service (04 - analysis)
└─ WebSocket Gateway (05 - streaming)

Data Storage
├─ PostgreSQL
│  ├─ Raw data from 02
│  ├─ Queries for 01/03/04
│  └─ Event history for 05
├─ Redis
│  ├─ Cache for 01
│  ├─ Pub/Sub for 05
│  └─ Dedup cache for 03
├─ ClickHouse
│  └─ Archive from 02
└─ ChromaDB
   └─ Embeddings for 04
```

## Common Scenarios

### Scenario 1: User Receives Critical Alert
```
1. EDR (Crowdstrike) detects suspicious process [02]
2. Webhook triggers alert creation [02]
3. Alert published to Redis pub/sub [02]
4. WebSocket broadcasts to user [05]
5. User's browser receives event in real-time [05]
6. Browser updates Zustand store [05]
7. Dashboard re-renders with new alert [01]
8. User clicks alert to see details [01]
9. Dashboard queries aggregated view [03]
10. Multi-source context shown [03]
11. User asks AI "What should I do?" [04]
12. AI analyzes using all sources [04]
13. User follows recommendations [04]
```

### Scenario 2: New Vulnerability Impacts Production Assets
```
1. CVE published in NVD [02 vulnerability sync]
2. Vulnerability added to database [02]
3. Asset manager tags asset as vulnerable [01]
4. Dashboard refresh shows in compliance view [01]
5. Real-time update notifies user [05]
6. User asks AI "Which assets are affected?" [04]
7. AI queries aggregation engine [04/03]
8. Result shows all affected assets [03]
9. AI provides remediation steps [04]
10. Patch pushed to asset [02 next sync]
```

### Scenario 3: Multi-Cloud Asset Discovery
```
1. Scheduled sync triggers [02]
2. AWS EC2 instances fetched [02]
3. Azure VMs fetched [02]
4. Same asset detected in both clouds [02]
5. Deduplication identifies match [03]
6. Merged record created [03]
7. User views dashboard [01]
8. Queries show unified asset [03]
9. User sees both cloud sources [01]
10. Real-time updates if asset changes in either cloud [05]
```

## Monitoring and Debugging

### Key Metrics Across Flows

```
01-Dashboard:
├─ API response time (p50, p95, p99)
├─ Cache hit rate (target >70%)
├─ Database query latency
└─ FCP/LCP times

02-Connector Sync:
├─ Sync success rate (target >95%)
├─ Data freshness (time since last sync)
├─ Records per connector
└─ Error rate by connector type

03-Aggregation:
├─ Deduplication match rate
├─ Correlation computation time
├─ Cache effectiveness
└─ False positive/negative rates

04-AI Assistant:
├─ Intent classification accuracy
├─ Answer relevance scoring
├─ Tool call success rate
└─ User satisfaction (feedback)

05-Real-Time:
├─ WebSocket connection success rate
├─ Message delivery latency
├─ Reconnection frequency
└─ Events per second throughput
```

### Distributed Tracing

All requests include:
- `Request-ID`: Unique request identifier
- `Trace-ID`: Follows entire request path
- `Span-ID`: Individual operation identifier
- `User-ID`: Which user made request
- `Timestamp`: When request started

Use tools like:
- SigNoz (traces + logs + metrics)
- Datadog (APM)
- Jaeger (distributed tracing)

## Next Steps

1. **Implementation**: Use these diagrams to guide development of each component
2. **Testing**: Ensure each flow is tested end-to-end
3. **Monitoring**: Set up observability for each diagram's components
4. **Optimization**: Use metrics to identify bottlenecks
5. **Documentation**: Keep diagrams updated as architecture evolves

## Related Documentation

- [System Architecture](../architecture/01-system-architecture.md) - High-level design
- [Platform Alignment](../architecture/02-platform-alignment.md) - Technology choices
- [Nexus UI PRD](../../planning-artifacts/nexus-ui-uplift-prd.md) - Product requirements
- [Architecture Document](../../planning-artifacts/nexus-architecture-document.md) - Detailed design

## Contributing

When updating diagrams:
1. Keep sequence flows clear and linear
2. Add detailed sections explaining each layer
3. Include performance targets
4. Document error handling
5. Provide real examples with actual data
6. Update cross-references to other diagrams
7. Include related resources and tools

Last Updated: 2024-01-15
Maintained By: Architecture Team
