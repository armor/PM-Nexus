#!/usr/bin/env python3
"""
Update Implementation Artifacts for JIRA Sync

Transforms task headers from:
  ### Task 1: Title (AC: X)
To:
  ### STORY-ID-T1: Title
  **Linked to:** AC-X

And adds JIRA sync comments.
"""

import re
from pathlib import Path

IMPL_DIR = Path(__file__).parent.parent / ".bmad/implementation-artifacts"


def extract_story_id(content: str) -> str:
    """Extract story ID from file content."""
    # Try format: # Story AUTH-001.2: Title
    match = re.search(r'^# Story ([A-Z]+-\d+\.\d+[a-z]?):', content, re.MULTILINE)
    if match:
        return match.group(1).replace('.', '-')

    # Try format: # Story auth-001.2: or auth-001-2:
    match = re.search(r'^# Story (auth-\d+-\d+[a-z]?):', content, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).upper().replace('.', '-')

    return None


def update_tasks_section(content: str, story_id: str) -> str:
    """Update Tasks section to JIRA-sync compatible format."""

    # Check if already has JIRA SYNC comment
    if "<!-- JIRA SYNC:" in content:
        print(f"    Already has JIRA SYNC format")
        return content

    # Add JIRA sync comment after ## Tasks header
    jira_comment = """## Tasks

<!-- JIRA SYNC: Each ### becomes a JIRA Task, each table row becomes a Sub-task -->
<!-- Task naming: {story_id}-T1, {story_id}-T2, etc. -->
""".format(story_id=story_id)

    content = re.sub(r'^## Tasks\s*\n', jira_comment, content, flags=re.MULTILINE)

    # Transform task headers: ### Task N: Title (AC: X) → ### STORY-ID-TN: Title
    def transform_task(match):
        task_num = match.group(1)
        title = match.group(2).strip()
        ac_ref = match.group(3) if match.group(3) else ""

        new_header = f"### {story_id}-T{task_num}: {title}"
        if ac_ref:
            # Extract AC numbers
            ac_nums = re.findall(r'\d+', ac_ref)
            ac_list = ", ".join([f"AC-{n}" for n in ac_nums])
            new_header += f"\n**Linked to:** {ac_list}"

        return new_header

    # Match: ### Task N: Title (AC: X, Y) or ### Task N: Title
    pattern = r'^### Task (\d+): ([^\n]+?)(?:\s*\(AC:\s*([^)]+)\))?\s*$'
    content = re.sub(pattern, transform_task, content, flags=re.MULTILINE)

    return content


def update_subtask_ids(content: str, story_id: str) -> str:
    """Update subtask IDs in tables to include story prefix."""

    # Pattern for subtask rows: | 1.1 | Title | ... |
    def transform_subtask_row(match):
        task_num = match.group(1)
        subtask_num = match.group(2)
        rest = match.group(3)

        new_id = f"T{task_num}-S{subtask_num}"
        return f"| {new_id} |{rest}"

    # Match: | N.M | rest of row
    pattern = r'^\| (\d+)\.(\d+) \|(.+)$'
    content = re.sub(pattern, transform_subtask_row, content, flags=re.MULTILINE)

    return content


def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single story file."""
    content = filepath.read_text()

    story_id = extract_story_id(content)
    if not story_id:
        print(f"  ⚠ Could not extract story ID from {filepath.name}")
        return False

    print(f"  Processing {filepath.name} (ID: {story_id})")

    # Update tasks section
    new_content = update_tasks_section(content, story_id)

    # Update subtask IDs
    new_content = update_subtask_ids(new_content, story_id)

    if new_content == content:
        print(f"    No changes needed")
        return False

    if dry_run:
        print(f"    [DRY RUN] Would update file")
        # Show diff preview
        old_lines = content.split('\n')
        new_lines = new_content.split('\n')
        for i, (old, new) in enumerate(zip(old_lines, new_lines)):
            if old != new:
                print(f"      Line {i+1}:")
                print(f"        - {old[:80]}")
                print(f"        + {new[:80]}")
                if i > 5:  # Limit preview
                    print(f"      ... and more changes")
                    break
    else:
        filepath.write_text(new_content)
        print(f"    ✓ Updated")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update implementation artifacts for JIRA sync")
    parser.add_argument("--dry-run", action="store_true", help="Preview without modifying")
    parser.add_argument("--file", type=str, help="Process single file")
    args = parser.parse_args()

    print("=" * 60)
    print("UPDATE IMPLEMENTATION ARTIFACTS FOR JIRA SYNC")
    print(f"Directory: {IMPL_DIR}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)

    if not IMPL_DIR.exists():
        print(f"ERROR: Directory not found: {IMPL_DIR}")
        return

    updated = 0
    skipped = 0

    if args.file:
        files = [IMPL_DIR / args.file]
    else:
        files = sorted(IMPL_DIR.glob("auth-*.md"))

    for filepath in files:
        if not filepath.exists():
            print(f"  ⚠ File not found: {filepath}")
            continue

        if process_file(filepath, args.dry_run):
            updated += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
