# Comprehensive Story Template with Party-Mode AI Prompts

> **Template Version:** 1.0.0
> **Last Updated:** 2026-01-02
> **Purpose:** Master template for generating JIRA stories with robust AI implementation prompts

---

## How to Use This Template

1. Copy this template for each new story
2. Replace all `{{PLACEHOLDER}}` values with story-specific content
3. Customize AI prompts based on story type (infrastructure, backend, frontend, integration)
4. Review and adjust scope boundaries
5. Ensure all functional requirements have specific AI prompts

---

# {{STORY_ID}}: {{STORY_TITLE}}

## Story Metadata

```yaml
story:
  id: {{STORY_ID}}
  title: "{{STORY_TITLE}}"
  type: {{STORY_TYPE}}  # engineering | infrastructure | frontend | integration | testing
  status: {{STATUS}}    # ready | in-progress | review | done

metadata:
  parent: {{EPIC_JIRA_KEY}}
  priority: {{PRIORITY}}  # P0 | P1 | P2
  points: {{POINTS}}
  sprint: {{SPRINT}}
  wave: {{WAVE}}
  labels:
    - {{EPIC_PREFIX_LOWERCASE}}
    - wave{{WAVE}}
    - sprint{{SPRINT}}
    - {{PRIORITY_LOWERCASE}}
    - {{MVP_LABEL}}
  owner: TBD
  reviewers:
    - TBD
```

---

## Problem Statement

{{PROBLEM_STATEMENT}}

### AI Implementation Prompt - Problem Analysis

```
You are implementing {{STORY_ID}}: {{STORY_TITLE}} for Armor Argus.

PLATFORM CONTEXT (memorize this):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Armor Argus is an autonomous cloud security platform that:
- Replaces visibility-only tools by safely FIXING highest-impact risks
- Uses NebulaGraph for attack path analysis (graph queries)
- Uses ClickHouse for findings, risk scores, events, and audit evidence (analytics)
- Uses Cedar policy language for deterministic policy enforcement
- Requires SigNoz/OpenTelemetry for all observability

ARCHITECTURE CONTEXT:
┌─────────────────────────────────────────────────────────────────────────────┐
│ {{ARCHITECTURE_DIAGRAM_ASCII}}                                               │
└─────────────────────────────────────────────────────────────────────────────┘

WHY THIS STORY MATTERS:
1. {{WHY_MATTERS_1}}
2. {{WHY_MATTERS_2}}
3. {{WHY_MATTERS_3}}
4. BLOCKS: {{BLOCKING_STORIES}}

BEFORE PROCEEDING, VERIFY YOU UNDERSTAND:
□ {{UNDERSTANDING_CHECK_1}}
□ {{UNDERSTANDING_CHECK_2}}
□ {{UNDERSTANDING_CHECK_3}}
□ {{UNDERSTANDING_CHECK_4}}

If ANY of the above is unclear, STOP and research before coding.
```

---

## Goal

{{GOAL_STATEMENT}}

### AI Implementation Prompt - Goal Verification

```
SUCCESS CRITERIA for {{STORY_ID}} (ALL must be TRUE):

FUNCTIONAL SUCCESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{FUNCTIONAL_SUCCESS_CRITERIA}}

INTEGRATION SUCCESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{INTEGRATION_SUCCESS_CRITERIA}}

QUALITY SUCCESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{QUALITY_SUCCESS_CRITERIA}}

ONE-SENTENCE SUCCESS DEFINITION:
"{{ONE_SENTENCE_SUCCESS}}"

EVIDENCE REQUIRED FOR PR:
1. {{EVIDENCE_1}}
2. {{EVIDENCE_2}}
3. {{EVIDENCE_3}}
4. {{EVIDENCE_4}}
```

---

## Scope

### In Scope
{{IN_SCOPE_LIST}}

### Out of Scope
{{OUT_OF_SCOPE_LIST}}

### AI Implementation Prompt - Scope Enforcement

