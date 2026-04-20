#!/usr/bin/env python3
"""tools/generate_hashed_taxonomy.py — hashed investigative taxonomy + gap analysis.

Walks the repository and emits a deterministic JSONL audit of occurrences mapped
to six namespaces (``aerospace``, ``floor``, ``yeshua``, ``math_popperian``,
``secular``, ``projection``), plus issue markers (``TODO``, ``FIXME``, ``HACK``,
``pass`` stubs, ``NotImplementedError`` stubs, ``float(`` usages, missing
``falsifies_if``/``Falsifies if:`` docstring pair on ``check_*`` functions,
missing ``Tuple[bool, ProofObject]`` annotations on ``check_*`` functions).

Each JSONL entry carries a SHA-256 commitment over the canonical JSON of that
entry, and the final summary JSON carries ``audit_sha256`` over the full
canonicalised document.

Authority: Yeshua Standard / .cursorrules / CLAUDE.md / SOP-AI-HANDSHAKE-1.0
Falsifies if: two runs over the same working tree produce different
``audit_sha256`` commitments.
falsifies_if: two runs over the same working tree produce different
audit_sha256 commitments.

Usage::

    python tools/generate_hashed_taxonomy.py \\
        --out audits/hashed_taxonomy_YYYYMMDD.jsonl \\
        --summary audits/gap_analysis_YYYYMMDD.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Namespace classification
# ---------------------------------------------------------------------------

NAMESPACE_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    # Aerospace: DO-178C / MIL-STD / NASA NPR
    "aerospace": (
        "aerospace",
        "do-178",
        "do178",
        "mil-std",
        "milstd",
        "nasa",
        "npr 7150",
        "nasa_npr",
        "sil-4",
        "iec 61508",
        "iec61508",
    ),
    # Universal Aerospace Floor: new ordering introduced in PR 139
    "floor": (
        "aerospace_floor",
        "aerospace-floor",
        "d_aerospace_floor",
        "universal_aerospace_floor",
        "af_floor",
        "floor_invariant",
    ),
    # Yeshua standard: 8 axioms, ProofObject, YeshuaClaim, falsifies_if
    "yeshua": (
        "yeshua",
        "proofobject",
        "yeshuaclaim",
        "proof_object",
        "yeshua_standard",
        "falsifies_if",
        "falsifies if:",
    ),
    # Mathematical / Popperian: Popper falsification, category theory, topos,
    # Peano, Fraction, surreal, transfinite, reverse math.
    "math_popperian": (
        "popperian",
        "popper",
        "falsifiability",
        "peano",
        "category_theory",
        "topos",
        "homotopy",
        "reverse_math",
        "surreal",
        "transfinite",
        "fraction(",
    ),
    # Secular projection: projections into non-theological namespaces
    "secular": (
        "secular",
        "secular_projection",
        "secular_namespace",
        "non_theological",
        "projection_secular",
    ),
    # Projected namespace (generic): projected views of domains, mirrors
    "projection": (
        "projected_namespace",
        "projected_view",
        "derivative_witness",
        "mirror",
        "projection",
    ),
}


# File types we read as text for evidence extraction.
TEXT_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".jsonl", ".toml", ".ini", ".txt", ".rst"}

# Directories always excluded from the walk (noise / third-party).
EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "venv",
    ".venv",
    "env",
    ".tox",
    "dist",
    "build",
    "orthogonal-engineering-ref",  # submodule
    "arxiv_vendor",
    "out",
    "audits",  # generated audit artifacts — do not re-scan our own output
}

# Path patterns excluded from the walk (giant session transcripts).
EXCLUDED_PATH_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"kimi[ _-]code", re.IGNORECASE),
    re.compile(r"^devin[ ]ai[ ]", re.IGNORECASE),
    re.compile(r"devin\s*ai\s*\d+\s*,?\s*architectural", re.IGNORECASE),
    re.compile(r"deepseek\s*ai\s*", re.IGNORECASE),
    re.compile(r"gpt\s*5\s*mini", re.IGNORECASE),
    re.compile(r"copilot\s*pr\s*\d+\s*checkpoint", re.IGNORECASE),
    re.compile(r"agent\s*github\s*copilot", re.IGNORECASE),
    re.compile(r"^CFNetworkDownload_", re.IGNORECASE),
)


# ---------------------------------------------------------------------------
# Issue detection patterns
# ---------------------------------------------------------------------------

# Critical: unconditional stubs and float() usage.
_RE_TODO = re.compile(r"\b(TODO|FIXME|HACK)\b")
_RE_STUB_PASS = re.compile(r"^\s*pass\s*(#.*)?$")
_RE_STUB_NOTIMPL = re.compile(r"\bNotImplementedError\b")
_RE_FLOAT_CALL = re.compile(r"\bfloat\(")
_RE_FLOAT_ANNOT = re.compile(r":\s*float\b")
_RE_CHECK_DEF = re.compile(r"^\s*def\s+(check_\w+)\s*\(", re.MULTILINE)
_RE_CHECK_RETURN = re.compile(r"Tuple\[\s*bool\s*,\s*ProofObject\s*\]")
_RE_FALS_TITLE = re.compile(r"Falsifies if:", re.IGNORECASE)
_RE_FALS_LOWER = re.compile(r"falsifies_if:")
_RE_ASSERT = re.compile(r"^\s*assert\b")


ISSUE_SEVERITY: Dict[str, str] = {
    "TODO": "low",
    "FIXME": "medium",
    "HACK": "medium",
    "STUB_PASS": "high",
    "STUB_NOTIMPL": "critical",
    "FLOAT_CALL": "high",
    "FLOAT_ANNOT": "medium",
    "CHECK_MISSING_PROOFOBJECT": "high",
    "CHECK_MISSING_FALSIFIES_IF_PAIR": "medium",
    "ASSERT_USE": "high",
}


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _sha256_text(text: str) -> str:
    """Return the hex SHA-256 of ``text`` encoded as UTF-8.

    Falsifies if: the digest is not 64 lowercase hex characters.
    falsifies_if: the digest is not 64 lowercase hex characters.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 of ``data``.

    Falsifies if: the digest is not 64 lowercase hex characters.
    falsifies_if: the digest is not 64 lowercase hex characters.
    """
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Return a deterministic canonical JSON serialisation (sorted keys, no BOM)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Walk + classify
# ---------------------------------------------------------------------------


def _is_excluded(rel_path: Path) -> bool:
    """Return True if this relative path is excluded from audit."""
    parts = rel_path.parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
    name = rel_path.name
    for pattern in EXCLUDED_PATH_PATTERNS:
        if pattern.search(name):
            return True
    return False


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    """Yield files under ``root`` eligible for text scanning, deterministically ordered."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        rel = path.relative_to(root)
        if _is_excluded(rel):
            continue
        try:
            if path.stat().st_size > 2 * 1024 * 1024:
                # skip files > 2 MiB (large session logs etc.)
                continue
        except OSError:
            continue
        yield path


