# Nexus UI Uplift - Operations Runbook

> **Version:** 1.0
> **Last Updated:** 2026-01-03
> **Status:** Draft
> **On-Call:** PagerDuty escalation enabled

---

## 1. Overview

This runbook provides operational procedures for managing the Nexus platform in production.

### Key References

- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/) (2025)
- [Datadog Monitoring Best Practices](https://docs.datadoghq.com/getting_started/) (2025)
- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug/) (2025)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nexus Production                          │
├─────────────────────────────────────────────────────────────┤
│  CloudFront CDN → ALB → EKS Cluster                         │
│                                                              │
│  Services:                                                   │
│  ├── nexus-frontend (Next.js, 2-4 pods)                     │
│  ├── nexus-api-gateway (Kong, 2 pods)                       │
│  ├── nexus-auth-service (Node.js, 2-3 pods)                 │
│  ├── nexus-core-api (Node.js, 3-5 pods)                     │
│  ├── nexus-metrics-api (Node.js, 2-3 pods)                  │
│  └── nexus-connector-service (Node.js, 2-4 pods)            │
│                                                              │
│  Data:                                                       │
│  ├── RDS PostgreSQL (Multi-AZ)                              │
│  ├── ElastiCache Redis (Cluster)                            │
│  └── S3 (Assets, Backups)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Service Level Objectives (SLOs)

| Metric | SLO | SLI | Alert Threshold |
|--------|-----|-----|-----------------|
| Availability | 99.9% | (1 - error_rate) * 100 | < 99.5% |
| API Latency (P95) | < 200ms | histogram_quantile(0.95) | > 500ms |
| Error Rate | < 0.1% | errors / total_requests | > 1% |
| Apdex | > 0.95 | satisfied + (tolerating/2) / total | < 0.90 |

---

## 4. Monitoring & Alerting

### 4.1 Datadog Dashboards

| Dashboard | Purpose | Link |
|-----------|---------|------|
| Nexus Overview | High-level health | [Link] |
| API Performance | Latency, errors, throughput | [Link] |
| Database Metrics | RDS performance | [Link] |
| Kubernetes | Pod health, resources | [Link] |

### 4.2 Alert Runbooks

#### ALERT: Nexus API High Error Rate

**Severity:** Critical
**Threshold:** Error rate > 1% for 5 minutes

**Investigation Steps:**
1. Check Datadog APM for error traces
   ```
   service:nexus-core-api status:error
   ```
2. Check recent deployments
   ```bash
   kubectl -n nexus-prod rollout history deployment/nexus-core-api
   ```
3. Check database connectivity
   ```bash
   kubectl -n nexus-prod exec -it deploy/nexus-core-api -- nc -zv postgres.rds.amazonaws.com 5432
   ```
4. Check Redis connectivity
   ```bash
   kubectl -n nexus-prod exec -it deploy/nexus-core-api -- redis-cli -h redis.cache.amazonaws.com ping
   ```

**Resolution:**
- If recent deployment: Rollback
- If database issue: Check RDS console
- If Redis issue: Check ElastiCache console

---

#### ALERT: Nexus API High Latency

**Severity:** Warning
**Threshold:** P95 latency > 500ms for 10 minutes

**Investigation Steps:**
1. Check slow endpoints in Datadog APM
2. Check database query performance
   ```sql
   SELECT * FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY query_start;
   ```
3. Check Redis cache hit rate
4. Check pod resource utilization
   ```bash
   kubectl -n nexus-prod top pods
   ```

**Resolution:**
- If slow query: Optimize or add index
- If resource constraint: Scale pods
- If cache miss: Investigate cache invalidation

---

#### ALERT: Nexus Pod CrashLooping

**Severity:** Critical
**Threshold:** > 3 restarts in 10 minutes

**Investigation Steps:**
1. Check pod status
   ```bash
   kubectl -n nexus-prod get pods
   kubectl -n nexus-prod describe pod <pod-name>
   ```
2. Check pod logs
   ```bash
   kubectl -n nexus-prod logs <pod-name> --previous
   ```
3. Check events
   ```bash
   kubectl -n nexus-prod get events --sort-by='.lastTimestamp'
   ```

**Resolution:**
- If OOM: Increase memory limits
- If config error: Fix and redeploy
- If dependency issue: Check external services

---

### 4.3 On-Call Responsibilities

| Time | Primary | Backup |
|------|---------|--------|
| Business Hours | Platform Team | SRE Team |
| After Hours | On-Call Engineer | Escalation Manager |

