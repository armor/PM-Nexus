#!/usr/bin/env python3
"""
Add coordination fields to existing task files.

This script adds:
1. Coordination section (Requires, Unlocks, Claimed By, Claimed At, JIRA Key)
2. Handoff Notes section

Run: python scripts/add-task-coordination.py
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

EPICS_DIR = Path(".bmad/epics")

COORDINATION_SECTION = """
## Coordination

| Field | Value |
|-------|-------|
| Requires | {requires} |
| Unlocks | {unlocks} |
| Claimed By | |
| Claimed At | |
| JIRA Key | |

---
"""

HANDOFF_SECTION = """---

## Handoff Notes

*Populated on task completion for next task*

### What Was Built
-

### Files Created/Modified
| File | Action | Notes |
|------|--------|-------|

### Context for Next Task
-

"""


def extract_task_number(filename: str) -> int:
    """Extract task number from filename like task-01-foo.md -> 1"""
    match = re.search(r'task-(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def get_tasks_in_story(tasks_dir: Path) -> List[Tuple[int, str]]:
    """Get list of (task_num, filename) sorted by task number."""
    tasks = []
    if tasks_dir.exists():
        for f in tasks_dir.glob("task-*.md"):
            num = extract_task_number(f.name)
            tasks.append((num, f.name))
    return sorted(tasks, key=lambda x: x[0])


def compute_dependencies(task_num: int, all_tasks: List[Tuple[int, str]]) -> Tuple[str, str]:
    """
    Compute requires and unlocks for a task.

    Simple linear model: T1 -> T2 -> T3 -> ...
    T1 requires nothing, unlocks T2
    T2 requires T1, unlocks T3
    etc.
    """
    task_nums = [t[0] for t in all_tasks]

    # Find previous task
    prev_tasks = [n for n in task_nums if n < task_num]
    requires = f"T{max(prev_tasks)}" if prev_tasks else "none"

    # Find next task
    next_tasks = [n for n in task_nums if n > task_num]
    unlocks = f"T{min(next_tasks)}" if next_tasks else "none"

    return requires, unlocks


def has_coordination_section(content: str) -> bool:
    """Check if file already has coordination section."""
    return "## Coordination" in content and "Claimed By" in content


def has_handoff_section(content: str) -> bool:
    """Check if file already has handoff notes section."""
    return "## Handoff Notes" in content


def add_coordination_to_task(filepath: Path, requires: str, unlocks: str) -> bool:
    """Add coordination section to a task file. Returns True if modified."""
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    # Add Coordination section after Status line if missing
    if not has_coordination_section(content):
        # Find the position after "**Status:**" line
        status_match = re.search(r'\*\*Status:\*\*[^\n]*\n', content)
        if status_match:
            insert_pos = status_match.end()
            # Check if there's a --- separator
            if content[insert_pos:insert_pos+5] == '\n---\n':
                insert_pos += 5  # Skip past the separator
            elif content[insert_pos:insert_pos+4] == '---\n':
                insert_pos += 4

            coordination = COORDINATION_SECTION.format(requires=requires, unlocks=unlocks)
            content = content[:insert_pos] + coordination + content[insert_pos:]
            modified = True

    # Add Handoff Notes section before Done When if missing
    if not has_handoff_section(content):
        # Find "## Done When" section
        done_match = re.search(r'\n## Done When', content)
        if done_match:
            insert_pos = done_match.start()
            content = content[:insert_pos] + HANDOFF_SECTION + content[insert_pos:]
            modified = True
        else:
            # If no Done When section, add at end
            if not content.endswith('\n'):
                content += '\n'
            content += HANDOFF_SECTION + "\n## Done When\n\n- [ ] All acceptance criteria met\n- [ ] Handoff notes written\n"
            modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)

    return modified


def process_all_tasks():
    """Process all task files in all epics."""
    stats = {
        'total': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0
    }

    if not EPICS_DIR.exists():
        print(f"Error: {EPICS_DIR} does not exist")
        return stats

    for epic_dir in EPICS_DIR.iterdir():
        if not epic_dir.is_dir():
            continue

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in stories_dir.iterdir():
            if not story_dir.is_dir():
                continue

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            # Get all tasks in this story for dependency calculation
            all_tasks = get_tasks_in_story(tasks_dir)

            for task_num, task_filename in all_tasks:
                task_path = tasks_dir / task_filename
                stats['total'] += 1

                try:
                    requires, unlocks = compute_dependencies(task_num, all_tasks)

                    if add_coordination_to_task(task_path, requires, unlocks):
                        stats['modified'] += 1
                        print(f"  Modified: {task_path.relative_to(EPICS_DIR)}")
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"  Error processing {task_path}: {e}")

    return stats


def main():
    print("=" * 60)
    print("Adding Coordination Fields to Task Files")
    print("=" * 60)
    print()

    stats = process_all_tasks()

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total task files:  {stats['total']}")
    print(f"Modified:          {stats['modified']}")
    print(f"Skipped (already): {stats['skipped']}")
    print(f"Errors:            {stats['errors']}")


if __name__ == "__main__":
    main()
