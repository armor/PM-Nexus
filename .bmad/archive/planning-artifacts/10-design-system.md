# Nexus UI Uplift - UX/Design System

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Alignment:** MUI v7 + Tailwind + Platform Standards

---

## 1. Overview

This document defines the UX and design system for Nexus UI Uplift, ensuring visual consistency, accessibility compliance, and enterprise-grade presentation.

### Design Principles

1. **Clarity First** - Information hierarchy guides decision-making
2. **Consistency** - Predictable patterns reduce cognitive load
3. **Accessibility** - WCAG 2.1 AA compliance mandatory
4. **Enterprise Polish** - Professional appearance builds trust
5. **Dark-First** - Optimized for security operations environments

---

## 2. Color System

### 2.1 Primary Palette (Dark Theme)

| Token | Hex | Usage |
|-------|-----|-------|
| `background.default` | `#0F172A` | Page background |
| `background.paper` | `#1E293B` | Card/container background |
| `background.elevated` | `#334155` | Hover states, dropdowns |
| `text.primary` | `#F8FAFC` | Primary text |
| `text.secondary` | `#94A3B8` | Secondary/muted text |
| `text.disabled` | `#64748B` | Disabled text |
| `divider` | `#334155` | Borders, separators |

### 2.2 Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary.main` | `#3B82F6` | Primary actions, links |
| `primary.light` | `#60A5FA` | Hover states |
| `primary.dark` | `#2563EB` | Active states |
| `secondary.main` | `#8B5CF6` | Secondary actions |

### 2.3 Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `success.main` | `#10B981` | Success states, positive |
| `warning.main` | `#F59E0B` | Warnings, caution |
| `error.main` | `#EF4444` | Errors, critical |
| `info.main` | `#3B82F6` | Information |

### 2.4 Severity Colors

| Severity | Hex | Background | Usage |
|----------|-----|------------|-------|
| Critical | `#DC2626` | `#7F1D1D` | Highest priority alerts |
| High | `#EA580C` | `#7C2D12` | Important issues |
| Medium | `#CA8A04` | `#713F12` | Moderate concerns |
| Low | `#16A34A` | `#14532D` | Minor items |
| Info | `#2563EB` | `#1E3A8A` | Informational |

---

## 3. Typography

### 3.1 Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
font-family-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
```

### 3.2 Type Scale

| Variant | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| `h1` | 2.5rem (40px) | 700 | 1.2 | Page titles |
| `h2` | 2rem (32px) | 600 | 1.25 | Section headers |
| `h3` | 1.5rem (24px) | 600 | 1.3 | Card titles |
| `h4` | 1.25rem (20px) | 600 | 1.4 | Sub-sections |
| `h5` | 1rem (16px) | 600 | 1.5 | Widget titles |
| `h6` | 0.875rem (14px) | 600 | 1.5 | Small headers |
| `body1` | 1rem (16px) | 400 | 1.5 | Body text |
| `body2` | 0.875rem (14px) | 400 | 1.5 | Secondary text |
| `caption` | 0.75rem (12px) | 400 | 1.5 | Captions, labels |
| `button` | 0.875rem (14px) | 600 | 1 | Button text |
| `code` | 0.875rem (14px) | 400 | 1.5 | Code snippets |

### 3.3 Usage Guidelines

```typescript
// Page title
<Typography variant="h1">Dashboard</Typography>

// Section header
<Typography variant="h3" component="h2">Recent Alerts</Typography>

// Card title
<Typography variant="h5">Alert Details</Typography>

// Body text
<Typography variant="body1">Description text here</Typography>

// Secondary/muted
<Typography variant="body2" color="text.secondary">
  Updated 5 minutes ago
</Typography>
```

---

## 4. Spacing System

### 4.1 Base Unit

Base spacing unit: **8px**

### 4.2 Spacing Scale

| Token | Value | Pixels | Usage |
|-------|-------|--------|-------|
| `0` | 0 | 0px | None |
| `0.5` | 0.5 | 4px | Tight spacing |
| `1` | 1 | 8px | Compact elements |
| `2` | 2 | 16px | Standard padding |
| `3` | 3 | 24px | Section spacing |
| `4` | 4 | 32px | Large gaps |
| `6` | 6 | 48px | Section breaks |
| `8` | 8 | 64px | Major sections |

### 4.3 Usage

```typescript
// MUI sx prop
<Box sx={{ p: 2, m: 1, gap: 2 }}>
  {/* padding: 16px, margin: 8px, gap: 16px */}