**Escalation Path:**
```
L1: On-Call Engineer (< 15 min response)
    │
    ├── Resolved: Document and close
    │
    ▼
L2: Platform Team Lead (< 30 min response)
    │
    ├── Resolved: Root cause analysis
    │
    ▼
L3: Engineering Manager (< 1 hour response)
    │
    └── Major incident: All-hands
```

---

## 5. Common Operations

### 5.1 Deployment

**Deploy to Staging:**
```bash
# Trigger via GitHub Actions or manual
gh workflow run deploy-staging.yml -f version=v1.2.3
```

**Deploy to Production:**
```bash
# Requires approval
gh workflow run deploy-production.yml -f version=v1.2.3

# Or via Helm
helm upgrade nexus-api ./charts/nexus-api \
  --namespace nexus-prod \
  --set image.tag=v1.2.3 \
  --wait
```

**Verify Deployment:**
```bash
kubectl -n nexus-prod rollout status deployment/nexus-core-api
kubectl -n nexus-prod get pods -l app=nexus-core-api
```

### 5.2 Rollback

**Rollback Helm Release:**
```bash
# List revisions
helm -n nexus-prod history nexus-api

# Rollback to previous
helm -n nexus-prod rollback nexus-api

# Rollback to specific revision
helm -n nexus-prod rollback nexus-api 5
```

**Rollback Kubernetes Deployment:**
```bash
kubectl -n nexus-prod rollout undo deployment/nexus-core-api
kubectl -n nexus-prod rollout status deployment/nexus-core-api
```

### 5.3 Scaling

**Manual Scaling:**
```bash
# Scale deployment
kubectl -n nexus-prod scale deployment/nexus-core-api --replicas=5

# Verify
kubectl -n nexus-prod get pods -l app=nexus-core-api
```

**HPA Status:**
```bash
kubectl -n nexus-prod get hpa
kubectl -n nexus-prod describe hpa nexus-core-api-hpa
```

### 5.4 Database Operations

**Connect to RDS:**
```bash
# Get credentials from Secrets Manager
aws secretsmanager get-secret-value --secret-id nexus/prod/database

# Connect via bastion
psql -h nexus-prod.xxx.rds.amazonaws.com -U nexus_admin -d nexus
```

**Run Migration:**
```bash
# Via pod exec
kubectl -n nexus-prod exec -it deploy/nexus-core-api -- npm run migrate

# Or dedicated job
kubectl apply -f k8s/jobs/db-migration.yaml
```

**Backup Database:**
```bash
# Automated via RDS snapshots, manual if needed
aws rds create-db-snapshot \
  --db-instance-identifier nexus-prod \
  --db-snapshot-identifier nexus-manual-$(date +%Y%m%d)
```

### 5.5 Cache Operations

**Flush Redis Cache:**
```bash
# Connect to Redis
kubectl -n nexus-prod exec -it deploy/nexus-core-api -- redis-cli -h redis.cache.amazonaws.com

# Flush specific pattern (careful!)
redis-cli -h redis.cache.amazonaws.com KEYS "cache:*" | xargs redis-cli DEL

# Flush all (DANGER - use only if necessary)
redis-cli -h redis.cache.amazonaws.com FLUSHALL
```

---

## 6. Incident Response

### 6.1 Incident Severity

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| **SEV1** | Complete outage | < 15 min | All users affected |
| **SEV2** | Major degradation | < 30 min | Core feature down |
| **SEV3** | Minor degradation | < 2 hours | Non-critical feature |
| **SEV4** | Low impact | < 24 hours | Cosmetic issue |

### 6.2 Incident Process

```
1. DETECT
   └── Alert fires or user report

2. TRIAGE (< 5 min)
   ├── Assign severity
   ├── Page on-call if SEV1/2
   └── Create incident channel

3. INVESTIGATE (ongoing)
   ├── Gather data
   ├── Form hypothesis
   └── Test hypothesis

4. MITIGATE (ASAP)
   ├── Apply fix or workaround
   ├── Verify resolution
   └── Monitor for recurrence

5. COMMUNICATE
   ├── Update status page
   ├── Notify stakeholders
   └── Send customer communication

6. POST-INCIDENT
   ├── Root cause analysis
   ├── Write post-mortem
   └── Create follow-up tasks
```

### 6.3 Communication Templates

**Status Page Update:**
```
[Investigating] We are investigating reports of elevated error rates
affecting the Nexus dashboard. Users may experience slow load times.
We will provide an update in 15 minutes.

[Identified] We have identified the root cause as a database connection
issue. Our team is working on a fix.

[Resolved] The issue has been resolved. All services are operating normally.
We will publish a post-mortem within 48 hours.
```

---

## 7. Maintenance Procedures

### 7.1 Scheduled Maintenance

