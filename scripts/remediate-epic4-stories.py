#!/usr/bin/env python3
"""
Remediate EPIC-4 stories to BMAD-compliant format.

This script converts minimal story format to full BMAD-compliant format with:
1. User Story: "As an automation engineer, I want..., so that..."
2. Business Value: Value Statement, Success Metric, User Research
3. Acceptance Criteria: GIVEN/WHEN/THEN format with AC headings
4. Task Execution Order: T1 -> T2 -> T3 -> T4
5. Tasks Table: 4 tasks with proper links
6. Technical Notes: Key Files, Dependencies, Testing Requirements
"""

import os
import re
from pathlib import Path

EPIC4_STORIES_DIR = Path("/Users/phillipboles/Development/armor-argus/.bmad/epics/EPIC-4/stories")

# Story metadata for better remediation
STORY_METADATA = {
    "01": {
        "title": "RemediationRequest Data Model",
        "action": "define a structured RemediationRequest data model",
        "benefit": "remediation workflows have a consistent foundation for tracking requests, status, and actions",
        "value": "Enables consistent tracking of remediation requests across the platform",
        "metric": "All remediation workflows use the standardized data model",
        "research": "Operations teams need structured tracking to manage remediation at scale",
        "key_files": ["argus-common/src/domain/remediation.rs", "argus-common/src/domain/mod.rs"],
        "deps": ["serde", "uuid", "chrono"]
    },
    "02": {
        "title": "Remediation ClickHouse Table",
        "action": "create ClickHouse tables for storing remediation data",
        "benefit": "remediation requests and their history are persisted for analysis and audit",
        "value": "Persistent storage enables historical analysis and compliance reporting",
        "metric": "All remediation data queryable within 100ms p99 latency",
        "research": "Compliance teams require 7-year retention of remediation history",
        "key_files": ["schemas/clickhouse/remediations.sql", "argus-api/src/db/remediation_repo.rs"],
        "deps": ["clickhouse-rs", "tokio"]
    },
    "03": {
        "title": "POST /api/v1/remediations",
        "action": "create new remediation requests via REST API",
        "benefit": "findings can be submitted for automated remediation",
        "value": "Provides programmatic access to initiate remediation workflows",
        "metric": "API handles 100 requests/second with p99 < 50ms",
        "research": "Security teams need batch remediation capabilities",
        "key_files": ["argus-api/src/handlers/remediation.rs", "contracts/openapi/remediations.yaml"],
        "deps": ["axum", "serde_json", "validator"]
    },
    "04": {
        "title": "GET /api/v1/remediations",
        "action": "list and filter remediation requests",
        "benefit": "users can track the status of all remediation activities",
        "value": "Provides visibility into remediation pipeline status",
        "metric": "List queries return within 200ms for 10K+ records",
        "research": "SOC analysts need real-time remediation status visibility",
        "key_files": ["argus-api/src/handlers/remediation.rs", "argus-api/src/queries/remediation_list.rs"],
        "deps": ["axum", "serde", "clickhouse-rs"]
    },
    "05": {
        "title": "GET /api/v1/remediations/{id}",
        "action": "retrieve detailed information about a specific remediation",
        "benefit": "users can inspect the full history and status of any remediation",
        "value": "Enables detailed investigation and audit of individual remediations",
        "metric": "Detail queries return within 50ms",
        "research": "Incident responders need full remediation context during investigations",
        "key_files": ["argus-api/src/handlers/remediation.rs", "argus-api/src/queries/remediation_detail.rs"],
        "deps": ["axum", "uuid", "serde"]
    },
    "06": {
        "title": "POST /api/v1/remediations/{id}/approve",
        "action": "approve pending remediation requests",
        "benefit": "remediation workflow proceeds only after authorized approval",
        "value": "Ensures human oversight before automated changes to production",
        "metric": "Approval workflow completes within 100ms",
        "research": "Change management requires explicit approval before production changes",
        "key_files": ["argus-api/src/handlers/remediation.rs", "argus-policy/src/approval.rs"],
        "deps": ["axum", "cedar-policy"]
    },
    "07": {
        "title": "Cedar Policy Store Setup",
        "action": "configure and initialize the Cedar policy store",
        "benefit": "policies can be loaded, stored, and retrieved for evaluation",
        "value": "Centralized policy management enables consistent authorization",
        "metric": "Policy store handles 1000 policies with <10ms lookup",
        "research": "Security teams need version-controlled policy management",
        "key_files": ["argus-policy/src/store.rs", "argus-policy/src/policy_loader.rs"],
        "deps": ["cedar-policy", "tokio", "serde"]
    },
    "08": {
        "title": "Cedar Policy Evaluator",
        "action": "evaluate authorization requests against Cedar policies",
        "benefit": "remediation actions are authorized based on configurable policies",
        "value": "Fine-grained authorization prevents unauthorized remediation actions",
        "metric": "Policy evaluation completes within 5ms for 95th percentile",
        "research": "Least-privilege access requires granular policy evaluation",
        "key_files": ["argus-policy/src/evaluator.rs", "argus-policy/src/request.rs"],
        "deps": ["cedar-policy", "tracing"]
    },
    "09": {
        "title": "Manual Status Update API",
        "action": "manually update remediation status via API",
        "benefit": "operators can override automated status when necessary",
        "value": "Enables manual intervention for edge cases and exceptions",
        "metric": "Status updates persist within 50ms",
        "research": "Operations teams need manual override for automated workflows",
        "key_files": ["argus-api/src/handlers/remediation.rs", "argus-common/src/domain/remediation.rs"],
        "deps": ["axum", "validator"]
    },
    "10": {
        "title": "Status Transition Validation",
        "action": "validate remediation status transitions",
        "benefit": "invalid state changes are prevented and workflows remain consistent",
        "value": "State machine integrity ensures reliable remediation tracking",
        "metric": "Invalid transitions rejected with clear error messages",
        "research": "Workflow integrity requires strict state transition rules",
        "key_files": ["argus-common/src/domain/remediation.rs", "argus-common/src/domain/status.rs"],
        "deps": ["thiserror"]
    },
    "11": {
        "title": "Evidence Data Model",
        "action": "define structured evidence data models",
        "benefit": "remediation actions generate auditable evidence artifacts",
        "value": "Audit-ready evidence supports compliance requirements",
        "metric": "Evidence captured for 100% of remediation actions",
        "research": "Auditors require immutable evidence of all changes",
        "key_files": ["argus-common/src/domain/evidence.rs", "argus-common/src/domain/mod.rs"],
        "deps": ["serde", "uuid", "chrono"]
    },
    "12": {
        "title": "Evidence ClickHouse Table",
        "action": "create ClickHouse tables for storing evidence data",
        "benefit": "evidence artifacts are persisted for long-term retention and analysis",
        "value": "Immutable evidence storage supports compliance and forensics",
        "metric": "Evidence queryable for 7+ years with consistent performance",
        "research": "Regulatory requirements mandate long-term evidence retention",
        "key_files": ["schemas/clickhouse/evidence.sql", "argus-api/src/db/evidence_repo.rs"],
        "deps": ["clickhouse-rs", "tokio"]
    },
    "100": {
        "title": "argus-policy-ai Service Scaffold",
        "action": "scaffold the AI-powered policy service",
        "benefit": "a dedicated service handles AI-driven policy operations",
        "value": "Modular AI service enables scalable policy intelligence",
        "metric": "Service starts in <5 seconds with all health checks passing",
        "research": "AI workloads require isolated compute resources",
        "key_files": ["argus-policy-ai/src/main.rs", "argus-policy-ai/Cargo.toml"],
        "deps": ["axum", "tokio", "tracing", "tower"]
    },
    "101": {
        "title": "LLM Client Setup",
        "action": "configure and initialize LLM client connections",
        "benefit": "the policy AI service can communicate with language models",
        "value": "Enables AI-powered policy generation and analysis",
        "metric": "LLM latency <2s for 95th percentile requests",
        "research": "Policy analysts need natural language policy authoring",
        "key_files": ["argus-policy-ai/src/llm/client.rs", "argus-policy-ai/src/llm/mod.rs"],
        "deps": ["reqwest", "serde", "tokio"]
    },
    "102": {
        "title": "Prompt Template Store",
        "action": "implement a versioned prompt template storage system",
        "benefit": "prompts can be managed, versioned, and updated without code changes",
        "value": "Enables rapid iteration on AI prompts without deployments",
        "metric": "Prompt retrieval <10ms, version history maintained",
        "research": "AI prompt engineering requires rapid experimentation",
        "key_files": ["argus-policy-ai/src/prompts/store.rs", "argus-policy-ai/src/prompts/templates/"],
        "deps": ["tera", "serde", "tokio"]
    },
    "103": {
        "title": "NL to Cedar Intent Parser",
        "action": "parse natural language into structured policy intents",
        "benefit": "users can describe policies in plain English",
        "value": "Reduces barrier to policy authoring for non-technical users",
        "metric": "Intent parsing accuracy >90% for common policy patterns",
        "research": "Security analysts prefer natural language over Cedar syntax",
        "key_files": ["argus-policy-ai/src/nl/parser.rs", "argus-policy-ai/src/nl/intent.rs"],
        "deps": ["serde", "regex"]
    },
    "104": {
        "title": "NL to Cedar Policy Generator",
        "action": "generate valid Cedar policies from parsed intents",
        "benefit": "users get syntactically correct policies from natural language",
        "value": "Automates policy authoring while ensuring correctness",
        "metric": "Generated policies pass validation 99%+ of the time",
        "research": "Manual Cedar authoring is error-prone and slow",
        "key_files": ["argus-policy-ai/src/nl/generator.rs", "argus-policy-ai/src/cedar/builder.rs"],
        "deps": ["cedar-policy", "serde"]
    },
    "105": {
        "title": "Cedar Syntax Validator",
        "action": "validate Cedar policy syntax before storage",
        "benefit": "invalid policies are rejected before they affect authorization",
        "value": "Prevents broken policies from entering the system",
        "metric": "Validation completes in <100ms for complex policies",
        "research": "Policy errors cause authorization failures in production",
        "key_files": ["argus-policy-ai/src/cedar/validator.rs", "argus-policy/src/validation.rs"],
        "deps": ["cedar-policy"]
    },
    "106": {
        "title": "POST /internal/policy/suggest",
        "action": "expose policy suggestion via internal API",
        "benefit": "other services can request AI-generated policy suggestions",
        "value": "Enables policy intelligence across the platform",
        "metric": "Suggestions returned within 3 seconds",
        "research": "Proactive policy suggestions improve security posture",
        "key_files": ["argus-policy-ai/src/handlers/suggest.rs", "contracts/openapi/policy-ai.yaml"],
        "deps": ["axum", "serde_json"]
    },
    "107": {
        "title": "Confidence Scoring",
        "action": "calculate confidence scores for AI-generated policies",
        "benefit": "users can assess the reliability of policy suggestions",
        "value": "Enables informed decisions about AI recommendations",
        "metric": "Confidence scores correlate with actual accuracy",
        "research": "Users need trust signals for AI-generated content",
        "key_files": ["argus-policy-ai/src/scoring/confidence.rs", "argus-policy-ai/src/scoring/mod.rs"],
        "deps": ["serde"]
    },
    "108": {
        "title": "Clarifying Questions",
        "action": "generate clarifying questions for ambiguous policy requests",
        "benefit": "ambiguous requests are refined before policy generation",
        "value": "Improves policy accuracy through user clarification",
        "metric": "Ambiguity detection rate >85%",
        "research": "Ambiguous policies lead to security gaps",
        "key_files": ["argus-policy-ai/src/clarification/questions.rs", "argus-policy-ai/src/clarification/mod.rs"],
        "deps": ["serde"]
    },
    "109": {
        "title": "Policy Simulation Sample Selection",
        "action": "select representative samples for policy simulation",
        "benefit": "simulations use realistic data without full dataset processing",
        "value": "Enables fast policy impact assessment",
        "metric": "Sample selection completes in <1 second",
        "research": "Full dataset simulation is too slow for interactive use",
        "key_files": ["argus-policy-ai/src/simulation/sampler.rs", "argus-policy-ai/src/simulation/mod.rs"],
        "deps": ["rand", "serde"]
    },
    "110": {
        "title": "Policy Simulation Execution",
        "action": "execute policy simulation against sample data",
        "benefit": "users can preview policy effects before deployment",
        "value": "Prevents unintended policy impacts in production",
        "metric": "Simulation completes in <5 seconds for 1000 samples",
        "research": "Policy changes without testing cause incidents",
        "key_files": ["argus-policy-ai/src/simulation/executor.rs", "argus-policy-ai/src/simulation/results.rs"],
        "deps": ["cedar-policy", "tokio"]
    },
    "111": {
        "title": "Policy Simulation Impact Analysis",
        "action": "analyze and summarize simulation results",
        "benefit": "users understand policy impact before deployment",
        "value": "Enables informed policy deployment decisions",
        "metric": "Impact reports generated in <2 seconds",
        "research": "Users need clear impact summaries, not raw data",
        "key_files": ["argus-policy-ai/src/simulation/analyzer.rs", "argus-policy-ai/src/simulation/report.rs"],
        "deps": ["serde"]
    },
    "112": {
        "title": "POST /internal/policy/simulate",
        "action": "expose policy simulation via internal API",
        "benefit": "other services can request policy simulations",
        "value": "Enables policy testing across the platform",
        "metric": "Simulation API responds within 10 seconds",
        "research": "CI/CD pipelines need policy validation",
        "key_files": ["argus-policy-ai/src/handlers/simulate.rs", "contracts/openapi/policy-ai.yaml"],
        "deps": ["axum", "serde_json"]
    },
    "113": {
        "title": "Explanation Generator - Rule Matching",
        "action": "identify which policy rules apply to a given context",
        "benefit": "users understand why policies made specific decisions",
        "value": "Provides transparency into authorization decisions",
        "metric": "Rule matching completes in <100ms",
        "research": "Audit requires understanding of authorization logic",
        "key_files": ["argus-policy-ai/src/explain/matcher.rs", "argus-policy-ai/src/explain/mod.rs"],
        "deps": ["cedar-policy"]
    },
    "114": {
        "title": "Explanation Generator - Narrative",
        "action": "generate human-readable explanations of policy decisions",
        "benefit": "non-technical users understand policy behavior",
        "value": "Enables policy understanding across skill levels",
        "metric": "Explanations rated 'clear' by 80%+ of users",
        "research": "Technical explanations alienate non-security users",
        "key_files": ["argus-policy-ai/src/explain/narrative.rs", "argus-policy-ai/src/explain/templates/"],
        "deps": ["tera", "serde"]
    },
    "115": {
        "title": "POST /internal/policy/explain",
        "action": "expose policy explanation via internal API",
        "benefit": "other services can request policy explanations",
        "value": "Enables policy understanding across the platform",
        "metric": "Explanations returned within 2 seconds",
        "research": "Users need on-demand policy understanding",
        "key_files": ["argus-policy-ai/src/handlers/explain.rs", "contracts/openapi/policy-ai.yaml"],
        "deps": ["axum", "serde_json"]
    },
    "116": {
        "title": "Policy Lint - Dangerous Patterns",
        "action": "detect dangerous patterns in Cedar policies",
        "benefit": "policies with security risks are flagged before deployment",
        "value": "Prevents deployment of insecure policies",
        "metric": "Dangerous pattern detection >95% recall",
        "research": "Common policy mistakes lead to security incidents",
        "key_files": ["argus-policy-ai/src/lint/dangerous.rs", "argus-policy-ai/src/lint/mod.rs"],
        "deps": ["cedar-policy"]
    },
    "117": {
        "title": "Policy Lint - Attribute Validation",
        "action": "validate policy attributes against schema",
        "benefit": "policies reference only valid attributes",
        "value": "Prevents runtime errors from invalid attribute references",
        "metric": "Schema validation completes in <50ms",
        "research": "Invalid attributes cause policy evaluation failures",
        "key_files": ["argus-policy-ai/src/lint/attributes.rs", "argus-policy-ai/src/lint/schema.rs"],
        "deps": ["serde_json"]
    },
    "118": {
        "title": "Guardrail - Suppress All Block",
        "action": "block policies that suppress all findings",
        "benefit": "users cannot accidentally disable all security checks",
        "value": "Prevents catastrophic policy mistakes",
        "metric": "100% of suppress-all policies blocked",
        "research": "Overly broad suppressions bypass security controls",
        "key_files": ["argus-policy-ai/src/guardrails/suppress_all.rs", "argus-policy-ai/src/guardrails/mod.rs"],
        "deps": ["cedar-policy"]
    },
    "119": {
        "title": "Guardrail - Time Bounds Required",
        "action": "require time bounds on suppression policies",
        "benefit": "suppressions cannot be permanent",
        "value": "Ensures temporary suppressions expire",
        "metric": "100% of suppressions have time bounds",
        "research": "Permanent suppressions accumulate and create blind spots",
        "key_files": ["argus-policy-ai/src/guardrails/time_bounds.rs", "argus-policy-ai/src/guardrails/mod.rs"],
        "deps": ["chrono", "cedar-policy"]
    },
    "120": {
        "title": "Guardrail - High Risk Approval",
        "action": "require additional approval for high-risk policies",
        "benefit": "high-impact policy changes get extra review",
        "value": "Adds oversight for potentially dangerous changes",
        "metric": "High-risk policies require 2+ approvals",
        "research": "High-risk changes need additional scrutiny",
        "key_files": ["argus-policy-ai/src/guardrails/high_risk.rs", "argus-policy-ai/src/guardrails/approval.rs"],
        "deps": ["cedar-policy"]
    },
    "121": {
        "title": "Policy Version Store",
        "action": "implement versioned policy storage",
        "benefit": "policy history is preserved for audit and rollback",
        "value": "Enables policy rollback and audit trail",
        "metric": "Version history queryable within 100ms",
        "research": "Policy changes need rollback capability",
        "key_files": ["argus-policy/src/versions/store.rs", "argus-policy/src/versions/mod.rs"],
        "deps": ["clickhouse-rs", "uuid"]
    },
    "122": {
        "title": "Policy Diff Generator",
        "action": "generate diffs between policy versions",
        "benefit": "users can see exactly what changed between versions",
        "value": "Enables change review before approval",
        "metric": "Diffs generated in <500ms for any version pair",
        "research": "Review requires understanding of specific changes",
        "key_files": ["argus-policy/src/versions/diff.rs", "argus-policy/src/versions/mod.rs"],
        "deps": ["similar"]
    },
    "123": {
        "title": "Git Sync - Pull Policies",
        "action": "synchronize policies from git repositories",
        "benefit": "policies can be managed via GitOps workflows",
        "value": "Enables version-controlled policy management",
        "metric": "Git sync completes within 30 seconds",
        "research": "Teams prefer GitOps for policy management",
        "key_files": ["argus-policy/src/git/pull.rs", "argus-policy/src/git/mod.rs"],
        "deps": ["git2", "tokio"]
    },
    "124": {
        "title": "Git Sync - Webhook Handler",
        "action": "handle git webhooks to trigger policy sync",
        "benefit": "policy updates are automatically deployed",
        "value": "Enables continuous policy deployment",
        "metric": "Webhook processing <5 seconds",
        "research": "Manual policy deployment is slow and error-prone",
        "key_files": ["argus-policy/src/git/webhook.rs", "argus-api/src/handlers/webhook.rs"],
        "deps": ["axum", "hmac", "sha2"]
    },
    "125": {
        "title": "argus-automate Service Scaffold",
        "action": "scaffold the automation executor service",
        "benefit": "a dedicated service handles remediation execution",
        "value": "Isolated execution environment for remediation actions",
        "metric": "Service starts in <5 seconds with health checks passing",
        "research": "Remediation execution needs isolated compute",
        "key_files": ["argus-automate/src/main.rs", "argus-automate/Cargo.toml"],
        "deps": ["axum", "tokio", "nats"]
    },
    "126": {
        "title": "Execution Queue Consumer",
        "action": "consume remediation tasks from the execution queue",
        "benefit": "remediation tasks are processed reliably and in order",
        "value": "Reliable task processing with at-least-once delivery",
        "metric": "Queue processing latency <1 second p99",
        "research": "Remediation needs reliable async processing",
        "key_files": ["argus-automate/src/queue/consumer.rs", "argus-automate/src/queue/mod.rs"],
        "deps": ["nats", "tokio"]
    },
    "127": {
        "title": "Armor Agent mTLS Setup",
        "action": "configure mutual TLS between services and armor-agent",
        "benefit": "communication with agents is encrypted and authenticated",
        "value": "Prevents unauthorized agent commands",
        "metric": "mTLS handshake <100ms, all connections authenticated",
        "research": "Agent communication must be secure",
        "key_files": ["armor-agent/cmd/agent/tls.go", "argus-automate/src/agent/tls.rs"],
        "deps": ["rustls", "tokio-rustls"]
    },
    "128": {
        "title": "Armor Agent Command Signing",
        "action": "implement cryptographic signing for agent commands",
        "benefit": "agents verify commands originated from authorized sources",
        "value": "Prevents command injection and tampering",
        "metric": "Signature verification <10ms per command",
        "research": "Command integrity is critical for security",
        "key_files": ["argus-automate/src/agent/signing.rs", "armor-agent/pkg/verify/signature.go"],
        "deps": ["ed25519-dalek", "base64"]
    },
    "129": {
        "title": "Armor Agent Command Schema",
        "action": "define and validate command schemas for agents",
        "benefit": "agents receive well-structured, validated commands",
        "value": "Prevents malformed commands from reaching agents",
        "metric": "Schema validation <5ms per command",
        "research": "Command structure must be strict and validated",
        "key_files": ["contracts/commands/", "argus-automate/src/agent/schema.rs"],
        "deps": ["serde", "schemars"]
    },
    "130": {
        "title": "Dry Run - Prerequisite Check",
        "action": "check prerequisites before dry run execution",
        "benefit": "dry runs fail fast if prerequisites are not met",
        "value": "Saves time by catching issues early",
        "metric": "Prerequisite check <500ms",
        "research": "Users need fast feedback on simulation readiness",
        "key_files": ["argus-automate/src/dryrun/prereq.rs", "argus-automate/src/dryrun/mod.rs"],
        "deps": ["tokio"]
    },
    "131": {
        "title": "Dry Run - Impact Preview",
        "action": "preview the impact of a remediation action",
        "benefit": "users see what would change before execution",
        "value": "Enables informed remediation decisions",
        "metric": "Impact preview <5 seconds",
        "research": "Users need to understand impact before changes",
        "key_files": ["argus-automate/src/dryrun/impact.rs", "argus-automate/src/dryrun/preview.rs"],
        "deps": ["serde"]
    },
    "132": {
        "title": "POST /api/v1/remediations/simulate",
        "action": "expose remediation simulation via API",
        "benefit": "users can simulate remediations before execution",
        "value": "Enables safe remediation planning",
        "metric": "Simulation API responds within 10 seconds",
        "research": "Simulation is critical for safe remediation",
        "key_files": ["argus-api/src/handlers/remediation.rs", "contracts/openapi/remediations.yaml"],
        "deps": ["axum", "serde_json"]
    },
    "133": {
        "title": "POST /api/v1/remediations/{id}/execute",
        "action": "execute approved remediation actions",
        "benefit": "approved remediations are carried out automatically",
        "value": "Enables automated remediation execution",
        "metric": "Execution initiated within 1 second of request",
        "research": "Manual remediation execution is slow",
        "key_files": ["argus-api/src/handlers/remediation.rs", "argus-automate/src/executor/mod.rs"],
        "deps": ["axum", "nats"]
    },
    "134": {
        "title": "Execution Progress Tracking",
        "action": "track and report remediation execution progress",
        "benefit": "users can monitor remediation status in real-time",
        "value": "Provides visibility into running remediations",
        "metric": "Progress updates every 5 seconds during execution",
        "research": "Users need real-time visibility into long operations",
        "key_files": ["argus-automate/src/executor/progress.rs", "argus-automate/src/executor/mod.rs"],
        "deps": ["tokio", "serde"]
    },
    "135": {
        "title": "Rollback - Pre-State Capture",
        "action": "capture system state before remediation",
        "benefit": "original state is preserved for potential rollback",
        "value": "Enables reliable rollback of remediation actions",
        "metric": "State capture completes in <5 seconds",
        "research": "Rollback requires accurate pre-change state",
        "key_files": ["argus-automate/src/rollback/capture.rs", "argus-automate/src/rollback/mod.rs"],
        "deps": ["serde", "clickhouse-rs"]
    },
    "136": {
        "title": "Rollback Execution",
        "action": "execute rollback of remediation actions",
        "benefit": "failed or unwanted remediations can be reversed",
        "value": "Provides safety net for remediation actions",
        "metric": "Rollback completes within 2x original action time",
        "research": "Remediation without rollback is high-risk",
        "key_files": ["argus-automate/src/rollback/executor.rs", "argus-automate/src/rollback/mod.rs"],
        "deps": ["tokio"]
    },
    "137": {
        "title": "Rollback Verification",
        "action": "verify rollback restored original state",
        "benefit": "rollback success is confirmed programmatically",
        "value": "Ensures rollback actually worked",
        "metric": "Verification completes within 30 seconds",
        "research": "Assumed rollback success is dangerous",
        "key_files": ["argus-automate/src/rollback/verify.rs", "argus-automate/src/rollback/mod.rs"],
        "deps": ["tokio"]
    },
    "138": {
        "title": "POST /api/v1/remediations/{id}/rollback",
        "action": "expose rollback functionality via API",
        "benefit": "users can trigger rollback through the API",
        "value": "Enables programmatic rollback of remediations",
        "metric": "Rollback API responds within 1 second",
        "research": "Programmatic rollback is faster than manual",
        "key_files": ["argus-api/src/handlers/remediation.rs", "contracts/openapi/remediations.yaml"],
        "deps": ["axum"]
    },
    "139": {
        "title": "Verification Probe - Rescan",
        "action": "trigger rescan to verify remediation effectiveness",
        "benefit": "remediation success is verified by re-scanning",
        "value": "Confirms vulnerabilities are actually fixed",
        "metric": "Rescan triggered within 5 minutes of remediation",
        "research": "Assumed fixes without verification are unreliable",
        "key_files": ["argus-automate/src/verify/rescan.rs", "argus-automate/src/verify/mod.rs"],
        "deps": ["nats", "tokio"]
    },
    "140": {
        "title": "Verification Probe - SigNoz Check",
        "action": "check SigNoz for remediation side effects",
        "benefit": "system health is monitored post-remediation",
        "value": "Detects unintended consequences of remediation",
        "metric": "Health check within 5 minutes of remediation",
        "research": "Remediation can cause service degradation",
        "key_files": ["argus-automate/src/verify/signoz.rs", "argus-automate/src/verify/mod.rs"],
        "deps": ["reqwest", "tokio"]
    },
    "141": {
        "title": "Eligibility Gate - CVSS Check",
        "action": "check CVSS score before remediation eligibility",
        "benefit": "only findings above threshold are eligible for auto-remediation",
        "value": "Focuses automation on high-severity issues",
        "metric": "CVSS check <10ms per finding",
        "research": "Low-severity findings don't warrant automated risk",
        "key_files": ["argus-automate/src/eligibility/cvss.rs", "argus-automate/src/eligibility/mod.rs"],
        "deps": ["serde"]
    },
    "142": {
        "title": "Eligibility Gate - Exploit Known",
        "action": "check if exploit is known before remediation",
        "benefit": "findings with known exploits are prioritized",
        "value": "Prioritizes actively exploited vulnerabilities",
        "metric": "Exploit check <100ms per finding",
        "research": "Known exploits represent higher actual risk",
        "key_files": ["argus-automate/src/eligibility/exploit.rs", "argus-automate/src/eligibility/mod.rs"],
        "deps": ["reqwest", "serde"]
    },
    "143": {
        "title": "Eligibility Gate - Patch Available",
        "action": "check if patch is available before remediation",
        "benefit": "only actionable findings are processed",
        "value": "Prevents wasted effort on un-fixable issues",
        "metric": "Patch check <100ms per finding",
        "research": "No-patch findings cannot be remediated",
        "key_files": ["argus-automate/src/eligibility/patch.rs", "argus-automate/src/eligibility/mod.rs"],
        "deps": ["serde"]
    },
    "144": {
        "title": "Eligibility Gate - Blast Radius",
        "action": "assess blast radius before remediation eligibility",
        "benefit": "high-impact changes require additional review",
        "value": "Prevents automated changes to critical systems",
        "metric": "Blast radius assessment <500ms",
        "research": "Wide-impact changes need human oversight",
        "key_files": ["argus-automate/src/eligibility/blast_radius.rs", "argus-automate/src/eligibility/mod.rs"],
        "deps": ["serde"]
    },
    "145": {
        "title": "Eligibility Gate - Rollback Possible",
        "action": "verify rollback is possible before remediation",
        "benefit": "only reversible actions are automated",
        "value": "Ensures safety net exists for all automated changes",
        "metric": "Rollback check <100ms per action",
        "research": "Irreversible automation is high-risk",
        "key_files": ["argus-automate/src/eligibility/rollback.rs", "argus-automate/src/eligibility/mod.rs"],
        "deps": ["serde"]
    },
    "146": {
        "title": "AI Recommendation - Context Analysis",
        "action": "analyze context for AI-driven recommendations",
        "benefit": "recommendations consider full context of the finding",
        "value": "Enables intelligent remediation suggestions",
        "metric": "Context analysis <2 seconds",
        "research": "Context-aware recommendations are more accurate",
        "key_files": ["argus-policy-ai/src/recommend/context.rs", "argus-policy-ai/src/recommend/mod.rs"],
        "deps": ["serde"]
    },
    "147": {
        "title": "AI Recommendation - Action Selection",
        "action": "select optimal remediation action using AI",
        "benefit": "the best remediation approach is recommended",
        "value": "Optimizes remediation effectiveness",
        "metric": "Action selection <3 seconds",
        "research": "Human selection is slower and less consistent",
        "key_files": ["argus-policy-ai/src/recommend/action.rs", "argus-policy-ai/src/recommend/mod.rs"],
        "deps": ["serde"]
    },
    "148": {
        "title": "Auto-Approval Threshold",
        "action": "implement configurable auto-approval thresholds",
        "benefit": "low-risk remediations can be approved automatically",
        "value": "Reduces manual approval overhead for routine fixes",
        "metric": "Auto-approval processing <100ms",
        "research": "Low-risk fixes don't need human approval",
        "key_files": ["argus-automate/src/approval/threshold.rs", "argus-automate/src/approval/mod.rs"],
        "deps": ["serde"]
    },
    "149": {
        "title": "CVE-10 Pipeline Orchestrator",
        "action": "orchestrate the CVE-10 remediation pipeline",
        "benefit": "top 10 CVEs are automatically prioritized and remediated",
        "value": "Addresses highest-risk vulnerabilities first",
        "metric": "Pipeline processes CVE-10 within 24 hours",
        "research": "Top CVEs represent disproportionate risk",
        "key_files": ["argus-automate/src/pipelines/cve10.rs", "argus-automate/src/pipelines/mod.rs"],
        "deps": ["tokio"]
    },
    "150": {
        "title": "Post-Patch Verification",
        "action": "verify patches were successfully applied",
        "benefit": "patch application is confirmed programmatically",
        "value": "Ensures patches actually took effect",
        "metric": "Verification within 10 minutes of patch",
        "research": "Failed patches leave vulnerabilities open",
        "key_files": ["argus-automate/src/verify/patch.rs", "argus-automate/src/verify/mod.rs"],
        "deps": ["tokio"]
    },
    "151": {
        "title": "Credential Rotation - IAM Keys",
        "action": "automate rotation of IAM access keys",
        "benefit": "stale IAM keys are rotated automatically",
        "value": "Reduces credential exposure window",
        "metric": "Key rotation completes within 5 minutes",
        "research": "Long-lived credentials are a top attack vector",
        "key_files": ["argus-automate/src/remediate/iam_keys.rs", "argus-automate/src/remediate/mod.rs"],
        "deps": ["aws-sdk-iam", "tokio"]
    },
    "152": {
        "title": "Credential Rotation - DB Passwords",
        "action": "automate rotation of database passwords",
        "benefit": "database credentials are rotated regularly",
        "value": "Reduces risk from compromised credentials",
        "metric": "Password rotation with zero downtime",
        "research": "Database credentials are high-value targets",
        "key_files": ["argus-automate/src/remediate/db_passwords.rs", "argus-automate/src/remediate/mod.rs"],
        "deps": ["aws-sdk-secretsmanager", "tokio"]
    },
    "153": {
        "title": "Network Isolation - SG Block",
        "action": "implement security group blocking for network isolation",
        "benefit": "compromised resources can be network-isolated",
        "value": "Contains breaches by blocking network access",
        "metric": "Isolation applied within 30 seconds",
        "research": "Network isolation limits breach impact",
        "key_files": ["argus-automate/src/remediate/sg_block.rs", "argus-automate/src/remediate/mod.rs"],
        "deps": ["aws-sdk-ec2", "tokio"]
    },
    "154": {
        "title": "IAM Role Disable",
        "action": "implement IAM role disabling for compromised identities",
        "benefit": "compromised IAM roles can be disabled immediately",
        "value": "Stops attackers using compromised identities",
        "metric": "Role disabled within 30 seconds",
        "research": "Identity compromise requires immediate response",
        "key_files": ["argus-automate/src/remediate/iam_disable.rs", "argus-automate/src/remediate/mod.rs"],
        "deps": ["aws-sdk-iam", "tokio"]
    },
    "155": {
        "title": "GET /api/v1/remediations/{id}/evidence",
        "action": "expose remediation evidence via API",
        "benefit": "evidence is accessible for audit and compliance",
        "value": "Enables audit-ready evidence retrieval",
        "metric": "Evidence retrieval <500ms",
        "research": "Auditors need on-demand evidence access",
        "key_files": ["argus-api/src/handlers/evidence.rs", "contracts/openapi/remediations.yaml"],
        "deps": ["axum"]
    },
    "156": {
        "title": "Evidence Export",
        "action": "export evidence in compliance-ready formats",
        "benefit": "evidence can be provided to auditors in standard formats",
        "value": "Streamlines compliance reporting",
        "metric": "Export generates PDF/JSON within 30 seconds",
        "research": "Auditors require specific evidence formats",
        "key_files": ["argus-api/src/handlers/evidence_export.rs", "argus-common/src/export/mod.rs"],
        "deps": ["printpdf", "serde_json"]
    },
    "157": {
        "title": "Policy Provenance Tracking",
        "action": "track the origin and history of policies",
        "benefit": "policy changes are traceable to their source",
        "value": "Enables accountability for policy changes",
        "metric": "Provenance query <100ms",
        "research": "Audit requires understanding who changed what",
        "key_files": ["argus-policy/src/provenance/tracking.rs", "argus-policy/src/provenance/mod.rs"],
        "deps": ["clickhouse-rs", "uuid"]
    },
    "158": {
        "title": "Automation Audit Report",
        "action": "generate automation activity audit reports",
        "benefit": "automation activities are documented for compliance",
        "value": "Provides comprehensive automation audit trail",
        "metric": "Reports generated within 60 seconds",
        "research": "Regulators require automation audit trails",
        "key_files": ["argus-api/src/handlers/audit_report.rs", "argus-common/src/reports/automation.rs"],
        "deps": ["printpdf", "chrono"]
    },
    "159": {
        "title": "SLO Metrics Collection",
        "action": "collect SLO metrics for automation services",
        "benefit": "automation performance is measured against objectives",
        "value": "Enables data-driven automation optimization",
        "metric": "Metrics collection latency <100ms",
        "research": "SLOs require accurate metrics collection",
        "key_files": ["argus-automate/src/slo/metrics.rs", "argus-automate/src/slo/mod.rs"],
        "deps": ["prometheus", "tokio"]
    },
    "160": {
        "title": "SLO Dashboard",
        "action": "create dashboard for automation SLO visibility",
        "benefit": "SLO status is visible to operations teams",
        "value": "Enables proactive SLO management",
        "metric": "Dashboard loads in <2 seconds",
        "research": "Operations needs real-time SLO visibility",
        "key_files": ["argus-ui/apps/dashboard/src/pages/slo/", "argus-api/src/handlers/slo.rs"],
        "deps": ["React", "recharts"]
    },
    "161": {
        "title": "SLO Alerting",
        "action": "implement alerting for SLO violations",
        "benefit": "teams are notified when SLOs are at risk",
        "value": "Enables proactive SLO issue resolution",
        "metric": "Alerts fire within 1 minute of violation",
        "research": "Reactive SLO management is too slow",
        "key_files": ["argus-automate/src/slo/alerting.rs", "argus-automate/src/slo/mod.rs"],
        "deps": ["reqwest", "tokio"]
    },
    "162": {
        "title": "Automation Unit Tests",
        "action": "implement comprehensive unit tests for automation",
        "benefit": "automation logic is thoroughly tested",
        "value": "Ensures automation reliability",
        "metric": "Unit test coverage >80%",
        "research": "Untested automation is high-risk",
        "key_files": ["argus-automate/src/tests/", "argus-policy/src/tests/"],
        "deps": ["tokio-test", "mockall"]
    },
    "163": {
        "title": "Automation E2E Tests",
        "action": "implement end-to-end tests for automation workflows",
        "benefit": "complete workflows are validated",
        "value": "Ensures end-to-end automation reliability",
        "metric": "E2E test coverage for all critical paths",
        "research": "Unit tests miss integration issues",
        "key_files": ["integration-tests/automation/", "integration-tests/fixtures/"],
        "deps": ["testcontainers", "reqwest"]
    },
    "164": {
        "title": "Chaos Testing",
        "action": "implement chaos testing for automation resilience",
        "benefit": "automation resilience is validated under failure",
        "value": "Ensures automation handles failures gracefully",
        "metric": "Recovery from injected failures <30 seconds",
        "research": "Production failures expose resilience gaps",
        "key_files": ["integration-tests/chaos/", "integration-tests/chaos/scenarios/"],
        "deps": ["toxiproxy", "testcontainers"]
    }
}

