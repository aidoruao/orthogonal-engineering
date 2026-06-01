#!/usr/bin/env python3
"""WARDEN.py — Directory block captain. Adopts non-citizens. Heals broken ones."""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any

def encode_fraction_name(name: str) -> str:
    """A=1/2, B=2/3, ... Z=26/27. Joined with ·"""
    out = []
    for ch in name.upper():
        if 'A' <= ch <= 'Z':
            n = ord(ch) - ord('A') + 1
            out.append(f"{n}/{n+1}")
    return "·".join(out)

class Citizen:
    def __init__(self, path: Path, frontmatter: dict):
        self.path = path
        self.fm = frontmatter

    def is_valid(self) -> bool:
        required = ["id", "sha256", "domain", "proof"]
        return all(k in self.fm for k in required)

    def needs(self) -> List[str]:
        out = []
        if not self.is_valid():
            out.append("citizenship_incomplete")
        if self.fm.get("status") == "broken":
            out.append("status_broken")
        if not self.fm.get("proof", [False])[0]:
            out.append("proof_failed")
        if self.fm.get("sha256") != self.compute_sha256():
            out.append("hash_mismatch")
        return out

    def compute_sha256(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def speak(self) -> dict:
        return {
            "path": str(self.path),
            "id": self.fm.get("id"),
            "status": self.fm.get("status", "unknown"),
            "needs": self.needs(),
            "domain": self.fm.get("domain"),
        }

    def to_frontmatter(self) -> str:
        return f"# CITIZENSHIP\n{json.dumps(self.fm, indent=2)}\n# END CITIZENSHIP\n"

class Warden:
    def __init__(self, directory: Path):
        self.directory = directory
        self.citizens: List[Citizen] = []
        self.non_citizens: List[Path] = []
        self.scan()

    def scan(self):
        for item in self.directory.iterdir():
            if item.name == "WARDEN.py" or item.is_dir():
                continue
            fm = self.parse_frontmatter(item)
            if fm:
                self.citizens.append(Citizen(item, fm))
            else:
                self.non_citizens.append(item)

    def parse_frontmatter(self, path: Path) -> Optional[dict]:
        try:
            text = path.read_text()
            m = re.search(r'# CITIZENSHIP\n(.*?)\n# END CITIZENSHIP', text, re.DOTALL)
            if m:
                return json.loads(m.group(1))
        except Exception:
            pass
        return None

    def invite(self):
        """Non-citizens, speak up. We will take care of you."""
        for nc in self.non_citizens:
            self.adopt(nc)
        self.non_citizens = []

    def adopt(self, path: Path):
        fm = {
            "id": encode_fraction_name(path.stem),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "domain": encode_fraction_name(str(self.directory.relative_to(Path.cwd()))),
            "sovereign_layer": "¹⁄₂",
            "invariants": [],
            "falsifies_if": [],
            "dependencies": [],
            "dependents": [],
            "proof": [True, "¹⁄₂"],
            "status": "adopted"
        }
        old = path.read_text()
        path.write_text(Citizen(path, fm).to_frontmatter() + old)
        self.citizens.append(Citizen(path, fm))

    def heal(self):
        for c in self.citizens:
            needs = c.needs()
            if "hash_mismatch" in needs:
                c.fm["sha256"] = c.compute_sha256()
                c.fm["status"] = "healed"
                body = re.sub(r'# CITIZENSHIP.*?# END CITIZENSHIP\n', '', c.path.read_text(), flags=re.DOTALL)
                c.path.write_text(c.to_frontmatter() + body)

    def query(self, q: str) -> Any:
        if q == "who_needs_help":
            return [c.speak() for c in self.citizens if c.needs()]
        if q == "all_citizens":
            return [c.speak() for c in self.citizens]
        if q == "non_citizens":
            return [{"path": str(p), "status": "stateless"} for p in self.non_citizens]
        if q == "local_state":
            return {
                "dir": str(self.directory),
                "citizens": len(self.citizens),
                "non_citizens": len(self.non_citizens),
                "needs": [c.speak() for c in self.citizens if c.needs()]
            }
        return {"error": "unknown_query"}

if __name__ == "__main__":
    w = Warden(Path(__file__).parent)
    w.invite()
    w.heal()
    print(json.dumps(w.query("who_needs_help"), indent=2))
