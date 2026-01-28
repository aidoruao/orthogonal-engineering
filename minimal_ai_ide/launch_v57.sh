#!/bin/bash
# MAXIMAL ORACLE v57 - LAUNCHER

echo "========================================"
echo "MAXIMAL ORACLE v57 - LAUNCHER"
echo "========================================"
echo ""

# Load environment variables from .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "ERROR: DEEPSEEK_API_KEY is not set"
    echo "Please edit .env file and add your API key"
    exit 1
fi

# Run the system
echo "Starting Maximal Oracle v57..."
echo "API Key: ${DEEPSEEK_API_KEY:0:10}... (hidden)"
echo "Mode: $V57_MODE"
echo "Workspace: $WORKSPACE_DIR"
echo "Prometheus: http://localhost:$PROMETHEUS_PORT"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

python maximal_oracle_v57.py
