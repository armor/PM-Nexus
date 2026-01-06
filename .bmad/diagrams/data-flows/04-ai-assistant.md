# AI Assistant Question Answering Flow

## Overview

This diagram illustrates how the Nexus UI AI Assistant processes natural language questions, retrieves relevant context from the platform's security data, performs intelligent analysis, and generates accurate, actionable responses. It demonstrates intent classification, context retrieval, LLM processing, and response generation with source attribution.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User<br/>(Chat Interface)
    participant Chat as Chat Service<br/>(Message Handler)
    participant Intent as Intent Classifier<br/>(ML Model)
    participant Context as Context Retriever<br/>(RAG Engine)
    participant MCP as MCP Server<br/>(Tool Executor)
    participant Cache as Response Cache<br/>(Redis)
    participant LLM as LLM Service<br/>(Claude API)
    participant DB as Data Layer<br/>(PostgreSQL/ClickHouse)
    participant Response as Response<br/>Generator

    User->>Chat: 1. Submit Question<br/>"What are my critical vulnerabilities<br/>on internet-facing servers?"

    Chat->>Chat: 2. Input Validation<br/>Check length, encoding, safety
    Note over Chat: Length: 75 chars<br/>Language: English<br/>Content: Safe

    Chat->>Cache: 3. Check Question Cache<br/>Hash: sha256(question)
    alt Cached Response (Same Question)
        Cache-->>Chat: 4a. Return Previous Response<br/>+ "From cache"
        Chat->>User: 5a. Display Cached Answer
        Note over Chat,User: Fast path: <100ms<br/>Same answer as before
    else Cache Miss (New Question)
        Chat->>Intent: 4b. Classify Intent<br/>question_text, user_context

        Intent->>Intent: 5b. Extract Features<br/>Tokenization + embeddings
        Note over Intent: Tokens: 15<br/>Embedding dim: 1536

        Intent->>Intent: 6. Run Classification Model<br/>Multi-label classifier
        Note over Intent: Intent scores:<br/>├─ vulnerability_query: 0.95<br/>├─ asset_query: 0.72<br/>├─ risk_assessment: 0.68<br/>└─ remediation: 0.15

        Intent-->>Chat: 7. Return Intent Scores<br/>Top intent: VULNERABILITY_QUERY

        alt Intent: VULNERABILITY_QUERY
            Chat->>Context: 8a. Retrieve Vulnerability Context<br/>Retrieved 1500 vulnerabilities
            Context->>Context: 9a1. Filter by criticality<br/>Status = CRITICAL

            Context->>Context: 9a2. Filter by exposure<br/>asset.exposure = INTERNET_FACING

            Context->>DB: 9a3. Query database
            Note over Context,DB: SELECT vulnerabilities<br/>WHERE severity = 'critical'<br/>AND asset.internet_facing = true<br/>ORDER BY cvss DESC LIMIT 50

            DB-->>Context: 10a. Return 23 critical vulns

            Context->>Context: 11a. Rank by Relevance<br/>BM25 scoring algorithm
            Note over Context: Score = (<br/>  frequency(query_term) × 0.6 +<br/>  idf(term) × 0.4<br/>)

            Context-->>Chat: 12a. Return Ranked Results<br/>Top 10 vulnerabilities<br/>with sources

        else Intent: ASSET_QUERY
            Chat->>Context: 8b. Retrieve Asset Context<br/>Retrieve 300 assets

            Context->>DB: 9b. Query by asset type<br/>SELECT * FROM assets<br/>WHERE type in (...)<br/>ORDER BY risk_score DESC

            Context-->>Chat: 12b. Return Asset Data<br/>Top 20 assets

        else Intent: RISK_ASSESSMENT
            Chat->>Context: 8c. Retrieve Risk Context<br/>Retrieve risk metrics
            Chat->>MCP: 8c. Invoke Risk Calculation<br/>Tool: analyze_risk
            Note over Chat,MCP: Execute MCP tool to<br/>compute custom risk scores

        else Intent: CUSTOM
            Chat->>MCP: 8d. Invoke MCP Tools<br/>Based on question content
            Note over Chat,MCP: Parse question for<br/>tool names and parameters
        end

        Chat->>MCP: 13. Prepare Tool Calls<br/>for LLM execution
        Note over Chat,MCP: Tools available:<br/>├─ get_vulnerabilities<br/>├─ get_assets<br/>├─ analyze_risk<br/>├─ get_compliance_status<br/>├─ search_assets<br/>└─ get_threat_context

        MCP->>MCP: 14. Create Tool Definitions<br/>OpenAI schema format
        Note over MCP: {\br/>  "name": "get_vulnerabilities",<br/>  "description": "...",<br/>  "parameters": {...}<br/>}

        Chat->>LLM: 15. Send to Claude LLM<br/>with context and tools
        Note over Chat,LLM: System Prompt:<br/>"You are a security analyst...",<br/>User Question,<br/>Retrieved Context,<br/>Tool Definitions,<br/>Temperature: 0.7

        LLM->>LLM: 16. Analyze Question<br/>with Retrieved Context
        Note over LLM: Process:<br/>1. Parse user intent<br/>2. Review context<br/>3. Identify patterns<br/>4. Determine tools needed

        alt LLM Needs More Data
            LLM->>LLM: 17a. Request Tool Call
            Note over LLM: "I need to call<br/>get_vulnerabilities()<br/>with filters: ..."
            LLM-->>Chat: Decision: Use Tools

            Chat->>MCP: 18a. Execute Tool Call<br/>Tool: get_vulnerabilities<br/>Params: {<br/>  severity: "critical",<br/>  exposure: "internet",<br/>  limit: 50<br/>}

            MCP->>DB: 19a. Execute Query<br/>Fetch from database

            DB-->>MCP: 20a. Return Results<br/>23 vulnerabilities

            MCP-->>Chat: 21a. Return Tool Result<br/>JSON data

            Chat->>LLM: 22a. Send Tool Result<br/>to LLM context
            Note over Chat,LLM: Add to message history<br/>for continued reasoning

            LLM->>LLM: 23a. Process Tool Result<br/>Continue analysis
            Note over LLM: "Now I have the data,<br/>I can answer..."

        else LLM Has Enough Data
            LLM->>LLM: 17b. Generate Response<br/>from context
            Note over LLM: "Based on the provided<br/>data, here's what I found..."
        end

        loop Additional Tool Calls
            alt More Tools Needed
                LLM-->>Chat: Request more tools
                Chat->>MCP: Execute tool call
                MCP->>DB: Query database
                DB-->>MCP: Return results
                MCP-->>Chat: Send results
                Chat->>LLM: Add to context
            else Done
                break No more tools needed
            end
        end

        LLM->>LLM: 24. Format Response<br/>Markdown with citations
        Note over LLM: Response Structure:<br/>├─ Summary<br/>├─ Detailed Findings<br/>├─ Analysis<br/>├─ Recommendations<br/>└─ Source Attribution

        LLM-->>Chat: 25. Return Final Response<br/>with metadata

        Chat->>Response: 26. Post-Process Response<br/>Add formatting, validate

        Response->>Response: 27a. Validate Structure<br/>Check required sections
        Note over Response: Validate:<br/>├─ Has summary<br/>├─ Sources cited<br/>├─ Markdown valid<br/>└─ Length <4000 tokens

        Response->>Response: 27b. Add Citations<br/>Format source references
        Note over Response: [1] Qualys: CVE-2024-1234<br/>[2] Dashboard: prod-web-01<br/>[3] CrowdStrike: Alert #5634

        Response->>Response: 27c. Add Context Links<br/>Create deep links to UI
        Note over Response: Link to:<br/>├─ Vulnerability details<br/>├─ Asset view<br/>├─ Alert timeline<br/>└─ Remediation steps

        Response-->>Chat: 28. Return Formatted<br/>Response object

        Chat->>Cache: 29. Store Response<br/>Question → Response cache<br/>TTL: 24 hours
        Note over Chat,Cache: Also store:<br/>├─ Intent classification<br/>├─ Tools used<br/>├─ Latency<br/>└─ User feedback

        Chat->>Chat: 30. Prepare Metadata<br/>execution_time: 4.2s<br/>tools_used: ["get_vulnerabilities"],<br/>sources_cited: 3,<br/>confidence: 0.92
    end

    Chat-->>User: 31. Display Response<br/>with formatting & sources
    Note over Chat,User: Display in chat:<br/>├─ Response text<br/>├─ Source links<br/>├─ Related questions<br/>└─ Feedback buttons

    User->>Chat: 32a. Provide Feedback<br/>Thumbs up/down,<br/>comment (optional)
    Note over User,Chat: Feedback: "Helpful and accurate"

    Chat->>Chat: 33. Log Feedback<br/>question, response,<br/>feedback, timestamp,<br/>user_id
    Note over Chat: Store in:<br/>├─ Analytics database<br/>├─ ML training queue<br/>└─ Team dashboard

    par Async Tasks
        Chat->>DB: 34a. Update Analytics<br/>questions_asked: +1<br/>avg_latency: update
        Note over Chat,DB: Metrics for monitoring
    and Async Tasks
        Chat->>Chat: 34b. Log to LLM<br/>Fine-tuning dataset<br/>(if positive feedback)
        Note over Chat: Collect positive<br/>examples for training
    and Async Tasks
        Chat->>Chat: 34c. Index Response<br/>Full-text search
        Note over Chat: Enable searching<br/>previous answers
    end

    User->>Chat: 35. Ask Follow-up<br/>"How do I patch these?"
    Note over User,Chat: Uses conversation<br/>context for understanding
