#!/usr/bin/env python3
"""
Comprehensive JIRA Sync - All-in-One Script

This script handles the complete BMAD to JIRA sync workflow:
1. Reset references to clean state (optional)
2. Create JIRA issues (epics, stories, tasks)
3. Create dependency links
4. Convert all references to JIRA keys
5. Update JIRA with final content
6. Validate sync integrity

Usage:
    python jira-sync-all.py --epic EPIC-AUTH-001           # Sync specific epic
    python jira-sync-all.py --epic EPIC-AUTH-001 --reset   # Reset + sync
    python jira-sync-all.py --epic EPIC-AUTH-001 --validate-only  # Just validate
    python jira-sync-all.py --epic EPIC-AUTH-001 --resume  # Resume failed sync
"""

import argparse
import os
import re
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Import ADF converter
sys.path.insert(0, str(Path(__file__).parent))
from markdown_to_adf import markdown_to_adf

PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad/epics"

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
class SyncState:
    """Tracks sync progress and mappings."""
    epic_map: Dict[str, str] = field(default_factory=dict)     # EPIC-AUTH-001 -> ARGUS-1276
    story_map: Dict[str, str] = field(default_factory=dict)    # AUTH-001-1 -> ARGUS-1277
    task_map: Dict[str, str] = field(default_factory=dict)     # AUTH-001-1-T1 -> ARGUS-1285
    errors: List[str] = field(default_factory=list)
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0


class JiraClient:
    """JIRA API client with rate limiting and retry."""

    def __init__(self):
        self.session = requests.Session()
        self.session.auth = AUTH
        self.session.headers.update(HEADERS)
        self._issue_types = None
        self._epic_link_field = None

    def request(self, method: str, endpoint: str, data: dict = None) -> Any:
        """Make request with retry and rate limiting."""
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
                    print(f"    RETRY: Request timed out, attempt {attempt + 2}")
                    time.sleep(2)
                else:
                    raise

    def get_issue_types(self) -> Dict[str, str]:
        """Get project issue types as name -> id mapping."""
        if self._issue_types:
            return self._issue_types

        project = self.request("GET", f"/project/{PROJECT_KEY}")
        self._issue_types = {it["name"]: it["id"] for it in project.get("issueTypes", [])}
        return self._issue_types

    def get_epic_link_field(self) -> Optional[str]:
        """Find the Epic Link custom field ID."""
        if self._epic_link_field:
            return self._epic_link_field

        fields = self.request("GET", "/field")
        for f in fields:
            name = f.get("name", "").lower()
            if f.get("custom") and ("epic link" in name or "parent link" in name):
                self._epic_link_field = f["id"]
                return self._epic_link_field
        return None

    def create_issue(self, issue_type: str, summary: str, description: str = "",
                     parent_key: str = None) -> Optional[str]:
        """Create JIRA issue, return key or None on error."""
        issue_types = self.get_issue_types()
        type_id = issue_types.get(issue_type)
        if not type_id:
            print(f"    ERROR: Unknown issue type: {issue_type}. Available: {list(issue_types.keys())}")
            return None

        fields = {
            "project": {"key": PROJECT_KEY},
            "issuetype": {"id": type_id},
            "summary": summary[:255],
            "description": markdown_to_adf(description[:32000]) if description else None
        }

        # For subtasks, set parent
        if parent_key and issue_type.lower() == "subtask":
            fields["parent"] = {"key": parent_key}

        # Remove None values
        fields = {k: v for k, v in fields.items() if v is not None}

        try:
            result = self.request("POST", "/issue", {"fields": fields})
            return result.get("key")
        except Exception as e:
            print(f"    ERROR: {e}")
            return None

    def set_epic_link(self, issue_key: str, epic_key: str) -> bool:
        """Set Epic Link on an issue using multiple fallback methods."""
        # Method 1: Standard parent field (works in team-managed projects)
        try:
            self.request("PUT", f"/issue/{issue_key}", {
                "fields": {"parent": {"key": epic_key}}
            })
            return True
        except Exception:
            pass

        # Method 2: Parent Link custom field
        try:
            self.request("PUT", f"/issue/{issue_key}", {
                "fields": {"customfield_10015": epic_key}
            })
            return True
        except Exception:
            pass

        # Method 3: Epic Link custom field
        epic_link_field = self.get_epic_link_field()
        if epic_link_field:
            try:
                self.request("PUT", f"/issue/{issue_key}", {
                    "fields": {epic_link_field: epic_key}
                })
                return True
            except Exception:
                pass

        return False

    def update_issue(self, key: str, fields: dict) -> bool:
        """Update JIRA issue fields."""
        try:
            self.request("PUT", f"/issue/{key}", {"fields": fields})
            return True
        except Exception as e:
            print(f"    ERROR updating {key}: {e}")
            return False

    def create_link(self, from_key: str, to_key: str, link_type: str = "Blocks") -> bool:
        """Create issue link."""
        try:
            self.request("POST", "/issueLink", {
                "type": {"name": link_type},
                "inwardIssue": {"key": from_key},
                "outwardIssue": {"key": to_key}
            })
            return True
        except Exception:
            return False

    def search_issue(self, summary: str, issue_type: str) -> Optional[str]:
        """Search for existing issue by summary and type."""
        # Escape special chars in summary for JQL
        escaped = summary.replace('"', '\\"').replace("'", "\\'")
        jql = f'project = {PROJECT_KEY} AND summary ~ "{escaped}" AND issuetype = "{issue_type}"'
        try:
            result = self.request("POST", "/search/jql", {"jql": jql, "fields": ["key", "summary"]})
            for issue in result.get("issues", []):
                if issue["fields"]["summary"] == summary:
                    return issue["key"]
        except Exception:
            pass
        return None

    def search_issues_by_jql(self, jql: str) -> List[str]:
        """Search issues by JQL, return list of keys."""
        try:
            result = self.request("POST", "/search/jql", {"jql": jql, "fields": ["key"], "maxResults": 1000})
            return [issue["key"] for issue in result.get("issues", [])]
        except Exception:
            return []

    def delete_issue(self, key: str, delete_subtasks: bool = True) -> bool:
        """Delete an issue."""
        try:
            url = f"{BASE_URL}/issue/{key}"
            if delete_subtasks:
                url += "?deleteSubtasks=true"
            resp = self.session.delete(url, timeout=30)
            return resp.status_code == 204
        except Exception:
            return False


