#!/usr/bin/env python3
"""
JIRA Post-Import Reference Fix Script

This script runs AFTER all epics have been synced to JIRA.
It resolves ALL references (including circular and cross-epic) by:

1. Building complete mappings from ALL synced epics
2. Converting ALL remaining non-JIRA refs to JIRA keys
3. Updating JIRA descriptions with corrected content
4. Creating missing dependency links
5. Validating everything is now using JIRA keys

The Two-Phase Approach:
=======================
Phase 1: jira-sync-all.py --epic all
  - Creates all issues in JIRA
  - Converts INTRA-epic refs only
  - Cross-epic refs remain as EPIC-1-PLATFORM, etc.

Phase 2: jira-post-import-fix.py (THIS SCRIPT)
  - Builds complete mapping of ALL issues -> JIRA keys
  - Converts ALL remaining refs to JIRA keys
  - Handles circular refs (A->B->A) because both exist
  - Updates JIRA with final content

Usage:
    python jira-post-import-fix.py                  # Fix all epics
    python jira-post-import-fix.py --validate-only  # Just check
    python jira-post-import-fix.py --dry-run        # Show what would change
    python jira-post-import-fix.py --no-jira-update # Local only, no JIRA API calls
"""

import argparse
import os
import re
import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

# Import ADF converter
sys.path.insert(0, str(Path(__file__).parent))
from markdown_to_adf import markdown_to_adf

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"
REPORT_DIR = PROJECT_ROOT / ".bmad/data"

# Jira Configuration
def load_dotenv():
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_dotenv()

SITE = os.getenv("ATLASSIAN_SITE", "armor-defense.atlassian.net")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "ARGUS")

