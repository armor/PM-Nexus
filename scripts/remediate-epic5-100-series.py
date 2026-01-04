#!/usr/bin/env python3
"""
Remediate EPIC-5 stories 100-123 with meaningful AC content and Technical Notes.
"""
import os
import re
from pathlib import Path

EPIC5_DIR = Path("/Users/phillipboles/Development/armor-argus/.bmad/epics/EPIC-5/stories")

# Map AC titles to meaningful GIVEN/WHEN/THEN content based on common UI patterns
AC_MAPPINGS = {
    # Input/Form patterns
    "text area": "**GIVEN** the policy creation form is displayed\n**WHEN** the user views the text area\n**THEN** a multi-line input field is visible with placeholder text guiding input format\n**AND** the text area supports at least 1000 characters",
    "character limit": "**GIVEN** the user is typing in the text area\n**WHEN** they approach the character limit\n**THEN** a character counter displays remaining characters\n**AND** input is blocked when the limit is reached with clear feedback",
    "placeholder": "**GIVEN** the input field is empty\n**WHEN** the component renders\n**THEN** placeholder text provides guidance on expected input\n**AND** the placeholder disappears when the user begins typing",
    "submit button": "**GIVEN** the form has valid input\n**WHEN** the user clicks the submit button\n**THEN** the form data is submitted to the backend API\n**AND** a loading indicator displays during submission\n**AND** success or error feedback is shown upon completion",
    "example suggestions": "**GIVEN** the user needs guidance on input format\n**WHEN** they view the input area\n**THEN** clickable example suggestions are displayed\n**AND** clicking an example populates the input field with that text",

    # Display patterns
    "logo": "**GIVEN** the component renders\n**WHEN** the page loads\n**THEN** the Argus logo is displayed with proper dimensions and alt text\n**AND** the logo maintains aspect ratio on different screen sizes",
    "welcome message": "**GIVEN** a new user accesses the application\n**WHEN** the welcome screen displays\n**THEN** a personalized welcome message is shown\n**AND** the message explains the platform's value proposition",
    "get started": "**GIVEN** the user views the welcome screen\n**WHEN** they click the Get Started button\n**THEN** the onboarding wizard begins\n**AND** progress is tracked for the user",
    "skip option": "**GIVEN** the user is viewing the onboarding flow\n**WHEN** they click Skip\n**THEN** they are taken directly to the main dashboard\n**AND** a flag is set to not show onboarding again",

    # Loading/Progress patterns
    "loading": "**GIVEN** an async operation is in progress\n**WHEN** data is being fetched or processed\n**THEN** a loading indicator is displayed\n**AND** the user cannot submit duplicate requests during loading",
    "progress bar": "**GIVEN** a multi-step process is running\n**WHEN** progress occurs\n**THEN** the progress bar updates to reflect completion percentage\n**AND** estimated time remaining is displayed when available",
    "generation": "**GIVEN** the user has submitted input for processing\n**WHEN** the backend generates output\n**THEN** real-time status updates are shown\n**AND** the user can cancel the operation if needed",

    # Display/View patterns
    "display": "**GIVEN** data is available to show\n**WHEN** the component renders\n**THEN** the data is displayed in a clear, formatted layout\n**AND** the display is responsive across screen sizes",
    "panel": "**GIVEN** the parent component renders\n**WHEN** the panel is visible\n**THEN** the panel displays relevant information in an organized layout\n**AND** the panel can be expanded or collapsed",
    "modal": "**GIVEN** the user triggers a modal action\n**WHEN** the modal opens\n**THEN** focus is trapped within the modal\n**AND** the modal can be closed via escape key or close button",
    "viewer": "**GIVEN** content is available for viewing\n**WHEN** the viewer renders\n**THEN** content is displayed with appropriate formatting\n**AND** the viewer supports scrolling for long content",

    # Action patterns
    "approval": "**GIVEN** an item requires approval\n**WHEN** the user reviews the item\n**THEN** Approve and Reject buttons are clearly visible\n**AND** clicking either triggers the appropriate workflow with confirmation",
    "button": "**GIVEN** the button is rendered\n**WHEN** the user clicks the button\n**THEN** the associated action is executed\n**AND** visual feedback indicates the button was clicked",

    # List/Queue patterns
    "list": "**GIVEN** items exist in the data source\n**WHEN** the list component renders\n**THEN** items are displayed in a sortable, filterable list\n**AND** pagination handles large datasets",
    "queue": "**GIVEN** items are pending in the queue\n**WHEN** the queue view renders\n**THEN** items are listed with status, priority, and timestamp\n**AND** the user can click items to view details",
    "detail": "**GIVEN** the user clicks an item\n**WHEN** the detail view opens\n**THEN** all relevant fields are displayed in an organized layout\n**AND** action buttons are available for next steps",

    # Setup/Wizard patterns
    "wizard": "**GIVEN** the user enters a multi-step workflow\n**WHEN** the wizard renders\n**THEN** step indicators show current position and total steps\n**AND** navigation allows moving forward and backward",
    "setup": "**GIVEN** configuration is required\n**WHEN** the setup component renders\n**THEN** required fields are clearly marked\n**AND** validation feedback is immediate",
    "profile": "**GIVEN** the user needs to select a configuration profile\n**WHEN** profiles are displayed\n**THEN** each profile shows name, description, and use case\n**AND** selection updates the preview immediately",
    "selection": "**GIVEN** multiple options are available\n**WHEN** the selection component renders\n**THEN** options are displayed with clear labels\n**AND** the current selection is highlighted",

    # Settings patterns
    "toggle": "**GIVEN** a feature can be enabled or disabled\n**WHEN** the user clicks the toggle\n**THEN** the state changes immediately with visual feedback\n**AND** the preference is persisted",
    "dark mode": "**GIVEN** the user prefers dark mode\n**WHEN** the toggle is activated\n**THEN** the entire application switches to dark theme\n**AND** the preference is saved to local storage",
    "keyboard shortcuts": "**GIVEN** keyboard shortcuts are configured\n**WHEN** the user presses a shortcut key combination\n**THEN** the associated action is triggered\n**AND** a shortcuts help dialog is accessible",

    # Accessibility patterns
    "accessibility": "**GIVEN** the application must meet WCAG 2.1 AA\n**WHEN** the component renders\n**THEN** proper ARIA labels and roles are applied\n**AND** focus management follows accessibility best practices",
    "audit": "**GIVEN** accessibility requirements exist\n**WHEN** an accessibility audit runs\n**THEN** zero critical violations are reported\n**AND** all interactive elements are keyboard accessible",

    # Integration patterns
    "trace": "**GIVEN** distributed tracing is enabled\n**WHEN** the user clicks a trace link\n**THEN** they are navigated to SigNoz with the trace ID pre-filled\n**AND** the trace context is preserved",
    "link": "**GIVEN** external navigation is required\n**WHEN** the user clicks the link\n**THEN** the destination opens in a new tab\n**AND** proper security attributes are applied",

    # Simulation/Preview patterns
    "simulation": "**GIVEN** a remediation is pending execution\n**WHEN** the simulation preview is requested\n**THEN** a dry-run output shows expected changes\n**AND** no actual changes are made to the environment",
    "preview": "**GIVEN** the user wants to see expected results\n**WHEN** the preview panel renders\n**THEN** a read-only view shows what will happen\n**AND** warnings highlight potential risks",

    # Rationale/Explanation patterns
    "rationale": "**GIVEN** AI-generated output requires explanation\n**WHEN** the rationale section renders\n**THEN** clear reasoning for the decision is displayed\n**AND** confidence scores are shown where applicable",
    "explanation": "**GIVEN** complex output needs clarification\n**WHEN** the user requests more detail\n**THEN** a detailed explanation modal opens\n**AND** technical terms include tooltips",

    # Evidence patterns
    "evidence": "**GIVEN** audit evidence is available\n**WHEN** the evidence viewer renders\n**THEN** before/after screenshots, logs, and diffs are displayed\n**AND** evidence can be exported for compliance",

    # First-run patterns
    "first scan": "**GIVEN** a new integration has been configured\n**WHEN** the first scan runs\n**THEN** progress is displayed in real-time\n**AND** estimated completion time is shown",
    "integration": "**GIVEN** the user is setting up an integration\n**WHEN** credentials are entered\n**THEN** connection validation occurs automatically\n**AND** success or failure is clearly indicated",
}

