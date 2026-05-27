#!/bin/bash
# YAA Dashboard — run in a second terminal: bash ~/oe-local/tools/yaa_dashboard.sh
while true; do
    clear
    echo "╔══════════════════════════════════════╗"
    echo "║     YAA DASHBOARD — Yeshua Agentic AI ║"
    echo "╠══════════════════════════════════════╣"
    echo "║ Bypasses: $(cat /tmp/yaa_bypass_count 2>/dev/null || echo 0)/10 max"
    echo "║ Merkle:   $(grep -o '"root_hash": "[a-f0-9]*"' ~/oe-local/merkle/global_root.json 2>/dev/null | cut -d'"' -f4 | head -c 16)..."
    echo "║ Scanner:  $(grep -o '"total_errors": [0-9]*' ~/oe-local/tools/yeshua_scan_results.json 2>/dev/null | head -1) errors"
    echo "║ Manifest: $(grep -o '"total_files": [0-9]*' ~/oe-local/lean4/mathlib_oe_manifest.json 2>/dev/null | head -1) .olean files"
    echo "║ CPU:      $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% user"
    echo "║ Memory:   $(free -h | awk '/Mem:/ {print $3}') used"
    echo "╚══════════════════════════════════════╝"
    sleep 2
done
