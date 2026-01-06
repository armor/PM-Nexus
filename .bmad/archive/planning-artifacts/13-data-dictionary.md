; add # Nexus UI Uplift - Data Dictionary

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **Database:** PostgreSQL 15

---

## 1. Overview

This document defines the data model for the Nexus platform, including table structures, relationships, and field definitions.

---

## 2. Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│  organizations  │──────<│     users       │
└────────┬────────┘       └─────────────────┘
         │
         │1
         │
         │*
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌────────┐ ┌─────────────────┐
│assets │ │ alerts │ │ vulnerabilities │
└───┬───┘ └────┬───┘ └────────┬────────┘
    │          │              │
    │          │              │
    └──────────┴──────────────┘
              │
              ▼
    ┌──────────────────┐
    │   asset_alerts   │ (junction)
    │   asset_vulns    │ (junction)
    └──────────────────┘
```

---

## 3. Core Tables

### 3.1 organizations

Primary table for tenant/customer data.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| name | VARCHAR(255) | NO | - | Organization name |
| slug | VARCHAR(100) | NO | - | URL-safe identifier |
| settings | JSONB | NO | '{}' | Configuration settings |
| subscription_tier | VARCHAR(50) | NO | 'standard' | Subscription level |
| status | VARCHAR(20) | NO | 'active' | Account status |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (slug)`
- `INDEX (status)`

**Settings JSONB Structure:**
```json
{
  "branding": {
    "logo_url": "string",
    "primary_color": "string"
  },
  "notifications": {
    "email_enabled": true,
    "slack_webhook": "string"
  },
  "security": {
    "mfa_required": false,
    "session_timeout_minutes": 480
  }
}
```

---

### 3.2 users

User accounts within organizations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| email | VARCHAR(255) | NO | - | User email |
| name | VARCHAR(255) | YES | - | Display name |
| role | VARCHAR(50) | NO | 'viewer' | User role |
| status | VARCHAR(20) | NO | 'active' | Account status |
| settings | JSONB | NO | '{}' | User preferences |
| last_login_at | TIMESTAMPTZ | YES | - | Last login time |
| password_hash | VARCHAR(255) | YES | - | Hashed password |
| mfa_enabled | BOOLEAN | NO | false | MFA status |
| mfa_secret | VARCHAR(255) | YES | - | Encrypted MFA secret |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (organization_id, email)`
- `INDEX (organization_id)`
- `INDEX (role)`
- `INDEX (status)`

**Roles:**
- `admin` - Full access
- `manager` - Read/write, user management
- `analyst` - Read/write security data
- `viewer` - Read-only access

---

### 3.3 assets

Security assets tracked by the platform.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| external_id | VARCHAR(255) | YES | - | ID from source system |
| type | VARCHAR(50) | NO | - | Asset type |
| name | VARCHAR(255) | NO | - | Asset name |
| hostname | VARCHAR(255) | YES | - | Hostname if applicable |
| ip_addresses | VARCHAR[] | YES | '{}' | Array of IP addresses |
| operating_system | VARCHAR(100) | YES | - | OS name and version |
| risk_score | INTEGER | YES | - | Calculated risk score (0-100) |
| criticality | VARCHAR(20) | NO | 'medium' | Business criticality |
| tags | VARCHAR[] | NO | '{}' | User-defined tags |
| metadata | JSONB | NO | '{}' | Additional properties |
| source | VARCHAR(100) | YES | - | Data source/connector |
| last_seen_at | TIMESTAMPTZ | YES | - | Last activity time |
| created_at | TIMESTAMPTZ | NO | NOW() | First discovered |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (organization_id, external_id, source)`
- `INDEX (organization_id, type)`
- `INDEX (organization_id, criticality)`
- `INDEX (organization_id, risk_score)`

**Asset Types:**
- `server` - Physical/virtual servers
- `endpoint` - Workstations, laptops
- `user` - User accounts
- `application` - Software applications
- `cloud_resource` - Cloud infrastructure
- `network_device` - Routers, switches, firewalls
- `container` - Docker containers
- `database` - Database instances

---

### 3.4 alerts