```

## Intent Classification

### Intent Categories

```
Intent Classification Hierarchy:

├─ VULNERABILITY_QUERY (confidence: 0.95)
│  ├─ Question: "critical vulnerabilities"
│  ├─ Keywords: [critical, vulnerability, patch]
│  ├─ Context filtering: severity > HIGH, status = OPEN
│  └─ Tools: get_vulnerabilities, search_assets
│
├─ ASSET_QUERY (confidence: 0.88)
│  ├─ Question: "production servers"
│  ├─ Keywords: [asset, server, host, infrastructure]
│  ├─ Context filtering: environment = PRODUCTION
│  └─ Tools: get_assets, analyze_risk
│
├─ RISK_ASSESSMENT (confidence: 0.72)
│  ├─ Question: "risk score"
│  ├─ Keywords: [risk, threat, exposure, impact]
│  ├─ Context filtering: compute risk metrics
│  └─ Tools: analyze_risk, get_threat_context
│
├─ COMPLIANCE_QUERY (confidence: 0.68)
│  ├─ Question: "compliance status"
│  ├─ Keywords: [compliance, standard, control, audit]
│  ├─ Context filtering: framework = PCI-DSS
│  └─ Tools: get_compliance_status
│
├─ REMEDIATION_QUERY (confidence: 0.65)
│  ├─ Question: "how to fix"
│  ├─ Keywords: [fix, patch, remediate, mitigate]
│  ├─ Context filtering: get open findings
│  └─ Tools: get_remediation_steps, search_kb
│
├─ THREAT_ANALYSIS (confidence: 0.82)
│  ├─ Question: "threat impact"
│  ├─ Keywords: [threat, attack, indicator, campaign]
│  ├─ Context filtering: threat_intel + affected_assets
│  └─ Tools: get_threat_context, correlate_incidents
│
├─ OPERATIONAL_QUERY (confidence: 0.71)
│  ├─ Question: "how to configure"
│  ├─ Keywords: [configure, setup, install, deploy]
│  ├─ Context filtering: operational docs
│  └─ Tools: search_documentation, get_setup_guide
│
└─ GENERAL_CONVERSATION (confidence: 0.45)
   ├─ Question: General chat/help
   ├─ Context filtering: General knowledge
   └─ Tools: None (pure LLM response)