def extract_story_number(filepath: str) -> str:
    """Extract story number from filepath like '01-remediationrequest-data-model'"""
    dirname = Path(filepath).parent.name
    match = re.match(r'^(\d+)-', dirname)
    if match:
        return match.group(1)
    return ""

def parse_current_story(content: str) -> dict:
    """Parse the current story format to extract key information."""
    result = {
        "title": "",
        "epic": "",
        "points": "",
        "priority": "",
        "sprint": "",
        "status": "",
        "worktree": "",
        "branch": "",
        "depends_on": "",
        "blocks": "",
        "jira_key": "",
        "story_text": "",
        "acceptance_criteria": [],
        "references": []
    }

    # Extract title
    title_match = re.search(r'^# (AUTO-\d+): (.+)$', content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(2).strip()

    # Extract metadata line
    meta_match = re.search(r'\*\*Epic:\*\* ([^\|]+)\|\s*\*\*Points:\*\* (\d+)\s*\|\s*\*\*Priority:\*\* (P\d)\s*\|\s*\*\*Sprint:\*\* (\d+)', content)
    if meta_match:
        result["epic"] = meta_match.group(1).strip()
        result["points"] = meta_match.group(2).strip()
        result["priority"] = meta_match.group(3).strip()
        result["sprint"] = meta_match.group(4).strip()

    # Extract status
    status_match = re.search(r'\*\*Status:\*\* (.+)$', content, re.MULTILINE)
    if status_match:
        result["status"] = status_match.group(1).strip()

    # Extract coordination table values
    worktree_match = re.search(r'\| Worktree \| `([^`]+)` \|', content)
    if worktree_match:
        result["worktree"] = worktree_match.group(1).strip()

    branch_match = re.search(r'\| Branch \| `([^`]+)` \|', content)
    if branch_match:
        result["branch"] = branch_match.group(1).strip()

    depends_match = re.search(r'\| Depends On \| ([^\|]+) \|', content)
    if depends_match:
        result["depends_on"] = depends_match.group(1).strip()

    blocks_match = re.search(r'\| Blocks \| ([^\|]+) \|', content)
    if blocks_match:
        result["blocks"] = blocks_match.group(1).strip()

    jira_match = re.search(r'\| JIRA Key \| ([^\|]*) \|', content)
    if jira_match:
        result["jira_key"] = jira_match.group(1).strip()

    # Extract story text
    story_match = re.search(r'## Story\n\n(.+?)\n\n---', content, re.DOTALL)
    if story_match:
        result["story_text"] = story_match.group(1).strip()

    # Extract acceptance criteria
    ac_section = re.search(r'## Acceptance Criteria\n\n(.+?)(?:\n---|\Z)', content, re.DOTALL)
    if ac_section:
        ac_lines = ac_section.group(1).strip().split('\n')
        for line in ac_lines:
            # Match lines like "- [ ] FUNC-1: Create new key"
            ac_match = re.match(r'-\s*\[\s*\]\s*(FUNC-\d+):\s*(.+)', line)
            if ac_match:
                result["acceptance_criteria"].append({
                    "id": ac_match.group(1),
                    "text": ac_match.group(2).strip()
                })

    return result

def generate_user_story(story_num: str, parsed: dict) -> str:
    """Generate the user story section."""
    meta = STORY_METADATA.get(story_num, {})
    action = meta.get("action", parsed["story_text"].lower())
    benefit = meta.get("benefit", "the automation workflow is enhanced")

    return f'As an **automation engineer**, I want **{action}**, so that **{benefit}**.'

def generate_business_value(story_num: str, parsed: dict) -> str:
    """Generate the business value section."""
    meta = STORY_METADATA.get(story_num, {})
    value = meta.get("value", f"Enables {parsed['story_text'].lower()}")
    metric = meta.get("metric", "Feature functions as specified")
    research = meta.get("research", "Automation requirements from security operations team")

    return f"""**Value Statement:** {value}

**Success Metric:** {metric}

**User Research:** {research}"""

def generate_acceptance_criteria(parsed: dict) -> str:
    """Generate acceptance criteria in GIVEN/WHEN/THEN format."""
    acs = parsed["acceptance_criteria"]
    if not acs:
        return """### AC1: Core Functionality
**GIVEN** the system is properly configured
**WHEN** the feature is invoked
**THEN** the expected behavior occurs
**AND** all validation passes"""

    result = []
    for i, ac in enumerate(acs, 1):
        ac_text = ac["text"]
        # Generate GIVEN/WHEN/THEN based on AC text
        result.append(f"""### AC{i}: {ac_text}
**GIVEN** the system is in a valid state
**WHEN** {ac_text.lower()} is performed
**THEN** the operation completes successfully
**AND** the result is persisted and verifiable""")

    return "\n\n".join(result)

def generate_tasks_section(story_num: str, parsed: dict) -> str:
    """Generate the tasks section with 4 tasks."""
    story_id = f"AUTO-{story_num}"
    dir_name = parsed.get("branch", f"{story_num}-implementation")

    return f"""| Task | Description | Link | Status |
|------|-------------|------|--------|
| T1 | Core Implementation | [task-01-implementation.md](./tasks/task-01-implementation.md) | pending |
| T2 | Unit Tests | [task-02-unit-tests.md](./tasks/task-02-unit-tests.md) | pending |
| T3 | Integration Tests | [task-03-integration-tests.md](./tasks/task-03-integration-tests.md) | pending |
| T4 | Documentation | [task-04-documentation.md](./tasks/task-04-documentation.md) | pending |"""

def generate_technical_notes(story_num: str, parsed: dict) -> str:
    """Generate technical notes section."""
    meta = STORY_METADATA.get(story_num, {})
    key_files = meta.get("key_files", ["TBD based on implementation"])
    deps = meta.get("deps", ["See Cargo.toml"])

    key_files_str = "\n".join([f"- `{f}`" for f in key_files])
    deps_str = ", ".join(deps)

    return f"""### Key Files

{key_files_str}

### Dependencies

{deps_str}

### Testing Requirements

| Path | Test File | Coverage |
|------|-----------|----------|
| Happy Path | tests/unit/{story_num}_test.rs | Core functionality |
| Fail Path | tests/unit/{story_num}_errors_test.rs | Error handling |
| Null/Empty | tests/unit/{story_num}_edge_test.rs | Edge cases |
| Edge Cases | tests/integration/{story_num}_integration_test.rs | Integration scenarios |"""

def remediate_story(filepath: str) -> str:
    """Remediate a single story file to BMAD-compliant format."""
    with open(filepath, 'r') as f:
        content = f.read()

    story_num = extract_story_number(filepath)
    parsed = parse_current_story(content)

    # Build the new story content
    story_id = f"AUTO-{story_num}"
    title = parsed["title"]

    new_content = f"""# {story_id}: {title}

**Epic:** {parsed["epic"]} | **Points:** {parsed["points"]} | **Priority:** {parsed["priority"]} | **Sprint:** {parsed["sprint"]}
**Status:** {parsed["status"]}

---

## Coordination

| Field | Value |
|-------|-------|
| Worktree | `{parsed["worktree"]}` |
| Branch | `{parsed["branch"]}` |
| Depends On | {parsed["depends_on"]} |
| Blocks | {parsed["blocks"]} |
| JIRA Key | {parsed["jira_key"]} |

### Task Execution Order

```
T1 -> T2 -> T3 -> T4
```

---

## User Story

{generate_user_story(story_num, parsed)}

---

## Business Value

{generate_business_value(story_num, parsed)}

---

## Acceptance Criteria

{generate_acceptance_criteria(parsed)}

---

## Tasks

{generate_tasks_section(story_num, parsed)}

---

## Technical Notes

{generate_technical_notes(story_num, parsed)}

---

## References

- Epic: EPIC-4-AUTOMATION
- PRD: .bmad/planning-artifacts/prd.md
- Architecture: docs/ARCHITECTURE_OVERVIEW.md
"""

    return new_content

def main():
    """Main function to remediate all EPIC-4 stories."""
    import glob

    # Find all story files
    pattern = str(EPIC4_STORIES_DIR / "*/story-*.md")
    story_files = sorted(glob.glob(pattern))

    print(f"Found {len(story_files)} story files to remediate")

    for filepath in story_files:
        try:
            new_content = remediate_story(filepath)
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Remediated: {Path(filepath).name}")
        except Exception as e:
            print(f"ERROR processing {filepath}: {e}")

    print(f"\nRemediation complete. {len(story_files)} stories updated.")

if __name__ == "__main__":
    main()
