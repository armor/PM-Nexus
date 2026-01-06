# OpenAPI Specification - Nexus Security Platform

## Overview

This document defines the OpenAPI 3.1 specification for the Nexus Security Platform API, derived from the existing platform codebase patterns.

---

## OpenAPI Specification (YAML)

```yaml
openapi: 3.1.0
info:
  title: Nexus Security Platform API
  description: |
    The Nexus Security Platform API provides programmatic access to security
    operations, vulnerability management, compliance monitoring, and threat
    detection capabilities.

    ## Authentication
    All API requests require OAuth 2.0 Bearer token authentication via Okta.

    ## Rate Limiting
    API requests are rate-limited based on your subscription tier.

    ## Versioning
    The API uses URL-based versioning (e.g., /v1/, /v2/).
  version: 1.0.0
  contact:
    name: Armor Developer Support
    url: https://developer.armor.com/support
    email: developers@armor.com
  license:
    name: Proprietary
    url: https://armor.com/terms

servers:
  - url: https://api.armor.com
    description: Production API
  - url: https://api.staging.armor.com
    description: Staging API
  - url: https://api.sandbox.armor.com
    description: Sandbox (testing)

tags:
  - name: Authentication
    description: OAuth 2.0 authentication endpoints
  - name: User
    description: Current user operations
  - name: Accounts
    description: Account management
  - name: Alerts
    description: Security alert management
  - name: Findings
    description: Security finding operations
  - name: Assets
    description: Asset inventory
  - name: Vulnerabilities
    description: Vulnerability management
  - name: Compliance
    description: Compliance monitoring
  - name: Connectors
    description: Third-party integrations
  - name: Security Detections
    description: Advanced security detection (v2)
  - name: Metrics
    description: Security metrics and scores
  - name: Reports
    description: Report generation
  - name: Webhooks
    description: Webhook configuration

security:
  - bearerAuth: []

paths:
  # ============================================
  # USER ENDPOINTS
  # ============================================
  /v1/me:
    get:
      tags:
        - User
      summary: Get current user
      description: |
        Returns the authenticated user's profile, accounts, permissions,
        and feature flags.
      operationId: getCurrentUser
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: User profile retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MeResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  # ============================================
  # ACCOUNT ENDPOINTS
  # ============================================
  /v1/accounts/{accountId}:
    get:
      tags:
        - Accounts
      summary: Get account details
      description: Retrieves detailed information about a specific account.
      operationId: getAccount
      parameters:
        - name: accountId
          in: path
          required: true
          schema:
            type: string
          description: Unique account identifier
      responses:
        '200':
          description: Account retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Account'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'

  /v1/account/children:
    get:
      tags:
        - Accounts
      summary: List sub-accounts
      description: Lists all child accounts under the current account.
      operationId: listSubAccounts
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
      responses:
        '200':
          description: Sub-accounts retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AccountListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - Accounts
      summary: Create sub-account
      description: Creates a new child account under the current account.
      operationId: createSubAccount
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSubAccountRequest'
      responses:
        '201':
          description: Sub-account created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Account'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

  # ============================================
  # ALERT ENDPOINTS
  # ============================================
  /v1/alerts:
    get:
      tags:
        - Alerts
      summary: List alerts
      description: |
        Returns a paginated list of security alerts with optional filtering.
      operationId: listAlerts
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
        - $ref: '#/components/parameters/Before'
        - name: severity
          in: query
          schema:
            type: array
            items:
              $ref: '#/components/schemas/Severity'
          style: form
          explode: false
          description: Filter by severity levels
        - name: status
          in: query
          schema:
            $ref: '#/components/schemas/AlertStatus'
          description: Filter by alert status
        - name: source
          in: query
          schema:
            type: string
          description: Filter by connector source
        - name: since
          in: query
          schema:
            type: string
            format: date-time
          description: Filter alerts created after this timestamp
        - name: sort
          in: query
          schema:
            type: string
            default: '-createdAt'
          description: Sort field (prefix with - for descending)
      responses:
        '200':
          description: Alerts retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AlertListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/alerts/{alertId}:
    get:
      tags:
        - Alerts
      summary: Get alert details
      description: Retrieves detailed information about a specific alert.
      operationId: getAlert
      parameters:
        - name: alertId
          in: path
          required: true
          schema:
            type: string
          description: Unique alert identifier
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Alert retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AlertDetail'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      tags:
        - Alerts
      summary: Update alert
      description: Updates the status or assignee of an alert.
      operationId: updateAlert
      parameters:
        - name: alertId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateAlertRequest'
      responses:
        '200':
          description: Alert updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AlertDetail'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /v1/alerts/{alertId}/acknowledge:
    post:
      tags:
        - Alerts
      summary: Acknowledge alert
      description: Marks an alert as acknowledged, indicating investigation has begun.
      operationId: acknowledgeAlert
      parameters:
        - name: alertId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                note:
                  type: string
                  description: Optional acknowledgment note
                assignee:
                  type: string
                  format: email
                  description: Email of assignee
      responses:
        '200':
          description: Alert acknowledged
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AlertDetail'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /v1/alerts/{alertId}/resolve:
    post:
      tags:
        - Alerts
      summary: Resolve alert
      description: Marks an alert as resolved.
      operationId: resolveAlert
      parameters:
        - name: alertId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                resolution:
                  type: string
                  enum: [fixed, false_positive, accepted_risk, duplicate]
                  description: Resolution type
                note:
                  type: string
                  description: Resolution notes
      responses:
        '200':
          description: Alert resolved
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # FINDINGS ENDPOINTS
  # ============================================
  /v1/findings:
    get:
      tags:
        - Findings
      summary: List findings
      description: Returns a paginated list of security findings.
      operationId: listFindings
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
        - name: severity
          in: query
          schema:
            type: array
            items:
              $ref: '#/components/schemas/Severity'
          style: form
          explode: false
        - name: source
          in: query
          schema:
            type: string
        - name: assetId
          in: query
          schema:
            type: string
          description: Filter by affected asset
      responses:
        '200':
          description: Findings retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FindingListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/findings/{findingId}:
    get:
      tags:
        - Findings
      summary: Get finding details
      operationId: getFinding
      parameters:
        - name: findingId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Finding retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FindingDetail'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # ASSET ENDPOINTS
  # ============================================
  /v1/assets:
    get:
      tags:
        - Assets
      summary: List assets
      description: Returns a paginated list of discovered assets.
      operationId: listAssets
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
        - name: type
          in: query
          schema:
            type: string
            enum: [server, workstation, container, cloud_resource, network_device]
        - name: os
          in: query
          schema:
            type: string
        - name: tags
          in: query
          schema:
            type: array
            items:
              type: string
          style: form
          explode: false
      responses:
        '200':
          description: Assets retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AssetListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/assets/{assetId}:
    get:
      tags:
        - Assets
      summary: Get asset details
      operationId: getAsset
      parameters:
        - name: assetId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Asset retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AssetDetail'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      tags:
        - Assets
      summary: Update asset
      description: Update asset tags or metadata.
      operationId: updateAsset
      parameters:
        - name: assetId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tags:
                  type: array
                  items:
                    type: string
                criticality:
                  type: string
                  enum: [critical, high, medium, low]
                owner:
                  type: string
                  format: email
      responses:
        '200':
          description: Asset updated
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # VULNERABILITY ENDPOINTS
  # ============================================
  /v1/vulnerabilities:
    get:
      tags:
        - Vulnerabilities
      summary: List vulnerabilities
      operationId: listVulnerabilities
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
        - name: severity
          in: query
          schema:
            type: array
            items:
              $ref: '#/components/schemas/Severity'
          style: form
          explode: false
        - name: cveId
          in: query
          schema:
            type: string
          description: Filter by CVE ID
        - name: assetId
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Vulnerabilities retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VulnerabilityListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/vulnerabilities/trend:
    get:
      tags:
        - Vulnerabilities
      summary: Get vulnerability trend
      description: Returns vulnerability counts over time.
      operationId: getVulnerabilityTrend
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - name: days
          in: query
          schema:
            type: integer
            default: 30
            minimum: 7
            maximum: 365
          description: Number of days of history
        - name: groupBy
          in: query
          schema:
            type: string
            enum: [day, week, month]
            default: day
      responses:
        '200':
          description: Trend data retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VulnerabilityTrendResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  # ============================================
  # COMPLIANCE ENDPOINTS
  # ============================================
  /v1/compliance/status:
    get:
      tags:
        - Compliance
      summary: Get compliance status
      description: Returns overall compliance status across all frameworks.
      operationId: getComplianceStatus
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Compliance status retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ComplianceStatusResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/compliance/frameworks:
    get:
      tags:
        - Compliance
      summary: List compliance frameworks
      operationId: listComplianceFrameworks
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Frameworks retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ComplianceFrameworkListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/compliance/frameworks/{frameworkId}:
    get:
      tags:
        - Compliance
      summary: Get framework details
      operationId: getComplianceFramework
      parameters:
        - name: frameworkId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Framework details retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ComplianceFrameworkDetail'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # CONNECTOR ENDPOINTS
  # ============================================
  /v1/connectors:
    get:
      tags:
        - Connectors
      summary: List connectors
      description: Returns all configured connectors.
      operationId: listConnectors
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Connectors retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConnectorListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - Connectors
      summary: Create connector
      operationId: createConnector
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateConnectorRequest'
      responses:
        '201':
          description: Connector created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Connector'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/connectors/health:
    get:
      tags:
        - Connectors
      summary: Get connector health
      description: Returns health status of all connectors.
      operationId: getConnectorHealth
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Health status retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConnectorHealthResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/connectors/{connectorId}:
    get:
      tags:
        - Connectors
      summary: Get connector details
      operationId: getConnector
      parameters:
        - name: connectorId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Connector retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Connector'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      tags:
        - Connectors
      summary: Update connector
      operationId: updateConnector
      parameters:
        - name: connectorId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateConnectorRequest'
      responses:
        '200':
          description: Connector updated
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      tags:
        - Connectors
      summary: Delete connector
      operationId: deleteConnector
      parameters:
        - name: connectorId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '204':
          description: Connector deleted
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /v1/connectors/{connectorId}/sync:
    post:
      tags:
        - Connectors
      summary: Trigger sync
      description: Manually triggers a data sync for the connector.
      operationId: syncConnector
      parameters:
        - name: connectorId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                fullSync:
                  type: boolean
                  default: false
                  description: Force full data sync instead of incremental
      responses:
        '202':
          description: Sync initiated
          content:
            application/json:
              schema:
                type: object
                properties:
                  syncId:
                    type: string
                  status:
                    type: string
                    enum: [queued, running]
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # SECURITY DETECTIONS (V2)
  # ============================================
  /v2/security-detections:
    get:
      tags:
        - Security Detections
      summary: List security detections
      description: Returns enhanced security detection data with pagination.
      operationId: listSecurityDetections
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/PaginationToken'
        - name: severity
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 5
        - name: detectionType
          in: query
          schema:
            type: string
            enum: [INCIDENT, ALERT, THREAT]
        - name: ticketStatus
          in: query
          schema:
            type: string
            enum: [PENDING, IN_PROGRESS, RESOLVED, DISMISSED]
      responses:
        '200':
          description: Detections retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecurityDetectionListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v2/security-detections/{detectionId}:
    get:
      tags:
        - Security Detections
      summary: Get detection details
      operationId: getSecurityDetection
      parameters:
        - name: detectionId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Detection retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecurityDetection'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # METRICS ENDPOINTS
  # ============================================
  /v1/metrics/security-score:
    get:
      tags:
        - Metrics
      summary: Get security score
      description: Returns the current security posture score with breakdown.
      operationId: getSecurityScore
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - name: includeBreakdown
          in: query
          schema:
            type: boolean
            default: true
        - name: includeTrend
          in: query
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Security score retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecurityScoreResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/metrics/risk-heatmap:
    get:
      tags:
        - Metrics
      summary: Get risk heatmap
      description: Returns risk distribution data for heatmap visualization.
      operationId: getRiskHeatmap
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - name: groupBy
          in: query
          schema:
            type: string
            enum: [asset_type, severity, source]
            default: severity
      responses:
        '200':
          description: Heatmap data retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RiskHeatmapResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

  # ============================================
  # REPORT ENDPOINTS
  # ============================================
  /v1/reports:
    get:
      tags:
        - Reports
      summary: List reports
      operationId: listReports
      parameters:
        - $ref: '#/components/parameters/AccountContext'
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/After'
      responses:
        '200':
          description: Reports retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReportListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - Reports
      summary: Generate report
      operationId: generateReport
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GenerateReportRequest'
      responses:
        '202':
          description: Report generation started
          content:
            application/json:
              schema:
                type: object
                properties:
                  reportId:
                    type: string
                  status:
                    type: string
                    enum: [queued, generating]
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/reports/{reportId}:
    get:
      tags:
        - Reports
      summary: Get report
      operationId: getReport
      parameters:
        - name: reportId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Report retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Report'
            application/pdf:
              schema:
                type: string
                format: binary
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # WEBHOOK ENDPOINTS
  # ============================================
  /v1/webhooks:
    get:
      tags:
        - Webhooks
      summary: List webhooks
      operationId: listWebhooks
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Webhooks retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WebhookListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - Webhooks
      summary: Create webhook
      operationId: createWebhook
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateWebhookRequest'
      responses:
        '201':
          description: Webhook created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Webhook'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/webhooks/{webhookId}:
    delete:
      tags:
        - Webhooks
      summary: Delete webhook
      operationId: deleteWebhook
      parameters:
        - name: webhookId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '204':
          description: Webhook deleted
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  /v1/webhooks/{webhookId}/test:
    post:
      tags:
        - Webhooks
      summary: Test webhook
      description: Sends a test payload to the webhook endpoint.
      operationId: testWebhook
      parameters:
        - name: webhookId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Test sent
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  statusCode:
                    type: integer
                  responseTime:
                    type: integer
                    description: Response time in milliseconds
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

  # ============================================
  # SECURE NOTES ENDPOINTS
  # ============================================
  /v1/securenotes:
    get:
      tags:
        - User
      summary: List secure notes
      operationId: listSecureNotes
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Secure notes retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecureNoteListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - User
      summary: Create secure note
      operationId: createSecureNote
      parameters:
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSecureNoteRequest'
      responses:
        '201':
          description: Secure note created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecureNote'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /v1/securenotes/{noteId}:
    get:
      tags:
        - User
      summary: Get secure note
      operationId: getSecureNote
      parameters:
        - name: noteId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '200':
          description: Secure note retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecureNote'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    put:
      tags:
        - User
      summary: Update secure note
      operationId: updateSecureNote
      parameters:
        - name: noteId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateSecureNoteRequest'
      responses:
        '200':
          description: Secure note updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecureNote'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      tags:
        - User
      summary: Delete secure note
      operationId: deleteSecureNote
      parameters:
        - name: noteId
          in: path
          required: true
          schema:
            type: string
        - $ref: '#/components/parameters/AccountContext'
      responses:
        '204':
          description: Secure note deleted
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Okta-issued JWT token

  parameters:
    AccountContext:
      name: X-Account-Context
      in: header
      required: true
      schema:
        type: string
      description: Account ID for multi-tenant access

    PaginationToken:
      name: X-Pagination-Token
      in: header
      schema:
        type: string
      description: Cursor token for pagination

    Limit:
      name: limit
      in: query
      schema:
        type: integer
        default: 25
        minimum: 1
        maximum: 100
      description: Maximum number of items to return

    After:
      name: after
      in: query
      schema:
        type: string
      description: Cursor for next page

    Before:
      name: before
      in: query
      schema:
        type: string
      description: Cursor for previous page

  responses:
    BadRequest:
      description: Bad Request - Validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Unauthorized:
      description: Unauthorized - Invalid or missing token
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Forbidden:
      description: Forbidden - Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    NotFound:
      description: Not Found - Resource does not exist
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    RateLimited:
      description: Too Many Requests - Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  schemas:
    # ============================================
    # COMMON SCHEMAS
    # ============================================
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
            - requestId
          properties:
            code:
              type: string
              description: Machine-readable error code
            message:
              type: string
              description: Human-readable error message
            details:
              type: object
              additionalProperties: true
            requestId:
              type: string
              description: Request ID for debugging
            documentation:
              type: string
              format: uri
              description: Link to relevant documentation

    Paging:
      type: object
      properties:
        before:
          type: string
          nullable: true
        after:
          type: string
          nullable: true
        total:
          type: integer

    Severity:
      type: string
      enum:
        - critical
        - high
        - medium
        - low
        - info

    # ============================================
    # USER SCHEMAS
    # ============================================
    MeResponse:
      type: object
      properties:
        user:
          $ref: '#/components/schemas/User'
        accounts:
          type: array
          items:
            $ref: '#/components/schemas/Account'
        permissions:
          type: object
          additionalProperties:
            type: array
            items:
              type: string
        features:
          type: array
          items:
            $ref: '#/components/schemas/Feature'

    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
          format: email
        firstName:
          type: string
        lastName:
          type: string
        role:
          type: string
        createdAt:
          type: string
          format: date-time

    Feature:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        enabled:
          type: boolean

    # ============================================
    # ACCOUNT SCHEMAS
    # ============================================
    Account:
      type: object
      properties:
        accountId:
          type: string
        name:
          type: string
        addressLine1:
          type: string
        addressLine2:
          type: string
        city:
          type: string
        state:
          type: string
        postalCode:
          type: string
        country:
          type: string
        accountSignupType:
          type: string

    AccountListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Account'
        paging:
          $ref: '#/components/schemas/Paging'

    CreateSubAccountRequest:
      type: object
      required:
        - companyName
        - relationshipEntity
        - addressLine1
        - city
        - state
        - postalCode
        - country
      properties:
        companyName:
          type: string
        relationshipEntity:
          type: string
        addressLine1:
          type: string
        addressLine2:
          type: string
        city:
          type: string
        state:
          type: string
        postalCode:
          type: string
        country:
          type: string
        autoAcceptUserInvite:
          type: boolean
          default: false

    # ============================================
    # ALERT SCHEMAS
    # ============================================
    Alert:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        severity:
          $ref: '#/components/schemas/Severity'
        status:
          $ref: '#/components/schemas/AlertStatus'
        source:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    AlertStatus:
      type: string
      enum:
        - open
        - acknowledged
        - resolved
        - dismissed

    AlertDetail:
      allOf:
        - $ref: '#/components/schemas/Alert'
        - type: object
          properties:
            description:
              type: string
            findings:
              type: array
              items:
                $ref: '#/components/schemas/Finding'
            assets:
              type: array
              items:
                $ref: '#/components/schemas/Asset'
            timeline:
              type: array
              items:
                $ref: '#/components/schemas/TimelineEvent'
            assignee:
              $ref: '#/components/schemas/User'
            rawData:
              type: object

    AlertListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Alert'
        paging:
          $ref: '#/components/schemas/Paging'

    UpdateAlertRequest:
      type: object
      properties:
        status:
          $ref: '#/components/schemas/AlertStatus'
        assignee:
          type: string
          format: email
        note:
          type: string

    TimelineEvent:
      type: object
      properties:
        timestamp:
          type: string
          format: date-time
        action:
          type: string
        actor:
          type: string
        details:
          type: object

    # ============================================
    # FINDING SCHEMAS
    # ============================================
    Finding:
      type: object
      properties:
        id:
          type: string
        externalId:
          type: string
        source:
          type: string
        severity:
          $ref: '#/components/schemas/Severity'
        title:
          type: string
        description:
          type: string
        firstSeen:
          type: string
          format: date-time
        lastSeen:
          type: string
          format: date-time

    FindingDetail:
      allOf:
        - $ref: '#/components/schemas/Finding'
        - type: object
          properties:
            assets:
              type: array
              items:
                $ref: '#/components/schemas/Asset'
            remediation:
              type: string
            references:
              type: array
              items:
                type: string
                format: uri
            rawData:
              type: object

    FindingListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Finding'
        paging:
          $ref: '#/components/schemas/Paging'

    # ============================================
    # ASSET SCHEMAS
    # ============================================
    Asset:
      type: object
      properties:
        id:
          type: string
        hostname:
          type: string
        ipAddress:
          type: string
        type:
          type: string
          enum:
            - server
            - workstation
            - container
            - cloud_resource
            - network_device
        os:
          type: string
        tags:
          type: array
          items:
            type: string
        lastSeen:
          type: string
          format: date-time

    AssetDetail:
      allOf:
        - $ref: '#/components/schemas/Asset'
        - type: object
          properties:
            criticality:
              type: string
              enum: [critical, high, medium, low]
            owner:
              type: string
              format: email
            findings:
              type: array
              items:
                $ref: '#/components/schemas/Finding'
            vulnerabilities:
              type: array
              items:
                $ref: '#/components/schemas/Vulnerability'
            metadata:
              type: object

    AssetListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Asset'
        paging:
          $ref: '#/components/schemas/Paging'

    # ============================================
    # VULNERABILITY SCHEMAS
    # ============================================
    Vulnerability:
      type: object
      properties:
        id:
          type: string
        cveId:
          type: string
        title:
          type: string
        severity:
          $ref: '#/components/schemas/Severity'
        cvssScore:
          type: number
        affectedAssets:
          type: integer
        firstSeen:
          type: string
          format: date-time

    VulnerabilityListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Vulnerability'
        paging:
          $ref: '#/components/schemas/Paging'

    VulnerabilityTrendResponse:
      type: object
      properties:
        data:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                format: date
              critical:
                type: integer
              high:
                type: integer
              medium:
                type: integer
              low:
                type: integer
              total:
                type: integer

    # ============================================
    # COMPLIANCE SCHEMAS
    # ============================================
    ComplianceStatusResponse:
      type: object
      properties:
        overallScore:
          type: number
        frameworks:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              name:
                type: string
              score:
                type: number
              status:
                type: string
                enum: [compliant, non_compliant, partial]

    ComplianceFramework:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        version:
          type: string
        score:
          type: number
        controlsTotal:
          type: integer
        controlsPassed:
          type: integer
        controlsFailed:
          type: integer

    ComplianceFrameworkDetail:
      allOf:
        - $ref: '#/components/schemas/ComplianceFramework'
        - type: object
          properties:
            controls:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  status:
                    type: string
                    enum: [passed, failed, not_applicable]
                  findings:
                    type: array
                    items:
                      $ref: '#/components/schemas/Finding'

    ComplianceFrameworkListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/ComplianceFramework'

    # ============================================
    # CONNECTOR SCHEMAS
    # ============================================
    Connector:
      type: object
      properties:
        id:
          type: string
        type:
          type: string
        name:
          type: string
        status:
          type: string
          enum: [active, inactive, error, rate_limited]
        lastSync:
          type: string
          format: date-time
        findingsCount:
          type: integer
        syncFrequency:
          type: integer
          description: Sync frequency in minutes

    ConnectorListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Connector'

    ConnectorHealthResponse:
      type: object
      properties:
        connectors:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              name:
                type: string
              status:
                type: string
                enum: [healthy, degraded, unhealthy]
              lastSync:
                type: string
                format: date-time
              error:
                type: string

    CreateConnectorRequest:
      type: object
      required:
        - type
        - name
        - credentials
      properties:
        type:
          type: string
        name:
          type: string
        credentials:
          type: object
          properties:
            type:
              type: string
              enum: [api_key, oauth2, aws_role]
            apiKey:
              type: string
            clientId:
              type: string
            clientSecret:
              type: string
        sync:
          type: object
          properties:
            frequency:
              type: integer
              default: 15
            batchSize:
              type: integer
              default: 100

    UpdateConnectorRequest:
      type: object
      properties:
        name:
          type: string
        sync:
          type: object
          properties:
            frequency:
              type: integer
            enabled:
              type: boolean

    # ============================================
    # SECURITY DETECTION SCHEMAS
    # ============================================
    SecurityDetection:
      type: object
      properties:
        accountId:
          type: integer
        detectionId:
          type: integer
        incidentId:
          type: string
        description:
          type: string
        severity:
          type: integer
          minimum: 1
          maximum: 5
        detectionType:
          type: string
          enum: [INCIDENT, ALERT, THREAT]
        ticketStatus:
          type: string
          enum: [PENDING, IN_PROGRESS, RESOLVED, DISMISSED]
        eventCount:
          type: integer
        startTime:
          type: string
          format: date-time
        lastUpdatedTime:
          type: string
          format: date-time
        deliveryReceipts:
          type: array
          items:
            type: object
        categories:
          type: array
          items:
            type: string

    SecurityDetectionListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/SecurityDetection'
        paging:
          type: object
          properties:
            before:
              type: string
              nullable: true
            after:
              type: string
              nullable: true

    # ============================================
    # METRICS SCHEMAS
    # ============================================
    SecurityScoreResponse:
      type: object
      properties:
        score:
          type: integer
          minimum: 0
          maximum: 100
        trend:
          type: string
          enum: [improving, stable, declining]
        breakdown:
          type: object
          properties:
            vulnerabilities:
              type: integer
            compliance:
              type: integer
            alerts:
              type: integer
            configuration:
              type: integer
        history:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                format: date
              score:
                type: integer

    RiskHeatmapResponse:
      type: object
      properties:
        data:
          type: array
          items:
            type: object
            properties:
              category:
                type: string
              severity:
                $ref: '#/components/schemas/Severity'
              count:
                type: integer

    # ============================================
    # REPORT SCHEMAS
    # ============================================
    Report:
      type: object
      properties:
        id:
          type: string
        type:
          type: string
          enum: [security_summary, compliance, vulnerability, executive]
        status:
          type: string
          enum: [queued, generating, completed, failed]
        createdAt:
          type: string
          format: date-time
        completedAt:
          type: string
          format: date-time
        downloadUrl:
          type: string
          format: uri
        expiresAt:
          type: string
          format: date-time

    ReportListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Report'
        paging:
          $ref: '#/components/schemas/Paging'

    GenerateReportRequest:
      type: object
      required:
        - type
      properties:
        type:
          type: string
          enum: [security_summary, compliance, vulnerability, executive]
        format:
          type: string
          enum: [pdf, csv, json]
          default: pdf
        dateRange:
          type: object
          properties:
            start:
              type: string
              format: date
            end:
              type: string
              format: date
        filters:
          type: object
          properties:
            severity:
              type: array
              items:
                $ref: '#/components/schemas/Severity'
            sources:
              type: array
              items:
                type: string

    # ============================================
    # WEBHOOK SCHEMAS
    # ============================================
    Webhook:
      type: object
      properties:
        id:
          type: string
        url:
          type: string
          format: uri
        events:
          type: array
          items:
            type: string
        secret:
          type: string
          description: Only returned on creation
        active:
          type: boolean
        createdAt:
          type: string
          format: date-time

    WebhookListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Webhook'

    CreateWebhookRequest:
      type: object
      required:
        - url
        - events
      properties:
        url:
          type: string
          format: uri
        events:
          type: array
          items:
            type: string
            enum:
              - alert.created
              - alert.updated
              - alert.resolved
              - finding.created
              - finding.resolved
              - asset.discovered
              - asset.removed
              - connector.connected
              - connector.disconnected
              - connector.error
              - compliance.status_changed
              - vulnerability.discovered
              - vulnerability.remediated

    # ============================================
    # SECURE NOTE SCHEMAS
    # ============================================
    SecureNote:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        content:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    SecureNoteListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/SecureNote'

    CreateSecureNoteRequest:
      type: object
      required:
        - title
        - content
      properties:
        title:
          type: string
          maxLength: 255
        content:
          type: string

    UpdateSecureNoteRequest:
      type: object
      properties:
        title:
          type: string
          maxLength: 255
        content:
          type: string
```

---

## Implementation Notes

### Generating from Platform Code

The OpenAPI specification above was derived from analyzing:

1. **API Hook Files**: `/libs/*/react-api-*/src/lib/use*.tsx`
2. **Zod Schemas**: Type definitions in hook files
3. **Mock Handlers**: MSW handlers in `*.mock.ts` files
4. **Base URL Configuration**: `/libs/shared/react-api-base/src/utils.tsx`

### Recommended Tools

| Tool | Purpose |
|------|---------|
| **Stoplight Studio** | OpenAPI editing and validation |
| **Redoc** | API documentation generation |
| **Swagger UI** | Interactive API explorer |
| **openapi-generator** | SDK generation |
| **Prism** | Mock server from OpenAPI |

### Validation Command

```bash
# Validate OpenAPI specification
npx @redocly/cli lint openapi.yaml

# Generate TypeScript types
npx openapi-typescript openapi.yaml -o types/api.d.ts

# Generate SDK
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o sdk/typescript
```
