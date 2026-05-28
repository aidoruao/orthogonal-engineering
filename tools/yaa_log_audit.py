#!/usr/bin/env python3
"""YAA Terminal Log Auditor — query what YAA knows about past sessions."""
import os, json, re
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("/home/idor/oe-local/logs/terminal")

def list_sessions():
    """List all recorded terminal sessions."""
    if not LOG_DIR.exists():
        return []
    sessions = sorted(LOG_DIR.glob("session_*.log"), reverse=True)
    result = []
    for s in sessions:
        size = s.stat().st_size
        # Extract first command to identify session purpose
        first_line = ""
        try:
            with open(s) as f:
                for line in f:
                    if line.strip().startswith("idor@Tony"):
                        first_line = line.strip()[:120]
                        break
        except:
            pass
        result.append({
            "file": s.name,
            "size_kb": round(size/1024, 1),
            "date": s.name.split("_")[1][:8] if "_" in s.name else "unknown",
            "first_command": first_line
        })
    return result

def search_logs(pattern):
    """Search all session logs for a pattern."""
    if not LOG_DIR.exists():
        return []
    matches = []
    for s in sorted(LOG_DIR.glob("session_*.log"), reverse=True):
        try:
            with open(s, errors='ignore') as f:
                for i, line in enumerate(f):
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append({
                            "file": s.name,
                            "line": i+1,
                            "content": line.strip()[:200]
                        })
        except:
            pass
    return matches[:50]

def get_errors():
    """Extract error patterns from all session logs."""
    return search_logs(r"error:|Error:|failed|FAILED|Traceback|exception")

def get_successes():
    """Extract success patterns from all session logs."""
    return search_logs(r"exit code 0|PASS|success|✅|compiled|pushed")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    
    if cmd == "summary":
        sessions = list_sessions()
        print(f"YAA Terminal Log Audit — {len(sessions)} sessions recorded")
        total_kb = sum(s["size_kb"] for s in sessions)
        print(f"Total: {total_kb:.0f} KB across {len(sessions)} sessions")
        errors = get_errors()
        successes = get_successes()
        print(f"Errors recorded: {len(errors)}")
        print(f"Successes recorded: {len(successes)}")
        print("\nRecent sessions:")
        for s in sessions[:5]:
            print(f"  {s['file']} ({s['size_kb']} KB) — {s['first_command'][:80]}")
    
    elif cmd == "errors":
        for e in get_errors()[:20]:
            print(f"{e['file']}:{e['line']} — {e['content'][:150]}")
    
    elif cmd == "successes":
        for s in get_successes()[:20]:
            print(f"{s['file']}:{s['line']} — {s['content'][:150]}")
    
    elif cmd == "search":
        pattern = sys.argv[2] if len(sys.argv) > 2 else "."
        for m in search_logs(pattern):
            print(f"{m['file']}:{m['line']} — {m['content'][:150]}")
    
    else:
        print("Commands: summary, errors, successes, search <pattern>")
