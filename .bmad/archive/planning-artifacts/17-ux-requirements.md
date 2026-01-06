# Nexus UX Requirements Specification

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Complete

---

## Executive Summary

This document specifies comprehensive UX requirements for the Nexus platform based on gap analysis of the existing platform submodule. It covers onboarding tours, tooltips, help menus, chart interactivity, behavior tracking, and in-app support.

---

## 1. Onboarding & Product Tours

### 1.1 Current State
**Gap Analysis:** No tour/onboarding system currently exists in the platform.

### 1.2 Requirements

#### Library Selection
**Recommended:** `react-joyride` (MIT License, 6k+ GitHub stars, actively maintained)

**Installation:**
```bash
npm install react-joyride
```

#### Tour Types Required

| Tour Type | Trigger | Target Users | Duration |
|-----------|---------|--------------|----------|
| Welcome Tour | First login | New users | 2-3 min |
| Feature Tour | New feature release | All users | 30 sec |
| Workflow Tour | Role-based first access | Role-specific | 1-2 min |
| Contextual Tour | Help icon click | On-demand | Variable |

#### Tour Specifications

**1. Welcome Tour Steps:**
```typescript
const welcomeTourSteps: Step[] = [
  {
    target: '[data-tour="sidebar-nav"]',
    content: 'Navigate between dashboards, alerts, connectors, and settings',
    placement: 'right',
    disableBeacon: true
  },
  {
    target: '[data-tour="security-score"]',
    content: 'Your overall security posture at a glance. Click to drill down.',
    placement: 'bottom'
  },
  {
    target: '[data-tour="alerts-widget"]',
    content: 'Active security alerts requiring your attention',
    placement: 'left'
  },
  {
    target: '[data-tour="connectors"]',
    content: 'Configure your security tool integrations here',
    placement: 'bottom'
  },
  {
    target: '[data-tour="help-menu"]',
    content: 'Get help, submit feedback, or contact support',
    placement: 'left'
  }
];
```

**2. Dashboard-Specific Tours:**
- Security Posture Dashboard
- Vulnerability Dashboard
- Compliance Dashboard
- Alert Center
- Asset Management

**3. Tour Progress Persistence:**
```typescript
interface TourProgress {
  userId: string;
  completedTours: string[];
  dismissedTours: string[];
  currentStep: { tourId: string; stepIndex: number } | null;
  firstLoginAt: ISO8601DateTime;
  lastTourAt: ISO8601DateTime;
}
```

### 1.3 Implementation Requirements

```typescript
// TourProvider component wrapper
import Joyride, { CallBackProps, STATUS } from 'react-joyride';

interface TourProviderProps {
  children: React.ReactNode;
}

export function TourProvider({ children }: TourProviderProps) {
  const [runTour, setRunTour] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);

  const handleTourCallback = (data: CallBackProps) => {
    const { status, index, type } = data;

    // Track tour progress
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status as any)) {
      trackTourCompletion(currentTourId, status);
    }

    // Track step views
    if (type === 'step:after') {
      trackTourStep(currentTourId, index);
    }
  };

  return (
    <TourContext.Provider value={{ startTour, endTour }}>
      {children}
      <Joyride
        steps={steps}
        run={runTour}
        continuous
        showProgress
        showSkipButton
        callback={handleTourCallback}
        styles={{
          options: {
            primaryColor: '#0066CC', // Platform primary
            zIndex: 10000
          }
        }}
      />
    </TourContext.Provider>
  );
}
```

---

## 2. Tooltip & Help System

### 2.1 Current State
**Gap Analysis:**
- `HelpTooltip` component exists but underutilized
- IconButtons throughout codebase lack `aria-label` attributes
- No consistent tooltip pattern

### 2.2 Requirements

#### Accessibility-First IconButton Wrapper

```typescript
// Required: All IconButtons must use this wrapper
interface AccessibleIconButtonProps extends IconButtonProps {
  'aria-label': string; // REQUIRED - not optional
  tooltip?: string;      // If different from aria-label
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right';
}

export function AccessibleIconButton({
  'aria-label': ariaLabel,
  tooltip,
  tooltipPlacement = 'top',
  children,
  ...props
}: AccessibleIconButtonProps) {
  return (
    <Tooltip title={tooltip || ariaLabel} placement={tooltipPlacement}>
      <IconButton aria-label={ariaLabel} {...props}>
        {children}
      </IconButton>
    </Tooltip>
  );
}
```

**Files Requiring Updates:**
- `DataListFooter.tsx` (lines 71, 81, 120, 129)
- `AppBar.tsx` (line 46)
- `DataList.tsx` (multiple instances)
- All form components with icon actions