```

### Multi-Intent Handling

```
Question: "Which production assets have critical
vulnerabilities that violate compliance requirements?"

Intent 1: ASSET_QUERY (0.85)
  → filter: environment = PRODUCTION

Intent 2: VULNERABILITY_QUERY (0.92)
  → filter: severity = CRITICAL

Intent 3: COMPLIANCE_QUERY (0.78)
  → filter: compliance_status = NON_COMPLIANT

Combined approach:
1. Retrieve production assets
2. Filter for critical vulnerabilities
3. Check compliance violation
4. Intersect results
5. Score by impact
```

## Context Retrieval (RAG)

### Embedding and Search

```
Question: "What are my critical vulnerabilities?"

Step 1: Embed Question
question_embedding = embed("What are my critical vulnerabilities?")
output: vector of 1536 dimensions

Step 2: Vector Search in ChromaDB
find_similar(question_embedding, k=10)
Returns:
├─ doc_1: CVE-2024-1234 (similarity: 0.92)
├─ doc_2: Patch Tuesday (similarity: 0.88)
├─ doc_3: Vulnerability Management (similarity: 0.85)
└─ ... (7 more results)

Step 3: Hybrid Search
Combine vector search + keyword search

Vector Results (0-1 scale):
├─ CVE-2024-1234: 0.92
├─ CVE-2024-5678: 0.88
└─ CVE-2024-9999: 0.85

