#!/usr/bin/env python3
"""
Create JIRA issue links using REST API directly.

This script bypasses MCP limitations to create:
- Epic Links (Story → Epic)
- Blocks/Is Blocked By links (dependency tracking)
- Any other issue link type

Usage:
    # Create a Blocks link
    python scripts/jira-create-links.py --from ARGUS-100 --to ARGUS-101 --type Blocks

    # Set Epic Link on a story
    python scripts/jira-create-links.py --story ARGUS-101 --epic ARGUS-100

    # Bulk create links from BMAD files
    python scripts/jira-create-links.py --sync-from-bmad

Environment Variables:
    ATLASSIAN_SITE      - JIRA site (default: armor-defense.atlassian.net)
    ATLASSIAN_EMAIL     - Your Atlassian email
    ATLASSIAN_API_TOKEN - Your API token

Requires: requests, pyyaml
"""

import os
import sys
import re
import argparse
import requests
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Configuration
SITE = os.getenv("ATLASSIAN_SITE", "armor-defense.atlassian.net")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

EPICS_DIR = Path(".bmad/epics")
CONFIG_FILE = Path("_bmad/config/jira-fields.yaml")
MAPPINGS_FILE = Path(".bmad/data/jira-mappings.yaml")


def get_auth() -> Tuple[str, str]:
    """Get authentication tuple."""
    if not EMAIL or not API_TOKEN:
        print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables")
        sys.exit(1)
    return (EMAIL, API_TOKEN)