#### Form Field Tooltip Pattern

```typescript
// Standard pattern for form field help
interface FormFieldProps {
  label: string;
  hint?: string;           // Short helper text below field
  helpTooltip?: string;    // Detailed tooltip on info icon
  helpLink?: {
    text: string;
    url: string;
  };
}

<FormControl>
  <Box display="flex" alignItems="center" gap={0.5}>
    <FormLabel>{label}</FormLabel>
    {helpTooltip && (
      <HelpTooltip content={helpTooltip} />
    )}
  </Box>
  <Input {...inputProps} />
  {hint && <FormHelperText>{hint}</FormHelperText>}
  {helpLink && (
    <Link href={helpLink.url} target="_blank" sx={{ fontSize: 'xs' }}>
      {helpLink.text}
    </Link>
  )}
</FormControl>
```

#### Tooltip Content Guidelines

| Element Type | Tooltip Requirement | Example |
|--------------|---------------------|---------|
| Icon buttons | Required | "Edit alert rule" |
| Form fields | Optional (hint preferred) | "Enter IP in CIDR format" |
| Charts | Required on data points | "45 critical vulnerabilities" |
| Metrics | Required with trend | "Security score: 85 (+5 from last week)" |
| Abbreviations | Required | "CVSS: Common Vulnerability Scoring System" |

### 2.3 Help Menu Implementation

```typescript
// Global help menu component
interface HelpMenuProps {
  variant: 'sidebar' | 'topbar' | 'floating';
}

export function HelpMenu({ variant }: HelpMenuProps) {
  const menuItems: HelpMenuItem[] = [
    {
      icon: <BookOpen />,
      label: 'Documentation',
      action: () => openDocs('/'),
      shortcut: 'Ctrl+Shift+?'
    },
    {
      icon: <Video />,
      label: 'Video Tutorials',
      action: () => openDocs('/tutorials'),
    },
    {
      icon: <MessageCircle />,
      label: 'Live Chat Support',
      action: () => openChat(),
      badge: 'Online'
    },
    {
      icon: <Ticket />,
      label: 'Submit Support Ticket',
      action: () => openTicketForm(),
    },
    {
      icon: <Compass />,
      label: 'Take a Tour',
      action: () => startTour('welcome'),
    },
    {
      icon: <Keyboard />,
      label: 'Keyboard Shortcuts',
      action: () => openShortcuts(),
      shortcut: '?'
    },
    {
      icon: <MessageSquare />,
      label: 'Give Feedback',
      action: () => openFeedback(),
    }
  ];

  return (
    <Menu>
      <MenuButton>
        <HelpCircle />
      </MenuButton>
      <MenuList>
        {menuItems.map(item => (
          <MenuItem key={item.label} onClick={item.action}>
            {item.icon}
            <span>{item.label}</span>
            {item.badge && <Badge>{item.badge}</Badge>}
            {item.shortcut && <Kbd>{item.shortcut}</Kbd>}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
}
```

---

## 3. Chart & Graph Requirements

### 3.1 Current State
**Gap Analysis:**
- Using Nivo charting library
- Arc labels disabled on pie charts
- No drill-through capability
- Inconsistent axis labeling

### 3.2 Requirements

#### Axis and Legend Standards

**All charts MUST include:**

| Element | Requirement | Implementation |
|---------|-------------|----------------|
| X-Axis Label | Required | Clear description of dimension |
| Y-Axis Label | Required | Unit of measurement |
| Legend | Required if >1 series | Interactive (click to toggle) |
| Tooltips | Required | Detailed data on hover |
| Grid lines | Optional | Subtle, not distracting |

**Axis Label Format:**
```typescript
// Standard axis configuration
const axisConfig = {
  axisLeft: {
    tickSize: 5,
    tickPadding: 5,
    tickRotation: 0,
    legend: 'Count', // REQUIRED
    legendPosition: 'middle' as const,
    legendOffset: -45,
    format: (value: number) => formatNumber(value)
  },
  axisBottom: {
    tickSize: 5,
    tickPadding: 5,
    tickRotation: -45,
    legend: 'Date', // REQUIRED
    legendPosition: 'middle' as const,
    legendOffset: 40,
    format: (value: string) => formatDate(value)
  }
};
```

#### Drill-Through Requirements

**All aggregated chart data MUST support drill-through:**

