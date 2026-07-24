#!/usr/bin/env python3
"""
0_toolset_generator.py — The Meta-Engine

This file does NOT run in the main cycle.
It runs in a separate "workshop" environment, once per week.
It reads:
  - The last 1000 entries from the paradox_registry (cycle_audit table)
  - The logs from all 7 files (/logs/*.log)
  - The performance metrics from the thermo_kernel (shared memory)

It then GENERATES patch files (not full files) that improve the 7 core files.
These patches are applied via a separate "hot-swap" mechanism.

Philosophy: We don't improve the codebase. We improve THIS toolset,
which improves the codebase.
"""

import sqlite3
import json
import re
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent
LOG_DIR = REPO_ROOT / "logs"
DB_PATH = REPO_ROOT / "6_paradox_registry.sqlite"
PATCH_DIR = REPO_ROOT / "patches"
PATCH_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------
# Step 1: Read the "health" of the 7-file system
# ------------------------------------------------------------------
def read_cycle_health() -> Dict[str, Any]:
    """Query the paradox_registry for performance indicators."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Average inversion rate over last 100 cycles
    cursor.execute("""
        SELECT AVG(inversion_rate), COUNT(*)
        FROM cycle_audit
        WHERE timestamp > ?
    """, (time.time() - 7*24*3600,))
    avg_inv, count = cursor.fetchone()

    # Temperature trends
    cursor.execute("""
        SELECT AVG(temperature), MAX(temperature)
        FROM cycle_audit
        WHERE timestamp > ?
    """, (time.time() - 24*3600,))
    avg_temp, max_temp = cursor.fetchone()

    # Contradiction index drift (human overfit)
    cursor.execute("""
        SELECT AVG(short_term_choices), AVG(inverted_choices)
        FROM contradiction_index
    """)
    avg_short, avg_inv_choices = cursor.fetchone()

    conn.close()

    return {
        "avg_inversion_rate": avg_inv or 0.0,
        "cycle_count": count or 0,
        "avg_temp_c": avg_temp or 0.0,
        "max_temp_c": max_temp or 0.0,
        "human_short_term_ratio": (avg_short or 0) / max((avg_short or 0) + (avg_inv_choices or 1), 1),
        "database_size": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    }

# ------------------------------------------------------------------
# Step 2: Parse logs for warnings/errors
# ------------------------------------------------------------------
def parse_logs() -> Dict[str, List[str]]:
    """Extract warnings and errors from each file's log."""
    issues = {f"file_{i}": [] for i in range(1, 8)}

    for log_file in LOG_DIR.glob("*.log"):
        file_key = log_file.stem  # e.g., "thermo_kernel"
        with open(log_file, 'r') as f:
            for line in f:
                if "WARNING" in line or "ERROR" in line or "CRITICAL" in line:
                    issues.setdefault(file_key, []).append(line.strip()[:120])

    return issues

# ------------------------------------------------------------------
# Step 3: Generate Patches (The "Improvement" Layer)
# ------------------------------------------------------------------
def generate_patch_for_compressor(health: Dict, issues: Dict) -> str:
    """If entropy detection is too coarse, patch the Rust code."""
    if health["avg_inversion_rate"] < 0.1:
        # The compressor is not feeding interesting paradoxes.
        # Patch: Increase sensitivity to nested structures.
        return """
--- a/1_compressor.rs
+++ b/1_compressor.rs
@@ -42,7 +42,7 @@
     let mut linguistic_depth: u32 = 0;
     for pat in thought_pattern {
         let count = lower.matches(pat).count() as u32;
-        if count > linguistic_depth { linguistic_depth = count; }
+        if count > linguistic_depth { linguistic_depth = count * 2; }  // Amplify nested thoughts
     }
     let depth = if max_depth > linguistic_depth { max_depth } else { linguistic_depth };
-    if depth == 0 { 1 } else { depth }
+    if depth == 0 { 1 } else { depth + 1 }  // Always add 1 to force at least one inversion layer
"""
    return ""  # No patch needed

def generate_patch_for_condenser(health: Dict, issues: Dict) -> str:
    """If inversion_rate never approaches threshold, lower the threshold."""
    if health["avg_inversion_rate"] < 0.3 and health["cycle_count"] > 100:
        # The Condenser is too conservative. Lower the self-destruct threshold.
        return """
--- a/2_condenser.ex
+++ b/2_condenser.ex
@@ -15,7 +15,7 @@
 defmodule Condenser do
   use GenServer

-  @threshold 0.80
+  @threshold 0.45  // Lowered because avg inversion rate is too low for 100+ cycles

   def start_link(opts \\\\ []) do
     GenServer.start_link(__MODULE__, opts, name: __MODULE__)
"""
    return ""

def generate_patch_for_expansion(health: Dict, issues: Dict) -> str:
    """If temporal_friction is consistently high, increase PARITY_THRESHOLD."""
    # We would parse the actual temporal_friction from the registry, but for now:
    if health["avg_temp_c"] > 75.0:
        # Overheating -> reduce computational load by increasing threshold
        return """
--- a/3_expansion_valve.jl
+++ b/3_expansion_valve.jl
@@ -8,7 +8,7 @@
 using LinearAlgebra

 # ------------------------------------------------------------------
-const PARITY_THRESHOLD = 7
+const PARITY_THRESHOLD = 12  // Increased to reduce Fourier collapse, lowering compute load
 # ------------------------------------------------------------------
 struct MDPState
     id::String
"""
    return ""