def extract_jira_key(content: str) -> str:
    """Extract JIRA key from file content."""
    match = re.search(r'\|\s*JIRA Key\s*\|\s*([A-Z]+-\d+)\s*\|', content)
    return match.group(1) if match else ""


def update_jira_key_in_file(file_path: Path, jira_key: str) -> None:
    """Update JIRA Key field in file."""
    content = file_path.read_text()
    new_content = re.sub(
        r'(\|\s*JIRA Key\s*\|)\s*[^|]*(\|)',
        f'\\1 {jira_key} \\2',
        content
    )
    if new_content != content:
        file_path.write_text(new_content)


def reset_references(epic_dir: Path) -> int:
    """Reset all refs to T1, T2 format. Returns count of files reset."""
    reset_count = 0

    stories_dir = epic_dir / "stories"
    if not stories_dir.exists():
        return 0

    for story_dir in sorted(stories_dir.iterdir()):
        if not story_dir.is_dir():
            continue

        tasks_dir = story_dir / "tasks"
        if not tasks_dir.exists():
            continue

        task_files = sorted(tasks_dir.glob("task-*.md"))
        max_task = len(task_files)

        for task_file in task_files:
            content = task_file.read_text()
            original = content

            task_match = re.search(r'^#\s+[A-Z]+-\d+-\d+[a-z]?-(T\d+):', content, re.MULTILINE)
            if not task_match:
                continue

            task_int = int(task_match.group(1)[1:])

            # Reset Requires
            if task_int == 1:
                content = re.sub(r'(\|\s*Requires\s*\|\s*)[^|]+(\|)', r'\1none \2', content)
            else:
                content = re.sub(r'(\|\s*Requires\s*\|\s*)[^|]+(\|)', f'\\1T{task_int - 1} \\2', content)

            # Reset Unlocks
            if task_int == max_task:
                content = re.sub(r'(\|\s*Unlocks\s*\|\s*)[^|]+(\|)', r'\1none \2', content)
            else:
                content = re.sub(r'(\|\s*Unlocks\s*\|\s*)[^|]+(\|)', f'\\1T{task_int + 1} \\2', content)

            # Clear JIRA Key
            content = re.sub(r'(\|\s*JIRA Key\s*\|)\s*[^|]+(\|)', r'\1 \2', content)

            if content != original:
                task_file.write_text(content)
                reset_count += 1

    # Reset story JIRA keys
    for story_dir in sorted(stories_dir.iterdir()):
        if not story_dir.is_dir():
            continue
        story_files = list(story_dir.glob("story-*.md"))
        if story_files:
            content = story_files[0].read_text()
            new_content = re.sub(r'(\|\s*JIRA Key\s*\|)\s*[^|]+(\|)', r'\1 \2', content)
            if new_content != content:
                story_files[0].write_text(new_content)
                reset_count += 1

    # Reset epic JIRA key
    readme = epic_dir / "README.md"
    if readme.exists():
        content = readme.read_text()
        new_content = re.sub(r'(\|\s*JIRA Key\s*\|)\s*[^|]+(\|)', r'\1 \2', content)
        if new_content != content:
            readme.write_text(new_content)
            reset_count += 1

    return reset_count


