#!/usr/bin/env python3
"""
Migrate generated stories to new BMAD structure.

Source: .bmad/generated-stories/{EPIC}/{STORY-ID}.md
Target: .bmad/epics/{EPIC}/stories/{NN}-{slug}/README.md
        .bmad/epics/{EPIC}/stories/{NN}-{slug}/tasks/{NN}-{slug}.md

Per .bmad/STRUCTURE.md:
- Story folders: {NN}-{slug}/ (e.g., 01-clickhouse-helm-deployment/)
- Task files: {NN}-{slug}.md (e.g., 01-helm-chart-config.md)

Usage:
  python scripts/migrate-stories-to-structure.py --dry-run  # Preview
  python scripts/migrate-stories-to-structure.py            # Execute
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Trim hyphens from ends
    return text.strip('-')[:50]  # Limit length


def extract_story_metadata(content: str) -> Dict:
    """Extract metadata from story file."""
    metadata = {
        'id': '',
        'title': '',
        'type': 'engineering',
        'priority': 'P2',
        'points': 3,
        'sprint': 1,
        'wave': 1,
    }

    # Extract title from first heading
    title_match = re.search(r'^#\s+(\S+):\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['id'] = title_match.group(1)
        metadata['title'] = title_match.group(2).strip()

    # Extract YAML metadata block
    yaml_match = re.search(r'```yaml\s*\nstory:\s*\n(.*?)```', content, re.DOTALL)
    if yaml_match:
        try:
            yaml_content = yaml_match.group(0).replace('```yaml', '').replace('```', '')
            parsed = yaml.safe_load(yaml_content)
            if parsed and 'story' in parsed:
                metadata.update(parsed['story'])
            if parsed and 'metadata' in parsed:
                metadata.update(parsed['metadata'])
        except:
            pass

    return metadata


def extract_functional_requirements(content: str) -> List[Dict]:
    """Extract functional requirements as tasks."""
    tasks = []

    # Find all FR sections
    fr_pattern = r'###\s+FR-(\d+):\s+(.+?)(?=\n\n|\n###|\n---|\Z)'
    matches = re.finditer(fr_pattern, content, re.DOTALL)

    for match in matches:
        fr_num = match.group(1)
        fr_content = match.group(2).strip()

        # Get FR title (first line)
        lines = fr_content.split('\n')
        title = lines[0].strip() if lines else f"Functional Requirement {fr_num}"

        tasks.append({
            'num': int(fr_num),
            'title': title,
            'content': fr_content
        })

    return tasks


def extract_acceptance_criteria(content: str) -> List[Dict]:
    """Extract acceptance criteria."""
    criteria = []

    # Find AC sections
    ac_pattern = r'###\s+AC-(\d+):\s+(.+?)```gherkin\s*\n(.+?)```'
    matches = re.finditer(ac_pattern, content, re.DOTALL)

    for match in matches:
        ac_num = match.group(1)
        ac_title = match.group(2).strip()
        ac_gherkin = match.group(3).strip()

        criteria.append({
            'num': int(ac_num),
            'title': ac_title,
            'gherkin': ac_gherkin
        })

    return criteria


def get_epic_mapping() -> Dict[str, str]:
    """Map generated-stories epic names to .bmad/epics names."""
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


def create_story_readme(metadata: Dict, content: str, criteria: List[Dict], tasks: List[Dict]) -> str:
    """Create story README.md content."""
    story_id = metadata.get('id', 'STORY-001')
    title = metadata.get('title', 'Story Title')
    points = metadata.get('points', 3)
    priority = metadata.get('priority', 'P2')
    sprint = metadata.get('sprint', 1)

    # Build acceptance criteria section
    ac_section = ""
    for ac in criteria:
        ac_section += f"""
### AC-{ac['num']}: {ac['title']}

```gherkin
{ac['gherkin']}
```
"""

    # Build tasks table
    task_rows = ""
    for i, task in enumerate(tasks, 1):
        slug = slugify(task['title'])[:30]
        task_rows += f"| T{i} | [{i:02d}-{slug}.md](./tasks/{i:02d}-{slug}.md) | {task['title'][:40]} | AC-{task['num']} | pending |\n"

    if not task_rows:
        task_rows = "| T1 | [01-implementation.md](./tasks/01-implementation.md) | Implementation | AC-1 | pending |\n"

    return f"""# {story_id}: {title}

**Epic:** {metadata.get('parent', 'EPIC-1')} | **Points:** {points} | **Priority:** {priority} | **Sprint:** {sprint}
**Status:** ready-for-dev

---

## Story

{extract_story_statement(content)}

---

## Acceptance Criteria
{ac_section if ac_section else "### AC-1: Implementation Complete\\n\\nAll functional requirements implemented and tested."}

---

## Tasks

| # | Task File | Title | Linked AC | Status |
|---|-----------|-------|-----------|--------|
{task_rows}
---

## Technical Notes

See full story documentation for implementation details.

---

## AI Implementation Prompt

