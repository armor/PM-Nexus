#!/usr/bin/env python3
"""
Migrate generated-stories to new structure with FULL AI prompts in tasks.

Structure:
  Story (~50 lines): Human context + ACs for JIRA
  Task (variable):   Full AI Implementation Prompt - everything Claude needs
  Subtasks:          Progress checkboxes within task

Source: .bmad/generated-stories/{EPIC}/*.md
Target: .bmad/epics/{EPIC}/stories/{NN}-{slug}/
        .bmad/epics/{EPIC}/stories/{NN}-{slug}/story-{NN}-{slug}.md
        .bmad/epics/{EPIC}/stories/{NN}-{slug}/tasks/task-{NN}-{ac-slug}.md

Usage:
  python scripts/migrate-full-content.py --dry-run  # Preview
  python scripts/migrate-full-content.py            # Execute
  python scripts/migrate-full-content.py --epic EPIC-1-PLATFORM  # Single epic
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to kebab-case slug."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:max_len]


def parse_story_file(content: str) -> Dict:
    """Parse a generated-story file into structured data."""
    data = {
        'id': '',
        'title': '',
        'metadata': {},
        'story_statement': '',
        'business_value': '',
        'acceptance_criteria': [],
        'target_files': '',
        'code_patterns': '',
        'anti_patterns': '',
        'edge_cases': '',
        'security_considerations': '',
        'testing_requirements': '',
        'dependencies': '',
        'definition_of_done': '',
        'references': '',
    }

    # Extract title from first heading
    title_match = re.search(r'^#\s+(\S+):\s+(.+)$', content, re.MULTILINE)
    if title_match:
        data['id'] = title_match.group(1)
        data['title'] = title_match.group(2).strip()

    # Extract YAML metadata block
    yaml_match = re.search(r'```yaml\s*\n(.*?)```', content, re.DOTALL)
    if yaml_match:
        try:
            parsed = yaml.safe_load(yaml_match.group(1))
            if parsed:
                data['metadata'] = parsed
        except:
            pass

    # Extract story statement
    story_match = re.search(r'## Story\s*\n+(As a.*?so that.*?\.)', content, re.DOTALL | re.IGNORECASE)
    if story_match:
        data['story_statement'] = story_match.group(1).strip()

    # Extract business value
    bv_match = re.search(r'## Business Value\s*\n+(.*?)(?=\n---|\n## )', content, re.DOTALL)
    if bv_match:
        data['business_value'] = bv_match.group(1).strip()

    # Extract acceptance criteria
    ac_pattern = r'### (AC\d+):\s*(.+?)\n(.*?)(?=\n### AC|\n---|\n## |\Z)'
    for match in re.finditer(ac_pattern, content, re.DOTALL):
        ac_id = match.group(1)
        ac_title = match.group(2).strip()
        ac_content = match.group(3).strip()
        data['acceptance_criteria'].append({
            'id': ac_id,
            'title': ac_title,
            'content': ac_content
        })

    # Extract major sections
    sections = [
        ('target_files', r'## Target Files\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('code_patterns', r'## Code Patterns\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('anti_patterns', r'## Anti-Patterns.*?\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('edge_cases', r'## Edge Cases.*?\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('security_considerations', r'## Security Considerations\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('testing_requirements', r'## Testing Requirements\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('dependencies', r'## Dependencies\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('definition_of_done', r'## Definition of Done\s*\n+(.*?)(?=\n---|\n## |\Z)'),
        ('references', r'## References\s*\n+(.*?)(?=\n---|\n## |\Z)'),
    ]

    for key, pattern in sections:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data[key] = match.group(1).strip()

    return data


def create_story_file(data: Dict, story_folder: str) -> str:
    """Create slim story file content."""
    story_id = data['id']
    title = data['title']
    meta = data.get('metadata', {})

    # Extract metadata
    story_meta = meta.get('story', {})
    metadata = meta.get('metadata', {})

    priority = metadata.get('priority', 'P2')
    points = metadata.get('points', 3)
    sprint = metadata.get('sprint', 1)
    parent = metadata.get('parent', 'EPIC-1')

    # Build AC section
    ac_lines = []
    for ac in data['acceptance_criteria']:
        ac_lines.append(f"\n### {ac['id']}: {ac['title']}\n")
        ac_lines.append(f"{ac['content']}\n")

    # Build task table
    task_rows = []
    for i, ac in enumerate(data['acceptance_criteria'], 1):
        ac_slug = slugify(ac['title'], 30)
        task_file = f"task-{i:02d}-{ac_slug}.md"
        task_rows.append(f"| T{i} | [{task_file}](./tasks/{task_file}) | {ac['title'][:40]} | {ac['id']} | pending |")

    if not task_rows:
        task_rows.append("| T1 | [task-01-implementation.md](./tasks/task-01-implementation.md) | Implementation | AC1 | pending |")

    return f"""# {story_id}: {title}