BASE_URL = f"https://{SITE}/rest/api/3"
AUTH = (EMAIL, API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


@dataclass
class ReferenceMapping:
    """Complete mapping of all identifiers to JIRA keys."""
    # Epic mappings: EPIC-AUTH-001 -> ARGUS-1338
    epics: Dict[str, str] = field(default_factory=dict)
    # Story mappings: AUTH-001-1 -> ARGUS-1339 (full IDs only)
    stories: Dict[str, str] = field(default_factory=dict)
    # Per-epic story mappings: (epic_name, S1) -> ARGUS-1339
    stories_by_epic: Dict[Tuple[str, str], str] = field(default_factory=dict)
    # Task mappings: AUTH-001-1-T1 -> ARGUS-1347, (story_dir, T1) -> ARGUS-1347
    tasks: Dict[str, str] = field(default_factory=dict)
    # Task tuple mappings for local refs
    task_tuples: Dict[Tuple[str, str], str] = field(default_factory=dict)


@dataclass
class FixResult:
    """Result of the fix operation."""
    epics_fixed: int = 0
    stories_fixed: int = 0
    tasks_fixed: int = 0
    links_created: int = 0
    jira_updated: int = 0
    unresolved_refs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class JiraClient:
    """JIRA API client with rate limiting and retry."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        if enabled:
            self.session = requests.Session()
            self.session.auth = AUTH
            self.session.headers.update(HEADERS)

    def request(self, method: str, endpoint: str, data: dict = None) -> Any:
        """Make request with retry and rate limiting."""
        if not self.enabled:
            return {}

        url = f"{BASE_URL}{endpoint}"
        for attempt in range(3):
            try:
                time.sleep(0.25)  # Rate limiting
                if data:
                    resp = self.session.request(method, url, json=data, timeout=30)
                else:
                    resp = self.session.request(method, url, timeout=30)
                if resp.ok:
                    return resp.json() if resp.content else {}
                if resp.status_code == 429:  # Rate limited
                    time.sleep(2)
                    continue
                raise Exception(f"JIRA API error {resp.status_code}: {resp.text[:300]}")
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise

    def update_issue(self, key: str, fields: dict) -> bool:
        """Update JIRA issue fields."""
        if not self.enabled:
            return True
        try:
            self.request("PUT", f"/issue/{key}", {"fields": fields})
            return True
        except Exception as e:
            print(f"    ERROR updating {key}: {e}")
            return False

    def create_link(self, from_key: str, to_key: str, link_type: str = "Blocks") -> bool:
        """Create issue link."""
        if not self.enabled:
            return True
        try:
            self.request("POST", "/issueLink", {
                "type": {"name": link_type},
                "inwardIssue": {"key": from_key},
                "outwardIssue": {"key": to_key}
            })
            return True
        except Exception:
            return False

    def get_existing_links(self, issue_key: str) -> Set[str]:
        """Get existing link targets for an issue."""
        if not self.enabled:
            return set()
        try:
            result = self.request("GET", f"/issue/{issue_key}?fields=issuelinks")
            links = set()
            for link in result.get("fields", {}).get("issuelinks", []):
                if "outwardIssue" in link:
                    links.add(link["outwardIssue"]["key"])
                if "inwardIssue" in link:
                    links.add(link["inwardIssue"]["key"])
            return links
        except Exception:
            return set()


def extract_jira_key(content: str) -> str:
    """Extract JIRA key from file content."""
    match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
    return match.group(1) if match else ""


def is_jira_key(ref: str) -> bool:
    """Check if reference is already a JIRA key."""
    return bool(re.match(r'^[A-Z]+-\d+$', ref.strip()))


def build_complete_mapping(epic_dirs: List[Path]) -> ReferenceMapping:
    """Build complete mapping of ALL identifiers to JIRA keys."""
    mapping = ReferenceMapping()

    for epic_dir in epic_dirs:
        if not epic_dir.is_dir():
            continue

        # Epic mapping
        readme = epic_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            jira_key = extract_jira_key(content)
            if jira_key:
                mapping.epics[epic_dir.name] = jira_key
                # Also map variations
                name = epic_dir.name
                if name.startswith("EPIC-"):
                    mapping.epics[name[5:]] = jira_key  # "AUTH-001" -> ARGUS-XXX
                    # Handle "EPIC-1-PLATFORM" -> just "1-PLATFORM"
                    if "-" in name[5:]:
                        short = name[5:].split("-")[0]  # "1"
                        mapping.epics[short] = jira_key

        # Story and task mappings
        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            story_files = list(story_dir.glob("story-*.md"))
            if not story_files:
                continue

            content = story_files[0].read_text()
            jira_key = extract_jira_key(content)

            # Extract story ID (e.g., AUTH-001-1, AUTH-001-2a, PLAT-004, GRAPH-001)
            # Try multiple patterns
            id_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[a-z]?):', content, re.MULTILINE)

            # Always map by directory and extract number from dir name for per-epic mapping
            epic_name = epic_dir.name
            mapping.stories[story_dir.name] = jira_key

            # Extract story number from directory name (e.g., "04" from "04-clickhouse-backup-cronjob")
            dir_num_match = re.match(r'^(\d+)', story_dir.name)
            if dir_num_match and jira_key:
                dir_num = dir_num_match.group(1).lstrip("0") or "0"
                mapping.stories_by_epic[(epic_name, dir_num)] = jira_key
                mapping.stories_by_epic[(epic_name, f"S{dir_num}")] = jira_key

            if id_match and jira_key:
                story_id = id_match.group(1)
                mapping.stories[story_id] = jira_key

                # Map short forms per-epic (1, 2a, S1, S2a)
                num = story_id.split("-")[-1]  # "1", "2a", "004", etc.
                # Strip leading zeros
                num_stripped = num.lstrip("0") or "0"
                mapping.stories_by_epic[(epic_name, num_stripped)] = jira_key
                mapping.stories_by_epic[(epic_name, f"S{num_stripped}")] = jira_key

            # Task mappings
            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                content = task_file.read_text()
                task_jira_key = extract_jira_key(content)

                if not task_jira_key:
                    continue

                # Extract task number from filename (e.g., "01" from "task-01-origin-config.md")
                task_num_match = re.match(r'task-(\d+)', task_file.name)
                if task_num_match:
                    task_num = task_num_match.group(1).lstrip("0") or "1"
                    # Map T1, T2, etc. to JIRA key for this story
                    mapping.task_tuples[(story_dir.name, f"T{task_num}")] = task_jira_key

                # Also try to extract task ID from content for full ID mappings
                # Patterns: AUTH-001-1-T1, POLICY-001-T1, PLAT-024-T1
                task_id_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[a-z]?-T\d+):', content, re.MULTILINE)
                if task_id_match:
                    task_id = task_id_match.group(1)
                    mapping.tasks[task_id] = task_jira_key

                    # Also map short form (T1, T2) from the ID
                    t_num = task_id.split("-T")[-1] if "-T" in task_id else ""
                    if t_num:
                        mapping.task_tuples[(story_dir.name, f"T{t_num}")] = task_jira_key

    return mapping


def convert_reference(ref: str, mapping: ReferenceMapping, context: dict = None) -> Tuple[str, bool]:
    """
    Convert a single reference to JIRA key.
    Returns (converted_ref, was_converted).
    context contains story_dir_name for task-local refs.
    """
    ref = ref.strip()

    # Already a JIRA key
    if is_jira_key(ref):
        return ref, False

    # Skip none/empty
    if ref.lower() in ["", "-", "none", "n/a"]:
        return ref, False

    # Try epic mapping (EPIC-1-PLATFORM, 1-PLATFORM, etc.)
    if ref in mapping.epics:
        return mapping.epics[ref], True
    if ref.startswith("EPIC-") and ref[5:] in mapping.epics:
        return mapping.epics[ref[5:]], True

    # Try story mapping (AUTH-001-1, full IDs)
    if ref in mapping.stories:
        return mapping.stories[ref], True

    # Try per-epic story mapping (S1, S2, 1, 2, etc.)
    epic_name = context.get("epic_name") if context else None
    if epic_name:
        # Try S-prefixed form
        if ref.startswith("S") and ref[1:].isalnum():
            if (epic_name, ref) in mapping.stories_by_epic:
                return mapping.stories_by_epic[(epic_name, ref)], True
            if (epic_name, ref[1:]) in mapping.stories_by_epic:
                return mapping.stories_by_epic[(epic_name, ref[1:])], True
        # Try bare number
        if ref.isdigit() or (len(ref) > 0 and ref[0].isdigit()):
            if (epic_name, ref) in mapping.stories_by_epic:
                return mapping.stories_by_epic[(epic_name, ref)], True
            if (epic_name, f"S{ref}") in mapping.stories_by_epic:
                return mapping.stories_by_epic[(epic_name, f"S{ref}")], True

    # Try task mapping (AUTH-001-1-T1, T1, etc.)
    if ref in mapping.tasks:
        return mapping.tasks[ref], True

    # Try task tuple mapping (context-dependent)
    if context and "story_dir_name" in context:
        story_dir = context["story_dir_name"]
        if (story_dir, ref) in mapping.task_tuples:
            return mapping.task_tuples[(story_dir, ref)], True

    # Couldn't convert
    return ref, False


def fix_references_in_content(
    content: str,
    mapping: ReferenceMapping,
    context: dict = None,
    field_names: List[str] = None
) -> Tuple[str, int, List[str]]:
    """
    Fix all references in content.
    Returns (fixed_content, num_fixed, unresolved_refs).
    """
    if field_names is None:
        field_names = ["Depends On", "Blocks", "Requires", "Unlocks"]

    num_fixed = 0
    unresolved = []

    for field_name in field_names:
        pattern = rf'(\|\s*{re.escape(field_name)}\s*\|\s*)([^|]+)(\|)'

        def replace_refs(match):
            nonlocal num_fixed, unresolved
            prefix, refs_str, suffix = match.group(1), match.group(2), match.group(3)

            refs_str = refs_str.strip()
            if refs_str.lower() in ["", "-", "none", "n/a"]:
                return match.group(0)

            refs = [r.strip() for r in refs_str.split(",")]
            converted = []
            any_converted = False

            for ref in refs:
                new_ref, was_converted = convert_reference(ref, mapping, context)
                converted.append(new_ref)
                if was_converted:
                    any_converted = True
                elif not is_jira_key(new_ref) and new_ref.lower() not in ["", "-", "none", "n/a"]:
                    unresolved.append(f"{field_name}: {ref}")

            if any_converted:
                num_fixed += 1

            return f"{prefix}{', '.join(converted)} {suffix}"

        content = re.sub(pattern, replace_refs, content)

    return content, num_fixed, unresolved


def fix_epic(
    epic_dir: Path,
    mapping: ReferenceMapping,
    client: JiraClient,
    result: FixResult,
    dry_run: bool = False
) -> None:
    """Fix references in an epic's README."""
    readme = epic_dir / "README.md"
    if not readme.exists():
        return

    content = readme.read_text()
    original = content
    jira_key = extract_jira_key(content)

    # Fix epic-level refs (Depends On, Blocks)
    content, num_fixed, unresolved = fix_references_in_content(
        content, mapping, field_names=["Depends On", "Blocks"]
    )

    if content != original:
        if not dry_run:
            readme.write_text(content)
        result.epics_fixed += 1
        print(f"    Fixed {epic_dir.name}")

    for u in unresolved:
        result.unresolved_refs.append(f"Epic {epic_dir.name} - {u}")

    # Update JIRA
    if jira_key and content != original and not dry_run:
        if client.update_issue(jira_key, {"description": markdown_to_adf(content[:32000])}):
            result.jira_updated += 1


def fix_story(
    story_file: Path,
    mapping: ReferenceMapping,
    client: JiraClient,
    result: FixResult,
    dry_run: bool = False,
    epic_name: str = None
) -> None:
    """Fix references in a story file."""
    content = story_file.read_text()
    original = content
    jira_key = extract_jira_key(content)

    # Extract story ID for context
    id_match = re.search(r'^#\s+([A-Z]+-\d+-\d+[a-z]?):', content, re.MULTILINE)
    story_id = id_match.group(1) if id_match else story_file.stem

    # Build context with epic name for per-epic mappings
    context = {"epic_name": epic_name} if epic_name else None

    # Fix story refs (Depends On, Blocks)
    content, num_fixed, unresolved = fix_references_in_content(
        content, mapping, context=context, field_names=["Depends On", "Blocks"]
    )

    if content != original:
        if not dry_run:
            story_file.write_text(content)
        result.stories_fixed += 1
        print(f"    Fixed {story_id}")

    for u in unresolved:
        result.unresolved_refs.append(f"Story {story_id} - {u}")

    # Update JIRA
    if jira_key and content != original and not dry_run:
        if client.update_issue(jira_key, {"description": markdown_to_adf(content[:32000])}):
            result.jira_updated += 1


def fix_task(
    task_file: Path,
    story_dir_name: str,
    mapping: ReferenceMapping,
    client: JiraClient,
    result: FixResult,
    dry_run: bool = False,
    epic_name: str = None
) -> None:
    """Fix references in a task file."""
    content = task_file.read_text()
    original = content
    jira_key = extract_jira_key(content)

    # Extract task ID for context
    # Match patterns: AUTH-001-1-T1, POLICY-001-T1, PLAT-024-T1
    id_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[a-z]?-T\d+):', content, re.MULTILINE)
    task_id = id_match.group(1) if id_match else task_file.stem

    context = {"story_dir_name": story_dir_name, "epic_name": epic_name}

    # Fix task refs (Requires, Unlocks)
    content, num_fixed, unresolved = fix_references_in_content(
        content, mapping, context=context, field_names=["Requires", "Unlocks"]
    )

    if content != original:
        if not dry_run:
            task_file.write_text(content)
        result.tasks_fixed += 1
        print(f"    Fixed {task_id}")

    for u in unresolved:
        result.unresolved_refs.append(f"Task {task_id} - {u}")

    # Update JIRA
    if jira_key and content != original and not dry_run:
        if client.update_issue(jira_key, {"description": markdown_to_adf(content[:32000])}):
            result.jira_updated += 1


