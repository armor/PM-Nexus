# Nexus UI Uplift - Document Suite Index

> **Project:** Nexus UI Uplift (POC to Production)
> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Platform Standards:** Aligned with `/submodules/platform/llm/` patterns

---

## Document Suite Overview

This document suite follows the platform's LLM documentation structure and provides comprehensive guidance for the Nexus UI Uplift initiative.

### Critical Platform Alignment

All documents adhere to these platform standards:
- **Nx Monorepo**: Apps are shells, libraries contain logic
- **Generators Required**: Never manually create components
- **MUI + Tailwind**: sx props preferred, semantic tokens
- **TanStack Query**: API hooks with placeholderData always set
- **Zod**: Types only, no runtime validation
- **MSW**: Required for all API mocking (Storybook + tests)
- **Deep E2E Testing**: Verify actual API calls, not UI feedback

---

## Document Categories

### 1. Product Vision & Strategy
| Document | File | Status |
|----------|------|--------|
| Extended PRD | `nexus-ui-uplift-extended-prd.md` | Complete |
| Roadmap | Included in PRD | Complete |

### 2. Business & GTM
| Document | File | Status |
|----------|------|--------|
| GTM Strategy | `02-gtm-strategy.md` | Complete |
| AMP Sunset Plan | Included in GTM | Complete |
| Customer Success Playbook | Included in GTM | Complete |

### 3. Architecture
| Document | File | Status |
|----------|------|--------|
| Architecture Document | `nexus-architecture-document.md` | Complete |
| AWS/K8s Design | Included in Architecture | Complete |
| API Layer Design | Included in Architecture | Complete |

### 4. Components
| Document | File | Status |
|----------|------|--------|
| Component Library Spec | `04-component-library.md` | Complete |
| Storybook Requirements | Included in Components | Complete |
| Design Tokens | Included in Components | Complete |

### 5. API Documentation
| Document | File | Status |
|----------|------|--------|
| API Specification | `05-api-specification.md` | Complete |
| OpenAPI Contracts | Reference to specs | Complete |
| Error Codes | Included in API | Complete |

### 6. Delivery & Process
| Document | File | Status |
|----------|------|--------|
| Development Workflow | `06-delivery-process.md` | Complete |
| Sprint Planning | Included in Delivery | Complete |
| Release Management | Included in Delivery | Complete |

### 7. Quality & Testing
| Document | File | Status |
|----------|------|--------|
| Testing Strategy | `07-testing-strategy.md` | Complete |
| E2E Test Requirements | Included in Testing | Complete |
| Quality Gates | Included in Testing | Complete |

### 8. Security & Compliance
| Document | File | Status |
|----------|------|--------|
| Security Architecture | `08-security-compliance.md` | Complete |
| RBAC Design | Included in Security | Complete |
| Compliance Controls | Included in Security | Complete |

### 9. Operations
| Document | File | Status |
|----------|------|--------|
| Operations Runbook | `09-operations-runbook.md` | Complete |
| Monitoring & Alerting | Included in Operations | Complete |
| Incident Response | Included in Operations | Complete |

### 10. Design
| Document | File | Status |
|----------|------|--------|
| UX/Design System | `10-design-system.md` | Complete |
| Accessibility (WCAG) | Included in Design | Complete |
| Responsive Patterns | Included in Design | Complete |

### 11. Epics
| Document | File | Status |
|----------|------|--------|
| Epic Breakdown | `11-epics-stories.md` | Complete |
| User Stories | Included in Epics | Complete |
| Acceptance Criteria | Included in Epics | Complete |

### 12. Training
| Document | File | Status |
|----------|------|--------|
| Training Materials | `12-training-materials.md` | Complete |
| User Guides | Included in Training | Complete |
| Admin Guides | Included in Training | Complete |

### 13. Data
| Document | File | Status |
|----------|------|--------|
| Data Dictionary | `13-data-dictionary.md` | Complete |
| Schema Definitions | Included in Data | Complete |
| Migration Guides | Included in Data | Complete |

### 14. Integration
| Document | File | Status |
|----------|------|--------|
| Integration Playbook | `14-integration-playbook.md` | Complete |
| Connector Catalog | Included in Integration | Complete |
| Third-Party APIs | Included in Integration | Complete |

### 15. Migration Architecture (NEW)
| Document | File | Status |
|----------|------|--------|
| POC to Platform Migration | `15-poc-migration-architecture.md` | Complete |
| MCP Server Integration | Included in Migration | Complete |
| Connector Migration | Included in Migration | Complete |

---

## Quick Navigation

### For Product Managers
1. Extended PRD
2. GTM Strategy
3. Epics & Stories
4. Training Materials

### For Engineers
1. Architecture Document
2. Component Library (Storybook)
3. API Specification
4. Testing Strategy
5. Delivery Process

### For Designers
1. UX/Design System
2. Component Library
3. Accessibility Requirements

### For DevOps/SRE
1. Architecture Document
2. Operations Runbook
3. Security & Compliance

### For Customer Success
1. GTM Strategy
2. Training Materials
3. User Guides

---

## Version Control

All documents are maintained in:
- **Repository**: `UI-Uplift`
- **Path**: `.bmad/planning-artifacts/`
- **Review Cadence**: Weekly during active development

---

## Related Resources

- **Platform Standards**: `/submodules/platform/llm/specifications/`
- **Armor-Dash POC**: `/submodules/Armor-Dash/`
- **MCP Server**: `/submodules/jira-mcp/`
- **Confluence PRD**: [Nexus UI Uplift](https://armor-defense.atlassian.net/wiki/spaces/PDM/pages/5015044104)
