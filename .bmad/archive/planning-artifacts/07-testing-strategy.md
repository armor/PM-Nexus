# Nexus UI Uplift - Quality & Testing Strategy

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Platform Alignment:** Deep E2E testing requirements (MANDATORY)

---

## 1. Overview

This document defines the testing strategy for Nexus UI Uplift, emphasizing **deep verification** of actual system behavior over surface-level UI feedback testing.

### Critical Testing Philosophy

> **"E2E tests MUST verify the system's actual behavior (network requests, database state), NOT just UI feedback. Toasts, loading spinners, and success messages are implementation details that CAN AND WILL LIE."**

---

## 2. Testing Pyramid

```
                    ┌─────────────────┐
                    │       E2E       │  < 10% of tests
                    │   (Playwright)  │  Critical paths only
                    ├─────────────────┤
                    │   Integration   │  ~20% of tests
                    │ (API + Hooks)   │  API contracts
                    ├─────────────────┤
                    │                 │
                    │      Unit       │  ~70% of tests
                    │    (Vitest)     │  Components, utils
                    │                 │
                    └─────────────────┘
```

---

## 3. Testing Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Unit | Vitest + React Testing Library | Components, hooks, utilities |
| Integration | Vitest + MSW | API hooks, data transformations |
| E2E | Playwright | User journeys, critical paths |
| Visual | Chromatic (Storybook) | Visual regression |
| Accessibility | jest-axe + Playwright | WCAG compliance |
| Performance | Lighthouse CI | Core Web Vitals |

---

## 4. Deep E2E Testing (MANDATORY)

### 4.1 Five Required Verification Layers

| Layer | What to Check | How to Verify | Failure Means |
|-------|---------------|---------------|---------------|
| 1. Network | Request actually sent | `page.waitForResponse()` | Silent failure |
| 2. HTTP Status | Backend accepted (200/201) | `response.status()` | Rejected data |
| 3. Persistence | Data in database | Reload page, verify visible | Lost data |
| 4. Console Errors | Zero JS errors | Capture and assert empty | Broken UI |
| 5. Network Errors | No 4xx/5xx | Monitor failed requests | API issues |

### 4.2 Anti-Patterns (FORBIDDEN)

| Anti-Pattern | Why It's Wrong | Do This Instead |
|--------------|----------------|-----------------|
| `expect(toast).toBeVisible()` | Toast fires before/without API | Intercept actual API call |
| "It should work" | Zero evidence | Show test output + screenshots |
| "Form saves correctly" | No proof of persistence | Reload page, verify data |
| "Validation works" | Could fail silently | Prove API was NOT called |
| Testing only happy path | Misses edge cases | Test invalid states too |

### 4.3 Required Test Patterns

#### Form Submission Test

```typescript
// FORBIDDEN - proves nothing
test("form saves", async ({ page }) => {
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Saved!")).toBeVisible(); // MEANINGLESS
});

// REQUIRED - proves system works
test("form saves", async ({ page }) => {
  // Capture console errors
  const consoleErrors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });

  // Fill form
  await page.getByLabel("Name").fill("New Alert Rule");

  // Intercept API and submit
  const [response] = await Promise.all([
    page.waitForResponse((r) =>
      r.url().includes("/api/v1/rules") && r.request().method() === "POST"
    ),
    page.getByRole("button", { name: "Save" }).click(),
  ]);

  // Verify API accepted
  expect(response.status()).toBe(201);

  // Verify persistence
  await page.reload();
  await expect(page.getByText("New Alert Rule")).toBeVisible();

  // Verify no console errors
  expect(consoleErrors).toHaveLength(0);
});
```

#### Validation Blocking Test

```typescript
test("validation blocks API call", async ({ page }) => {
  let apiCalled = false;

  // Monitor for any API calls
  page.on("request", (request) => {
    if (request.url().includes("/api/")) {
      apiCalled = true;
    }
  });

  // Submit with empty required fields
  await page.getByRole("button", { name: "Save" }).click();

  // Wait for potential API call
  await page.waitForTimeout(1000);

  // API should NOT have been called
  expect(apiCalled).toBe(false);

  // Error message should be visible
  await expect(page.getByRole("alert")).toBeVisible();
});
```

