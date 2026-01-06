# Dashboard Data Request Cycle

## Overview

This diagram illustrates the complete data flow for dashboard requests in the Nexus UI platform, from initial user request through UI rendering. It demonstrates the interplay between TanStack Query, Fastify API layer, authentication, database, caching, and the frontend rendering pipeline.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User Browser
    participant UI as React Dashboard<br/>(TanStack Query)
    participant Network as Network Layer<br/>(Fetch/Axios)
    participant API as Fastify API<br/>Layer
    participant Auth as Okta Auth<br/>Middleware
    participant Cache as Redis Cache<br/>Layer
    participant DB as PostgreSQL<br/>Database
    participant Render as UI Rendering<br/>Engine

    User->>UI: 1. Request Dashboard
    Note over User,UI: User navigates to /dashboard

    UI->>UI: 2. Check Local Cache<br/>(TanStack Query)
    alt Cache Hit
        UI->>UI: 3a. Return Cached Data
        UI->>Render: 4a. Skip API Call
    else Cache Miss / Stale
        UI->>Network: 3b. Initiate API Request
        Note over UI,Network: GET /api/dashboard/data

        Network->>API: 4b. HTTP GET Request
        Note over Network,API: Authorization header included<br/>Request ID: uuid-12345

        API->>Auth: 5. Verify Token<br/>(JWT/Okta)
        alt Token Valid
            Auth->>Auth: 6a. Extract User Context<br/>User ID, Roles, Permissions
            Auth-->>API: 6b. User Context
        else Token Invalid
            Auth-->>API: 6c. 401 Unauthorized
            API-->>Network: 7a. Error Response
            Network-->>UI: 8a. Handle Auth Error
            UI->>User: 9a. Redirect to Login
        end

        API->>Cache: 7. Check Redis Cache<br/>Key: dashboard:{userId}
        alt Cache Hit (Valid)
            Cache-->>API: 8. Return Cached Data
            Note over API,Cache: TTL: 5 minutes
            API->>DB: (Skip DB Query)
        else Cache Miss
            API->>DB: 8. Query Database
            Note over API,DB: SELECT * FROM dashboard_data<br/>WHERE user_id = {userId}<br/>AND tenant_id = {tenantId}

            alt Query Successful
                DB-->>API: 9. Return Query Results
                Note over DB,API: 50-500ms latency<br/>Aggregated from multiple tables
                API->>API: 10. Data Transformation<br/>Format Response
                API->>Cache: 11. Store in Redis<br/>Key: dashboard:{userId}<br/>TTL: 300 seconds
                Cache-->>API: 12. Cache Confirmed
            else Query Error
                DB-->>API: 9. Error Response<br/>(Connection, Timeout, etc)
                API->>API: 10. Log Error<br/>(SigNoz/Datadog)
                API-->>Network: 11. 500 Error Response
            end
        end

        API->>API: 12. Add Response Headers<br/>Cache-Control, ETag, CORS
        API-->>Network: 13. HTTP 200 + JSON
        Note over API,Network: Response Time: 50-200ms<br/>Compressed payload

        Network->>UI: 14. Receive API Response
        UI->>UI: 15. Parse JSON<br/>Validate Schema
        alt Schema Valid
            UI->>UI: 16. Update TanStack Query Cache
            Note over UI: Store in @tanstack/react-query<br/>Invalidate related queries
            UI->>Render: 17. Trigger Re-render
        else Schema Invalid
            UI->>UI: 16. Log Validation Error
            UI->>User: 17. Show Error Toast
        end
    end

    Render->>Render: 18. Render Components<br/>Memoization Applied
    Note over Render: Dashboard Cards<br/>Charts, Tables, Widgets<br/>Lazy-load below fold

    Render->>Render: 19. Apply Styling<br/>(Tailwind CSS)
    Render->>Render: 20. Compute Layout<br/>(CSS Grid/Flex)

    Render-->>User: 21. Display Dashboard
    Note over Render,User: Full render: 100-300ms<br/>FCP: 1.5s, LCP: 2.5s

    par Browser Activities
        User->>User: 22a. Scroll/Interact
        Render->>Render: Event Handler Execution
        Render->>User: Update UI State
    and Background
        UI->>UI: 22b. TanStack Query Polling<br/>(staleTime expired)
        Note over UI: Auto-refetch every 30s
        UI->>Network: Re-fetch Data
    end
