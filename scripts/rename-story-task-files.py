#!/usr/bin/env python3
"""
Rename story and task files to new naming convention.

Story: README.md -> story-{folder-slug}.md
Task: {NN}-{slug}.md -> task-{NN}-{slug}.md

Usage:
  python scripts/rename-story-task-files.py --dry-run  # Preview
  python scripts/rename-story-task-files.py            # Execute
"""

import os
import re
import argparse
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def rename_files(epics_dir: Path, dry_run: bool = True):
    """Rename all story and task files."""

    stories_renamed = 0
    tasks_renamed = 0

    # Find all story directories
    for epic_dir in sorted(epics_dir.iterdir()):
        if not epic_dir.is_dir():
            continue

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        print(f"\n{epic_dir.name}")

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            folder_name = story_dir.name  # e.g., "01-clickhouse-helm-chart-deployment"

            # Rename README.md -> story-{folder-slug}.md
            readme_file = story_dir / "README.md"
            if readme_file.exists():
                new_story_name = f"story-{folder_name}.md"
                new_story_path = story_dir / new_story_name

                print(f"  {folder_name}/README.md -> {new_story_name}")

                if not dry_run:
                    readme_file.rename(new_story_path)
                stories_renamed += 1

            # Rename task files: {NN}-{slug}.md -> task-{NN}-{slug}.md
            tasks_dir = story_dir / "tasks"
            if tasks_dir.exists():
                for task_file in sorted(tasks_dir.glob("*.md")):
                    if task_file.name.startswith("task-"):
                        continue  # Already renamed

                    new_task_name = f"task-{task_file.name}"
                    new_task_path = tasks_dir / new_task_name

                    if not dry_run:
                        task_file.rename(new_task_path)
                    tasks_renamed += 1

    return stories_renamed, tasks_renamed


def main():
    parser = argparse.ArgumentParser(description='Rename story and task files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    args = parser.parse_args()

    project_root = get_project_root()
    epics_dir = project_root / '.bmad' / 'epics'

    print(f"Epics directory: {epics_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print("=" * 60)

    stories, tasks = rename_files(epics_dir, args.dry_run)

    print("\n" + "=" * 60)
    print(f"{'Would rename' if args.dry_run else 'Renamed'}:")
    print(f"  - {stories} story files (README.md -> story-*.md)")
    print(f"  - {tasks} task files ({'{NN}'}-*.md -> task-{'{NN}'}-*.md)")

    if args.dry_run:
        print("\nRun without --dry-run to execute")


if __name__ == '__main__':
    main()
