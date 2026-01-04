#!/usr/bin/env bash
# ============================================
# Argus Local Kubernetes Development Helper
# ============================================
# Usage:
#   ./scripts/local-k8s.sh up      - Deploy all infrastructure
#   ./scripts/local-k8s.sh down    - Remove all infrastructure
#   ./scripts/local-k8s.sh status  - Check status
#   ./scripts/local-k8s.sh logs    - View logs
#   ./scripts/local-k8s.sh reset   - Delete and recreate everything
#   ./scripts/local-k8s.sh connect - Port-forward services
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$REPO_ROOT/deploy/local"
NAMESPACE="argus-dev"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Is your cluster running?"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

deploy_infrastructure() {
    log_info "Deploying Argus infrastructure to Kubernetes..."

    # Apply all manifests using kustomize
    kubectl apply -k "$DEPLOY_DIR"

    log_info "Waiting for pods to be ready..."

    # Wait for each component
    log_info "Waiting for ClickHouse..."
    kubectl wait --for=condition=ready pod -l app=clickhouse -n "$NAMESPACE" --timeout=180s || true

    log_info "Waiting for Redis..."
    kubectl wait --for=condition=ready pod -l app=redis -n "$NAMESPACE" --timeout=60s || true

    log_info "Waiting for Zookeeper..."
    kubectl wait --for=condition=ready pod -l app=zookeeper -n "$NAMESPACE" --timeout=120s || true

    log_info "Waiting for Kafka..."
    kubectl wait --for=condition=ready pod -l app=kafka -n "$NAMESPACE" --timeout=180s || true

    log_info "Waiting for NebulaGraph..."
    kubectl wait --for=condition=ready pod -l app=nebula-metad -n "$NAMESPACE" --timeout=120s || true
    kubectl wait --for=condition=ready pod -l app=nebula-graphd -n "$NAMESPACE" --timeout=120s || true
    kubectl wait --for=condition=ready pod -l app=nebula-storaged -n "$NAMESPACE" --timeout=120s || true

    log_info "Waiting for SigNoz..."
    kubectl wait --for=condition=ready pod -l app=signoz -n "$NAMESPACE" --timeout=180s || true

    log_success "Infrastructure deployed successfully!"

    print_access_info
}

teardown_infrastructure() {
    log_info "Removing Argus infrastructure from Kubernetes..."

    kubectl delete -k "$DEPLOY_DIR" --ignore-not-found=true

    log_success "Infrastructure removed"
}

reset_infrastructure() {
    log_warn "This will delete all data and recreate the infrastructure."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        teardown_infrastructure

        log_info "Deleting persistent volume claims..."
        kubectl delete pvc --all -n "$NAMESPACE" --ignore-not-found=true || true

        log_info "Waiting for cleanup..."
        sleep 5

        deploy_infrastructure
    else
        log_info "Reset cancelled"
    fi
}

show_status() {
    log_info "Argus Development Environment Status"
    echo ""

    echo "=== Namespace ==="
    kubectl get namespace "$NAMESPACE" 2>/dev/null || echo "Namespace not found"
    echo ""

    echo "=== Pods ==="
    kubectl get pods -n "$NAMESPACE" -o wide 2>/dev/null || echo "No pods found"
    echo ""

    echo "=== Services ==="
    kubectl get svc -n "$NAMESPACE" 2>/dev/null || echo "No services found"
    echo ""

    echo "=== Persistent Volume Claims ==="
    kubectl get pvc -n "$NAMESPACE" 2>/dev/null || echo "No PVCs found"
    echo ""

    echo "=== Resource Usage ==="
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "Metrics not available (install metrics-server)"
}

show_logs() {
    local service="${2:-}"

    if [ -z "$service" ]; then
        log_info "Available services: clickhouse, redis, kafka, zookeeper, kafka-ui, nebula-metad, nebula-graphd, nebula-storaged, signoz"
        read -p "Enter service name: " service
    fi

    log_info "Showing logs for $service..."
    kubectl logs -f -l app="$service" -n "$NAMESPACE" --tail=100
}