def create_missing_links(
    epic_dirs: List[Path],
    mapping: ReferenceMapping,
    client: JiraClient,
    result: FixResult,
    dry_run: bool = False
) -> None:
    """Create JIRA links for dependencies."""
    print("\n  Creating missing JIRA links...")

    for epic_dir in epic_dirs:
        if not epic_dir.is_dir():
            continue

        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            # Check story dependencies
            story_files = list(story_dir.glob("story-*.md"))
            if story_files:
                content = story_files[0].read_text()
                story_jira = extract_jira_key(content)

                if story_jira:
                    # Get existing links
                    existing = client.get_existing_links(story_jira) if not dry_run else set()

                    # Create links for Blocks
                    blocks_match = re.search(r'\|\s*Blocks\s*\|\s*([^|]+)\|', content)
                    if blocks_match:
                        refs = blocks_match.group(1).strip()
                        if refs.lower() not in ["", "-", "none"]:
                            for ref in refs.split(","):
                                ref = ref.strip()
                                if is_jira_key(ref) and ref not in existing:
                                    if not dry_run:
                                        if client.create_link(story_jira, ref, "Blocks"):
                                            result.links_created += 1
                                            print(f"    Created link: {story_jira} blocks {ref}")
                                    else:
                                        print(f"    Would create: {story_jira} blocks {ref}")

            # Check task dependencies
            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                content = task_file.read_text()
                task_jira = extract_jira_key(content)

                if task_jira:
                    existing = client.get_existing_links(task_jira) if not dry_run else set()

                    # Create links for Unlocks
                    unlocks_match = re.search(r'\|\s*Unlocks\s*\|\s*([^|]+)\|', content)
                    if unlocks_match:
                        refs = unlocks_match.group(1).strip()
                        if refs.lower() not in ["", "-", "none"]:
                            for ref in refs.split(","):
                                ref = ref.strip()
                                if is_jira_key(ref) and ref not in existing:
                                    if not dry_run:
                                        if client.create_link(task_jira, ref, "Blocks"):
                                            result.links_created += 1
                                            print(f"    Created link: {task_jira} blocks {ref}")
                                    else:
                                        print(f"    Would create: {task_jira} blocks {ref}")