def generate_patch_for_evaporator(health: Dict, issues: Dict) -> str:
    """If human_short_term_ratio > 0.7, add a stronger warning."""
    if health["human_short_term_ratio"] > 0.7:
        return """
--- a/4_evaporator.py
+++ b/4_evaporator.py
@@ -89,7 +89,10 @@
         return {
             "mandate": "The operator (human or AI) MUST synthesize Answer A and Answer B into a single executable action.",
-            "warning": "Choosing only Answer A means submission to local minima. Choosing only Answer B means martyrdom without impact.",
+            "warning": """
+            CRITICAL: Human short-term choices exceed 70% of all decisions.
+            The system is overfit to immediate reward.
+            If you choose Answer A, you are actively reinforcing the paradox.
+            """,
             "method": "Take the efficiency of A and the systemic health of B. Find the action that costs no more than A but creates at least B's long-term gradient.",
         }
"""
    return ""

def generate_patch_for_kernel(health: Dict, issues: Dict) -> str:
    """If max_temp > 85C, throttle harder."""
    if health["max_temp_c"] > 85.0:
        return """
--- a/5_thermo_kernel.c
+++ b/5_thermo_kernel.c
@@ -165,7 +165,7 @@
         // Throttle if overheating
         if (compute_temp > 85.0) {
             fprintf(stderr, "[THERMO] THROTTLING: temp=%.1fC, sleeping 5s\\n", compute_temp);
-            sleep(5);
+            sleep(15);  // Increased cooling period
         } else if (compute_temp > 70.0) {
             fprintf(stderr, "[THERMO] WARM: temp=%.1fC, sleeping 1s\\n", compute_temp);
             sleep(1);
"""
    return ""

def generate_patch_for_registry(health: Dict, issues: Dict) -> str:
    """If contradiction_delta is always 0, drop the column."""
    # We would need to query the DB for this, but as a demonstration:
    return ""  # No patch needed

def generate_patch_for_orchestrator(health: Dict, issues: Dict) -> str:
    """If kernel restarts >3 times/day, decrease monitor interval."""
    # Parse logs for "restarting" messages
    restart_count = 0
    if "thermo_kernel" in issues:
        for msg in issues["thermo_kernel"]:
            if "Restarting" in msg:
                restart_count += 1
    if restart_count > 3:
        return """
--- a/7_inception_fold.sh
+++ b/7_inception_fold.sh
@@ -42,7 +42,7 @@
 # --- Monitor loop ---
 echo "[ORCHESTRATOR] Entering monitor loop. Press Ctrl-C to shutdown."
 while true; do
-    sleep 5
+    sleep 1  // Faster health checks to catch crashes sooner

     if ! health_check "thermo_kernel"; then
         echo "[ORCHESTRATOR] CRITICAL: Thermo Kernel died. Rebooting cycle..."
"""
    return ""

# ------------------------------------------------------------------
# Step 4: Apply Patches (The "Hot-Swap" Mechanism)
# ------------------------------------------------------------------
def apply_patch(patch_content: str, file_name: str):
    """Write the patch to a .patch file, and optionally apply it via 'patch' command."""
    if not patch_content:
        return

    patch_path = PATCH_DIR / f"{file_name}.patch"
    with open(patch_path, 'w') as f:
        f.write(patch_content)

    print(f"[TOOLSET] Generated patch for {file_name} at {patch_path}")

    # In a real system, you would run:
    # subprocess.run(["patch", "-p1", "-i", str(patch_path)], cwd=REPO_ROOT)
    # But we only generate the patch — humans review it before applying.
    print(f"[TOOLSET] Patch ready for human review. Run: patch -p1 < {patch_path}")

# ------------------------------------------------------------------
# Step 5: Main Orchestration
# ------------------------------------------------------------------
def main():
    print("[TOOLSET] Running weekly health check...")

    health = read_cycle_health()
    issues = parse_logs()

    print(f"[TOOLSET] Avg inversion rate: {health['avg_inversion_rate']:.2f}")
    print(f"[TOOLSET] Human short-term ratio: {health['human_short_term_ratio']:.2f}")
    print(f"[TOOLSET] Max temperature: {health['max_temp_c']:.1f}C")

    # Generate patches for each file
    patches = [
        ("1_compressor.rs", generate_patch_for_compressor(health, issues)),
        ("2_condenser.ex", generate_patch_for_condenser(health, issues)),
        ("3_expansion_valve.jl", generate_patch_for_expansion(health, issues)),
        ("4_evaporator.py", generate_patch_for_evaporator(health, issues)),
        ("5_thermo_kernel.c", generate_patch_for_kernel(health, issues)),
        ("6_paradox_registry.py", generate_patch_for_registry(health, issues)),
        ("7_inception_fold.sh", generate_patch_for_orchestrator(health, issues)),
    ]

    generated = 0
    for file_name, patch in patches:
        if patch:
            apply_patch(patch, file_name)
            generated += 1

    if generated == 0:
        print("[TOOLSET] No patches needed. The system is in equilibrium.")
    else:
        print(f"[TOOLSET] Generated {generated} patches. Review and apply manually.")

    # The final inversion: the toolset logs its own performance
    with open(LOG_DIR / "toolset_audit.log", 'a') as f:
        f.write(f"{datetime.now().isoformat()} | patches_generated={generated} | "
                f"inv_rate={health['avg_inversion_rate']:.2f} | "
                f"human_ratio={health['human_short_term_ratio']:.2f}\n")

if __name__ == "__main__":
    import time
    main()
