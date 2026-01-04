#!/usr/bin/env python3
"""
Enhanced Story Generator with Party Mode AI Prompts

This script generates comprehensive stories with:
- Story-specific file paths based on title analysis
- Exact code patterns per story type
- Anti-patterns to avoid
- Edge cases to handle
- Verification commands that prove completion
- Reference implementations

Usage:
    python scripts/generate-enhanced-stories.py [--epic EPIC_ID] [--dry-run]
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
EPICS_DIR = PROJECT_ROOT / ".bmad" / "planning-artifacts" / "epics"
OUTPUT_DIR = PROJECT_ROOT / ".bmad" / "generated-stories"
TEMPLATES_DIR = PROJECT_ROOT / ".bmad" / "templates"

# Epic to JIRA key mapping
EPIC_JIRA_KEYS = {
    "EPIC-1-PLATFORM": "ARGUS-1",
    "EPIC-2-GRAPH": "ARGUS-3",
    "EPIC-3-RISK": "ARGUS-4",
    "EPIC-4-AUTOMATION": "ARGUS-5",
    "EPIC-5-UX": "ARGUS-6",
    "EPIC-6-INTEGRATION": "ARGUS-7",
    "EPIC-7-DIFFERENTIATION": "ARGUS-8",
    "EPIC-8-PLATFORM-DOMINANCE": "ARGUS-9",
    "EPIC-8-EXEC-COMPLIANCE": "ARGUS-92",
    "EPIC-9-OPERATIONS": "ARGUS-10",
    "EPIC-9-POLICY-AI": "ARGUS-93",
    "EPIC-AUTH-001": "ARGUS-11",
    "EPIC-11-CARTOGRAPHY": "ARGUS-94",
    "EPIC-11-CARTOGRAPHY-NEBULAGRAPH": "ARGUS-94",
}

# Story prefix to service/directory mapping (Party Mode: Winston's enhancement)
SERVICE_MAP = {
    "PLAT": {
        "service": "argus-api",
        "directories": ["submodules/argus-api/", "submodules/argus-common/", "deploy/charts/"],
        "language": "rust",
        "port": 8080,
    },
    "GRAPH": {
        "service": "argus-graph-service",
        "directories": ["submodules/argus-graph-service/", "submodules/argus-common/"],
        "language": "rust",
        "port": 8084,
    },
    "RISK": {
        "service": "argus-score",
        "directories": ["submodules/argus-score/", "submodules/argus-common/"],
        "language": "rust",
        "port": 8082,
    },
    "AUTO": {
        "service": "argus-policy",
        "directories": ["submodules/argus-policy/", "policies/cedar/"],
        "language": "rust",
        "port": 8083,
    },
    "UX": {
        "service": "argus-ui",
        "directories": ["submodules/argus-ui/apps/argus-ui/src/"],
        "language": "typescript",
        "port": 3000,
    },
    "INT": {
        "service": "argus-ingest",
        "directories": ["submodules/argus-ingest/", "submodules/argus-common/"],
        "language": "rust",
        "port": 8081,
    },
    "DIFF": {
        "service": "argus-api",
        "directories": ["submodules/argus-api/", "submodules/argus-ui/"],
        "language": "rust",
        "port": 8080,
    },
    "EXEC": {
        "service": "argus-ui",
        "directories": ["submodules/argus-ui/apps/argus-ui/src/"],
        "language": "typescript",
        "port": 3000,
    },
    "COMP": {
        "service": "argus-ui",
        "directories": ["submodules/argus-ui/apps/argus-ui/src/"],
        "language": "typescript",
        "port": 3000,
    },
    "POLICY": {
        "service": "argus-policy",
        "directories": ["submodules/argus-policy/", "policies/cedar/"],
        "language": "rust",
        "port": 8083,
    },
    "CARTO": {
        "service": "argus-graph-service",
        "directories": ["submodules/argus-graph-service/"],
        "language": "rust",
        "port": 8084,
    },
    "STORY": {
        "service": "argus-common",
        "directories": ["submodules/argus-common/", "submodules/argus-api/"],
        "language": "rust",
        "port": 8080,
    },
}

# Reference implementations per story type (Party Mode: Winston's enhancement)
REFERENCE_IMPLEMENTATIONS = {
    "infrastructure": "PLAT-001 (ClickHouse Helm Chart)",
    "backend": "PLAT-020 (Finding API Handler)",
    "frontend": "UX-001 (Tailwind Configuration)",
    "integration": "INT-001 (Scanner Adapter Trait)",
}


@dataclass
class FunctionalRequirement:
    id: str
    name: str
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class Story:
    id: str
    title: str
    description: str
    points: int
    wave: int
    sprint: int
    priority: str
    mvp: int
    epic_id: str
    epic_jira_key: str
    story_type: str
    functional_requirements: List[FunctionalRequirement] = field(default_factory=list)
    code_quality: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    unit_testing: List[str] = field(default_factory=list)
    integration_testing: List[str] = field(default_factory=list)
    e2e_testing: List[str] = field(default_factory=list)
    verification: Optional[str] = None

    @property
    def prefix(self) -> str:
        return self.id.split("-")[0].upper()

    @property
    def service_info(self) -> Dict:
        return SERVICE_MAP.get(self.prefix, SERVICE_MAP["PLAT"])

    @property
    def labels(self) -> List[str]:
        prefix = self.id.split("-")[0].lower()
        return [prefix, f"wave{self.wave}", f"sprint{self.sprint}", self.priority.lower(), f"mvp{self.mvp}"]


def infer_file_paths(story: Story) -> List[str]:
    """Infer specific file paths from story title (Party Mode: Amelia's enhancement)."""
    title_lower = story.title.lower()
    service = story.service_info
    base_dir = service["directories"][0]
    paths = []

    # Rust backend patterns
    if service["language"] == "rust":
        if "helm" in title_lower or "chart" in title_lower:
            chart_name = re.sub(r'[^a-z0-9]+', '-', title_lower.split("helm")[0].strip())
            paths.append(f"deploy/charts/{chart_name}/")
        elif "handler" in title_lower or "endpoint" in title_lower or "api" in title_lower:
            handler_name = re.sub(r'[^a-z_]+', '_', title_lower.replace("handler", "").replace("endpoint", "").strip())
            paths.append(f"{base_dir}src/handlers/{handler_name}.rs")
            paths.append(f"{base_dir}src/handlers/mod.rs")
        elif "model" in title_lower or "schema" in title_lower or "table" in title_lower:
            model_name = re.sub(r'[^a-z_]+', '_', title_lower.replace("model", "").replace("schema", "").strip())
            paths.append(f"{base_dir}src/domain/{model_name}.rs")
        elif "service" in title_lower:
            service_name = re.sub(r'[^a-z_]+', '_', title_lower.replace("service", "").strip())
            paths.append(f"{base_dir}src/services/{service_name}.rs")
        elif "config" in title_lower:
            paths.append(f"{base_dir}src/config.rs")
        else:
            paths.append(f"{base_dir}src/")

    # TypeScript frontend patterns
    elif service["language"] == "typescript":
        if "component" in title_lower or "button" in title_lower or "modal" in title_lower:
            comp_name = to_pascal_case(title_lower.replace("component", "").strip())
            paths.append(f"{base_dir}components/{comp_name}/{comp_name}.tsx")
            paths.append(f"{base_dir}components/{comp_name}/{comp_name}.stories.tsx")
            paths.append(f"{base_dir}components/{comp_name}/index.ts")
        elif "page" in title_lower or "dashboard" in title_lower:
            page_name = to_kebab_case(title_lower.replace("page", "").replace("dashboard", "").strip())
            paths.append(f"{base_dir}pages/{page_name}/index.tsx")
        elif "hook" in title_lower:
            hook_name = to_camel_case(title_lower.replace("hook", "").strip())
            paths.append(f"{base_dir}hooks/use{hook_name}.ts")
        elif "context" in title_lower or "provider" in title_lower:
            ctx_name = to_pascal_case(title_lower.replace("context", "").replace("provider", "").strip())
            paths.append(f"{base_dir}contexts/{ctx_name}Context.tsx")
        elif "api" in title_lower:
            api_name = to_kebab_case(title_lower.replace("api", "").strip())
            paths.append(f"{base_dir}api/{api_name}.ts")
        else:
            paths.append(f"{base_dir}")

    return paths if paths else [base_dir]


def to_pascal_case(s: str) -> str:
    """Convert to PascalCase."""
    return ''.join(word.capitalize() for word in re.split(r'[^a-zA-Z0-9]+', s) if word)


def to_camel_case(s: str) -> str:
    """Convert to camelCase."""
    pascal = to_pascal_case(s)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def to_kebab_case(s: str) -> str:
    """Convert to kebab-case."""
    return '-'.join(word.lower() for word in re.split(r'[^a-zA-Z0-9]+', s) if word)


def to_snake_case(s: str) -> str:
    """Convert to snake_case."""
    return '_'.join(word.lower() for word in re.split(r'[^a-zA-Z0-9]+', s) if word)


def determine_story_type(section: str, story_id: str) -> str:
    """Determine story type based on content analysis and story ID prefix."""
    section_lower = section.lower()
    story_prefix = story_id.split("-")[0].upper()

    if story_prefix in ["UX", "EXEC", "COMP"]:
        return "frontend"

    if any(kw in section_lower for kw in ["helm", "kubernetes", "k8s", "deployment", "statefulset", "cronjob", "chart"]):
        return "infrastructure"

    if any(kw in section_lower for kw in ["react", "component", "page", "ui display", "button", "modal", "dashboard", "tailwind"]):
        return "frontend"

    if any(kw in section_lower for kw in ["integration", "adapter", "scanner", "sync", "webhook"]):
        return "integration"

    return "backend"


def get_rust_patterns(story: Story) -> str:
    """Get Rust-specific code patterns (Party Mode: Amelia's enhancement)."""
    return f'''
RUST CODE PATTERNS (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HANDLER PATTERN (if implementing API endpoint):
```rust
use axum::{{extract::{{State, Path, Query}}, Json, http::StatusCode}};
use serde::{{Deserialize, Serialize}};

#[derive(Debug, Deserialize)]
pub struct Request {{
    // Request fields
}}

#[derive(Debug, Serialize)]
pub struct Response {{
    // Response fields
}}

#[tracing::instrument(name = "{to_snake_case(story.title)}", skip(state))]
pub async fn {to_snake_case(story.title)}(
    State(state): State<AppState>,
    Json(request): Json<Request>,
) -> Result<Json<Response>, AppError> {{
    tracing::info!("Processing request");

    // Implementation here

    Ok(Json(Response {{ /* fields */ }}))
}}
```

ERROR HANDLING PATTERN:
```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum {to_pascal_case(story.title)}Error {{
    #[error("Not found: {{0}}")]
    NotFound(String),
    #[error("Validation failed: {{0}}")]
    ValidationError(String),
    #[error("Database error: {{0}}")]
    DatabaseError(#[from] clickhouse::error::Error),
}}
```

TEST PATTERN:
```rust
#[cfg(test)]
mod tests {{
    use super::*;
    use axum::http::StatusCode;

    #[tokio::test]
    async fn test_{to_snake_case(story.title)}_success() {{
        // Arrange
        let app = create_test_app().await;
        let request = Request {{ /* fields */ }};

        // Act
        let response = app
            .oneshot(
                axum::http::Request::builder()
                    .method("POST")
                    .uri("/api/v1/endpoint")
                    .header("content-type", "application/json")
                    .body(serde_json::to_string(&request).unwrap().into())
                    .unwrap(),
            )
            .await
            .unwrap();

        // Assert
        assert_eq!(response.status(), StatusCode::OK);
    }}

    #[tokio::test]
    async fn test_{to_snake_case(story.title)}_not_found() {{
        // Test error case
    }}

    #[tokio::test]
    async fn test_{to_snake_case(story.title)}_validation_error() {{
        // Test validation
    }}
}}
```

ANTI-PATTERNS (FORBIDDEN):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ unwrap() - Use `?` or explicit error handling
❌ println!() - Use tracing::{{info, debug, error, warn}}
❌ Hardcoded values - Use config or environment variables
❌ TODO/FIXME without issue link
❌ Clone when borrow would work
❌ String when &str would work
❌ pub fields without validation - Use constructor methods
'''


def get_typescript_patterns(story: Story) -> str:
    """Get TypeScript/React-specific code patterns (Party Mode: Sally's enhancement)."""
    comp_name = to_pascal_case(story.title)
    return f'''
TYPESCRIPT/REACT PATTERNS (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT PATTERN:
```typescript
import {{ FC }} from 'react';
import {{ cn }} from '@/lib/utils';

interface {comp_name}Props {{
  className?: string;
  // Other props
}}

export const {comp_name}: FC<{comp_name}Props> = ({{
  className,
  // destructured props
}}) => {{
  return (
    <div className={{cn('', className)}}>
      {{/* Component content */}}
    </div>
  );
}};
```

API HOOK PATTERN:
```typescript
import {{ useQuery, useMutation, useQueryClient }} from '@tanstack/react-query';
import {{ api }} from '@/lib/api';

interface {comp_name}Data {{
  // Data type
}}

export function use{comp_name}() {{
  return useQuery({{
    queryKey: ['{to_kebab_case(story.title)}'],
    queryFn: async (): Promise<{comp_name}Data> => {{
      const response = await api.get('/api/v1/{to_kebab_case(story.title)}');
      return response.data;
    }},
  }});
}}

export function useCreate{comp_name}() {{
  const queryClient = useQueryClient();

  return useMutation({{
    mutationFn: async (data: Create{comp_name}Request) => {{
      return api.post('/api/v1/{to_kebab_case(story.title)}', data);
    }},
    onSuccess: () => {{
      queryClient.invalidateQueries({{ queryKey: ['{to_kebab_case(story.title)}'] }});
    }},
  }});
}}
```

FORM PATTERN (with Zod validation):
```typescript
import {{ useForm }} from 'react-hook-form';
import {{ zodResolver }} from '@hookform/resolvers/zod';
import {{ z }} from 'zod';

const {to_camel_case(story.title)}Schema = z.object({{
  // Field validations
  name: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
}});

type {comp_name}FormData = z.infer<typeof {to_camel_case(story.title)}Schema>;

export function {comp_name}Form() {{
  const {{ register, handleSubmit, formState: {{ errors }} }} = useForm<{comp_name}FormData>({{
    resolver: zodResolver({to_camel_case(story.title)}Schema),
  }});

  const onSubmit = (data: {comp_name}FormData) => {{
    // Handle submission
  }};

  return (
    <form onSubmit={{handleSubmit(onSubmit)}}>
      {{/* Form fields */}}
    </form>
  );
}}
```

ANTI-PATTERNS (FORBIDDEN):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ any type - Always use explicit types
❌ console.log - Use proper logging or remove
❌ Inline styles - Use Tailwind classes
❌ Default exports - Use named exports
❌ useEffect for data fetching - Use React Query
❌ Props drilling > 2 levels - Use Context or Zustand
❌ Non-semantic HTML - Use proper elements (button, nav, main)
'''


def get_storybook_pattern(story: Story) -> str:
    """Get Storybook patterns (Party Mode: Sally's enhancement)."""
    comp_name = to_pascal_case(story.title)
    return f'''
STORYBOOK STORY FILE (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Location: submodules/argus-ui/apps/argus-ui/src/components/{comp_name}/{comp_name}.stories.tsx

```typescript
import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ within, userEvent, expect }} from '@storybook/test';
import {{ {comp_name} }} from './{comp_name}';

const meta: Meta<typeof {comp_name}> = {{
  title: 'Features/{story.epic_id.replace("EPIC-", "").replace("-", " ").title()}/{comp_name}',
  component: {comp_name},
  tags: ['autodocs'],
  parameters: {{
    layout: 'centered',
    docs: {{
      description: {{
        component: '{story.description}',
      }},
    }},
  }},
  argTypes: {{
    // Define prop controls
  }},
}};

export default meta;
type Story = StoryObj<typeof {comp_name}>;

// REQUIRED: Default state
export const Default: Story = {{
  args: {{
    // Default props
  }},
}};

// REQUIRED: Loading state
export const Loading: Story = {{
  args: {{
    isLoading: true,
  }},
}};

// REQUIRED: Empty state
export const Empty: Story = {{
  args: {{
    data: [],
  }},
}};

// REQUIRED: Error state
export const Error: Story = {{
  args: {{
    error: 'Failed to load data',
  }},
}};

// REQUIRED: Interaction test
export const WithInteraction: Story = {{
  play: async ({{ canvasElement }}) => {{
    const canvas = within(canvasElement);

    // Find and click a button
    await userEvent.click(canvas.getByRole('button'));

    // Verify result
    await expect(canvas.getByText('Expected result')).toBeInTheDocument();
  }},
}};
```

ACCESSIBILITY REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ aria-label on all interactive elements without visible text
□ aria-describedby for complex inputs with help text
□ role="button" only on non-button elements that act as buttons
□ Tab order matches visual order (no tabindex > 0)
□ Focus visible on all interactive elements
□ Color contrast: 4.5:1 for normal text, 3:1 for large text
□ Touch target: minimum 44x44px for mobile
'''


def get_e2e_test_pattern(story: Story) -> str:
    """Get E2E test patterns (Party Mode: Murat's enhancement)."""
    return f'''
E2E TEST PATTERN (MANDATORY for user-facing features):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Location: submodules/argus-ui/apps/argus-ui/e2e/{to_kebab_case(story.title)}.spec.ts

```typescript
import {{ test, expect, Page }} from '@playwright/test';

test.describe('{story.title}', () => {{
  let page: Page;
  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];

  test.beforeEach(async ({{ page: p }}) => {{
    page = p;
    consoleErrors.length = 0;
    networkErrors.length = 0;

    // Capture console errors
    page.on('console', msg => {{
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    }});

    // Capture network errors
    page.on('response', response => {{
      if (response.status() >= 400) {{
        networkErrors.push(`${{response.status()}}: ${{response.url()}}`);
      }}
    }});
  }});

  test.afterEach(async () => {{
    // MANDATORY: Zero console errors
    expect(consoleErrors).toHaveLength(0);
    // MANDATORY: Zero network errors
    expect(networkErrors).toHaveLength(0);
  }});

  test('should complete happy path with persistence', async () => {{
    // 1. Navigate
    await page.goto('/path');

    // 2. Perform action
    await page.getByRole('button', {{ name: 'Submit' }}).click();

    // 3. MANDATORY: Verify API call
    const response = await page.waitForResponse(r =>
      r.url().includes('/api/v1/endpoint') &&
      r.request().method() === 'POST'
    );
    expect(response.status()).toBe(200);

    // 4. MANDATORY: Verify persistence (reload test)
    await page.reload();
    await expect(page.getByText('Expected saved value')).toBeVisible();
  }});

  test('should block submission with invalid data', async () => {{
    let apiCalled = false;
    page.on('request', r => {{
      if (r.url().includes('/api/')) apiCalled = true;
    }});

    // Try invalid submission
    await page.getByRole('button', {{ name: 'Submit' }}).click();

    // MANDATORY: API should NOT be called
    await page.waitForTimeout(500);
    expect(apiCalled).toBe(false);

    // Validation error should be visible
    await expect(page.getByRole('alert')).toBeVisible();
  }});
}});
```

VERIFICATION (all must pass):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
npm run e2e -- {to_kebab_case(story.title)}.spec.ts
# Expected: All tests pass, 0 console errors, 0 network errors
'''


def get_edge_cases(story: Story) -> str:
    """Get edge cases to handle (Party Mode: Mary's enhancement)."""
    return f'''
EDGE CASES (must handle all):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EMPTY/NULL STATES:
- Empty list/array returns
- Null/undefined optional fields
- Empty string inputs
- Zero numeric values

BOUNDARY CONDITIONS:
- Maximum pagination limit (100 items)
- Maximum string length (varies by field)
- Timeout after 30 seconds
- Maximum file size (10MB)

CONCURRENT ACCESS:
- Optimistic locking for updates
- Retry logic for conflicts (3 attempts)
- Stale data handling

NETWORK FAILURES:
- API timeout → show retry option
- 5xx errors → show error message + retry
- 4xx errors → show specific error
- Offline → show cached data if available

AUTHORIZATION:
- Unauthenticated → redirect to login
- Unauthorized → show 403 message
- Token expired → refresh token or re-login
'''


def get_verification_commands(story: Story) -> str:
    """Get verification commands (Party Mode: Bob's enhancement)."""
    service = story.service_info

    if story.story_type == "infrastructure":
        return f'''
VERIFICATION COMMANDS (execute in order):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Lint Helm chart
helm lint deploy/charts/{{chart-name}}
# Expected: 0 errors

# 2. Template render test
helm template test deploy/charts/{{chart-name}} --debug
# Expected: Valid YAML output

# 3. Dry run against cluster
helm template test deploy/charts/{{chart-name}} | kubectl apply --dry-run=client -f -
# Expected: "created (dry run)" messages

# 4. Deploy to dev namespace
helm upgrade --install {{release}} deploy/charts/{{chart-name}} -n argus-dev --wait
# Expected: "Release ... has been upgraded"

# 5. Verify pods running
kubectl get pods -l app.kubernetes.io/name={{app}} -n argus-dev
# Expected: All pods Running, Ready

# 6. Health check
kubectl exec -n argus-dev deployment/{{deployment}} -- wget -qO- http://localhost:{{port}}/healthz
# Expected: {{"status": "healthy"}}
'''
    elif service["language"] == "rust":
        return f'''
VERIFICATION COMMANDS (execute in order):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Format check
cargo fmt -p {service["service"].replace("-", "_")} --check
# Expected: No output (already formatted)

# 2. Lint check
cargo clippy -p {service["service"].replace("-", "_")} -- -D warnings
# Expected: No warnings

# 3. Unit tests
cargo test -p {service["service"].replace("-", "_")}
# Expected: All tests pass

# 4. Build
cargo build -p {service["service"].replace("-", "_")}
# Expected: Compiled successfully

# 5. Run service
cargo run -p {service["service"].replace("-", "_")} &
# Expected: "Listening on 0.0.0.0:{service["port"]}"

# 6. API test (if endpoint story)
curl -X POST http://localhost:{service["port"]}/api/v1/{{endpoint}} \\
  -H "Content-Type: application/json" \\
  -d '{{"field": "value"}}'
# Expected: 200 OK with response body
'''
    else:  # TypeScript/frontend
        return f'''
VERIFICATION COMMANDS (execute in order):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Type check
cd submodules/argus-ui && npm run typecheck
# Expected: No type errors

# 2. Lint check
npm run lint
# Expected: No lint errors

# 3. Unit tests
npm run test -- --coverage
# Expected: All tests pass, coverage > 80%

# 4. Storybook build
npm run storybook:build
# Expected: Build succeeds

# 5. E2E tests
npm run e2e -- {to_kebab_case(story.title)}.spec.ts
# Expected: All tests pass

# 6. Dev server check
npm run dev &
# Open http://localhost:3000 and verify component renders
'''


def generate_problem_statement(story: Story) -> str:
    """Generate enhanced problem statement with party mode prompts."""
    service = story.service_info
    file_paths = infer_file_paths(story)
    ref_impl = REFERENCE_IMPLEMENTATIONS.get(story.story_type, "N/A")

    return f'''## Problem Statement

{story.description}

### AI Implementation Prompt - Problem Analysis

```
You are implementing {story.id}: {story.title} for Armor Argus.

PLATFORM CONTEXT (memorize this):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Armor Argus is an autonomous cloud security platform that:
- Replaces visibility-only tools by safely FIXING highest-impact risks
- Uses NebulaGraph for attack path analysis (graph queries)
- Uses ClickHouse for findings, risk scores, events, and audit evidence (analytics)
- Uses Cedar policy language for deterministic policy enforcement
- Requires SigNoz/OpenTelemetry for all observability
- All services are Rust-based (axum framework) except UI (React/TypeScript)

SERVICE CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target Service: {service["service"]}
Language: {service["language"].upper()}
Port: {service["port"]}
Directories: {", ".join(service["directories"])}

TARGET FILES (create/modify these):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f"- {p}" for p in file_paths)}

REFERENCE IMPLEMENTATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Follow patterns from: {ref_impl}

EPIC CONTEXT: {story.epic_id}
Wave: {story.wave} | Sprint: {story.sprint} | Priority: {story.priority} | MVP: {story.mvp} | Points: {story.points}

WHY THIS STORY MATTERS:
1. {story.description}
2. This enables downstream features in later sprints
3. Blocking: stories that depend on this must wait

BEFORE PROCEEDING, VERIFY YOU UNDERSTAND:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ What files will you create/modify?
□ What existing patterns should you follow?
□ What are the acceptance criteria?
□ What tests are required?
□ What edge cases must you handle?

If ANY of the above is unclear, STOP and research before coding.
Read existing code in {service["directories"][0]} first.
```
'''


def generate_functional_requirements_section(story: Story) -> str:
    """Generate enhanced functional requirements with party mode prompts."""
    service = story.service_info
    lines = ["## Functional Requirements\n"]

    code_patterns = get_rust_patterns(story) if service["language"] == "rust" else get_typescript_patterns(story)

    for i, fr in enumerate(story.functional_requirements, 1):
        lines.append(f'''
### FR-{i}: {fr.name}

**Acceptance Criteria (GIVEN-WHEN-THEN):**
```
GIVEN: The system is in a valid state
WHEN: {fr.name}
THEN: The operation completes successfully
VERIFY: Run verification command below
```

### AI Implementation Prompt - FR-{i}

```
IMPLEMENT FR-{i}: {fr.name}

STORY CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Story: {story.id} - {story.title}
Service: {service["service"]}
Language: {service["language"].upper()}

THIS REQUIREMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{fr.name}

{code_patterns}

IMPLEMENTATION CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Create/modify the required file(s)
□ Follow the code pattern above exactly
□ Add tracing spans for observability
□ Add unit tests (see test pattern above)
□ Handle all error cases
□ No hardcoded values

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Code compiles: cargo build / npm run build
□ Tests pass: cargo test / npm test
□ Lint passes: cargo clippy / npm run lint
□ Pattern matches reference implementation
```
''')

    return "\n".join(lines)


def generate_storybook_section(story: Story) -> str:
    """Generate enhanced Storybook requirements."""
    if story.story_type != "frontend":
        return ""

    return f'''## Storybook Requirements

### AI Implementation Prompt - Storybook Implementation

```
STORYBOOK REQUIREMENTS FOR {story.id}

MANDATORY: All UI components MUST have Storybook stories.

{get_storybook_pattern(story)}

STORYBOOK VALIDATION CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Story file created at correct location
□ Default story renders without errors
□ Loading state story exists
□ Empty state story exists
□ Error state story exists
□ Interaction test exists with play function
□ Props documented with argTypes
□ Component renders without console errors
□ All interactive elements have aria-labels
□ Keyboard navigation works (Tab, Enter, Space)
□ Focus indicators visible
□ Color contrast passes WCAG AA

VERIFICATION COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd submodules/argus-ui
npm run storybook        # Start dev server, check component
npm run storybook:build  # Must succeed
npm run test:storybook   # Interaction tests must pass

COMMON FAILURES & FIXES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "Cannot find module" → Check import paths
- "Invalid hook call" → Check component is wrapped in providers
- Accessibility errors → Add aria-label, fix contrast
```
'''


def generate_testing_section(story: Story) -> str:
    """Generate enhanced testing requirements with party mode prompts."""
    service = story.service_info

    storybook_section = ""
    e2e_section = ""

    if story.story_type == "frontend":
        storybook_section = '''
TIER 4 - STORYBOOK TESTS (MANDATORY for frontend):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Story file exists with all required stories
□ Default, Loading, Empty, Error states
□ Interaction test with play function
□ No console errors in Storybook
□ Accessibility addon passes'''
        e2e_section = get_e2e_test_pattern(story)

    return f'''## Testing Requirements

### AI Implementation Prompt - Testing Strategy

```
TEST STRATEGY FOR {story.id}

RISK ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Impact if broken: {"HIGH - blocks other stories" if story.priority == "P0" else "MEDIUM" if story.priority == "P1" else "LOW"}
Story type: {story.story_type}
Language: {service["language"].upper()}
Points: {story.points} (complexity indicator)

COVERAGE REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Unit tests: 80% line coverage minimum
- Integration tests: All API endpoints
- E2E tests: Happy path + error path

TIER 1 - UNIT TESTS (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Test success case
□ Test error/failure case
□ Test edge cases (null, empty, max)
□ Test validation logic
□ Mock external dependencies

{"RUST TEST PATTERN:" if service["language"] == "rust" else "TYPESCRIPT TEST PATTERN:"}
```{"rust" if service["language"] == "rust" else "typescript"}
#[tokio::test]
async fn test_success_case() {{
    // Arrange
    let input = create_valid_input();

    // Act
    let result = function_under_test(input).await;

    // Assert
    assert!(result.is_ok());
    let output = result.unwrap();
    assert_eq!(output.field, expected_value);
}}

#[tokio::test]
async fn test_error_case() {{
    // Arrange
    let invalid_input = create_invalid_input();

    // Act
    let result = function_under_test(invalid_input).await;

    // Assert
    assert!(result.is_err());
    assert!(matches!(result.unwrap_err(), ExpectedError::ValidationFailed(_)));
}}
```

TIER 2 - INTEGRATION TESTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ API endpoint returns correct response
□ Database operations work correctly
□ Cross-service calls succeed
□ Error responses are correct format

TIER 3 - E2E TESTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Happy path completes successfully
□ API calls are intercepted and verified
□ Data persists after page reload
□ Validation blocks invalid submissions
□ Console errors = 0
□ Network errors = 0
{storybook_section}

{e2e_section}

{get_edge_cases(story)}

FORBIDDEN (automatic PR rejection):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ #[ignore] annotations on tests
❌ .skip() or .only() in tests
❌ Tests without assertions
❌ Flaky tests
❌ Coverage < 80%
{"❌ Components without Storybook stories" if story.story_type == "frontend" else ""}
```
'''


def generate_done_checklist(story: Story) -> str:
    """Generate enhanced done checklist with party mode prompts."""
    service = story.service_info

    storybook_checks = ""
    if story.story_type == "frontend":
        storybook_checks = '''
STORYBOOK CHECKS (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ SB-1: npm run storybook:build succeeds
□ SB-2: Default story renders correctly
□ SB-3: Loading state story exists
□ SB-4: Empty state story exists
□ SB-5: Error state story exists
□ SB-6: Interaction test passes
□ SB-7: No console errors in Storybook
□ SB-8: Accessibility (a11y) addon passes
□ SB-9: All props documented with argTypes
'''

    return f'''## Done Checklist

### AI Implementation Prompt - Completion Verification

```
DONE CHECKLIST FOR {story.id}
Execute each command. ALL must pass before PR.

ENGINEERING CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ ENG-1: Code compiles without errors
  → {"cargo build -p " + service["service"].replace("-", "_") if service["language"] == "rust" else "npm run build"}

□ ENG-2: All functional requirements implemented
  → Review each FR in this story

□ ENG-3: Code follows existing patterns
  → Compare with reference implementation

□ ENG-4: No hardcoded values
  → grep -r "localhost" src/ → should be empty
  → grep -r "password" src/ → should be empty

QUALITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ QA-1: Lint passes with zero warnings
  → {"cargo clippy -- -D warnings" if service["language"] == "rust" else "npm run lint"}

□ QA-2: Format check passes
  → {"cargo fmt --check" if service["language"] == "rust" else "npm run format:check"}

□ QA-3: No TODO/FIXME without issue link
  → grep -r "TODO\\|FIXME" src/ | grep -v "ARGUS-"

SECURITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ SEC-1: No hardcoded secrets
  → gitleaks detect --source .

□ SEC-2: Input validation on all external inputs
  → Review API handlers

□ SEC-3: Auth required for endpoints (if applicable)
  → Check middleware/guards

OBSERVABILITY CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ OBS-1: Tracing spans on key operations
  → grep -r "tracing::instrument" src/

□ OBS-2: Error logging with context
  → grep -r "tracing::error" src/

□ OBS-3: Metrics if applicable
  → Check metrics module

TEST CHECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ TEST-1: All tests pass
  → {"cargo test -p " + service["service"].replace("-", "_") if service["language"] == "rust" else "npm test"}

□ TEST-2: Coverage > 80%
  → {"cargo tarpaulin -p " + service["service"].replace("-", "_") if service["language"] == "rust" else "npm run test:coverage"}

□ TEST-3: No skipped tests
  → grep -r "#\\[ignore\\]\\|.skip(" tests/
{storybook_checks}
FINAL VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ All checks above pass
□ PR description includes verification evidence
□ Screenshots/outputs attached
□ No TODO/FIXME without issue links

{get_verification_commands(story)}

COMMON FAILURES & TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Clippy warnings → Fix all warnings, don't suppress
- Test failures → Check test database is running
- Build errors → Check dependencies in Cargo.toml
- Lint errors → Run formatter first
```
'''


def generate_implementation_guide(story: Story) -> str:
    """Generate enhanced implementation guide with party mode prompts."""
    service = story.service_info
    file_paths = infer_file_paths(story)

    return f'''## Implementation Guide - Master AI Prompt

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    {story.id}: {story.title[:50]}
║                         COMPLETE IMPLEMENTATION GUIDE
╚══════════════════════════════════════════════════════════════════════════════╝

MISSION BRIEFING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are implementing {story.id} for Armor Argus.
Service: {service["service"]} ({service["language"].upper()})
Epic: {story.epic_id} | Wave: {story.wave} | Sprint: {story.sprint}
Priority: {story.priority} | Points: {story.points}

DESCRIPTION:
{story.description}

TARGET FILES:
{chr(10).join(f"  - {p}" for p in file_paths)}

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: RESEARCH (10 min)
═══════════════════════════════════════════════════════════════════════════════

DELIVERABLES:
□ Read existing code in {service["directories"][0]}
□ Identify similar patterns to follow
□ List all files to create/modify
□ Understand data flow and dependencies

CHECKPOINT:
→ Can you explain what this story does in one sentence?
→ Do you know which files to modify?

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: IMPLEMENTATION ({story.points * 30} min)
═══════════════════════════════════════════════════════════════════════════════

DELIVERABLES:
{chr(10).join(f"□ FR-{i+1}: {fr.name}" for i, fr in enumerate(story.functional_requirements))}

CHECKPOINT:
→ {"cargo build" if service["language"] == "rust" else "npm run build"} succeeds
→ No compiler/type errors

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: TESTING ({story.points * 20} min)
═══════════════════════════════════════════════════════════════════════════════

DELIVERABLES:
□ Unit tests for all new functions
□ Integration tests for API endpoints (if applicable)
□ E2E tests for user-facing features (if applicable)
{"□ Storybook stories for all components" if story.story_type == "frontend" else ""}

CHECKPOINT:
→ {"cargo test" if service["language"] == "rust" else "npm test"} passes
→ Coverage > 80%
{"→ npm run storybook:build succeeds" if story.story_type == "frontend" else ""}

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: QUALITY (10 min)
═══════════════════════════════════════════════════════════════════════════════

DELIVERABLES:
□ {"cargo fmt && cargo clippy -- -D warnings" if service["language"] == "rust" else "npm run lint && npm run format"}
□ No TODO/FIXME without issue links
□ All observability added (tracing, logging)

CHECKPOINT:
→ Zero lint warnings
→ Zero clippy warnings

═══════════════════════════════════════════════════════════════════════════════
PHASE 5: PR & EVIDENCE (10 min)
═══════════════════════════════════════════════════════════════════════════════

DELIVERABLES:
□ Commit with conventional message format
□ PR description with:
  - Summary of changes
  - Test output screenshot
  - Verification commands run
□ All checks passing

CHECKPOINT:
→ CI pipeline green
→ Ready for review

═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA (all must be TRUE):
═══════════════════════════════════════════════════════════════════════════════

□ All functional requirements implemented
□ All tests passing (0 skipped, 0 ignored)
□ Coverage > 80%
□ Zero lint/clippy warnings
□ Zero console errors
□ PR includes evidence screenshots
{"□ Storybook stories complete" if story.story_type == "frontend" else ""}

ESTIMATED TIME: {story.points * 60} minutes
MAXIMUM TIME: {story.points * 120} minutes

IF BLOCKED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Check logs: kubectl logs -l app={service["service"]}
2. Check database: psql/clickhouse-client
3. Ask for help if stuck > 30 min

╔══════════════════════════════════════════════════════════════════════════════╗
║                              END OF GUIDE                                     ║
║           If anything is unclear, STOP and ask before proceeding.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
'''


def generate_story_markdown(story: Story) -> str:
    """Generate complete enhanced story markdown."""
    labels_yaml = "\n".join(f"    - {label}" for label in story.labels)
    service = story.service_info
    file_paths = infer_file_paths(story)

    storybook_section = generate_storybook_section(story)
    storybook_ac = ""
    if story.story_type == "frontend":
        storybook_ac = '''- [ ] Storybook story file created
- [ ] All component states have stories (default, loading, empty, error)
- [ ] Interaction tests pass
- [ ] No console errors in Storybook
- [ ] Storybook builds successfully'''

    return f'''# {story.id}: {story.title}

## Story Metadata

```yaml
story:
  id: {story.id}
  title: "{story.title}"
  type: {story.story_type}
  status: ready

metadata:
  parent: {story.epic_jira_key}
  priority: {story.priority}
  points: {story.points}
  sprint: {story.sprint}
  wave: {story.wave}
  labels:
{labels_yaml}
  owner: TBD
  reviewers:
    - TBD

service:
  name: {service["service"]}
  language: {service["language"]}
  port: {service["port"]}
  directories:
{chr(10).join(f"    - {d}" for d in service["directories"])}

target_files:
{chr(10).join(f"  - {f}" for f in file_paths)}
```

---

{generate_problem_statement(story)}

---

## Goal

{story.description}

Successfully implement all acceptance criteria with proper testing and documentation.

---

## Scope

### In Scope
{chr(10).join(f"- {fr.name}" for fr in story.functional_requirements)}

### Out of Scope
- Features not listed in functional requirements
- Future sprint enhancements
- Performance optimizations beyond SLAs

---

{generate_functional_requirements_section(story)}

---

{storybook_section}
{"---" if story.story_type == "frontend" else ""}

{generate_testing_section(story)}

---

{generate_done_checklist(story)}

---

## Acceptance Criteria

- [ ] All functional requirements implemented
- [ ] All tests passing (0 skipped, coverage > 80%)
- [ ] Zero lint/clippy warnings
- [ ] Zero console errors
- [ ] PR includes verification evidence
- [ ] Code merged to main branch
{storybook_ac}

---

## Deployment Notes

### Target
- Service: {service["service"]}
- Namespace: argus-system
- Port: {service["port"]}

### Verification
{get_verification_commands(story)}

---

## Rollback Strategy

### Risk Assessment
- Database changes: Review migration before merge
- API changes: Check for breaking changes
- State changes: Document any state introduced

### Rollback Command
```bash
# Revert commit
git revert <commit-sha>

# Or rollback Helm release
helm rollback {service["service"]} -n argus-system
```

---

{generate_implementation_guide(story)}

---

## References

- Epic: {story.epic_id}
- PRD: .bmad/planning-artifacts/prd.md
- Architecture: docs/ARCHITECTURE_OVERVIEW.md
- Reference: {REFERENCE_IMPLEMENTATIONS.get(story.story_type, "N/A")}

---

*Generated: {datetime.now().isoformat()}*
*Enhanced with Party Mode AI Prompts*
'''


def parse_epic_file(epic_path: Path) -> List[Story]:
    """Parse an epic markdown file and extract stories."""
    content = epic_path.read_text()
    stories = []

    epic_id = epic_path.stem
    epic_jira_key = EPIC_JIRA_KEYS.get(epic_id, "UNKNOWN")

    if epic_jira_key == "UNKNOWN":
        epic_match = re.search(r"# (EPIC-\d+)", content)
        if epic_match:
            partial_id = epic_match.group(1)
            for key in EPIC_JIRA_KEYS:
                if key.startswith(partial_id):
                    epic_jira_key = EPIC_JIRA_KEYS[key]
                    break

    story_pattern = re.compile(
        r'#### ([A-Z]+-\d+): (.+?)\n'
        r'\*\*Points:\*\* (\d+) \| \*\*Wave:\*\* (\d+) \| \*\*Sprint:\*\* (\d+) \| \*\*Priority:\*\* (P\d) \| \*\*MVP:\*\* (\d+)',
        re.MULTILINE
    )

    story_sections = re.split(r'(?=#### [A-Z]+-\d+:)', content)

    for section in story_sections:
        match = story_pattern.search(section)
        if not match:
            continue

        story_id, title, points, wave, sprint, priority, mvp = match.groups()
        story_type = determine_story_type(section, story_id)

        desc_match = re.search(r'\*\*MVP:\*\* \d+\n.*?\n\n(.+?)(?=\n\n\*\*|\Z)', section, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else title

        func_reqs = parse_functional_requirements(section)
        code_quality = parse_checklist(section, "Code Quality")
        security = parse_checklist(section, "Security")
        unit_testing = parse_checklist(section, "Unit Testing")
        integration_testing = parse_checklist(section, "Integration Testing")
        e2e_testing = parse_checklist(section, "E2E Testing")

        ver_match = re.search(r'\*\*Verification:\*\*\n- Command: (.+?)(?=\n- Expected:)', section)
        verification = ver_match.group(1).strip() if ver_match else None

        story = Story(
            id=story_id,
            title=title,
            description=description,
            points=int(points),
            wave=int(wave),
            sprint=int(sprint),
            priority=priority,
            mvp=int(mvp),
            epic_id=epic_id,
            epic_jira_key=epic_jira_key,
            story_type=story_type,
            functional_requirements=func_reqs,
            code_quality=code_quality,
            security=security,
            unit_testing=unit_testing,
            integration_testing=integration_testing,
            e2e_testing=e2e_testing,
            verification=verification,
        )
        stories.append(story)

    return stories


def parse_functional_requirements(section: str) -> List[FunctionalRequirement]:
    """Parse functional requirements from story section."""
    reqs = []
    fr_match = re.search(r'\*\*Functional Requirements:\*\*\n(.*?)(?=\n\n\*\*|\Z)', section, re.DOTALL)
    if not fr_match:
        return reqs

    fr_content = fr_match.group(1)
    func_pattern = re.compile(r'- \[ \] (FUNC-\d+): (.+)')
    for match in func_pattern.finditer(fr_content):
        func_id, desc = match.groups()
        reqs.append(FunctionalRequirement(id=func_id, name=desc.strip(), acceptance_criteria=[desc.strip()]))

    return reqs


def parse_checklist(section: str, header: str) -> List[str]:
    """Parse a checklist section."""
    items = []
    pattern = rf'\*\*{header}:\*\*\n(.*?)(?=\n\n\*\*|\Z)'
    match = re.search(pattern, section, re.DOTALL)
    if not match:
        return items

    content = match.group(1)
    item_pattern = re.compile(r'- \[ \] [A-Z]+-\d+: (.+)')
    for m in item_pattern.finditer(content):
        items.append(m.group(1).strip())

    return items


def process_epic(epic_name: str, dry_run: bool = False) -> int:
    """Process a single epic and generate enhanced stories."""
    epic_path = EPICS_DIR / f"{epic_name}.md"

    if not epic_path.exists():
        print(f"  ERROR: Epic file not found: {epic_path}")
        return 0

    stories = parse_epic_file(epic_path)
    print(f"  Found {len(stories)} stories in {epic_name}")

    if dry_run:
        for story in stories[:3]:
            print(f"    - {story.id}: {story.title} ({story.story_type})")
        if len(stories) > 3:
            print(f"    ... and {len(stories) - 3} more")
        return len(stories)

    output_dir = OUTPUT_DIR / epic_name
    output_dir.mkdir(parents=True, exist_ok=True)

    for story in stories:
        story_file = output_dir / f"{story.id}.md"
        story_content = generate_story_markdown(story)
        story_file.write_text(story_content)
        print(f"    Generated: {story.id} ({story.story_type})")

    return len(stories)


def main():
    parser = argparse.ArgumentParser(description="Generate enhanced story templates with Party Mode AI prompts")
    parser.add_argument("--epic", help="Process single epic (e.g., EPIC-1-PLATFORM)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating files")
    args = parser.parse_args()

    print("=" * 70)
    print("Armor Argus - Enhanced Story Generator (Party Mode)")
    print("=" * 70)
    print()

    total_stories = 0

    if args.epic:
        print(f"Processing epic: {args.epic}")
        total_stories = process_epic(args.epic, args.dry_run)
    else:
        epic_files = sorted(EPICS_DIR.glob("EPIC-*.md"))
        print(f"Found {len(epic_files)} epic files")
        print()

        for epic_path in epic_files:
            epic_name = epic_path.stem
            print(f"Processing: {epic_name}")
            count = process_epic(epic_name, args.dry_run)
            total_stories += count
            print()

    print("=" * 70)
    print(f"Total stories: {total_stories}")
    if args.dry_run:
        print("(Dry run - no files generated)")
    else:
        print(f"Output directory: {OUTPUT_DIR}")
    print("Enhanced with Party Mode AI Prompts:")
    print("  - Winston: Service mapping, file paths, reference implementations")
    print("  - Amelia: Code patterns, anti-patterns, test templates")
    print("  - Bob: GIVEN-WHEN-THEN criteria, verification commands")
    print("  - Murat: Coverage requirements, E2E patterns, edge cases")
    print("  - Sally: Storybook patterns, accessibility, interaction tests")
    print("  - Mary: Edge cases, business rules, downstream impact")
    print("=" * 70)


if __name__ == "__main__":
    main()
