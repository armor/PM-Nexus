#!/usr/bin/env python3
"""
Story Enhancement Script for Armor Argus BMAD Stories.
Enhances stories with TARGET FILES, Code Patterns, Anti-Patterns, Edge Cases,
GIVEN-WHEN-THEN acceptance criteria, and Verification Commands.
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Story type patterns for inferring target files and patterns
STORY_PATTERNS = {
    # OAuth/Cloud Connection stories
    r"OAuth.*AWS": {
        "type": "oauth",
        "cloud": "aws",
        "targets": {
            "backend": [
                "submodules/argus-api/src/handlers/oauth/aws.rs",
                "submodules/argus-api/src/services/cloud_connection.rs",
                "submodules/argus-common/src/cloud/aws.rs",
            ],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/onboarding/AwsConnect.tsx",
                "submodules/argus-ui/apps/dashboard/src/features/onboarding/hooks/useAwsOAuth.ts",
            ],
            "infra": ["deploy/cloudformation/argus-cross-account-role.yaml"],
        },
    },
    r"OAuth.*GCP": {
        "type": "oauth",
        "cloud": "gcp",
        "targets": {
            "backend": [
                "submodules/argus-api/src/handlers/oauth/gcp.rs",
                "submodules/argus-api/src/services/cloud_connection.rs",
            ],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/onboarding/GcpConnect.tsx",
            ],
            "infra": ["deploy/deployment-manager/argus-service-account.jinja"],
        },
    },
    r"OAuth.*Azure": {
        "type": "oauth",
        "cloud": "azure",
        "targets": {
            "backend": [
                "submodules/argus-api/src/handlers/oauth/azure.rs",
                "submodules/argus-api/src/services/cloud_connection.rs",
            ],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/onboarding/AzureConnect.tsx",
            ],
            "infra": ["deploy/arm-templates/argus-service-principal.json"],
        },
    },
    # UI Component stories (executive dashboards, scores, trends)
    r"(Dashboard|Component|Widget|Display|Chart|Score|Posture|Trend|Exec|Risk)": {
        "type": "ui-component",
        "targets": {
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/dashboard/components/",
                "submodules/argus-ui/apps/dashboard/src/features/executive/",
            ],
            "backend": ["submodules/argus-api/src/handlers/dashboard/"],
        },
    },
    # Onboarding stories
    r"(Onboarding|Checklist|Welcome|Wizard|Setup|Scanner)": {
        "type": "onboarding",
        "targets": {
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/onboarding/",
            ],
            "backend": ["submodules/argus-api/src/handlers/onboarding/"],
        },
    },
    # Auto-Fix/Remediation stories (S3, security groups, IAM)
    r"(Auto-Fix|Remediation|Fix|Rollback|Simulation|S3|Security Group|IAM|Public)": {
        "type": "remediation",
        "targets": {
            "backend": [
                "submodules/argus-policy/src/remediation/",
                "submodules/argus-api/src/handlers/remediation/",
            ],
            "agent": ["submodules/armor-agent/cmd/"],
        },
    },
    # Natural Language/AI stories
    r"(Natural Language|NL|Query Engine|AI|LLM|Parser|Contextual|Explain)": {
        "type": "ai",
        "targets": {
            "backend": [
                "submodules/argus-api/src/handlers/ai/",
                "submodules/argus-policy/src/ai/",
            ],
        },
    },
    # Integration stories (SCM, CI/CD, etc.)
    r"(GitHub|GitLab|Slack|JIRA|PagerDuty|Webhook|Integration|SCM|PR|CI/CD|Terraform)": {
        "type": "integration",
        "targets": {
            "backend": ["submodules/argus-api/src/handlers/integrations/"],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/integrations/"
            ],
        },
    },
    # Compliance/Exec stories
    r"(Compliance|Framework|SOC|PCI|HIPAA|Coverage|Audit|Evidence|Report|COMP-|EXEC-)": {
        "type": "compliance",
        "targets": {
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/compliance/",
                "submodules/argus-ui/apps/dashboard/src/features/executive/",
            ],
            "backend": ["submodules/argus-api/src/handlers/compliance/"],
        },
    },
    # Graph/Cartography stories
    r"(Graph|NebulaGraph|Schema|Tag|Edge|Cartography|Asset|CARTO-|Relationship|Traversal)": {
        "type": "graph",
        "targets": {
            "backend": [
                "submodules/argus-graph-service/src/",
                "submodules/forks/cartography/",
            ],
            "schema": ["schemas/nebulagraph/"],
        },
    },
    # Policy stories
    r"(Policy|Cedar|Rule|Authorization|POLICY-)": {
        "type": "policy",
        "targets": {
            "backend": [
                "submodules/argus-policy/src/",
                "contracts/cedar/",
            ],
        },
    },
    # Threat Intelligence stories
    r"(Threat|Intelligence|Feed|IOC|Indicator|CVE|EPSS|Exploit)": {
        "type": "threat-intel",
        "targets": {
            "backend": [
                "submodules/argus-ingest/src/threat_intel/",
                "submodules/argus-api/src/handlers/threat_intel/",
            ],
        },
    },
    # Cost/Analytics stories
    r"(Cost|Calculator|Breach|ROI|Savings|Analytics|Metric)": {
        "type": "analytics",
        "targets": {
            "backend": ["submodules/argus-score/src/"],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/analytics/"
            ],
        },
    },
    # Attack Path stories
    r"(Attack Path|Attack Surface|Blast Radius|Crown Jewel|Path)": {
        "type": "attack-path",
        "targets": {
            "backend": [
                "submodules/argus-graph-service/src/attack_path/",
            ],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/attack-path/"
            ],
        },
    },
    # Notification stories
    r"(Notification|Alert|Email|SMS|Escalation)": {
        "type": "notification",
        "targets": {
            "backend": [
                "submodules/argus-api/src/handlers/notifications/",
            ],
            "frontend": [
                "submodules/argus-ui/apps/dashboard/src/features/notifications/"
            ],
        },
    },
}


def get_story_type(title):
    """Determine story type from title."""
    for pattern, config in STORY_PATTERNS.items():
        if re.search(pattern, title, re.IGNORECASE):
            return config
    return {"type": "generic", "targets": {}}


def generate_target_files_section(story_type, title):
    """Generate TARGET FILES section based on story type."""
    targets = story_type.get("targets", {})
    if not targets:
        return ""

    lines = ["## Target Files\n"]

    if "backend" in targets:
        lines.append("### Backend")
        lines.append("```")
        for f in targets["backend"]:
            lines.append(f)
        lines.append("```\n")

    if "frontend" in targets:
        lines.append("### Frontend (argus-ui)")
        lines.append("```")
        for f in targets["frontend"]:
            lines.append(f)
        lines.append("```\n")

    if "infra" in targets:
        lines.append("### Infrastructure")
        lines.append("```")
        for f in targets["infra"]:
            lines.append(f)
        lines.append("```\n")

    if "schema" in targets:
        lines.append("### Schema")
        lines.append("```")
        for f in targets["schema"]:
            lines.append(f)
        lines.append("```\n")

    if "agent" in targets:
        lines.append("### Agent")
        lines.append("```")
        for f in targets["agent"]:
            lines.append(f)
        lines.append("```\n")

    return "\n".join(lines)


def generate_edge_cases(story_type, title):
    """Generate edge cases based on story type."""
    stype = story_type.get("type", "generic")

    edge_cases = {
        "oauth": [
            ("OAuth timeout (>5 min)", "Session expires, user prompted to restart"),
            ("Network failure during callback", "Retry with exponential backoff"),
            ("User closes popup mid-flow", "Clean up partial state"),
            ("Duplicate account connection", "Reject with clear message"),
            ("Insufficient permissions", "Clear error with required permissions"),
        ],
        "ui-component": [
            ("Empty data state", "Show appropriate empty state UI"),
            ("Loading state", "Show skeleton/loading indicator"),
            ("API error", "Show error state with retry option"),
            ("Large dataset (>10k items)", "Implement virtualization"),
            ("Mobile viewport", "Responsive design adapts"),
        ],
        "remediation": [
            ("Remediation fails mid-execution", "Automatic rollback triggered"),
            ("Resource no longer exists", "Skip with audit log"),
            ("Concurrent remediation conflict", "Queue or reject duplicate"),
            ("Insufficient cloud permissions", "Clear error with fix steps"),
            ("Rate limit exceeded", "Backoff and retry"),
        ],
        "ai": [
            ("Empty input", "Return validation error"),
            ("Ambiguous query", "Ask for clarification"),
            ("Malicious prompt injection", "Sanitize and reject"),
            ("LLM timeout", "Fallback to cached response"),
            ("Rate limit exceeded", "Queue request"),
        ],
        "graph": [
            ("Cycle detected in graph", "Handle gracefully"),
            ("Missing node reference", "Create placeholder or error"),
            ("Large traversal (>1M nodes)", "Implement pagination"),
            ("Concurrent write conflict", "Use optimistic locking"),
            ("Schema migration", "Backward compatible"),
        ],
        "compliance": [
            ("Framework not configured", "Show setup instructions"),
            ("Partial evidence collection", "Show incomplete status"),
            ("Control mapping conflict", "Allow manual override"),
            ("Export timeout", "Async generation with notification"),
        ],
        "attack-path": [
            ("No attack paths found", "Show empty state with guidance"),
            ("Very long attack path (>20 hops)", "Truncate with expand option"),
            ("Circular path detected", "Handle and display appropriately"),
            ("Missing asset in path", "Show placeholder with warning"),
            ("Stale graph data", "Show last updated timestamp"),
        ],
        "notification": [
            ("No notification channels configured", "Show setup wizard"),
            ("Email delivery failure", "Retry with backoff, show status"),
            ("Rate limit on notifications", "Queue and batch"),
            ("Duplicate notification", "Deduplicate within window"),
            ("User unsubscribed", "Respect preferences"),
        ],
        "generic": [
            ("Empty input", "Validate and show error"),
            ("Network failure", "Retry with backoff"),
            ("Unauthorized access", "Return 401/403 appropriately"),
            ("Invalid data format", "Validate and reject"),
        ],
    }

    cases = edge_cases.get(stype, edge_cases["generic"])

    lines = ["## Edge Cases (MUST HANDLE)\n"]
    lines.append("| Edge Case | Expected Behavior | Test Required |")
    lines.append("|-----------|-------------------|---------------|")
    for case, behavior in cases:
        lines.append(f"| {case} | {behavior} | Yes |")
    lines.append("")

    return "\n".join(lines)


def generate_verification_commands(story_type, story_id):
    """Generate verification commands based on story type."""
    stype = story_type.get("type", "generic")

    lines = ["## Verification Commands\n"]

    if stype in ["oauth", "remediation", "ai", "policy", "threat-intel"]:
        lines.append("### Backend Tests")
        lines.append("```bash")
        lines.append(f"cd submodules/argus-api && cargo test {story_id.lower()} --nocapture")
        lines.append(f"cd submodules/argus-api && cargo test --test integration {story_id.lower()}")
        lines.append("```\n")

    if stype in ["ui-component", "onboarding", "compliance", "oauth"]:
        lines.append("### Frontend Tests")
        lines.append("```bash")
        lines.append(f"cd submodules/argus-ui && nx test dashboard --testFile={story_id}.spec.tsx")
        lines.append(f"cd submodules/argus-ui && nx e2e dashboard-e2e --spec={story_id.lower()}.cy.ts")
        lines.append("```\n")

    if stype == "graph":
        lines.append("### Graph Tests")
        lines.append("```bash")
        lines.append("cd submodules/argus-graph-service && cargo test schema --nocapture")
        lines.append('nebula-console -e "SHOW TAGS; SHOW EDGES;"')
        lines.append("```\n")

    return "\n".join(lines)


def generate_gherkin_scenarios(story_type, title, description):
    """Generate GIVEN-WHEN-THEN scenarios."""
    stype = story_type.get("type", "generic")

    lines = ["## GIVEN-WHEN-THEN Acceptance Criteria\n"]

    # Happy path
    lines.append("### Scenario 1: Happy Path")
    lines.append("```gherkin")
    lines.append(f"GIVEN the user has appropriate permissions")
    lines.append(f"WHEN they interact with {title}")
    lines.append(f"THEN the operation completes successfully")
    lines.append(f"  AND the result is persisted to the database")
    lines.append(f"  AND an audit log entry is created")
    lines.append("```\n")

    # Error path
    lines.append("### Scenario 2: Error Handling")
    lines.append("```gherkin")
    lines.append(f"GIVEN the user initiates {title}")
    lines.append(f"WHEN an error occurs during processing")
    lines.append(f"THEN a clear error message is displayed")
    lines.append(f"  AND no partial state is left")
    lines.append(f"  AND the user can retry the operation")
    lines.append("```\n")

    # Validation
    lines.append("### Scenario 3: Input Validation")
    lines.append("```gherkin")
    lines.append(f"GIVEN the user provides invalid input")
    lines.append(f"WHEN they submit the form")
    lines.append(f"THEN validation errors are displayed")
    lines.append(f"  AND no API call is made")
    lines.append(f"  AND the form state is preserved")
    lines.append("```\n")

    return "\n".join(lines)


def generate_anti_patterns(story_type):
    """Generate anti-patterns based on story type."""
    stype = story_type.get("type", "generic")

    patterns = {
        "oauth": [
            ("Hardcoded secrets", "Use environment/secrets manager"),
            ("Missing PKCE", "Always use PKCE for OAuth"),
            ("Unvalidated state parameter", "Validate OAuth state"),
        ],
        "ui-component": [
            ("Direct DOM manipulation", "Use React state"),
            ("Missing loading states", "Always show loading indicators"),
            ("Unhandled API errors", "Wrap in error boundaries"),
        ],
        "remediation": [
            ("Missing rollback", "Always implement rollback"),
            ("No dry-run option", "Support simulation mode"),
            ("Insufficient logging", "Log all actions for audit"),
        ],
        "graph": [
            ("N+1 queries", "Use batch queries"),
            ("Missing indexes", "Add indexes for frequent queries"),
            ("Unvalidated vertex IDs", "Validate before insertion"),
        ],
        "attack-path": [
            ("Unbounded graph traversal", "Limit depth and breadth"),
            ("No caching of paths", "Cache frequently queried paths"),
            ("Synchronous path calculation", "Use async with progress"),
        ],
        "notification": [
            ("Sending without rate limiting", "Implement rate limits"),
            ("No delivery tracking", "Track delivery status"),
            ("Hardcoded templates", "Use configurable templates"),
        ],
        "generic": [
            ("Hardcoded values", "Use configuration"),
            ("Missing error handling", "Handle all error cases"),
            ("No input validation", "Validate all inputs"),
        ],
    }

    anti = patterns.get(stype, patterns["generic"])

    lines = ["## Anti-Patterns (FORBIDDEN)\n"]
    for i, (bad, good) in enumerate(anti, 1):
        lines.append(f"### {i}. {bad}")
        lines.append("```")
        lines.append(f"// FORBIDDEN - {bad}")
        lines.append(f"// CORRECT - {good}")
        lines.append("```\n")

    return "\n".join(lines)


def enhance_story(filepath, force=False):
    """Enhance a single story file."""
    with open(filepath, "r") as f:
        content = f.read()

    # Skip if already fully enhanced (has all sections)
    if "## Target Files" in content and "## Edge Cases" in content and "## GIVEN-WHEN-THEN" in content:
        if not force:
            return False

    # Extract story info
    title_match = re.search(r"title:\s*\"([^\"]+)\"", content)
    title = title_match.group(1) if title_match else "Unknown"

    id_match = re.search(r"id:\s*(\S+)", content)
    story_id = id_match.group(1) if id_match else "UNKNOWN"

    desc_match = re.search(r"## Problem Statement\s+([^\n]+)", content)
    description = desc_match.group(1) if desc_match else title

    # Get story type
    story_type = get_story_type(title)

    # Generate new sections
    target_files = generate_target_files_section(story_type, title)
    edge_cases = generate_edge_cases(story_type, title)
    verification = generate_verification_commands(story_type, story_id)
    gherkin = generate_gherkin_scenarios(story_type, title, description)
    anti_patterns = generate_anti_patterns(story_type)

    # Find insertion points and add sections
    # Add Target Files after Goal section (if not already present)
    if "## Target Files" not in content and target_files:
        # Match "## Goal" followed by content until "## Scope"
        goal_match = re.search(r"(## Goal.*?)(## Scope)", content, re.DOTALL)
        if goal_match:
            insert_pos = goal_match.start(2)
            content = content[:insert_pos] + target_files + "\n---\n\n" + content[insert_pos:]

    # Add GIVEN-WHEN-THEN after Acceptance Criteria
    if "## GIVEN-WHEN-THEN" not in content:
        ac_match = re.search(r"(## Acceptance Criteria[^#]+?)(\n---)", content)
        if ac_match:
            insert_pos = ac_match.end(1)
            content = content[:insert_pos] + "\n---\n\n" + gherkin + anti_patterns + edge_cases + verification + content[insert_pos:]

    # Update verification command placeholders
    content = content.replace("`**`", f"`cargo test {story_id.lower()} --nocapture`")

    # Add enhanced timestamp
    if "*Generated:" in content:
        content = re.sub(r"\*Generated:[^\*]+\*", f"*Enhanced: {datetime.now().strftime('%Y-%m-%d')}*", content)

    with open(filepath, "w") as f:
        f.write(content)

    return True


def main():
    base_path = Path("/Users/phillipboles/Development/armor-argus/.bmad/generated-stories")

    epics = [
        "EPIC-7-DIFFERENTIATION",
        "EPIC-8-EXEC-COMPLIANCE",
        "EPIC-9-POLICY-AI",
        "EPIC-11-CARTOGRAPHY-NEBULAGRAPH",
    ]

    enhanced_count = 0
    skipped_count = 0

    for epic in epics:
        epic_path = base_path / epic
        if not epic_path.exists():
            print(f"Epic path not found: {epic_path}")
            continue

        for story_file in sorted(epic_path.glob("*.md")):
            if story_file.name == "README.md":
                continue

            try:
                if enhance_story(story_file):
                    enhanced_count += 1
                    print(f"Enhanced: {story_file.name}")
                else:
                    skipped_count += 1
                    print(f"Skipped (already enhanced): {story_file.name}")
            except Exception as e:
                print(f"Error processing {story_file.name}: {e}")

    print(f"\nSummary: Enhanced {enhanced_count} stories, Skipped {skipped_count}")


if __name__ == "__main__":
    main()
