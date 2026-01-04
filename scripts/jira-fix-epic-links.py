#!/usr/bin/env python3
"""
JIRA Epic Link Fix Script
Links all stories to their parent epics using the parent field
"""

import os
import sys
import yaml
import time
import requests
from pathlib import Path
from typing import Dict, Tuple

# Rate limiting - pause between API calls
API_DELAY_MS = 200

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
STATE_FILE = PROJECT_ROOT / "_bmad/data/jira-sync-state.yaml"

# Epic mappings: BMAD Epic ID -> JIRA Epic Key
EPIC_JIRA_KEYS = {
    "EPIC-1": "ARGUS-1",      # Platform Foundation
    "EPIC-2": "ARGUS-3",      # Graph & Attack Paths
    "EPIC-3": "ARGUS-4",      # Risk Engine
    "EPIC-4": "ARGUS-5",      # Automation & Remediation
    "EPIC-5": "ARGUS-6",      # UX & Dashboard
    "EPIC-6": "ARGUS-7",      # Integrations
    "EPIC-7": "ARGUS-8",      # Differentiation
    "EPIC-8": "ARGUS-92",     # Market Dominance
    "EPIC-9": "ARGUS-93",     # Policy & AI
    "EPIC-11": "ARGUS-94",    # Cartography NebulaGraph
    "EPIC-AUTH-001": "ARGUS-11",  # Unified Scanner Auth
}

# Story prefix to Epic mapping
STORY_PREFIX_TO_EPIC = {
    "PLAT": "EPIC-1",     # Platform stories
    "GRAPH": "EPIC-2",    # Graph stories
    "RISK": "EPIC-3",     # Risk stories
    "AUTO": "EPIC-4",     # Automation stories
    "UX": "EPIC-5",       # UX stories
    "INT": "EPIC-6",      # Integration stories
    "DIFF": "EPIC-7",     # Differentiation stories
    "DOM": "EPIC-8",      # Dominance stories
    "POL": "EPIC-9",      # Policy stories
    "CART": "EPIC-11",    # Cartography stories
    "AUTH": "EPIC-AUTH-001",  # Auth stories
}

# Load from environment
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")
JIRA_BASE_URL = "https://armor-defense.atlassian.net"


class JIRAEpicFixer:
    def __init__(self):
        self.session = requests.Session()
        self.session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.fixed = []
        self.skipped = []
        self.errors = []

    def _api_put(self, endpoint: str, data: dict) -> Tuple[bool, dict]:
        url = f"{JIRA_BASE_URL}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.put(url, json=data)
        if resp.status_code in (200, 204):
            return True, {}
        return False, {"error": resp.text, "status": resp.status_code}

    def _api_get(self, endpoint: str) -> dict:
        url = f"{JIRA_BASE_URL}/rest/api/3/{endpoint}"
        time.sleep(API_DELAY_MS / 1000)  # Rate limiting
        resp = self.session.get(url)
        if resp.status_code == 200:
            return resp.json()
        return {}

    def get_story_epic(self, story_id: str) -> str:
        """Determine the epic for a story based on its prefix"""
        for prefix, epic in STORY_PREFIX_TO_EPIC.items():
            if story_id.startswith(prefix):
                return epic
        return None

    def check_current_parent(self, jira_key: str) -> str:
        """Check if issue already has a parent"""
        issue = self._api_get(f"issue/{jira_key}?fields=parent")
        if issue and "fields" in issue:
            parent = issue["fields"].get("parent")
            if parent:
                return parent.get("key")
        return None

    def set_parent(self, story_key: str, epic_key: str) -> bool:
        """Set the parent of a story to the epic"""
        data = {
            "fields": {
                "parent": {"key": epic_key}
            }
        }
        success, result = self._api_put(f"issue/{story_key}", data)
        if not success:
            self.errors.append(f"Failed to set parent for {story_key}: {result}")
            return False
        return True

    def fix_epic_links(self):
        """Fix epic links for all synced stories"""
        # Load sync state
        if not STATE_FILE.exists():
            print(f"ERROR: State file not found: {STATE_FILE}")
            return

        with open(STATE_FILE) as f:
            state = yaml.safe_load(f)

        if not state or "items" not in state:
            print("ERROR: Invalid state file")
            return

        items = state["items"]
        total = len(items)
        print(f"\nProcessing {total} items...")
        print("=" * 60)

        for i, (story_id, info) in enumerate(items.items(), 1):
            jira_key = info.get("jira_key")
            if not jira_key:
                continue

            # Skip epics (they start with EPIC-)
            if story_id.startswith("EPIC-"):
                print(f"[{i}/{total}] SKIP {story_id} (is an epic)")
                self.skipped.append(story_id)
                continue

            # Determine the parent epic
            epic_id = self.get_story_epic(story_id)
            if not epic_id:
                print(f"[{i}/{total}] SKIP {story_id} -> {jira_key} (unknown epic mapping)")
                self.skipped.append(story_id)
                continue

            epic_key = EPIC_JIRA_KEYS.get(epic_id)
            if not epic_key:
                print(f"[{i}/{total}] SKIP {story_id} -> {jira_key} (epic {epic_id} not in JIRA)")
                self.skipped.append(story_id)
                continue

            # Check if already has correct parent
            current_parent = self.check_current_parent(jira_key)
            if current_parent == epic_key:
                print(f"[{i}/{total}] OK   {story_id} -> {jira_key} (already linked to {epic_key})")
                self.skipped.append(story_id)
                continue

            # Set the parent
            print(f"[{i}/{total}] FIX  {story_id} -> {jira_key} (linking to {epic_key})...", end=" ")
            if self.set_parent(jira_key, epic_key):
                print("DONE")
                self.fixed.append(f"{story_id} -> {epic_key}")
            else:
                print("FAILED")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Fixed:   {len(self.fixed)}")
        print(f"Skipped: {len(self.skipped)}")
        print(f"Errors:  {len(self.errors)}")

        if self.errors:
            print("\nERRORS:")
            for err in self.errors:
                print(f"  - {err}")


def main():
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("ERROR: Set JIRA_EMAIL and JIRA_API_TOKEN environment variables")
        print("\nUsage:")
        print("  export JIRA_EMAIL='your-email@company.com'")
        print("  export JIRA_API_TOKEN='your-api-token'")
        print("  python3 scripts/jira-fix-epic-links.py")
        sys.exit(1)

    fixer = JIRAEpicFixer()
    fixer.fix_epic_links()


if __name__ == "__main__":
    main()