**Epic:** {parent} | **Points:** {points} | **Priority:** {priority} | **Sprint:** {sprint}
**Status:** ready-for-dev

---

## Story

{data['story_statement']}

---

## Business Value

{data['business_value']}

---

## Acceptance Criteria
{''.join(ac_lines)}
---

## Tasks

| # | Task File | Title | Linked AC | Status |
|---|-----------|-------|-----------|--------|
{chr(10).join(task_rows)}

---

## References

{data['references'] if data['references'] else f'- Epic: {parent}'}
"""


def create_task_file(data: Dict, ac: Dict, task_num: int) -> str:
    """Create full AI implementation prompt task file."""
    story_id = data['id']
    title = data['title']
    ac_id = ac['id']
    ac_title = ac['title']

    # Build subtasks from definition of done or defaults
    subtasks = []
    if data['definition_of_done']:
        done_items = re.findall(r'- \[ \] (.+)', data['definition_of_done'])
        for i, item in enumerate(done_items[:5], 1):  # Max 5 subtasks
            subtasks.append(f"| S{i} | {item[:60]} | pending |")

    if not subtasks:
        subtasks = [
            "| S1 | Implement core functionality | pending |",
            "| S2 | Write unit tests | pending |",
            "| S3 | Verify acceptance criteria | pending |",
        ]

    return f"""# {story_id}-T{task_num}: {ac_title}

**Story:** {story_id}
**Linked to:** {ac_id}
**Status:** pending

---

## Acceptance Criteria

{ac['content']}

---

## AI Implementation Prompt

You are implementing **{story_id}-T{task_num}: {ac_title}** for the Armor Argus platform.

### Context
{data['story_statement']}

### This Task
Implement {ac_id}: {ac_title}

{ac['content']}

---

## Target Files

{data['target_files'] if data['target_files'] else '- TBD based on implementation'}

---

## Code Patterns

{data['code_patterns'] if data['code_patterns'] else 'Follow existing codebase patterns.'}

---

## Anti-Patterns (FORBIDDEN)

{data['anti_patterns'] if data['anti_patterns'] else '- Do not hardcode values\n- Do not skip error handling\n- Do not ignore security considerations'}

---

## Edge Cases

{data['edge_cases'] if data['edge_cases'] else 'Handle all error conditions gracefully.'}

---

## Security Considerations

{data['security_considerations'] if data['security_considerations'] else 'Follow security best practices.'}

---

## Testing Requirements

{data['testing_requirements'] if data['testing_requirements'] else '- Unit tests for all new code\n- Integration tests for API endpoints'}

---

## Dependencies

{data['dependencies'] if data['dependencies'] else 'See Cargo.toml / package.json'}

---

## Subtasks

| # | Description | Status |
|---|-------------|--------|
{chr(10).join(subtasks)}

---

## Verification

```bash
# Run tests
cargo test --features auth

# Verify functionality
# Add specific verification commands here
```

---

## Done When

