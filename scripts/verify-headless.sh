#!/usr/bin/env bash
# ============================================
# Verify Integration is Running Headless
# ============================================
# Usage: ./scripts/verify-headless.sh <system-name> [namespace]
#
# This script verifies that an integrated system:
# 1. Has no UI ports exposed
# 2. Has API responding
# 3. Has UI endpoints disabled
# 4. Has proper annotations
# 5. Has NetworkPolicy
# ============================================

set -euo pipefail

SYSTEM=${1:-}
NAMESPACE=${2:-argus}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}PASS${NC}: $1"; }
fail() { echo -e "${RED}FAIL${NC}: $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "${YELLOW}WARN${NC}: $1"; }
info() { echo -e "INFO: $1"; }

FAILURES=0

if [ -z "$SYSTEM" ]; then
    echo "Usage: $0 <system-name> [namespace]"
    echo ""
    echo "Examples:"
    echo "  $0 defectdojo argus"
    echo "  $0 prowler argus"
    echo "  $0 trivy argus"
    exit 1
fi

echo "============================================"
echo "Verifying $SYSTEM is running headless"
echo "Namespace: $NAMESPACE"
echo "============================================"
echo ""

# --------------------------------------------
# 1. Check Deployment Exists
# --------------------------------------------
info "Checking deployment exists..."
if ! kubectl get deployment "$SYSTEM" -n "$NAMESPACE" &>/dev/null; then
    if kubectl get deployment "${SYSTEM}-api" -n "$NAMESPACE" &>/dev/null; then
        DEPLOY_NAME="${SYSTEM}-api"
    else
        fail "Deployment $SYSTEM not found in namespace $NAMESPACE"
        exit 1
    fi
else
    DEPLOY_NAME="$SYSTEM"
fi
pass "Deployment $DEPLOY_NAME exists"

# --------------------------------------------
# 2. Check Headless Annotation
# --------------------------------------------
info "Checking headless annotation..."
HEADLESS_ANNO=$(kubectl get deployment "$DEPLOY_NAME" -n "$NAMESPACE" \
    -o jsonpath='{.metadata.annotations.argus\.armor\.io/headless}' 2>/dev/null || echo "")

if [ "$HEADLESS_ANNO" == "true" ]; then
    pass "Deployment has argus.armor.io/headless=true annotation"
else
    fail "Deployment missing argus.armor.io/headless=true annotation"
fi

# --------------------------------------------
# 3. Check UI Disabled Annotation
# --------------------------------------------
info "Checking ui-disabled annotation..."
UI_DISABLED=$(kubectl get deployment "$DEPLOY_NAME" -n "$NAMESPACE" \
    -o jsonpath='{.metadata.annotations.argus\.armor\.io/ui-disabled}' 2>/dev/null || echo "")

if [ "$UI_DISABLED" == "true" ]; then
    pass "Deployment has argus.armor.io/ui-disabled=true annotation"
else
    warn "Deployment missing argus.armor.io/ui-disabled=true annotation"
fi

# --------------------------------------------
# 4. Check Service Ports
# --------------------------------------------
info "Checking Service ports..."
SERVICE_NAME=$(kubectl get svc -n "$NAMESPACE" -l app="$SYSTEM" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "$SYSTEM")

if kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE" &>/dev/null; then
    PORTS=$(kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.ports[*].port}')
    PORT_NAMES=$(kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.ports[*].name}')

    # Check for common UI ports
    UI_PORT_FOUND=false
    for port in $PORTS; do
        case $port in
            80|443|3000|4200|8081|8443)
                # These are commonly UI ports
                warn "Port $port found - verify this is not a UI port"
                ;;
        esac
    done

    # Check for UI-related port names
    for name in $PORT_NAMES; do
        case $name in
            *ui*|*web*|*frontend*|*dashboard*)
                fail "UI-related port name found: $name"
                UI_PORT_FOUND=true
                ;;
        esac
    done

    if [ "$UI_PORT_FOUND" == "false" ]; then
        pass "No obvious UI ports in Service (ports: $PORTS)"
    fi
else
    warn "Service $SERVICE_NAME not found"
fi

