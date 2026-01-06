# Component Diagrams - Nexus UI Platform

This directory contains component architecture diagrams showing the React component hierarchy, widget dependencies, and UI structure for the Nexus UI security platform.

## Diagram Index

### 1. [Dashboard Hierarchy](./01-dashboard-hierarchy.md)
**Purpose:** Understand the React component tree structure and page organization

**Scope:** App Shell → Navigation → Dashboard Pages → Widget Grid → Widget Components

**Key Components:**
- **App Shell:** AppLayout, NavigationSidebar, TopBar, MainContent
- **Navigation:** Logo, NavMenu, UserProfile, links to all main sections
- **Dashboard Pages:** Security Posture, Vulnerability, Compliance, Alert Center, Asset Management, Risk Overview, Executive Summary
- **Widget Grid:** MetricCard, TrendChart, PieChart, DataTable, AlertsList, MapWidget
- **Shared Components:** DateRangePicker, ConnectorFilter, SeverityFilter, ExportButton

**Component Library:**
| Category | Components | Source |
|----------|------------|--------|
| Layout | AppShell, Sidebar, TopBar | MUI + Custom |
| Navigation | NavMenu, Breadcrumb, Tabs | MUI Tabs |
| Data Display | Card, Table, List, Badge | MUI + Custom |
| Charts | Line, Bar, Pie, Area | Recharts |
| Forms | Input, Select, DatePicker | MUI Forms |
| Feedback | Alert, Toast, Modal | MUI + Sonner |

**Use Cases:**
- Planning new dashboard features
- Understanding component reuse
- Debugging render issues
- Onboarding frontend developers

---

### 2. [Widget Dependencies](./02-widget-dependencies.md)
**Purpose:** Map which data sources feed which dashboard widgets

**Scope:** Data Sources → API Endpoints → TanStack Query Hooks → Widget Components

**Key Concepts:**
- Data source to widget mapping
- Query key patterns for caching
- Dependency graph for invalidation
- Loading and error state propagation

**Widget Data Sources:**
| Widget | Primary Data Source | Cache TTL |
|--------|---------------------|-----------|
| MetricCard | `/api/metrics/summary` | 60s |
| TrendChart | `/api/metrics/trends` | 300s |
| AlertsList | `/api/alerts/recent` | 30s |
| DataTable | `/api/assets` (paginated) | 60s |
| MapWidget | `/api/assets/geo` | 300s |

**Use Cases:**
- Optimizing data fetching
- Debugging stale data issues
- Planning cache invalidation
- Understanding data dependencies

---

## Component State Flow

### State Management Architecture

```
                      ┌─────────────────────────────┐
                      │      Zustand Store          │
                      │  (Global UI State)          │
                      └──────────────┬──────────────┘
                                     │
    ┌────────────────────────────────┼────────────────────────────────┐
    │                                │                                │
    ▼                                ▼                                ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│ TanStack    │              │ URL State   │              │ Local State │
│ Query       │              │ (Router)    │              │ (useState)  │
│ (Server)    │              │ (Filters)   │              │ (UI only)   │
└─────────────┘              └─────────────┘              └─────────────┘
```

### State Types

| State Type | Tool | Use Case |
|------------|------|----------|
| Server State | TanStack Query | API data, caching, sync |
| Global UI State | Zustand | Theme, sidebar, user prefs |
| URL State | Next.js Router | Filters, pagination, search |
| Local State | React useState | Form inputs, modals, hover |

---

## Storybook Organization

```
stories/
├── layout/
│   ├── AppShell.stories.tsx
│   ├── Sidebar.stories.tsx
│   └── TopBar.stories.tsx
├── dashboards/
│   ├── SecurityPosture.stories.tsx
│   ├── Vulnerability.stories.tsx
│   └── Compliance.stories.tsx
├── widgets/
│   ├── MetricCard.stories.tsx
│   ├── TrendChart.stories.tsx
│   └── DataTable.stories.tsx
├── charts/
│   ├── LineChart.stories.tsx
│   ├── BarChart.stories.tsx
│   └── PieChart.stories.tsx
└── forms/
    ├── ConnectorForm.stories.tsx
    ├── FilterForm.stories.tsx
    └── SettingsForm.stories.tsx
```

---

## Related Diagrams

| Category | Diagram | Relationship |
|----------|---------|--------------|
| Architecture | [System Architecture](../architecture/01-system-architecture.md) | Shows where frontend fits |
| Data Flows | [Dashboard Request](../data-flows/01-dashboard-request.md) | How data reaches components |
| Data Flows | [Real-time Updates](../data-flows/05-real-time-updates.md) | WebSocket to component updates |

---

## Related Documentation

- [Component Library](../../planning-artifacts/04-component-library.md) - Full component specifications
- [Design System](../../planning-artifacts/10-design-system.md) - Design tokens and patterns
- [UX Requirements](../../planning-artifacts/17-ux-requirements.md) - User experience guidelines

---

Last Updated: 2026-01-04
Maintained By: Frontend Team