- [ ] {ac_id} acceptance criteria met
- [ ] Tests passing
- [ ] Code reviewed
- [ ] No security vulnerabilities introduced
"""


def get_epic_mapping() -> Dict[str, str]:
    """Map source epic names to target epic names."""
    return {
        'EPIC-1-PLATFORM': 'EPIC-1-PLATFORM',
        'EPIC-2-GRAPH': 'EPIC-2',
        'EPIC-3-RISK': 'EPIC-3',
        'EPIC-4-AUTOMATION': 'EPIC-4',
        'EPIC-5-UX': 'EPIC-5',
        'EPIC-6-INTEGRATION': 'EPIC-6',
        'EPIC-7-DIFFERENTIATION': 'EPIC-7',
        'EPIC-8-EXEC-COMPLIANCE': 'EPIC-8-EXEC-COMPLIANCE',
        'EPIC-8-PLATFORM-DOMINANCE': 'EPIC-8-PLATFORM-DOMINANCE',
        'EPIC-9-OPERATIONS': 'EPIC-9-OPERATIONS',
        'EPIC-9-POLICY-AI': 'EPIC-9-POLICY-AI',
        'EPIC-11-CARTOGRAPHY-NEBULAGRAPH': 'EPIC-11',
        'EPIC-11-CARTOGRAPHY': 'EPIC-11',
        'EPIC-AUTH-001-unified-scanner-auth': 'EPIC-AUTH-001',
        'EPIC-AUTH-001': 'EPIC-AUTH-001',
    }


def get_story_number(story_id: str) -> Tuple[int, str]:
    """Extract story number from ID like AUTH-001-1 or PLAT-001."""
    # Try various patterns
    patterns = [
        r'-(\d+)([a-z])?$',           # AUTH-001-1, AUTH-001-2a
        r'STORY-(\d+)',               # STORY-001
        r'(\d+)([a-z])?$',            # fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, story_id)
        if match:
            num = int(match.group(1))
            letter = match.group(2) if len(match.groups()) > 1 else ''
            return num, letter or ''
    return 1, ''


def migrate_story(source_file: Path, target_epic_dir: Path, dry_run: bool = True) -> bool:
    """Migrate a single story with full task content."""
    content = source_file.read_text()
    data = parse_story_file(content)

    if not data['id']:
        print(f"  SKIP: Could not parse {source_file.name}")
        return False

    story_id = data['id']
    title = data['title']
    num, letter = get_story_number(story_id)
    slug = slugify(title)

    folder_name = f"{num:02d}{letter}-{slug}"
    story_dir = target_epic_dir / "stories" / folder_name
    tasks_dir = story_dir / "tasks"

    ac_count = len(data['acceptance_criteria'])
    print(f"  {story_id} -> {folder_name}/ ({ac_count} tasks)")

    if dry_run:
        return True

    # Create directories
    story_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir.mkdir(exist_ok=True)

    # Create story file
    story_content = create_story_file(data, folder_name)
    story_file = story_dir / f"story-{folder_name}.md"
    story_file.write_text(story_content)

    # Create task files (one per AC)
    if data['acceptance_criteria']:
        for i, ac in enumerate(data['acceptance_criteria'], 1):
            ac_slug = slugify(ac['title'], 30)
            task_content = create_task_file(data, ac, i)
            task_file = tasks_dir / f"task-{i:02d}-{ac_slug}.md"
            task_file.write_text(task_content)
    else:
        # Create default task
        default_ac = {'id': 'AC1', 'title': 'Implementation', 'content': f'Implement {title}'}
        task_content = create_task_file(data, default_ac, 1)
        task_file = tasks_dir / "task-01-implementation.md"
        task_file.write_text(task_content)

    return True


def main():
    parser = argparse.ArgumentParser(description='Migrate stories with full AI prompts')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--epic', type=str, help='Migrate only specific epic')
    parser.add_argument('--clear', action='store_true', help='Clear target before migration')
    args = parser.parse_args()

    project_root = get_project_root()
    source_dir = project_root / '.bmad' / 'generated-stories'
    target_dir = project_root / '.bmad' / 'epics'

    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print("=" * 60)

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return 1

    # Clear target if requested
    if args.clear and not args.dry_run:
        print("\nClearing existing stories in target...")
        for epic_dir in target_dir.iterdir():
            if epic_dir.is_dir():
                stories_dir = epic_dir / "stories"
                if stories_dir.exists():
                    shutil.rmtree(stories_dir)
                    stories_dir.mkdir()
                    print(f"  Cleared: {epic_dir.name}/stories/")

    epic_mapping = get_epic_mapping()
    total_stories = 0
    total_tasks = 0
    migrated = 0

    for source_epic_dir in sorted(source_dir.iterdir()):
        if not source_epic_dir.is_dir():
            continue

        source_epic_name = source_epic_dir.name

        if args.epic and args.epic not in source_epic_name:
            continue

        target_epic_name = epic_mapping.get(source_epic_name, source_epic_name)
        target_epic_dir = target_dir / target_epic_name

        story_files = sorted([f for f in source_epic_dir.glob("*.md") if f.name != 'README.md'])
        if not story_files:
            continue

        print(f"\n{source_epic_name} -> {target_epic_name} ({len(story_files)} stories)")

        if not args.dry_run:
            (target_epic_dir / "stories").mkdir(parents=True, exist_ok=True)

        for story_file in story_files:
            total_stories += 1
            if migrate_story(story_file, target_epic_dir, args.dry_run):
                migrated += 1
                # Count tasks created
                content = story_file.read_text()
                ac_count = len(re.findall(r'### AC\d+:', content))
                total_tasks += max(ac_count, 1)

    print("\n" + "=" * 60)
    print(f"{'Would migrate' if args.dry_run else 'Migrated'}: {migrated}/{total_stories} stories")
    print(f"{'Would create' if args.dry_run else 'Created'}: ~{total_tasks} task files")

    if args.dry_run:
        print("\nRun without --dry-run to execute")
        print("Add --clear to remove existing stories first")
    else:
        print(f"\nMigration complete!")
        print("\nNext steps:")
        print("1. Verify stories: ls .bmad/epics/*/stories/")
        print("2. Check task content: cat .bmad/epics/EPIC-AUTH-001/stories/*/tasks/task-01-*.md")
        print("3. Archive old directories if satisfied")

    return 0


if __name__ == '__main__':
    exit(main())
