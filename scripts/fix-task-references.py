#!/usr/bin/env python3
"""
Fix task references to use fully qualified IDs.
Changes: T1, T2 -> AUTH-001-1-T1, AUTH-001-1-T2
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

def extract_story_id(task_content: str) -> str:
    """Extract the story ID from task content."""
    # Look for "**Story:** AUTH-001-1" pattern
    match = re.search(r'\*\*Story:\*\*\s*([A-Z]+-\d+-\d+[a-z]?)', task_content)
    if match:
        return match.group(1)
    return ""

def expand_task_refs(refs: str, story_id: str) -> str:
    """Expand short task refs (T1, T2) to full refs (AUTH-001-1-T1)."""
    if not refs.strip() or refs.strip().lower() == "none" or refs.strip() == "-":
        return refs

    parts = [p.strip() for p in refs.split(",")]
    expanded = []

    for part in parts:
        # Check if it's already fully qualified
        if re.match(r'^[A-Z]+-\d+-\d+[a-z]?-T\d+$', part):
            expanded.append(part)
        # Check if it's a short ref like T1, T2
        elif re.match(r'^T\d+$', part):
            expanded.append(f"{story_id}-{part}")
        else:
            # Keep as-is (might be "none" or other)
            expanded.append(part)

    return ", ".join(expanded)

def fix_task_file(task_path: Path) -> tuple[bool, str]:
    """Fix references in a single task file. Returns (changed, description)."""
    content = task_path.read_text()
    original = content

    story_id = extract_story_id(content)
    if not story_id:
        return False, "Could not extract story ID"

    # Find and replace Requires row
    requires_match = re.search(r'(\|\s*Requires\s*\|\s*)([^|]+)(\|)', content)
    if requires_match:
        old_refs = requires_match.group(2).strip()
        new_refs = expand_task_refs(old_refs, story_id)
        if old_refs != new_refs:
            content = content.replace(
                requires_match.group(0),
                f"{requires_match.group(1)}{new_refs} {requires_match.group(3)}"
            )

    # Find and replace Unlocks row
    unlocks_match = re.search(r'(\|\s*Unlocks\s*\|\s*)([^|]+)(\|)', content)
    if unlocks_match:
        old_refs = unlocks_match.group(2).strip()
        new_refs = expand_task_refs(old_refs, story_id)
        if old_refs != new_refs:
            content = content.replace(
                unlocks_match.group(0),
                f"{unlocks_match.group(1)}{new_refs} {unlocks_match.group(3)}"
            )

    if content != original:
        task_path.write_text(content)
        return True, f"Fixed: Requires/Unlocks now use {story_id}-Tn format"

    return False, "No changes needed"

def main():
    print("=" * 60)
    print("Fixing Task References to Fully Qualified IDs")
    print("=" * 60)

    fixed = 0
    skipped = 0
    errors = 0

    for epic_dir in sorted(EPICS_DIR.iterdir()):
        if not epic_dir.is_dir():
            continue

        print(f"\n[{epic_dir.name}]")

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                try:
                    changed, description = fix_task_file(task_file)
                    if changed:
                        print(f"  FIXED: {task_file.name} - {description}")
                        fixed += 1
                    else:
                        skipped += 1
                except Exception as e:
                    print(f"  ERROR: {task_file.name} - {e}")
                    errors += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: Fixed={fixed}, Skipped={skipped}, Errors={errors}")
    print("=" * 60)

if __name__ == "__main__":
    main()