Keyword Results (BM25):
├─ "critical": 15.2
├─ "vulnerability": 12.8
└─ "patch": 9.5

Combined Score (0.7 × vector + 0.3 × keyword):
├─ CVE-2024-1234: 0.91
├─ CVE-2024-5678: 0.87
└─ CVE-2024-9999: 0.85

Step 4: Filter by Query Intent
Remove non-relevant results:
├─ Keep: CVE-2024-1234 (CRITICAL)
├─ Keep: CVE-2024-5678 (HIGH)
└─ Remove: "Patch Tuesday" (not CRITICAL)

Final Context (top 10):
Selected 8 highly relevant documents
Total tokens: 2,400 / 3,600 limit
```

### Context Sources

```
Internal Data Sources:
├─ Vulnerability Database
│  ├─ ID, CVE, CVSS score
│  ├─ Affected assets
│  ├─ Status, dates
│  └─ Remediation steps
│
├─ Asset Database
│  ├─ Name, type, location
│  ├─ Owner, cost center
│  ├─ Health status
│  └─ Recent changes
│
├─ Alert/Event Logs
│  ├─ EDR alerts
│  ├─ SIEM events
│  ├─ Compliance violations
│  └─ Timestamps
│
├─ Compliance Data
│  ├─ Control status
│  ├─ Audit findings
│  ├─ Evidence
│  └─ Remediation plans
│
└─ Knowledge Base
   ├─ Runbooks
   ├─ FAQ
   ├─ Best practices
   └─ Procedures

External Data Sources:
├─ Threat Intelligence
│  ├─ CVE feeds
│  ├─ Threat campaigns
│  └─ Indicators
│
└─ Public Documentation
   ├─ CIS Benchmarks
   ├─ NIST guidelines
   └─ Vendor guides
```

## MCP Server Tools

### Available Tools

```yaml
Tools Registry:

- name: get_vulnerabilities
  description: Query vulnerabilities from the database
  parameters:
    severity: [CRITICAL, HIGH, MEDIUM, LOW]
    status: [OPEN, MITIGATED, PATCHED]
    affected_asset_id: UUID (optional)
    limit: 50 (default)
  execution_time: 100-500ms

- name: get_assets
  description: Query assets with filters
  parameters:
    type: [server, workstation, network, container]
    environment: [production, staging, dev]
    owner_id: UUID (optional)
    risk_score_min: 0-100
    limit: 100 (default)
  execution_time: 200-800ms

- name: analyze_risk
  description: Compute risk score for entity
  parameters:
    entity_id: UUID
    entity_type: [asset, user, application]
    include_context: boolean
  execution_time: 500-2000ms

- name: get_compliance_status
  description: Get compliance framework status
  parameters:
    framework: [PCI-DSS, HIPAA, SOC2, ISO27001]
    asset_id: UUID (optional)
    include_failed_controls: boolean
  execution_time: 300-1000ms

