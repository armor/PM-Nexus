#!/usr/bin/env python3
"""
Update existing JIRA subtasks with full task content (AI prompts).
"""
import os
import re
import time
import requests
from pathlib import Path

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

def update_issue_description(issue_key: str, description: str) -> bool:
    """Update a JIRA issue's description."""
    url = f"{BASE_URL}/issue/{issue_key}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    payload = {
        "fields": {
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description[:32000]}]
                }]
            }
        }
    }

    response = requests.put(url, auth=AUTH, headers=headers, json=payload, timeout=30)
    return response.ok

def main():
    # Find all task files in EPIC-AUTH-001
    epic_dir = PROJECT_ROOT / ".bmad/epics/EPIC-AUTH-001/stories"

    updated = 0
    errors = 0

    for story_dir in sorted(epic_dir.iterdir()):
        if not story_dir.is_dir():
            continue

        tasks_dir = story_dir / "tasks"
        if not tasks_dir.exists():
            continue

        for task_file in sorted(tasks_dir.glob("task-*.md")):
            content = task_file.read_text()

            # Extract JIRA key from file
            jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
            if not jira_match:
                print(f"  SKIP: No JIRA key in {task_file.name}")
                continue

            jira_key = jira_match.group(1)

            print(f"  Updating {jira_key} with full content...")

            if update_issue_description(jira_key, content):
                print(f"    SUCCESS: {jira_key}")
                updated += 1
            else:
                print(f"    ERROR: {jira_key}")
                errors += 1

            time.sleep(0.25)  # Rate limiting

    print(f"\nUpdated: {updated}, Errors: {errors}")

if __name__ == "__main__":
    main()
