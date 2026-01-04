#!/usr/bin/env python3
"""
Reset task references from JIRA keys back to task IDs (T1, T2 format).
This is needed before a fresh sync when JIRA was cleared.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

def extract_story_id(content: str) -> str:
    """Extract story ID from task content."""
    match = re.search(r'\*\*Story:\*\*\s*([A-Z]+-\d+-\d+[a-z]?)', content)
    return match.group(1) if match else ""

def extract_task_num(content: str) -> str:
    """Extract task number from task header."""
    match = re.search(r'^#\s+[A-Z]+-\d+-\d+[a-z]?-(T\d+):', content, re.MULTILINE)
    return match.group(1) if match else ""

def reset_refs(file_path: Path) -> bool:
    """Reset JIRA key refs to task ID refs. Returns True if changed."""
    content = file_path.read_text()
    original = content

    story_id = extract_story_id(content)
    task_num = extract_task_num(content)

    if not story_id or not task_num:
        return False

    # Get the task number as int
    task_int = int(task_num[1:])  # T3 -> 3

    # Reset Requires to previous task or "none"
    if task_int == 1:
        content = re.sub(
            r'(\|\s*Requires\s*\|\s*)[^|]+(\|)',
            r'\1none \2',
            content
        )
    else:
        prev_task = f"T{task_int - 1}"
        content = re.sub(
            r'(\|\s*Requires\s*\|\s*)[^|]+(\|)',
            f'\\1{prev_task} \\2',
            content
        )

    # Reset Unlocks to next task or "none"
    # We don't know the max task, so just increment
    next_task = f"T{task_int + 1}"
    # Check if this is the last task by looking for "none" pattern later
    # For now, just set to next task - we'll fix last tasks manually or detect them

    if content != original:
        file_path.write_text(content)
        return True
    return False

def main():
    print("Resetting task references to task IDs (T1, T2 format)...")

    reset_count = 0

    for epic_dir in sorted(EPICS_DIR.iterdir()):
        if not epic_dir.is_dir():
            continue

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            # Get all task files to know the max
            task_files = sorted(tasks_dir.glob("task-*.md"))
            max_task = len(task_files)

            for task_file in task_files:
                content = task_file.read_text()
                original = content

                task_num_match = re.search(r'^#\s+[A-Z]+-\d+-\d+[a-z]?-(T\d+):', content, re.MULTILINE)
                if not task_num_match:
                    continue

                task_int = int(task_num_match.group(1)[1:])

                # Reset Requires
                if task_int == 1:
                    content = re.sub(
                        r'(\|\s*Requires\s*\|\s*)[^|]+(\|)',
                        r'\1none \2',
                        content
                    )
                else:
                    content = re.sub(
                        r'(\|\s*Requires\s*\|\s*)[^|]+(\|)',
                        f'\\1T{task_int - 1} \\2',
                        content
                    )

                # Reset Unlocks
                if task_int == max_task:
                    content = re.sub(
                        r'(\|\s*Unlocks\s*\|\s*)[^|]+(\|)',
                        r'\1none \2',
                        content
                    )
                else:
                    content = re.sub(
                        r'(\|\s*Unlocks\s*\|\s*)[^|]+(\|)',
                        f'\\1T{task_int + 1} \\2',
                        content
                    )

                if content != original:
                    task_file.write_text(content)
                    reset_count += 1

    print(f"Reset {reset_count} task files")

if __name__ == "__main__":
    main()