#### Delete Confirmation Test

```typescript
test("delete removes item", async ({ page }) => {
  // Navigate to item
  await page.goto("/alerts/alert-123");

  // Intercept delete and confirm
  const [response] = await Promise.all([
    page.waitForResponse((r) =>
      r.url().includes("/api/v1/alerts/alert-123") &&
      r.request().method() === "DELETE"
    ),
    page.getByRole("button", { name: "Delete" }).click(),
    page.getByRole("button", { name: "Confirm" }).click(),
  ]);

  // Verify API accepted
  expect(response.status()).toBe(200);

  // Verify redirect
  await expect(page).toHaveURL("/alerts");

  // Verify item is gone
  await page.reload();
  await expect(page.getByText("alert-123")).not.toBeVisible();
});
```

---

## 5. Unit Testing (Vitest)

### 5.1 Setup

```typescript
// test-setup.ts
import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import { server } from "./mocks/server";

// MSW setup
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  cleanup();
});
afterAll(() => server.close());

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
});
```

### 5.2 Component Test Template

```typescript
// AlertCard.spec.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AlertCard } from "./AlertCard";

describe("AlertCard", () => {
  const defaultProps = {
    id: "alert-1",
    title: "Test Alert",
    severity: "high" as const,
    status: "open" as const,
    timestamp: "2026-01-03T10:00:00Z",
  };

  it("renders title", () => {
    render(<AlertCard {...defaultProps} />);
    expect(screen.getByText("Test Alert")).toBeInTheDocument();
  });

  it("applies correct severity styling", () => {
    render(<AlertCard {...defaultProps} severity="critical" />);
    const card = screen.getByTestId("alert-card-alert-1");
    expect(card).toHaveStyle({ borderLeftColor: expect.stringContaining("error") });
  });

  it("calls onAcknowledge when button clicked", async () => {
    const onAcknowledge = vi.fn();
    render(<AlertCard {...defaultProps} onAcknowledge={onAcknowledge} />);

    await userEvent.click(screen.getByRole("button", { name: /acknowledge/i }));

    expect(onAcknowledge).toHaveBeenCalledWith("alert-1");
  });
});
```

### 5.3 Hook Test Template

```typescript
// useAlerts.spec.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAlerts } from "./useAlerts";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("useAlerts", () => {
  it("returns alerts on success", async () => {
    const { result } = renderHook(() => useAlerts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].title).toBe("Test Alert 1");
  });

  it("handles error state", async () => {
    server.use(
      http.get("/api/v1/alerts", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    const { result } = renderHook(() => useAlerts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
```

---

## 6. Integration Testing

### 6.1 API Integration Test

```typescript
// alerts-api.integration.spec.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { useAlerts, useMutateAlert } from "./useAlerts";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

describe("Alerts API Integration", () => {
  it("fetches and displays alerts correctly", async () => {
    const { result } = renderHook(() => useAlerts(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data structure
    expect(result.current.data).toMatchObject([
      expect.objectContaining({
        id: expect.any(String),
        title: expect.any(String),
        severity: expect.stringMatching(/critical|high|medium|low/),
      }),
    ]);
  });

  it("creates alert and updates cache", async () => {
    const { result: mutationResult } = renderHook(() => useMutateAlert(), { wrapper });
    const { result: queryResult } = renderHook(() => useAlerts(), { wrapper });

    await waitFor(() => expect(queryResult.current.isSuccess).toBe(true));
    const initialCount = queryResult.current.data?.length ?? 0;

    await mutationResult.current.mutateAsync({
      title: "New Alert",
      severity: "high",
    });

    await waitFor(() => {
      expect(queryResult.current.data?.length).toBe(initialCount + 1);
    });
  });
});
```

---

## 7. E2E Testing (Playwright)

### 7.1 Test Structure