</Box>

// Tailwind classes
<div className="p-4 m-2 gap-4">
  {/* padding: 16px, margin: 8px, gap: 16px */}
</div>
```

---

## 5. Grid & Layout

### 5.1 Page Layout

```
┌──────────────────────────────────────────────────────────┐
│  TopBar (64px height, fixed)                             │
├──────────┬───────────────────────────────────────────────┤
│          │                                               │
│  Sidebar │               Main Content                    │
│  (240px) │           (fluid, padding: 24px)              │
│  fixed   │                                               │
│          │                                               │
│          │                                               │
│          │                                               │
└──────────┴───────────────────────────────────────────────┘
```

### 5.2 Breakpoints

| Breakpoint | Width | Columns | Usage |
|------------|-------|---------|-------|
| `xs` | 0-599px | 4 | Mobile (sidebar collapsed) |
| `sm` | 600-899px | 8 | Tablet portrait |
| `md` | 900-1199px | 12 | Tablet landscape |
| `lg` | 1200-1535px | 12 | Desktop |
| `xl` | 1536px+ | 12 | Large desktop |

### 5.3 Dashboard Grid

```typescript
<Grid container spacing={3}>
  {/* Full width metric bar */}
  <Grid item xs={12}>
    <MetricBar />
  </Grid>

  {/* Main content (8 cols) + sidebar (4 cols) */}
  <Grid item xs={12} lg={8}>
    <AlertList />
  </Grid>
  <Grid item xs={12} lg={4}>
    <QuickActions />
  </Grid>

  {/* Three equal columns */}
  <Grid item xs={12} md={4}>
    <Widget1 />
  </Grid>
  <Grid item xs={12} md={4}>
    <Widget2 />
  </Grid>
  <Grid item xs={12} md={4}>
    <Widget3 />
  </Grid>
</Grid>
```

---

## 6. Component Patterns

### 6.1 Cards

```typescript
// Standard card
<Card sx={{ bgcolor: "background.paper", borderRadius: 2 }}>
  <CardContent sx={{ p: 3 }}>
    <Typography variant="h5" gutterBottom>
      Card Title
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Card content
    </Typography>
  </CardContent>
</Card>

// Clickable card
<Card
  sx={{
    bgcolor: "background.paper",
    cursor: "pointer",
    "&:hover": {
      bgcolor: "background.elevated",
    },
  }}
>
  ...
</Card>

// Card with left border accent
<Card
  sx={{
    borderLeft: 4,
    borderColor: "error.main", // severity color
  }}
>
  ...
</Card>
```

### 6.2 Buttons

```typescript
// Primary action
<Button variant="contained" color="primary">
  Save Changes
</Button>

// Secondary action
<Button variant="outlined">
  Cancel
</Button>

// Destructive action
<Button variant="contained" color="error">
  Delete
</Button>

// Icon button
<IconButton aria-label="settings">
  <SettingsIcon />
</IconButton>
```

### 6.3 Status Indicators

```typescript
// Chip for status
<Chip
  label="Critical"
  size="small"
  sx={{
    bgcolor: "error.dark",
    color: "error.contrastText",
  }}
/>

// Badge for counts
<Badge badgeContent={5} color="error">
  <NotificationIcon />
</Badge>

// Status dot
<Box
  sx={{
    width: 8,
    height: 8,
    borderRadius: "50%",
    bgcolor: "success.main",
  }}
/>
```

### 6.4 Data Tables

```typescript
<DataTable
  columns={[
    { field: "title", header: "Alert", sortable: true },
    { field: "severity", header: "Severity", sortable: true },
    { field: "status", header: "Status", filterable: true },
    { field: "createdAt", header: "Created", sortable: true },
  ]}
  data={alerts}
  loading={isLoading}
  pagination={{ page, limit, total }}
  onSort={handleSort}
  onFilter={handleFilter}
  onPageChange={handlePageChange}
  emptyState={<EmptyState message="No alerts found" />}
