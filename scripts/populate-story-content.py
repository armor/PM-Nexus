#!/usr/bin/env python3
"""
Populate Story Content from Full Epic Files

Reads the full story content from .bmad/planning-artifacts/epics/*-full.md
and populates the story files in .bmad/epics/

Usage:
    python scripts/populate-story-content.py
    python scripts/populate-story-content.py --dry-run
    python scripts/populate-story-content.py --epic EPIC-1-PLATFORM
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_FULL_DIR = PROJECT_ROOT / ".bmad/planning-artifacts/epics"
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"


def parse_full_epic_file(filepath: Path) -> Dict[str, Dict]:
    """Parse a full epic file and extract all story content."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    stories = {}

    # Pattern to match story headers like "#### PLAT-001: Title"
    story_pattern = re.compile(r'^####\s+([A-Z]+-\d+):\s+(.+?)$', re.MULTILINE)

    # Find all story starts
    matches = list(story_pattern.finditer(content))

    for i, match in enumerate(matches):
        story_id = match.group(1)
        story_title = match.group(2).strip()

        # Get content from this story to the next story (or end of file)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        story_content = content[start:end].strip()

        # Parse the story content
        stories[story_id] = {
            'title': story_title,
            'raw_content': story_content,
            **parse_story_content(story_content)
        }

    return stories


def parse_story_content(content: str) -> Dict:
    """Parse individual story content into sections."""
    result = {
        'metadata': '',
        'description': '',
        'functional_requirements': [],
        'code_quality': [],
        'security': [],
        'interface_adherence': [],
        'unit_testing': [],
        'integration_testing': [],
        'e2e_testing': [],
        'ui_testing': [],
        'ux_testing': [],
    }

    lines = content.split('\n')
    current_section = 'metadata'
    section_content = []

    section_map = {
        '**Functional Requirements:**': 'functional_requirements',
        '**Code Quality:**': 'code_quality',
        '**Security:**': 'security',
        '**Interface Adherence:**': 'interface_adherence',
        '**Unit Testing:**': 'unit_testing',
        '**Integration Testing:**': 'integration_testing',
        '**E2E Testing:**': 'e2e_testing',
        '**UI Testing:**': 'ui_testing',
        '**UX Testing:**': 'ux_testing',
    }

    for line in lines:
        stripped = line.strip()

        # Check if this is a new section
        new_section = None
        for marker, section_name in section_map.items():
            if stripped.startswith(marker):
                new_section = section_name
                break

        if new_section:
            # Save current section
            if current_section == 'metadata':
                # Extract description from metadata
                for meta_line in section_content:
                    meta_stripped = meta_line.strip()
                    if meta_stripped and not meta_stripped.startswith('**'):
                        result['description'] = meta_stripped
                        break
                result['metadata'] = '\n'.join(section_content[:3])  # First 3 lines are usually metadata
            else:
                result[current_section] = [l for l in section_content if l.strip().startswith('- [')]

            current_section = new_section
            section_content = []
        else:
            section_content.append(line)

    # Don't forget the last section
    if current_section != 'metadata':
        result[current_section] = [l.strip() for l in section_content if l.strip().startswith('- [')]

    return result


def find_story_file(story_id: str, epic_name: str = None) -> Optional[Path]:
    """Find the story file for a given story ID."""
    # Story ID format: PLAT-001, GRAPH-002, STORY-001, etc.
    parts = story_id.split('-')
    prefix = parts[0]

    # Handle numeric part - could be "001", "002a", etc.
    num_str = parts[1] if len(parts) > 1 else "0"
    # Extract just the numeric portion
    num_match = re.match(r'^(\d+)', num_str)
    if not num_match:
        return None
    num_int = int(num_match.group(1))

    # Map prefix to epic directory
    prefix_to_epic = {
        'PLAT': 'EPIC-1-PLATFORM',
        'GRAPH': 'EPIC-2',
        'RISK': 'EPIC-3',
        'AUTO': 'EPIC-4',
        'UX': 'EPIC-5',
        'INT': 'EPIC-6',
        'DIFF': 'EPIC-7',
        'EXEC': 'EPIC-8-EXEC-COMPLIANCE',
        'COMP': 'EPIC-8-EXEC-COMPLIANCE',
        'POLICY': 'EPIC-9-POLICY-AI',
        'CARTO': 'EPIC-11',
        'STORY': 'EPIC-AUTH-001',  # AUTH stories use STORY-XXX format
    }

    epic_dir = prefix_to_epic.get(prefix)
    if not epic_dir:
        # Try to infer from epic_name if provided
        if epic_name:
            # Extract directory name from epic name
            epic_dir = epic_name.replace('-full', '')
        else:
            return None

    epic_path = EPICS_DIR / epic_dir / "stories"
    if not epic_path.exists():
        return None

    # Search for story directory matching the number
    for story_dir in epic_path.iterdir():
        if not story_dir.is_dir():
            continue
        # Extract number from directory name (e.g., "01-clickhouse-helm" -> 1, "02a-secrets" -> 2)
        dir_name = story_dir.name
        match = re.match(r'^(\d+)', dir_name)
        if match:
            dir_num = int(match.group(1))
            if dir_num == num_int:
                # Check for suffix match (e.g., "02a" vs "02")
                suffix_match = re.match(r'^\d+([a-z]*)-', dir_name)
                story_suffix = re.match(r'^\d+([a-z]*)', num_str)
                if suffix_match and story_suffix:
                    dir_suffix = suffix_match.group(1)
                    id_suffix = story_suffix.group(1)
                    if dir_suffix == id_suffix:
                        story_file = story_dir / f"story-{story_dir.name}.md"
                        if story_file.exists():
                            return story_file
                elif not suffix_match or not suffix_match.group(1):
                    # No suffix required
                    story_file = story_dir / f"story-{story_dir.name}.md"
                    if story_file.exists():
                        return story_file

    return None


