#!/usr/bin/env python3
"""
Add Tasks and Subtasks to Verbose Stories

Adds a ## Tasks section to existing verbose story files with:
- Tasks derived from Functional Requirements (FR-*)
- Subtasks for implementation steps

Preserves ALL existing content (AI prompts, etc.)

Usage:
  python scripts/add-tasks-to-stories.py --dry-run           # Preview
  python scripts/add-tasks-to-stories.py --epic EPIC-5-UX    # Single epic
  python scripts/add-tasks-to-stories.py                     # All epics
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
STORIES_DIR = PROJECT_ROOT / ".bmad/generated-stories"


def extract_functional_requirements(content: str) -> List[Dict]:
    """Extract FR-* requirements from story content."""
    frs = []

    # Find FR sections with their content
    fr_pattern = r'### FR-(\d+): (.+?)(?=\n### FR-|\n---|\n## [A-Z]|\Z)'
    matches = re.findall(fr_pattern, content, re.DOTALL)

    for fr_num, fr_content in matches:
        # Get the title (first line)
        lines = fr_content.strip().split('\n')
        title = lines[0].strip() if lines else f"Functional Requirement {fr_num}"

        # Look for acceptance criteria checkboxes
        criteria = re.findall(r'- \[[ x]\] (.+?)$', fr_content, re.MULTILINE)

        frs.append({
            "id": f"FR-{fr_num}",
            "num": int(fr_num),
            "title": title[:80],
            "criteria": criteria[:5]  # Max 5 per FR
        })

    return frs


def extract_scope_items(content: str) -> List[str]:
    """Extract In Scope items as backup for tasks."""
    scope_match = re.search(r'### In Scope\s+(.+?)(?=\n###|\n---|\n## )', content, re.DOTALL)
    if scope_match:
        items = re.findall(r'^- (.+)$', scope_match.group(1), re.MULTILINE)
        return [item.strip()[:80] for item in items[:8]]
    return []


def generate_tasks_section(story_id: str, frs: List[Dict], scope_items: List[str]) -> str:
    """Generate a Tasks section with subtasks."""
    lines = [
        "",
        "---",
        "",
        "## Tasks",
        "",
        "<!-- JIRA SYNC: Tasks below will be synced as JIRA Tasks, subtasks as Sub-tasks -->",
        ""
    ]

    # Strategy 1: Use Functional Requirements as tasks
    if frs:
        for i, fr in enumerate(frs, 1):
            task_id = f"T{i}"
            lines.append(f"### {story_id}-{task_id}: {fr['title']}")
            lines.append(f"**Linked to:** {fr['id']}")
            lines.append("")
            lines.append("| Subtask | Description | Status |")
            lines.append("|---------|-------------|--------|")

            # Add subtasks from acceptance criteria
            if fr["criteria"]:
                for j, crit in enumerate(fr["criteria"], 1):
                    lines.append(f"| {task_id}-S{j} | {crit[:60]} | pending |")
            else:
                # Default subtasks
                lines.append(f"| {task_id}-S1 | Implement {fr['title'][:40]} | pending |")
                lines.append(f"| {task_id}-S2 | Write unit tests | pending |")
                lines.append(f"| {task_id}-S3 | Integration test | pending |")

            lines.append("")

    # Strategy 2: Use scope items if no FRs
    elif scope_items:
        for i, scope in enumerate(scope_items, 1):
            task_id = f"T{i}"
            lines.append(f"### {story_id}-{task_id}: {scope}")
            lines.append("")
            lines.append("| Subtask | Description | Status |")
            lines.append("|---------|-------------|--------|")
            lines.append(f"| {task_id}-S1 | Implement: {scope[:40]} | pending |")
            lines.append(f"| {task_id}-S2 | Write tests | pending |")
            lines.append(f"| {task_id}-S3 | Documentation | pending |")
            lines.append("")

    # Strategy 3: Default tasks
    else:
        lines.append(f"### {story_id}-T1: Implementation")
        lines.append("")
        lines.append("| Subtask | Description | Status |")
        lines.append("|---------|-------------|--------|")
        lines.append("| T1-S1 | Core implementation | pending |")
        lines.append("| T1-S2 | Unit tests | pending |")
        lines.append("| T1-S3 | Integration tests | pending |")
        lines.append("")

    # Always add final verification task
    final_task = f"T{len(frs) + 1 if frs else len(scope_items) + 1 if scope_items else 2}"
    lines.extend([
        f"### {story_id}-{final_task}: Verification & Documentation",
        "",
        "| Subtask | Description | Status |",
        "|---------|-------------|--------|",
        f"| {final_task}-S1 | Run all tests | pending |",
        f"| {final_task}-S2 | Code review prep | pending |",
        f"| {final_task}-S3 | Update documentation | pending |",
        "",
    ])

    return "\n".join(lines)


def has_tasks_section(content: str) -> bool:
    """Check if story already has a Tasks section."""
    return bool(re.search(r'^## Tasks\s*$', content, re.MULTILINE))


def add_tasks_to_story(filepath: Path, dry_run: bool = False) -> Optional[int]:
    """Add Tasks section to a story file. Returns number of tasks added."""
    content = filepath.read_text()

    # Skip if already has Tasks
    if has_tasks_section(content):
        return None

    # Extract story ID
    id_match = re.search(r'^# ([A-Z]+-\d+):', content, re.MULTILINE)
    if not id_match:
        return None
    story_id = id_match.group(1)

    # Extract requirements and scope
    frs = extract_functional_requirements(content)
    scope_items = extract_scope_items(content)

    # Generate Tasks section
    tasks_section = generate_tasks_section(story_id, frs, scope_items)
    task_count = len(frs) if frs else len(scope_items) if scope_items else 1
    task_count += 1  # Add verification task

    # Find insertion point (before ## References or at end)
    insertion_patterns = [
        r'\n## References\s*\n',
        r'\n---\s*\n\*Enhanced:',
        r'\Z'
    ]

    for pattern in insertion_patterns:
        match = re.search(pattern, content)
        if match:
            new_content = content[:match.start()] + tasks_section + content[match.start():]
            break
    else:
        new_content = content + tasks_section

    if dry_run:
        return task_count
    else:
        filepath.write_text(new_content)
        return task_count


def process_epic(epic_dir: Path, dry_run: bool = False) -> Dict:
    """Process all stories in an epic directory."""
    results = {"updated": 0, "skipped": 0, "tasks_added": 0}

    story_files = sorted(epic_dir.glob("*.md"))

    for story_file in story_files:
        if story_file.name == "README.md":
            continue

        task_count = add_tasks_to_story(story_file, dry_run)

        if task_count is None:
            results["skipped"] += 1
            print(f"    [SKIP] {story_file.name} (already has Tasks)")
        else:
            results["updated"] += 1
            results["tasks_added"] += task_count
            action = "[DRY]" if dry_run else "✓"
            print(f"    {action} {story_file.name}: +{task_count} tasks")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add Tasks section to verbose stories")
    parser.add_argument("--dry-run", action="store_true", help="Preview without modifying")
    parser.add_argument("--epic", type=str, help="Process single epic")
    parser.add_argument("--show", type=str, help="Show generated Tasks for one story file")
    args = parser.parse_args()

    if args.show:
        # Show what would be generated for a specific file
        filepath = Path(args.show)
        if not filepath.exists():
            filepath = STORIES_DIR / args.show
        if filepath.exists():
            content = filepath.read_text()
            id_match = re.search(r'^# ([A-Z]+-\d+):', content, re.MULTILINE)
            story_id = id_match.group(1) if id_match else "STORY"
            frs = extract_functional_requirements(content)
            scope = extract_scope_items(content)
            tasks = generate_tasks_section(story_id, frs, scope)
            print("=" * 60)
            print(f"Generated Tasks for {filepath.name}")
            print("=" * 60)
            print(tasks)
        return

    print("=" * 60)
    print("ADD TASKS TO VERBOSE STORIES")
    print(f"Directory: {STORIES_DIR}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)

    if not STORIES_DIR.exists():
        print(f"ERROR: Stories directory not found: {STORIES_DIR}")
        return

    total = {"updated": 0, "skipped": 0, "tasks_added": 0}

    epic_dirs = sorted([d for d in STORIES_DIR.iterdir() if d.is_dir()])

    for epic_dir in epic_dirs:
        if args.epic and args.epic not in epic_dir.name:
            continue

        print(f"\n  Processing {epic_dir.name}...")
        results = process_epic(epic_dir, args.dry_run)
        total["updated"] += results["updated"]
        total["skipped"] += results["skipped"]
        total["tasks_added"] += results["tasks_added"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Stories updated: {total['updated']}")
    print(f"Stories skipped: {total['skipped']} (already have Tasks)")
    print(f"Total tasks added: {total['tasks_added']}")


if __name__ == "__main__":
    main()
