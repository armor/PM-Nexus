#!/usr/bin/env python3
"""
Add coordination fields to existing story files.

This script adds:
1. Coordination section (Worktree, Branch, Depends On, Blocks, JIRA Key, Task Execution Order)

Run: python scripts/add-story-coordination.py
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

EPICS_DIR = Path(".bmad/epics")


def extract_story_number(folder_name: str) -> Tuple[int, str]:
    """Extract story number and letter suffix from folder like 01-foo or 02a-foo."""
    match = re.match(r'^(\d+)([a-z])?-(.+)$', folder_name)
    if match:
        num = int(match.group(1))
        letter = match.group(2) or ""
        slug = match.group(3)
        return num, letter, slug
    return 0, "", folder_name


def get_stories_in_epic(epic_dir: Path) -> List[Tuple[int, str, str, Path]]:
    """Get list of (story_num, letter, slug, path) sorted by number."""
    stories = []
    stories_dir = epic_dir / "stories"
    if stories_dir.exists():
        for d in stories_dir.iterdir():
            if d.is_dir():
                num, letter, slug = extract_story_number(d.name)
                stories.append((num, letter, slug, d))
    return sorted(stories, key=lambda x: (x[0], x[1]))


def extract_repo_from_target_files(story_dir: Path) -> str:
    """Try to extract repo name from task target files."""
    tasks_dir = story_dir / "tasks"
    if not tasks_dir.exists():
        return "argus-common"  # Default

    for task_file in tasks_dir.glob("task-*.md"):
        with open(task_file, 'r') as f:
            content = f.read()
        # Look for submodules/argus-XXX in target files
        match = re.search(r'submodules/(argus-\w+)', content)
        if match:
            return match.group(1)

    return "argus-common"  # Default


def compute_task_order(story_dir: Path) -> str:
    """Compute task execution order from tasks in the story."""
    tasks_dir = story_dir / "tasks"
    if not tasks_dir.exists():
        return "T1"

    task_nums = []
    for f in tasks_dir.glob("task-*.md"):
        match = re.search(r'task-(\d+)', f.name)
        if match:
            task_nums.append(int(match.group(1)))

    task_nums.sort()

    if len(task_nums) == 0:
        return "T1"
    elif len(task_nums) == 1:
        return f"T{task_nums[0]}"
    else:
        # Simple linear order: T1 -> T2 -> T3 -> ...
        return " -> ".join([f"T{n}" for n in task_nums])


def compute_story_dependencies(story_num: int, letter: str, all_stories: List[Tuple[int, str, str, Path]]) -> Tuple[str, str]:
    """
    Compute depends_on and blocks for a story.

    Simple linear model for numbered stories.
    Letter suffixes (2a, 2b) are considered parallel.
    """
    # Group by number
    stories_by_num = {}
    for num, l, slug, path in all_stories:
        if num not in stories_by_num:
            stories_by_num[num] = []
        stories_by_num[num].append((l, slug))

    # Current story's group size
    current_group = stories_by_num.get(story_num, [])
    is_parallel = len(current_group) > 1

    # Previous story number
    prev_nums = [n for n in stories_by_num.keys() if n < story_num]
    depends_on = "-"
    if prev_nums:
        prev_num = max(prev_nums)
        prev_group = stories_by_num[prev_num]
        if len(prev_group) == 1:
            depends_on = f"S{prev_num}"
        else:
            # Depends on all parallel stories from previous group
            depends_on = ", ".join([f"S{prev_num}{l}" for l, _ in prev_group])

    # Next story number
    next_nums = [n for n in stories_by_num.keys() if n > story_num]
    blocks = "-"
    if next_nums:
        next_num = min(next_nums)
        next_group = stories_by_num[next_num]
        if len(next_group) == 1:
            blocks = f"S{next_num}"
        else:
            # Blocks all parallel stories in next group
            blocks = ", ".join([f"S{next_num}{l}" for l, _ in next_group])

    return depends_on, blocks


def has_coordination_section(content: str) -> bool:
    """Check if file already has coordination section."""
    return "## Coordination" in content and "Worktree" in content


def generate_coordination_section(story_dir: Path, slug: str, depends_on: str, blocks: str, task_order: str) -> str:
    """Generate the coordination section content."""
    repo = extract_repo_from_target_files(story_dir)

    return f"""
## Coordination

| Field | Value |
|-------|-------|
| Worktree | `worktrees/{repo}-{slug}` |
| Branch | `{slug}` |
| Depends On | {depends_on} |
| Blocks | {blocks} |
| JIRA Key | |

### Task Execution Order

```
{task_order}
```

---
"""


def add_coordination_to_story(story_file: Path, story_dir: Path, slug: str, depends_on: str, blocks: str) -> bool:
    """Add coordination section to a story file. Returns True if modified."""
    with open(story_file, 'r') as f:
        content = f.read()

    if has_coordination_section(content):
        return False

    # Find position after Status line
    status_match = re.search(r'\*\*Status:\*\*[^\n]*\n', content)
    if not status_match:
        return False

    insert_pos = status_match.end()
    # Skip past any --- separator
    remaining = content[insert_pos:]
    if remaining.startswith('\n---\n'):
        insert_pos += 5
    elif remaining.startswith('---\n'):
        insert_pos += 4

    task_order = compute_task_order(story_dir)
    coordination = generate_coordination_section(story_dir, slug, depends_on, blocks, task_order)

    content = content[:insert_pos] + coordination + content[insert_pos:]

    with open(story_file, 'w') as f:
        f.write(content)

    return True


def process_all_stories():
    """Process all story files in all epics."""
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

        # Get all stories in this epic for dependency calculation
        all_stories = get_stories_in_epic(epic_dir)

        for story_num, letter, slug, story_dir in all_stories:
            # Find story file
            story_file = story_dir / f"story-{story_dir.name}.md"
            if not story_file.exists():
                # Try older naming
                for f in story_dir.glob("story-*.md"):
                    story_file = f
                    break

            if not story_file.exists():
                continue

            stats['total'] += 1

            try:
                depends_on, blocks = compute_story_dependencies(story_num, letter, all_stories)
                full_slug = f"{story_num:02d}{letter}-{slug}"

                if add_coordination_to_story(story_file, story_dir, full_slug, depends_on, blocks):
                    stats['modified'] += 1
                    print(f"  Modified: {story_file.relative_to(EPICS_DIR)}")
                else:
                    stats['skipped'] += 1
            except Exception as e:
                stats['errors'] += 1
                print(f"  Error processing {story_file}: {e}")

    return stats


def main():
    print("=" * 60)
    print("Adding Coordination Fields to Story Files")
    print("=" * 60)
    print()

    stats = process_all_stories()

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total story files:  {stats['total']}")
    print(f"Modified:           {stats['modified']}")
    print(f"Skipped (already):  {stats['skipped']}")
    print(f"Errors:             {stats['errors']}")


if __name__ == "__main__":
    main()