```
SCOPE BOUNDARIES FOR {{STORY_ID}} (STRICTLY ENFORCED):

✅ YOU MUST IMPLEMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{MUST_IMPLEMENT_LIST}}

❌ YOU MUST NOT IMPLEMENT (future stories):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{MUST_NOT_IMPLEMENT_LIST}}

⚠️ SCOPE CREEP DETECTION:
If you find yourself:
{{SCOPE_CREEP_WARNINGS}}

SCOPE VERIFICATION:
Expected files created/modified:
{{EXPECTED_FILES_TREE}}

If creating files outside this structure: VERIFY SCOPE
```

---

## Functional Requirements

{{FOR_EACH_FUNCTIONAL_REQUIREMENT}}

### FR-{{FR_NUMBER}}: {{FR_NAME}}

**Acceptance Criteria:**
{{FR_ACCEPTANCE_CRITERIA}}

### AI Implementation Prompt - FR-{{FR_NUMBER}}

```
IMPLEMENT FR-{{FR_NUMBER}}: {{FR_NAME}}

TARGET FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{TARGET_FILES}}

SPECIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{SPECIFICATION_DETAILS}}

IMPLEMENTATION:
──────────────────────────────────────
{{IMPLEMENTATION_CODE}}

VERIFICATION:
──────────────────────────────────────
{{VERIFICATION_COMMANDS}}

ACCEPTANCE CRITERIA:
{{FR_AC_CHECKLIST}}
```

{{END_FOR_EACH}}

---

## Non-Functional Requirements

### Performance
| Metric | Target |
|--------|--------|
{{PERFORMANCE_TABLE}}

### Quality
{{QUALITY_CHECKLIST}}

### Logging
{{LOGGING_REQUIREMENTS}}

---

## Testing Requirements

### AI Implementation Prompt - Testing Strategy

```
TEST STRATEGY FOR {{STORY_ID}}

RISK ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Impact if broken: {{IMPACT_LEVEL}} ({{IMPACT_REASON}})
User-facing: {{USER_FACING}}
Data mutation: {{DATA_MUTATION}}
External calls: {{EXTERNAL_CALLS}}

REQUIRED TESTS:

TIER 1 - UNIT TESTS (mandatory):
──────────────────────────────────────
{{UNIT_TEST_CODE}}

TIER 2 - INTEGRATION TESTS ({{INTEGRATION_MANDATORY}}):
──────────────────────────────────────
{{INTEGRATION_TEST_CODE}}

TIER 3 - E2E TESTS ({{E2E_MANDATORY}}):
──────────────────────────────────────
{{E2E_TEST_CODE}}

RUN ALL TESTS:
──────────────────────────────────────
{{TEST_RUN_COMMANDS}}

EXPECTED OUTPUT:
{{EXPECTED_TEST_OUTPUT}}

FORBIDDEN:
- #[ignore] annotations
- .skip() in tests
- Tests without assertions
- Flaky tests
```

---

## Done Checklist

### AI Implementation Prompt - Completion Verification

```
DONE CHECKLIST FOR {{STORY_ID}}
Execute each check. ALL must pass.

ENGINEERING CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{ENGINEERING_CHECKLIST}}

QUALITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{QUALITY_CHECKLIST}}

OBSERVABILITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{OBSERVABILITY_CHECKLIST}}

OPERATIONAL CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{OPERATIONAL_CHECKLIST}}

FINAL VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ All acceptance criteria met
□ PR includes all evidence screenshots/outputs
□ No TODOs without issue links
```

---

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA_LIST}}

---

## Deployment Notes

### Target Environment
{{DEPLOYMENT_ENVIRONMENT}}

### Dependencies
{{DEPENDENCIES}}

### Deployment Commands
```bash
{{DEPLOYMENT_COMMANDS}}
```

---

## Rollback Strategy

### AI Implementation Prompt - Rollback

```
ROLLBACK STRATEGY FOR {{STORY_ID}}

RISK ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Database changes: {{DATABASE_CHANGES}}
- Schema migrations: {{SCHEMA_MIGRATIONS}}
- State introduced: {{STATE_INTRODUCED}}
- Dependencies created: {{DEPENDENCIES_CREATED}}

ROLLBACK IMPACT: {{ROLLBACK_IMPACT_LEVEL}}
{{ROLLBACK_IMPACT_DESCRIPTION}}

ROLLBACK COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{ROLLBACK_COMMANDS}}

VERIFICATION AFTER ROLLBACK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{ROLLBACK_VERIFICATION}}
```

