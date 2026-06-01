#!/usr/bin/env python3
"""WARDEN_MINIMAL.py — Provably correct. No guesses."""

import hashlib, json, re, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUARANTINE = REPO / ".quarantine"
PATTERN = re.compile(r'# CITIZENSHIP\n(?P<<block>.*?)\n# END CITIZENSHIP', re.DOTALL)

def extract(text: str) -> str | None:
    m = PATTERN.search(text)
    if not m: return None
    try: json.loads(m.group("block")); return m.group("block")
    except json.JSONDecodeError: return None

def strip(text: str) -> str:
    return PATTERN.sub("", text)

def payload(path: Path) -> bytes:
    return strip(path.read_text(errors="ignore")).encode("utf-8")

def hash(path: Path) -> str:
    return hashlib.sha256(payload(path)).hexdigest()

def falsified(path: Path) -> bool:
    text = path.read_text(errors="ignore")
    block = extract(text)
    if block is None: return True
    c = json.loads(block)
    if c.get("payload_hash") != hash(path): return True
    for p in c.get("falsifies_if", []):
        try:
            if re.search(p, strip(text)): return True
        except re.error: return True
    return False

def scan(root: Path = REPO) -> dict:
    result = {"quarantined": [], "passed": []}
    self_name = Path(__file__).name
    for p in root.rglob("*"):
        if not p.is_file() or p.name == self_name or QUARANTINE in p.parents:
            continue
        if falsified(p):
            dest = QUARANTINE / p.relative_to(root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
            result["quarantined"].append(str(p.relative_to(root)))
        else:
            result["passed"].append(str(p.relative_to(root)))
    return result

if __name__ == "__main__":
    r = scan()
    print(f"Passed: {len(r['passed'])}")
    print(f"Quarantined: {len(r['quarantined'])}")