def load_config() -> Dict:
    """Load JIRA field configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_mappings() -> Dict:
    """Load JIRA key mappings."""
    if MAPPINGS_FILE.exists():
        with open(MAPPINGS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_mappings(mappings: Dict):
    """Save JIRA key mappings."""
    MAPPINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MAPPINGS_FILE, "w") as f:
        yaml.dump(mappings, f, default_flow_style=False)


def get_link_types() -> List[Dict]:
    """Get available issue link types from JIRA."""
    url = f"https://{SITE}/rest/api/3/issueLinkType"
    response = requests.get(url, auth=get_auth())

    if response.status_code != 200:
        print(f"WARNING: Failed to fetch link types: {response.status_code}")
        return []

    return response.json().get("issueLinkTypes", [])


def create_issue_link(inward_key: str, outward_key: str, link_type: str = "Blocks") -> bool:
    """Create an issue link.

    Args:
        inward_key: The issue that IS the relationship (e.g., the blocker)
        outward_key: The issue that HAS the relationship (e.g., the blocked)
        link_type: Link type name (Blocks, Relates, Duplicates, etc.)

    Returns:
        True if successful, False otherwise
    """
    url = f"https://{SITE}/rest/api/3/issueLink"

    payload = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_key},
        "outwardIssue": {"key": outward_key}
    }

    response = requests.post(url, json=payload, auth=get_auth())

    if response.status_code == 201:
        print(f"✅ Created link: {inward_key} --[{link_type}]--> {outward_key}")
        return True
    elif response.status_code == 404:
        print(f"❌ Issue not found: {inward_key} or {outward_key}")
        return False
    else:
        print(f"❌ Failed to create link: {response.status_code}")
        print(f"   {response.text[:200]}")
        return False


def set_epic_link(story_key: str, epic_key: str, epic_link_field: str = "customfield_10014") -> bool:
    """Set the Epic Link field on a story.

    Args:
        story_key: The story issue key
        epic_key: The epic issue key
        epic_link_field: Custom field ID for Epic Link

    Returns:
        True if successful, False otherwise
    """
    url = f"https://{SITE}/rest/api/3/issue/{story_key}"

    payload = {
        "fields": {
            epic_link_field: epic_key
        }
    }

    response = requests.put(url, json=payload, auth=get_auth())

    if response.status_code == 204:
        print(f"✅ Set Epic Link: {story_key} --> {epic_key}")
        return True
    elif response.status_code == 404:
        print(f"❌ Issue not found: {story_key}")
        return False
    else:
        print(f"❌ Failed to set Epic Link: {response.status_code}")
        print(f"   {response.text[:200]}")
        return False


def parse_task_coordination(task_file: Path) -> Dict:
    """Parse coordination section from a task file."""
    with open(task_file) as f:
        content = f.read()

    result = {
        "requires": [],
        "unlocks": [],
        "jira_key": None
    }

    # Parse coordination table
    coord_match = re.search(r'\| Requires \| ([^|]+) \|', content)
    if coord_match:
        requires = coord_match.group(1).strip()
        if requires and requires != "none" and requires != "-":
            result["requires"] = [r.strip() for r in requires.split(",")]

    unlock_match = re.search(r'\| Unlocks \| ([^|]+) \|', content)
    if unlock_match:
        unlocks = unlock_match.group(1).strip()
        if unlocks and unlocks != "none" and unlocks != "-":
            result["unlocks"] = [u.strip() for u in unlocks.split(",")]

    jira_match = re.search(r'\| JIRA Key \| ([^|]+) \|', content)
    if jira_match:
        jira_key = jira_match.group(1).strip()
        if jira_key:
            result["jira_key"] = jira_key

    return result


def sync_links_from_bmad():
    """Sync dependency links from BMAD task files to JIRA."""
    print("=" * 60)
    print("Syncing Links from BMAD to JIRA")
    print("=" * 60)

    mappings = load_mappings()
    config = load_config()

    stats = {
        "processed": 0,
        "links_created": 0,
        "links_failed": 0,
        "skipped_no_jira": 0
    }

    # Process all task files
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

            # Build task number to JIRA key mapping for this story
            task_keys = {}
            for task_file in sorted(tasks_dir.glob("task-*.md")):
                match = re.search(r'task-(\d+)', task_file.name)
                if match:
                    task_num = int(match.group(1))
                    coord = parse_task_coordination(task_file)
                    if coord["jira_key"]:
                        task_keys[f"T{task_num}"] = coord["jira_key"]

            # Now create links
            for task_file in sorted(tasks_dir.glob("task-*.md")):
                match = re.search(r'task-(\d+)', task_file.name)
                if not match:
                    continue

                task_num = int(match.group(1))
                task_id = f"T{task_num}"
                coord = parse_task_coordination(task_file)
                stats["processed"] += 1

                if not coord["jira_key"]:
                    stats["skipped_no_jira"] += 1
                    continue

                current_jira = coord["jira_key"]

                # Create "is blocked by" links for requires
                for req in coord["requires"]:
                    if req in task_keys:
                        req_jira = task_keys[req]
                        # req_jira blocks current_jira
                        if create_issue_link(req_jira, current_jira, "Blocks"):
                            stats["links_created"] += 1
                        else:
                            stats["links_failed"] += 1

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Tasks processed:     {stats['processed']}")
    print(f"Links created:       {stats['links_created']}")
    print(f"Links failed:        {stats['links_failed']}")
    print(f"Skipped (no JIRA):   {stats['skipped_no_jira']}")


def list_link_types():
    """List available issue link types."""
    print("Available Issue Link Types:")
    print("-" * 40)

    for lt in get_link_types():
        print(f"  {lt['name']}:")
        print(f"    Inward:  '{lt.get('inward', 'N/A')}'")
        print(f"    Outward: '{lt.get('outward', 'N/A')}'")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Create JIRA issue links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a Blocks link (ARGUS-100 blocks ARGUS-101)
  python scripts/jira-create-links.py --from ARGUS-100 --to ARGUS-101 --type Blocks

  # Set Epic Link on a story
  python scripts/jira-create-links.py --story ARGUS-101 --epic ARGUS-100

  # List available link types
  python scripts/jira-create-links.py --list-types

  # Sync all links from BMAD task files
  python scripts/jira-create-links.py --sync-from-bmad
        """
    )

    parser.add_argument("--from", dest="from_key", help="Inward issue key (blocker)")
    parser.add_argument("--to", dest="to_key", help="Outward issue key (blocked)")
    parser.add_argument("--type", default="Blocks", help="Link type (default: Blocks)")
    parser.add_argument("--story", help="Story key for Epic Link")
    parser.add_argument("--epic", help="Epic key for Epic Link")
    parser.add_argument("--epic-field", default="customfield_10014", help="Epic Link field ID")
    parser.add_argument("--list-types", action="store_true", help="List available link types")
    parser.add_argument("--sync-from-bmad", action="store_true", help="Sync links from BMAD files")

    args = parser.parse_args()

    if args.list_types:
        list_link_types()
    elif args.sync_from_bmad:
        sync_links_from_bmad()
    elif args.story and args.epic:
        set_epic_link(args.story, args.epic, args.epic_field)
    elif args.from_key and args.to_key:
        create_issue_link(args.from_key, args.to_key, args.type)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
