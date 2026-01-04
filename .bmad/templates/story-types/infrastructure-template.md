# Infrastructure Story Template

> **Template Type:** Infrastructure (Helm, Kubernetes, Databases)
> **Applies To:** Deployments, StatefulSets, ConfigMaps, database setup

---

## Pre-filled Sections for Infrastructure Stories

### Standard Helm Chart Structure
```
deploy/charts/{{chart-name}}/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml OR statefulset.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pdb.yaml
│   └── serviceaccount.yaml
└── README.md
```

### Standard Verification Commands
```bash
# Helm lint
helm lint deploy/charts/{{chart-name}}

# Template render
helm template {{release}} deploy/charts/{{chart-name}}

# Dry run
helm template {{release}} deploy/charts/{{chart-name}} | kubectl apply --dry-run=client -f -

# Deploy
helm install {{release}} deploy/charts/{{chart-name}} -n {{namespace}}

# Verify pods
kubectl get pods -l app.kubernetes.io/name={{app-name}} -n {{namespace}}

# Verify PVCs (if stateful)
kubectl get pvc -l app.kubernetes.io/name={{app-name}} -n {{namespace}}
```

### Standard values.yaml Structure
```yaml
# {{Chart Name}} Configuration
replicaCount: 2

image:
  repository: {{image}}
  tag: "{{version}}"
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: "{{cpu_request}}"
    memory: "{{memory_request}}"
  limits:
    cpu: "{{cpu_limit}}"
    memory: "{{memory_limit}}"

service:
  type: ClusterIP
  port: {{port}}

probes:
  readiness:
    path: /healthz
    initialDelaySeconds: 10
    periodSeconds: 10
  liveness:
    path: /healthz
    initialDelaySeconds: 30
    periodSeconds: 20
```

### Standard Probe Configuration
```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 30
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 3
```

---

## Infrastructure Story AI Prompt Template

```
IMPLEMENT {{STORY_ID}}: {{STORY_TITLE}}

CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are deploying {{WHAT}} to Kubernetes for Armor Argus.
This component provides {{PURPOSE}}.

KUBERNETES RESOURCES TO CREATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {{RESOURCE_1}}: {{PURPOSE_1}}
2. {{RESOURCE_2}}: {{PURPOSE_2}}
3. {{RESOURCE_3}}: {{PURPOSE_3}}

TARGET FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
deploy/charts/{{chart}}/
├── Chart.yaml
├── values.yaml
└── templates/
    └── {{template}}.yaml

IMPLEMENTATION STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Create Helm chart directory structure
2. Define values.yaml with all configuration
3. Create {{resource}} template
4. Add service template
5. Add probes and resource limits
6. Test deployment

EXACT YAML:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{EXACT_YAML}}

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm lint deploy/charts/{{chart}}
# Expected: 0 errors

kubectl get pods -l app.kubernetes.io/name={{app}}
# Expected: {{EXPECTED_POD_COUNT}} pods Running

kubectl exec {{pod}} -- {{HEALTH_CHECK_COMMAND}}
# Expected: {{EXPECTED_OUTPUT}}

ROLLBACK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm uninstall {{release}} -n {{namespace}}
kubectl delete pvc -l app.kubernetes.io/name={{app}} # if data loss acceptable
```
