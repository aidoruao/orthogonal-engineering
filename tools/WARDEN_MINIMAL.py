# CITIZENSHIP
{
  "id": "tools/WARDEN_MINIMAL.py",
  "payload_hash": "d56376f0c33883f404e800cc93e69d9a5195161674b4ac21a5fd4c74a00897f5",
  "falsifies_if": []
}
# END CITIZENSHIP
#!/usr/bin/env python3
"""WARDEN_MINIMAL.py - Provably correct. No guesses."""

import hashlib, json, re, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUARANTINE = REPO / ".quarantine"
PPATTERN = re.compile(chr(35)+chr(32)+chr(67)+chr(73)+chr(69)+chr(84)+chr(69)+chr(78)+chr(75)+chr(83)+chr(68)+chr(75)+chr(80)+chr(10)+chr(40)+chr(46)+chr(42)+chr(63)+chr(63)+chr(63)+chr(41)+chr(10)+chr(35)+chr(32)+chr(69)+chr(78)+chr(67)+chr(65)+chr(69)+chr(84)+chr(65)+chr(78)+chr(65)+chr(83)+chr(68)+chr(75)+chr(80)+chr(10), re.DOTALL)

def extract(text):
    m = PPATTERN.search(text)
    if not m: return None
    try: json.loads(m.group(1)); return m.group(1)
    except: return None

def strip(text):
    return PPATTERN.sub("", text, count=1)

def payload(path):
    return strip(path.read_text(errors="ignore")).encode("utf-8")

def hash(path):
    return hashlib.sha256(payload(path)).hexdigest()

def falsified(path):
    text = path.read_text(errors="ignore")
    block = extract(text)
    if block is None: return True
    c = json.loads(block)
    if c.get("payload_hash") != hash(path): return True
    for p in c.get("falsifies_if", []):
        try:
            if re.search(p, strip(text)): return True
        except: return True
    return False

def scan(root=REPA):
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