---

## Implementation Guide - Master AI Prompt

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    {{STORY_ID}}: {{STORY_TITLE}}                              ║
║                         COMPLETE IMPLEMENTATION GUIDE                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

MISSION BRIEFING:
{{MISSION_BRIEFING}}

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: {{PHASE_1_NAME}} ({{PHASE_1_TIME}})
═══════════════════════════════════════════════════════════════════════════════

{{PHASE_1_STEPS}}

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: {{PHASE_2_NAME}} ({{PHASE_2_TIME}})
═══════════════════════════════════════════════════════════════════════════════

{{PHASE_2_STEPS}}

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: {{PHASE_3_NAME}} ({{PHASE_3_TIME}})
═══════════════════════════════════════════════════════════════════════════════

{{PHASE_3_STEPS}}

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: {{PHASE_4_NAME}} ({{PHASE_4_TIME}})
═══════════════════════════════════════════════════════════════════════════════

{{PHASE_4_STEPS}}

═══════════════════════════════════════════════════════════════════════════════
PHASE 5: {{PHASE_5_NAME}} ({{PHASE_5_TIME}})
═══════════════════════════════════════════════════════════════════════════════

{{PHASE_5_STEPS}}

═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA CHECKLIST (all must be TRUE):
═══════════════════════════════════════════════════════════════════════════════

{{SUCCESS_CHECKLIST}}

ESTIMATED TIME: {{ESTIMATED_TIME}}
MAXIMUM TIME: {{MAXIMUM_TIME}} - if exceeding, ask for help

═══════════════════════════════════════════════════════════════════════════════
REFERENCE IMPLEMENTATIONS:
═══════════════════════════════════════════════════════════════════════════════

{{REFERENCE_IMPLEMENTATIONS}}

╔══════════════════════════════════════════════════════════════════════════════╗
║                              END OF GUIDE                                     ║
║           If anything is unclear, STOP and ask before proceeding.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## References

{{REFERENCES_LIST}}

---

# Template Variables Reference

## Required Variables (must be filled for every story)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{STORY_ID}}` | Story identifier | PLAT-001, AUTO-100 |
| `{{STORY_TITLE}}` | Short descriptive title | ClickHouse Helm Chart Deployment |
| `{{STORY_TYPE}}` | Category | engineering, infrastructure, frontend |
| `{{EPIC_JIRA_KEY}}` | Parent epic JIRA key | ARGUS-1, ARGUS-5 |
| `{{PRIORITY}}` | P0, P1, or P2 | P0 |
| `{{POINTS}}` | Story points | 2, 3, 5 |
| `{{SPRINT}}` | Sprint number | 1, 11 |
| `{{WAVE}}` | Wave number | 1, 6 |
| `{{PROBLEM_STATEMENT}}` | Why this story matters | 1-2 paragraphs |
| `{{GOAL_STATEMENT}}` | What success looks like | 1 paragraph |

## Story Type Specific Templates

### Infrastructure Stories
- Focus on Helm charts, K8s resources, databases
- AI prompts include kubectl commands
- Verification via kubectl get/describe

### Backend/Engineering Stories
- Focus on Rust code, APIs, services
- AI prompts include cargo commands, exact code
- Verification via cargo test, curl

### Frontend Stories
- Focus on React components, UI state
- AI prompts include npm commands, component code
- Verification via npm test, screenshots

### Integration Stories
- Focus on connecting services
- AI prompts include multi-service testing
- Verification via E2E tests

---

# Generation Instructions for AI

When generating a story from this template:

1. **Read the source epic file** to extract story details
2. **Read the PRD** for platform context
3. **Identify story type** to customize prompts
4. **Generate problem statement** explaining WHY this matters
5. **Define measurable goals** with verification commands
6. **Set hard scope boundaries** with creep detection
7. **Create detailed FR prompts** with exact code when possible
8. **Design risk-based tests** appropriate to story impact
9. **Build phased implementation guide** with time estimates
10. **Include rollback strategy** based on state changes

**Quality Bar:** Every AI prompt should enable a developer to implement
the story correctly on the FIRST PASS without needing clarification.
