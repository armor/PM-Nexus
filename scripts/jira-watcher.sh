#!/bin/bash
# JIRA Watcher Control Script
# Manages background process that watches for new JIRA issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/_bmad/data"
PID_FILE="$DATA_DIR/jira-watcher.pid"
LOG_FILE="$DATA_DIR/jira-watcher.log"
CONFIG_FILE="$PROJECT_ROOT/_bmad/config/jira-integration.yaml"

# Ensure data directory exists
mkdir -p "$DATA_DIR"

usage() {
    echo "Usage: $0 {start|stop|status|logs|once}"
    echo ""
    echo "Commands:"
    echo "  start   Start the watcher in background"
    echo "  stop    Stop the running watcher"
    echo "  status  Check if watcher is running"
    echo "  logs    Tail the watcher log file"
    echo "  once    Run a single poll cycle (for testing)"
    exit 1
}

check_mcp() {
    # Verify MCP server is configured
    if ! command -v claude &> /dev/null; then
        echo "Error: Claude CLI not found"
        exit 1
    fi
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

start_watcher() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Watcher already running (PID: $PID)"
            exit 1
        fi
    fi

    check_mcp

    echo "Starting JIRA watcher..."
    log "Watcher started"

    # Start background loop
    (
        while true; do
            log "Polling JIRA for new issues..."

            # Run the poll skill
            claude --skill bmad:bmm:workflows:jira-poll --quiet 2>> "$LOG_FILE" || true

            # Sleep for poll interval (default 5 minutes)
            sleep 300
        done
    ) &

    echo $! > "$PID_FILE"
    echo "Watcher started (PID: $(cat "$PID_FILE"))"
    echo "Logs: tail -f $LOG_FILE"
}

stop_watcher() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Watcher not running (no PID file)"
        exit 0
    fi

    PID=$(cat "$PID_FILE")

    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID" 2>/dev/null || true
        log "Watcher stopped"
        echo "Watcher stopped (was PID: $PID)"
    else
        echo "Watcher not running (stale PID file)"
    fi

    rm -f "$PID_FILE"
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Watcher running (PID: $PID)"
            echo ""
            echo "Last log entries:"
            tail -5 "$LOG_FILE" 2>/dev/null || echo "  (no logs yet)"
            exit 0
        fi
    fi
    echo "Watcher not running"
    exit 1
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found at: $LOG_FILE"
        exit 1
    fi
}

run_once() {
    check_mcp
    log "Running single poll cycle..."
    claude --skill bmad:bmm:workflows:jira-poll
}

case "${1:-}" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    once)
        run_once
        ;;
    *)
        usage
        ;;
esac
