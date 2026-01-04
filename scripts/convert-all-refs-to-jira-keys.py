#!/usr/bin/env python3
"""
Convert ALL references (tasks and stories) to JIRA keys.
- Task refs: T1, T2 -> ARGUS-XXXX
- Story refs: S1, S2a -> ARGUS-XXXX
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

def build_story_jira_map() -> dict:
    """Build mapping from story IDs (1, 2, 2a) to JIRA keys."""
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

            # Find story file
            story_files = list(story_dir.glob("story-*.md"))
            if not story_files:
                continue

            content = story_files[0].read_text()

            # Extract story ID from header (e.g., "# AUTH-001-2a: ...")
            id_match = re.search(r'^#\s+[A-Z]+-\d+-(\d+[a-z]?):', content, re.MULTILINE)
            if not id_match:
                continue
            story_num = id_match.group(1)  # "1", "2", "2a", etc.

            # Extract JIRA key
            jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
            if not jira_match:
                continue

            mapping[story_num] = jira_match.group(1)
            # Also map with S prefix
            mapping[f"S{story_num}"] = jira_match.group(1)

    return mapping

def build_task_jira_map() -> dict:
    """Build mapping from task numbers (T1, T2) to JIRA keys per story."""
    mapping = {}  # key: (story_dir_name, task_num) -> JIRA key

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

                # Extract task number from header
                task_match = re.search(r'^#\s+[A-Z]+-\d+-\d+[a-z]?-(T\d+):', content, re.MULTILINE)
                if not task_match:
                    continue
                task_num = task_match.group(1)  # "T1", "T2", etc.

                # Extract JIRA key
                jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
                if not jira_match:
                    continue

                mapping[(story_dir.name, task_num)] = jira_match.group(1)

    return mapping

def convert_story_refs(content: str, story_map: dict) -> str:
    """Convert story refs (S1, S2a) to JIRA keys."""

    def replace_ref(match):
        ref = match.group(1)
        if ref in story_map:
            return story_map[ref]
        return ref

    # Find refs in Depends On and Blocks fields
    # Pattern: S followed by number and optional letter
    # In comma-separated lists

    def replace_field(match):
        prefix = match.group(1)
        refs = match.group(2)
        suffix = match.group(3)

        # Split by comma, convert each
        parts = [p.strip() for p in refs.split(",")]
        converted = []
        for p in parts:
            if p in story_map:
                converted.append(story_map[p])
            elif p.startswith("S") and p[1:] in story_map:
                converted.append(story_map[p[1:]])
            else:
                converted.append(p)

        return f"{prefix}{', '.join(converted)} {suffix}"

    # Convert Depends On field
    content = re.sub(
        r'(\|\s*Depends On\s*\|\s*)([^|]+)(\|)',
        replace_field,
        content
    )

    # Convert Blocks field
    content = re.sub(
        r'(\|\s*Blocks\s*\|\s*)([^|]+)(\|)',
        replace_field,
        content
    )

    return content

def convert_task_refs(content: str, task_map: dict, story_dir_name: str) -> str:
    """Convert task refs (T1, T2) to JIRA keys."""

    def replace_field(match):
        prefix = match.group(1)
        refs = match.group(2)
        suffix = match.group(3)

        if refs.strip().lower() == "none" or refs.strip() == "-":
            return match.group(0)

        parts = [p.strip() for p in refs.split(",")]
        converted = []
        for p in parts:
            key = (story_dir_name, p)
            if key in task_map:
                converted.append(task_map[key])
            else:
                converted.append(p)

        return f"{prefix}{', '.join(converted)} {suffix}"

    # Convert Requires field
    content = re.sub(
        r'(\|\s*Requires\s*\|\s*)([^|]+)(\|)',
        replace_field,
        content
    )

    # Convert Unlocks field
    content = re.sub(
        r'(\|\s*Unlocks\s*\|\s*)([^|]+)(\|)',
        replace_field,
        content
    )

    return content

def main():
    print("=" * 70)
    print("Converting All References to JIRA Keys")
    print("=" * 70)

    print("\nBuilding mappings...")
    story_map = build_story_jira_map()
    print(f"  Story mappings: {len(story_map)}")
    for k, v in list(story_map.items())[:6]:
        print(f"    {k} -> {v}")

    task_map = build_task_jira_map()
    print(f"  Task mappings: {len(task_map)}")

    stories_fixed = 0
    tasks_fixed = 0

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

            # Process story file
            story_files = list(story_dir.glob("story-*.md"))
            if story_files:
                story_file = story_files[0]
                content = story_file.read_text()
                original = content

                content = convert_story_refs(content, story_map)

                if content != original:
                    if not epic_has_changes:
                        print(f"\n[{epic_dir.name}]")
                        epic_has_changes = True
                    print(f"  STORY: {story_file.name}")
                    story_file.write_text(content)
                    stories_fixed += 1

            # Process task files
            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                content = task_file.read_text()
                original = content

                content = convert_task_refs(content, task_map, story_dir.name)

                if content != original:
                    if not epic_has_changes:
                        print(f"\n[{epic_dir.name}]")
                        epic_has_changes = True
                    print(f"  TASK: {task_file.name}")
                    task_file.write_text(content)
                    tasks_fixed += 1

    print("\n" + "=" * 70)
    print(f"SUMMARY: Stories fixed={stories_fixed}, Tasks fixed={tasks_fixed}")
    print("=" * 70)

if __name__ == "__main__":
    main()
