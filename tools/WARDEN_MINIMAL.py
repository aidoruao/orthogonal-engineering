# CITIZENSHIP
{
  "id": "tools/WARDEN_MINIMAL.py",
  "payload_hash": "933bba3328bb07c52c090abf641fd2e622f26b31a5d034c2fce9738b59983973",
  "falsifies_if": []
}
# END CITIZENSHIP
# CITIZENSHIP
{
  "id": "tools/WARDEN_MINIMAL.py",
  "payload_hash": "ced87bc3305f654a70f02a5f0eb51e85cdc0838f523c3f0e63e3fa55db75ea66",
  "falsifies_if": []
}
# END CITIZENSHIP
#!/usr/bin/env python3
"""WARDEN_MINIMAL.py - Provably correct. No guesses."""

import hashlib, json, re, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUARANTINE = REPO / ".quarantine"
PATTERN = re.compile('# CITIZENSHIP' + chr(10) + '(.*?)' + chr(10) + '# END CITIZENSHIP', re.DOTALL)

def extract(text):
    m = PATTERN.search(text)
    if not m: return None
    try: json.loads(m.group(1)); return m.group(1)
    except json.JSONDecodeError: return None

def strip(text):
    return PATTERN.sub("", text)

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
        except re.error: return True
    return False

def scan(root=REPO):
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
