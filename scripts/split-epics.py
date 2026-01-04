#!/usr/bin/env python3
"""
Split Epic Files into Summary + Full versions.

Transforms:
  EPIC-{N}.md (huge file with all stories)
Into:
  EPIC-{N}-summary.md (~100 lines for JIRA)
  EPIC-{N}-full.md (original, renamed)
"""

import re
import os
from pathlib import Path

EPICS_DIR = Path(__file__).parent.parent / ".bmad/planning-artifacts/epics"


def extract_epic_metadata(content: str) -> dict:
    """Extract key metadata from epic file."""
    metadata = {}

    # Title
    title_match = re.search(r'^# (EPIC-[\w-]+): (.+)$', content, re.MULTILINE)
    if title_match:
        metadata['id'] = title_match.group(1)
        metadata['title'] = title_match.group(2)

    # Status, Priority, Team, etc.
    for field in ['Status', 'Team', 'MVP Scope', 'Priority']:
        match = re.search(rf'\*\*{field}:\*\* (.+)$', content, re.MULTILINE)
        if match:
            metadata[field.lower().replace(' ', '_')] = match.group(1).strip()

    # Total Stories and Points
    stories_match = re.search(r'\*\*Total Stories:\*\* (\d+)', content)
    points_match = re.search(r'\*\*Total Points:\*\* (\d+)', content)
    if stories_match:
        metadata['total_stories'] = stories_match.group(1)
    if points_match:
        metadata['total_points'] = points_match.group(1)

    # Summary section
    summary_match = re.search(r'## Summary\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    if summary_match:
        metadata['summary'] = summary_match.group(1).strip()[:500]

    # Business Value
    bv_match = re.search(r'## Business Value\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    if bv_match:
        metadata['business_value'] = bv_match.group(1).strip()

    # Acceptance Criteria
    ac_match = re.search(r'## (?:Epic )?Acceptance Criteria\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    if ac_match:
        metadata['acceptance_criteria'] = ac_match.group(1).strip()

    return metadata


def extract_stories(content: str) -> list:
    """Extract story IDs and titles."""
    stories = []

    # Pattern for story headers: #### STORY-ID: Title
    pattern = r'^#### ([A-Z]+-\d+): (.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        story_id = match.group(1)
        title = match.group(2).strip()

        # Try to extract points
        points_match = re.search(
            rf'{re.escape(story_id)}.*?\*\*Points:\*\* (\d+)',
            content[match.start():match.start()+500]
        )
        points = points_match.group(1) if points_match else '?'

        # Try to extract sprint
        sprint_match = re.search(
            rf'{re.escape(story_id)}.*?\*\*Sprint:\*\* (\d+)',
            content[match.start():match.start()+500]
        )
        sprint = sprint_match.group(1) if sprint_match else '?'

        stories.append({
            'id': story_id,
            'title': title[:60],
            'points': points,
            'sprint': sprint
        })

    return stories


def generate_summary(metadata: dict, stories: list) -> str:
    """Generate the summary file content."""
    lines = [
        f"# {metadata.get('id', 'EPIC-?')}: {metadata.get('title', 'Unknown')}",
        "",
        f"**Status:** {metadata.get('status', 'backlog')}",
        f"**Priority:** {metadata.get('priority', 'P1')}",
        f"**Owner:** {metadata.get('team', 'TBD')}",
        f"**MVP:** {metadata.get('mvp_scope', 'MVP 1')}",
        f"**Total Stories:** {metadata.get('total_stories', len(stories))} | **Total Points:** {metadata.get('total_points', '?')}",
        "",
        "---",
        "",
        "## Summary",
        "",
        metadata.get('summary', 'No summary available.'),
        "",
        "---",
        "",
        "## Business Value",
        "",
        metadata.get('business_value', '- TBD'),
        "",
        "---",
        "",
        "## Acceptance Criteria",
        "",
        metadata.get('acceptance_criteria', '- [ ] TBD'),
        "",
        "---",
        "",
        "## Stories",
        "",
        "| ID | Title | Pts | Sprint | Status |",
        "|----|-------|-----|--------|--------|",
    ]

    for story in stories[:100]:  # Limit to 100 stories in summary
        lines.append(f"| {story['id']} | {story['title']} | {story['points']} | {story['sprint']} | backlog |")

    if len(stories) > 100:
        lines.append(f"| ... | ({len(stories) - 100} more stories) | ... | ... | ... |")

    lines.extend([
        "",
        "---",
        "",
        f"**Full Documentation:** [{metadata.get('id', 'EPIC')}-full.md](./{metadata.get('id', 'EPIC')}-full.md) | Confluence (pending sync)",
    ])

    return "\n".join(lines)


def process_epic(filepath: Path, dry_run: bool = False) -> bool:
    """Process a single epic file."""
    # Skip if already processed
    if '-summary' in filepath.name or '-full' in filepath.name:
        return False

    content = filepath.read_text()

    # Extract metadata and stories
    metadata = extract_epic_metadata(content)
    stories = extract_stories(content)

    if not metadata.get('id'):
        print(f"  ⚠ Could not extract epic ID from {filepath.name}")
        return False

    print(f"  Processing {filepath.name}")
    print(f"    ID: {metadata.get('id')}, Stories: {len(stories)}")

    # Generate summary
    summary = generate_summary(metadata, stories)

    # File paths
    summary_path = filepath.parent / f"{metadata['id']}-summary.md"
    full_path = filepath.parent / f"{metadata['id']}-full.md"

    if dry_run:
        print(f"    [DRY RUN] Would create: {summary_path.name}")
        print(f"    [DRY RUN] Would rename to: {full_path.name}")
    else:
        # Write summary
        summary_path.write_text(summary)
        print(f"    ✓ Created: {summary_path.name}")

        # Rename original to full
        filepath.rename(full_path)
        print(f"    ✓ Renamed to: {full_path.name}")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Split epic files into summary + full versions")
    parser.add_argument("--dry-run", action="store_true", help="Preview without modifying")
    parser.add_argument("--epic", type=str, help="Process single epic file")
    args = parser.parse_args()

    print("=" * 60)
    print("SPLIT EPIC FILES")
    print(f"Directory: {EPICS_DIR}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)

    if not EPICS_DIR.exists():
        print(f"ERROR: Directory not found: {EPICS_DIR}")
        return

    processed = 0
    skipped = 0

    if args.epic:
        files = [EPICS_DIR / args.epic]
    else:
        # Get all epic files that haven't been split yet
        files = sorted([
            f for f in EPICS_DIR.glob("EPIC-*.md")
            if '-summary' not in f.name and '-full' not in f.name
        ])

    for filepath in files:
        if not filepath.exists():
            print(f"  ⚠ File not found: {filepath}")
            continue

        if process_epic(filepath, args.dry_run):
            processed += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