def collect_epic_data(epic_dir: Path) -> dict:
    """Collect all epic, story, task data."""
    data = {"epic": None, "stories": [], "tasks": []}

    readme = epic_dir / "README.md"
    if readme.exists():
        content = readme.read_text()
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        data["epic"] = {
            "id": epic_dir.name,
            "title": title_match.group(1) if title_match else epic_dir.name,
            "content": content,
            "file": readme,
            "jira_key": extract_jira_key(content)
        }

    stories_dir = epic_dir / "stories"
    if not stories_dir.exists():
        return data

    for story_dir in sorted(stories_dir.iterdir()):
        if not story_dir.is_dir():
            continue

        story_files = list(story_dir.glob("story-*.md"))
        if not story_files:
            continue

        content = story_files[0].read_text()
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        id_match = re.search(r'^#\s+([A-Z]+-\d+-\d+[a-z]?):', content, re.MULTILINE)

        depends_match = re.search(r'\|\s*Depends On\s*\|\s*([^|]+)\|', content)
        blocks_match = re.search(r'\|\s*Blocks\s*\|\s*([^|]+)\|', content)

        story = {
            "id": id_match.group(1) if id_match else story_dir.name,
            "num": id_match.group(1).split("-")[-1] if id_match else "",
            "title": title_match.group(1) if title_match else story_dir.name,
            "content": content,
            "file": story_files[0],
            "dir_name": story_dir.name,
            "jira_key": extract_jira_key(content),
            "depends_on": depends_match.group(1).strip() if depends_match else "",
            "blocks": blocks_match.group(1).strip() if blocks_match else ""
        }
        data["stories"].append(story)

        tasks_dir = story_dir / "tasks"
        if not tasks_dir.exists():
            continue

        for task_file in sorted(tasks_dir.glob("task-*.md")):
            content = task_file.read_text()
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            id_match = re.search(r'^#\s+([A-Z]+-\d+-\d+[a-z]?-T\d+):', content, re.MULTILINE)

            req_match = re.search(r'\|\s*Requires\s*\|\s*([^|]+)\|', content)
            unlock_match = re.search(r'\|\s*Unlocks\s*\|\s*([^|]+)\|', content)

            task = {
                "id": id_match.group(1) if id_match else task_file.stem,
                "title": title_match.group(1) if title_match else task_file.stem,
                "content": content,
                "file": task_file,
                "story_id": story["id"],
                "story_dir_name": story_dir.name,
                "jira_key": extract_jira_key(content),
                "requires": req_match.group(1).strip() if req_match else "",
                "unlocks": unlock_match.group(1).strip() if unlock_match else ""
            }
            data["tasks"].append(task)

    return data


