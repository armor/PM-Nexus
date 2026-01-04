#!/usr/bin/env python3
"""
JIRA Cleanup Script

Deletes all issues in a JIRA project and clears JIRA keys from local files.

Usage:
    # Dry run - show what would be deleted
    python scripts/jira-cleanup.py --dry-run

    # Delete all issues in ARGUS project
    python scripts/jira-cleanup.py --delete-issues

    # Clear JIRA keys from local story/task files
    python scripts/jira-cleanup.py --clear-local

    # Do both
    python scripts/jira-cleanup.py --delete-issues --clear-local

Environment Variables:
    ATLASSIAN_SITE      - JIRA site (default: armor-defense.atlassian.net)
    ATLASSIAN_EMAIL     - Your Atlassian email
    ATLASSIAN_API_TOKEN - Your API token
    JIRA_PROJECT_KEY    - Project key (default: ARGUS)
"""

import os
import re
import time
import argparse
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Auto-load .env file if it exists
def load_dotenv():
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_dotenv()

# Configuration
SITE = os.getenv("ATLASSIAN_SITE", "armor-defense.atlassian.net")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "ARGUS")

EPICS_DIR = PROJECT_ROOT / ".bmad/epics"
STATE_FILE = PROJECT_ROOT / ".bmad/data/jira-sync-state.json"

RATE_LIMIT_DELAY = 0.1  # seconds between delete requests


def get_auth():
    if not EMAIL or not API_TOKEN:
        print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables")
        exit(1)
    return (EMAIL, API_TOKEN)


def search_all_issues():
    """Search for all issues in the project."""
    url = f"https://{SITE}/rest/api/3/search/jql"

    all_issues = []
    next_page_token = None

    while True:
        payload = {
            "jql": f"project = {PROJECT_KEY} ORDER BY created ASC",
            "fields": ["summary", "issuetype"],
            "maxResults": 100
        }

        if next_page_token:
            payload["nextPageToken"] = next_page_token

        response = requests.post(url, json=payload, auth=get_auth())

        if response.status_code != 200:
            print(f"ERROR: Failed to search issues: {response.status_code}")
            print(response.text[:500])
            return []

        data = response.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)

        total = data.get("total", len(all_issues))
        print(f"  Fetched {len(all_issues)}/{total} issues...")

        # Check for next page
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return all_issues


def delete_issue(issue_key: str) -> bool:
    """Delete a single JIRA issue."""
    url = f"https://{SITE}/rest/api/3/issue/{issue_key}?deleteSubtasks=true"

    response = requests.delete(url, auth=get_auth())

    if response.status_code == 204:
        return True
    elif response.status_code == 404:
        print(f"  Issue not found: {issue_key}")
        return True  # Already deleted
    else:
        print(f"  Failed to delete {issue_key}: {response.status_code}")
        return False


def delete_all_issues(dry_run: bool = False):
    """Delete all issues in the project."""
    print("=" * 60)
    print("Searching for issues to delete...")
    print("=" * 60)

    issues = search_all_issues()

    if not issues:
        print("No issues found in project.")
        return

    print(f"\nFound {len(issues)} issues to delete:")

    # Group by type for summary
    by_type = {}
    for issue in issues:
        issue_type = issue["fields"]["issuetype"]["name"]
        by_type[issue_type] = by_type.get(issue_type, 0) + 1

    for issue_type, count in sorted(by_type.items()):
        print(f"  {issue_type}: {count}")

    if dry_run:
        print("\n[DRY RUN] Would delete these issues:")
        for issue in issues[:20]:
            print(f"  {issue['key']}: {issue['fields']['summary'][:50]}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
        return

    print("\nDeleting issues (this may take a while)...")

    # Delete in reverse order (newest first, so subtasks before parents)
    deleted = 0
    failed = 0

    for issue in reversed(issues):
        issue_key = issue["key"]
        if delete_issue(issue_key):
            deleted += 1
            if deleted % 10 == 0:
                print(f"  Deleted {deleted}/{len(issues)}...")
        else:
            failed += 1

        time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDeleted: {deleted}, Failed: {failed}")


def clear_local_jira_keys(dry_run: bool = False):
    """Clear JIRA keys from local story and task files."""
    print("=" * 60)
    print("Clearing JIRA keys from local files...")
    print("=" * 60)

    # Pattern to match JIRA Key line in coordination table
    jira_key_pattern = re.compile(r'(\| JIRA Key \| )([A-Z]+-\d+)( \|)')

    files_updated = 0

    # Process story files
    for story_file in EPICS_DIR.glob("*/stories/*/story-*.md"):
        with open(story_file, encoding='utf-8') as f:
            content = f.read()

        if jira_key_pattern.search(content):
            new_content = jira_key_pattern.sub(r'\1\3', content)

            if dry_run:
                print(f"  Would clear: {story_file.name}")
            else:
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            files_updated += 1

    # Process task files
    for task_file in EPICS_DIR.glob("*/stories/*/tasks/task-*.md"):
        with open(task_file, encoding='utf-8') as f:
            content = f.read()

        if jira_key_pattern.search(content):
            new_content = jira_key_pattern.sub(r'\1\3', content)

            if dry_run:
                print(f"  Would clear: {task_file.name}")
            else:
                with open(task_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            files_updated += 1

    # Clear sync state file
    if STATE_FILE.exists():
        if dry_run:
            print(f"  Would delete: {STATE_FILE.name}")
        else:
            STATE_FILE.unlink()
            print(f"  Deleted: {STATE_FILE.name}")

    print(f"\n{'Would update' if dry_run else 'Updated'}: {files_updated} files")


def main():
    parser = argparse.ArgumentParser(description='Clean up JIRA issues and local keys')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--delete-issues', action='store_true', help='Delete all JIRA issues')
    parser.add_argument('--clear-local', action='store_true', help='Clear JIRA keys from local files')
    args = parser.parse_args()

    if not args.delete_issues and not args.clear_local:
        print("Specify --delete-issues and/or --clear-local")
        print("Use --dry-run to preview changes")
        parser.print_help()
        return

    print("=" * 60)
    print("JIRA Cleanup")
    print("=" * 60)
    print(f"Site:     {SITE}")
    print(f"Project:  {PROJECT_KEY}")
    print(f"Dry Run:  {args.dry_run}")
    print()

    if args.delete_issues:
        delete_all_issues(args.dry_run)

    if args.clear_local:
        clear_local_jira_keys(args.dry_run)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