def _namespaces_for_text(text_lower: str, path_lower: str) -> Tuple[str, ...]:
    """Return the sorted tuple of namespace labels matching ``text_lower``/``path_lower``."""
    matched: List[str] = []
    for label, keywords in NAMESPACE_KEYWORDS.items():
        for kw in keywords:
            if kw in path_lower or kw in text_lower:
                matched.append(label)
                break
    return tuple(sorted(set(matched)))


# ---------------------------------------------------------------------------
# Issue scanners
# ---------------------------------------------------------------------------


def _scan_line_level(text: str, is_python: bool) -> List[Tuple[int, str, str]]:
    """Yield ``(line_no, issue_type, snippet)`` for line-local patterns.

    The ``is_python`` flag gates detectors that only apply to Python sources
    (``STUB_PASS``, ``STUB_NOTIMPL``, ``FLOAT_CALL``, ``FLOAT_ANNOT``,
    ``ASSERT_USE``) so we do not emit false positives against e.g. Markdown
    prose or JSON that mentions the words.
    """
    out: List[Tuple[int, str, str]] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\r")
        snippet = line.strip()[:240]
        todo_match = _RE_TODO.search(line)
        if todo_match is not None:
            out.append((idx, todo_match.group(1).upper(), snippet))
        if is_python:
            if _RE_STUB_PASS.match(line):
                out.append((idx, "STUB_PASS", snippet))
            if _RE_STUB_NOTIMPL.search(line):
                out.append((idx, "STUB_NOTIMPL", snippet))
            if _RE_FLOAT_CALL.search(line):
                out.append((idx, "FLOAT_CALL", snippet))
            if _RE_FLOAT_ANNOT.search(line):
                out.append((idx, "FLOAT_ANNOT", snippet))
            if _RE_ASSERT.match(line):
                out.append((idx, "ASSERT_USE", snippet))
    return out


