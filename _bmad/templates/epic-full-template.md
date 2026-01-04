# EPIC-{{epic_id}}: {{epic_title}}

> **This is the full documentation for humans and AI implementation.**
> For JIRA sync, see [EPIC-{{epic_id}}.md](./EPIC-{{epic_id}}.md)

**Status:** {{status}}
**Priority:** {{priority}}
**Owner:** {{team}}
**MVP Phase:** {{mvp_phase}}
**Created:** {{created_date}}
**Last Updated:** {{updated_date}}

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Business Value](#business-value)
4. [Success Metrics](#success-metrics)
5. [User Personas](#user-personas)
6. [Architecture Overview](#architecture-overview)
7. [Technical Constraints](#technical-constraints)
8. [Dependencies](#dependencies)
9. [Risk Assessment](#risk-assessment)
10. [Acceptance Criteria](#acceptance-criteria)
11. [Stories Overview](#stories-overview)
12. [Implementation Patterns](#implementation-patterns)
13. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
14. [Testing Strategy](#testing-strategy)
15. [Security Considerations](#security-considerations)
16. [Performance Requirements](#performance-requirements)
17. [Observability](#observability)
18. [Rollout Plan](#rollout-plan)
19. [References](#references)
20. [AI Implementation Guide](#ai-implementation-guide)

---

## Executive Summary

{{2-4 paragraph executive summary explaining what this epic delivers, why it matters, and the expected business impact}}

---

## Problem Statement

### Current State

{{Describe the current situation, pain points, and limitations}}

### Desired State

{{Describe what success looks like after this epic is complete}}

### Gap Analysis

| Current | Gap | Target |
|---------|-----|--------|
| {{current_1}} | {{gap_1}} | {{target_1}} |
| {{current_2}} | {{gap_2}} | {{target_2}} |

---

## Business Value

### Primary Value Drivers

1. **{{value_driver_1}}**: {{description}}
2. **{{value_driver_2}}**: {{description}}
3. **{{value_driver_3}}**: {{description}}

### ROI Analysis

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| {{metric_1}} | {{before}} | {{after}} | {{improvement}} |

### Stakeholder Benefits

| Stakeholder | Benefit |
|-------------|---------|
| {{stakeholder_1}} | {{benefit_1}} |
| {{stakeholder_2}} | {{benefit_2}} |

---

## Success Metrics

### Key Performance Indicators (KPIs)

| KPI | Baseline | Target | Measurement Method |
|-----|----------|--------|-------------------|
| {{kpi_1}} | {{baseline}} | {{target}} | {{method}} |
| {{kpi_2}} | {{baseline}} | {{target}} | {{method}} |

### Definition of Done (Epic Level)

- [ ] All stories completed and merged
- [ ] E2E tests passing at 100%
- [ ] Zero critical/high security vulnerabilities
- [ ] Performance SLAs met
- [ ] Documentation complete
- [ ] Stakeholder sign-off obtained

---

## User Personas

### {{persona_1_name}}

**Role:** {{role}}
**Goals:** {{goals}}
**Pain Points:** {{pain_points}}
**Key Scenarios:**
1. {{scenario_1}}
2. {{scenario_2}}

### {{persona_2_name}}

**Role:** {{role}}
**Goals:** {{goals}}
**Pain Points:** {{pain_points}}
**Key Scenarios:**
1. {{scenario_1}}
2. {{scenario_2}}

---

## Architecture Overview

### System Context

```
{{system_context_diagram_or_description}}
```

### Component Diagram

```
{{component_diagram_or_description}}
```

### Data Flow

```
{{data_flow_description}}
```

### Key Architectural Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| {{decision_1}} | {{rationale}} | {{alternatives}} |
| {{decision_2}} | {{rationale}} | {{alternatives}} |

### Relevant Architecture Documents

- [ARCHITECTURE_OVERVIEW.md](../../docs/ARCHITECTURE_OVERVIEW.md)
- [SECURITY_BOUNDARIES.md](../../docs/SECURITY_BOUNDARIES.md)
- {{additional_docs}}

---

## Technical Constraints

### Must Have

- {{constraint_1}}
- {{constraint_2}}
- {{constraint_3}}

### Should Have

- {{constraint_4}}
- {{constraint_5}}

### Won't Have (Out of Scope)

- {{out_of_scope_1}}
- {{out_of_scope_2}}

### Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| {{layer}} | {{tech}} | {{version}} | {{rationale}} |

---

## Dependencies

### Blocked By (Must Complete First)

| Dependency | Type | Status | Owner | ETA |
|------------|------|--------|-------|-----|
| {{dependency}} | {{type}} | {{status}} | {{owner}} | {{eta}} |

### Blocks (Waiting on This)

| Dependent | Type | Impact if Delayed |
|-----------|------|-------------------|
| {{dependent}} | {{type}} | {{impact}} |

### External Dependencies

| System/Service | Integration Type | Contact |
|----------------|------------------|---------|
| {{system}} | {{type}} | {{contact}} |

---

## Risk Assessment

### Risk Register

| Risk | Probability | Impact | Score | Mitigation | Owner |
|------|-------------|--------|-------|------------|-------|
| {{risk_1}} | {{prob}} | {{impact}} | {{score}} | {{mitigation}} | {{owner}} |
| {{risk_2}} | {{prob}} | {{impact}} | {{score}} | {{mitigation}} | {{owner}} |

### Contingency Plans

**If {{risk_scenario}}:**
{{contingency_plan}}

---

## Acceptance Criteria

### AC-1: {{ac_title}}

**Description:** {{description}}

```gherkin
GIVEN {{given}}
WHEN {{when}}
THEN {{then}}
AND {{and}}
```

**Verification:**
- Command: `{{verification_command}}`
- Expected: `{{expected_result}}`

### AC-2: {{ac_title}}

{{repeat for each AC}}

---

## Stories Overview

### Wave 1: {{wave_theme}} (Sprints {{sprint_range}})

| Story ID | Title | Points | Priority | Status |
|----------|-------|--------|----------|--------|
| {{story_id}} | {{title}} | {{points}} | {{priority}} | {{status}} |

**Wave 1 Goal:** {{wave_goal}}

### Wave 2: {{wave_theme}} (Sprints {{sprint_range}})

| Story ID | Title | Points | Priority | Status |
|----------|-------|--------|----------|--------|
| {{story_id}} | {{title}} | {{points}} | {{priority}} | {{status}} |

**Wave 2 Goal:** {{wave_goal}}

### Story Dependency Graph

```
{{story_dependency_visualization}}
```

---

## Implementation Patterns

### Pattern 1: {{pattern_name}}

**When to Use:** {{when}}

**Example:**
```{{language}}
{{code_example}}
```

**Anti-pattern:** {{what_not_to_do}}

### Pattern 2: {{pattern_name}}

{{repeat}}

### Code Style Guidelines

- {{guideline_1}}
- {{guideline_2}}
- {{guideline_3}}

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| {{type}} | {{convention}} | {{example}} |

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: {{name}}

**Problem:** {{description}}
**Why It's Wrong:** {{explanation}}
**Correct Approach:** {{correct}}

### Anti-Pattern 2: {{name}}

{{repeat}}

---

## Testing Strategy

### Test Pyramid

| Level | Coverage Target | Focus |
|-------|-----------------|-------|
| Unit | 80%+ | Business logic |
| Integration | Key paths | API contracts |
| E2E | Critical flows | User journeys |

### Unit Testing Requirements

- All public functions must have tests
- Coverage minimum: 80%
- Edge cases: empty, null, max values
- Error paths tested
- No skipped tests allowed

### Integration Testing Requirements

- API endpoints tested with real HTTP
- Database operations tested
- Cross-service calls verified
- Circuit breaker behavior validated

### E2E Testing Requirements (CRITICAL)

> **E2E tests MUST verify actual behavior, not UI feedback.**

- [ ] Happy path automated
- [ ] API responses verified (status + body)
- [ ] Data persistence verified (reload test)
- [ ] Console errors = 0
- [ ] Performance within SLA
- [ ] **NO SKIPPED TESTS**

### Test Data Strategy

{{describe test data approach}}

---

## Security Considerations

### Security Classification

**Data Classification:** {{classification}}
**Security Review Required:** {{yes/no}}

### Threat Model

| Threat | Mitigation | Verified |
|--------|------------|----------|
| {{threat_1}} | {{mitigation}} | [ ] |
| {{threat_2}} | {{mitigation}} | [ ] |

### Security Checklist

- [ ] No hardcoded secrets
- [ ] Input validation on all external inputs
- [ ] SQL/injection prevention
- [ ] Authentication required
- [ ] Authorization checks before data access
- [ ] Sensitive data not logged
- [ ] HTTPS/TLS enforced

---

## Performance Requirements

### SLAs

| Metric | Target | Measurement |
|--------|--------|-------------|
| P50 Latency | {{target}} | {{measurement}} |
| P99 Latency | {{target}} | {{measurement}} |
| Throughput | {{target}} | {{measurement}} |
| Error Rate | {{target}} | {{measurement}} |

### Load Testing

- Tool: {{tool}}
- Scenarios: {{scenarios}}
- Acceptance: {{criteria}}

### Performance Optimization Patterns

{{describe optimization approaches}}

---

## Observability

### Logging

| Event | Log Level | Fields |
|-------|-----------|--------|
| {{event}} | {{level}} | {{fields}} |

### Metrics

| Metric | Type | Labels | Alert Threshold |
|--------|------|--------|-----------------|
| {{metric}} | {{type}} | {{labels}} | {{threshold}} |

### Tracing

- Span naming: `{{convention}}`
- Required tags: {{tags}}
- SigNoz dashboard: {{link}}

### Alerting Rules

| Alert | Condition | Severity | Runbook |
|-------|-----------|----------|---------|
| {{alert}} | {{condition}} | {{severity}} | {{runbook}} |

---

## Rollout Plan

### Feature Flags

| Flag | Purpose | Default |
|------|---------|---------|
| {{flag}} | {{purpose}} | {{default}} |

### Rollout Phases

1. **Phase 1 (Dev):** {{description}}
2. **Phase 2 (Staging):** {{description}}
3. **Phase 3 (Production Canary):** {{description}}
4. **Phase 4 (Production GA):** {{description}}

### Rollback Plan

**Trigger:** {{rollback_trigger}}
**Steps:**
1. {{step_1}}
2. {{step_2}}

---

## References

### Internal Documentation

- [PRD]({{link}})
- [Architecture]({{link}})
- [API Contracts]({{link}})
- [UX Designs]({{link}})

### External Documentation

- {{external_ref_1}}
- {{external_ref_2}}

### Related Epics

| Epic ID | Relationship |
|---------|--------------|
| {{epic_id}} | {{relationship}} |

---

## AI Implementation Guide

> **This section provides context for AI agents implementing stories in this epic.**

### Codebase Orientation

**Primary Repositories:**
- `{{repo_1}}`: {{purpose}}
- `{{repo_2}}`: {{purpose}}

**Key Files to Understand:**
- `{{file_1}}`: {{what_it_does}}
- `{{file_2}}`: {{what_it_does}}

### Implementation Order

1. {{story_id}} - {{reason_for_order}}
2. {{story_id}} - {{reason_for_order}}

### Common Gotchas

1. **{{gotcha_1}}**: {{explanation_and_solution}}
2. **{{gotcha_2}}**: {{explanation_and_solution}}

### Verification Commands

```bash
# Build
{{build_command}}

# Test
{{test_command}}

# Lint
{{lint_command}}
```

### Success Criteria for AI Implementation

- [ ] All acceptance criteria pass
- [ ] Code review by code-reviewer agent passes
- [ ] Security review by security-reviewer agent passes (if applicable)
- [ ] E2E tests pass at 100%
- [ ] No console errors
- [ ] Performance SLAs met

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| {{date}} | {{change}} | {{author}} |

---

*Last updated: {{timestamp}}*
*Confluence sync: {{confluence_link}}*