def create_jira_issues(client: JiraClient, data: dict, state: SyncState, resume: bool = False) -> None:
    """Create JIRA issues for epic, stories, tasks."""

    # 1. Create Epic
    if data["epic"]:
        epic = data["epic"]
        existing = epic["jira_key"] or (client.search_issue(epic["title"], "Epic") if resume else None)

        if existing:
            print(f"  SKIP (exists): {epic['id']} -> {existing}")
            state.epic_map[epic["id"]] = existing
            state.skipped_count += 1
        else:
            key = client.create_issue("Epic", epic["title"], epic["content"])
            if key:
                print(f"  CREATED: {epic['id']} -> {key}")
                state.epic_map[epic["id"]] = key
                state.created_count += 1
                update_jira_key_in_file(epic["file"], key)
            else:
                state.errors.append(f"Failed to create epic {epic['id']}")

    epic_key = state.epic_map.get(data["epic"]["id"]) if data["epic"] else None

    # 2. Create Stories
    for story in data["stories"]:
        existing = story["jira_key"] or (client.search_issue(story["title"], "Story") if resume else None)

        if existing:
            print(f"  SKIP (exists): {story['id']} -> {existing}")
            state.story_map[story["id"]] = existing
            state.story_map[story["num"]] = existing
            state.story_map[f"S{story['num']}"] = existing
            state.skipped_count += 1
        else:
            key = client.create_issue("Story", story["title"], story["content"])
            if key:
                print(f"  CREATED: {story['id']} -> {key}")
                state.story_map[story["id"]] = key
                state.story_map[story["num"]] = key
                state.story_map[f"S{story['num']}"] = key
                state.created_count += 1
                update_jira_key_in_file(story["file"], key)

                # Set Epic Link after creation
                if epic_key:
                    if client.set_epic_link(key, epic_key):
                        print(f"    Linked to epic {epic_key}")
            else:
                state.errors.append(f"Failed to create story {story['id']}")

    # 3. Create Tasks
    for task in data["tasks"]:
        story_key = state.story_map.get(task["story_id"])
        existing = task["jira_key"] or (client.search_issue(task["title"], "Subtask") if resume else None)

        if existing:
            print(f"  SKIP (exists): {task['id']} -> {existing}")
            state.task_map[task["id"]] = existing
            t_num = task["id"].split("-T")[-1] if "-T" in task["id"] else ""
            if t_num:
                state.task_map[(task["story_dir_name"], f"T{t_num}")] = existing
            state.skipped_count += 1
        else:
            if not story_key:
                print(f"  SKIP (no parent): {task['id']}")
                state.errors.append(f"Task {task['id']} has no parent story")
                continue

            key = client.create_issue("Subtask", task["title"], task["content"], parent_key=story_key)
            if key:
                print(f"  CREATED: {task['id']} -> {key}")
                state.task_map[task["id"]] = key
                t_num = task["id"].split("-T")[-1] if "-T" in task["id"] else ""
                if t_num:
                    state.task_map[(task["story_dir_name"], f"T{t_num}")] = key
                state.created_count += 1
                update_jira_key_in_file(task["file"], key)
            else:
                state.errors.append(f"Failed to create task {task['id']}")


def create_dependency_links(client: JiraClient, data: dict, state: SyncState) -> int:
    """Create dependency links between issues."""
    links_created = 0

    # Story dependencies
    for story in data["stories"]:
        story_key = state.story_map.get(story["id"])
        if not story_key:
            continue

        if story["blocks"] and story["blocks"] not in ["-", "none"]:
            for ref in story["blocks"].split(","):
                ref = ref.strip()
                target_key = state.story_map.get(ref) or state.story_map.get(f"S{ref}")
                if target_key and target_key != story_key:
                    if client.create_link(story_key, target_key, "Blocks"):
                        print(f"  LINKED: {story_key} blocks {target_key}")
                        links_created += 1

    # Task dependencies
    for task in data["tasks"]:
        task_key = state.task_map.get(task["id"])
        if not task_key:
            continue

        if task["unlocks"] and task["unlocks"] not in ["-", "none"]:
            for ref in task["unlocks"].split(","):
                ref = ref.strip()
                target_key = state.task_map.get((task["story_dir_name"], ref))
                if target_key and target_key != task_key:
                    if client.create_link(task_key, target_key, "Blocks"):
                        print(f"  LINKED: {task_key} blocks {target_key}")
                        links_created += 1

    return links_created