def _scan_check_function(path: Path, text: str) -> List[Tuple[int, str, str]]:
    """Yield issues for ``check_*`` functions missing the required contract.

    Heuristic: find ``def check_*(``; scan the next 40 lines for
    a ``Tuple[bool, ProofObject]`` return annotation or for a docstring
    containing both ``Falsifies if:`` and ``falsifies_if:``.
    """
    out: List[Tuple[int, str, str]] = []
    lines = text.splitlines()
    for m in _RE_CHECK_DEF.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        # Look at the def line and up to the next 40 lines for the annotations.
        window = "\n".join(lines[line_no - 1 : min(len(lines), line_no + 40)])
        has_return = bool(_RE_CHECK_RETURN.search(window))
        has_title = bool(_RE_FALS_TITLE.search(window))
        has_lower = bool(_RE_FALS_LOWER.search(window))
        if not has_return:
            out.append(
                (
                    line_no,
                    "CHECK_MISSING_PROOFOBJECT",
                    f"{m.group(0).strip()}  # no Tuple[bool, ProofObject] within 40 lines",
                )
            )
        if not (has_title and has_lower):
            out.append(
                (
                    line_no,
                    "CHECK_MISSING_FALSIFIES_IF_PAIR",
                    f"{m.group(0).strip()}  # missing both 'Falsifies if:' and 'falsifies_if:' in docstring",
                )
            )
    return out


# ---------------------------------------------------------------------------
# Entry construction
# ---------------------------------------------------------------------------


