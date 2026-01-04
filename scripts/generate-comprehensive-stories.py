#!/usr/bin/env python3
"""
Generate Comprehensive Story Templates for Armor Argus

This script reads epic markdown files and generates comprehensive
story templates with party-mode AI prompts for JIRA sync.

Usage:
    python scripts/generate-comprehensive-stories.py [--epic EPIC_ID] [--dry-run]

Examples:
    python scripts/generate-comprehensive-stories.py                    # All epics
    python scripts/generate-comprehensive-stories.py --epic EPIC-1     # Single epic
    python scripts/generate-comprehensive-stories.py --dry-run         # Preview only
"""

import os
import re
import json
import yaml
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad" / "planning-artifacts" / "epics"
OUTPUT_DIR = PROJECT_ROOT / ".bmad" / "generated-stories"
TEMPLATES_DIR = PROJECT_ROOT / ".bmad" / "templates"
PRD_PATH = PROJECT_ROOT / ".bmad" / "planning-artifacts" / "prd.md"

# Epic to JIRA key mapping (from jira-sync-state.yaml)
EPIC_JIRA_KEYS = {
    "EPIC-1-PLATFORM": "ARGUS-1",
    "EPIC-2-GRAPH": "ARGUS-3",
    "EPIC-3-RISK": "ARGUS-4",
    "EPIC-4-AUTOMATION": "ARGUS-5",
    "EPIC-5-UX": "ARGUS-6",
    "EPIC-6-INTEGRATION": "ARGUS-7",
    "EPIC-7-DIFFERENTIATION": "ARGUS-8",
    "EPIC-8-PLATFORM-DOMINANCE": "ARGUS-9",
    "EPIC-8-EXEC-COMPLIANCE": "ARGUS-92",
    "EPIC-9-OPERATIONS": "ARGUS-10",
    "EPIC-9-POLICY-AI": "ARGUS-93",
    "EPIC-AUTH-001": "ARGUS-11",
    "EPIC-11-CARTOGRAPHY": "ARGUS-94",
}

# Story prefix to epic mapping
STORY_PREFIX_MAP = {
    "PLAT": "EPIC-1-PLATFORM",
    "GRAPH": "EPIC-2-GRAPH",
    "RISK": "EPIC-3-RISK",
    "AUTO": "EPIC-4-AUTOMATION",
    "UX": "EPIC-5-UX",
    "INT": "EPIC-6-INTEGRATION",
    "DIFF": "EPIC-7-DIFFERENTIATION",
    "DOM": "EPIC-8-PLATFORM-DOMINANCE",
    "EXEC": "EPIC-8-EXEC-COMPLIANCE",
    "OPS": "EPIC-9-OPERATIONS",
    "PAI": "EPIC-9-POLICY-AI",
    "AUTH": "EPIC-AUTH-001",
    "CART": "EPIC-11-CARTOGRAPHY",
}


@dataclass
class FunctionalRequirement:
    id: str
    name: str
    acceptance_criteria: List[str] = field(default_factory=list)
    specification: Optional[Dict] = None


@dataclass
class Story:
    id: str
    title: str
    description: str
    points: int
    wave: int
    sprint: int
    priority: str
    mvp: int
    epic_id: str
    epic_jira_key: str
    story_type: str  # infrastructure, backend, frontend, integration
    functional_requirements: List[FunctionalRequirement] = field(default_factory=list)
    code_quality: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    unit_testing: List[str] = field(default_factory=list)
    integration_testing: List[str] = field(default_factory=list)
    e2e_testing: List[str] = field(default_factory=list)
    verification: Optional[str] = None

    @property
    def labels(self) -> List[str]:
        prefix = self.id.split("-")[0].lower()
        return [
            prefix,
            f"wave{self.wave}",
            f"sprint{self.sprint}",
            self.priority.lower(),
            f"mvp{self.mvp}",
        ]