```
e2e/
├── fixtures/
│   └── test-data.ts          # Shared test data
├── pages/
│   ├── alerts.page.ts        # Page objects
│   ├── dashboard.page.ts
│   └── login.page.ts
├── tests/
│   ├── alerts.spec.ts        # Test files
│   ├── dashboard.spec.ts
│   └── auth.spec.ts
└── playwright.config.ts
```

### 7.2 Page Object Pattern

```typescript
// pages/alerts.page.ts
import { Page, Locator, expect } from "@playwright/test";

export class AlertsPage {
  readonly page: Page;
  readonly alertList: Locator;
  readonly createButton: Locator;
  readonly filterSeverity: Locator;

  constructor(page: Page) {
    this.page = page;
    this.alertList = page.getByTestId("alert-list");
    this.createButton = page.getByRole("button", { name: "Create Alert" });
    this.filterSeverity = page.getByLabel("Filter by Severity");
  }

  async goto() {
    await this.page.goto("/alerts");
    await this.page.waitForLoadState("networkidle");
  }

  async createAlert(data: { title: string; severity: string }) {
    await this.createButton.click();
    await this.page.getByLabel("Title").fill(data.title);
    await this.page.getByLabel("Severity").selectOption(data.severity);

    const [response] = await Promise.all([
      this.page.waitForResponse((r) =>
        r.url().includes("/api/v1/alerts") && r.request().method() === "POST"
      ),
      this.page.getByRole("button", { name: "Save" }).click(),
    ]);

    return response;
  }

  async filterBySeverity(severity: string) {
    await this.filterSeverity.selectOption(severity);
    await this.page.waitForLoadState("networkidle");
  }

  async getAlertCount() {
    return await this.alertList.locator("[data-testid^='alert-card-']").count();
  }
}
```

### 7.3 E2E Test Template

```typescript
// tests/alerts.spec.ts
import { test, expect } from "@playwright/test";
import { AlertsPage } from "../pages/alerts.page";
import { loginAndGoto } from "@platform/react-ui-auth/e2e";

test.describe("Alerts Management", () => {
  let alertsPage: AlertsPage;
  const consoleErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Capture console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    // Login and navigate
    await loginAndGoto(page, "/alerts");
    alertsPage = new AlertsPage(page);
  });

  test.afterEach(async () => {
    // Verify no console errors
    expect(consoleErrors).toHaveLength(0);
    consoleErrors.length = 0;
  });

  test("creates alert and verifies persistence", async ({ page }) => {
    // Create alert
    const response = await alertsPage.createAlert({
      title: "E2E Test Alert",
      severity: "high",
    });

    // Verify API accepted
    expect(response.status()).toBe(201);

    // Verify persistence
    await page.reload();
    await expect(page.getByText("E2E Test Alert")).toBeVisible();
  });

  test("filters alerts by severity", async ({ page }) => {
    // Get initial count
    const initialCount = await alertsPage.getAlertCount();

    // Filter to critical only
    const [response] = await Promise.all([
      page.waitForResponse((r) => r.url().includes("/api/v1/alerts")),
      alertsPage.filterBySeverity("critical"),
    ]);

    expect(response.status()).toBe(200);

    // Verify filter applied
    const filteredCount = await alertsPage.getAlertCount();
    expect(filteredCount).toBeLessThanOrEqual(initialCount);
  });

  test("validation prevents submission with empty title", async ({ page }) => {
    let apiCalled = false;
    page.on("request", (r) => {
      if (r.url().includes("/api/v1/alerts") && r.method() === "POST") {
        apiCalled = true;
      }
    });

    // Try to submit empty form
    await alertsPage.createButton.click();
    await page.getByRole("button", { name: "Save" }).click();

    // Wait for potential API call
    await page.waitForTimeout(1000);

    // API should NOT be called
    expect(apiCalled).toBe(false);

    // Error should be visible
    await expect(page.getByText(/title is required/i)).toBeVisible();
  });
});
```

### 7.4 Authentication Setup

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from "@playwright/test";

const authFile = ".auth/user.json";

