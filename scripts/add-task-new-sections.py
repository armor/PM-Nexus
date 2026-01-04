#!/usr/bin/env python3
"""
Add new sections to existing task files:
1. Architecture References (after Context)
2. External Dependencies (after Architecture References)
3. Implementation Learnings (after Handoff Notes)

Run: python scripts/add-task-new-sections.py
"""

import re
from pathlib import Path

EPICS_DIR = Path(".bmad/epics")

ARCHITECTURE_SECTION = """
### Architecture References

| Document | Relevant Sections |
|----------|-------------------|
| [ARCHITECTURE_OVERVIEW.md](../../../../../docs/ARCHITECTURE_OVERVIEW.md) | Data flow, trust zones |
| [SECURITY_BOUNDARIES.md](../../../../../docs/SECURITY_BOUNDARIES.md) | Authentication, authorization |

### External Dependencies

| Dependency | Story | Status | Interface Used |
|------------|-------|--------|----------------|
| - | - | - | - |

*If external dependencies exist, coordinate with that story's owner before proceeding.*

"""

LEARNINGS_SECTION = """
## Implementation Learnings

*Populated after code review - feeds back into future task prompts*

| Issue Found | Root Cause | Prevention for Future |
|-------------|------------|----------------------|
| | | |

### Patterns Discovered
-

### Anti-Patterns Discovered
-

---

"""


def has_architecture_section(content: str) -> bool:
    """Check if file already has architecture references."""
    return "### Architecture References" in content


def has_learnings_section(content: str) -> bool:
    """Check if file already has implementation learnings."""
    return "## Implementation Learnings" in content


def add_sections_to_task(filepath: Path) -> bool:
    """Add new sections to a task file. Returns True if modified."""
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False

    # Add Architecture References after "### Context" and before "### This Task"
    if not has_architecture_section(content):
        # Find "### This Task" section
        this_task_match = re.search(r'\n### This Task\n', content)
        if this_task_match:
            insert_pos = this_task_match.start()
            content = content[:insert_pos] + ARCHITECTURE_SECTION + content[insert_pos:]
            modified = True

    # Add Implementation Learnings before "## Done When"
    if not has_learnings_section(content):
        done_match = re.search(r'\n## Done When\n', content)
        if done_match:
            insert_pos = done_match.start()
            content = content[:insert_pos] + LEARNINGS_SECTION + content[insert_pos:]
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

            for task_file in tasks_dir.glob("task-*.md"):
                stats['total'] += 1

                try:
                    if add_sections_to_task(task_file):
                        stats['modified'] += 1
                        print(f"  Modified: {task_file.relative_to(EPICS_DIR)}")
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"  Error processing {task_file}: {e}")

    return stats


def main():
    print("=" * 60)
    print("Adding New Sections to Task Files")
    print("=" * 60)
    print()
    print("Adding:")
    print("  - Architecture References")
    print("  - External Dependencies")
    print("  - Implementation Learnings")
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