```

<!-- SVG: 01-dashboard-request-1.svg -->
![Diagram 1](../../diagrams-svg/data-flows/01-dashboard-request-1.svg)


## Data Flow Layers

### Layer 1: Frontend (React/TanStack Query)
**Components:**
- React Dashboard Page Component
- TanStack Query (React Query) hooks
- Query client with cache management
- Stale-while-revalidate logic

**Key Features:**
- Automatic caching and synchronization
- Background refetching at configured intervals
- Request deduplication
- Optimistic updates support

**Performance Metrics:**
- Local cache hit: <5ms
- Query resolution: 50-200ms (API) or <5ms (cache)

### Layer 2: Network Transport Layer
**Components:**
- Fetch API or Axios HTTP client
- Request interceptors (auth token injection)
- Response interceptors (error handling)
- Network error handling and retries

**Headers Added:**
```
Authorization: Bearer {token}
X-Request-ID: {uuid}
X-API-Version: v1
Content-Type: application/json
Accept-Encoding: gzip, deflate
```

**Timeouts:**
- Connection: 10 seconds
- Request: 30 seconds
- Total: 60 seconds

### Layer 3: API Gateway (Fastify)
**Components:**
- HTTP routing and matching
- Middleware pipeline execution
- Request validation
- Response serialization

**Middleware Stack:**
1. Request logging (correlate with request ID)
2. Rate limiting check
3. CORS header injection
4. Auth middleware (Okta verification)
5. Request context setup
6. Response compression (gzip)
7. Error handling

**Processing Time:** 10-50ms (excluding downstream operations)

### Layer 4: Authentication (Okta)
**Components:**
- JWT token validation
- Token claims extraction
- Permission checking
- Tenant context establishment

**Token Lifecycle:**
```
Issued: JWT with 1-hour expiry
Refresh: Via refresh token rotation
Validation: RS256 signature verification
Claims: sub, email, tenant_id, roles
```

**Okta Integration:**
- Token endpoint: https://your-org.okta.com/oauth2/v1/token
- Introspect endpoint for validation
- Cache token validation result (TTL: 5 minutes)

### Layer 5: Cache Layer (Redis)
**Components:**
- Redis cluster for distributed caching
- Key: `dashboard:{userId}`
- Data structure: JSON serialized

**Cache Patterns:**
- **TTL Strategy:** 5 minutes for dashboard data
- **Invalidation:** On user action (create/update/delete)
- **Refresh:** Background job before expiry
- **Distributed:** Multi-region cache coherence via pub/sub

**Hit Rate Target:** 70-80%

**Cache Keys:**
```
dashboard:{userId}
dashboard:{userId}:summary
dashboard:{userId}:recent-alerts
dashboard:{userId}:metrics
```

### Layer 6: Database (PostgreSQL)
**Components:**
- Primary database replica for read queries
- Connection pooling (PgBouncer)
- Query optimization with indexes

**Queries Executed:**
```sql
-- Main dashboard data
SELECT * FROM dashboard_data
WHERE user_id = $1 AND tenant_id = $2

-- Recent alerts
SELECT * FROM alerts
WHERE tenant_id = $2 AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC LIMIT 50