# --------------------------------------------
# 5. Check No LoadBalancer/NodePort
# --------------------------------------------
info "Checking Service type..."
SVC_TYPE=$(kubectl get svc "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.type}' 2>/dev/null || echo "ClusterIP")

if [ "$SVC_TYPE" == "ClusterIP" ]; then
    pass "Service type is ClusterIP (not externally exposed)"
else
    warn "Service type is $SVC_TYPE - verify this is intentional"
fi

# --------------------------------------------
# 6. Check No Ingress
# --------------------------------------------
info "Checking for Ingress..."
INGRESS=$(kubectl get ingress -n "$NAMESPACE" -l app="$SYSTEM" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

if [ -z "$INGRESS" ]; then
    pass "No Ingress found for $SYSTEM"
else
    fail "Ingress found: $INGRESS - UI should not be externally accessible"
fi

# --------------------------------------------
# 7. Check NetworkPolicy
# --------------------------------------------
info "Checking NetworkPolicy..."
NP=$(kubectl get networkpolicy -n "$NAMESPACE" -l app="$SYSTEM" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
NP_SPECIFIC=$(kubectl get networkpolicy "${SYSTEM}-api-only" -n "$NAMESPACE" -o name 2>/dev/null || echo "")

if [ -n "$NP" ] || [ -n "$NP_SPECIFIC" ]; then
    pass "NetworkPolicy exists"
else
    warn "No NetworkPolicy found - consider adding ${SYSTEM}-api-only"
fi

# --------------------------------------------
# 8. Check API Health (if pods running)
# --------------------------------------------
info "Checking API health..."
POD=$(kubectl get pods -n "$NAMESPACE" -l app="$SYSTEM" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$POD" ]; then
    # Try common API health endpoints
    API_ENDPOINTS=("/api/health" "/api/v1/health" "/api/v2/health" "/health" "/healthz" "/api/status")
    API_PORTS=("8080" "8000" "5000" "3000")

    API_HEALTHY=false
    for port in "${API_PORTS[@]}"; do
        for endpoint in "${API_ENDPOINTS[@]}"; do
            STATUS=$(kubectl exec -it "$POD" -n "$NAMESPACE" -- \
                curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}${endpoint}" 2>/dev/null || echo "000")
            if [ "$STATUS" == "200" ]; then
                pass "API healthy at port $port endpoint $endpoint"
                API_HEALTHY=true
                break 2
            fi
        done
    done

    if [ "$API_HEALTHY" == "false" ]; then
        warn "Could not verify API health - check manually"
    fi
else
    warn "No running pods found - cannot verify API health"
fi

# --------------------------------------------
# 9. Check UI Endpoints Disabled (if pods running)
# --------------------------------------------
info "Checking UI endpoints disabled..."
if [ -n "$POD" ]; then
    # Try common UI endpoints
    UI_ENDPOINTS=("/" "/index.html" "/login" "/dashboard" "/ui" "/app")
    UI_DISABLED_CHECK=true

    for port in "${API_PORTS[@]}"; do
        for endpoint in "${UI_ENDPOINTS[@]}"; do
            STATUS=$(kubectl exec -it "$POD" -n "$NAMESPACE" -- \
                curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}${endpoint}" 2>/dev/null || echo "000")

            if [ "$STATUS" == "200" ]; then
                # Check if it's returning HTML (UI) vs JSON (API)
                CONTENT_TYPE=$(kubectl exec -it "$POD" -n "$NAMESPACE" -- \
                    curl -s -I "http://localhost:${port}${endpoint}" 2>/dev/null | grep -i "content-type" || echo "")

                if echo "$CONTENT_TYPE" | grep -qi "text/html"; then
                    fail "UI endpoint responding with HTML at port $port$endpoint"
                    UI_DISABLED_CHECK=false
                fi
            fi
        done
    done

    if [ "$UI_DISABLED_CHECK" == "true" ]; then
        pass "UI endpoints not serving HTML content"
    fi
else
    warn "No running pods - cannot verify UI endpoints"
fi

# --------------------------------------------
# Summary
# --------------------------------------------
echo ""
echo "============================================"
echo "Verification Summary"
echo "============================================"

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ $SYSTEM verified as headless${NC}"
    exit 0
else
    echo -e "${RED}❌ $SYSTEM has $FAILURES failure(s)${NC}"
    echo ""
    echo "Please fix the issues above before merging."
    echo "See: docs/development/HEADLESS_INTEGRATION_GUIDE.md"
    exit 1
fi
