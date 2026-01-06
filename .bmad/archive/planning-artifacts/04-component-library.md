# Nexus UI Uplift - Component Library Specification

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Platform Alignment:** `/submodules/platform/llm/specifications/`

---

## 1. Overview

This document specifies the component library requirements for Nexus UI Uplift, including Storybook requirements for all components.

### Critical Platform Standards

**MANDATORY: All components MUST:**
1. Be created using Nx generators (never manual creation)
2. Have Storybook stories with MSW handlers
3. Use MUI sx props (not styled-components)
4. Include proper TypeScript interfaces
5. Have unit tests with Vitest
6. Support accessibility (WCAG 2.1 AA)

---

## 2. Technology Stack

### 2.1 Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| React | 19.x | UI framework |
| TypeScript | 5.x | Type safety |
| MUI | 7.1.x | Component library |
| Tailwind CSS | 3.x | Utility classes |
| Storybook | 8.x | Component documentation |
| Vitest | 1.x | Unit testing |
| MSW | 2.x | API mocking |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Type definitions (NOT runtime validation) |
| TanStack Query | 5.x | Server state management |

### 2.2 Platform Libraries

| Library | Purpose |
|---------|---------|
| `@platform/react-ui` | Shared UI components |
| `@platform/react-ui-form` | Form components (RHF + Zod) |
| `@platform/react-api-base` | API utilities |
| `@platform/react-api-auth` | Authentication |

---

## 3. Component Architecture

### 3.1 Directory Structure

```
libs/{domain}/react-ui-{domain}/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   └── {ComponentName}/
│   │   │       ├── {ComponentName}.tsx        # Component
│   │   │       ├── {ComponentName}.spec.tsx   # Tests
│   │   │       ├── {ComponentName}.stories.tsx # Storybook
│   │   │       └── index.ts                   # Export
│   │   ├── pages/
│   │   │   └── {PageName}Page/
│   │   │       ├── {PageName}Page.tsx
│   │   │       ├── {PageName}Page.spec.tsx
│   │   │       ├── {PageName}Page.stories.tsx
│   │   │       └── index.ts
│   │   └── utils/
│   └── index.ts                               # Library exports
├── .storybook/
│   ├── main.ts
│   └── preview.ts
└── project.json
```

### 3.2 Component Template

```typescript
// libs/nexus/react-ui-nexus/src/lib/components/AlertCard/AlertCard.tsx

import { Box, Card, CardContent, Typography, Chip } from "@mui/material";
import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";

interface AlertCardProps {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "acknowledged" | "resolved";
  timestamp: string;
  onAcknowledge?: (id: string) => void;
}

export function AlertCard({
  id,
  title,
  severity,
  status,
  timestamp,
  onAcknowledge,
}: AlertCardProps) {
  const severityColors = {
    critical: "error.main",
    high: "warning.main",
    medium: "info.main",
    low: "success.main",
  };

  return (
    <Card
      sx={{
        borderLeft: 4,
        borderColor: severityColors[severity],
        "&:hover": { bgcolor: "action.hover" },
      }}
      data-testid={`alert-card-${id}`}
    >
      <CardContent sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Box sx={{ color: severityColors[severity] }}>
          {severity === "critical" && <XCircle />}
          {severity === "high" && <AlertTriangle />}
          {(severity === "medium" || severity === "low") && <CheckCircle />}
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="subtitle1">{title}</Typography>
          <Typography variant="caption" color="text.secondary">
            {timestamp}
          </Typography>
        </Box>
        <Chip
          label={status}
          size="small"
          color={status === "resolved" ? "success" : "default"}
        />
      </CardContent>
    </Card>
  );
}
```

### 3.3 Generator Command

**ALWAYS use the generator:**

```bash
nx g @platform/armor-nx-plugin:react-component \
  --name=AlertCard \
  --project=react-ui-nexus \
  --directory=components/AlertCard \
  --export=true
```

---

## 4. Storybook Requirements

### 4.1 Story Structure

**Every component MUST have:**
1. Default story
2. All variant stories
3. Interactive stories (with actions)
4. Loading state story
5. Error state story
6. MSW handlers for API-connected components

### 4.2 Story Template

