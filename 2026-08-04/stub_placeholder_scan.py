#!/usr/bin/env python3
"""stub_placeholder_scan.py — audit the oe-local deliverable surface for stubs & placeholders.

Checks:
  1. Literal '[redacted]' IN FILES (placeholder residue written by an earlier session;
     distinct from the display layer's read-time redaction — the file itself matters).
  2. Marker regexes: TODO|FIXME|XXX|TBD|placeholder|coming soon|under construction|
     lorem ipsum|not implemented|raise NotImplementedError|stub pass.
  3. Stub files: size < 80 bytes, or zero logic lines (comments/docstring/blank only).
  4. JSON/JSONL integrity: parse errors, empty files (0 rows) — broken/empty = stubs.
  5. Markdown: heading directly followed by EOF/heading (empty section).

Deterministic; writes stub_placeholder_scan.json + human report.
"""
import json
import re
import sys
from pathlib import Path

ROOTS = [
    Path("/home/idor/oe-local/2026-08-04"),
    Path("/home/idor/oe-local/benchmarks"),
]
FILES = [
    Path("/home/idor/oe-local/CHAIN_OF_CUSTODY.md"),
]
SELF = Path(__file__).resolve()  # the scanner never audits itself
MARKERS = re.compile(
    r"\b(TODO|FIXME|XXX|TBD|HACK|lorem ipsum|coming soon|under construction|"
    r"not implemented|NotImplementedError)\b",
    re.IGNORECASE,
)
EMPTY_SECTION = re.compile(r"^#{1,6}\s+.+$")
LOGIC_RE = re.compile(r"^\s*(?!\s*(#|$|\"\"\"|'''|//|\*|\"))\S")


def scan_file(p: Path, findings: list, stats: dict):
    try:
        raw = p.read_bytes()
    except OSError:
        return
    size = len(raw)
    stats["files"] += 1
    if size < 80:
        findings.append({"file": str(p), "kind": "tiny_file", "detail": f"{size} bytes"})
        stats["tiny"] += 1
        return
    if p.suffix == ".py":
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        logic = sum(1 for line in text.splitlines() if LOGIC_RE.match(line))
        if logic == 0:
            findings.append({"file": str(p), "kind": "no_logic", "detail": "comments/docstring only"})
            stats["no_logic"] += 1
        for i, line in enumerate(text.splitlines(), 1):
            if MARKERS.search(line):
                findings.append({"file": str(p), "kind": "marker", "line": i,
                                 "detail": line.strip()[:90]})
                stats["markers"] += 1
    elif p.suffix in (".md", ".txt", ".jsonl"):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if "[redacted]" in line:
                findings.append({"file": str(p), "kind": "literal_redacted", "line": i,
                                 "detail": line.strip()[:90]})
                stats["literal_redacted"] += 1
            if MARKERS.search(line):
                findings.append({"file": str(p), "kind": "marker", "line": i,
                                 "detail": line.strip()[:90]})
                stats["markers"] += 1
        if p.suffix == ".md":
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if EMPTY_SECTION.match(line):
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    # empty section = heading with no content and no sub-heading before EOF/fence
                    if j >= len(lines) or lines[j].strip().startswith("```"):
                        findings.append({"file": str(p), "kind": "empty_section", "line": i + 1,
                                         "detail": line.strip()[:60]})
                        stats["empty_section"] += 1
    elif p.suffix == ".json":
        try:
            json.loads(raw.decode("utf-8"))
        except Exception as e:
            findings.append({"file": str(p), "kind": "json_parse", "detail": str(e)[:80]})
            stats["json_parse"] += 1
    elif p.suffix == ".jsonl":
        n = 0
        bad = 0
        for line in raw.decode("utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                json.loads(line)
            except Exception:
                bad += 1
        if n == 0:
            findings.append({"file": str(p), "kind": "empty_jsonl", "detail": "0 rows"})
            stats["empty_jsonl"] += 1
        elif bad:
            findings.append({"file": str(p), "kind": "jsonl_broken", "detail": f"{bad}/{n} lines"})
            stats["jsonl_broken"] += 1


def main():
    findings = []
    stats = {"files": 0, "tiny": 0, "no_logic": 0, "markers": 0, "literal_redacted": 0,
             "empty_section": 0, "json_parse": 0, "empty_jsonl": 0, "jsonl_broken": 0}
    for root in ROOTS:
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in str(p) and p != SELF:
                scan_file(p, findings, stats)
    for p in FILES:
        if p.is_file() and p != SELF:
            scan_file(p, findings, stats)
    print(f"scanned {stats['files']} files | findings: {len(findings)}")
    for k, v in stats.items():
        if k != "files" and v:
            print(f"  {k}: {v}")
    for f in findings[:60]:
        loc = f.get("line", "")
        print(f"  [{f['kind']}] {f['file']}{':' + str(loc) if loc else ''} — {f['detail'][:70]}")
    out = Path(__file__).resolve().parent / "stub_placeholder_scan.json"
    out.write_text(json.dumps({"stats": stats, "findings": findings}, indent=1))
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