```typescript
// Pie chart with drill-through
interface DrillablePieChartProps {
  data: PieChartData[];
  onSegmentClick: (datum: PieChartData) => void;
  drillPath?: DrillPath[];
}

export function DrillablePieChart({
  data,
  onSegmentClick,
  drillPath = []
}: DrillablePieChartProps) {
  return (
    <Box>
      {/* Breadcrumb for drill path */}
      {drillPath.length > 0 && (
        <Breadcrumb>
          <BreadcrumbItem onClick={() => resetDrill()}>
            All
          </BreadcrumbItem>
          {drillPath.map((level, idx) => (
            <BreadcrumbItem
              key={idx}
              onClick={() => drillToLevel(idx)}
            >
              {level.label}
            </BreadcrumbItem>
          ))}
        </Breadcrumb>
      )}

      <ResponsivePie
        data={data}
        onClick={onSegmentClick} // REQUIRED
        enableArcLabels={true}    // REQUIRED
        arcLabel={(d) => `${d.id}: ${formatNumber(d.value)}`}
        arcLabelsSkipAngle={10}
        tooltip={({ datum }) => (
          <ChartTooltip>
            <strong>{datum.id}</strong>
            <span>{formatNumber(datum.value)} ({datum.formattedValue})</span>
            <span className="drill-hint">Click to view details</span>
          </ChartTooltip>
        )}
        // ... other props
      />
    </Box>
  );
}
```

**Drill-Through Navigation Pattern:**
```
Level 1: Summary (e.g., "Critical: 45")
  → Click →
Level 2: Category breakdown (e.g., "By Source: CrowdStrike: 20, Tenable: 25")
  → Click →
Level 3: Individual items (e.g., List of 20 specific vulnerabilities)
  → Click →
Level 4: Detail view (e.g., Full vulnerability record)
```

#### Arc Labels and Data Labels

```typescript
// Required arc label configuration for pie charts
const pieChartConfig = {
  enableArcLabels: true,  // REQUIRED - was false
  arcLabel: (d: Datum) => `${d.value}`,
  arcLabelsSkipAngle: 10, // Skip label if arc too small
  arcLabelsTextColor: {
    from: 'color',
    modifiers: [['darker', 2]]
  },
  arcLabelsRadiusOffset: 0.55
};
```

#### Interactive Legend

```typescript
// Legend with show/hide capability
interface InteractiveLegendProps {
  items: LegendItem[];
  onToggle: (id: string) => void;
  hiddenIds: Set<string>;
}

export function InteractiveLegend({
  items,
  onToggle,
  hiddenIds
}: InteractiveLegendProps) {
  return (
    <Box display="flex" flexWrap="wrap" gap={1}>
      {items.map(item => (
        <Chip
          key={item.id}
          label={item.label}
          onClick={() => onToggle(item.id)}
          sx={{
            backgroundColor: hiddenIds.has(item.id)
              ? 'gray.200'
              : item.color,
            opacity: hiddenIds.has(item.id) ? 0.5 : 1,
            cursor: 'pointer'
          }}
        />
      ))}
    </Box>
  );
}
```

---

## 4. Behavior Tracking Requirements

### 4.1 Recommended Tooling

**Primary Recommendation:** PostHog (Open Source, Self-Hosted Option)

| Feature | PostHog | Mixpanel | Amplitude |
|---------|---------|----------|-----------|
| License | MIT | Proprietary | Proprietary |
| Self-hosted | Yes | No | No |
| Free tier | 1M events/mo | 20M events/mo | 10M events/mo |
| Session recording | Yes | Yes | Yes |
| Heatmaps | Yes | No | No |
| Feature flags | Yes | No | Yes |

**Installation:**
```bash
npm install posthog-js
```

### 4.2 Event Tracking Specification

#### Core Events

| Event Name | When Tracked | Properties |
|------------|--------------|------------|
| `page_view` | Page load | path, referrer, title |
| `feature_used` | Feature interaction | feature_id, context |
| `form_submitted` | Form submission | form_id, success, errors |
| `error_occurred` | JS error | message, stack, context |
| `tour_started` | Tour begins | tour_id |
| `tour_completed` | Tour finishes | tour_id, steps_completed |
| `help_accessed` | Help menu used | help_type, context |
| `chart_drilled` | Chart drill-through | chart_id, from_level, to_level |
| `alert_actioned` | Alert workflow action | alert_id, action_type |
| `search_performed` | Search executed | query, results_count |

#### Implementation Pattern