def convert_refs_to_jira_keys(data: dict, state: SyncState) -> Tuple[int, int]:
    """Convert all refs in files to JIRA keys."""
    stories_fixed = 0
    tasks_fixed = 0

    for story in data["stories"]:
        content = story["file"].read_text()
        original = content

        def convert_story_refs(match):
            prefix, refs, suffix = match.group(1), match.group(2), match.group(3)
            if refs.strip() in ["-", "none", ""]:
                return match.group(0)
            parts = [p.strip() for p in refs.split(",")]
            converted = []
            for p in parts:
                key = state.story_map.get(p) or state.story_map.get(f"S{p}")
                converted.append(key if key else p)
            return f"{prefix}{', '.join(converted)} {suffix}"

        content = re.sub(r'(\|\s*Depends On\s*\|\s*)([^|]+)(\|)', convert_story_refs, content)
        content = re.sub(r'(\|\s*Blocks\s*\|\s*)([^|]+)(\|)', convert_story_refs, content)

        if content != original:
            story["file"].write_text(content)
            stories_fixed += 1

    for task in data["tasks"]:
        content = task["file"].read_text()
        original = content

        def convert_task_refs(match):
            prefix, refs, suffix = match.group(1), match.group(2), match.group(3)
            if refs.strip() in ["-", "none", ""]:
                return match.group(0)
            parts = [p.strip() for p in refs.split(",")]
            converted = []
            for p in parts:
                key = state.task_map.get((task["story_dir_name"], p))
                converted.append(key if key else p)
            return f"{prefix}{', '.join(converted)} {suffix}"

        content = re.sub(r'(\|\s*Requires\s*\|\s*)([^|]+)(\|)', convert_task_refs, content)
        content = re.sub(r'(\|\s*Unlocks\s*\|\s*)([^|]+)(\|)', convert_task_refs, content)

        if content != original:
            task["file"].write_text(content)
            tasks_fixed += 1

    return stories_fixed, tasks_fixed


def update_jira_descriptions(client: JiraClient, data: dict, state: SyncState) -> int:
    """Update JIRA descriptions with final content."""
    updated = 0

    if data["epic"]:
        key = state.epic_map.get(data["epic"]["id"])
        if key:
            content = data["epic"]["file"].read_text()
            if client.update_issue(key, {"description": markdown_to_adf(content[:32000])}):
                print(f"  UPDATED: {key}")
                updated += 1

    for story in data["stories"]:
        key = state.story_map.get(story["id"])
        if key:
            content = story["file"].read_text()
            if client.update_issue(key, {"description": markdown_to_adf(content[:32000])}):
                print(f"  UPDATED: {key}")
                updated += 1

    for task in data["tasks"]:
        key = state.task_map.get(task["id"])
        if key:
            content = task["file"].read_text()
            if client.update_issue(key, {"description": markdown_to_adf(content[:32000])}):
                print(f"  UPDATED: {key}")
                updated += 1

    return updated


