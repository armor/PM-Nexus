# Dashboard Component Hierarchy

## Component Tree Structure

```mermaid
graph TB
    subgraph "App Shell"
        A[AppLayout]
        A --> B[NavigationSidebar]
        A --> C[TopBar]
        A --> D[MainContent]
    end

    subgraph "Navigation"
        B --> B1[Logo]
        B --> B2[NavMenu]
        B --> B3[UserProfile]
        B2 --> B2a[Dashboard Link]
        B2 --> B2b[Alerts Link]
        B2 --> B2c[Connectors Link]
        B2 --> B2d[Reports Link]
        B2 --> B2e[Settings Link]
    end

    subgraph "Top Bar"
        C --> C1[SearchBar]
        C --> C2[NotificationBell]
        C --> C3[HelpMenu]
        C --> C4[UserAvatar]
    end

    subgraph "Dashboard Page"
        D --> E[DashboardView]
        E --> E1[FilterBar]
        E --> E2[WidgetGrid]
        E --> E3[ActionBar]
    end

    subgraph "Widget Grid"
        E2 --> W1[MetricCard]
        E2 --> W2[TrendChart]
        E2 --> W3[PieChart]
        E2 --> W4[DataTable]
        E2 --> W5[AlertsList]
        E2 --> W6[MapWidget]
    end

    subgraph "Widget Components"
        W1 --> W1a[KPIValue]
        W1 --> W1b[TrendIndicator]
        W1 --> W1c[Sparkline]

        W2 --> W2a[XAxis]
        W2 --> W2b[YAxis]
        W2 --> W2c[Legend]
        W2 --> W2d[Tooltip]
        W2 --> W2e[DataSeries]

        W4 --> W4a[TableHeader]
        W4 --> W4b[TableBody]
        W4 --> W4c[Pagination]
        W4 --> W4d[RowActions]
    end

    classDef shell fill:#E2E8F0,stroke:#333
    classDef nav fill:#93C5FD,stroke:#333
    classDef widget fill:#86EFAC,stroke:#333
    classDef chart fill:#FCD34D,stroke:#333

    class A,B,C,D shell
    class B1,B2,B2a,B2b,B2c,B2d,B2e,B3 nav
    class W1,W2,W3,W4,W5,W6 widget
    class W1a,W1b,W1c,W2a,W2b,W2c,W2d,W2e chart
```

<!-- SVG: 01-dashboard-hierarchy-1.svg -->
![Diagram 1](../../diagrams-svg/components/01-dashboard-hierarchy-1.svg)


## Page Component Hierarchy

```mermaid
graph LR
    subgraph "Dashboard Types"
        D1[Security Posture]
        D2[Vulnerability]
        D3[Compliance]
        D4[Alert Center]
        D5[Asset Management]
        D6[Risk Overview]
        D7[Executive Summary]
    end

    subgraph "Shared Components"
        S1[DateRangePicker]
        S2[ConnectorFilter]
        S3[SeverityFilter]
        S4[ExportButton]
        S5[RefreshButton]
        S6[FullscreenToggle]
    end

    D1 --> S1
    D1 --> S2
    D2 --> S1
    D2 --> S3
    D3 --> S1
    D3 --> S2
    D4 --> S1
    D4 --> S3
    D5 --> S2
    D6 --> S1
    D6 --> S2
    D7 --> S1

    D1 --> S4
    D2 --> S4
    D3 --> S4
    D4 --> S5
    D7 --> S6
```

<!-- SVG: 01-dashboard-hierarchy-2.svg -->
![Diagram 2](../../diagrams-svg/components/01-dashboard-hierarchy-2.svg)


## Component State Flow

```mermaid
stateDiagram-v2
    [*] --> Loading: Page Load
    Loading --> Error: API Failed
    Loading --> Empty: No Data
    Loading --> Populated: Data Received

    Error --> Loading: Retry
    Empty --> Populated: Data Added
    Populated --> Loading: Refresh
    Populated --> Filtered: Apply Filter
    Filtered --> Populated: Clear Filter

    Populated --> DrillDown: Click Widget
    DrillDown --> Populated: Back
    DrillDown --> DetailView: Select Item
    DetailView --> DrillDown: Back
```

<!-- SVG: 01-dashboard-hierarchy-3.svg -->
![Diagram 3](../../diagrams-svg/components/01-dashboard-hierarchy-3.svg)


## Component Library Structure

| Category | Components | Platform Alignment |
|----------|------------|-------------------|
| Layout | AppShell, Sidebar, TopBar, Grid | MUI + Custom |
| Navigation | NavMenu, Breadcrumb, Tabs | MUI Tabs |
| Data Display | Card, Table, List, Badge | MUI + Custom |
| Charts | Line, Bar, Pie, Area, Scatter | Recharts |
| Forms | Input, Select, DatePicker, Checkbox | MUI Forms |
| Feedback | Alert, Toast, Modal, Drawer | MUI + Sonner |
| Actions | Button, IconButton, Menu, Tooltip | MUI Actions |

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
