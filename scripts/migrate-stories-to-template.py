#!/usr/bin/env python3
"""
Story Template Migration Script

Migrates existing epic stories to the STORY-TEMPLATE.md specification.
Adds missing header fields and 8 AC categories.

Usage:
    python scripts/migrate-stories-to-template.py [--dry-run] [--epic EPIC_FILE]

Options:
    --dry-run       Preview changes without writing files
    --epic FILE     Process a single epic file instead of all
    --backup        Create .bak files before modifying
"""

import argparse
import re
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

# Epic to team/worktree mapping
EPIC_TEAM_MAP = {
    "EPIC-1": ("ARGUS-PLATFORM", "team-platform"),
    "EPIC-2": ("ARGUS-GRAPH", "team-graph"),
    "EPIC-3": ("ARGUS-RISK", "team-risk"),
    "EPIC-4": ("ARGUS-AUTOMATION", "team-automation"),
    "EPIC-5": ("ARGUS-UX", "team-ux"),
    "EPIC-6": ("ARGUS-INTEGRATION", "team-integration"),
    "EPIC-7": ("ARGUS-PLATFORM", "team-platform"),
    "EPIC-8": ("ARGUS-UX", "team-ux"),
    "EPIC-9": ("ARGUS-AUTOMATION", "team-automation"),
    "EPIC-10": ("ARGUS-PLATFORM", "team-platform"),
    "EPIC-AUTH": ("ARGUS-INTEGRATION", "team-integration"),
}

# Story ID prefix to epic mapping
STORY_PREFIX_MAP = {
    "PLAT": "EPIC-1",
    "GRAPH": "EPIC-2",
    "RISK": "EPIC-3",
    "AUTO": "EPIC-4",
    "REM": "EPIC-4",
    "UX": "EPIC-5",
    "ONBOARD": "EPIC-5",
    "INT": "EPIC-6",
    "AUTH": "EPIC-6",
    "SCAN": "EPIC-6",
    "WHATIF": "EPIC-7",
    "SIM": "EPIC-7",
    "EXEC": "EPIC-8",
    "COMP": "EPIC-8",
    "POLICY": "EPIC-9",
    "OPS": "EPIC-10",
    "SRE": "EPIC-10",
    "STORY": "EPIC-AUTH",  # For EPIC-AUTH-001 stories
}

@dataclass
class Story:
    """Represents a parsed story"""
    story_id: str
    title: str
    points: int = 3
    wave: int = 1
    sprint: int = 1
    priority: str = "P0"
    mvp: int = 1
    interface: str = "N/A"
    team: str = ""
    worktree: str = ""
    description: str = ""
    original_acs: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    verification: str = ""
    is_frontend: bool = False
    story_type: str = "standard"  # standard, validation, contract, summary