setup("authenticate", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Email").fill(process.env.TEST_USERNAME!);
  await page.getByLabel("Password").fill(process.env.TEST_PASSWORD!);

  await Promise.all([
    page.waitForURL("/dashboard"),
    page.getByRole("button", { name: "Sign in" }).click(),
  ]);

  await page.context().storageState({ path: authFile });
});
```

---

## 8. Visual Regression Testing

### 8.1 Chromatic Configuration

```typescript
// .storybook/main.ts
export default {
  stories: ["../src/**/*.stories.@(js|jsx|ts|tsx|mdx)"],
  addons: [
    "@storybook/addon-essentials",
    "@chromatic-com/storybook",
  ],
};
```

### 8.2 Visual Test in Playwright

```typescript
test("dashboard matches visual baseline", async ({ page }) => {
  await page.goto("/dashboard");
  await page.waitForLoadState("networkidle");

  // Hide dynamic content
  await page.evaluate(() => {
    document.querySelectorAll("[data-testid='timestamp']").forEach((el) => {
      (el as HTMLElement).style.visibility = "hidden";
    });
  });

  await expect(page).toHaveScreenshot("dashboard.png", {
    maxDiffPixels: 100,
  });
});
```

---

## 9. Accessibility Testing

### 9.1 Automated Accessibility Tests

```typescript
// Component level
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

test("has no accessibility violations", async () => {
  const { container } = render(<AlertCard {...props} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// E2E level
import AxeBuilder from "@axe-core/playwright";

test("dashboard is accessible", async ({ page }) => {
  await page.goto("/dashboard");

  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

---

## 10. Performance Testing

### 10.1 Lighthouse CI

```yaml
# lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ["http://localhost:3000/dashboard"],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        "first-contentful-paint": ["warn", { maxNumericValue: 2000 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 4000 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
        "total-blocking-time": ["warn", { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
```

---

## 11. Test Coverage Requirements

### 11.1 Coverage Targets

| Type | Minimum | Target |
|------|---------|--------|
| Unit (Statements) | 70% | 85% |
| Unit (Branches) | 60% | 75% |
| Integration | 50% | 70% |
| E2E (Critical Paths) | 100% | 100% |

### 11.2 Critical Paths (100% E2E Coverage)

1. **Authentication** - Login, logout, session refresh
2. **Dashboard** - Load, widget data, time range
3. **Alerts** - List, filter, acknowledge, resolve
4. **Vulnerabilities** - List, filter, mark remediated
5. **Compliance** - View frameworks, control status
6. **Settings** - User profile, preferences
7. **API Key Management** - Create, revoke

---

## 12. Quality Gates

### 12.1 PR Merge Requirements

| Check | Requirement | Blocking |
|-------|-------------|----------|
| Unit Tests | All passing | Yes |
| E2E Tests | All passing | Yes |
| Coverage | Meets minimum | Yes |
| Lint | Zero errors | Yes |
| TypeScript | Zero errors | Yes |
| Build | Successful | Yes |
| Accessibility | Zero violations | Yes |
| Visual | Approved | No |

### 12.2 Release Requirements

| Check | Requirement |
|-------|-------------|
| All PRs merged | Quality gates passed |
| E2E Suite | Full suite passing |
| Performance | Lighthouse scores met |
| Security Scan | Zero critical/high |
| Manual QA | Sign-off received |

---

## 13. Test Completion Checklist

Before marking ANY feature complete:

- [ ] **Unit Tests**: Components and utilities tested
- [ ] **Integration Tests**: API hooks tested with MSW
- [ ] **E2E Tests**: Critical paths verified
- [ ] **API Intercepted**: `waitForResponse()` captured requests
- [ ] **Status Verified**: Response status is 200/201
- [ ] **Persistence Proven**: Data visible after `page.reload()`
- [ ] **Validation Tested**: Invalid submission makes NO API call
- [ ] **Errors Captured**: Console errors array is empty
- [ ] **Network Clean**: No 4xx/5xx responses
- [ ] **Accessibility**: Zero violations
- [ ] **Visual**: Baseline captured/approved

---

*This document is mandatory reading for all engineers. Violations of deep testing requirements will block PRs.*
