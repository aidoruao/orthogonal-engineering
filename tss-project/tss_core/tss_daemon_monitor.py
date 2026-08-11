#!/usr/bin/env python3
"""
TSS Daemon Monitor — systemd health check with auto-restart trigger
"""
import subprocess
import json
import sys
from datetime import datetime

def check_daemon(name):
    """Check if a systemd user service is active."""
    result = {
        "daemon": name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "active": False,
        "enabled": False,
        "pid": None,
        "uptime": None,
        "restarts": 0
    }

    try:
        # Check active status
        active = subprocess.run(
            ["systemctl", "--user", "is-active", name],
            capture_output=True, text=True, timeout=5
        )
        result["active"] = active.returncode == 0

        # Check enabled status
        enabled = subprocess.run(
            ["systemctl", "--user", "is-enabled", name],
            capture_output=True, text=True, timeout=5
        )
        result["enabled"] = enabled.returncode == 0

        # Get detailed status
        status = subprocess.run(
            ["systemctl", "--user", "status", name, "--no-pager"],
            capture_output=True, text=True, timeout=5
        )

        # Extract PID from status output
        for line in status.stdout.split("\n"):
            if "Main PID:" in line:
                pid_part = line.split("Main PID:")[1].strip()
                result["pid"] = pid_part.split()[0] if pid_part.split() else None
            if "ago" in line and "min" in line:
                result["uptime"] = line.strip()

        return result

    except Exception as e:
        result["error"] = str(e)
        return result

def restart_daemon(name):
    """Restart a daemon if it's not active."""
    try:
        subprocess.run(
            ["systemctl", "--user", "restart", name],
            capture_output=True, timeout=10
        )
        return True
    except Exception:
        return False

if __name__ == "__main__":
    daemons = ["tor-tss", "ipfs-tss"]
    results = []
    all_ok = True

    for daemon in daemons:
        status = check_daemon(daemon)
        if not status["active"]:
            all_ok = False
            status["restart_attempted"] = restart_daemon(daemon)
            # Re-check after restart
            status["active_after_restart"] = check_daemon(daemon)["active"]
        results.append(status)

    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "all_daemons_ok": all_ok,
        "daemons": results
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if all_ok else 1)
