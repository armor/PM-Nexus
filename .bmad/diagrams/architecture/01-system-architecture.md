# System Architecture Diagram

## Full Platform Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[Mobile Browser]
        C[Claude Code / MCP Client]
    end

    subgraph "CDN & Edge"
        D[CloudFront CDN]
        E[WAF / DDoS Protection]
    end

    subgraph "Load Balancing"
        F[Application Load Balancer]
    end

    subgraph "Kubernetes Cluster - EKS"
        subgraph "Ingress Layer"
            G[Kong API Gateway]
        end

        subgraph "Frontend Services"
            H[Nexus Frontend<br/>Next.js 15 / React 19]
        end

        subgraph "API Services"
            I[Auth Service<br/>Okta OAuth2]
            J[Core API<br/>Node.js / Fastify]
            K[Metrics API<br/>Aggregation]
            L[Connector Service<br/>Data Sync]
        end

        subgraph "Worker Services"
            M[Job Runner<br/>Scheduled Tasks]
            N[Notification Service<br/>Alerts / Email]
        end

        subgraph "MCP Services"
            O[Nexus MCP Server<br/>Claude Tools]
            P[Jira MCP Server<br/>Atlassian Tools]
        end
    end

    subgraph "Data Layer"
        Q[(PostgreSQL<br/>RDS Multi-AZ)]
        R[(Redis<br/>ElastiCache)]
        S[(OpenSearch<br/>Logs & Search)]
        T[S3<br/>Assets & Backups]
    end

    subgraph "Message Queue"
        U[SQS<br/>Async Processing]
        V[SNS<br/>Notifications]
    end

    subgraph "External Integrations"
        W[AWS Security Hub]
        X[CrowdStrike]
        Y[Okta / Azure AD]
        Z[45+ Connectors]
    end

    A --> D
    B --> D
    C --> O
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    G --> J
    G --> K
    J --> Q
    J --> R
    K --> Q
    K --> R
    L --> U
    L --> Z
    M --> U
    N --> V
    O --> J
    P --> J
    U --> L
    Z --> W
    Z --> X
    Z --> Y

    classDef frontend fill:#61DAFB,stroke:#333,stroke-width:2px
    classDef api fill:#68D391,stroke:#333,stroke-width:2px
    classDef data fill:#F6AD55,stroke:#333,stroke-width:2px
    classDef external fill:#B794F4,stroke:#333,stroke-width:2px
    classDef mcp fill:#F687B3,stroke:#333,stroke-width:2px

    class H frontend
    class I,J,K,L api
    class Q,R,S,T data
    class W,X,Y,Z external
    class O,P mcp
```

<!-- SVG: 01-system-architecture-1.svg -->
![Diagram 1](../../diagrams-svg/architecture/01-system-architecture-1.svg)


## Layer Descriptions

### Client Layer
- **Web Browser**: Primary access via desktop/laptop
- **Mobile Browser**: Responsive mobile experience
- **MCP Client**: Claude Code / AI assistant integration

### CDN & Edge
- **CloudFront**: Static asset caching, global distribution
- **WAF**: Web Application Firewall, rate limiting, DDoS protection

### Kubernetes Services
- **Frontend**: Next.js 15 with React 19, server-side rendering
- **API Services**: RESTful APIs with Fastify
- **Workers**: Background job processing
- **MCP**: Model Context Protocol servers for AI tooling

### Data Layer
- **PostgreSQL**: Primary transactional database (Multi-AZ)
- **Redis**: Session cache, query cache, rate limiting
- **OpenSearch**: Log aggregation and full-text search
- **S3**: Object storage for exports, backups

### External Integrations
- 45+ security tool connectors
- Cloud providers (AWS, Azure, GCP)
- Identity providers (Okta, Azure AD)
