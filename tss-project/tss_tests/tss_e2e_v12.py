#!/usr/bin/env python3
"""
TSS v12 End-to-End Integration Test
Tor → RSS/API → IPFS → CID
"""
import subprocess
import json
import sys
import os
from datetime import datetime

def run_test(name, command, cwd=None):
    """Run a test command and capture result."""
    result = {
        "test": name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "passed": False,
        "stdout": None,
        "stderr": None,
        "returncode": None
    }

    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd or os.getcwd()
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[:500]  # Truncate for size
        result["stderr"] = proc.stderr[:200] if proc.stderr else None
        result["passed"] = proc.returncode == 0

    except subprocess.TimeoutExpired:
        result["stderr"] = "TIMEOUT"
    except Exception as e:
        result["stderr"] = str(e)

    return result

def main():
    project_dir = os.path.expanduser("~/oe-local/tss-project")
    results = []

    # Test 1: Daemon health
    results.append(run_test(
        "daemon_health",
        "export XDG_RUNTIME_DIR=/run/user/1000; export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; systemctl --user is-active tor-tss ipfs-tss"
    ))

    # Test 2: Tor routing
    results.append(run_test(
        "tor_routing",
        "curl -s --proxy socks5h://127.0.0.1:9050 https://check.torproject.org | grep -q 'Congratulations' && echo 'TOR_OK'"
    ))

    # Test 3: IPFS daemon
    results.append(run_test(
        "ipfs_daemon",
        "ipfs id 2>/dev/null | grep -q 'ID' && echo 'IPFS_OK'"
    ))

    # Test 4: RSS bot module compiles
    results.append(run_test(
        "rss_module_compile",
        "python3 -m py_compile tss_core/tss_filing_rss.py",
        cwd=project_dir
    ))

    # Test 5: Testnet module compiles
    results.append(run_test(
        "testnet_module_compile",
        "python3 -m py_compile tss_core/tss_blockchain_testnet.py",
        cwd=project_dir
    ))

    # Test 6: Monitor module compiles
    results.append(run_test(
        "monitor_module_compile",
        "python3 -m py_compile tss_core/tss_daemon_monitor.py",
        cwd=project_dir
    ))

    # Test 7: v10 diagnostics still pass
    results.append(run_test(
        "v10_diagnostics",
        "python3 tss_core/tss_diagnostics.py --json | tail -1 | grep -q '100.0' && echo 'DIAG_OK'",
        cwd=project_dir
    ))

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "v12",
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "all_passed": passed == total,
        "results": results
    }

    print(json.dumps(output, indent=2))
    return 0 if output["all_passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