def validate_all_refs(epic_dirs: List[Path]) -> Tuple[int, int, List[str]]:
    """
    Validate all refs are JIRA keys.
    Returns (total_refs, jira_refs, non_jira_refs).
    """
    total = 0
    jira = 0
    non_jira = []

    for epic_dir in epic_dirs:
        if not epic_dir.is_dir():
            continue

        # Check epic
        readme = epic_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            for field in ["Depends On", "Blocks"]:
                match = re.search(rf'\|\s*{field}\s*\|\s*([^|]+)\|', content)
                if match:
                    refs = match.group(1).strip()
                    if refs.lower() not in ["", "-", "none", "n/a"]:
                        for ref in refs.split(","):
                            ref = ref.strip()
                            total += 1
                            if is_jira_key(ref):
                                jira += 1
                            else:
                                non_jira.append(f"Epic {epic_dir.name} {field}: {ref}")

        # Check stories and tasks
        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            story_files = list(story_dir.glob("story-*.md"))
            if story_files:
                content = story_files[0].read_text()
                id_match = re.search(r'^#\s+([A-Z]+-\d+-\d+[a-z]?):', content, re.MULTILINE)
                story_id = id_match.group(1) if id_match else story_dir.name

                for field in ["Depends On", "Blocks"]:
                    match = re.search(rf'\|\s*{field}\s*\|\s*([^|]+)\|', content)
                    if match:
                        refs = match.group(1).strip()
                        if refs.lower() not in ["", "-", "none", "n/a"]:
                            for ref in refs.split(","):
                                ref = ref.strip()
                                total += 1
                                if is_jira_key(ref):
                                    jira += 1
                                else:
                                    non_jira.append(f"Story {story_id} {field}: {ref}")

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                content = task_file.read_text()
                # Match patterns: AUTH-001-1-T1, POLICY-001-T1, PLAT-024-T1
                id_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[a-z]?-T\d+):', content, re.MULTILINE)
                task_id = id_match.group(1) if id_match else task_file.stem

                for field in ["Requires", "Unlocks"]:
                    match = re.search(rf'\|\s*{field}\s*\|\s*([^|]+)\|', content)
                    if match:
                        refs = match.group(1).strip()
                        if refs.lower() not in ["", "-", "none", "n/a"]:
                            for ref in refs.split(","):
                                ref = ref.strip()
                                total += 1
                                if is_jira_key(ref):
                                    jira += 1
                                else:
                                    non_jira.append(f"Task {task_id} {field}: {ref}")

    return total, jira, non_jira


