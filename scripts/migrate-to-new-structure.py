#!/usr/bin/env python3
"""
Migrate BMAD artifacts to new directory structure.

Per .bmad/STRUCTURE.md:
  OLD: .bmad/planning-artifacts/epics/EPIC-*-summary.md
       .bmad/planning-artifacts/epics/EPIC-*-full.md

  NEW: .bmad/epics/{EPIC-ID}/README.md         (summary)
       .bmad/epics/{EPIC-ID}/DOCUMENTATION.md  (full)
       .bmad/epics/{EPIC-ID}/stories/          (empty, for stories)

Usage:
  python scripts/migrate-to-new-structure.py --dry-run  # Preview
  python scripts/migrate-to-new-structure.py            # Execute
"""

import os
import re
import shutil
import argparse
from pathlib import Path


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_epic_id(filename: str) -> str:
    """
    Extract EPIC ID from filename.

    Examples:
      EPIC-1-PLATFORM-summary.md -> EPIC-1-PLATFORM
      EPIC-8-EXEC-COMPLIANCE-full.md -> EPIC-8-EXEC-COMPLIANCE
      EPIC-AUTH-001-summary.md -> EPIC-AUTH-001
      EPIC-11-summary.md -> EPIC-11
    """
    # Remove -summary.md or -full.md suffix
    name = filename.replace('-summary.md', '').replace('-full.md', '')
    return name


def find_epic_pairs(source_dir: Path) -> dict:
    """
    Find matching summary/full file pairs.

    Returns: {epic_id: {'summary': path, 'full': path}}
    """
    pairs = {}

    for f in source_dir.glob("EPIC-*.md"):
        filename = f.name
        epic_id = get_epic_id(filename)

        if epic_id not in pairs:
            pairs[epic_id] = {'summary': None, 'full': None}

        if '-summary.md' in filename:
            pairs[epic_id]['summary'] = f
        elif '-full.md' in filename:
            pairs[epic_id]['full'] = f

    return pairs


def migrate_epic(epic_id: str, files: dict, target_dir: Path, dry_run: bool = True) -> bool:
    """Migrate a single epic to new structure."""
    epic_dir = target_dir / epic_id

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {epic_id}")

    # Create epic directory
    if not dry_run:
        epic_dir.mkdir(parents=True, exist_ok=True)
        (epic_dir / 'stories').mkdir(exist_ok=True)
    print(f"  Create: {epic_dir}/")
    print(f"  Create: {epic_dir}/stories/")

    # Copy summary -> README.md
    if files.get('summary'):
        target = epic_dir / 'README.md'
        print(f"  Copy: {files['summary'].name} -> README.md")
        if not dry_run:
            shutil.copy2(files['summary'], target)
    else:
        print(f"  WARNING: No summary file for {epic_id}")

    # Copy full -> DOCUMENTATION.md
    if files.get('full'):
        target = epic_dir / 'DOCUMENTATION.md'
        print(f"  Copy: {files['full'].name} -> DOCUMENTATION.md")
        if not dry_run:
            shutil.copy2(files['full'], target)
    else:
        print(f"  WARNING: No full file for {epic_id}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Migrate BMAD artifacts to new structure')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    args = parser.parse_args()

    project_root = get_project_root()
    source_dir = project_root / '.bmad' / 'planning-artifacts' / 'epics'
    target_dir = project_root / '.bmad' / 'epics'

    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print("=" * 60)

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return 1

    # Find all epic file pairs
    pairs = find_epic_pairs(source_dir)
    print(f"\nFound {len(pairs)} epics to migrate:")
    for epic_id in sorted(pairs.keys()):
        files = pairs[epic_id]
        summary = "YES" if files['summary'] else "NO"
        full = "YES" if files['full'] else "NO"
        print(f"  {epic_id}: summary={summary}, full={full}")

    # Create target directory
    if not args.dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    # Migrate each epic
    success = 0
    for epic_id in sorted(pairs.keys()):
        if migrate_epic(epic_id, pairs[epic_id], target_dir, args.dry_run):
            success += 1

    print("\n" + "=" * 60)
    print(f"Migration {'preview' if args.dry_run else 'complete'}: {success}/{len(pairs)} epics")

    if args.dry_run:
        print("\nTo execute migration, run without --dry-run flag")
    else:
        print(f"\nNew structure created at: {target_dir}")
        print("\nNext steps:")
        print("1. Verify files in .bmad/epics/")
        print("2. Update references in workflows")
        print("3. Run /jira-sync to sync with JIRA")

    return 0


if __name__ == '__main__':
    exit(main())
