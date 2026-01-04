#!/usr/bin/env python3
"""
Update existing JIRA issues with properly formatted ADF descriptions.
Converts markdown content to Atlassian Document Format for proper rendering.
"""
import os
import re
import time
import requests
from pathlib import Path
from markdown_to_adf import markdown_to_adf

PROJECT_ROOT = Path(__file__).parent.parent

# Load .env
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

SITE = os.getenv("ATLASSIAN_SITE", "armor-defense.atlassian.net")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")
BASE_URL = f"https://{SITE}/rest/api/3"
AUTH = (EMAIL, API_TOKEN)

def update_issue_description(issue_key: str, markdown_content: str) -> bool:
    """Update a JIRA issue's description with ADF-converted markdown."""
    url = f"{BASE_URL}/issue/{issue_key}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Convert markdown to ADF
    adf_content = markdown_to_adf(markdown_content[:32000])

    payload = {
        "fields": {
            "description": adf_content
        }
    }

    response = requests.put(url, auth=AUTH, headers=headers, json=payload, timeout=30)
    if not response.ok:
        print(f"    ERROR: {response.status_code} - {response.text[:200]}")
    return response.ok

def extract_jira_key(content: str) -> str:
    """Extract JIRA key from file content."""
    match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
    if match:
        return match.group(1)
    # Also check for jira_key: format
    match = re.search(r'jira_key:\s*([A-Z]+-\d+)', content)
    if match:
        return match.group(1)
    return ""

def main():
    epic_dir = PROJECT_ROOT / ".bmad/epics/EPIC-AUTH-001"

    updated = 0
    errors = 0
    skipped = 0

    print("=" * 60)
    print("Updating EPIC-AUTH-001 JIRA Issues with ADF Content")
    print("=" * 60)

    # 1. Update Epic README
    print("\n[EPIC]")
    epic_readme = epic_dir / "README.md"
    if epic_readme.exists():
        content = epic_readme.read_text()
        jira_key = extract_jira_key(content)
        if jira_key:
            print(f"  Updating {jira_key} (Epic README)...")
            if update_issue_description(jira_key, content):
                print(f"    SUCCESS")
                updated += 1
            else:
                errors += 1
            time.sleep(0.25)
        else:
            print(f"  SKIP: No JIRA key in Epic README")
            skipped += 1

    # 2. Update Stories
    print("\n[STORIES]")
    stories_dir = epic_dir / "stories"
    if stories_dir.exists():
        for story_dir in sorted(stories_dir.iterdir()):
            if not story_dir.is_dir():
                continue

            # Find story file (pattern: story-*.md)
            story_files = list(story_dir.glob("story-*.md"))
            if not story_files:
                continue
            story_file = story_files[0]

            content = story_file.read_text()
            jira_key = extract_jira_key(content)

            if not jira_key:
                print(f"  SKIP: No JIRA key in {story_dir.name}")
                skipped += 1
                continue

            print(f"  Updating {jira_key} ({story_dir.name})...")
            if update_issue_description(jira_key, content):
                print(f"    SUCCESS")
                updated += 1
            else:
                errors += 1
            time.sleep(0.25)

            # 3. Update Tasks for this story
            tasks_dir = story_dir / "tasks"
            if not tasks_dir.exists():
                continue

            for task_file in sorted(tasks_dir.glob("task-*.md")):
                content = task_file.read_text()
                jira_key = extract_jira_key(content)

                if not jira_key:
                    print(f"    SKIP: No JIRA key in {task_file.name}")
                    skipped += 1
                    continue

                print(f"    Updating {jira_key} ({task_file.name})...")
                if update_issue_description(jira_key, content):
                    print(f"      SUCCESS")
                    updated += 1
                else:
                    errors += 1
                time.sleep(0.25)

    print("\n" + "=" * 60)
    print(f"SUMMARY: Updated={updated}, Errors={errors}, Skipped={skipped}")
    print("=" * 60)

if __name__ == "__main__":
    main()