def generate_report(result: FixResult, mapping: ReferenceMapping, elapsed: float) -> str:
    """Generate a report of the fix operation."""
    report = []
    report.append("=" * 70)
    report.append("JIRA Post-Import Reference Fix Report")
    report.append("=" * 70)
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"Duration: {elapsed:.1f} seconds")
    report.append("")

    report.append("Mappings Built:")
    report.append(f"  Epics:  {len(mapping.epics)}")
    report.append(f"  Stories: {len(mapping.stories)}")
    report.append(f"  Tasks:   {len(mapping.tasks)} + {len(mapping.task_tuples)} tuples")
    report.append("")

    report.append("Fixes Applied:")
    report.append(f"  Epics fixed:    {result.epics_fixed}")
    report.append(f"  Stories fixed:  {result.stories_fixed}")
    report.append(f"  Tasks fixed:    {result.tasks_fixed}")
    report.append(f"  JIRA updated:   {result.jira_updated}")
    report.append(f"  Links created:  {result.links_created}")
    report.append("")

    if result.unresolved_refs:
        report.append(f"Unresolved References ({len(result.unresolved_refs)}):")
        for ref in result.unresolved_refs[:20]:
            report.append(f"  - {ref}")
        if len(result.unresolved_refs) > 20:
            report.append(f"  ... and {len(result.unresolved_refs) - 20} more")
        report.append("")

    if result.errors:
        report.append(f"Errors ({len(result.errors)}):")
        for err in result.errors[:10]:
            report.append(f"  - {err}")
        report.append("")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="JIRA Post-Import Reference Fix")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no fixes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--no-jira-update", action="store_true", help="Fix local files only")
    parser.add_argument("--epic", help="Fix specific epic only")
    parser.add_argument("--create-links", action="store_true", help="Create missing JIRA links")
    parser.add_argument("--save-report", action="store_true", help="Save report to .bmad/data/")
    args = parser.parse_args()

    start_time = time.time()

    print("=" * 70)
    print("JIRA Post-Import Reference Fix")
    print("=" * 70)

    # Collect epic directories
    if args.epic:
        epic_dir = EPICS_DIR / args.epic
        if not epic_dir.exists():
            print(f"ERROR: Epic not found: {epic_dir}")
            sys.exit(1)
        epic_dirs = [epic_dir]
    else:
        epic_dirs = sorted([d for d in EPICS_DIR.iterdir() if d.is_dir()])

    print(f"Epics: {len(epic_dirs)}")
    print(f"Mode:  {'Validate Only' if args.validate_only else 'Dry Run' if args.dry_run else 'Fix'}")
    print(f"JIRA:  {'Disabled' if args.no_jira_update else 'Enabled'}")

    # Phase 1: Build complete mapping
    print("\n" + "-" * 70)
    print("Phase 1: Building Complete Mapping")
    print("-" * 70)

    mapping = build_complete_mapping(epic_dirs)
    print(f"  Epic mappings:  {len(mapping.epics)}")
    print(f"  Story mappings: {len(mapping.stories)} global + {len(mapping.stories_by_epic)} per-epic")
    print(f"  Task mappings:  {len(mapping.tasks)} direct + {len(mapping.task_tuples)} tuples")

    # Show some example mappings
    print("\n  Sample mappings:")
    for i, (k, v) in enumerate(list(mapping.epics.items())[:3]):
        print(f"    {k} -> {v}")
    for i, (k, v) in enumerate(list(mapping.stories.items())[:3]):
        print(f"    {k} -> {v}")

    # Phase 2: Validate current state
    print("\n" + "-" * 70)
    print("Phase 2: Validating Current State")
    print("-" * 70)

    total, jira, non_jira = validate_all_refs(epic_dirs)
    print(f"  Total references: {total}")
    pct = f"{100*jira/total:.1f}%" if total > 0 else "N/A"
    print(f"  JIRA keys:        {jira} ({pct})")
    print(f"  Non-JIRA:         {len(non_jira)}")

    if non_jira and len(non_jira) <= 10:
        print("\n  Non-JIRA references:")
        for ref in non_jira:
            print(f"    - {ref}")
    elif non_jira:
        print(f"\n  First 10 non-JIRA references:")
        for ref in non_jira[:10]:
            print(f"    - {ref}")
        print(f"    ... and {len(non_jira) - 10} more")

    if args.validate_only:
        print("\n[Validate Only - stopping here]")
        elapsed = time.time() - start_time
        print(f"\nCompleted in {elapsed:.1f} seconds")

        if len(non_jira) > 0:
            sys.exit(1)  # Exit with error if unresolved refs
        sys.exit(0)

    if len(non_jira) == 0:
        print("\n  All references are already JIRA keys!")
        if not args.create_links:
            print("\n[Nothing to fix]")
            sys.exit(0)

    # Phase 3: Fix references
    print("\n" + "-" * 70)
    print("Phase 3: Fixing References")
    print("-" * 70)

    client = JiraClient(enabled=not args.no_jira_update and not args.dry_run)
    result = FixResult()

    for epic_dir in epic_dirs:
        if not epic_dir.is_dir():
            continue

        print(f"\n  [{epic_dir.name}]")

        # Fix epic
        fix_epic(epic_dir, mapping, client, result, dry_run=args.dry_run)

        # Fix stories and tasks
        stories_dir = epic_dir / "stories"
        if not stories_dir.exists():
            continue

        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            story_files = list(story_dir.glob("story-*.md"))
            if story_files:
                fix_story(story_files[0], mapping, client, result, dry_run=args.dry_run, epic_name=epic_dir.name)

            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                fix_task(task_file, story_dir.name, mapping, client, result, dry_run=args.dry_run, epic_name=epic_dir.name)

    # Phase 4: Create missing links (optional)
    if args.create_links:
        print("\n" + "-" * 70)
        print("Phase 4: Creating Missing JIRA Links")
        print("-" * 70)
        create_missing_links(epic_dirs, mapping, client, result, dry_run=args.dry_run)

    # Phase 5: Final validation
    print("\n" + "-" * 70)
    print("Phase 5: Final Validation")
    print("-" * 70)

    total, jira, non_jira = validate_all_refs(epic_dirs)
    print(f"  Total references: {total}")
    print(f"  JIRA keys:        {jira} ({100*jira/total:.1f}%)" if total > 0 else "  No references")
    print(f"  Non-JIRA:         {len(non_jira)}")

    if non_jira:
        print("\n  Remaining non-JIRA refs (need manual fix or missing epics):")
        for ref in non_jira[:15]:
            print(f"    - {ref}")
        if len(non_jira) > 15:
            print(f"    ... and {len(non_jira) - 15} more")

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Epics fixed:    {result.epics_fixed}")
    print(f"  Stories fixed:  {result.stories_fixed}")
    print(f"  Tasks fixed:    {result.tasks_fixed}")
    print(f"  JIRA updated:   {result.jira_updated}")
    print(f"  Links created:  {result.links_created}")
    print(f"  Unresolved:     {len(result.unresolved_refs)}")
    print(f"  Errors:         {len(result.errors)}")
    print(f"  Duration:       {elapsed:.1f}s")

    # Save report
    if args.save_report:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(result, mapping, elapsed)
        report_file = REPORT_DIR / f"POST-IMPORT-FIX-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.md"
        report_file.write_text(report)
        print(f"\n  Report saved: {report_file}")

    if len(non_jira) > 0 and not args.dry_run:
        print("\n  WARNING: Some refs could not be converted. Run sync for missing epics first.")
        sys.exit(1)

    print("\n  SUCCESS! All references are now JIRA keys." if len(non_jira) == 0 else "")


if __name__ == "__main__":
    main()
