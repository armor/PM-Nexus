#!/usr/bin/env python3
"""
JIRA Bulk Sync Script
Syncs BMAD epics and stories to JIRA using REST API

Directory Structure:
  .bmad/planning-artifacts/epics/EPIC-*.md     - Epic summaries
  .bmad/generated-stories/EPIC-*/STORY-*.md   - Detailed story files with Party Mode prompts
"""

import os
import re
import sys
import json
import yaml
import hashlib
import requests
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

# Rate limiting - pause between API calls
API_DELAY_MS = 200

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "_bmad/config/atlassian-integration.yaml"
STATE_FILE = PROJECT_ROOT / "_bmad/data/jira-sync-state.yaml"
EPICS_DIR = PROJECT_ROOT / ".bmad/planning-artifacts/epics"
STORIES_DIR = PROJECT_ROOT / ".bmad/generated-stories"

# Epic ID to JIRA parent key mapping (after duplicate cleanup 2026-01-02)
EPIC_JIRA_KEYS = {
    "EPIC-1": "ARGUS-1",
    "EPIC-2": "ARGUS-3",
    "EPIC-3": "ARGUS-4",
    "EPIC-4": "ARGUS-5",
    "EPIC-5": "ARGUS-6",
    "EPIC-6": "ARGUS-7",
    "EPIC-7": "ARGUS-8",
    "EPIC-8": "ARGUS-92",
    "EPIC-9": "ARGUS-93",
    "EPIC-11": "ARGUS-94",
    "EPIC-AUTH-001": "ARGUS-11",
}

# Load from environment or prompt
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")