```
You are implementing {story_id}: {title}.

See the original story file for detailed AI prompts and implementation guidance.
```
"""


def extract_story_statement(content: str) -> str:
    """Extract story statement (As a... I want... So that...)."""
    # Try to find As a/I want/So that pattern
    pattern = r'As a[n]?\s+(.+?),\s*\n?\s*I want\s+(.+?),\s*\n?\s*[Ss]o that\s+(.+?)(?:\.|$)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        role = match.group(1).strip()
        action = match.group(2).strip()
        benefit = match.group(3).strip()
        return f"As a {role}, I want {action}, so that {benefit}."

    # Fallback: use goal or problem statement
    goal_match = re.search(r'##\s+Goal\s*\n+(.+?)(?=\n##|\n---|\Z)', content, re.DOTALL)
    if goal_match:
        return goal_match.group(1).strip().split('\n')[0]

    return "As a developer, I want to implement this feature, so that the system functionality is enhanced."


def create_task_file(task: Dict, story_id: str, story_title: str) -> str:
    """Create task file content."""
    task_num = task['num']
    task_title = task['title']

    return f"""# {story_id}-T{task_num}: {task_title}

**Story:** {story_id}
**Linked to:** AC-{task_num}
**Estimated:** 2 hours
**Status:** pending

---

## Description

{task['content'][:500] if task.get('content') else task_title}

---

## Target Files

- See AI Implementation Prompt in story README.md

---

## Subtasks

| # | Description | Status |
|---|-------------|--------|
| S1 | Implement core functionality | pending |
| S2 | Write unit tests | pending |
| S3 | Integration test | pending |

---

## Done When

- [ ] Functional requirement implemented
- [ ] Tests passing
- [ ] No regressions
- [ ] Code reviewed
"""


def get_story_number(story_id: str) -> Tuple[int, str]:
    """Extract story number and optional letter from ID like PLAT-001 or AUTH-001-2a."""
    # Pattern: PREFIX-NNN or PREFIX-NNN-N or PREFIX-NNN-Na
    match = re.search(r'-(\d+)([a-z])?$', story_id)
    if match:
        num = int(match.group(1))
        letter = match.group(2) or ''
        return num, letter
    return 1, ''


def migrate_story(
    source_file: Path,
    target_epic_dir: Path,
    dry_run: bool = True
) -> bool:
    """Migrate a single story to new structure."""

    # Read source content
    content = source_file.read_text()

    # Extract metadata
    metadata = extract_story_metadata(content)
    story_id = metadata.get('id', source_file.stem)
    title = metadata.get('title', 'Untitled Story')

    # Get story number for folder naming
    num, letter = get_story_number(story_id)
    slug = slugify(title)

    # Create folder name: {NN}{letter}-{slug}/
    folder_name = f"{num:02d}{letter}-{slug}"
    story_dir = target_epic_dir / "stories" / folder_name
    tasks_dir = story_dir / "tasks"

    print(f"  {story_id} -> {folder_name}/")

    if dry_run:
        return True

    # Create directories
    story_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir.mkdir(exist_ok=True)

    # Extract acceptance criteria and functional requirements
    criteria = extract_acceptance_criteria(content)
    tasks = extract_functional_requirements(content)

    # Create README.md
    readme_content = create_story_readme(metadata, content, criteria, tasks)
    (story_dir / "README.md").write_text(readme_content)

    # Create task files
    if tasks:
        for task in tasks:
            task_slug = slugify(task['title'])[:30]
            task_file = tasks_dir / f"{task['num']:02d}-{task_slug}.md"
            task_content = create_task_file(task, story_id, title)
            task_file.write_text(task_content)
    else:
        # Create default implementation task
        task_file = tasks_dir / "01-implementation.md"
        task_content = create_task_file(
            {'num': 1, 'title': 'Implementation', 'content': f'Implement {title}'},
            story_id, title
        )
        task_file.write_text(task_content)

    return True


def main():
    parser = argparse.ArgumentParser(description='Migrate stories to new BMAD structure')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--epic', type=str, help='Migrate only specific epic')
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

    epic_mapping = get_epic_mapping()

    total_stories = 0
    migrated_stories = 0

    # Process each epic
    for source_epic_dir in sorted(source_dir.iterdir()):
        if not source_epic_dir.is_dir():
            continue

        source_epic_name = source_epic_dir.name

        # Filter by epic if specified
        if args.epic and args.epic not in source_epic_name:
            continue

        # Map to target epic
        target_epic_name = epic_mapping.get(source_epic_name, source_epic_name)
        target_epic_dir = target_dir / target_epic_name

        # Get story files
        story_files = sorted(source_epic_dir.glob("*.md"))
        story_files = [f for f in story_files if f.name != 'README.md']

        if not story_files:
            continue

        print(f"\n{source_epic_name} -> {target_epic_name} ({len(story_files)} stories)")

        # Ensure target epic directory exists
        if not args.dry_run:
            (target_epic_dir / "stories").mkdir(parents=True, exist_ok=True)

        for story_file in story_files:
            total_stories += 1
            if migrate_story(story_file, target_epic_dir, args.dry_run):
                migrated_stories += 1

    print("\n" + "=" * 60)
    print(f"Migration {'preview' if args.dry_run else 'complete'}: {migrated_stories}/{total_stories} stories")

    if args.dry_run:
        print("\nTo execute migration, run without --dry-run flag")
    else:
        print(f"\nStories migrated to: {target_dir}")
        print("\nNext steps:")
        print("1. Verify stories in .bmad/epics/*/stories/")
        print("2. Review task files in tasks/ subdirectories")
        print("3. Run /jira-sync to sync with JIRA")

    return 0


if __name__ == '__main__':
    exit(main())