def infer_wave_from_sprint(sprint: int) -> int:
    """Infer wave number from sprint (2 sprints per wave)"""
    return max(1, (sprint + 1) // 2)


def infer_team_from_story_id(story_id: str, epic_file: str) -> tuple:
    """Infer team and worktree from story ID or epic file"""
    # First try to match story prefix
    for prefix, epic in STORY_PREFIX_MAP.items():
        if story_id.upper().startswith(prefix):
            if epic in EPIC_TEAM_MAP:
                return EPIC_TEAM_MAP[epic]

    # Fallback to epic file name
    epic_name = Path(epic_file).stem.upper()
    for epic_key in EPIC_TEAM_MAP:
        if epic_key in epic_name:
            return EPIC_TEAM_MAP[epic_key]

    # Default
    return ("ARGUS-PLATFORM", "team-platform")


def is_frontend_story(story: Story) -> bool:
    """Determine if story is frontend (needs UI/UX testing)"""
    frontend_keywords = [
        "ui", "frontend", "component", "page", "screen", "dashboard",
        "form", "button", "modal", "drawer", "table", "chart",
        "visualization", "react", "storybook", "css", "style"
    ]
    text = f"{story.title} {story.description}".lower()
    return any(kw in text for kw in frontend_keywords)


def parse_story_header(line: str) -> Optional[tuple]:
    """Parse story header line to extract ID and title"""
    # Match patterns like:
    # #### PLAT-001: Title
    # #### STORY-001: Title (S)
    # #### GRAPH-001: Resource Tag Definition
    match = re.match(r'^#{3,4}\s+([A-Z]+-\d+[a-z]?):\s*(.+?)(?:\s*\([SML]\))?\s*$', line)
    if match:
        return match.group(1), match.group(2).strip()
    return None


def parse_existing_story(lines: List[str], start_idx: int, epic_file: str) -> tuple:
    """Parse an existing story block and return Story object and end index"""
    header = parse_story_header(lines[start_idx])
    if not header:
        return None, start_idx

    story_id, title = header
    story = Story(story_id=story_id, title=title)

    # Get team from epic
    story.team, story.worktree = infer_team_from_story_id(story_id, epic_file)

    i = start_idx + 1
    current_section = None

    while i < len(lines):
        line = lines[i].rstrip()

        # Check for next story or section break
        if line.startswith('#### ') or line.startswith('### ') or line.startswith('## '):
            break

        # Parse metadata line
        if line.startswith('**Points:**'):
            # Parse: **Points:** 3 | **Sprint:** 1 | **Priority:** P0 | **MVP:** 1
            points_match = re.search(r'\*\*Points:\*\*\s*(\d+)', line)
            sprint_match = re.search(r'\*\*Sprint:\*\*\s*(\d+)', line)
            priority_match = re.search(r'\*\*Priority:\*\*\s*(P\d)', line)
            mvp_match = re.search(r'\*\*MVP:\*\*\s*(\d)', line)
            wave_match = re.search(r'\*\*Wave:\*\*\s*(\d+)', line)

            if points_match:
                story.points = int(points_match.group(1))
            if sprint_match:
                story.sprint = int(sprint_match.group(1))
            if priority_match:
                story.priority = priority_match.group(1)
            if mvp_match:
                story.mvp = int(mvp_match.group(1))
            if wave_match:
                story.wave = int(wave_match.group(1))
            else:
                story.wave = infer_wave_from_sprint(story.sprint)

        # Parse sections
        elif line.startswith('**Acceptance Criteria:**') or line.startswith('**AC:**'):
            current_section = 'ac'
        elif line.startswith('**Tasks:**'):
            current_section = 'tasks'
        elif line.startswith('**Verification:**'):
            current_section = 'verification'
            # Check if inline verification
            if ':' in line and line.index(':') < len(line) - 1:
                story.verification = line.split(':', 1)[1].strip().strip('`')
        elif line.startswith('**'):
            current_section = None

        # Collect content based on section
        elif current_section == 'ac' and line.strip().startswith('- '):
            ac_item = line.strip()[2:].strip()
            if ac_item.startswith('[ ] '):
                ac_item = ac_item[4:]
            story.original_acs.append(ac_item)
        elif current_section == 'tasks' and line.strip().startswith('- '):
            task_item = line.strip()[2:].strip()
            if task_item.startswith('[ ] '):
                task_item = task_item[4:]
            story.tasks.append(task_item)
        elif current_section == 'verification' and line.strip() and not story.verification:
            story.verification = line.strip().strip('`')

        # Description (first non-metadata line after header)
        elif not story.description and line.strip() and not line.startswith('**'):
            story.description = line.strip()

        i += 1

    # Determine if frontend story
    story.is_frontend = is_frontend_story(story)

    return story, i


def generate_functional_requirements(story: Story) -> List[str]:
    """Generate FUNC- requirements from original ACs or tasks"""
    func_items = []

    # Use original ACs if available, otherwise use tasks
    source = story.original_acs if story.original_acs else story.tasks

    for idx, item in enumerate(source[:5], 1):  # Max 5 FUNC items
        # Clean up the item
        item = item.strip()
        if item.startswith('[ ] '):
            item = item[4:]
        func_items.append(f"FUNC-{idx}: {item}")

    # If no items, create placeholder based on title
    if not func_items:
        func_items.append(f"FUNC-1: {story.title} works as specified")
        func_items.append(f"FUNC-2: Edge cases handled correctly")

    return func_items


def format_story_to_template(story: Story) -> str:
    """Format a story to the new template specification"""

    # Generate functional requirements
    func_reqs = generate_functional_requirements(story)

    # Build the story output
    output = []

    # Header
    output.append(f"#### {story.story_id}: {story.title}")
    output.append(f"**Points:** {story.points} | **Wave:** {story.wave} | **Sprint:** {story.sprint} | **Priority:** {story.priority} | **MVP:** {story.mvp}")
    output.append(f"**Interface:** {story.interface}")
    output.append(f"**Team:** {story.team}")
    output.append(f"**Worktree:** {story.worktree}")
    output.append("")

    # Description
    if story.description:
        output.append(story.description)
    else:
        output.append(f"Implement {story.title.lower()}.")
    output.append("")

    # Functional Requirements
    output.append("**Functional Requirements:**")
    for func in func_reqs:
        output.append(f"- [ ] {func}")
    output.append("")

    # Code Quality
    output.append("**Code Quality:**")
    output.append("- [ ] CQ-1: No clippy warnings (`cargo clippy -- -D warnings`)")
    output.append("- [ ] CQ-2: Code formatted (`cargo fmt --check`)")
    output.append("- [ ] CQ-3: No TODO/FIXME without linked issue")
    output.append("- [ ] CQ-4: Functions < 50 lines")
    output.append("- [ ] CQ-5: Cyclomatic complexity < 10")
    output.append("")

    # Security
    output.append("**Security:**")
    output.append("- [ ] SEC-1: No hardcoded secrets (gitleaks passes)")
    output.append("- [ ] SEC-2: Input validation on external inputs")
    output.append("- [ ] SEC-3: SQL/injection prevention")
    output.append("- [ ] SEC-4: Auth required for endpoints")
    output.append("- [ ] SEC-5: Authorization check before data access")
    output.append("- [ ] SEC-6: Sensitive data not logged")
    output.append("")

    # Interface Adherence
    output.append("**Interface Adherence:**")
    if story.interface != "N/A":
        output.append(f"- [ ] INT-1: Implements {story.interface} trait exactly")
        output.append("- [ ] INT-2: Error types match contract spec")
        output.append("- [ ] INT-3: No extra public methods beyond contract")
        output.append("- [ ] INT-4: Contract version documented")
        output.append("- [ ] INT-5: Breaking changes via RFC")
    else:
        output.append("- [ ] INT-1: N/A (no interface contract)")
    output.append("")

    # Unit Testing
    output.append("**Unit Testing:**")
    output.append("- [ ] UT-1: All public functions have unit tests")
    output.append("- [ ] UT-2: Coverage > 80% for new code")
    output.append("- [ ] UT-3: Edge cases tested (empty, null, max)")
    output.append("- [ ] UT-4: Error paths tested")
    output.append("- [ ] UT-5: Mocks for external dependencies")
    output.append("- [ ] UT-6: No skipped tests (`#[ignore]` forbidden)")
    output.append("")

    # Integration Testing
    output.append("**Integration Testing:**")
    output.append("- [ ] IT-1: API endpoint tested with real HTTP")
    output.append("- [ ] IT-2: Database ops tested with test DB")
    output.append("- [ ] IT-3: Cross-service calls tested")
    output.append("- [ ] IT-4: Circuit breaker behavior tested")
    output.append("- [ ] IT-5: Retry logic tested")
    output.append("- [ ] IT-6: No skipped tests")
    output.append("")

    # E2E Testing
    output.append("**E2E Testing:**")
    output.append("- [ ] E2E-1: Happy path scenario automated")
    output.append("- [ ] E2E-2: API response verified (status + body)")
    output.append("- [ ] E2E-3: Data persistence verified (reload test)")
    output.append("- [ ] E2E-4: Console errors captured (must be zero)")
    output.append("- [ ] E2E-5: Performance within SLA (< 500ms p95)")
    output.append("- [ ] E2E-6: No skipped tests")
    output.append("")

    # UI/UX Testing (frontend only)
    if story.is_frontend:
        output.append("**UI Testing:**")
        output.append("- [ ] UI-1: Component renders without errors")
        output.append("- [ ] UI-2: Responsive at 320px, 768px, 1024px, 1440px")
        output.append("- [ ] UI-3: Keyboard navigation works")
        output.append("- [ ] UI-4: Screen reader compatible (ARIA)")
        output.append("- [ ] UI-5: Loading/error/empty states render")
        output.append("- [ ] UI-6: Visual regression baseline captured")
        output.append("- [ ] UI-7: No skipped tests")
        output.append("")

        output.append("**UX Testing:**")
        output.append("- [ ] UX-1: Matches approved design")
        output.append("- [ ] UX-2: Flow completes in < 3 clicks")
        output.append("- [ ] UX-3: Error messages actionable")
        output.append("- [ ] UX-4: Success feedback visible")
        output.append("- [ ] UX-5: No dead ends in flow")
        output.append("- [ ] UX-6: Undo for destructive actions")
        output.append("")
    else:
        output.append("**UI Testing:** N/A (backend story)")
        output.append("")
        output.append("**UX Testing:** N/A (backend story)")
        output.append("")

    # Verification
    output.append("**Verification:**")
    if story.verification:
        output.append(f"- Command: `{story.verification}`")
    else:
        output.append(f"- Command: `cargo test {story.story_id.lower().replace('-', '_')}::`")
    output.append("- Expected: All tests pass, 0 skipped")
    output.append(f"- E2E Test: `tests/e2e/{story.story_id.lower()}.spec.ts`")
    output.append("")
    output.append("---")

    return "\n".join(output)


def process_epic_file(filepath: str, dry_run: bool = False, backup: bool = False) -> Dict:
    """Process a single epic file and migrate all stories"""

    print(f"\nProcessing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Find all stories
    stories = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#### ') and parse_story_header(lines[i]):
            story, end_idx = parse_existing_story(lines, i, filepath)
            if story:
                stories.append((i, end_idx, story))
            i = end_idx
        else:
            i += 1

    print(f"  Found {len(stories)} stories")

    if dry_run:
        # Just show what would be changed
        for start, end, story in stories[:3]:  # Show first 3 as preview
            print(f"  - {story.story_id}: {story.title}")
            print(f"    Points: {story.points}, Sprint: {story.sprint}, Wave: {story.wave}")
            print(f"    Team: {story.team}, Frontend: {story.is_frontend}")
            print(f"    Original ACs: {len(story.original_acs)}")
        if len(stories) > 3:
            print(f"  ... and {len(stories) - 3} more stories")
        return {"file": filepath, "stories": len(stories), "migrated": 0, "dry_run": True}

    # Build new content
    new_lines = []
    last_end = 0

    for start, end, story in stories:
        # Add content before this story
        new_lines.extend(lines[last_end:start])

        # Add migrated story
        new_lines.append(format_story_to_template(story))

        last_end = end

    # Add remaining content
    new_lines.extend(lines[last_end:])

    new_content = '\n'.join(new_lines)

    # Remove excessive blank lines
    new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)

    # Backup if requested
    if backup:
        backup_path = filepath + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Backup saved to: {backup_path}")

    # Write new content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  Migrated {len(stories)} stories")

    return {"file": filepath, "stories": len(stories), "migrated": len(stories), "dry_run": False}


def main():
    parser = argparse.ArgumentParser(description='Migrate stories to STORY-TEMPLATE.md specification')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--epic', type=str, help='Process single epic file')
    parser.add_argument('--backup', action='store_true', help='Create .bak files before modifying')

    args = parser.parse_args()

    # Find epic files
    epics_dir = Path(__file__).parent.parent / '.bmad' / 'planning-artifacts' / 'epics'

    if args.epic:
        epic_files = [Path(args.epic)]
    else:
        epic_files = list(epics_dir.glob('EPIC-*.md'))

    if not epic_files:
        print("No epic files found!")
        sys.exit(1)

    print("=" * 60)
    print("Story Template Migration Script")
    print("=" * 60)
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Files: {len(epic_files)}")
    print("=" * 60)

    results = []
    total_stories = 0
    total_migrated = 0

    for epic_file in sorted(epic_files):
        result = process_epic_file(str(epic_file), args.dry_run, args.backup)
        results.append(result)
        total_stories += result['stories']
        total_migrated += result['migrated']

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Epic files processed: {len(results)}")
    print(f"Total stories found: {total_stories}")
    print(f"Stories migrated: {total_migrated}")

    if args.dry_run:
        print("\nThis was a DRY RUN. No files were modified.")
        print("Run without --dry-run to apply changes.")


if __name__ == '__main__':
    main()