port_forward() {
    log_info "Setting up port forwarding for local access..."

    # Kill any existing port-forwards
    pkill -f "kubectl port-forward.*argus-dev" 2>/dev/null || true

    # Start port forwards in background
    log_info "ClickHouse HTTP: localhost:8123"
    kubectl port-forward svc/clickhouse 8123:8123 -n "$NAMESPACE" &

    log_info "ClickHouse Native: localhost:9000"
    kubectl port-forward svc/clickhouse 9000:9000 -n "$NAMESPACE" &

    log_info "NebulaGraph: localhost:9669"
    kubectl port-forward svc/nebula-graphd 9669:9669 -n "$NAMESPACE" &

    log_info "Redis: localhost:6379"
    kubectl port-forward svc/redis 6379:6379 -n "$NAMESPACE" &

    log_info "Kafka: localhost:9092"
    kubectl port-forward svc/kafka 9092:9092 -n "$NAMESPACE" &

    log_info "Kafka UI: localhost:8080"
    kubectl port-forward svc/kafka-ui 8080:8080 -n "$NAMESPACE" &

    log_info "SigNoz UI: localhost:3301"
    kubectl port-forward svc/signoz 3301:3301 -n "$NAMESPACE" &

    log_info "OTLP gRPC: localhost:4317"
    kubectl port-forward svc/signoz 4317:4317 -n "$NAMESPACE" &

    log_success "Port forwarding started. Press Ctrl+C to stop all."

    # Wait for Ctrl+C
    wait
}

print_access_info() {
    echo ""
    echo "============================================"
    echo "  Argus Local Development Environment"
    echo "============================================"
    echo ""
    echo "Option 1: Use NodePort services (if supported)"
    echo "  ClickHouse HTTP:    http://localhost:30123"
    echo "  ClickHouse Native:  localhost:30900"
    echo "  NebulaGraph:        localhost:30669"
    echo "  Redis:              localhost:30379"
    echo "  Kafka:              localhost:30092"
    echo "  Kafka UI:           http://localhost:30080"
    echo "  SigNoz:             http://localhost:30301"
    echo ""
    echo "Option 2: Use port-forwarding (recommended)"
    echo "  Run: ./scripts/local-k8s.sh connect"
    echo ""
    echo "  Then access services at their default ports:"
    echo "    ClickHouse:       localhost:8123, localhost:9000"
    echo "    NebulaGraph:      localhost:9669"
    echo "    Redis:            localhost:6379"
    echo "    Kafka:            localhost:9092"
    echo "    Kafka UI:         http://localhost:8080"
    echo "    SigNoz:           http://localhost:3301"
    echo ""
    echo "NebulaGraph Console:"
    echo "  kubectl exec -it nebula-console -n argus-dev -- nebula-console -addr nebula-graphd -port 9669 -u root -p nebula"
    echo ""
    echo "============================================"
}

init_nebula_schema() {
    log_info "Initializing NebulaGraph schema..."

    if [ -f "$REPO_ROOT/schemas/nebulagraph/SCHEMA.ngql" ]; then
        kubectl exec -i nebula-console -n "$NAMESPACE" -- \
            nebula-console -addr nebula-graphd -port 9669 -u root -p nebula \
            < "$REPO_ROOT/schemas/nebulagraph/SCHEMA.ngql"
        log_success "NebulaGraph schema initialized"
    else
        log_warn "Schema file not found at schemas/nebulagraph/SCHEMA.ngql"
    fi
}

init_clickhouse_schema() {
    log_info "Initializing ClickHouse schema..."

    for schema_file in "$REPO_ROOT"/schemas/clickhouse/*.sql; do
        if [ -f "$schema_file" ]; then
            log_info "Applying $(basename "$schema_file")..."
            kubectl exec -i clickhouse-0 -n "$NAMESPACE" -- \
                clickhouse-client --user argus --password argus_dev \
                < "$schema_file"
        fi
    done

    log_success "ClickHouse schema initialized"
}

# Main command handler
case "${1:-help}" in
    up|deploy|start)
        check_prerequisites
        deploy_infrastructure
        ;;
    down|delete|stop)
        check_prerequisites
        teardown_infrastructure
        ;;
    reset|recreate)
        check_prerequisites
        reset_infrastructure
        ;;
    status|ps)
        check_prerequisites
        show_status
        ;;
    logs)
        check_prerequisites
        show_logs "$@"
        ;;
    connect|forward|pf)
        check_prerequisites
        port_forward
        ;;
    init-schema)
        check_prerequisites
        init_nebula_schema
        init_clickhouse_schema
        ;;
    info|access)
        print_access_info
        ;;
    help|--help|-h)
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  up, deploy, start    Deploy infrastructure to local K8s"
        echo "  down, delete, stop   Remove infrastructure"
        echo "  reset, recreate      Delete everything and start fresh"
        echo "  status, ps           Show current status"
        echo "  logs [service]       View logs for a service"
        echo "  connect, forward     Set up port forwarding"
        echo "  init-schema          Initialize database schemas"
        echo "  info, access         Show access information"
        echo "  help                 Show this help"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