```typescript
// AlertCard.stories.tsx

import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";
import { AlertCard } from "./AlertCard";

const meta: Meta<typeof AlertCard> = {
  title: "Nexus/Alerts/AlertCard",
  component: AlertCard,
  tags: ["autodocs"],
  parameters: {
    layout: "padded",
  },
  argTypes: {
    severity: {
      control: "select",
      options: ["critical", "high", "medium", "low"],
    },
    status: {
      control: "select",
      options: ["open", "acknowledged", "resolved"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof AlertCard>;

// Default story
export const Default: Story = {
  args: {
    id: "alert-1",
    title: "Suspicious login detected from new location",
    severity: "high",
    status: "open",
    timestamp: "2026-01-03T10:30:00Z",
  },
};

// Severity variants
export const Critical: Story = {
  args: {
    ...Default.args,
    severity: "critical",
    title: "Active ransomware detected",
  },
};

export const Medium: Story = {
  args: {
    ...Default.args,
    severity: "medium",
    title: "Unusual network traffic pattern",
  },
};

export const Low: Story = {
  args: {
    ...Default.args,
    severity: "low",
    title: "Configuration recommendation",
  },
};

// Status variants
export const Acknowledged: Story = {
  args: {
    ...Default.args,
    status: "acknowledged",
  },
};

export const Resolved: Story = {
  args: {
    ...Default.args,
    status: "resolved",
  },
};

// Interactive test
export const WithInteraction: Story = {
  args: Default.args,
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const card = canvas.getByTestId(`alert-card-${args.id}`);

    await expect(card).toBeInTheDocument();
    await expect(canvas.getByText(args.title)).toBeVisible();
  },
};
```

### 4.3 Stories with API Calls (MSW Required)

```typescript
// AlertList.stories.tsx

import type { Meta, StoryObj } from "@storybook/react";
import { http, HttpResponse } from "msw";
import { AlertList } from "./AlertList";

// Mock handlers
const mockAlerts = [
  { id: "1", title: "Alert 1", severity: "high", status: "open" },
  { id: "2", title: "Alert 2", severity: "medium", status: "acknowledged" },
];

const handlers = [
  http.get("/api/v1/alerts", () => {
    return HttpResponse.json({ data: { items: mockAlerts } });
  }),
];

const errorHandlers = [
  http.get("/api/v1/alerts", () => {
    return new HttpResponse(null, { status: 500 });
  }),
];

const loadingHandlers = [
  http.get("/api/v1/alerts", async () => {
    await new Promise((resolve) => setTimeout(resolve, 999999));
    return HttpResponse.json({ data: { items: [] } });
  }),
];

const meta: Meta<typeof AlertList> = {
  title: "Nexus/Alerts/AlertList",
  component: AlertList,
  parameters: {
    msw: {
      handlers: handlers, // Default handlers
    },
  },
};

export default meta;
type Story = StoryObj<typeof AlertList>;

export const Default: Story = {};

export const Loading: Story = {
  parameters: {
    msw: {
      handlers: loadingHandlers,
    },
  },
};

export const Error: Story = {
  parameters: {
    msw: {
      handlers: errorHandlers,
    },
  },
};

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("/api/v1/alerts", () => {
          return HttpResponse.json({ data: { items: [] } });
        }),
      ],
    },
  },
};
```

---

## 5. Component Categories

### 5.1 Dashboard Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `MetricCard` | Display single metric with trend | P0 |
| `MetricGrid` | Grid of metric cards | P0 |
| `TrendChart` | Line/area chart for trends | P0 |
| `SeverityDonut` | Donut chart by severity | P0 |
| `StatusBadge` | Status indicator badge | P0 |
| `TimeRangeSelector` | Date range picker | P0 |
| `RefreshIndicator` | Auto-refresh status | P1 |

### 5.2 Alert Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `AlertCard` | Alert summary card | P0 |
| `AlertList` | Paginated alert list | P0 |
| `AlertDetail` | Full alert details | P0 |
| `AlertTimeline` | Timeline view | P1 |
| `AlertFilters` | Filter controls | P0 |
| `AlertActions` | Bulk action buttons | P1 |

### 5.3 Asset Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `AssetCard` | Asset summary card | P0 |
| `AssetTable` | Asset data table | P0 |
| `AssetDetail` | Asset detail view | P0 |
| `AssetRiskScore` | Risk score visualization | P0 |
| `AssetGraph` | Network graph view | P2 |

### 5.4 Vulnerability Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `VulnCard` | Vulnerability card | P0 |
| `VulnTable` | Vulnerability table | P0 |
| `VulnDetail` | Detail with CVSS | P0 |
| `VulnTrend` | Trend over time | P1 |
| `VulnSLATracker` | SLA countdown | P1 |

### 5.5 Compliance Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `ComplianceScore` | Overall score display | P0 |
| `FrameworkCard` | Framework status | P0 |
| `ControlList` | Control checklist | P0 |
| `EvidenceUploader` | Evidence attachment | P1 |
| `GapAnalysis` | Gap visualization | P1 |

