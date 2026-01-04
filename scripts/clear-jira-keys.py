#!/usr/bin/env python3
"""
Clear all JIRA keys from BMAD files to prepare for fresh sync.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

def clear_jira_key(file_path: Path) -> bool:
    """Clear JIRA key from a file. Returns True if changed."""
    content = file_path.read_text()

    # Replace JIRA Key value with empty
    new_content = re.sub(
        r'(\|\s*JIRA Key\s*\|\s*)[A-Z]+-\d+(\s*\|)',
        r'\1\2',
        content
    )

    # Also clear Requires/Unlocks that have JIRA keys (reset to none for first task, keep structure)
    # Actually, we need to keep the dependency structure - just clear the JIRA keys

    if new_content != content:
        file_path.write_text(new_content)
        return True
    return False

def main():
    print("Clearing JIRA keys from all BMAD files...")

    cleared = 0

    for epic_dir in sorted(EPICS_DIR.iterdir()):
        if not epic_dir.is_dir():
            continue

        # Clear epic README
        readme = epic_dir / "README.md"
        if readme.exists() and clear_jira_key(readme):
            print(f"  Cleared: {epic_dir.name}/README.md")
            cleared += 1

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            # Clear story file
            for story_file in story_dir.glob("story-*.md"):
                if clear_jira_key(story_file):
                    print(f"  Cleared: {story_file.relative_to(EPICS_DIR)}")
                    cleared += 1

            # Clear task files
            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                if clear_jira_key(task_file):
                    cleared += 1

    print(f"\nCleared {cleared} JIRA keys")

if __name__ == "__main__":
    main()
