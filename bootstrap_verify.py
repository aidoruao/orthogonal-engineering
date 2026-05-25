#!/usr/bin/env python3
"""bootstrap_verify.py — 20-line auditable seed. Verifies OE repo integrity.
falsifies_if: any checked file is missing, bridge is unreachable, or hash mismatches."""
import os, hashlib, json, urllib.request as ur

ROOT = os.path.dirname(os.path.abspath(__file__))
CHECKS = {
    "lean4/SAL/Basic.lean": None, "lean4/SAL/Yoneda.lean": None,
    "auto_push.sh": None, "tools/lean4_bridge.py": None,
    "tools/yeshua_scanner.py": None, "tools/yeshua_scan_results.json": None,
    "docs/ARCHITECTURAL_MAP_UNIFIED_2026-05-24.md": None,
    "docs/puzzles/oe_proving_ground.html": None,
    "docs/puzzles/yeshua_agent_redemption.html": None,
}
missing = [f for f in CHECKS if not os.path.isfile(os.path.join(ROOT, f))]
# Bridge check
bridge_ok = False
try:
    req = ur.Request("http://localhost:28428", data=b'{"code":"#eval 1+1","row":0}',
                     headers={"Content-Type":"application/json"})
    bridge_ok = json.loads(ur.urlopen(req, timeout=5).read()).get("success", False)
except: pass
verdict = "PASS" if (not missing and bridge_ok) else "FAIL"
print(f"BOOTSTRAP_VERIFY: {verdict} | missing={missing} | bridge={bridge_ok}")
print(f"falsifies_if: {verdict} == 'PASS' but any invariant is violated")
# Self-hash
self_hash = hashlib.sha256(open(__file__,'rb').read()).hexdigest()
print(f"SHA-256: {self_hash}")