def get_ac_content(ac_title: str, story_title: str) -> str:
    """Generate meaningful AC content based on AC title patterns."""
    ac_lower = ac_title.lower()

    # Find best matching pattern
    for pattern, content in AC_MAPPINGS.items():
        if pattern in ac_lower:
            return content

    # Fallback: generate generic but meaningful content
    return f"**GIVEN** the user is on the {story_title.lower()} component\n**WHEN** the {ac_title.lower()} element is interacted with\n**THEN** the expected behavior is executed successfully\n**AND** appropriate user feedback is provided"

def remediate_story(story_path: Path):
    """Remediate a single story file."""
    with open(story_path, 'r') as f:
        content = f.read()

    # Skip if already has good ACs (no placeholder content)
    if "the specified action is performed" not in content:
        print(f"  Skipping {story_path.name} - already remediated")
        return False

    # Extract story title from header
    title_match = re.search(r'^# UX-\d+: (.+)$', content, re.MULTILINE)
    story_title = title_match.group(1) if title_match else "Unknown"

    # Find all AC sections and replace their content
    ac_pattern = r'(### AC\d+: ([^\n]+)\n\n)\*\*GIVEN\*\*.+?(?=\n---|\n### AC|\n## )'

    def replace_ac(match):
        ac_header = match.group(1)
        ac_title = match.group(2).strip()
        new_content = get_ac_content(ac_title, story_title)
        return f"{ac_header}{new_content}\n"

    new_content = re.sub(ac_pattern, replace_ac, content, flags=re.DOTALL)

    # Add Technical Notes section if missing
    if "## Technical Notes" not in new_content:
        # Determine appropriate key files based on story content
        story_num = re.search(r'UX-(\d+)', content).group(1)

        # Generate key files based on story title patterns
        key_files = []
        if any(x in story_title.lower() for x in ['dashboard', 'findings', 'risk', 'overview']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/dashboard/",
                "submodules/argus-ui/libs/ui-components/src/components/dashboard/"
            ]
        elif any(x in story_title.lower() for x in ['policy', 'cedar', 'approval']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/policies/",
                "submodules/argus-ui/libs/ui-components/src/components/policies/"
            ]
        elif any(x in story_title.lower() for x in ['remediation', 'queue', 'execution']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/remediation/",
                "submodules/argus-ui/libs/ui-components/src/components/remediation/"
            ]
        elif any(x in story_title.lower() for x in ['onboarding', 'welcome', 'setup', 'wizard']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/onboarding/",
                "submodules/argus-ui/libs/ui-components/src/components/onboarding/"
            ]
        elif any(x in story_title.lower() for x in ['settings', 'dark mode', 'keyboard', 'accessibility']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/settings/",
                "submodules/argus-ui/libs/ui-components/src/components/settings/"
            ]
        elif any(x in story_title.lower() for x in ['graph', 'attack path', 'visualization']):
            key_files = [
                "submodules/argus-ui/apps/argus-ui/src/app/graph/",
                "submodules/argus-ui/libs/ui-components/src/components/graph/"
            ]
        else:
            key_files = [
                f"submodules/argus-ui/apps/argus-ui/src/app/{story_title.lower().replace(' ', '-')}/",
                f"submodules/argus-ui/libs/ui-components/src/components/{story_title.lower().replace(' ', '-')}/"
            ]

        # Extract depends on and blocks
        depends_match = re.search(r'\| Depends On \| ([^\|]+) \|', new_content)
        blocks_match = re.search(r'\| Blocks \| ([^\|]+) \|', new_content)
        depends_on = depends_match.group(1).strip() if depends_match else "-"
        blocks = blocks_match.group(1).strip() if blocks_match else "-"

        tech_notes = f"""
## Technical Notes

### Key Files
- `{key_files[0]}` - Main component directory
- `{key_files[1]}` - Shared UI components

### Dependencies
- Depends on: {depends_on}
- Blocks: {blocks}

---

"""
        # Insert before References section
        new_content = re.sub(
            r'\n## References\n',
            f'{tech_notes}## References\n',
            new_content
        )

    with open(story_path, 'w') as f:
        f.write(new_content)

    print(f"  Remediated {story_path.name}")
    return True

def main():
    print("Remediating EPIC-5 stories 100-123...")

    # Find all stories that need remediation
    story_files = sorted(EPIC5_DIR.glob("1*/story-*.md"))

    remediated = 0
    for story_file in story_files:
        if remediate_story(story_file):
            remediated += 1

    print(f"\nRemediated {remediated} stories")

if __name__ == "__main__":
    main()