def parse_epic_file(epic_path: Path) -> List[Story]:
    """Parse an epic markdown file and extract stories."""
    content = epic_path.read_text()
    stories = []

    # Use filename as epic ID (more reliable than content extraction)
    epic_id = epic_path.stem  # e.g., "EPIC-4-AUTOMATION"

    # Get JIRA key from filename-based epic ID
    epic_jira_key = EPIC_JIRA_KEYS.get(epic_id, "UNKNOWN")

    # If not found, try extracting from content and check all partial matches
    if epic_jira_key == "UNKNOWN":
        epic_match = re.search(r"# (EPIC-\d+)", content)
        if epic_match:
            partial_id = epic_match.group(1)  # e.g., "EPIC-4"
            # Find a key that starts with this partial ID
            for key in EPIC_JIRA_KEYS:
                if key.startswith(partial_id):
                    epic_jira_key = EPIC_JIRA_KEYS[key]
                    break

    # Find all stories using regex
    story_pattern = re.compile(
        r'#### ([A-Z]+-\d+): (.+?)\n'
        r'\*\*Points:\*\* (\d+) \| \*\*Wave:\*\* (\d+) \| \*\*Sprint:\*\* (\d+) \| \*\*Priority:\*\* (P\d) \| \*\*MVP:\*\* (\d+)',
        re.MULTILINE
    )

    # Find story sections
    story_sections = re.split(r'(?=#### [A-Z]+-\d+:)', content)

    for section in story_sections:
        match = story_pattern.search(section)
        if not match:
            continue

        story_id, title, points, wave, sprint, priority, mvp = match.groups()

        # Determine story type based on content
        story_type = determine_story_type(section, story_id)

        # Extract description (line after title)
        desc_match = re.search(r'\*\*MVP:\*\* \d+\n.*?\n\n(.+?)(?=\n\n\*\*|\Z)', section, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else title

        # Extract functional requirements
        func_reqs = parse_functional_requirements(section)

        # Extract other requirements
        code_quality = parse_checklist(section, "Code Quality")
        security = parse_checklist(section, "Security")
        unit_testing = parse_checklist(section, "Unit Testing")
        integration_testing = parse_checklist(section, "Integration Testing")
        e2e_testing = parse_checklist(section, "E2E Testing")

        # Extract verification
        ver_match = re.search(r'\*\*Verification:\*\*\n- Command: (.+?)(?=\n- Expected:)', section)
        verification = ver_match.group(1).strip() if ver_match else None

        story = Story(
            id=story_id,
            title=title,
            description=description,
            points=int(points),
            wave=int(wave),
            sprint=int(sprint),
            priority=priority,
            mvp=int(mvp),
            epic_id=epic_id,
            epic_jira_key=epic_jira_key,
            story_type=story_type,
            functional_requirements=func_reqs,
            code_quality=code_quality,
            security=security,
            unit_testing=unit_testing,
            integration_testing=integration_testing,
            e2e_testing=e2e_testing,
            verification=verification,
        )
        stories.append(story)

    return stories


def determine_story_type(section: str, story_id: str) -> str:
    """Determine story type based on content analysis and story ID prefix."""
    section_lower = section.lower()
    story_prefix = story_id.split("-")[0].upper()

    # UX stories are almost always frontend
    if story_prefix == "UX":
        return "frontend"

    # Infrastructure keywords take priority
    if any(kw in section_lower for kw in ["helm", "kubernetes", "k8s", "deployment", "statefulset", "cronjob", "configmap", "secret", "pvc", "chart"]):
        return "infrastructure"

    # Service scaffold stories are backend
    if "service scaffold" in section_lower or "service" in section_lower and "rust" in section_lower:
        return "backend"

    # Explicit frontend indicators
    if any(kw in section_lower for kw in ["react", "component", "page", "ui display", "button", "modal", "dashboard", "tailwind"]):
        return "frontend"

    # API and endpoint stories are backend
    if any(kw in section_lower for kw in ["api", "endpoint", "post /", "get /", "put /", "delete /", "cargo", "rust", "axum"]):
        return "backend"

    # Integration stories
    if any(kw in section_lower for kw in ["integration", "adapter", "scanner", "sync", "webhook"]):
        return "integration"

    # Default based on prefix
    if story_prefix in ["PLAT", "AUTO", "RISK", "INT", "GRAPH", "POLICY", "AUTH", "CARTO"]:
        return "backend"
    elif story_prefix in ["UX", "EXEC"]:
        return "frontend"
    else:
        return "backend"  # Default


def parse_functional_requirements(section: str) -> List[FunctionalRequirement]:
    """Parse functional requirements from story section."""
    reqs = []

    # Find functional requirements section
    fr_match = re.search(r'\*\*Functional Requirements:\*\*\n(.*?)(?=\n\n\*\*|\Z)', section, re.DOTALL)
    if not fr_match:
        return reqs

    fr_content = fr_match.group(1)

    # Parse each FUNC-N item
    func_pattern = re.compile(r'- \[ \] (FUNC-\d+): (.+)')
    for match in func_pattern.finditer(fr_content):
        func_id, desc = match.groups()
        reqs.append(FunctionalRequirement(
            id=func_id,
            name=desc.strip(),
            acceptance_criteria=[desc.strip()],
        ))

    return reqs


def parse_checklist(section: str, header: str) -> List[str]:
    """Parse a checklist section."""
    items = []

    pattern = rf'\*\*{header}:\*\*\n(.*?)(?=\n\n\*\*|\Z)'
    match = re.search(pattern, section, re.DOTALL)
    if not match:
        return items

    content = match.group(1)
    item_pattern = re.compile(r'- \[ \] [A-Z]+-\d+: (.+)')
    for m in item_pattern.finditer(content):
        items.append(m.group(1).strip())

    return items


def generate_problem_statement(story: Story) -> str:
    """Generate problem statement with AI prompt."""
    return f"""## Problem Statement

{story.description}

### AI Implementation Prompt - Problem Analysis

```
You are implementing {story.id}: {story.title} for Armor Argus.

PLATFORM CONTEXT (memorize this):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Armor Argus is an autonomous cloud security platform that:
- Replaces visibility-only tools by safely FIXING highest-impact risks
- Uses NebulaGraph for attack path analysis (graph queries)
- Uses ClickHouse for findings, risk scores, events, and audit evidence (analytics)
- Uses Cedar policy language for deterministic policy enforcement
- Requires SigNoz/OpenTelemetry for all observability

EPIC CONTEXT: {story.epic_id}
This story is part of Wave {story.wave}, Sprint {story.sprint}.
Priority: {story.priority} | MVP: {story.mvp} | Points: {story.points}

WHY THIS STORY MATTERS:
1. {story.description}
2. This enables downstream features in later sprints
3. Blocking: stories that depend on this must wait

BEFORE PROCEEDING, VERIFY YOU UNDERSTAND:
□ What does this story accomplish?
□ What services/components does it modify?
□ What are the acceptance criteria?
□ What patterns should you follow from existing code?

If ANY of the above is unclear, STOP and research before coding.
```
"""


def generate_functional_requirements_section(story: Story) -> str:
    """Generate functional requirements with AI prompts."""
    lines = ["## Functional Requirements\n"]

    for i, fr in enumerate(story.functional_requirements, 1):
        lines.append(f"""
### FR-{i}: {fr.name}

**Acceptance Criteria:**
- [ ] {fr.name}

### AI Implementation Prompt - FR-{i}

```
IMPLEMENT FR-{i}: {fr.name}

CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Story: {story.id} - {story.title}
This requirement: {fr.name}

IMPLEMENTATION STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Identify the target file(s)
2. Implement the requirement
3. Add unit tests
4. Verify functionality

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Requirement implemented
- [ ] Tests passing
- [ ] No regressions
```
""")

    return "\n".join(lines)


def generate_storybook_section(story: Story) -> str:
    """Generate Storybook requirements for frontend stories."""
    if story.story_type != "frontend":
        return ""

    return f"""## Storybook Requirements

### AI Implementation Prompt - Storybook Implementation

```
STORYBOOK REQUIREMENTS FOR {story.id}

MANDATORY: All UI components MUST have Storybook stories.

STORYBOOK STORY FILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Location: apps/argus-ui/src/components/{{feature}}/{{Component}}.stories.tsx

REQUIRED STORIES:
──────────────────────────────────────
1. Default - Component with default props
2. Loading - Component in loading state
3. Empty - Component with no data
4. Error - Component in error state
5. Interactive - Component with user interactions
6. Variants - All visual variants (if applicable)

STORYBOOK PATTERN:
──────────────────────────────────────
import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {{Component}} }} from './{{Component}}';

const meta: Meta<typeof {{Component}}> = {{
  title: 'Features/{{Feature}}/{{Component}}',
  component: {{Component}},
  tags: ['autodocs'],
  parameters: {{
    layout: 'centered',
    docs: {{
      description: {{
        component: '{{Component description}}',
      }},
    }},
  }},
  argTypes: {{
    // Define controls for props
  }},
}};

export default meta;
type Story = StoryObj<typeof {{Component}}>;

export const Default: Story = {{
  args: {{
    // Default props
  }},
}};

export const Loading: Story = {{
  args: {{
    isLoading: true,
  }},
}};

export const Empty: Story = {{
  args: {{
    data: [],
  }},
}};

export const Error: Story = {{
  args: {{
    error: 'Failed to load data',
  }},
}};

STORYBOOK VALIDATION CHECKLIST:
──────────────────────────────────────
□ Story file created at correct location
□ All component states have stories
□ Props documented with argTypes
□ Component renders without console errors
□ Interactions work in Storybook
□ Accessibility checks pass (a11y addon)
□ Visual regression baseline captured

VERIFICATION COMMANDS:
──────────────────────────────────────
npm run storybook        # Start Storybook dev server
npm run storybook:build  # Build static Storybook
npm run test:storybook   # Run Storybook tests

ACCEPTANCE CRITERIA:
──────────────────────────────────────
- [ ] Storybook story file exists
- [ ] All states documented (default, loading, empty, error)
- [ ] No console errors in Storybook
- [ ] Component accessible via keyboard
- [ ] Visual appearance matches design
```
"""


def generate_testing_section(story: Story) -> str:
    """Generate testing requirements with AI prompts."""
    storybook_tests = ""
    if story.story_type == "frontend":
        storybook_tests = """
TIER 4 - STORYBOOK TESTS (mandatory for UI):
──────────────────────────────────────
- [ ] Storybook story file exists
- [ ] All component states have stories (default, loading, empty, error)
- [ ] No console errors in Storybook
- [ ] Accessibility checks pass (a11y addon)
- [ ] Visual regression test baseline captured
- [ ] Interactions work correctly in Storybook"""

    return f"""## Testing Requirements

### AI Implementation Prompt - Testing Strategy

```
TEST STRATEGY FOR {story.id}

RISK ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Impact if broken: {"HIGH" if story.priority == "P0" else "MEDIUM" if story.priority == "P1" else "LOW"}
Story type: {story.story_type}
Points: {story.points} (complexity indicator)

REQUIRED TESTS:

TIER 1 - UNIT TESTS (mandatory):
──────────────────────────────────────
{chr(10).join(f"- [ ] {ut}" for ut in story.unit_testing) if story.unit_testing else "- [ ] All public functions have unit tests"}

TIER 2 - INTEGRATION TESTS:
──────────────────────────────────────
{chr(10).join(f"- [ ] {it}" for it in story.integration_testing) if story.integration_testing else "- [ ] Integration tests for cross-service calls"}

TIER 3 - E2E TESTS:
──────────────────────────────────────
{chr(10).join(f"- [ ] {e2e}" for e2e in story.e2e_testing) if story.e2e_testing else "- [ ] E2E test for happy path"}
{storybook_tests}

VERIFICATION COMMAND:
{story.verification if story.verification else "cargo test / npm test"}
{"npm run storybook:build  # Verify Storybook builds" if story.story_type == "frontend" else ""}

FORBIDDEN:
- #[ignore] annotations
- .skip() in tests
- Tests without assertions
- Flaky tests
{"- Components without Storybook stories" if story.story_type == "frontend" else ""}
```
"""


def generate_done_checklist(story: Story) -> str:
    """Generate done checklist with AI prompts."""
    storybook_checks = ""
    if story.story_type == "frontend":
        storybook_checks = """
STORYBOOK CHECKS (MANDATORY FOR UI):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ SB-1: Storybook story file created
□ SB-2: Default story renders correctly
□ SB-3: Loading state story exists
□ SB-4: Empty state story exists
□ SB-5: Error state story exists
□ SB-6: No console errors in Storybook
□ SB-7: Accessibility (a11y) addon passes
□ SB-8: Component documented with argTypes
□ SB-9: Storybook builds successfully (npm run storybook:build)
"""

    return f"""## Done Checklist

### AI Implementation Prompt - Completion Verification

```
DONE CHECKLIST FOR {story.id}
Execute each check. ALL must pass.

ENGINEERING CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ ENG-1: Code compiles without errors
□ ENG-2: All functional requirements implemented
□ ENG-3: Code follows existing patterns
□ ENG-4: No hardcoded values

QUALITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f"□ {cq}" for cq in story.code_quality) if story.code_quality else "□ Code formatted and linted"}

SECURITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f"□ {sec}" for sec in story.security) if story.security else "□ No hardcoded secrets"}

OBSERVABILITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ OBS-1: Tracing spans added for key operations
□ OBS-2: Logs include correlation IDs
□ OBS-3: Metrics exposed if applicable
{storybook_checks}
FINAL VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ All tests passing
□ No TODO/FIXME without issue links
□ PR ready for review
{"□ Storybook story file included in PR" if story.story_type == "frontend" else ""}
```
"""


def generate_implementation_guide(story: Story) -> str:
    """Generate master implementation guide AI prompt."""
    return f"""## Implementation Guide - Master AI Prompt

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    {story.id}: {story.title[:50]}
║                         COMPLETE IMPLEMENTATION GUIDE
╚══════════════════════════════════════════════════════════════════════════════╝

MISSION BRIEFING:
You are implementing {story.id} for Armor Argus.
Epic: {story.epic_id} | Wave: {story.wave} | Sprint: {story.sprint}
Priority: {story.priority} | Points: {story.points}

DESCRIPTION:
{story.description}

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: SETUP & UNDERSTANDING (10-15 min)
═══════════════════════════════════════════════════════════════════════════════

1. Read and understand the story requirements
2. Identify target files and existing patterns
3. Review related code for consistency
4. Plan the implementation approach

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: IMPLEMENTATION ({story.points * 30} min estimated)
═══════════════════════════════════════════════════════════════════════════════

Implement each functional requirement:
{chr(10).join(f"- FR-{i+1}: {fr.name}" for i, fr in enumerate(story.functional_requirements))}

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: TESTING (20-30 min)
═══════════════════════════════════════════════════════════════════════════════

1. Write unit tests for new code
2. Run integration tests if applicable
3. Verify E2E scenarios
4. Check for console errors = 0

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: QUALITY & COMMIT (10 min)
═══════════════════════════════════════════════════════════════════════════════

1. Run linters and formatters
2. Verify no TODOs without issue links
3. Commit with conventional message
4. Create PR with evidence

═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA (all must be TRUE):
═══════════════════════════════════════════════════════════════════════════════

□ All functional requirements implemented
□ All tests passing (0 skipped, 0 ignored)
□ Code quality checks pass
□ PR includes verification evidence

ESTIMATED TIME: {story.points * 60} minutes
MAXIMUM TIME: {story.points * 120} minutes - if exceeding, ask for help

╔══════════════════════════════════════════════════════════════════════════════╗
║                              END OF GUIDE                                     ║
║           If anything is unclear, STOP and ask before proceeding.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
"""


def generate_story_markdown(story: Story) -> str:
    """Generate complete story markdown file."""
    labels_yaml = "\n".join(f"    - {label}" for label in story.labels)
    return f"""# {story.id}: {story.title}

## Story Metadata

```yaml
story:
  id: {story.id}
  title: "{story.title}"
  type: {story.story_type}
  status: ready

metadata:
  parent: {story.epic_jira_key}
  priority: {story.priority}
  points: {story.points}
  sprint: {story.sprint}
  wave: {story.wave}
  labels:
{labels_yaml}
  owner: TBD
  reviewers:
    - TBD
```

---

{generate_problem_statement(story)}

---

## Goal

{story.description}

Successfully implement all acceptance criteria with proper testing and documentation.

---

## Scope

### In Scope
{chr(10).join(f"- {fr.name}" for fr in story.functional_requirements)}

### Out of Scope
- Features not listed in functional requirements
- Future sprint enhancements
- Performance optimizations beyond SLAs

---

{generate_functional_requirements_section(story)}

---

{generate_storybook_section(story)}
{"---" if story.story_type == "frontend" else ""}

{generate_testing_section(story)}

---

{generate_done_checklist(story)}

---

## Acceptance Criteria

- [ ] All functional requirements met
- [ ] All tests passing (0 skipped)
- [ ] Code quality checks pass
- [ ] PR includes evidence
- [ ] Code merged to main branch
{f'''- [ ] Storybook story file created and documented
- [ ] All component states have Storybook stories
- [ ] No console errors in Storybook
- [ ] Storybook builds successfully''' if story.story_type == "frontend" else ""}

---

## Deployment Notes

### Target
- Kubernetes namespace: argus-system
- Story type: {story.story_type}

### Verification
{story.verification if story.verification else "Run tests and verify functionality"}

---

## Rollback Strategy

### Risk Assessment
- Database changes: Review before merge
- State introduced: Document any state changes
- Dependencies: List downstream impacts

### Rollback Command
```bash
git revert <commit-sha>
```

---

{generate_implementation_guide(story)}

---

## References

- Epic: {story.epic_id}
- PRD: .bmad/planning-artifacts/prd.md
- Architecture: docs/ARCHITECTURE_OVERVIEW.md

---

*Generated: {datetime.now().isoformat()}*
"""


def process_epic(epic_name: str, dry_run: bool = False) -> int:
    """Process a single epic and generate stories."""
    epic_path = EPICS_DIR / f"{epic_name}.md"

    if not epic_path.exists():
        print(f"  ERROR: Epic file not found: {epic_path}")
        return 0

    stories = parse_epic_file(epic_path)
    print(f"  Found {len(stories)} stories in {epic_name}")

    if dry_run:
        for story in stories[:3]:  # Show first 3 as preview
            print(f"    - {story.id}: {story.title} ({story.points} pts)")
        if len(stories) > 3:
            print(f"    ... and {len(stories) - 3} more")
        return len(stories)

    # Create output directory
    output_dir = OUTPUT_DIR / epic_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate story files
    for story in stories:
        story_file = output_dir / f"{story.id}.md"
        story_content = generate_story_markdown(story)
        story_file.write_text(story_content)
        print(f"    Generated: {story.id}")

    return len(stories)


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive story templates")
    parser.add_argument("--epic", help="Process single epic (e.g., EPIC-1-PLATFORM)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating files")
    args = parser.parse_args()

    print("=" * 60)
    print("Armor Argus - Comprehensive Story Generator")
    print("=" * 60)
    print()

    total_stories = 0

    if args.epic:
        # Process single epic
        print(f"Processing epic: {args.epic}")
        total_stories = process_epic(args.epic, args.dry_run)
    else:
        # Process all epics
        epic_files = sorted(EPICS_DIR.glob("EPIC-*.md"))
        print(f"Found {len(epic_files)} epic files")
        print()

        for epic_path in epic_files:
            epic_name = epic_path.stem
            print(f"Processing: {epic_name}")
            count = process_epic(epic_name, args.dry_run)
            total_stories += count
            print()

    print("=" * 60)
    print(f"Total stories: {total_stories}")
    if args.dry_run:
        print("(Dry run - no files generated)")
    else:
        print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