- name: search_assets
  description: Full-text search on assets
  parameters:
    query: string
    type: [server, workstation, network]
    limit: 50 (default)
  execution_time: 200-500ms

- name: get_threat_context
  description: Get threat intelligence context
  parameters:
    threat_id: string (optional)
    asset_id: UUID (optional)
    include_indicators: boolean
  execution_time: 100-300ms

- name: correlate_incidents
  description: Find related incidents
  parameters:
    incident_id: UUID
    time_window_minutes: 60 (default)
    include_related_assets: boolean
  execution_time: 1000-3000ms

- name: search_documentation
  description: Search knowledge base
  parameters:
    query: string
    category: [runbooks, faq, best-practices]
    limit: 10 (default)
  execution_time: 50-200ms
```

## LLM Interaction

### System Prompt

```
You are a security analyst assistant for the Nexus
security platform. Your role is to:

1. Understand security questions from users
2. Use provided context data to answer accurately
3. Call tools when you need current data
4. Cite sources for all claims
5. Prioritize critical findings
6. Provide actionable recommendations

Guidelines:
- Be precise and factual
- Always cite your sources
- Explain reasoning clearly
- Highlight critical risks in bold
- Provide step-by-step remediation
- Link to relevant UI pages
- Acknowledge confidence levels
- Ask for clarification if ambiguous

Tools Available:
[Tool definitions provided as JSON schema]

Instructions:
- If information is not in provided context, use tools
- Prefer specific data over general knowledge
- Include execution confidence (0-100%)
- Format response in Markdown
- Keep response under 2000 words
- Use tables for structured data
```

### Token Management

```
Conversation Context Token Limits:

Model: Claude Haiku 4.5 (200K context)
Target allocation:
├─ System prompt: 500 tokens
├─ User question: 100-200 tokens
├─ Retrieved context: 2000-3000 tokens
├─ Tool definitions: 500 tokens
├─ Previous messages: 2000 tokens
├─ Response budget: 2000 tokens
└─ Buffer: remaining

Token Budget Tracking:

Initial context: 5000 tokens
- System prompt: -500 (4500 left)
- User question: -150 (4350 left)
- Context docs: -2000 (2350 left)
- Tools: -300 (2050 left)
- Previous msgs: -1000 (1050 left)
- Response: -1000 (50 left)

When running out of tokens:
1. Prioritize most recent messages
2. Summarize older context
3. Remove least relevant documents
4. Use tool results only
```

## Response Generation

### Response Structure

```markdown
# Answer

## Summary
1-2 sentence summary of key finding

## Detailed Findings

### Finding 1
- Asset: prod-web-01
- Vulnerability: CVE-2024-1234
- Severity: CRITICAL
- Impact: Code execution
- Status: Unpatched

### Finding 2
- Asset: prod-api-01
- ...

## Analysis
Explain patterns and implications

## Recommendations

1. Immediate (24 hours)
   - Step-by-step fix instructions
   - Impact of remediation

2. Short-term (1 week)
   - Additional hardening
   - Monitoring improvements

3. Long-term (ongoing)
   - Process improvements
   - Architecture changes

## Sources

[1] Qualys: CVE-2024-1234 vulnerability details
[2] CrowdStrike: Alert #5634 on prod-web-01
[3] Dashboard: Asset inventory for prod
[4] Compliance: PCI-DSS requirement #6.2

## Related Resources

- View full asset details: [link to prod-web-01]
- Patch guide: [link to KB article]
- Ticket template: [link to Jira]
```

### Citation Format

```
Inline Citations:
"According to our vulnerability scan [1], CVE-2024-1234
is actively exploited in the wild."

Bracketed References:
[1] Qualys: CVE-2024-1234 (2024-01-15, high confidence)
[2] Dashboard: prodweb-01 vulnerability list
[3] Threat Intel: "Exploitation in the wild" report