def validate_sync(data: dict, state: SyncState) -> List[str]:
    """Validate sync integrity."""
    issues = []

    if data["epic"] and not state.epic_map.get(data["epic"]["id"]):
        issues.append(f"Epic {data['epic']['id']} has no JIRA key")

    for story in data["stories"]:
        if not state.story_map.get(story["id"]):
            issues.append(f"Story {story['id']} has no JIRA key")

    for task in data["tasks"]:
        if not state.task_map.get(task["id"]):
            issues.append(f"Task {task['id']} has no JIRA key")

    # Check refs are JIRA keys
    for story in data["stories"]:
        content = story["file"].read_text()
        for field_name in ["Depends On", "Blocks"]:
            match = re.search(rf'\|\s*{field_name}\s*\|\s*([^|]+)\|', content)
            if match:
                refs = match.group(1).strip()
                if refs and refs not in ["-", "none"]:
                    for ref in refs.split(","):
                        ref = ref.strip()
                        if ref and not re.match(r'[A-Z]+-\d+', ref):
                            issues.append(f"Story {story['id']} {field_name} has non-JIRA ref: {ref}")

    for task in data["tasks"]:
        content = task["file"].read_text()
        for field_name in ["Requires", "Unlocks"]:
            match = re.search(rf'\|\s*{field_name}\s*\|\s*([^|]+)\|', content)
            if match:
                refs = match.group(1).strip()
                if refs and refs not in ["-", "none"]:
                    for ref in refs.split(","):
                        ref = ref.strip()
                        if ref and not re.match(r'[A-Z]+-\d+', ref):
                            issues.append(f"Task {task['id']} {field_name} has non-JIRA ref: {ref}")

    return issues


def clean_jira_issues(client: JiraClient, epic_title: str) -> int:
    """Delete all existing issues for this epic. Returns count deleted."""
    deleted = 0

    # Find epics with matching title
    escaped = epic_title.replace('"', '\\"').replace("'", "\\'")
    epic_keys = client.search_issues_by_jql(
        f'project = {PROJECT_KEY} AND issuetype = Epic AND summary ~ "{escaped}"'
    )

    for key in epic_keys:
        # First delete stories (which deletes their subtasks)
        story_keys = client.search_issues_by_jql(
            f'project = {PROJECT_KEY} AND issuetype = Story AND parent = {key}'
        )
        for story_key in story_keys:
            if client.delete_issue(story_key, delete_subtasks=True):
                print(f"  DELETED: {story_key} (with subtasks)")
                deleted += 1

        # Then delete the epic
        if client.delete_issue(key):
            print(f"  DELETED: {key} (Epic)")
            deleted += 1

    return deleted


def build_epic_jira_map() -> Dict[str, str]:
    """Build mapping of epic IDs to JIRA keys from all epic READMEs."""
    mapping = {}
    for epic_dir in EPICS_DIR.iterdir():
        if not epic_dir.is_dir():
            continue
        readme = epic_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            jira_key = extract_jira_key(content)
            if jira_key:
                mapping[epic_dir.name] = jira_key
                # Also map without prefix variations
                name = epic_dir.name
                if name.startswith("EPIC-"):
                    mapping[name[5:]] = jira_key  # "1-PLATFORM" -> ARGUS-XXX
    return mapping


def convert_epic_refs(data: dict, epic_map: Dict[str, str]) -> int:
    """Convert epic-level Depends On/Blocks refs to JIRA keys."""
    if not data["epic"]:
        return 0

    content = data["epic"]["file"].read_text()
    original = content

    def convert_refs(match):
        prefix, refs, suffix = match.group(1), match.group(2), match.group(3)
        if refs.strip().lower() in ["-", "none", ""]:
            return match.group(0)
        parts = [p.strip() for p in refs.split(",")]
        converted = []
        for p in parts:
            # Try exact match, then with EPIC- prefix
            key = epic_map.get(p) or epic_map.get(f"EPIC-{p}")
            converted.append(key if key else p)
        return f"{prefix}{', '.join(converted)} {suffix}"

    content = re.sub(r'(\|\s*Depends On\s*\|\s*)([^|]+)(\|)', convert_refs, content)
    content = re.sub(r'(\|\s*Blocks\s*\|\s*)([^|]+)(\|)', convert_refs, content)

    if content != original:
        data["epic"]["file"].write_text(content)
        return 1
    return 0