Security alerts and incidents.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| title | VARCHAR(500) | NO | - | Alert title |
| description | TEXT | YES | - | Detailed description |
| severity | VARCHAR(20) | NO | - | Severity level |
| status | VARCHAR(50) | NO | 'open' | Current status |
| source | VARCHAR(100) | NO | - | Source system |
| source_id | VARCHAR(255) | YES | - | ID in source system |
| asset_id | UUID | YES | - | FK to assets |
| assignee_id | UUID | YES | - | FK to users |
| metadata | JSONB | NO | '{}' | Additional data |
| created_at | TIMESTAMPTZ | NO | NOW() | Alert creation time |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |
| acknowledged_at | TIMESTAMPTZ | YES | - | When acknowledged |
| acknowledged_by | UUID | YES | - | FK to users |
| resolved_at | TIMESTAMPTZ | YES | - | When resolved |
| resolved_by | UUID | YES | - | FK to users |
| resolution_notes | TEXT | YES | - | Resolution details |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX (organization_id, status)`
- `INDEX (organization_id, severity)`
- `INDEX (organization_id, created_at)`
- `INDEX (source, source_id)`
- `INDEX (asset_id)`
- `INDEX (assignee_id)`

**Severity Levels:**
- `critical` - Immediate action required
- `high` - Urgent attention needed
- `medium` - Should be addressed soon
- `low` - Informational

**Status Values:**
- `open` - New, unaddressed
- `acknowledged` - Being investigated
- `in_progress` - Active remediation
- `resolved` - Fixed
- `closed` - No action needed
- `false_positive` - Not a real issue

---

### 3.5 vulnerabilities

Security vulnerabilities.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| cve_id | VARCHAR(50) | YES | - | CVE identifier |
| title | VARCHAR(500) | NO | - | Vulnerability title |
| description | TEXT | YES | - | Detailed description |
| severity | VARCHAR(20) | NO | - | Severity level |
| cvss_score | DECIMAL(3,1) | YES | - | CVSS score (0.0-10.0) |
| cvss_vector | VARCHAR(100) | YES | - | CVSS vector string |
| status | VARCHAR(50) | NO | 'open' | Current status |
| asset_id | UUID | YES | - | FK to assets |
| affected_software | VARCHAR(255) | YES | - | Affected software |
| affected_version | VARCHAR(100) | YES | - | Affected versions |
| fixed_version | VARCHAR(100) | YES | - | Version with fix |
| remediation | TEXT | YES | - | Remediation steps |
| references | VARCHAR[] | NO | '{}' | Reference URLs |
| exploit_available | BOOLEAN | NO | false | Known exploit exists |
| due_date | DATE | YES | - | SLA due date |
| source | VARCHAR(100) | YES | - | Scanner source |
| source_id | VARCHAR(255) | YES | - | ID in source |
| discovered_at | TIMESTAMPTZ | NO | NOW() | When discovered |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |
| remediated_at | TIMESTAMPTZ | YES | - | When fixed |
| remediated_by | UUID | YES | - | FK to users |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX (organization_id, status)`
- `INDEX (organization_id, severity)`
- `INDEX (organization_id, due_date)`
- `INDEX (cve_id)`
- `INDEX (asset_id)`

**Status Values:**
- `open` - Not addressed
- `in_progress` - Being fixed
- `remediated` - Fixed
- `accepted` - Risk accepted
- `false_positive` - Not applicable

---

### 3.6 compliance_frameworks

Compliance framework definitions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| name | VARCHAR(100) | NO | - | Framework name |
| description | TEXT | YES | - | Description |
| version | VARCHAR(50) | NO | - | Framework version |
| control_count | INTEGER | NO | 0 | Number of controls |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation time |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (name, version)`

---

### 3.7 compliance_controls

Individual controls within frameworks.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| framework_id | UUID | NO | - | FK to frameworks |
| control_id | VARCHAR(50) | NO | - | Control identifier |
| title | VARCHAR(255) | NO | - | Control title |
| description | TEXT | YES | - | Control description |
| category | VARCHAR(100) | YES | - | Control category |
| parent_control_id | UUID | YES | - | Parent control (hierarchy) |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation time |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (framework_id, control_id)`
- `INDEX (framework_id)`
- `INDEX (category)`

---

### 3.8 org_compliance_status

