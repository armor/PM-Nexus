#!/usr/bin/env python3
"""
Simplify BMAD Stories for JIRA Sync

Converts verbose 600+ line stories into clean ~50-80 line format
with proper Task and Subtask breakdown for JIRA hierarchy:

  Epic → Story → Task → Sub-task

Usage:
  python scripts/simplify-stories.py --dry-run           # Preview
  python scripts/simplify-stories.py --epic EPIC-5-UX    # Single epic
  python scripts/simplify-stories.py                     # All epics
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / ".bmad/generated-stories"
OUTPUT_DIR = PROJECT_ROOT / ".bmad/jira-stories"


def parse_verbose_story(filepath: Path) -> Optional[Dict]:
    """Parse a verbose story file and extract key information."""
    content = filepath.read_text()

    story = {
        "file": filepath.name,
        "id": "",
        "title": "",
        "epic": "",
        "priority": "P2",
        "points": 0,
        "sprint": 1,
        "description": "",
        "acceptance_criteria": [],
        "functional_requirements": [],
        "in_scope": [],
        "files": []
    }

    # Extract YAML metadata
    yaml_match = re.search(r'```yaml\s*\n(story:.*?)```', content, re.DOTALL)
    if yaml_match:
        try:
            metadata = yaml.safe_load(yaml_match.group(1))
            if "story" in metadata:
                story["id"] = metadata["story"].get("id", "")
                story["title"] = metadata["story"].get("title", "").strip('"')
            if "metadata" in metadata:
                meta = metadata["metadata"]
                story["epic"] = meta.get("parent", "")
                story["priority"] = meta.get("priority", "P2")
                story["points"] = meta.get("points", 0)
                story["sprint"] = meta.get("sprint", 1)
        except yaml.YAMLError:
            pass

    # Extract title from header if not in YAML
    if not story["id"]:
        title_match = re.search(r'^# ([A-Z]+-\d+): (.+)$', content, re.MULTILINE)
        if title_match:
            story["id"] = title_match.group(1)
            story["title"] = title_match.group(2).strip()

    # Extract description (Problem Statement or first paragraph)
    desc_match = re.search(r'## Problem Statement\s+([^#\n`].+?)(?=\n###|\n---|\n##|\n```)', content, re.DOTALL)
    if desc_match:
        story["description"] = desc_match.group(1).strip()[:300]

    # Extract In Scope items
    scope_match = re.search(r'### In Scope\s+(.+?)(?=\n###|\n---|\n##)', content, re.DOTALL)
    if scope_match:
        scope_items = re.findall(r'^- (.+)$', scope_match.group(1), re.MULTILINE)
        story["in_scope"] = [item.strip() for item in scope_items[:10]]

    # Extract Functional Requirements
    fr_matches = re.findall(r'### FR-(\d+): (.+?)(?=\n###|\n---|\n##|\Z)', content, re.DOTALL)
    for fr_num, fr_content in fr_matches:
        fr_title_match = re.search(r'^(.+?)(?:\n|$)', fr_content.strip())
        if fr_title_match:
            story["functional_requirements"].append({
                "id": f"FR-{fr_num}",
                "title": fr_title_match.group(1).strip()[:100]
            })

    # Extract GIVEN-WHEN-THEN acceptance criteria
    ac_section = re.search(r'## Acceptance Criteria \(GIVEN-WHEN-THEN\)\s+(.+?)(?=\n---|\n## |\Z)', content, re.DOTALL)
    if ac_section:
        ac_blocks = re.findall(r'### AC-(\d+): (.+?)```gherkin\s*\n(.+?)```', ac_section.group(1), re.DOTALL)
        for ac_num, ac_title, gherkin in ac_blocks:
            # Extract THEN clauses as acceptance criteria
            then_matches = re.findall(r'THEN (.+?)(?=\n|$)', gherkin)
            for then_clause in then_matches:
                story["acceptance_criteria"].append(then_clause.strip()[:150])

    # Fallback: extract any checkbox acceptance criteria
    if not story["acceptance_criteria"]:
        ac_match = re.search(r'## Acceptance Criteria\s+(.+?)(?=\n---|\n##)', content, re.DOTALL)
        if ac_match:
            criteria = re.findall(r'- \[[ x]\] (.+?)$', ac_match.group(1), re.MULTILINE)
            story["acceptance_criteria"] = [c.strip()[:150] for c in criteria[:10]]

    # Extract target files
    files_match = re.search(r'## Target Files\s+```\s*\n(.+?)```', content, re.DOTALL)
    if files_match:
        file_lines = re.findall(r'^\s*(\S+\.\w+)\s', files_match.group(1), re.MULTILINE)
        story["files"] = file_lines[:10]

    return story if story["id"] else None


def generate_tasks_from_story(story: Dict) -> List[Dict]:
    """Generate tasks and subtasks from story content."""
    tasks = []

    # Strategy 1: Use Functional Requirements as tasks
    if story["functional_requirements"]:
        for i, fr in enumerate(story["functional_requirements"], 1):
            task = {
                "id": f"T{i}",
                "title": fr["title"],
                "subtasks": []
            }
            # Generate subtasks from the requirement
            task["subtasks"].append({"id": "S1", "title": f"Implement {fr['title'][:50]}"})
            task["subtasks"].append({"id": "S2", "title": "Write unit tests"})
            task["subtasks"].append({"id": "S3", "title": "Update documentation"})
            tasks.append(task)

    # Strategy 2: Use In Scope items as tasks
    elif story["in_scope"]:
        for i, scope in enumerate(story["in_scope"], 1):
            task = {
                "id": f"T{i}",
                "title": scope[:80],
                "subtasks": [
                    {"id": "S1", "title": f"Implement: {scope[:40]}"},
                    {"id": "S2", "title": "Test implementation"},
                ]
            }
            tasks.append(task)

    # Strategy 3: Generate generic tasks from acceptance criteria
    else:
        # Group acceptance criteria into tasks
        for i, ac in enumerate(story["acceptance_criteria"][:5], 1):
            task = {
                "id": f"T{i}",
                "title": f"Implement: {ac[:60]}",
                "subtasks": [
                    {"id": "S1", "title": ac[:80]},
                    {"id": "S2", "title": "Verify with tests"},
                ]
            }
            tasks.append(task)

    # Always add a final testing task
    if tasks:
        tasks.append({
            "id": f"T{len(tasks) + 1}",
            "title": "Final Testing & Documentation",
            "subtasks": [
                {"id": "S1", "title": "Run all unit tests"},
                {"id": "S2", "title": "Run integration tests"},
                {"id": "S3", "title": "Update README if needed"},
            ]
        })

    return tasks


def generate_simplified_story(story: Dict) -> str:
    """Generate simplified markdown for JIRA sync."""
    tasks = generate_tasks_from_story(story)

    # Calculate task points distribution
    total_points = story["points"] or 1
    points_per_task = round(total_points / max(len(tasks), 1), 1)

    lines = [
        f"# {story['id']}: {story['title']}",
        "",
        f"**Epic:** {story['epic']} | **Points:** {story['points']} | **Priority:** {story['priority']} | **Sprint:** {story['sprint']}",
        "",
        "## Description",
        story["description"] or "No description available.",
        "",
        "## Acceptance Criteria",
    ]

    for ac in story["acceptance_criteria"][:8]:
        lines.append(f"- [ ] {ac}")

    if not story["acceptance_criteria"]:
        lines.append("- [ ] All functional requirements implemented")
        lines.append("- [ ] Tests passing")

    lines.extend(["", "## Tasks", ""])

    for task in tasks:
        lines.append(f"### {task['id']}: {task['title']} ({points_per_task} pts)")
        for st in task["subtasks"]:
            lines.append(f"- [ ] {st['id']}: {st['title']}")
        lines.append("")

    if story["files"]:
        lines.extend(["## Files"])
        for f in story["files"][:8]:
            lines.append(f"- `{f}`")

    return "\n".join(lines)


def process_epic_directory(epic_dir: Path, output_dir: Path, dry_run: bool = False) -> Dict:
    """Process all stories in an epic directory."""
    results = {"processed": 0, "skipped": 0, "errors": []}

    epic_name = epic_dir.name
    output_epic_dir = output_dir / epic_name

    if not dry_run:
        output_epic_dir.mkdir(parents=True, exist_ok=True)

    story_files = sorted(epic_dir.glob("*.md"))
    print(f"\n  Processing {epic_name}: {len(story_files)} stories")

    for story_file in story_files:
        if story_file.name == "README.md":
            continue

        try:
            story = parse_verbose_story(story_file)
            if not story:
                results["skipped"] += 1
                continue

            simplified = generate_simplified_story(story)
            output_file = output_epic_dir / story_file.name

            if dry_run:
                print(f"    [DRY] {story_file.name}: {len(simplified.splitlines())} lines")
            else:
                output_file.write_text(simplified)
                print(f"    ✓ {story_file.name}: {len(simplified.splitlines())} lines")

            results["processed"] += 1

        except Exception as e:
            results["errors"].append(f"{story_file.name}: {e}")
            print(f"    ✗ {story_file.name}: {e}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simplify BMAD stories for JIRA")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--epic", type=str, help="Process single epic (e.g., EPIC-5-UX)")
    parser.add_argument("--sample", action="store_true", help="Show sample output for one story")
    args = parser.parse_args()

    if not INPUT_DIR.exists():
        print(f"ERROR: Input directory not found: {INPUT_DIR}")
        return

    if args.sample:
        # Show sample conversion
        sample_dirs = list(INPUT_DIR.iterdir())
        if sample_dirs:
            sample_stories = list(sample_dirs[0].glob("*.md"))
            if sample_stories:
                story = parse_verbose_story(sample_stories[0])
                if story:
                    print("=" * 60)
                    print("SAMPLE CONVERSION")
                    print("=" * 60)
                    print(f"Original: {sample_stories[0]} ({sample_stories[0].stat().st_size} bytes)")
                    print("-" * 60)
                    simplified = generate_simplified_story(story)
                    print(simplified)
                    print("-" * 60)
                    print(f"Simplified: {len(simplified.splitlines())} lines")
        return

    print("=" * 60)
    print("BMAD Story Simplifier")
    print(f"Input:  {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)

    total = {"processed": 0, "skipped": 0, "errors": []}

    epic_dirs = sorted([d for d in INPUT_DIR.iterdir() if d.is_dir()])

    for epic_dir in epic_dirs:
        if args.epic and args.epic not in epic_dir.name:
            continue

        results = process_epic_directory(epic_dir, OUTPUT_DIR, args.dry_run)
        total["processed"] += results["processed"]
        total["skipped"] += results["skipped"]
        total["errors"].extend(results["errors"])

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {total['processed']}")
    print(f"Skipped:   {total['skipped']}")
    print(f"Errors:    {len(total['errors'])}")

    if not args.dry_run:
        print(f"\nOutput written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