### 5.6 Form Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `RHFInput` | Text input (RHF) | P0 |
| `RHFSelect` | Select dropdown | P0 |
| `RHFMultiSelect` | Multi-select | P0 |
| `RHFCheckbox` | Checkbox | P0 |
| `RHFDatePicker` | Date picker | P0 |
| `RHFSwitch` | Toggle switch | P0 |
| `FormActions` | Submit/Cancel buttons | P0 |

### 5.7 Layout Components

| Component | Description | Priority |
|-----------|-------------|----------|
| `PageHeader` | Page title + actions | P0 |
| `PageLayout` | Standard page wrapper | P0 |
| `Sidebar` | Navigation sidebar | P0 |
| `TopBar` | Top navigation bar | P0 |
| `ContentCard` | Content container | P0 |
| `LoadingOverlay` | Loading state | P0 |
| `EmptyState` | No data state | P0 |
| `ErrorState` | Error display | P0 |

---

## 6. Design Tokens

### 6.1 Color Tokens

```typescript
const tokens = {
  // Severity colors
  severity: {
    critical: "#DC2626", // red-600
    high: "#EA580C",     // orange-600
    medium: "#CA8A04",   // yellow-600
    low: "#16A34A",      // green-600
    info: "#2563EB",     // blue-600
  },

  // Status colors
  status: {
    open: "#F59E0B",         // amber-500
    acknowledged: "#3B82F6", // blue-500
    resolved: "#10B981",     // emerald-500
    closed: "#6B7280",       // gray-500
  },

  // Background
  background: {
    default: "#0F172A", // slate-900
    paper: "#1E293B",   // slate-800
    elevated: "#334155", // slate-700
  },

  // Text
  text: {
    primary: "#F8FAFC",   // slate-50
    secondary: "#94A3B8", // slate-400
    disabled: "#64748B",  // slate-500
  },
};
```

### 6.2 Typography Tokens

```typescript
const typography = {
  fontFamily: "'Inter', -apple-system, sans-serif",
  h1: { fontSize: "2.5rem", fontWeight: 700 },
  h2: { fontSize: "2rem", fontWeight: 600 },
  h3: { fontSize: "1.5rem", fontWeight: 600 },
  h4: { fontSize: "1.25rem", fontWeight: 600 },
  h5: { fontSize: "1rem", fontWeight: 600 },
  h6: { fontSize: "0.875rem", fontWeight: 600 },
  body1: { fontSize: "1rem", fontWeight: 400 },
  body2: { fontSize: "0.875rem", fontWeight: 400 },
  caption: { fontSize: "0.75rem", fontWeight: 400 },
  button: { fontSize: "0.875rem", fontWeight: 600, textTransform: "none" },
};
```

### 6.3 Spacing Tokens

```typescript
// MUI default spacing: 8px base
const spacing = {
  xs: 0.5,  // 4px
  sm: 1,    // 8px
  md: 2,    // 16px
  lg: 3,    // 24px
  xl: 4,    // 32px
  xxl: 6,   // 48px
};
```

---

## 7. Accessibility Requirements

### 7.1 WCAG 2.1 AA Compliance

| Criterion | Requirement |
|-----------|-------------|
| 1.1.1 | Alt text for images |
| 1.3.1 | Semantic HTML structure |
| 1.4.1 | Color not sole indicator |
| 1.4.3 | 4.5:1 contrast ratio |
| 2.1.1 | Keyboard accessible |
| 2.4.4 | Link purpose clear |
| 2.4.7 | Focus visible |
| 3.1.1 | Page language set |
| 4.1.2 | ARIA attributes correct |

### 7.2 Required ARIA Attributes

```typescript
// Button with icon only
<IconButton
  aria-label="Delete alert"
  onClick={handleDelete}
>
  <DeleteIcon />
</IconButton>

// Status indicators
<Chip
  label="Critical"
  role="status"
  aria-label="Alert severity: critical"
/>

// Loading states
<Box
  role="status"
  aria-live="polite"
  aria-busy={isLoading}
>
  {isLoading ? "Loading..." : content}
</Box>
```

---

## 8. Testing Requirements

### 8.1 Unit Test Requirements

Every component must test:
1. Renders without crashing
2. Props are applied correctly
3. User interactions work
4. Accessibility requirements met
5. Edge cases handled

### 8.2 Unit Test Template