/>
```

---

## 7. Forms

### 7.1 Form Layout

```typescript
<form onSubmit={handleSubmit}>
  <Stack spacing={3}>
    {/* Form fields */}
    <RHFInput
      name="title"
      label="Alert Title"
      required
      helperText="Enter a descriptive title"
    />

    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <RHFSelect name="severity" label="Severity" required>
          <MenuItem value="critical">Critical</MenuItem>
          <MenuItem value="high">High</MenuItem>
          <MenuItem value="medium">Medium</MenuItem>
          <MenuItem value="low">Low</MenuItem>
        </RHFSelect>
      </Grid>
      <Grid item xs={12} md={6}>
        <RHFSelect name="status" label="Status" required>
          <MenuItem value="open">Open</MenuItem>
          <MenuItem value="acknowledged">Acknowledged</MenuItem>
        </RHFSelect>
      </Grid>
    </Grid>

    <RHFTextarea
      name="description"
      label="Description"
      rows={4}
    />

    {/* Form actions */}
    <Stack direction="row" spacing={2} justifyContent="flex-end">
      <Button variant="outlined" onClick={onCancel}>
        Cancel
      </Button>
      <Button variant="contained" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Save"}
      </Button>
    </Stack>
  </Stack>
</form>
```

### 7.2 Validation States

```typescript
// Error state
<TextField
  error
  helperText="Title is required"
  label="Title"
/>

// Success state (after save)
<TextField
  label="Title"
  InputProps={{
    endAdornment: <CheckIcon color="success" />,
  }}
/>

// Loading state
<TextField
  label="Title"
  disabled
  InputProps={{
    endAdornment: <CircularProgress size={20} />,
  }}
/>
```

---

## 8. Loading States

### 8.1 Skeleton Loaders

```typescript
// Card skeleton
<Card sx={{ p: 3 }}>
  <Skeleton variant="text" width="60%" height={32} />
  <Skeleton variant="text" width="80%" />
  <Skeleton variant="rectangular" height={200} sx={{ mt: 2 }} />
</Card>

// Table skeleton
<TableRow>
  <TableCell><Skeleton /></TableCell>
  <TableCell><Skeleton /></TableCell>
  <TableCell><Skeleton /></TableCell>
  <TableCell><Skeleton width={100} /></TableCell>
</TableRow>
```

### 8.2 Loading Overlays

```typescript
// Full page loading
<Box
  sx={{
    position: "fixed",
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    bgcolor: "background.default",
    zIndex: 9999,
  }}
>
  <CircularProgress />
</Box>

// Section loading
<Box sx={{ position: "relative" }}>
  {isLoading && (
    <Box
      sx={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "rgba(15, 23, 42, 0.8)",
        zIndex: 10,
      }}
    >
      <CircularProgress />
    </Box>
  )}
  <Content />
</Box>
```

---

## 9. Empty & Error States

### 9.1 Empty State

```typescript
<Box
  sx={{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    py: 8,
    textAlign: "center",
  }}
>
  <InboxIcon sx={{ fontSize: 64, color: "text.disabled", mb: 2 }} />
  <Typography variant="h6" gutterBottom>
    No alerts found
  </Typography>
  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
    Try adjusting your filters or check back later
  </Typography>
  <Button variant="outlined" onClick={onClearFilters}>
    Clear Filters
  </Button>
</Box>
```

### 9.2 Error State

```typescript
<Box
  sx={{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    py: 8,
    textAlign: "center",
  }}
>
  <ErrorIcon sx={{ fontSize: 64, color: "error.main", mb: 2 }} />
  <Typography variant="h6" gutterBottom>
    Unable to load alerts
  </Typography>
  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
    {error.message}
  </Typography>
  <Button variant="contained" onClick={onRetry}>
    Try Again
  </Button>
</Box>
```

---

## 10. Navigation

### 10.1 Sidebar Navigation

```typescript
const navItems = [
  { icon: DashboardIcon, label: "Dashboard", path: "/" },
  { icon: AlertIcon, label: "Alerts", path: "/alerts" },
  { icon: AssetIcon, label: "Assets", path: "/assets" },
  { icon: VulnIcon, label: "Vulnerabilities", path: "/vulnerabilities" },
  { icon: ComplianceIcon, label: "Compliance", path: "/compliance" },
  { icon: ReportsIcon, label: "Reports", path: "/reports" },
  { icon: SettingsIcon, label: "Settings", path: "/settings" },
];

// Active state
<ListItemButton
  selected={isActive}
  sx={{
    borderRadius: 1,
    "&.Mui-selected": {
      bgcolor: "primary.main",
      "&:hover": { bgcolor: "primary.dark" },
    },
  }}
>
  <ListItemIcon>{item.icon}</ListItemIcon>
  <ListItemText primary={item.label} />
</ListItemButton>
```

### 10.2 Breadcrumbs

```typescript
<Breadcrumbs aria-label="breadcrumb">
  <Link href="/" color="inherit">
    Dashboard
  </Link>
  <Link href="/alerts" color="inherit">
    Alerts
  </Link>
  <Typography color="text.primary">
    Alert Details
  </Typography>
