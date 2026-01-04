#!/usr/bin/env python3
"""
Remediate all 84 stories in EPIC-5-UX to match the required template format.

Applies the following remediation pattern:
1. User Story Format: "As a **frontend developer**, I want **{action}**, so that **{benefit}**."
2. Business Value Section with Value Statement, Success Metric, User Research
3. Acceptance Criteria in GIVEN/WHEN/THEN format with ### AC# headings
4. Tasks Section with 4 tasks, proper table, and Task Execution Order
5. Testing Requirements with 4-path testing table
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

EPIC5_STORIES_DIR = Path("/Users/phillipboles/Development/armor-argus/.bmad/epics/EPIC-5/stories")

# Story context mapping for better user stories and business value
STORY_CONTEXT = {
    "01-tailwind-css-configuration": {
        "action": "configure Tailwind CSS with custom brand tokens",
        "benefit": "I have a consistent, maintainable styling foundation for all UI components",
        "value": "Enables rapid, consistent UI development with design system tokens",
        "metric": "100% of UI components using shared Tailwind tokens",
        "research": "Developers need a scalable CSS architecture that enforces design consistency"
    },
    "02-typography-system": {
        "action": "implement a typography system with semantic scale",
        "benefit": "text hierarchy is consistent and accessible across all pages",
        "value": "Ensures readable, accessible text hierarchy following WCAG guidelines",
        "metric": "Typography passes WCAG 2.1 AA contrast requirements",
        "research": "Users require clear visual hierarchy to scan and comprehend content quickly"
    },
    "03-color-palette-tokens": {
        "action": "define semantic color tokens for the design system",
        "benefit": "colors are consistent, accessible, and support dark mode",
        "value": "Establishes accessible color palette with semantic naming",
        "metric": "All color combinations pass WCAG 2.1 AA contrast ratio",
        "research": "Security dashboards need clear color semantics for severity and status"
    },
    "04-icon-library-setup": {
        "action": "configure an icon library with security-focused icons",
        "benefit": "icons are consistent, accessible, and performant",
        "value": "Provides consistent iconography for security concepts and actions",
        "metric": "Icon load time under 100ms with tree-shaking",
        "research": "Users rely on icons for quick recognition of security states and actions"
    },
    "05-sidebar-navigation-component": {
        "action": "build a collapsible sidebar navigation component",
        "benefit": "users can navigate the application efficiently",
        "value": "Enables intuitive navigation across all security modules",
        "metric": "Navigation to any section in under 2 clicks",
        "research": "Security analysts need quick access to different views during incident response"
    },
    "06-top-header-component": {
        "action": "create a top header with user menu and notifications",
        "benefit": "users have access to account settings and alerts",
        "value": "Provides persistent access to user context and system notifications",
        "metric": "Alert notification visible within 2 seconds of trigger",
        "research": "Users need immediate visibility of critical security alerts"
    },
    "07-main-content-layout": {
        "action": "implement the main content area layout with responsive grid",
        "benefit": "content displays correctly across all screen sizes",
        "value": "Ensures responsive, accessible main content presentation",
        "metric": "Layout functions correctly from 320px to 4K screens",
        "research": "Security teams use various screen sizes from mobile to SOC displays"
    },
    "08-login-page": {
        "action": "create a secure login page with SSO support",
        "benefit": "users can authenticate securely with their identity provider",
        "value": "Provides secure, enterprise-grade authentication experience",
        "metric": "Login flow completes in under 5 seconds",
        "research": "Enterprise users require SSO integration and MFA support"
    },
    "09-jwt-token-handler": {
        "action": "implement JWT token handling with refresh logic",
        "benefit": "user sessions are secure and seamless",
        "value": "Ensures secure token management with automatic refresh",
        "metric": "Zero token expiry interruptions for active users",
        "research": "Security platforms require robust token handling to prevent session hijacking"
    },
    "10-auth-context-provider": {
        "action": "create an auth context provider for React",
        "benefit": "authentication state is accessible throughout the application",
        "value": "Provides centralized authentication state management",
        "metric": "Auth state updates propagate in under 100ms",
        "research": "Developers need consistent access to user permissions and auth state"
    },
    "11-route-configuration": {
        "action": "configure protected and public routes",
        "benefit": "navigation is secure and role-based",
        "value": "Implements secure routing with role-based access control",
        "metric": "100% of protected routes verified against permissions",
        "research": "Different user roles require different access levels to security data"
    },
    "12-breadcrumb-component": {
        "action": "build a breadcrumb navigation component",
        "benefit": "users always know their location in the application",
        "value": "Provides clear navigation context and quick backtracking",
        "metric": "Users can navigate back to any parent in 1 click",
        "research": "Deep navigation hierarchies require clear location indicators"
    },
    "13-mobile-navigation-menu": {
        "action": "create a mobile-friendly navigation menu",
        "benefit": "the application is usable on mobile devices",
        "value": "Enables mobile access for on-the-go security monitoring",
        "metric": "All navigation accessible on screens 320px and above",
        "research": "Security teams need mobile access for off-hours incident response"
    },
    "14-api-client-configuration": {
        "action": "configure the API client with interceptors and error handling",
        "benefit": "API calls are consistent, authenticated, and handle errors gracefully",
        "value": "Provides reliable, consistent API communication layer",
        "metric": "API error handling covers 100% of error scenarios",
        "research": "Developers need a robust API client that handles auth and errors automatically"
    },
    "15-react-query-setup": {
        "action": "configure React Query for data fetching and caching",
        "benefit": "data fetching is efficient with proper caching and refetching",
        "value": "Enables efficient data management with optimistic updates",
        "metric": "Data cache reduces redundant API calls by 80%",
        "research": "Real-time security data requires smart caching and background refresh"
    },
    "16-top-risks-page-layout": {
        "action": "create the Top Risks dashboard page layout",
        "benefit": "users can view prioritized risks at a glance",
        "value": "Provides immediate visibility into highest-priority security risks",
        "metric": "Top 10 risks visible above the fold on standard screens",
        "research": "Security teams need quick access to the most critical risks first"
    },
    "17-top-risks-api-hook": {
        "action": "implement the API hook for fetching top risks",
        "benefit": "risk data is fetched efficiently with proper loading states",
        "value": "Enables real-time risk data with proper loading feedback",
        "metric": "Risk data loads in under 2 seconds on average connection",
        "research": "Users need responsive data loading with clear feedback"
    },
    "18-risk-card-component": {
        "action": "build a risk card component displaying severity and details",
        "benefit": "users can quickly understand risk severity and take action",
        "value": "Provides clear, actionable risk information at a glance",
        "metric": "Users identify risk severity in under 1 second",
        "research": "Risk prioritization requires clear visual severity indicators"
    },
    "19-risk-card-why-this-matters-preview": {
        "action": "add a 'Why This Matters' preview to risk cards",
        "benefit": "users understand the business impact of each risk",
        "value": "Communicates business context for prioritization decisions",
        "metric": "80% of users understand risk impact without expanding details",
        "research": "Non-technical stakeholders need plain-language risk explanations"
    },
    "20-risk-card-action-buttons": {
        "action": "implement action buttons on risk cards",
        "benefit": "users can take immediate action on risks",
        "value": "Enables one-click remediation initiation from risk view",
        "metric": "Remediation initiated in under 3 clicks from risk card",
        "research": "Security analysts need quick action paths to reduce MTTR"
    },
    "21-risk-cards-grid": {
        "action": "create a responsive grid layout for risk cards",
        "benefit": "risk cards display optimally across screen sizes",
        "value": "Maximizes risk visibility across all device types",
        "metric": "Grid adjusts from 1-4 columns based on screen width",
        "research": "SOC environments use various screen configurations"
    },
    "22-loading-skeleton-for-risks": {
        "action": "implement loading skeletons for the risks view",
        "benefit": "users see placeholder content during data loading",
        "value": "Provides perceived performance improvement during data fetch",
        "metric": "Skeleton appears within 100ms of navigation",
        "research": "Users perceive loading as faster with skeleton UI patterns"
    },
    "23-empty-state-for-risks": {
        "action": "create an empty state for when no risks are found",
        "benefit": "users receive helpful guidance when risk data is empty",
        "value": "Guides users when no risks match filters or data is unavailable",
        "metric": "Empty state provides clear next action for users",
        "research": "Users need guidance when expected data is not present"
    },
    "24-environment-filter": {
        "action": "build an environment filter dropdown",
        "benefit": "users can filter risks by cloud environment",
        "value": "Enables focused risk analysis by environment context",
        "metric": "Filter applies in under 500ms",
        "research": "Multi-cloud users need to segment risks by environment"
    },
    "25-timeframe-filter": {
        "action": "implement a timeframe filter for risk data",
        "benefit": "users can analyze risks over different time periods",
        "value": "Enables trend analysis and time-based risk assessment",
        "metric": "Timeframe change reflects in data within 1 second",
        "research": "Security teams need to track risk trends over time"
    },
    "26-severity-filter-chips": {
        "action": "create severity filter chips for quick filtering",
        "benefit": "users can quickly filter by risk severity level",
        "value": "Enables rapid severity-based risk prioritization",
        "metric": "Severity filter toggles in under 200ms",
        "research": "Critical/High severity filtering is a common workflow"
    },
    "27-why-this-matters-expanded-panel": {
        "action": "build an expanded panel for detailed risk explanation",
        "benefit": "users can read full risk context and business impact",
        "value": "Provides comprehensive risk context for decision making",
        "metric": "Panel loads full content in under 300ms",
        "research": "Stakeholders need detailed explanations for risk decisions"
    },
    "28-summary-statistics-header": {
        "action": "create a summary statistics header for the dashboard",
        "benefit": "users see key metrics at the top of the risks view",
        "value": "Provides instant visibility into overall risk posture",
        "metric": "Key metrics visible without scrolling",
        "research": "Executives need quick security posture overview"
    },
    "29-risk-detail-layout": {
        "action": "design the risk detail page layout",
        "benefit": "users can explore comprehensive risk information",
        "value": "Enables deep-dive analysis of individual risks",
        "metric": "All risk details accessible within the page",
        "research": "Analysts need comprehensive risk context for remediation"
    },
    "30-risk-detail-api-hook": {
        "action": "implement the API hook for risk detail data",
        "benefit": "risk detail data loads efficiently with caching",
        "value": "Provides fast access to detailed risk information",
        "metric": "Risk detail loads in under 1 second",
        "research": "Users expect instant data when drilling into risks"
    },
    "31-score-breakdown-chart": {
        "action": "build a chart showing risk score breakdown",
        "benefit": "users understand what factors contribute to the score",
        "value": "Explains risk scoring methodology visually",
        "metric": "All score factors visible in chart",
        "research": "Users need transparency in how risks are scored"
    },
    "32-factor-tooltips": {
        "action": "add tooltips explaining each risk factor",
        "benefit": "users can learn about risk factors without leaving the page",
        "value": "Provides inline education on risk factors",
        "metric": "Tooltips appear within 200ms of hover",
        "research": "New users need contextual help understanding factors"
    },
    "33-contributing-findings-tab": {
        "action": "create a tab showing contributing findings",
        "benefit": "users can see which findings contribute to the risk",
        "value": "Links risks to underlying security findings",
        "metric": "All contributing findings visible and clickable",
        "research": "Analysts need to trace risks back to raw findings"
    },
    "34-risk-explanation-drawer": {
        "action": "build a drawer with AI-generated risk explanation",
        "benefit": "users get contextual explanation of the risk",
        "value": "Provides AI-powered risk context and recommendations",
        "metric": "AI explanation loads in under 2 seconds",
        "research": "Users benefit from AI-generated risk summaries"
    },
    "35-graph-library-setup": {
        "action": "configure a graph visualization library",
        "benefit": "attack path visualizations are possible",
        "value": "Enables interactive attack path graph rendering",
        "metric": "Graph renders 100 nodes in under 1 second",
        "research": "Attack paths require interactive graph visualization"
    },
    "36-node-rendering": {
        "action": "implement node rendering for graph visualization",
        "benefit": "assets are displayed as interactive nodes",
        "value": "Displays assets as interactive, informative graph nodes",
        "metric": "Node type identifiable within 1 second",
        "research": "Different asset types need distinct visual representations"
    },
    "37-edge-rendering": {
        "action": "implement edge rendering for graph connections",
        "benefit": "relationships between assets are visualized",
        "value": "Visualizes attack path connections between assets",
        "metric": "Edge direction and type clearly visible",
        "research": "Attack paths require clear relationship visualization"
    },
    "38-hierarchical-layout": {
        "action": "implement hierarchical layout for attack paths",
        "benefit": "attack paths display in a logical flow",
        "value": "Presents attack paths in intuitive directional flow",
        "metric": "Attack direction flows top-to-bottom or left-to-right",
        "research": "Users expect attack paths to flow in logical direction"
    },
    "39-pan-and-zoom": {
        "action": "add pan and zoom controls to the graph",
        "benefit": "users can navigate large attack path graphs",
        "value": "Enables navigation of complex attack path graphs",
        "metric": "Smooth 60fps pan and zoom interactions",
        "research": "Large graphs require pan/zoom for exploration"
    },
    "40-node-detail-popover": {
        "action": "create a popover showing node details",
        "benefit": "users can see asset details without leaving the graph",
        "value": "Provides asset context without disrupting graph view",
        "metric": "Popover appears within 200ms of hover/click",
        "research": "Users need quick access to node details"
    },
    "41-edge-labels": {
        "action": "add labels to graph edges showing relationship type",
        "benefit": "users understand the nature of connections",
        "value": "Clarifies relationship types in attack paths",
        "metric": "Edge labels readable without zoom",
        "research": "Relationship types are critical for understanding attacks"
    },
    "42-path-highlighting": {
        "action": "implement path highlighting on selection",
        "benefit": "users can trace specific attack paths",
        "value": "Enables focused analysis of specific attack vectors",
        "metric": "Selected path highlighted within 100ms",
        "research": "Analysts need to isolate individual attack paths"
    },
    "43-graph-controls-panel": {
        "action": "build a controls panel for graph settings",
        "benefit": "users can customize the graph visualization",
        "value": "Provides user control over graph display options",
        "metric": "All graph controls accessible from panel",
        "research": "Power users need customization options"
    },
    "44-findings-page-layout": {
        "action": "create the findings list page layout",
        "benefit": "users can browse all security findings",
        "value": "Provides comprehensive view of all security findings",
        "metric": "Initial findings load in under 2 seconds",
        "research": "Users need to browse and search all findings"
    },
    "45-findings-data-table": {
        "action": "build a data table for findings with sorting",
        "benefit": "users can sort and organize findings efficiently",
        "value": "Enables efficient findings analysis with sorting",
        "metric": "Sort operation completes in under 300ms",
        "research": "Large finding sets require sortable tables"
    },
    "46-findings-pagination": {
        "action": "implement pagination for the findings table",
        "benefit": "users can navigate through large finding sets",
        "value": "Enables navigation of large finding datasets",
        "metric": "Page change loads in under 500ms",
        "research": "Thousands of findings require pagination"
    },
    "47-findings-severity-filter": {
        "action": "add severity filtering to findings",
        "benefit": "users can focus on findings by severity level",
        "value": "Enables severity-based findings prioritization",
        "metric": "Filter applies within 300ms",
        "research": "Severity filtering is primary findings workflow"
    },
    "48-findings-status-filter": {
        "action": "add status filtering to findings",
        "benefit": "users can filter by open, resolved, or suppressed status",
        "value": "Enables status-based findings workflow",
        "metric": "Filter applies within 300ms",
        "research": "Users need to focus on actionable findings"
    },
    "49-findings-search": {
        "action": "implement search functionality for findings",
        "benefit": "users can find specific findings quickly",
        "value": "Enables rapid finding discovery via search",
        "metric": "Search results appear within 500ms",
        "research": "Users often know what they're looking for"
    },
    "50-finding-detail-page": {
        "action": "create the finding detail page",
        "benefit": "users can view comprehensive finding information",
        "value": "Provides complete finding context for remediation",
        "metric": "All finding details load in under 1 second",
        "research": "Analysts need full finding context"
    },
    "51-finding-status-update": {
        "action": "implement status update functionality for findings",
        "benefit": "users can mark findings as resolved or suppressed",
        "value": "Enables findings workflow management",
        "metric": "Status update confirms in under 1 second",
        "research": "Workflow requires status management"
    },
    "52-bulk-select-findings": {
        "action": "add bulk selection to the findings table",
        "benefit": "users can select multiple findings for batch actions",
        "value": "Enables efficient bulk findings management",
        "metric": "Select all works with 1000+ findings",
        "research": "Large finding sets require bulk operations"
    },
    "53-bulk-status-update": {
        "action": "implement bulk status update for findings",
        "benefit": "users can update multiple findings at once",
        "value": "Enables rapid bulk findings remediation",
        "metric": "Bulk update 100 findings in under 5 seconds",
        "research": "Efficient triage requires bulk operations"
    },
    "54-assets-list-page": {
        "action": "create the assets inventory list page",
        "benefit": "users can browse all discovered cloud assets",
        "value": "Provides comprehensive asset visibility",
        "metric": "Assets load with pagination in under 2 seconds",
        "research": "Asset inventory is foundational to security"
    },
    "55-asset-detail-page": {
        "action": "build the asset detail page",
        "benefit": "users can view comprehensive asset information",
        "value": "Provides complete asset context and related findings",
        "metric": "Asset details load in under 1 second",
        "research": "Asset context is critical for risk assessment"
    },
    "56-playwright-e2e-setup": {
        "action": "configure Playwright for end-to-end testing",
        "benefit": "I can run automated E2E tests for critical flows",
        "value": "Establishes E2E testing infrastructure",
        "metric": "E2E test suite runs in under 5 minutes",
        "research": "Automated testing prevents regressions"
    },
    "57-test-fixtures": {
        "action": "create test fixtures for E2E tests",
        "benefit": "tests have consistent, reliable test data",
        "value": "Provides reliable test data for E2E scenarios",
        "metric": "Fixtures cover all major data types",
        "research": "Consistent test data ensures reliable tests"
    },
    "58-top-risks-e2e-tests": {
        "action": "write E2E tests for the Top Risks page",
        "benefit": "the Top Risks page functionality is verified automatically",
        "value": "Ensures Top Risks page functions correctly",
        "metric": "100% of critical paths covered",
        "research": "Core workflows require automated verification"
    },
    "59-findings-e2e-tests": {
        "action": "write E2E tests for the Findings page",
        "benefit": "the Findings page functionality is verified automatically",
        "value": "Ensures Findings page functions correctly",
        "metric": "100% of critical paths covered",
        "research": "Core workflows require automated verification"
    },
    "60-attack-path-e2e-tests": {
        "action": "write E2E tests for the Attack Path visualization",
        "benefit": "the Attack Path visualization is verified automatically",
        "value": "Ensures Attack Path visualization functions correctly",
        "metric": "Graph interactions verified end-to-end",
        "research": "Complex visualizations require E2E testing"
    },
    "100-policy-intent-input": {
        "action": "create a natural language input for policy creation",
        "benefit": "users can describe policies in plain language",
        "value": "Enables natural language policy authoring",
        "metric": "Users can submit policy intent in under 30 seconds",
        "research": "Non-experts need simplified policy creation"
    },
    "101-policy-generation-loading": {
        "action": "implement loading state for AI policy generation",
        "benefit": "users see feedback during policy generation",
        "value": "Provides feedback during AI processing",
        "metric": "Loading indicator appears within 100ms",
        "research": "AI operations require clear progress feedback"
    },
    "102-generated-policy-display": {
        "action": "create a display component for generated policies",
        "benefit": "users can review AI-generated policy code",
        "value": "Presents generated policies for user review",
        "metric": "Policy code displayed with syntax highlighting",
        "research": "Users must review policies before approval"
    },
    "103-ai-rationale-display": {
        "action": "build a component showing AI decision rationale",
        "benefit": "users understand why the AI made certain decisions",
        "value": "Explains AI reasoning for transparency",
        "metric": "Rationale visible alongside policy",
        "research": "AI transparency builds user trust"
    },
    "104-simulation-preview": {
        "action": "create a simulation preview showing policy impact",
        "benefit": "users can see what the policy will affect before applying",
        "value": "Enables safe policy preview before execution",
        "metric": "Simulation results load in under 5 seconds",
        "research": "Users need to preview changes before applying"
    },
    "105-policy-approval-buttons": {
        "action": "implement approve/reject buttons for policies",
        "benefit": "users can approve or reject AI-generated policies",
        "value": "Provides human-in-the-loop policy approval",
        "metric": "Approval action completes in under 1 second",
        "research": "Human approval required for policy changes"
    },
    "106-policy-explanation-modal": {
        "action": "build a modal explaining policy details",
        "benefit": "users can understand complex policies in detail",
        "value": "Provides detailed policy explanations",
        "metric": "Modal loads policy details in under 500ms",
        "research": "Complex policies need detailed explanations"
    },
    "107-remediation-queue-list": {
        "action": "create a list showing pending remediations",
        "benefit": "users can see all remediations awaiting approval",
        "value": "Provides visibility into remediation pipeline",
        "metric": "Queue updates in real-time",
        "research": "Users need to manage remediation workflow"
    },
    "108-remediation-detail-page": {
        "action": "build the remediation detail page",
        "benefit": "users can review comprehensive remediation information",
        "value": "Provides complete remediation context",
        "metric": "All remediation details load in under 1 second",
        "research": "Detailed review required before execution"
    },
    "109-simulation-preview-panel": {
        "action": "create a panel showing remediation simulation results",
        "benefit": "users can preview what changes will be made",
        "value": "Enables safe remediation preview",
        "metric": "Simulation diff displayed clearly",
        "research": "Users must verify changes before execution"
    },
    "110-execution-progress-bar": {
        "action": "implement a progress bar for remediation execution",
        "benefit": "users can track remediation progress",
        "value": "Provides real-time execution feedback",
        "metric": "Progress updates every 2 seconds",
        "research": "Long operations need progress feedback"
    },
    "111-evidence-viewer": {
        "action": "build a viewer for remediation evidence artifacts",
        "benefit": "users can review proof of remediation completion",
        "value": "Provides audit evidence for compliance",
        "metric": "Evidence artifacts viewable inline",
        "research": "Compliance requires execution evidence"
    },
    "112-welcome-screen": {
        "action": "create a welcome screen for new users",
        "benefit": "new users are guided through initial setup",
        "value": "Provides guided onboarding experience",
        "metric": "Users complete onboarding in under 5 minutes",
        "research": "New users need guided setup experience"
    },
    "113-integration-setup-wizard": {
        "action": "build a wizard for cloud integration setup",
        "benefit": "users can connect their cloud accounts easily",
        "value": "Enables self-service cloud integration",
        "metric": "Integration completes in under 10 minutes",
        "research": "Users need guided integration setup"
    },
    "114-setup-profile-selection": {
        "action": "create a profile selection for security baseline",
        "benefit": "users can choose their security scanning profile",
        "value": "Enables customized security scanning",
        "metric": "Profile selection takes under 1 minute",
        "research": "Different users need different security profiles"
    },
    "115-first-scan-progress": {
        "action": "implement progress tracking for initial scan",
        "benefit": "users can track their first security scan progress",
        "value": "Provides feedback during initial scanning",
        "metric": "Progress visible with time estimate",
        "research": "First scan can take time and needs feedback"
    },
    "116-dark-mode-toggle": {
        "action": "add a dark mode toggle to the interface",
        "benefit": "users can switch between light and dark themes",
        "value": "Provides theme preference for user comfort",
        "metric": "Theme switch instant with no flash",
        "research": "SOC environments often prefer dark mode"
    },
    "117-keyboard-shortcuts": {
        "action": "implement keyboard shortcuts for common actions",
        "benefit": "power users can navigate faster with keyboard",
        "value": "Enables keyboard-driven power user workflows",
        "metric": "All major actions have keyboard shortcuts",
        "research": "Power users prefer keyboard navigation"
    },
    "118-accessibility-audit": {
        "action": "conduct and remediate accessibility issues",
        "benefit": "the application is accessible to users with disabilities",
        "value": "Ensures WCAG 2.1 AA compliance",
        "metric": "Zero critical accessibility violations",
        "research": "Accessibility is required for enterprise deployment"
    },
    "119-signoz-trace-links": {
        "action": "add links to SigNoz traces from the UI",
        "benefit": "users can drill down to trace details for debugging",
        "value": "Enables trace-based debugging from UI",
        "metric": "Trace links open correct SigNoz view",
        "research": "Developers need trace correlation for debugging"
    },
    "120-mobile-responsive": {
        "action": "ensure full mobile responsiveness",
        "benefit": "the application works on mobile devices",
        "value": "Enables mobile access for on-call response",
        "metric": "All pages functional on 375px screens",
        "research": "On-call staff need mobile access"
    },
    "121-performance-optimization": {
        "action": "optimize bundle size and load performance",
        "benefit": "the application loads quickly",
        "value": "Ensures fast load times for user productivity",
        "metric": "Initial load under 3 seconds on 3G",
        "research": "Slow load times reduce user adoption"
    },
    "122-policy-workflow-e2e-tests": {
        "action": "write E2E tests for the policy workflow",
        "benefit": "the policy creation workflow is verified automatically",
        "value": "Ensures policy workflow functions correctly",
        "metric": "100% of policy workflow paths covered",
        "research": "Critical workflows require automated testing"
    },
    "123-remediation-e2e-tests": {
        "action": "write E2E tests for the remediation workflow",
        "benefit": "the remediation workflow is verified automatically",
        "value": "Ensures remediation workflow functions correctly",
        "metric": "100% of remediation workflow paths covered",
        "research": "Critical workflows require automated testing"
    },
}


def get_story_dirs() -> List[Path]:
    """Get all story directories sorted."""
    dirs = [d for d in EPIC5_STORIES_DIR.iterdir() if d.is_dir()]
    return sorted(dirs, key=lambda x: (int(x.name.split('-')[0]), x.name))


def get_story_file(story_dir: Path) -> Path:
    """Get the story markdown file from a story directory."""
    story_name = story_dir.name
    story_file = story_dir / f"story-{story_name}.md"
    return story_file


def parse_story(content: str) -> Dict:
    """Parse existing story content into structured data."""
    data = {
        "title": "",
        "story_id": "",
        "epic": "",
        "points": "",
        "priority": "",
        "sprint": "",
        "status": "",
        "coordination": {},
        "story_text": "",
        "business_value": "",
        "acceptance_criteria": [],
        "references": []
    }

    # Extract header info
    header_match = re.search(r'^# (\w+-\d+): (.+)$', content, re.MULTILINE)
    if header_match:
        data["story_id"] = header_match.group(1)
        data["title"] = header_match.group(2)

    # Extract metadata line
    meta_match = re.search(r'\*\*Epic:\*\* ([\w-]+) \| \*\*Points:\*\* (\d+) \| \*\*Priority:\*\* (\w+) \| \*\*Sprint:\*\* (\d+)', content)
    if meta_match:
        data["epic"] = meta_match.group(1)
        data["points"] = meta_match.group(2)
        data["priority"] = meta_match.group(3)
        data["sprint"] = meta_match.group(4)

    # Extract status
    status_match = re.search(r'\*\*Status:\*\* ([\w-]+)', content)
    if status_match:
        data["status"] = status_match.group(1)

    # Extract coordination table
    coord_section = re.search(r'## Coordination\n\n\|[^\n]+\n\|[-|]+\n((?:\|[^\n]+\n)+)', content)
    if coord_section:
        for line in coord_section.group(1).strip().split('\n'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2:
                data["coordination"][parts[0]] = parts[1]

    # Extract story text
    story_match = re.search(r'## Story\n\n(.+?)(?=\n---|\n##)', content, re.DOTALL)
    if story_match:
        data["story_text"] = story_match.group(1).strip()

    # Extract acceptance criteria
    ac_section = re.search(r'## Acceptance Criteria\n\n((?:- \[[ x]\] [^\n]+\n?)+)', content)
    if ac_section:
        for line in ac_section.group(1).strip().split('\n'):
            match = re.match(r'- \[[ x]\] (\w+-\d+): (.+)', line)
            if match:
                data["acceptance_criteria"].append({
                    "id": match.group(1),
                    "text": match.group(2)
                })

    return data


def generate_ac_given_when_then(ac_text: str, story_context: str) -> Dict[str, str]:
    """Generate GIVEN/WHEN/THEN format for an acceptance criterion."""
    # Generic patterns based on common AC types
    text_lower = ac_text.lower()

    if "installed" in text_lower or "configured" in text_lower or "setup" in text_lower:
        return {
            "given": "the development environment is ready",
            "when": f"I {ac_text.lower()}",
            "then": "the configuration is applied successfully",
            "and": "no errors are reported in the console"
        }
    elif "click" in text_lower or "button" in text_lower:
        return {
            "given": "the user is viewing the component",
            "when": f"the user interacts with {ac_text.lower()}",
            "then": "the expected action is triggered",
            "and": "feedback is provided to the user"
        }
    elif "display" in text_lower or "show" in text_lower or "visible" in text_lower:
        return {
            "given": "the component is rendered",
            "when": "the data is loaded",
            "then": f"{ac_text}",
            "and": "the display is responsive and accessible"
        }
    elif "filter" in text_lower:
        return {
            "given": "data is displayed in the component",
            "when": "the user applies the filter",
            "then": f"{ac_text}",
            "and": "the filter state is persisted"
        }
    elif "api" in text_lower or "hook" in text_lower or "fetch" in text_lower:
        return {
            "given": "the component is mounted",
            "when": "data is requested from the API",
            "then": f"{ac_text}",
            "and": "loading and error states are handled"
        }
    elif "test" in text_lower or "e2e" in text_lower:
        return {
            "given": "the test environment is configured",
            "when": "the tests are executed",
            "then": f"{ac_text}",
            "and": "test results are reported accurately"
        }
    else:
        return {
            "given": "the user is in the appropriate context",
            "when": "the specified action is performed",
            "then": f"{ac_text}",
            "and": "the system state is updated correctly"
        }


def generate_remediated_story(story_dir: Path, parsed_data: Dict) -> str:
    """Generate the remediated story content."""
    story_name = story_dir.name
    story_key = story_name

    # Get context for this story
    context = STORY_CONTEXT.get(story_key, {
        "action": parsed_data["story_text"].lower() if parsed_data["story_text"] else "implement the required functionality",
        "benefit": "the feature works as expected",
        "value": f"This story enables: {parsed_data['story_text']}" if parsed_data["story_text"] else "Delivers required functionality",
        "metric": "Feature works as specified",
        "research": "Users require this functionality"
    })

    # Build the remediated content
    content = []

    # Header
    content.append(f"# {parsed_data['story_id']}: {parsed_data['title']}")
    content.append("")
    content.append(f"**Epic:** {parsed_data['epic']} | **Points:** {parsed_data['points']} | **Priority:** {parsed_data['priority']} | **Sprint:** {parsed_data['sprint']}")
    content.append(f"**Status:** {parsed_data['status']}")
    content.append("")
    content.append("---")
    content.append("")

    # Coordination section
    content.append("## Coordination")
    content.append("")
    content.append("| Field | Value |")
    content.append("|-------|-------|")
    content.append(f"| Worktree | `{parsed_data['coordination'].get('Worktree', f'worktrees/argus-ui-{story_name}')}` |")
    content.append(f"| Branch | `{parsed_data['coordination'].get('Branch', story_name)}` |")
    content.append(f"| Depends On | {parsed_data['coordination'].get('Depends On', '-')} |")
    content.append(f"| Blocks | {parsed_data['coordination'].get('Blocks', '-')} |")
    content.append(f"| JIRA Key | {parsed_data['coordination'].get('JIRA Key', '')} |")
    content.append("")
    content.append("### Task Execution Order")
    content.append("")
    content.append("```")
    content.append("T1 -> T2 -> T3 -> T4")
    content.append("```")
    content.append("")
    content.append("---")
    content.append("")

    # User Story section
    content.append("## Story")
    content.append("")
    content.append(f"As a **frontend developer**, I want **{context['action']}**, so that **{context['benefit']}**.")
    content.append("")
    content.append("---")
    content.append("")

    # Business Value section
    content.append("## Business Value")
    content.append("")
    content.append(f"**Value Statement:** {context['value']}")
    content.append(f"**Success Metric:** {context['metric']}")
    content.append(f"**User Research:** {context['research']}")
    content.append("")
    content.append("---")
    content.append("")

    # Acceptance Criteria section
    content.append("## Acceptance Criteria")
    content.append("")

    for i, ac in enumerate(parsed_data["acceptance_criteria"], 1):
        gwt = generate_ac_given_when_then(ac["text"], parsed_data["story_text"])
        content.append(f"### AC{i}: {ac['text']}")
        content.append("")
        content.append(f"**GIVEN** {gwt['given']}")
        content.append(f"**WHEN** {gwt['when']}")
        content.append(f"**THEN** {gwt['then']}")
        content.append(f"**AND** {gwt['and']}")
        content.append("")

    # If no AC found, add placeholder
    if not parsed_data["acceptance_criteria"]:
        content.append("### AC1: Implementation Complete")
        content.append("")
        content.append("**GIVEN** the development environment is ready")
        content.append("**WHEN** the implementation is complete")
        content.append("**THEN** all requirements are satisfied")
        content.append("**AND** tests pass successfully")
        content.append("")

    content.append("---")
    content.append("")

    # Tasks section
    content.append("## Tasks")
    content.append("")
    content.append("| # | Task File | Title | Linked AC | Status |")
    content.append("|---|-----------|-------|-----------|--------|")

    # Generate 4 task entries
    task_titles = [
        ("Setup and Configuration", "AC1"),
        ("Core Implementation", "AC1, AC2"),
        ("Testing and Validation", "AC3"),
        ("Documentation and Cleanup", "AC4")
    ]

    for i, (title, linked_ac) in enumerate(task_titles, 1):
        task_file = f"task-{i:02d}-{'setup' if i == 1 else 'implementation' if i == 2 else 'testing' if i == 3 else 'documentation'}.md"
        content.append(f"| T{i} | [./{task_file}](./tasks/{task_file}) | {title} | {linked_ac} | pending |")

    content.append("")
    content.append("---")
    content.append("")

    # Testing Requirements section
    content.append("## Testing Requirements")
    content.append("")
    content.append("| Path | Test File | Coverage |")
    content.append("|------|-----------|----------|")

    test_file_base = story_name.replace('-', '_')
    content.append(f"| Happy Path | tests/e2e/test_{test_file_base}.ts | Success case: all features work correctly |")
    content.append(f"| Fail Path | tests/e2e/test_{test_file_base}_error.ts | Error handling: API failures, validation errors |")
    content.append(f"| Null/Empty | tests/e2e/test_{test_file_base}_empty.ts | Empty state: no data, null values |")
    content.append(f"| Edge Cases | tests/e2e/test_{test_file_base}_edge.ts | Boundary conditions: limits, special characters |")
    content.append("")
    content.append("---")
    content.append("")

    # References section
    content.append("## References")
    content.append("")
    content.append("- Epic: EPIC-5-UX")
    content.append("- PRD: .bmad/planning-artifacts/prd.md")
    content.append("- Architecture: docs/ARCHITECTURE_OVERVIEW.md")
    content.append("- Design System: docs/design/FIGMA_DESIGN_BRIEF.md")
    content.append("")

    return '\n'.join(content)


def remediate_story(story_dir: Path) -> bool:
    """Remediate a single story file."""
    story_file = get_story_file(story_dir)

    if not story_file.exists():
        print(f"  WARNING: Story file not found: {story_file}")
        return False

    try:
        # Read existing content
        with open(story_file, 'r') as f:
            content = f.read()

        # Parse existing content
        parsed = parse_story(content)

        # Generate remediated content
        new_content = generate_remediated_story(story_dir, parsed)

        # Write back
        with open(story_file, 'w') as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"  ERROR: Failed to remediate {story_file}: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("EPIC-5-UX Story Remediation")
    print("=" * 60)
    print()

    story_dirs = get_story_dirs()
    total = len(story_dirs)
    success = 0
    failed = 0

    print(f"Found {total} stories to remediate")
    print()

    for i, story_dir in enumerate(story_dirs, 1):
        print(f"[{i}/{total}] Remediating: {story_dir.name}")

        if remediate_story(story_dir):
            success += 1
            print(f"  OK")
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"Complete: {success} success, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