def build_entries(root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Walk ``root`` and build (entries, summary)."""
    entries: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {k: 0 for k in ISSUE_SEVERITY}
    counts_by_namespace: Dict[str, int] = {k: 0 for k in NAMESPACE_KEYWORDS}
    counts_by_namespace["unclassified"] = 0
    files_scanned = 0

    for path in _iter_candidate_files(root):
        rel = path.relative_to(root).as_posix()
        path_lower = rel.lower()
        try:
            data = path.read_bytes()
            text = data.decode("utf-8", errors="replace")
        except OSError:
            continue

        files_scanned += 1
        text_lower = text.lower()
        namespaces = _namespaces_for_text(text_lower, path_lower)
        if not namespaces:
            # No namespace hit: we still scan for issues but mark namespace=unclassified.
            ns_record: Tuple[str, ...] = ("unclassified",)
        else:
            ns_record = namespaces

        file_sha = _sha256_bytes(data)
        is_python = path.suffix == ".py"

        hits: List[Tuple[int, str, str]] = []
        hits.extend(_scan_line_level(text, is_python=is_python))
        if is_python:
            hits.extend(_scan_check_function(path, text))

        for line_no, issue_type, snippet in hits:
            counts[issue_type] = counts.get(issue_type, 0) + 1
            for ns in ns_record:
                counts_by_namespace[ns] = counts_by_namespace.get(ns, 0) + 1
            ev_sha = _sha256_text(f"{rel}:{line_no}:{snippet}")
            entry: Dict[str, Any] = {
                "id": f"OE-TAX-{ev_sha[:12]}",
                "path": rel,
                "line": line_no,
                "issue_type": issue_type,
                "severity": ISSUE_SEVERITY.get(issue_type, "low"),
                "namespaces": list(ns_record),
                "evidence": {"snippet": snippet},
                "sha256_evidence": ev_sha,
                "file_sha256": file_sha,
            }
            entry["entry_sha256"] = _sha256_text(_canonical_json(entry))
            entries.append(entry)

    summary: Dict[str, Any] = {
        "schema": "OE-HASHED-TAXONOMY-1.0",
        "files_scanned": files_scanned,
        "issue_count_total": len(entries),
        "issue_count_by_type": dict(sorted(counts.items())),
        "issue_count_by_namespace": dict(sorted(counts_by_namespace.items())),
    }
    return entries, summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _write_jsonl(entries: List[Dict[str, Any]], out_path: Path) -> None:
    """Write entries as JSONL, deterministically ordered by ``entry_sha256``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(entries, key=lambda e: (e["path"], e["line"], e["issue_type"], e["entry_sha256"]))
    with out_path.open("w", encoding="utf-8") as fh:
        for e in ordered:
            fh.write(_canonical_json(e) + "\n")


def _write_summary(
    summary: Dict[str, Any], entries: List[Dict[str, Any]], out_path: Path, jsonl_path: Path
) -> str:
    """Write the summary JSON with ``audit_sha256`` commitment. Returns the sha.

    The ``audit_sha256`` commits over content only (summary + ordered entry
    hashes); output paths are metadata, not covered by the commitment, so two
    runs against the same working tree produce the same ``audit_sha256``
    regardless of where the artifacts are written.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered_hashes = sorted(e["entry_sha256"] for e in entries)
    commit_payload = {
        "summary": summary,
        "ordered_entry_hashes": ordered_hashes,
    }
    audit_sha256 = _sha256_text(_canonical_json(commit_payload))
    try:
        jsonl_label = jsonl_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        jsonl_label = jsonl_path.name

    # Percent of entries classified — as Fraction, rendered as "num/den".
    total = max(len(entries), 1)
    classified = sum(1 for e in entries if e["namespaces"] != ["unclassified"])
    frac_classified = Fraction(classified, total)
    # ``metadata`` collects fields that are *intentionally* not covered by
    # ``audit_sha256`` (timestamps, output paths). Separating them makes the
    # commitment boundary visible to reviewers: only ``summary`` +
    # ``ordered_entry_hashes`` participate in the commit payload.
    doc = {
        "schema": "OE-GAP-ANALYSIS-1.0",
        "summary": summary,
        "classified_fraction": f"{frac_classified.numerator}/{frac_classified.denominator}",
        "audit_sha256": audit_sha256,
        "entry_count": len(entries),
        "metadata": {
            "generated_at_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "jsonl_path": jsonl_label,
            "not_covered_by_audit_sha256": ["generated_at_utc", "jsonl_path"],
        },
    }
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=True) + "\n")
    return audit_sha256


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate hashed investigative taxonomy.")
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSONL path (default: audits/hashed_taxonomy_<UTC>.jsonl).",
    )
    parser.add_argument(
        "--summary",
        default=None,
        help="Output summary JSON path (default: audits/gap_analysis_<UTC>.json).",
    )
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out) if args.out else root / "audits" / f"hashed_taxonomy_{stamp}.jsonl"
    summary_path = (
        Path(args.summary) if args.summary else root / "audits" / f"gap_analysis_{stamp}.json"
    )

    entries, summary = build_entries(root)
    _write_jsonl(entries, out)
    audit_sha = _write_summary(summary, entries, summary_path, out)

    print(
        _canonical_json(
            {
                "files_scanned": summary["files_scanned"],
                "issue_count_total": summary["issue_count_total"],
                "audit_sha256": audit_sha,
                "jsonl_path": str(out),
                "summary_path": str(summary_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