```typescript
// AlertCard.spec.tsx

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe, toHaveNoViolations } from "jest-axe";
import { AlertCard } from "./AlertCard";

expect.extend(toHaveNoViolations);

const defaultProps = {
  id: "alert-1",
  title: "Test Alert",
  severity: "high" as const,
  status: "open" as const,
  timestamp: "2026-01-03T10:00:00Z",
};

describe("AlertCard", () => {
  it("renders without crashing", () => {
    render(<AlertCard {...defaultProps} />);
    expect(screen.getByTestId("alert-card-alert-1")).toBeInTheDocument();
  });

  it("displays the title", () => {
    render(<AlertCard {...defaultProps} />);
    expect(screen.getByText("Test Alert")).toBeVisible();
  });

  it("shows correct severity styling", () => {
    render(<AlertCard {...defaultProps} severity="critical" />);
    // Test styling based on severity
  });

  it("calls onAcknowledge when clicked", async () => {
    const onAcknowledge = vi.fn();
    render(<AlertCard {...defaultProps} onAcknowledge={onAcknowledge} />);

    await userEvent.click(screen.getByRole("button", { name: /acknowledge/i }));
    expect(onAcknowledge).toHaveBeenCalledWith("alert-1");
  });

  it("has no accessibility violations", async () => {
    const { container } = render(<AlertCard {...defaultProps} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 8.3 Visual Regression Testing

```typescript
// AlertCard.visual.spec.tsx (Chromatic)

import { test, expect } from "@playwright/experimental-ct-react";
import { AlertCard } from "./AlertCard";

test.describe("AlertCard Visual", () => {
  test("matches snapshot - default", async ({ mount, page }) => {
    await mount(<AlertCard {...defaultProps} />);
    await expect(page).toHaveScreenshot("alert-card-default.png");
  });

  test("matches snapshot - critical severity", async ({ mount, page }) => {
    await mount(<AlertCard {...defaultProps} severity="critical" />);
    await expect(page).toHaveScreenshot("alert-card-critical.png");
  });
});
```

---

## 9. Documentation Requirements

### 9.1 Storybook Documentation

Every component must include:
1. **Overview**: What the component does
2. **Props table**: Auto-generated from TypeScript
3. **Usage examples**: Code snippets
4. **Accessibility notes**: ARIA, keyboard nav
5. **Design rationale**: Why decisions were made

### 9.2 Documentation Template

```mdx
{/* AlertCard.mdx */}

import { Canvas, Meta, ArgTypes } from "@storybook/blocks";
import * as AlertCardStories from "./AlertCard.stories";

<Meta of={AlertCardStories} />

# AlertCard

Displays a summary of a security alert with severity and status.

## Usage

```tsx
import { AlertCard } from "@platform/react-ui-nexus";

<AlertCard
  id="alert-1"
  title="Suspicious login detected"
  severity="high"
  status="open"
  timestamp="2026-01-03T10:00:00Z"
  onAcknowledge={(id) => handleAcknowledge(id)}
/>
```

## Props

<ArgTypes of={AlertCardStories} />

## Accessibility

- Uses semantic HTML (`<article>` wrapper)
- Includes `aria-label` for severity indicator
- Keyboard navigable
- Focus visible on interactive elements

## Variants

<Canvas of={AlertCardStories.Critical} />
<Canvas of={AlertCardStories.Resolved} />
```

---

## 10. Component Checklist

Before any component is considered complete:

- [ ] Created with Nx generator
- [ ] TypeScript interfaces defined
- [ ] MUI sx props used (no styled-components)
- [ ] Unit tests written and passing
- [ ] Storybook stories for all variants
- [ ] MSW handlers for API-connected components
- [ ] Loading state implemented
- [ ] Error state implemented
- [ ] Empty state implemented
- [ ] Accessibility audit passed
- [ ] data-testid attributes added
- [ ] Documentation written
- [ ] Code review completed
- [ ] Visual regression baseline captured

---

## 11. Related Diagrams

### Figure 1: Dashboard Component Hierarchy
*React component tree structure and page organization.*

> **Diagram:** [Dashboard Hierarchy](../diagrams/components/01-dashboard-hierarchy.md)
>
> Shows:
> - App Shell structure (Layout, Sidebar, TopBar)
> - Dashboard page types (7 views)
> - Widget Grid system
> - Shared components across dashboards

### Figure 2: Widget Data Dependencies
*Data source to widget mapping and query patterns.*

> **Diagram:** [Widget Dependencies](../diagrams/components/02-widget-dependencies.md)
>
> Maps:
> - API endpoints to widgets
> - TanStack Query hooks
> - Cache TTL settings
> - Loading/error state propagation

---

*This document is maintained by the Frontend team. Updates require PR review.*
