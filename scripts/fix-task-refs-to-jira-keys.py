#!/usr/bin/env python3
"""
Convert task references from story-task format (AUTH-001-1-T1) to JIRA keys (ARGUS-1224).
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

def build_task_id_to_jira_map() -> dict:
    """Build a mapping from task IDs (AUTH-001-1-T1) to JIRA keys (ARGUS-1224)."""
    mapping = {}

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
                content = task_file.read_text()

                # Extract task ID from header (e.g., "# AUTH-001-1-T1: ClickHouse Table Creation")
                task_id_match = re.search(r'^#\s+([A-Z]+-\d+-\d+[a-z]?-T\d+):', content, re.MULTILINE)
                if not task_id_match:
                    continue
                task_id = task_id_match.group(1)

                # Extract JIRA key
                jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
                if not jira_match:
                    continue
                jira_key = jira_match.group(1)

                mapping[task_id] = jira_key

    return mapping

def convert_refs_to_jira_keys(refs: str, mapping: dict) -> str:
    """Convert task ID refs to JIRA keys."""
    if not refs.strip() or refs.strip().lower() == "none" or refs.strip() == "-":
        return refs

    parts = [p.strip() for p in refs.split(",")]
    converted = []

    for part in parts:
        if part in mapping:
            converted.append(mapping[part])
        else:
            # Keep as-is if not found (might already be JIRA key or "none")
            converted.append(part)

    return ", ".join(converted)

def fix_task_file(task_path: Path, mapping: dict) -> tuple[bool, str]:
    """Fix references in a single task file. Returns (changed, description)."""
    content = task_path.read_text()
    original = content

    changes = []

    # Find and replace Requires row
    requires_match = re.search(r'(\|\s*Requires\s*\|\s*)([^|]+)(\|)', content)
    if requires_match:
        old_refs = requires_match.group(2).strip()
        new_refs = convert_refs_to_jira_keys(old_refs, mapping)
        if old_refs != new_refs:
            content = content.replace(
                requires_match.group(0),
                f"{requires_match.group(1)}{new_refs} {requires_match.group(3)}"
            )
            changes.append(f"Requires: {old_refs} -> {new_refs}")

    # Find and replace Unlocks row
    unlocks_match = re.search(r'(\|\s*Unlocks\s*\|\s*)([^|]+)(\|)', content)
    if unlocks_match:
        old_refs = unlocks_match.group(2).strip()
        new_refs = convert_refs_to_jira_keys(old_refs, mapping)
        if old_refs != new_refs:
            content = content.replace(
                unlocks_match.group(0),
                f"{unlocks_match.group(1)}{new_refs} {unlocks_match.group(3)}"
            )
            changes.append(f"Unlocks: {old_refs} -> {new_refs}")

    if content != original:
        task_path.write_text(content)
        return True, "; ".join(changes)

    return False, "No changes needed"

def main():
    print("=" * 70)
    print("Converting Task References to JIRA Keys")
    print("=" * 70)

    print("\nBuilding task ID -> JIRA key mapping...")
    mapping = build_task_id_to_jira_map()
    print(f"  Found {len(mapping)} task mappings")

    # Show sample mappings
    print("\n  Sample mappings:")
    for i, (task_id, jira_key) in enumerate(list(mapping.items())[:5]):
        print(f"    {task_id} -> {jira_key}")

    print("\nUpdating task files...")

    fixed = 0
    skipped = 0
    errors = 0

    for epic_dir in sorted(EPICS_DIR.iterdir()):
        if not epic_dir.is_dir():
            continue

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        epic_has_changes = False

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                try:
                    changed, description = fix_task_file(task_file, mapping)
                    if changed:
                        if not epic_has_changes:
                            print(f"\n[{epic_dir.name}]")
                            epic_has_changes = True
                        print(f"  FIXED: {task_file.name}")
                        print(f"         {description}")
                        fixed += 1
                    else:
                        skipped += 1
                except Exception as e:
                    print(f"  ERROR: {task_file.name} - {e}")
                    errors += 1

    print("\n" + "=" * 70)
    print(f"SUMMARY: Fixed={fixed}, Skipped={skipped}, Errors={errors}")
    print("=" * 70)

if __name__ == "__main__":
    main()