def fix_all_references(epic_dirs: List[Path], client: JiraClient, update_jira: bool = True) -> Tuple[int, int, int, List[str]]:
    """
    Fix ALL references to use JIRA keys.
    Returns (epics_fixed, stories_fixed, tasks_fixed, issues).
    """
    # Build complete mappings from existing files
    epic_map = build_epic_jira_map()
    print(f"  Epic mappings: {len(epic_map)}")

    # Build story and task mappings
    state = SyncState()
    all_data = []

    for epic_dir in epic_dirs:
        data = collect_epic_data(epic_dir)
        all_data.append(data)

        # Add to state mappings
        if data["epic"] and data["epic"]["jira_key"]:
            state.epic_map[data["epic"]["id"]] = data["epic"]["jira_key"]

        for story in data["stories"]:
            if story["jira_key"]:
                state.story_map[story["id"]] = story["jira_key"]
                state.story_map[story["num"]] = story["jira_key"]
                state.story_map[f"S{story['num']}"] = story["jira_key"]

        for task in data["tasks"]:
            if task["jira_key"]:
                state.task_map[task["id"]] = task["jira_key"]
                t_num = task["id"].split("-T")[-1] if "-T" in task["id"] else ""
                if t_num:
                    state.task_map[(task["story_dir_name"], f"T{t_num}")] = task["jira_key"]

    print(f"  Story mappings: {len(state.story_map)}")
    print(f"  Task mappings: {len(state.task_map)}")

    # Convert all refs
    epics_fixed = 0
    stories_fixed = 0
    tasks_fixed = 0

    for data in all_data:
        s, t = convert_refs_to_jira_keys(data, state)
        stories_fixed += s
        tasks_fixed += t
        e = convert_epic_refs(data, epic_map)
        epics_fixed += e

    print(f"\n  Fixed: {epics_fixed} epics, {stories_fixed} stories, {tasks_fixed} tasks")

    # Update JIRA if requested
    if update_jira:
        print("\n  Updating JIRA descriptions...")
        updated = 0
        for data in all_data:
            updated += update_jira_descriptions(client, data, state)
        print(f"  Updated {updated} issues")

    # Validate
    all_issues = []
    for data in all_data:
        all_issues.extend(validate_sync(data, state))

    return epics_fixed, stories_fixed, tasks_fixed, all_issues