Organization's compliance status per control.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| control_id | UUID | NO | - | FK to controls |
| status | VARCHAR(50) | NO | 'not_assessed' | Compliance status |
| evidence | JSONB | NO | '[]' | Evidence attachments |
| owner_id | UUID | YES | - | FK to users |
| notes | TEXT | YES | - | Implementation notes |
| due_date | DATE | YES | - | Assessment due date |
| last_assessed_at | TIMESTAMPTZ | YES | - | Last assessment time |
| assessed_by | UUID | YES | - | FK to users |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation time |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE (organization_id, control_id)`
- `INDEX (organization_id, status)`
- `INDEX (owner_id)`

**Status Values:**
- `not_assessed` - Not yet evaluated
- `compliant` - Meets requirements
- `non_compliant` - Does not meet requirements
- `partially_compliant` - Partial implementation
- `not_applicable` - N/A for this org
- `in_progress` - Being addressed

---

### 3.9 connectors

Integration connector configurations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| name | VARCHAR(100) | NO | - | Connector name |
| type | VARCHAR(50) | NO | - | Connector type |
| category | VARCHAR(50) | NO | - | Category |
| status | VARCHAR(20) | NO | 'disconnected' | Connection status |
| config | JSONB | NO | '{}' | Encrypted config |
| sync_frequency_minutes | INTEGER | NO | 15 | Sync interval |
| last_sync_at | TIMESTAMPTZ | YES | - | Last successful sync |
| next_sync_at | TIMESTAMPTZ | YES | - | Next scheduled sync |
| item_count | INTEGER | YES | - | Items synced |
| error_message | TEXT | YES | - | Last error if any |
| created_at | TIMESTAMPTZ | NO | NOW() | Creation time |
| updated_at | TIMESTAMPTZ | NO | NOW() | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX (organization_id)`
- `INDEX (status)`
- `INDEX (next_sync_at)`

**Status Values:**
- `connected` - Active and syncing
- `disconnected` - Not connected
- `error` - Connection error
- `syncing` - Currently syncing

---

### 3.10 audit_logs

Audit trail for all actions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| organization_id | UUID | NO | - | FK to organizations |
| user_id | UUID | YES | - | FK to users |
| action | VARCHAR(100) | NO | - | Action performed |
| resource_type | VARCHAR(50) | NO | - | Resource type |
| resource_id | UUID | YES | - | Resource ID |
| details | JSONB | NO | '{}' | Action details |
| ip_address | INET | YES | - | Client IP |
| user_agent | TEXT | YES | - | Client user agent |
| created_at | TIMESTAMPTZ | NO | NOW() | Action timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX (organization_id, created_at)`
- `INDEX (user_id)`
- `INDEX (resource_type, resource_id)`
- `INDEX (action)`

**Partitioning:**
- Partitioned by `created_at` (monthly)
- Retention: 2 years

---

## 4. Junction Tables

### 4.1 asset_alerts

Many-to-many between assets and alerts.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| asset_id | UUID | NO | - | FK to assets |
| alert_id | UUID | NO | - | FK to alerts |
| created_at | TIMESTAMPTZ | NO | NOW() | Association time |

**Indexes:**
- `PRIMARY KEY (asset_id, alert_id)`
- `INDEX (alert_id)`

---

### 4.2 asset_vulnerabilities

Many-to-many between assets and vulnerabilities.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| asset_id | UUID | NO | - | FK to assets |
| vulnerability_id | UUID | NO | - | FK to vulnerabilities |
| created_at | TIMESTAMPTZ | NO | NOW() | Association time |

**Indexes:**
- `PRIMARY KEY (asset_id, vulnerability_id)`
- `INDEX (vulnerability_id)`

---

## 5. Enumerations

### 5.1 Severity

| Value | Description |
|-------|-------------|
| critical | Immediate action required |
| high | Urgent attention |
| medium | Should address |
| low | Informational |

### 5.2 Alert Status

| Value | Description |
|-------|-------------|
| open | New, unaddressed |
| acknowledged | Being investigated |
| in_progress | Active remediation |
| resolved | Fixed |
| closed | No action needed |
| false_positive | Not a real issue |

### 5.3 Vulnerability Status

| Value | Description |
|-------|-------------|
| open | Not addressed |
| in_progress | Being fixed |
| remediated | Fixed |
| accepted | Risk accepted |
| false_positive | Not applicable |

### 5.4 User Role

| Value | Permissions |
|-------|-------------|
| admin | Full access |
| manager | Read/write, user mgmt |
| analyst | Read/write security |
| viewer | Read-only |

---

## 6. Data Retention

| Table | Retention | Archival |
|-------|-----------|----------|
| audit_logs | 2 years | S3 Glacier |
| alerts | 1 year active | Archive after |
| vulnerabilities | 1 year active | Archive after |
| assets | Indefinite | - |
| users | Until deleted | - |
| organizations | Until deleted | - |

---

## 7. Migration Strategy

```sql
-- Example migration: Add new column
-- migrations/20260103_add_risk_score.sql

BEGIN;

ALTER TABLE assets
ADD COLUMN risk_score INTEGER;

CREATE INDEX CONCURRENTLY idx_assets_risk_score
ON assets(organization_id, risk_score);

COMMIT;
```

---

*This data dictionary is maintained by the Database team. Schema changes require review.*