class JIRASync:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self.base_url = self.config["atlassian"]["site_url"]
        self.project_key = self.config["jira"]["project_key"]
        self.custom_fields = self.config["jira"]["custom_fields"]
        self.priority_map = self.config["priority_map"]["bmad_to_jira"]
        self.session = requests.Session()
        self.session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.created = []
        self.updated = []
        self.skipped = []
        self.errors = []

    def _load_config(self) -> dict:
        if not CONFIG_FILE.exists():
            print(f"WARNING: Config file not found at {CONFIG_FILE}")
            return {
                "atlassian": {"site_url": "https://armor-defense.atlassian.net"},
                "jira": {
                    "project_key": "ARGUS",
                    "custom_fields": {
                        "epic_link": "customfield_10014",
                        "story_points": "customfield_10016",
                        "sprint": "customfield_10020"
                    }
                },
                "priority_map": {
                    "bmad_to_jira": {"P0": "Highest", "P1": "High", "P2": "Medium", "P3": "Low"}
                }
            }
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)

    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = yaml.safe_load(f)
                if state and "items" in state:
                    return state
        return {"last_sync": None, "items": {}, "conflicts": []}

    def _save_state(self):
        self.state["last_sync"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            yaml.dump(self.state, f, default_flow_style=False)

    def _content_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _api_get(self, endpoint: str) -> Optional[dict]:
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.get(url)
        if resp.status_code == 200:
            return resp.json()
        return None

    def _api_post(self, endpoint: str, data: dict) -> Tuple[bool, dict]:
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.post(url, json=data)
        if resp.status_code in (200, 201):
            return True, resp.json()
        return False, {"error": resp.text, "status": resp.status_code}

    def _api_put(self, endpoint: str, data: dict) -> Tuple[bool, dict]:
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.put(url, json=data)
        if resp.status_code in (200, 204):
            return True, {}
        return False, {"error": resp.text, "status": resp.status_code}

    def _search_issue(self, summary: str, issue_type: str = None) -> Optional[dict]:
        """Search for issue by summary using new JQL search API"""
        jql = f'project = {self.project_key} AND summary ~ "{summary}"'
        if issue_type:
            jql += f' AND issuetype = "{issue_type}"'

        # Use new POST /search/jql endpoint (old GET /search is deprecated)
        url = f"{self.base_url}/rest/api/3/search/jql"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.post(url, json={
            "jql": jql,
            "maxResults": 1,
            "fields": ["summary", "issuetype", "key"]
        })
        if resp.status_code == 200:
            result = resp.json()
            if result.get("issues"):
                return result["issues"][0]
        return None

    def _create_epic(self, epic_id: str, title: str, description: str) -> Optional[str]:
        """Create an epic in JIRA"""
        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"{epic_id}: {title}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description[:2000]}]}]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        success, result = self._api_post("issue", data)
        if success:
            return result.get("key")
        else:
            self.errors.append(f"Failed to create epic {epic_id}: {result}")
            return None

    def _create_story(self, story_id: str, title: str, description: str,
                      points: int, priority: str, epic_key: str,
                      labels: List[str] = None, sprint: int = None) -> Optional[str]:
        """Create a story in JIRA"""
        jira_priority = self.priority_map.get(priority, "Medium")

        # Build description with story points and epic reference (since fields not on JIRA screen)
        desc_with_context = description[:1800] if description else "No description"
        if points:
            desc_with_context = f"**Story Points: {points}**\n\n{desc_with_context}"
        if epic_key:
            desc_with_context = f"**Epic: {epic_key}**\n{desc_with_context}"

        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"{story_id}: {title}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": desc_with_context}]}]
                },
                "issuetype": {"name": "Story"},
                "priority": {"name": jira_priority}
            }
        }

        # Add labels if provided (include points and epic for filtering)
        if labels:
            data["fields"]["labels"] = labels
        else:
            data["fields"]["labels"] = []
        if points:
            data["fields"]["labels"].append(f"sp-{points}")
        if epic_key:
            data["fields"]["labels"].append(f"epic-{epic_key.lower()}")

        # Remove None values
        data["fields"] = {k: v for k, v in data["fields"].items() if v is not None}

        success, result = self._api_post("issue", data)
        if success:
            return result.get("key")
        else:
            self.errors.append(f"Failed to create story {story_id}: {result}")
            return None

    def parse_story_file(self, filepath: Path) -> Optional[dict]:
        """Parse a story markdown file with YAML metadata block"""
        content = filepath.read_text()

        story_data = {
            "file": str(filepath),
            "content_hash": self._content_hash(content)
        }

        # Extract YAML metadata block
        yaml_match = re.search(r'```yaml\s*\n(story:.*?)```', content, re.DOTALL)
        if yaml_match:
            try:
                yaml_content = yaml_match.group(1)
                metadata = yaml.safe_load(yaml_content)

                if "story" in metadata:
                    story_data["id"] = metadata["story"].get("id", "")
                    story_data["title"] = metadata["story"].get("title", "").strip('"')
                    story_data["type"] = metadata["story"].get("type", "engineering")
                    story_data["status"] = metadata["story"].get("status", "ready")

                if "metadata" in metadata:
                    meta = metadata["metadata"]
                    story_data["parent"] = meta.get("parent", "")
                    story_data["priority"] = meta.get("priority", "P2")
                    story_data["points"] = meta.get("points", 0)
                    story_data["sprint"] = meta.get("sprint", 0)
                    story_data["wave"] = meta.get("wave", 0)
                    story_data["labels"] = meta.get("labels", [])

            except yaml.YAMLError as e:
                print(f"  WARNING: Failed to parse YAML in {filepath.name}: {e}")

        # Extract Problem Statement as description
        problem_match = re.search(r'## Problem Statement\s+(.+?)(?=\n###|\n---|\n## |\Z)', content, re.DOTALL)
        if problem_match:
            story_data["description"] = problem_match.group(1).strip()[:1500]
        else:
            story_data["description"] = story_data.get("title", "No description")

        # Extract Goal as additional description
        goal_match = re.search(r'## Goal\s+(.+?)(?=\n###|\n---|\n## |\Z)', content, re.DOTALL)
        if goal_match:
            goal_text = goal_match.group(1).strip()[:500]
            story_data["description"] = f"{story_data.get('description', '')}\n\nGoal: {goal_text}"

        # Extract Acceptance Criteria
        ac_match = re.search(r'## GIVEN-WHEN-THEN Acceptance Criteria\s+(.+?)(?=\n## |\Z)', content, re.DOTALL)
        if ac_match:
            story_data["acceptance_criteria"] = ac_match.group(1).strip()[:2000]

        return story_data if story_data.get("id") else None

    def parse_epic_file(self, filepath: Path) -> dict:
        """Parse an epic markdown file"""
        content = filepath.read_text()

        epic_data = {
            "file": str(filepath),
            "content_hash": self._content_hash(content),
            "stories": []
        }

        # Parse epic title - supports multiple formats
        title_patterns = [
            r'^# (EPIC-\d+): (.+)$',
            r'^# (EPIC-\d+[A-Z]?): (.+)$',
            r'^# (EPIC-[A-Z]+-\d+[a-z]?): (.+)$',
        ]

        for pattern in title_patterns:
            title_match = re.search(pattern, content, re.MULTILINE)
            if title_match:
                epic_data["id"] = title_match.group(1)
                epic_data["title"] = title_match.group(2).strip()
                break

        # Parse summary
        summary_match = re.search(r'## Summary\s+(.+?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        if summary_match:
            epic_data["summary"] = summary_match.group(1).strip()[:2000]
        else:
            epic_data["summary"] = epic_data.get("title", "No summary")

        return epic_data

    def discover_stories_for_epic(self, epic_id: str) -> List[dict]:
        """Discover story files from generated-stories directory for an epic"""
        stories = []

        # Map epic ID to directory name
        epic_dir_patterns = [
            f"EPIC-{epic_id.split('-')[-1]}-*",  # EPIC-3-RISK from EPIC-3
            epic_id,  # Exact match
            f"{epic_id}-*",  # EPIC-AUTH-001-unified-scanner-auth
        ]

        # Find the stories directory
        stories_base = STORIES_DIR
        if not stories_base.exists():
            print(f"  WARNING: Stories directory not found: {stories_base}")
            return stories

        # Find matching epic directory
        epic_dir = None
        for pattern in epic_dir_patterns:
            matches = list(stories_base.glob(pattern))
            if matches:
                epic_dir = matches[0]
                break

        if not epic_dir or not epic_dir.is_dir():
            # Try direct mapping
            for d in stories_base.iterdir():
                if d.is_dir() and epic_id in d.name:
                    epic_dir = d
                    break

        if not epic_dir:
            print(f"  WARNING: No stories directory found for {epic_id}")
            return stories

        # Parse all story files
        story_files = sorted(epic_dir.glob("*.md"))
        print(f"  Found {len(story_files)} story files in {epic_dir.name}")

        for story_file in story_files:
            story_data = self.parse_story_file(story_file)
            if story_data:
                stories.append(story_data)

        return stories

    def sync_epic(self, epic_data: dict, batch_size: int = 10) -> dict:
        """Sync a single epic and its stories to JIRA"""
        epic_id = epic_data.get("id", "UNKNOWN")
        epic_title = epic_data.get("title", "Unknown Epic")
        epic_summary = epic_data.get("summary", "")

        print(f"\n{'='*60}")
        print(f"Syncing {epic_id}: {epic_title}")

        # Discover stories from generated-stories directory
        stories = self.discover_stories_for_epic(epic_id)
        epic_data["stories"] = stories
        print(f"  Total stories to sync: {len(stories)}")
        print(f"{'='*60}")

        # Check if epic exists in JIRA
        existing_epic = self._search_issue(f"{epic_id}:", "Epic")

        if existing_epic:
            epic_key = existing_epic["key"]
            print(f"  Epic exists: {epic_key}")
            self.skipped.append(f"{epic_id} -> {epic_key} (exists)")
        else:
            # Create epic
            epic_key = self._create_epic(epic_id, epic_title, epic_summary)
            if epic_key:
                print(f"  Created epic: {epic_key}")
                self.created.append(f"{epic_id} -> {epic_key} (Epic)")
                self.state["items"][epic_id] = {
                    "jira_key": epic_key,
                    "last_sync": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "bmad_hash": epic_data.get("content_hash", "")
                }
            else:
                print(f"  ERROR: Failed to create epic")
                return {"created": 0, "skipped": 0, "errors": 1}

        # Sync stories in batches
        created_count = 0
        skipped_count = 0
        error_count = 0

        for i, story in enumerate(stories):
            story_id = story.get("id", f"STORY-{i}")
            story_title = story.get("title", "Untitled")

            # Check if story exists
            existing_story = self._search_issue(f"{story_id}:", "Story")

            if existing_story:
                print(f"    [{i+1}/{len(stories)}] {story_id} exists: {existing_story['key']}")
                self.skipped.append(f"{story_id} -> {existing_story['key']} (exists)")
                skipped_count += 1
            else:
                # Create story
                story_key = self._create_story(
                    story_id,
                    story_title,
                    story.get("description", ""),
                    story.get("points", 0),
                    story.get("priority", "P2"),
                    epic_key,
                    labels=story.get("labels", []),
                    sprint=story.get("sprint")
                )

                if story_key:
                    print(f"    [{i+1}/{len(stories)}] Created: {story_id} -> {story_key}")
                    self.created.append(f"{story_id} -> {story_key} (Story)")
                    self.state["items"][story_id] = {
                        "jira_key": story_key,
                        "last_sync": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        "bmad_hash": story.get("content_hash", "")
                    }
                    created_count += 1
                else:
                    print(f"    [{i+1}/{len(stories)}] ERROR: {story_id}")
                    error_count += 1

            # Save state periodically
            if (i + 1) % batch_size == 0:
                self._save_state()
                print(f"    [Checkpoint saved at {i+1} stories]")

        return {"created": created_count, "skipped": skipped_count, "errors": error_count}

    def list_stories(self):
        """List all stories in the generated-stories directory"""
        print("\n" + "="*60)
        print("STORY INVENTORY")
        print("="*60)

        if not STORIES_DIR.exists():
            print(f"ERROR: Stories directory not found: {STORIES_DIR}")
            return

        total_stories = 0
        for epic_dir in sorted(STORIES_DIR.iterdir()):
            if epic_dir.is_dir() and epic_dir.name.startswith("EPIC-"):
                story_files = list(epic_dir.glob("*.md"))
                total_stories += len(story_files)
                print(f"  {epic_dir.name}: {len(story_files)} stories")

        print(f"\nTotal: {total_stories} stories")

    def run_bulk_sync(self, dry_run: bool = False, epic_filter: str = None):
        """Run bulk sync of all epics"""
        print("\n" + "="*60)
        print("JIRA BULK SYNC")
        print(f"Project: {self.project_key}")
        print(f"Site: {self.base_url}")
        print(f"Dry Run: {dry_run}")
        if epic_filter:
            print(f"Filter: {epic_filter}")
        print("="*60)

        if not dry_run and (not JIRA_EMAIL or not JIRA_API_TOKEN):
            print("\nERROR: JIRA credentials not set!")
            print("Set environment variables:")
            print("  export JIRA_EMAIL='your-email@example.com'")
            print("  export JIRA_API_TOKEN='your-api-token'")
            sys.exit(1)

        if not dry_run:
            # Test connection
            print("\nTesting JIRA connection...")
            test = self._api_get(f"project/{self.project_key}")
            if not test:
                print("ERROR: Could not connect to JIRA. Check credentials.")
                sys.exit(1)
            print(f"Connected to project: {test.get('name', self.project_key)}")

        # Find all epic files
        epic_files = sorted(EPICS_DIR.glob("EPIC-*.md"))
        print(f"\nFound {len(epic_files)} epic files")

        # Show story inventory
        self.list_stories()

        if dry_run:
            print("\n[DRY RUN] Would sync the following:")
            for f in epic_files:
                epic_data = self.parse_epic_file(f)
                epic_id = epic_data.get('id', 'UNKNOWN')

                if epic_filter and epic_filter not in epic_id:
                    continue

                stories = self.discover_stories_for_epic(epic_id)
                print(f"\n  {epic_id}: {epic_data.get('title', 'Unknown')}")
                print(f"    Stories: {len(stories)}")
                for story in stories[:5]:
                    print(f"      - {story.get('id')}: {story.get('title', '')[:50]}... ({story.get('points', 0)} pts, {story.get('priority', 'P2')})")
                if len(stories) > 5:
                    print(f"      ... and {len(stories) - 5} more")
            return

        # Sync each epic
        total_created = 0
        total_skipped = 0
        total_errors = 0

        for filepath in epic_files:
            epic_data = self.parse_epic_file(filepath)
            epic_id = epic_data.get("id")

            if not epic_id:
                print(f"\nSkipping {filepath.name} - could not parse epic ID")
                continue

            if epic_filter and epic_filter not in epic_id:
                continue

            result = self.sync_epic(epic_data)
            total_created += result["created"]
            total_skipped += result["skipped"]
            total_errors += result["errors"]

            # Save state after each epic
            self._save_state()

        # Final report
        print("\n" + "="*60)
        print("SYNC COMPLETE")
        print("="*60)
        print(f"\nCreated: {len(self.created)}")
        for item in self.created[:20]:
            print(f"  {item}")
        if len(self.created) > 20:
            print(f"  ... and {len(self.created) - 20} more")

        print(f"\nSkipped (already exists): {len(self.skipped)}")

        if self.errors:
            print(f"\nErrors: {len(self.errors)}")
            for err in self.errors[:10]:
                print(f"  {err}")

        print(f"\nSync state saved to: {STATE_FILE}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync BMAD stories to JIRA")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating issues")
    parser.add_argument("--epic", type=str, help="Filter to specific epic (e.g., EPIC-3)")
    parser.add_argument("--list", action="store_true", help="List all stories")
    args = parser.parse_args()

    sync = JIRASync()

    if args.list:
        sync.list_stories()
    else:
        sync.run_bulk_sync(dry_run=args.dry_run, epic_filter=args.epic)


if __name__ == "__main__":
    main()
