#!/usr/bin/env python3
"""
JIRA Hierarchy Sync - Full Epic → Story → Task → Sub-task

Syncs simplified BMAD stories to JIRA with complete hierarchy:
  Epic (existing) → Story → Task → Sub-task

Usage:
  python scripts/jira-sync-hierarchy.py --dry-run
  python scripts/jira-sync-hierarchy.py --epic EPIC-1-PLATFORM
  python scripts/jira-sync-hierarchy.py

Prerequisites:
  export JIRA_EMAIL='your-email@example.com'
  export JIRA_API_TOKEN='your-api-token'
"""

import os
import re
import sys
import yaml
import time
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

# Rate limiting
API_DELAY_MS = 250

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
STORIES_DIR = PROJECT_ROOT / ".bmad/jira-stories"  # Simplified stories
STATE_FILE = PROJECT_ROOT / "_bmad/data/jira-hierarchy-state.yaml"

# Epic to JIRA key mapping
EPIC_JIRA_KEYS = {
    "ARGUS-1": "ARGUS-1",
    "ARGUS-3": "ARGUS-3",
    "ARGUS-4": "ARGUS-4",
    "ARGUS-5": "ARGUS-5",
    "ARGUS-6": "ARGUS-6",
    "ARGUS-7": "ARGUS-7",
    "ARGUS-8": "ARGUS-8",
    "ARGUS-92": "ARGUS-92",
    "ARGUS-93": "ARGUS-93",
    "ARGUS-94": "ARGUS-94",
    "ARGUS-11": "ARGUS-11",
}

JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")