```typescript
// Tracking hook
function useTracking() {
  const posthog = usePostHog();
  const user = useCurrentUser();

  return {
    track: (event: string, properties?: Record<string, unknown>) => {
      posthog.capture(event, {
        ...properties,
        $set: {
          user_role: user.role,
          organization_id: user.orgId
        }
      });
    },

    trackPageView: (pageName: string) => {
      posthog.capture('$pageview', {
        page_name: pageName,
        path: window.location.pathname
      });
    },

    trackFeatureUsage: (featureId: string, context?: string) => {
      posthog.capture('feature_used', {
        feature_id: featureId,
        context
      });
    }
  };
}
```

### 4.3 Funnel Analysis Requirements

**Critical User Funnels to Track:**

```typescript
const funnels = {
  onboarding: [
    'sign_up_started',
    'account_created',
    'first_connector_added',
    'first_dashboard_viewed',
    'first_action_taken'
  ],

  alertWorkflow: [
    'alert_list_viewed',
    'alert_opened',
    'alert_investigated',
    'alert_actioned',
    'alert_resolved'
  ],

  connectorSetup: [
    'connectors_page_viewed',
    'add_connector_clicked',
    'connector_selected',
    'credentials_entered',
    'connector_tested',
    'connector_saved'
  ],

  reportGeneration: [
    'reports_page_viewed',
    'report_type_selected',
    'report_configured',
    'report_generated',
    'report_downloaded'
  ]
};
```

### 4.4 Session Recording

```typescript
// Session recording configuration
posthog.init(POSTHOG_KEY, {
  api_host: POSTHOG_HOST,
  session_recording: {
    maskAllInputs: true,         // Privacy
    maskInputFn: (text, element) => {
      // Mask sensitive fields
      if (element?.matches('input[type="password"], [data-sensitive]')) {
        return '***';
      }
      return text;
    }
  },
  capture_pageview: false,       // Manual control
  capture_pageleave: true
});
```

---

## 5. In-App Support

### 5.1 Current State
**Gap Analysis:** Basic ticket widget exists, links to external Atlassian portal.

### 5.2 Requirements

#### Live Chat Widget

**Recommended:** Chatwoot (Open Source, Self-Hosted)

```typescript
// Chat widget integration
interface ChatWidgetProps {
  userId: string;
  userEmail: string;
  userName: string;
  organizationId: string;
}

export function ChatWidget({ userId, userEmail, userName, organizationId }: ChatWidgetProps) {
  useEffect(() => {
    window.chatwootSettings = {
      hideMessageBubble: false,
      position: 'right',
      locale: 'en',
      type: 'expanded_bubble',
      launcherTitle: 'Chat with Support'
    };

    window.chatwootSDK.run({
      websiteToken: CHATWOOT_TOKEN,
      baseUrl: CHATWOOT_URL
    });

    // Set user context
    window.$chatwoot.setUser(userId, {
      email: userEmail,
      name: userName,
      organization_id: organizationId
    });
  }, []);

  return null;
}
```

#### Contextual Support

```typescript
// Context-aware support component
interface ContextualSupportProps {
  context: 'dashboard' | 'connector' | 'alert' | 'settings';
  entityId?: string;
}

export function ContextualSupport({ context, entityId }: ContextualSupportProps) {
  const supportContent = useSupportContent(context);

  return (
    <Box>
      <Typography variant="h6">Need Help?</Typography>

      {/* Quick Help Articles */}
      <List>
        {supportContent.articles.map(article => (
          <ListItem
            key={article.id}
            onClick={() => openArticle(article.url)}
          >
            <ListItemIcon><FileText /></ListItemIcon>
            <ListItemText primary={article.title} />
          </ListItem>
        ))}
      </List>

      {/* Related Videos */}
      {supportContent.videos.length > 0 && (
        <Box>
          <Typography variant="subtitle2">Video Tutorials</Typography>
          {supportContent.videos.map(video => (
            <VideoThumbnail key={video.id} video={video} />
          ))}
        </Box>
      )}

      {/* Contact Options */}
      <Box display="flex" gap={1} mt={2}>
        <Button onClick={openChat} startIcon={<MessageCircle />}>
          Chat Now
        </Button>
        <Button onClick={openTicket} startIcon={<Ticket />} variant="outlined">
          Create Ticket
        </Button>
      </Box>
    </Box>
  );
}
```

#### Feedback System