Citation Metadata:
{
  "source_id": "vuln-12345",
  "source_system": "Qualys",
  "source_type": "vulnerability_database",
  "last_updated": "2024-01-15T10:30:00Z",
  "confidence": 0.95,
  "link": "https://dashboard/vulnerabilities/cve-2024-1234"
}
```

## Conversation Context

### Multi-Turn Dialogue

```
Turn 1:
User: "What critical vulnerabilities do we have?"
Assistant: "You have 23 critical vulnerabilities..."

Turn 2:
User: "How do I patch these?"
Assistant: Uses context:
├─ Previous question about vulnerabilities
├─ Already knows which vulns are critical
├─ References same assets
└─ Provides patch instructions

Turn 3:
User: "What about servers in production?"
Assistant: Filters to:
├─ Previous vulnerabilities
├─ Constrains to production environment
├─ Provides updated count and severity
```

### Conversation State

```typescript
interface ConversationState {
  conversation_id: UUID;
  user_id: UUID;
  created_at: ISO8601DateTime;
  last_message_at: ISO8601DateTime;

  // Conversation context
  intent_history: Intent[];
  entity_mentions: {
    type: string;
    id: UUID;
    first_mentioned_turn: number;
  }[];
  filters_applied: {
    severity?: string;
    environment?: string;
    asset_type?: string;
  };

  // Messages
  messages: Message[];

  // Performance
  total_tokens_used: number;
  avg_response_time_ms: number;

  // Feedback
  helpful_count: number;
  unhelpful_count: number;
}
```

## Error Handling

### Graceful Degradation

```
Tool Failure Scenarios:

1. Tool Timeout (>10 seconds)
   → Use cached data if available
   → Explain data freshness limitation
   → Offer alternative query

2. Database Connection Error
   → Fall back to previous context
   → Provide answer with known data
   → Suggest retry

3. LLM Rate Limit
   → Queue request for retry
   → Provide interim response
   → Notify user of delay

4. Tool Returns Empty Result
   → Clarify question with user
   → Expand search parameters
   → Suggest related questions

Error Message Format:
"I wasn't able to retrieve the latest data
from [system], but based on information from
[alternative source], here's what I found..."
```

## Monitoring and Analytics

### Performance Metrics

```
Response Metrics:
- Questions answered: 1000/day
- Average latency: 2-4 seconds
- Tool usage frequency
- Cache hit rate: 60%
- User satisfaction: 4.2/5.0

Quality Metrics:
- Answer accuracy: 92%
- Citation completeness: 98%
- Hallucination rate: <2%
- Feedback score: 85% helpful

Cost Metrics:
- Avg tokens per question: 4000
- Cost per question: $0.02-0.05
- LLM API usage trends
```

### User Feedback Loop

```
Feedback Collection:
1. Thumbs up/down on response
2. Optional comment/reason
3. Rating scale (1-5)
4. Suggestion text

Feedback Processing:
├─ Count metrics
├─ Identify patterns
├─ Flag for human review
├─ Train on positive examples
└─ Improve intent classifier

Feedback Handling:
- Negative feedback: Alert team for review
- Low confidence responses: Flag for verification
- Repeated questions: Check cache effectiveness
- Edge cases: Add to training data
```

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Intent Classification | <100ms | ML model inference |
| Context Retrieval | <500ms | Vector search + hybrid |
| MCP Tool Calls | <2000ms | Average all tools |
| LLM Response | <2000ms | Token generation |
| Post-processing | <200ms | Formatting + citations |
| Total Response Time | <5000ms | All steps combined |
| Cache Hit Serving | <200ms | Fast path |
| Context Accuracy | >90% | Retrieved relevance |
| Answer Accuracy | >92% | Fact correctness |

## Related Diagrams

- [Dashboard Request Flow](./01-dashboard-request.md) - Data retrieval
- [Multi-Connector Aggregation](./03-multi-connector.md) - Context sources
- [System Architecture](../architecture/01-system-architecture.md) - LLM integration

## Additional Resources

- [Retrieval Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401)
- [Claude API Documentation](https://docs.anthropic.com/en/docs/about-claude/latest-models)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Prompt Engineering Guide](https://github.com/brexhq/prompt-engineering)
- [Vector Embeddings](https://huggingface.co/docs/transformers/tasks/sentence_similarity)