def update_story_file(story_file: Path, story_data: Dict, dry_run: bool = False) -> bool:
    """Update a story file with content from the full epic."""
    with open(story_file, encoding='utf-8') as f:
        content = f.read()

    # Build new content sections
    story_text = story_data.get('description', '')

    # Build acceptance criteria from functional requirements
    func_reqs = story_data.get('functional_requirements', [])
    ac_text = '\n'.join(func_reqs) if func_reqs else ''

    # Build business value (combine with description)
    business_value = f"This story enables: {story_text}" if story_text else ''

    # Replace empty Story section
    new_content = content

    # Replace Story section
    story_section_pattern = r'(## Story\n\n)(.*?)(\n---)'
    if story_text:
        new_content = re.sub(
            story_section_pattern,
            f'\\1{story_text}\n\\3',
            new_content,
            flags=re.DOTALL
        )

    # Replace Business Value section
    bv_section_pattern = r'(## Business Value\n\n)(.*?)(\n---)'
    if business_value:
        new_content = re.sub(
            bv_section_pattern,
            f'\\1{business_value}\n\\3',
            new_content,
            flags=re.DOTALL
        )

    # Replace Acceptance Criteria section
    ac_section_pattern = r'(## Acceptance Criteria\n\n)(.*?)(\n---)'
    if ac_text:
        new_content = re.sub(
            ac_section_pattern,
            f'\\1{ac_text}\n\\3',
            new_content,
            flags=re.DOTALL
        )

    if new_content != content:
        if dry_run:
            print(f"  Would update: {story_file}")
            print(f"    Story: {story_text[:60]}...")
            print(f"    AC count: {len(func_reqs)}")
        else:
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Updated: {story_file.name}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description='Populate story content from full epic files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--epic', help='Process only this epic (e.g., EPIC-1-PLATFORM)')
    args = parser.parse_args()

    print("=" * 60)
    print("Populate Story Content")
    print("=" * 60)
    print(f"Dry Run: {args.dry_run}")
    print()

    stats = {
        'epics_processed': 0,
        'stories_found': 0,
        'stories_updated': 0,
        'stories_not_found': 0,
    }

    # Find all full epic files
    full_files = list(EPICS_FULL_DIR.glob("*-full.md"))
    print(f"Found {len(full_files)} full epic files")
    print()

    for full_file in sorted(full_files):
        epic_name = full_file.stem.replace('-full', '')

        # Filter by epic if specified
        if args.epic and args.epic not in epic_name:
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {epic_name}")
        print(f"{'='*60}")

        stories = parse_full_epic_file(full_file)
        stats['epics_processed'] += 1
        stats['stories_found'] += len(stories)

        print(f"Found {len(stories)} stories in {full_file.name}")

        for story_id, story_data in stories.items():
            story_file = find_story_file(story_id, epic_name)

            if not story_file:
                print(f"  NOT FOUND: {story_id}")
                stats['stories_not_found'] += 1
                continue

            if update_story_file(story_file, story_data, args.dry_run):
                stats['stories_updated'] += 1

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Epics processed:    {stats['epics_processed']}")
    print(f"Stories in files:   {stats['stories_found']}")
    print(f"Stories updated:    {stats['stories_updated']}")
    print(f"Stories not found:  {stats['stories_not_found']}")


if __name__ == '__main__':
    main()