```typescript
// In-app feedback widget
interface FeedbackWidgetProps {
  context: string;
  trigger: 'button' | 'modal' | 'inline';
}

export function FeedbackWidget({ context, trigger }: FeedbackWidgetProps) {
  const [feedback, setFeedback] = useState({
    type: 'suggestion' as 'bug' | 'suggestion' | 'praise',
    message: '',
    includeScreenshot: false
  });

  const submitFeedback = async () => {
    const payload = {
      ...feedback,
      context,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      screenshot: feedback.includeScreenshot ? await captureScreenshot() : null
    };

    await api.submitFeedback(payload);
    showToast('Thank you for your feedback!');
  };

  return (
    <Dialog>
      <DialogTitle>Share Your Feedback</DialogTitle>
      <DialogContent>
        <ToggleButtonGroup
          value={feedback.type}
          onChange={(_, value) => setFeedback(f => ({ ...f, type: value }))}
        >
          <ToggleButton value="bug"><Bug /> Report Bug</ToggleButton>
          <ToggleButton value="suggestion"><Lightbulb /> Suggestion</ToggleButton>
          <ToggleButton value="praise"><Heart /> Praise</ToggleButton>
        </ToggleButtonGroup>

        <TextField
          multiline
          rows={4}
          value={feedback.message}
          onChange={(e) => setFeedback(f => ({ ...f, message: e.target.value }))}
          placeholder="Tell us more..."
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={feedback.includeScreenshot}
              onChange={(e) => setFeedback(f => ({
                ...f,
                includeScreenshot: e.target.checked
              }))}
            />
          }
          label="Include screenshot"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={submitFeedback}>Submit Feedback</Button>
      </DialogActions>
    </Dialog>
  );
}
```

---

## 6. Keyboard Shortcuts

### 6.1 Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `?` | Open keyboard shortcuts help |
| `Ctrl+K` | Global search |
| `Ctrl+Shift+?` | Open documentation |
| `G then D` | Go to Dashboard |
| `G then A` | Go to Alerts |
| `G then C` | Go to Connectors |
| `G then S` | Go to Settings |
| `Esc` | Close modal/drawer |

### 6.2 Context Shortcuts

**Dashboard:**
| Shortcut | Action |
|----------|--------|
| `R` | Refresh data |
| `F` | Toggle fullscreen |
| `E` | Export data |

**Alert List:**
| Shortcut | Action |
|----------|--------|
| `J` / `K` | Navigate up/down |
| `O` | Open selected |
| `A` | Assign to me |
| `C` | Close/resolve |

---

## 7. Implementation Priority

### Phase 1 (Weeks 1-2): Foundation
1. **AccessibleIconButton wrapper** - All icon buttons get aria-labels
2. **PostHog integration** - Core event tracking
3. **react-joyride setup** - Tour infrastructure

### Phase 2 (Weeks 3-4): Core UX
4. **Welcome tour** - New user onboarding
5. **Chart drill-through** - All major charts
6. **Help menu** - Global help access

### Phase 3 (Weeks 5-6): Enhancement
7. **Chatwoot integration** - Live chat support
8. **Feedback widget** - In-app feedback
9. **Keyboard shortcuts** - Power user features

### Phase 4 (Weeks 7-8): Polish
10. **Feature tours** - Per-dashboard tours
11. **Session recording** - User behavior analysis
12. **Accessibility audit** - WCAG compliance

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tour completion rate | >70% | Users who finish welcome tour |
| Time to first value | <5 min | Time from login to first action |
| Help article usage | >20% | Users accessing self-service help |
| Support ticket volume | -30% | Reduction in basic "how-to" tickets |
| Feature adoption | +25% | Users discovering advanced features |
| NPS Score | >50 | User satisfaction rating |
| Accessibility score | 100% | Automated a11y audit passing |

---

## Related Documents

- [User Personas & Journeys](./16-user-personas-journeys.md)
- [Component Library](./04-component-library.md)
- [Design System](./10-design-system.md)
- [Testing Strategy](./07-testing-strategy.md)

---

## References

- [react-joyride Documentation](https://react-joyride.com/)
- [PostHog Documentation](https://posthog.com/docs)
- [Chatwoot Documentation](https://www.chatwoot.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

---

## 9. Related Diagrams

### Figure 1: AI Assistant Flow
*Natural language question processing and RAG-based answering.*

> **Diagram:** [AI Assistant](../diagrams/data-flows/04-ai-assistant.md)
>
> Shows the complete AI assistant pipeline:
> - Intent classification
> - RAG context retrieval (vector + keyword search)
> - MCP tool invocation (8 available tools)
> - Claude LLM processing
> - Response generation with citations

### Figure 2: Dashboard Component Hierarchy
*React component structure for dashboard UX.*

> **Diagram:** [Dashboard Hierarchy](../diagrams/components/01-dashboard-hierarchy.md)
>
> Illustrates:
> - App shell structure
> - Navigation patterns
> - Widget grid system
> - Component state flow

---

*This document is maintained by the UX team. Updates require design review.*