**Notification Timeline:**
- 7 days: Initial notification
- 24 hours: Reminder
- 1 hour: Final notice
- Post: Completion notice

**Maintenance Window:**
- Standard: Saturday 02:00-06:00 UTC
- Emergency: As needed with approval

### 7.2 Certificate Rotation

**ACM Certificates:**
- Automatic renewal via ACM
- Monitor: Certificate Expiry dashboard
- Alert: 30 days before expiry

**Internal Certificates:**
```bash
# Check cert expiry
kubectl -n nexus-prod get secret tls-cert -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -enddate

# Rotate via cert-manager
kubectl -n nexus-prod delete certificate nexus-tls
kubectl -n nexus-prod apply -f k8s/certificates/nexus-tls.yaml
```

### 7.3 Secret Rotation

**Database Password:**
```bash
# 1. Generate new password
aws secretsmanager get-random-password --password-length 32

# 2. Update in Secrets Manager
aws secretsmanager update-secret --secret-id nexus/prod/database \
  --secret-string '{"password":"NEW_PASSWORD"}'

# 3. Restart pods to pick up new secret
kubectl -n nexus-prod rollout restart deployment/nexus-core-api
```

---

## 8. Disaster Recovery

### 8.1 Recovery Objectives

| Metric | Target |
|--------|--------|
| RTO (Recovery Time) | < 1 hour |
| RPO (Recovery Point) | < 15 minutes |

### 8.2 Backup Schedule

| Resource | Frequency | Retention | Location |
|----------|-----------|-----------|----------|
| RDS Snapshots | Daily | 30 days | AWS RDS |
| RDS PITR | Continuous | 7 days | AWS RDS |
| S3 Assets | Versioned | 90 days | S3 Cross-Region |
| K8s Configs | Every deploy | Git | GitHub |
| Secrets | On change | Versioned | Secrets Manager |

### 8.3 Recovery Procedures

**Database Recovery:**
```bash
# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier nexus-prod-restored \
  --db-snapshot-identifier nexus-prod-snapshot-20260103

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier nexus-prod \
  --target-db-instance-identifier nexus-prod-pitr \
  --restore-time 2026-01-03T10:00:00Z
```

**Kubernetes Recovery:**
```bash
# Restore from Git
git checkout v1.2.3
kubectl apply -f k8s/

# Or restore from backup
velero restore create --from-backup nexus-backup-20260103
```

---

## 9. Performance Tuning

### 9.1 Database Optimization

**Identify Slow Queries:**
```sql
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

**Add Index:**
```sql
-- Analyze query plan first
EXPLAIN ANALYZE SELECT * FROM alerts WHERE organization_id = 'xxx' AND status = 'open';

-- Add index if full scan
CREATE INDEX CONCURRENTLY idx_alerts_org_status ON alerts(organization_id, status);
```

### 9.2 Application Tuning

**Node.js Memory:**
```yaml
# Increase memory limit
resources:
  limits:
    memory: 2Gi
  requests:
    memory: 1Gi
```

**Connection Pooling:**
```typescript
// Database pool settings
const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

---

## 10. Troubleshooting

### 10.1 Quick Diagnostics

```bash
# Overall cluster health
kubectl -n nexus-prod get pods
kubectl -n nexus-prod get events --sort-by='.lastTimestamp' | head -20

# Service health
kubectl -n nexus-prod get endpoints
kubectl -n nexus-prod describe service nexus-core-api

# Resource usage
kubectl -n nexus-prod top pods
kubectl -n nexus-prod top nodes

# Logs (last 100 lines)
kubectl -n nexus-prod logs -l app=nexus-core-api --tail=100
```

### 10.2 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Pods pending | Resource constraints | Scale nodes or reduce requests |
| CrashLoopBackOff | App error or config | Check logs, fix issue |
| ImagePullBackOff | Registry auth or image missing | Check ECR, fix image tag |
| Connection refused | Service not ready | Check readiness probe |
| 502 Bad Gateway | Backend not responding | Check pod health |
| High latency | Resource saturation | Scale or optimize |

---

## 11. Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| Platform Lead | [Name] | [Email] | PagerDuty |
| SRE Lead | [Name] | [Email] | PagerDuty |
| DBA | [Name] | [Email] | Slack |
| Security | [Name] | [Email] | PagerDuty |
| AWS Support | - | AWS Console | Support Case |

---

## 12. References

### Internal
- Architecture Document
- Security & Compliance
- Deployment Playbook

### External
- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug/) (2025)
- [AWS EKS User Guide](https://docs.aws.amazon.com/eks/) (2025)
- [Datadog APM](https://docs.datadoghq.com/tracing/) (2025)

---

*This runbook is maintained by the Platform team. Review monthly.*