class JIRAHierarchySync:
    def __init__(self):
        self.base_url = "https://armor-defense.atlassian.net"
        self.project_key = "ARGUS"
        self.session = requests.Session()
        self.session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.state = self._load_state()
        self.stats = {"stories": 0, "tasks": 0, "subtasks": 0, "errors": []}

    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return yaml.safe_load(f) or {}
        return {"synced": {}, "last_run": None}

    def _save_state(self):
        self.state["last_run"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            yaml.dump(self.state, f, default_flow_style=False)

    def _api_post(self, endpoint: str, data: dict) -> Tuple[bool, dict]:
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)
        try:
            resp = self.session.post(url, json=data)
            if resp.status_code in (200, 201):
                return True, resp.json()
            return False, {"error": resp.text, "status": resp.status_code}
        except Exception as e:
            return False, {"error": str(e)}

    def _search_issue(self, summary: str, issue_type: str = None) -> Optional[str]:
        """Search for existing issue by summary, return key if found."""
        jql = f'project = {self.project_key} AND summary ~ "{summary[:50]}"'
        if issue_type:
            jql += f' AND issuetype = "{issue_type}"'

        url = f"{self.base_url}/rest/api/3/search/jql"
        time.sleep(API_DELAY_MS / 1000)
        resp = self.session.post(url, json={"jql": jql, "maxResults": 1})
        if resp.status_code == 200:
            result = resp.json()
            if result.get("issues"):
                return result["issues"][0]["key"]
        return None

    def _create_issue(self, summary: str, description: str, issue_type: str,
                      parent_key: str = None, labels: List[str] = None) -> Optional[str]:
        """Create a JIRA issue."""
        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary[:255],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description[:2000]}]}]
                },
                "issuetype": {"name": issue_type}
            }
        }

        # Add parent for Sub-task
        if issue_type == "Sub-task" and parent_key:
            data["fields"]["parent"] = {"key": parent_key}

        # Add labels
        if labels:
            data["fields"]["labels"] = labels

        success, result = self._api_post("issue", data)
        if success:
            return result.get("key")
        else:
            self.stats["errors"].append(f"Failed to create {issue_type}: {result}")
            return None

    def parse_simplified_story(self, filepath: Path) -> Optional[Dict]:
        """Parse a simplified story file with tasks and subtasks."""
        content = filepath.read_text()

        story = {
            "id": "",
            "title": "",
            "epic": "",
            "points": 0,
            "priority": "P2",
            "sprint": 1,
            "description": "",
            "acceptance_criteria": [],
            "tasks": [],
            "files": []
        }

        # Parse header
        header_match = re.search(r'^# ([A-Z]+-\d+): (.+)$', content, re.MULTILINE)
        if header_match:
            story["id"] = header_match.group(1)
            story["title"] = header_match.group(2).strip()

        # Parse metadata line
        meta_match = re.search(r'\*\*Epic:\*\* ([^\|]+)\| \*\*Points:\*\* (\d+)', content)
        if meta_match:
            story["epic"] = meta_match.group(1).strip()
            story["points"] = int(meta_match.group(2))

        # Parse description
        desc_match = re.search(r'## Description\s+(.+?)(?=\n##)', content, re.DOTALL)
        if desc_match:
            story["description"] = desc_match.group(1).strip()

        # Parse acceptance criteria
        ac_match = re.search(r'## Acceptance Criteria\s+(.+?)(?=\n##)', content, re.DOTALL)
        if ac_match:
            criteria = re.findall(r'- \[[ x]\] (.+?)$', ac_match.group(1), re.MULTILINE)
            story["acceptance_criteria"] = criteria

        # Parse tasks with subtasks
        tasks_section = re.search(r'## Tasks\s+(.+?)(?=\n## Files|\n## References|\Z)', content, re.DOTALL)
        if tasks_section:
            task_blocks = re.findall(
                r'### (T\d+): (.+?) \([\d.]+ pts\)\s*\n((?:- \[[ x]\] .+?\n?)+)',
                tasks_section.group(1),
                re.DOTALL
            )
            for task_id, task_title, subtasks_text in task_blocks:
                subtasks = re.findall(r'- \[[ x]\] (S\d+): (.+?)$', subtasks_text, re.MULTILINE)
                story["tasks"].append({
                    "id": task_id,
                    "title": task_title.strip(),
                    "subtasks": [{"id": sid, "title": stitle.strip()} for sid, stitle in subtasks]
                })

        return story if story["id"] else None

    def sync_story(self, story: Dict, dry_run: bool = False) -> Dict:
        """Sync a story with its tasks and subtasks to JIRA."""
        story_id = story["id"]
        story_title = story["title"]

        result = {"story": None, "tasks": [], "subtasks": []}

        # Check if story exists
        existing = self._search_issue(f"{story_id}:", "Story")
        if existing:
            print(f"    Story exists: {existing}")
            result["story"] = existing
            story_key = existing
        else:
            if dry_run:
                print(f"    [DRY] Would create Story: {story_id}: {story_title}")
                story_key = f"{story_id}-DRY"
            else:
                # Create story
                summary = f"{story_id}: {story_title}"
                description = story["description"]
                if story["acceptance_criteria"]:
                    description += "\n\nAcceptance Criteria:\n"
                    for ac in story["acceptance_criteria"]:
                        description += f"- {ac}\n"

                story_key = self._create_issue(
                    summary=summary,
                    description=description,
                    issue_type="Story",
                    labels=[f"epic-{story['epic'].lower().replace(' ', '-')}"]
                )
                if story_key:
                    print(f"    ✓ Created Story: {story_key}")
                    result["story"] = story_key
                    self.stats["stories"] += 1
                else:
                    print(f"    ✗ Failed to create Story: {story_id}")
                    return result

        # Create tasks under the story
        for task in story["tasks"]:
            task_id = f"{story_id}-{task['id']}"
            task_title = task["title"]

            existing_task = self._search_issue(f"{task_id}:", "Task")
            if existing_task:
                print(f"      Task exists: {existing_task}")
                task_key = existing_task
            else:
                if dry_run:
                    print(f"      [DRY] Would create Task: {task_id}: {task_title}")
                    task_key = f"{task_id}-DRY"
                else:
                    task_key = self._create_issue(
                        summary=f"{task_id}: {task_title}",
                        description=f"Part of {story_key}\n\nSubtasks:\n" + "\n".join(
                            f"- {st['id']}: {st['title']}" for st in task["subtasks"]
                        ),
                        issue_type="Task",
                        labels=[f"story-{story_id.lower()}"]
                    )
                    if task_key:
                        print(f"      ✓ Created Task: {task_key}")
                        result["tasks"].append(task_key)
                        self.stats["tasks"] += 1

            # Create subtasks under the task
            if task_key:
                for subtask in task["subtasks"]:
                    subtask_id = f"{story_id}-{task['id']}-{subtask['id']}"

                    existing_st = self._search_issue(f"{subtask_id}:", "Sub-task")
                    if existing_st:
                        print(f"        Subtask exists: {existing_st}")
                    else:
                        if dry_run:
                            print(f"        [DRY] Would create Sub-task: {subtask_id}: {subtask['title']}")
                        else:
                            st_key = self._create_issue(
                                summary=f"{subtask_id}: {subtask['title']}",
                                description=f"Part of {task_key}",
                                issue_type="Sub-task",
                                parent_key=task_key
                            )
                            if st_key:
                                print(f"        ✓ Created Sub-task: {st_key}")
                                result["subtasks"].append(st_key)
                                self.stats["subtasks"] += 1

        return result

    def run(self, dry_run: bool = False, epic_filter: str = None):
        """Run the full hierarchy sync."""
        print("=" * 60)
        print("JIRA HIERARCHY SYNC")
        print(f"Source: {STORIES_DIR}")
        print(f"Dry Run: {dry_run}")
        print("=" * 60)

        if not STORIES_DIR.exists():
            print(f"\nERROR: Stories directory not found: {STORIES_DIR}")
            print("Run: python scripts/simplify-stories.py first")
            return

        if not dry_run and (not JIRA_EMAIL or not JIRA_API_TOKEN):
            print("\nERROR: Set JIRA_EMAIL and JIRA_API_TOKEN environment variables")
            return

        # Process each epic directory
        epic_dirs = sorted([d for d in STORIES_DIR.iterdir() if d.is_dir()])

        for epic_dir in epic_dirs:
            if epic_filter and epic_filter not in epic_dir.name:
                continue

            print(f"\n{'='*60}")
            print(f"Epic: {epic_dir.name}")
            print(f"{'='*60}")

            story_files = sorted(epic_dir.glob("*.md"))
            for story_file in story_files:
                story = self.parse_simplified_story(story_file)
                if story:
                    print(f"\n  Processing {story['id']}...")
                    self.sync_story(story, dry_run)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Stories created: {self.stats['stories']}")
        print(f"Tasks created:   {self.stats['tasks']}")
        print(f"Subtasks created: {self.stats['subtasks']}")

        if self.stats["errors"]:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for err in self.stats["errors"][:5]:
                print(f"  - {err}")

        if not dry_run:
            self._save_state()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync BMAD stories to JIRA with full hierarchy")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--epic", type=str, help="Filter to specific epic")
    args = parser.parse_args()

    sync = JIRAHierarchySync()
    sync.run(dry_run=args.dry_run, epic_filter=args.epic)


if __name__ == "__main__":
    main()