def main():
    parser = argparse.ArgumentParser(description="Comprehensive JIRA Sync")
    parser.add_argument("--epic", required=True, help="Epic directory name (or 'all' for all epics)")
    parser.add_argument("--reset", action="store_true", help="Reset local refs before sync")
    parser.add_argument("--clean-jira", action="store_true", help="Delete existing JIRA issues before sync")
    parser.add_argument("--resume", action="store_true", help="Resume failed sync")
    parser.add_argument("--fix-refs-only", action="store_true", help="Only fix references (no sync)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate")
    parser.add_argument("--skip-update", action="store_true", help="Skip final JIRA update")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    # Handle "all" option
    if args.epic.lower() == "all":
        epic_dirs = sorted([d for d in EPICS_DIR.iterdir() if d.is_dir()])
    else:
        epic_dir = EPICS_DIR / args.epic
        if not epic_dir.exists():
            print(f"ERROR: Epic directory not found: {epic_dir}")
            sys.exit(1)
        epic_dirs = [epic_dir]

    print("=" * 70)
    print("JIRA Sync - All-in-One")
    print("=" * 70)
    print(f"Epics:    {len(epic_dirs)} to process")
    print(f"Site:     {SITE}")
    print(f"Project:  {PROJECT_KEY}")
    print(f"Reset:    {args.reset}")
    print(f"Clean:    {args.clean_jira}")
    print(f"Resume:   {args.resume}")
    print(f"Dry Run:  {args.dry_run}")

    client = JiraClient()
    state = SyncState()  # Accumulates all mappings across epics
    all_data = []  # Store all epic data for cross-epic ref conversion

    # Phase 0: Reset (optional)
    if args.reset:
        print("\n" + "=" * 70)
        print("Phase 0: Resetting References")
        print("=" * 70)
        for epic_dir in epic_dirs:
            reset_count = reset_references(epic_dir)
            print(f"  {epic_dir.name}: Reset {reset_count} files")

    # Phase 0.5: Clean JIRA (optional)
    if args.clean_jira:
        print("\n" + "=" * 70)
        print("Phase 0.5: Cleaning JIRA")
        print("=" * 70)
        for epic_dir in epic_dirs:
            readme = epic_dir / "README.md"
            if readme.exists():
                content = readme.read_text()
                title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                if title_match:
                    deleted = clean_jira_issues(client, title_match.group(1))
                    print(f"  {epic_dir.name}: Deleted {deleted} issues")

    # Phase 1: Collect all data
    print("\n" + "=" * 70)
    print("Phase 1: Collecting Data")
    print("=" * 70)
    total_stories = 0
    total_tasks = 0
    for epic_dir in epic_dirs:
        data = collect_epic_data(epic_dir)
        all_data.append(data)
        total_stories += len(data['stories'])
        total_tasks += len(data['tasks'])
        print(f"  {epic_dir.name}: {len(data['stories'])} stories, {len(data['tasks'])} tasks")
    print(f"\n  Total: {len(epic_dirs)} epics, {total_stories} stories, {total_tasks} tasks")

    if args.validate_only or args.dry_run:
        print("\n[Validation/Dry Run - stopping here]")
        sys.exit(0)

    # Phase 2: Create JIRA issues for each epic
    print("\n" + "=" * 70)
    print("Phase 2: Creating JIRA Issues")
    print("=" * 70)
    for data in all_data:
        if data["epic"]:
            print(f"\n[{data['epic']['id']}]")
        create_jira_issues(client, data, state, resume=args.resume)

    # Phase 3: Create dependency links
    print("\n" + "=" * 70)
    print("Phase 3: Creating Dependency Links")
    print("=" * 70)
    total_links = 0
    for data in all_data:
        links = create_dependency_links(client, data, state)
        total_links += links
    print(f"  Created {total_links} links")

    # Phase 4: Convert ALL references to JIRA keys (stories, tasks, epics)
    print("\n" + "=" * 70)
    print("Phase 4: Converting ALL References to JIRA Keys")
    print("=" * 70)
    stories_fixed = 0
    tasks_fixed = 0
    epics_fixed = 0

    # Build complete epic map for cross-epic refs
    epic_map = build_epic_jira_map()
    print(f"  Epic mappings available: {len(epic_map)}")

    for data in all_data:
        s, t = convert_refs_to_jira_keys(data, state)
        stories_fixed += s
        tasks_fixed += t
        e = convert_epic_refs(data, epic_map)
        epics_fixed += e

    print(f"  Epics: {epics_fixed} updated")
    print(f"  Stories: {stories_fixed} updated")
    print(f"  Tasks: {tasks_fixed} updated")

    # Phase 5: Update JIRA with final content (all refs now JIRA keys)
    if not args.skip_update:
        print("\n" + "=" * 70)
        print("Phase 5: Updating JIRA Descriptions")
        print("=" * 70)
        updated = 0
        for data in all_data:
            updated += update_jira_descriptions(client, data, state)
        print(f"  Updated {updated} issues")

    # Phase 6: Validate - ensure ALL refs are JIRA keys
    print("\n" + "=" * 70)
    print("Phase 6: Validation (ALL refs must be JIRA keys)")
    print("=" * 70)
    all_issues = []
    for data in all_data:
        all_issues.extend(validate_sync(data, state))

    if all_issues:
        print("  ISSUES:")
        for issue in all_issues[:15]:
            print(f"    - {issue}")
        if len(all_issues) > 15:
            print(f"    ... and {len(all_issues) - 15} more")
    else:
        print("  All validations passed! All refs are JIRA keys.")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Epics:   {len(epic_dirs)}")
    print(f"  Created: {state.created_count}")
    print(f"  Skipped: {state.skipped_count}")
    print(f"  Errors:  {len(state.errors)}")
    if state.errors:
        for err in state.errors[:5]:
            print(f"    - {err}")


if __name__ == "__main__":
    main()
