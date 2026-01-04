#!/usr/bin/env python3
"""
Comprehensive JIRA Sync Script for BMAD Structure v3.0

Syncs epics, stories, and tasks from .bmad/epics/ to JIRA with:
- Full hierarchy creation (Epic → Story → Task)
- Dependency link creation (Blocks/Is Blocked By)
- Local file updates with JIRA keys

Usage:
    # Dry run (show what would be created)
    python scripts/jira-sync-comprehensive.py --dry-run

    # Full sync
    python scripts/jira-sync-comprehensive.py

    # Sync specific epic
    python scripts/jira-sync-comprehensive.py --epic EPIC-1-PLATFORM

    # Only create dependency links (after issues exist)
    python scripts/jira-sync-comprehensive.py --links-only

    # Resume sync (skip existing JIRA keys)
    python scripts/jira-sync-comprehensive.py --resume

Environment Variables:
    ATLASSIAN_SITE      - JIRA site (default: armor-defense.atlassian.net)
    ATLASSIAN_EMAIL     - Your Atlassian email
    ATLASSIAN_API_TOKEN - Your API token
    JIRA_PROJECT_KEY    - Project key (default: ARGUS)

Author: Armor Security
"""

import os
import sys
import re
import json
import time
import argparse
import requests
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Set
from datetime import datetime
from markdown_to_adf import markdown_to_adf

PROJECT_ROOT = Path(__file__).parent.parent

# Auto-load .env file if it exists
def load_dotenv():
    """Load environment variables from .env file if it exists."""
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

# Rate limiting
RATE_LIMIT_DELAY = 0.25  # seconds between requests
MAX_RETRIES = 3


@dataclass
class Task:
    """Represents a task in the BMAD structure."""
    id: str  # e.g., "POLICY-001-T2"
    title: str
    story_id: str
    task_num: int
    file_path: Path
    requires: List[str] = field(default_factory=list)  # Task refs like "T1"
    unlocks: List[str] = field(default_factory=list)
    jira_key: str = ""
    status: str = "pending"


@dataclass
class Story:
    """Represents a story in the BMAD structure."""
    id: str  # e.g., "PLAT-002"
    title: str
    epic_id: str
    story_num: int
    file_path: Path
    points: int = 0
    priority: str = "P2"
    sprint: int = 0
    depends_on: List[str] = field(default_factory=list)  # Story refs like "S1"
    blocks: List[str] = field(default_factory=list)
    jira_key: str = ""
    status: str = "backlog"
    tasks: List[Task] = field(default_factory=list)


@dataclass
class Epic:
    """Represents an epic in the BMAD structure."""
    id: str  # e.g., "EPIC-1-PLATFORM"
    name: str
    file_path: Path
    summary: str = ""
    jira_key: str = ""
    owner: str = ""
    stories: List[Story] = field(default_factory=list)