-- User preferences
SELECT * FROM user_preferences
WHERE user_id = $1
```

**Performance Characteristics:**
- Query execution: 20-100ms
- Network roundtrip: 5-20ms
- Connection acquisition: <5ms
- Total latency: 50-150ms

**Indexes:**
- `dashboard_data(user_id, tenant_id)` - BTREE
- `alerts(tenant_id, created_at)` - BTREE
- `user_preferences(user_id)` - BTREE

### Layer 7: UI Rendering
**Components:**
- Virtual DOM reconciliation
- Component memoization (@memo)
- Lazy loading of below-fold content
- CSS-in-JS styling (Tailwind)

**Render Performance:**
- Initial render: 100-300ms
- First Contentful Paint (FCP): 1.5 seconds
- Largest Contentful Paint (LCP): 2.5 seconds
- Cumulative Layout Shift (CLS): <0.1

**Optimization Techniques:**
- React.memo for child components
- useMemo for expensive calculations
- Code splitting with dynamic imports
- Image lazy loading with Intersection Observer

## Error Handling Flows

### Authentication Failures
```
1. Token validation fails at Okta middleware
2. API returns 401 Unauthorized
3. Frontend detects 401 response
4. Clear stored token from localStorage
5. Redirect user to /login
6. Show "Session expired" message
7. User re-authenticates
```

### Database Query Errors
```
1. PostgreSQL connection timeout
2. API catches error in try/catch
3. Log error with correlation ID to SigNoz
4. Check if partial data available from cache
5. Return 500 with error details
6. Frontend shows "Unable to load dashboard" toast
7. Provide "Retry" button for manual refetch
8. Auto-retry with exponential backoff after 5s
```

### API Response Validation Errors
```
1. Response schema validation fails
2. Frontend detects validation error
3. Log validation error with response payload
4. Show "Data format error" notification
5. Fall back to cached data if available
6. Trigger error boundary to prevent crash
```

### Network Connection Errors
```
1. Network request times out
2. Frontend detects timeout error
3. Show "Connection timeout" message
4. Queue request for retry
5. Auto-retry with exponential backoff (500ms → 2s → 8s)
6. Show offline indicator if persistent failure
7. Resume on connection restore
```

## Caching Strategy

### Cache Hierarchy
```
Level 1: Browser Cache
├─ TanStack Query in-memory cache
├─ staleTime: 5 minutes
└─ gcTime: 10 minutes (garbage collection)

Level 2: Redis Cache (Server-Side)
├─ Key: dashboard:{userId}
├─ TTL: 5 minutes
└─ Shared across all API replicas

Level 3: Database
├─ PostgreSQL with replication
├─ Read replicas for analytics
└─ Full historical data
```

### Cache Invalidation
**Automatic Invalidation Triggers:**
1. TTL expiry (5 minutes)
2. User updates dashboard settings
3. New alerts arrive (webhook trigger)
4. Manual refresh action
5. Background job every 30 minutes

**Invalidation Mechanism:**
```
1. Delete from Redis: dashboard:{userId}
2. Publish to Redis Pub/Sub: dashboard:invalidated:{userId}
3. TanStack Query refetch triggered
4. Fresh data fetched from database
```

## Monitoring and Observability

### Key Metrics
- **API Response Time:** Track p50, p95, p99
- **Cache Hit Rate:** Target 70-80%
- **Database Query Time:** Track slow queries (>100ms)
- **Error Rate:** Track 4xx and 5xx responses
- **User Engagement:** FCP, LCP, CLS measurements

### Tracing
- **Request ID:** Injected in all requests
- **Trace ID:** Follows request through entire stack
- **Span Details:** Auth time, cache check time, DB query time
- **Error Context:** Full stack trace with line numbers

### Logging
- **SigNoz Integration:** Structured JSON logging
- **Log Levels:** DEBUG (local), INFO (production)
- **Sensitive Data:** Token and user ID redacted from logs
- **Audit Trail:** User actions logged with timestamps

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API Response Time (p95) | <200ms | Cache hit |
| API Response Time (p95) | <500ms | Cache miss |
| First Contentful Paint | <1.5s | Full page load |
| Largest Contentful Paint | <2.5s | Dashboard fully visible |
| Cache Hit Rate | >70% | Reduces backend load |
| Database Query Time (p95) | <100ms | With proper indexes |
| Network Latency | <50ms | Depends on geography |

## Related Diagrams

- [System Architecture](../architecture/01-system-architecture.md) - Overall system design
- [02-Connector Sync Flow](./02-connector-sync.md) - Data ingestion pipeline
- [Real-Time Updates Flow](./05-real-time-updates.md) - WebSocket/SSE updates

## Additional Resources

- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Fastify API Guide](https://www.fastify.io/)
- [Okta Authentication](https://developer.okta.com/)
- [Redis Caching Strategies](https://redis.io/topics/client-side-caching)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance.html)
