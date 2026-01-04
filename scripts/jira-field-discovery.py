#!/usr/bin/env python3
"""
JIRA Field Discovery Script

Discovers custom field IDs for Epic Link, Story Points, Sprint, etc.
Saves to _bmad/config/jira-fields.yaml for use by jira-sync.

Usage:
    python scripts/jira-field-discovery.py

Requires: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, ATLASSIAN_SITE environment variables
"""

import os
import sys
import json
import yaml
import requests
from pathlib import Path

# Configuration
SITE = os.getenv("ATLASSIAN_SITE", "armor-defense.atlassian.net")
EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "ARGUS")

OUTPUT_FILE = Path("_bmad/config/jira-fields.yaml")

# Fields we need to discover
FIELDS_TO_FIND = [
    "Epic Link",
    "Parent Link",
    "Story Points",
    "Sprint",
    "Story point estimate",
    "Labels",
]


def get_auth():
    """Get authentication tuple."""
    if not EMAIL or not API_TOKEN:
        print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables")
        sys.exit(1)
    return (EMAIL, API_TOKEN)


def get_all_fields():
    """Fetch all fields from JIRA."""
    url = f"https://{SITE}/rest/api/3/field"
    response = requests.get(url, auth=get_auth())

    if response.status_code != 200:
        print(f"ERROR: Failed to fetch fields: {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()


def get_issue_types(project_key: str):
    """Get issue types for a project."""
    url = f"https://{SITE}/rest/api/3/project/{project_key}"
    response = requests.get(url, auth=get_auth())

    if response.status_code != 200:
        print(f"ERROR: Failed to fetch project: {response.status_code}")
        return []

    project = response.json()
    return project.get("issueTypes", [])


def get_link_types():
    """Get available issue link types."""
    url = f"https://{SITE}/rest/api/3/issueLinkType"
    response = requests.get(url, auth=get_auth())

    if response.status_code != 200:
        print(f"WARNING: Failed to fetch link types: {response.status_code}")
        return []

    return response.json().get("issueLinkTypes", [])


def discover_fields():
    """Discover and save field IDs."""
    print("=" * 60)
    print("JIRA Field Discovery")
    print("=" * 60)
    print(f"Site: {SITE}")
    print(f"Project: {PROJECT_KEY}")
    print()

    # Get all fields
    print("Fetching all fields...")
    all_fields = get_all_fields()
    print(f"Found {len(all_fields)} fields")
    print()

    # Find the fields we need
    discovered = {}
    for field in all_fields:
        name = field.get("name", "")
        field_id = field.get("id", "")

        # Check if this is a field we're looking for
        for target in FIELDS_TO_FIND:
            if target.lower() in name.lower():
                if target not in discovered:
                    discovered[target] = []
                discovered[target].append({
                    "id": field_id,
                    "name": name,
                    "custom": field.get("custom", False),
                    "schema": field.get("schema", {}).get("type", "unknown")
                })

    # Print discovered fields
    print("Discovered Fields:")
    print("-" * 60)
    for target, matches in discovered.items():
        print(f"\n{target}:")
        for match in matches:
            print(f"  - {match['id']}: {match['name']} (custom={match['custom']}, type={match['schema']})")

    # Get link types
    print("\n" + "-" * 60)
    print("Issue Link Types:")
    link_types = get_link_types()
    for lt in link_types:
        print(f"  - {lt['name']}: inward='{lt.get('inward')}', outward='{lt.get('outward')}'")

    # Build config
    config = {
        "site": SITE,
        "project_key": PROJECT_KEY,
        "custom_fields": {},
        "link_types": {}
    }

    # Select best match for each field
    field_priorities = {
        "Epic Link": ["customfield_10014", "customfield_10008", "parent"],
        "Story Points": ["customfield_10016", "customfield_10028", "customfield_10004"],
        "Sprint": ["customfield_10020", "customfield_10007"],
    }

    for target, matches in discovered.items():
        if matches:
            # Use first match (usually the right one)
            best = matches[0]
            key = target.lower().replace(" ", "_")
            config["custom_fields"][key] = {
                "id": best["id"],
                "name": best["name"]
            }

    # Add link types
    for lt in link_types:
        key = lt["name"].lower().replace(" ", "_")
        config["link_types"][key] = {
            "id": lt["id"],
            "name": lt["name"],
            "inward": lt.get("inward"),
            "outward": lt.get("outward")
        }

    # Save config
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"\nConfiguration saved to: {OUTPUT_FILE}")
    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Review the config file and verify field IDs are correct")
    print("2. Update jira-sync workflow to use these field IDs")
    print("3. Test creating an issue with Epic Link")

    return config


if __name__ == "__main__":
    discover_fields()
