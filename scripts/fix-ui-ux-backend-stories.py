#!/usr/bin/env python3
"""
Fix UI/UX Testing sections in backend epic stories.
Changes full UI/UX checklists to "N/A (backend story)" for non-frontend epics.
"""

import re
from pathlib import Path

# Backend epics that should NOT have UI/UX testing checklists
BACKEND_EPICS = [
    "EPIC-1-PLATFORM.md",
    "EPIC-2-GRAPH.md",
    "EPIC-3-RISK.md",
    "EPIC-4-AUTOMATION.md",
    "EPIC-6-INTEGRATION.md",
    "EPIC-9-POLICY-AI.md",
    "EPIC-AUTH-001-unified-scanner-auth.md",
]

# Pattern to match UI Testing checklist (multiline)
UI_TESTING_PATTERN = re.compile(
    r'\*\*UI Testing:\*\*\n'
    r'(- \[ \] UI-\d+:.*\n)+',
    re.MULTILINE
)

# Pattern to match UX Testing checklist (multiline)
UX_TESTING_PATTERN = re.compile(
    r'\*\*UX Testing:\*\*\n'
    r'(- \[ \] UX-\d+:.*\n)+',
    re.MULTILINE
)

def fix_file(filepath: Path) -> tuple[int, int]:
    """Fix UI/UX testing in a single file. Returns (ui_fixes, ux_fixes)."""
    content = filepath.read_text()
    original = content

    # Count and replace UI Testing checklists
    ui_matches = UI_TESTING_PATTERN.findall(content)
    ui_count = len(UI_TESTING_PATTERN.findall(content))
    content = UI_TESTING_PATTERN.sub('**UI Testing:** N/A (backend story)\n\n', content)

    # Count and replace UX Testing checklists
    ux_count = len(UX_TESTING_PATTERN.findall(content))
    content = UX_TESTING_PATTERN.sub('**UX Testing:** N/A (backend story)\n\n', content)

    if content != original:
        filepath.write_text(content)

    return ui_count, ux_count

def main():
    epics_dir = Path(".bmad/planning-artifacts/epics")

    total_ui = 0
    total_ux = 0

    print("Fixing UI/UX Testing sections in backend epics...")
    print("-" * 60)

    for epic_file in BACKEND_EPICS:
        filepath = epics_dir / epic_file
        if filepath.exists():
            ui_fixes, ux_fixes = fix_file(filepath)
            total_ui += ui_fixes
            total_ux += ux_fixes
            print(f"{epic_file}: {ui_fixes} UI fixes, {ux_fixes} UX fixes")
        else:
            print(f"{epic_file}: NOT FOUND")

    print("-" * 60)
    print(f"TOTAL: {total_ui} UI sections fixed, {total_ux} UX sections fixed")

if __name__ == "__main__":
    main()