</Breadcrumbs>
```

---

## 11. Accessibility

### 11.1 Requirements (WCAG 2.1 AA)

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.4.3 | 4.5:1 contrast | Color tokens verified |
| 2.1.1 | Keyboard accessible | All interactive elements |
| 2.4.4 | Link purpose clear | Descriptive link text |
| 2.4.7 | Focus visible | Focus ring on all elements |
| 4.1.2 | ARIA attributes | Proper roles and labels |

### 11.2 Focus States

```typescript
// Global focus style
const theme = createTheme({
  components: {
    MuiButtonBase: {
      styleOverrides: {
        root: {
          "&:focus-visible": {
            outline: "2px solid #3B82F6",
            outlineOffset: "2px",
          },
        },
      },
    },
  },
});
```

### 11.3 ARIA Patterns

```typescript
// Accessible button
<Button aria-label="Delete alert">
  <DeleteIcon />
</Button>

// Live region for updates
<Box role="status" aria-live="polite">
  {message}
</Box>

// Modal dialog
<Dialog
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <DialogTitle id="dialog-title">Confirm Delete</DialogTitle>
  <DialogContent id="dialog-description">
    Are you sure?
  </DialogContent>
</Dialog>

// Navigation landmark
<nav aria-label="Main navigation">
  {/* Nav content */}
</nav>
```

---

## 12. Responsive Design

### 12.1 Breakpoint Behavior

| Element | xs-sm | md | lg+ |
|---------|-------|-----|-----|
| Sidebar | Collapsed (drawer) | Collapsed | Expanded (240px) |
| Grid columns | Stack (12) | 2-3 columns | 3-4 columns |
| Table | Card view | Horizontal scroll | Full table |
| Typography | Scaled down 10% | Normal | Normal |

### 12.2 Responsive Patterns

```typescript
// Hide on mobile
<Box sx={{ display: { xs: "none", md: "block" } }}>
  Desktop content
</Box>

// Stack to row
<Stack
  direction={{ xs: "column", md: "row" }}
  spacing={2}
>
  {children}
</Stack>

// Responsive padding
<Box sx={{ p: { xs: 2, md: 3, lg: 4 } }}>
  {content}
</Box>
```

---

## 13. Animation & Motion

### 13.1 Transition Tokens

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| `fast` | 150ms | ease-out | Hover, focus |
| `normal` | 250ms | ease-in-out | Modals, dropdowns |
| `slow` | 350ms | ease-in-out | Page transitions |

### 13.2 Animation Patterns

```typescript
// Fade in
<Fade in={visible} timeout={250}>
  <Box>{content}</Box>
</Fade>

// Slide in
<Slide direction="up" in={visible} timeout={250}>
  <Box>{content}</Box>
</Slide>

// Skeleton to content
<Box
  sx={{
    transition: "opacity 250ms ease-in-out",
    opacity: isLoading ? 0 : 1,
  }}
>
  {content}
</Box>
```

---

## 14. Charts & Data Visualization

### 14.1 Chart Colors

```typescript
const chartColors = [
  "#3B82F6", // Primary blue
  "#8B5CF6", // Purple
  "#10B981", // Green
  "#F59E0B", // Amber
  "#EF4444", // Red
  "#06B6D4", // Cyan
  "#EC4899", // Pink
  "#6366F1", // Indigo
];
```

### 14.2 Chart Patterns

```typescript
// Trend line chart
<LineChart
  data={trendData}
  xAxis={{ dataKey: "date" }}
  yAxis={{ width: 60 }}
  colors={chartColors}
  height={300}
/>

// Severity donut
<DonutChart
  data={severityData}
  colors={{
    critical: "#DC2626",
    high: "#EA580C",
    medium: "#CA8A04",
    low: "#16A34A",
  }}
  innerRadius={60}
  outerRadius={80}
/>
```

---

## 15. Design Checklist

Before any design is considered complete:

- [ ] Color contrast meets 4.5:1 ratio
- [ ] All interactive elements keyboard accessible
- [ ] Focus states visible and consistent
- [ ] ARIA labels on all icons/buttons
- [ ] Loading states implemented
- [ ] Error states designed
- [ ] Empty states designed
- [ ] Responsive behavior defined
- [ ] Dark theme colors verified
- [ ] Typography hierarchy clear
- [ ] Spacing consistent (8px grid)
- [ ] Storybook story created

---

*This design system is maintained by the Design team. Updates require review.*
