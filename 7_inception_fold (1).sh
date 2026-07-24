#!/usr/bin/env bash
# 7_inception_fold.sh — The Orchestrator
# Responsibility: Starts all 6 files in the correct order, monitors PIDs,
# and restarts any file that dies. 50 lines. Operational sanity.
#
# Run: chmod +x 7_inception_fold.sh && ./7_inception_fold.sh
# Or:  ./cycle --input "text" --horizon 5years (symlink to this script)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Configuration ---
SHM_NAME="/oe_thermo_ring"
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# --- Cleanup on exit ---
cleanup() {
    echo "[ORCHESTRATOR] Shutdown signal received. Killing all children..."
    jobs -p | xargs -r kill -TERM 2>/dev/null || true
    sleep 1
    jobs -p | xargs -r kill -KILL 2>/dev/null || true
    shm_unlink "$SHM_NAME" 2>/dev/null || true
    echo "[ORCHESTRATOR] All processes terminated."
    exit 0
}
trap cleanup INT TERM EXIT

# --- Stage launcher ---
launch_stage() {
    local name="$1"
    local cmd="$2"
    local logfile="$LOG_DIR/${name}.log"

    echo "[ORCHESTRATOR] Starting $name..."
    eval "$cmd" > "$logfile" 2>&1 &
    local pid=$!
    echo "$pid" > "$LOG_DIR/${name}.pid"
    echo "[ORCHESTRATOR] $name PID=$pid"
}

# --- Health check ---
health_check() {
    local name="$1"
    local pidfile="$LOG_DIR/${name}.pid"
    if [[ ! -f "$pidfile" ]]; then return 1; fi
    local pid=$(cat "$pidfile")
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "[ORCHESTRATOR] WARNING: $name (PID=$pid) died. Restarting..."
        return 1
    fi
    return 0
}

# --- Main sequence ---
echo "[ORCHESTRATOR] Inception Fold v1.0 — Thermodynamic Kernel Orchestrator"
echo "[ORCHESTRATOR] Directory: $SCRIPT_DIR"

# 1. Ensure registry exists
if [[ ! -f "6_paradox_registry.sqlite" ]]; then
    echo "[ORCHESTRATOR] Initializing paradox registry..."
    python3 6_paradox_registry.py
fi

# 2. Launch the Thermo Kernel (the cycle scheduler)
launch_stage "thermo_kernel" "sudo ./thermo_kernel"
sleep 2

# 3. Launch the Compressor (input harvester)
if [[ -f "1_compressor.rs" ]]; then
    if [[ ! -x "compressor" ]]; then
        echo "[ORCHESTRATOR] Building compressor..."
        rustc -O -o compressor 1_compressor.rs 2>/dev/null || echo "[ORCHESTRATOR] WARNING: rustc not found, compressor unavailable"
    fi
fi

# 4. The kernel manages the other stages internally via its cycle loop.
#    We just monitor the kernel and restart it if it dies.

# --- Monitor loop ---
echo "[ORCHESTRATOR] Entering monitor loop. Press Ctrl-C to shutdown."
while true; do
    sleep 5

    if ! health_check "thermo_kernel"; then
        echo "[ORCHESTRATOR] CRITICAL: Thermo Kernel died. Rebooting cycle..."
        launch_stage "thermo_kernel" "sudo ./thermo_kernel"
        sleep 2
    fi

    # Check for self-destruct fasting period
    if [[ -f "$LOG_DIR/thermo_kernel.log" ]]; then
        if grep -q "FASTING PERIOD ACTIVE" "$LOG_DIR/thermo_kernel.log" 2>/dev/null; then
            echo "[ORCHESTRATOR] Self-destruct clause triggered. Human-only fasting active."
            echo "[ORCHESTRATOR] Halting all AI cycles. Operator must take manual control."
            break
        fi
    fi
done

# --- Symlink trick for CLI usage ---
# ln -s 7_inception_fold.sh cycle
# ./cycle --input "any text" --horizon 5years
if [[ "${1:-}" == "--input" ]]; then
    INPUT="$2"
    HORIZON="${4:-5years}"
    echo "$INPUT" | ./compressor | elixir 2_condenser.ex | julia 3_expansion_valve.jl | python3 4_evaporator.py
    exit 0
fi