class JiraClient:
    """Direct JIRA REST API client with rate limiting."""

    def __init__(self, site: str, email: str, api_token: str, project_key: str):
        self.base_url = f"https://{site}/rest/api/3"
        self.auth = (email, api_token)
        self.project_key = project_key
        self.last_request_time = 0

        # Issue type IDs (will be populated on first call)
        self._issue_types: Dict[str, str] = {}
        self._epic_link_field: Optional[str] = None

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def _request(self, method: str, endpoint: str, data: dict = None, retries: int = 0) -> dict:
        """Make a rate-limited request to JIRA API."""
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.request(
                method,
                url,
                auth=self.auth,
                headers=headers,
                json=data if data else None,
                timeout=30
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                print(f"  Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                return self._request(method, endpoint, data, retries)

            # Handle server errors with retry
            if response.status_code >= 500 and retries < MAX_RETRIES:
                print(f"  Server error {response.status_code}. Retrying ({retries + 1}/{MAX_RETRIES})...")
                time.sleep(5 * (retries + 1))
                return self._request(method, endpoint, data, retries + 1)

            if response.status_code == 204:
                return {}

            if not response.ok:
                error_text = response.text[:500]
                raise Exception(f"JIRA API error {response.status_code}: {error_text}")

            return response.json() if response.text else {}

        except requests.exceptions.Timeout:
            if retries < MAX_RETRIES:
                print(f"  Timeout. Retrying ({retries + 1}/{MAX_RETRIES})...")
                time.sleep(5)
                return self._request(method, endpoint, data, retries + 1)
            raise

    def get_issue_types(self) -> Dict[str, str]:
        """Get issue type name to ID mapping."""
        if self._issue_types:
            return self._issue_types

        project = self._request("GET", f"/project/{self.project_key}")
        for it in project.get("issueTypes", []):
            self._issue_types[it["name"]] = it["id"]

        return self._issue_types

    def get_epic_link_field(self) -> Optional[str]:
        """Find the Epic Link custom field ID."""
        if self._epic_link_field:
            return self._epic_link_field

        fields = self._request("GET", "/field")
        for f in fields:
            name_lower = f.get("name", "").lower()
            if f.get("custom") and ("epic link" in name_lower or "parent link" in name_lower):
                self._epic_link_field = f["id"]
                return self._epic_link_field

        return None

    def search_issues(self, jql: str, max_results: int = 100) -> List[dict]:
        """Search for issues using JQL."""
        result = self._request("POST", "/search/jql", {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["summary", "issuetype", "status", "parent"]
        })
        return result.get("issues", [])

    def create_issue(self, issue_type: str, summary: str, description: str = "",
                     parent_key: str = None, labels: List[str] = None,
                     priority: str = None) -> str:
        """Create a JIRA issue and return its key."""
        issue_types = self.get_issue_types()
        type_id = issue_types.get(issue_type)

        if not type_id:
            raise Exception(f"Unknown issue type: {issue_type}. Available: {list(issue_types.keys())}")

        fields = {
            "project": {"key": self.project_key},
            "issuetype": {"id": type_id},
            "summary": summary[:255],  # JIRA limit
        }

        if description:
            # Convert markdown to Atlassian Document Format for proper rendering
            fields["description"] = markdown_to_adf(description[:32000])

        if parent_key and issue_type.lower() in ("sub-task", "subtask"):
            fields["parent"] = {"key": parent_key}

        if labels:
            fields["labels"] = labels

        if priority:
            fields["priority"] = {"name": priority}

        result = self._request("POST", "/issue", {"fields": fields})
        return result["key"]

    def set_epic_link(self, issue_key: str, epic_key: str):
        """Set the Epic Link on an issue. Tries multiple methods."""
        # Try standard parent field first (works in team-managed projects)
        try:
            self._request("PUT", f"/issue/{issue_key}", {
                "fields": {"parent": {"key": epic_key}}
            })
            return
        except Exception:
            pass

        # Try Parent Link custom field
        try:
            self._request("PUT", f"/issue/{issue_key}", {
                "fields": {"customfield_10015": epic_key}
            })
            return
        except Exception:
            pass

        # Try Epic Link custom field
        epic_link_field = self.get_epic_link_field()
        if epic_link_field:
            self._request("PUT", f"/issue/{issue_key}", {
                "fields": {epic_link_field: epic_key}
            })

    def create_issue_link(self, inward_key: str, outward_key: str, link_type: str = "Blocks") -> bool:
        """Create an issue link."""
        try:
            self._request("POST", "/issueLink", {
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_key},
                "outwardIssue": {"key": outward_key}
            })
            return True
        except Exception as e:
            print(f"  WARNING: Failed to create link {inward_key} -> {outward_key}: {e}")
            return False


class BMadParser:
    """Parser for BMAD structure v3.0 files."""

    @staticmethod
    def parse_epic_readme(file_path: Path) -> Epic:
        """Parse an epic README.md file."""
        content = file_path.read_text()

        # Get epic ID from directory name
        epic_id = file_path.parent.name

        # Parse title - handle variations like "# EPIC-1: Title" or with leading chars
        title_match = re.search(r'#\s+(EPIC-[^:]+:\s*.+?)(?:\n|$)', content)
        if title_match:
            name = title_match.group(1).strip()
        else:
            # Fallback: use epic_id
            name = epic_id

        # Parse summary
        summary_match = re.search(r'##\s+Summary\s*\n+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        summary = summary_match.group(1).strip()[:500] if summary_match else ""

        # Parse owner
        owner_match = re.search(r'\*\*Owner:\*\*\s*(\S+)', content)
        owner = owner_match.group(1) if owner_match else ""

        return Epic(
            id=epic_id,
            name=name,
            file_path=file_path,
            summary=summary,
            owner=owner
        )

    @staticmethod
    def parse_story_file(file_path: Path, epic_id: str) -> Story:
        """Parse a story markdown file."""
        content = file_path.read_text()

        # Parse header - supports formats like:
        # "# PLAT-002: Title" or "# AUTH-001-1: Title" or "# CARTO-003: Title"
        header_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[A-Za-z]?):\s*(.+?)(?:\n|$)', content, re.MULTILINE)
        if header_match:
            story_id = header_match.group(1)
            title = header_match.group(2).strip()
        else:
            # Fallback: extract from filename
            story_id = file_path.stem.replace("story-", "").upper()
            title = story_id

        # Parse story number from directory name (e.g., "02-clickhouse-connection-pool")
        dir_match = re.match(r'^(\d+)-', file_path.parent.name)
        story_num = int(dir_match.group(1)) if dir_match else 0

        # Parse metadata line (e.g., "**Epic:** ARGUS-1 | **Points:** 2 | **Priority:** P0 | **Sprint:** 1")
        points = 0
        priority = "P2"
        sprint = 0
        status = "backlog"

        meta_match = re.search(r'\*\*Points:\*\*\s*(\d+)', content)
        if meta_match:
            points = int(meta_match.group(1))

        priority_match = re.search(r'\*\*Priority:\*\*\s*(P\d)', content)
        if priority_match:
            priority = priority_match.group(1)

        sprint_match = re.search(r'\*\*Sprint:\*\*\s*(\d+)', content)
        if sprint_match:
            sprint = int(sprint_match.group(1))

        status_match = re.search(r'\*\*Status:\*\*\s*(\S+)', content)
        if status_match:
            status = status_match.group(1)

        # Parse coordination table
        depends_on = []
        blocks = []
        jira_key = ""

        depends_match = re.search(r'\|\s*Depends On\s*\|\s*([^|]+)\s*\|', content)
        if depends_match:
            deps = depends_match.group(1).strip()
            if deps and deps.lower() not in ("none", "-", ""):
                depends_on = [d.strip() for d in re.split(r'[,\s]+', deps) if d.strip()]

        blocks_match = re.search(r'\|\s*Blocks\s*\|\s*([^|]+)\s*\|', content)
        if blocks_match:
            blks = blocks_match.group(1).strip()
            if blks and blks.lower() not in ("none", "-", ""):
                blocks = [b.strip() for b in re.split(r'[,\s]+', blks) if b.strip()]

        jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([^|]+)\s*\|', content)
        if jira_match:
            key = jira_match.group(1).strip()
            if key and re.match(r'^[A-Z]+-\d+$', key):
                jira_key = key

        return Story(
            id=story_id,
            title=title,
            epic_id=epic_id,
            story_num=story_num,
            file_path=file_path,
            points=points,
            priority=priority,
            sprint=sprint,
            depends_on=depends_on,
            blocks=blocks,
            jira_key=jira_key,
            status=status
        )

    @staticmethod
    def parse_task_file(file_path: Path, story_id: str) -> Task:
        """Parse a task markdown file."""
        content = file_path.read_text()

        # Parse header - supports formats like:
        # "# POLICY-001-T2: Title" or "# AUTH-001-1-T7: Title"
        header_match = re.search(r'^#\s+([A-Z]+-\d+(?:-\d+)?[A-Za-z]?-T\d+):\s*(.+?)(?:\n|$)', content, re.MULTILINE)
        if header_match:
            task_id = header_match.group(1)
            title = header_match.group(2).strip()
        else:
            # Fallback: extract from filename
            task_match = re.search(r'task-(\d+)', file_path.name)
            task_num = int(task_match.group(1)) if task_match else 1
            task_id = f"{story_id}-T{task_num}"
            title = "Implementation"

        # Parse task number
        task_num_match = re.search(r'-T(\d+)', task_id)
        task_num = int(task_num_match.group(1)) if task_num_match else 1

        # Parse coordination table
        requires = []
        unlocks = []
        jira_key = ""
        status = "pending"

        requires_match = re.search(r'\|\s*Requires\s*\|\s*([^|]+)\s*\|', content)
        if requires_match:
            reqs = requires_match.group(1).strip()
            if reqs and reqs.lower() not in ("none", "-", ""):
                requires = [r.strip() for r in re.split(r'[,\s]+', reqs) if r.strip()]

        unlocks_match = re.search(r'\|\s*Unlocks\s*\|\s*([^|]+)\s*\|', content)
        if unlocks_match:
            unls = unlocks_match.group(1).strip()
            if unls and unls.lower() not in ("none", "-", ""):
                unlocks = [u.strip() for u in re.split(r'[,\s]+', unls) if u.strip()]

        jira_match = re.search(r'\|\s*JIRA Key\s*\|\s*([^|]+)\s*\|', content)
        if jira_match:
            key = jira_match.group(1).strip()
            if key and re.match(r'^[A-Z]+-\d+$', key):
                jira_key = key

        status_match = re.search(r'\*\*Status:\*\*\s*(\S+)', content)
        if status_match:
            status = status_match.group(1)

        return Task(
            id=task_id,
            title=title,
            story_id=story_id,
            task_num=task_num,
            file_path=file_path,
            requires=requires,
            unlocks=unlocks,
            jira_key=jira_key,
            status=status
        )


class SyncState:
    """Manages sync state for resume capability."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.data: Dict = self._load()

    def _load(self) -> Dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {
            "epics": {},
            "stories": {},
            "tasks": {},
            "links_created": [],
            "last_sync": None
        }

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.data, indent=2))

    def get_epic_key(self, epic_id: str) -> Optional[str]:
        return self.data["epics"].get(epic_id)

    def set_epic_key(self, epic_id: str, jira_key: str):
        self.data["epics"][epic_id] = jira_key
        self.save()

    def get_story_key(self, story_id: str) -> Optional[str]:
        return self.data["stories"].get(story_id)

    def set_story_key(self, story_id: str, jira_key: str):
        self.data["stories"][story_id] = jira_key
        self.save()

    def get_task_key(self, task_id: str) -> Optional[str]:
        return self.data["tasks"].get(task_id)

    def set_task_key(self, task_id: str, jira_key: str):
        self.data["tasks"][task_id] = jira_key
        self.save()

    def is_link_created(self, from_key: str, to_key: str) -> bool:
        link_id = f"{from_key}->{to_key}"
        return link_id in self.data["links_created"]

    def mark_link_created(self, from_key: str, to_key: str):
        link_id = f"{from_key}->{to_key}"
        if link_id not in self.data["links_created"]:
            self.data["links_created"].append(link_id)
            self.save()


def update_jira_key_in_file(file_path: Path, jira_key: str):
    """Update the JIRA Key field in a markdown file."""
    content = file_path.read_text()

    # Pattern matches "| JIRA Key | <anything> |"
    pattern = r'(\|\s*JIRA Key\s*\|)\s*[^|]*\s*(\|)'
    replacement = rf'\1 {jira_key} \2'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        file_path.write_text(new_content)
        return True
    return False


def collect_bmad_data(epic_filter: str = None) -> List[Epic]:
    """Collect all epics, stories, and tasks from BMAD structure."""
    epics = []

    for epic_dir in sorted(EPICS_DIR.iterdir()):
        if not epic_dir.is_dir():
            continue

        # Apply epic filter if specified
        if epic_filter and epic_filter not in epic_dir.name:
            continue

        readme_path = epic_dir / "README.md"
        if not readme_path.exists():
            print(f"  WARNING: No README.md in {epic_dir.name}")
            continue

        epic = BMadParser.parse_epic_readme(readme_path)

        # Parse stories
        stories_dir = epic_dir / "stories"
        if stories_dir.exists():
            for story_dir in sorted(stories_dir.iterdir()):
                if not story_dir.is_dir():
                    continue

                # Find story file
                story_files = list(story_dir.glob("story-*.md"))
                if not story_files:
                    continue

                story = BMadParser.parse_story_file(story_files[0], epic.id)

                # Parse tasks
                tasks_dir = story_dir / "tasks"
                if tasks_dir.exists():
                    for task_file in sorted(tasks_dir.glob("task-*.md")):
                        task = BMadParser.parse_task_file(task_file, story.id)
                        story.tasks.append(task)

                epic.stories.append(story)

        epics.append(epic)

    return epics


def sync_to_jira(epics: List[Epic], client: JiraClient, state: SyncState,
                 dry_run: bool = False, resume: bool = False, links_only: bool = False):
    """Sync epics, stories, and tasks to JIRA."""

    stats = {
        "epics_created": 0,
        "stories_created": 0,
        "tasks_created": 0,
        "links_created": 0,
        "skipped": 0,
        "errors": 0
    }

    # Build ID to JIRA key mappings
    story_jira_keys: Dict[str, str] = {}  # story_id -> JIRA key
    task_jira_keys: Dict[str, str] = {}   # task_id -> JIRA key

    if not links_only:
        # Phase 1: Create Epics
        print("\n" + "=" * 60)
        print("Phase 1: Creating Epics")
        print("=" * 60)

        for epic in epics:
            existing_key = state.get_epic_key(epic.id) or epic.jira_key

            if resume and existing_key:
                print(f"  SKIP (exists): {epic.id} -> {existing_key}")
                stats["skipped"] += 1
                continue

            summary = f"{epic.name}"
            # Read full epic README content for description
            try:
                epic_content = epic.file_path.read_text()
                description = epic_content[:32000]  # JIRA description limit
            except Exception:
                description = epic.summary

            if dry_run:
                print(f"  DRY RUN: Would create Epic '{summary}'")
                stats["epics_created"] += 1
            else:
                try:
                    jira_key = client.create_issue(
                        issue_type="Epic",
                        summary=summary,
                        description=description,
                        labels=[epic.owner] if epic.owner else None
                    )
                    print(f"  CREATED: {epic.id} -> {jira_key}")
                    state.set_epic_key(epic.id, jira_key)
                    epic.jira_key = jira_key
                    stats["epics_created"] += 1

                    # Update local file
                    update_jira_key_in_file(epic.file_path, jira_key)

                except Exception as e:
                    print(f"  ERROR creating {epic.id}: {e}")
                    stats["errors"] += 1

        # Phase 2: Create Stories
        print("\n" + "=" * 60)
        print("Phase 2: Creating Stories")
        print("=" * 60)

        for epic in epics:
            epic_jira_key = state.get_epic_key(epic.id) or epic.jira_key

            for story in epic.stories:
                existing_key = state.get_story_key(story.id) or story.jira_key

                if resume and existing_key:
                    print(f"  SKIP (exists): {story.id} -> {existing_key}")
                    story_jira_keys[story.id] = existing_key
                    story.jira_key = existing_key
                    stats["skipped"] += 1
                    continue

                summary = f"[{story.id}] {story.title}"
                # Read full story content for description
                try:
                    story_content = story.file_path.read_text()
                    description = story_content[:32000]  # JIRA description limit
                except Exception:
                    description = f"Epic: {epic.name}\nSprint: {story.sprint}\nPoints: {story.points}"

                # Map P0-P3 to JIRA priority names
                priority_map = {
                    "P0": "Critical",
                    "P1": "High",
                    "P2": "Medium",
                    "P3": "Low",
                    "P4": "Low"
                }
                jira_priority = priority_map.get(story.priority, "Medium")

                if dry_run:
                    print(f"  DRY RUN: Would create Story '{summary}'")
                    stats["stories_created"] += 1
                else:
                    try:
                        jira_key = client.create_issue(
                            issue_type="Story",
                            summary=summary,
                            description=description,
                            priority=jira_priority
                        )
                        print(f"  CREATED: {story.id} -> {jira_key}")
                        state.set_story_key(story.id, jira_key)
                        story_jira_keys[story.id] = jira_key
                        story.jira_key = jira_key
                        stats["stories_created"] += 1

                        # Link to epic (may fail if field not on screen)
                        if epic_jira_key:
                            try:
                                client.set_epic_link(jira_key, epic_jira_key)
                            except Exception as link_err:
                                print(f"    (Epic link skipped: {str(link_err)[:50]})")

                        # Update local file
                        update_jira_key_in_file(story.file_path, jira_key)

                    except Exception as e:
                        print(f"  ERROR creating {story.id}: {e}")
                        stats["errors"] += 1

        # Phase 3: Create Tasks (as Sub-tasks under Stories)
        print("\n" + "=" * 60)
        print("Phase 3: Creating Tasks")
        print("=" * 60)

        for epic in epics:
            for story in epic.stories:
                story_jira_key = state.get_story_key(story.id) or story.jira_key

                if not story_jira_key:
                    print(f"  SKIP: No JIRA key for story {story.id}")
                    continue

                for task in story.tasks:
                    existing_key = state.get_task_key(task.id) or task.jira_key

                    if resume and existing_key:
                        print(f"  SKIP (exists): {task.id} -> {existing_key}")
                        task_jira_keys[task.id] = existing_key
                        task.jira_key = existing_key
                        stats["skipped"] += 1
                        continue

                    summary = f"[{task.id}] {task.title}"
                    # Read full task content for description (includes AI prompts)
                    try:
                        task_content = task.file_path.read_text()
                        task_description = task_content[:32000]  # JIRA description limit
                    except Exception:
                        task_description = ""

                    if dry_run:
                        print(f"  DRY RUN: Would create Task '{summary}'")
                        stats["tasks_created"] += 1
                    else:
                        try:
                            jira_key = client.create_issue(
                                issue_type="Subtask",
                                summary=summary,
                                description=task_description,
                                parent_key=story_jira_key
                            )
                            print(f"  CREATED: {task.id} -> {jira_key}")
                            state.set_task_key(task.id, jira_key)
                            task_jira_keys[task.id] = jira_key
                            task.jira_key = jira_key
                            stats["tasks_created"] += 1

                            # Update local file
                            update_jira_key_in_file(task.file_path, jira_key)

                        except Exception as e:
                            print(f"  ERROR creating {task.id}: {e}")
                            stats["errors"] += 1

    # Reload state for link creation
    for epic in epics:
        for story in epic.stories:
            story.jira_key = state.get_story_key(story.id) or story.jira_key
            story_jira_keys[story.id] = story.jira_key

            for task in story.tasks:
                task.jira_key = state.get_task_key(task.id) or task.jira_key
                task_jira_keys[task.id] = task.jira_key

    # Phase 4: Create Dependency Links
    print("\n" + "=" * 60)
    print("Phase 4: Creating Dependency Links")
    print("=" * 60)

    if dry_run:
        print("  DRY RUN: Skipping link creation")
    else:
        # Story dependencies (S1, S2, etc. refer to story numbers within same epic)
        for epic in epics:
            # Build story number to JIRA key mapping for this epic
            story_num_to_key: Dict[int, str] = {}
            for story in epic.stories:
                if story.jira_key:
                    story_num_to_key[story.story_num] = story.jira_key

            for story in epic.stories:
                if not story.jira_key:
                    continue

                # Create "is blocked by" links for depends_on
                for dep in story.depends_on:
                    dep_match = re.match(r'S(\d+)', dep)
                    if dep_match:
                        dep_num = int(dep_match.group(1))
                        dep_key = story_num_to_key.get(dep_num)
                        if dep_key:
                            if not state.is_link_created(dep_key, story.jira_key):
                                if client.create_issue_link(dep_key, story.jira_key, "Blocks"):
                                    print(f"  LINKED: {dep_key} blocks {story.jira_key}")
                                    state.mark_link_created(dep_key, story.jira_key)
                                    stats["links_created"] += 1
                            else:
                                print(f"  SKIP (exists): {dep_key} -> {story.jira_key}")

        # Task dependencies (T1, T2, etc. refer to task numbers within same story)
        for epic in epics:
            for story in epic.stories:
                # Build task number to JIRA key mapping for this story
                task_num_to_key: Dict[int, str] = {}
                for task in story.tasks:
                    if task.jira_key:
                        task_num_to_key[task.task_num] = task.jira_key

                for task in story.tasks:
                    if not task.jira_key:
                        continue

                    # Create "is blocked by" links for requires
                    for req in task.requires:
                        req_match = re.match(r'T(\d+)', req)
                        if req_match:
                            req_num = int(req_match.group(1))
                            req_key = task_num_to_key.get(req_num)
                            if req_key:
                                if not state.is_link_created(req_key, task.jira_key):
                                    if client.create_issue_link(req_key, task.jira_key, "Blocks"):
                                        print(f"  LINKED: {req_key} blocks {task.jira_key}")
                                        state.mark_link_created(req_key, task.jira_key)
                                        stats["links_created"] += 1
                                else:
                                    print(f"  SKIP (exists): {req_key} -> {task.jira_key}")

    # Summary
    print("\n" + "=" * 60)
    print("Sync Summary")
    print("=" * 60)
    print(f"  Epics created:   {stats['epics_created']}")
    print(f"  Stories created: {stats['stories_created']}")
    print(f"  Tasks created:   {stats['tasks_created']}")
    print(f"  Links created:   {stats['links_created']}")
    print(f"  Skipped:         {stats['skipped']}")
    print(f"  Errors:          {stats['errors']}")

    state.data["last_sync"] = datetime.now().isoformat()
    state.save()

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive JIRA sync for BMAD structure v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    parser.add_argument("--resume", action="store_true", help="Skip items that already have JIRA keys")
    parser.add_argument("--links-only", action="store_true", help="Only create dependency links")
    parser.add_argument("--epic", help="Only sync specific epic (e.g., EPIC-1-PLATFORM)")
    parser.add_argument("--stats-only", action="store_true", help="Show statistics without syncing")

    args = parser.parse_args()

    print("=" * 60)
    print("Comprehensive JIRA Sync")
    print("=" * 60)
    print(f"Site:     {SITE}")
    print(f"Project:  {PROJECT_KEY}")
    print(f"Dry Run:  {args.dry_run}")
    print(f"Resume:   {args.resume}")

    # Validate credentials
    if not args.dry_run and not args.stats_only:
        if not EMAIL or not API_TOKEN:
            print("\nERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables")
            sys.exit(1)

    # Collect data
    print("\nCollecting BMAD data...")
    epics = collect_bmad_data(epic_filter=args.epic)

    total_stories = sum(len(e.stories) for e in epics)
    total_tasks = sum(len(s.tasks) for e in epics for s in e.stories)

    print(f"  Found {len(epics)} epics")
    print(f"  Found {total_stories} stories")
    print(f"  Found {total_tasks} tasks")

    if args.stats_only:
        print("\n" + "=" * 60)
        print("Detailed Statistics")
        print("=" * 60)
        for epic in epics:
            epic_stories = len(epic.stories)
            epic_tasks = sum(len(s.tasks) for s in epic.stories)
            print(f"  {epic.id}: {epic_stories} stories, {epic_tasks} tasks")
        return

    # Initialize client and state
    client = None
    if not args.dry_run:
        client = JiraClient(SITE, EMAIL, API_TOKEN, PROJECT_KEY)

    state = SyncState(STATE_FILE)

    # Sync
    sync_to_jira(
        epics=epics,
        client=client,
        state=state,
        dry_run=args.dry_run,
        resume=args.resume,
        links_only=args.links_only
    )


if __name__ == "__main__":
    main()
