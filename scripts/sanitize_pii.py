#!/usr/bin/env python3
"""
Repo-wide PII sanitizer for orthogonal-engineering.
Handles 6 categories: HRT/medical, substance use, diagnosis, profanity,
personal names, and NSFW content.

Usage:
    python scripts/sanitize_pii.py --dry-run            # Preview (default)
    python scripts/sanitize_pii.py --apply              # Apply changes
    python scripts/sanitize_pii.py --apply --paths FILE1 FILE2
    python scripts/sanitize_pii.py --dry-run --ci       # CI mode: exit 1 if PII found

Per SAFE_OPERATIONS.md: --dry-run is the default behavior.
--apply is required for actual writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Term lists
# ---------------------------------------------------------------------------

# Category 1 — HRT/Medical
HRT_TERMS: list[tuple[str, str]] = [
    (r"\bHRT\b", "[MEDICAL_REDACTED]"),
    (r"\bhrt\b", "[MEDICAL_REDACTED]"),
    (r"\bhormone replacement\b", "[MEDICAL_REDACTED]"),
    (r"\bhormone therapy\b", "[MEDICAL_REDACTED]"),
    (r"\bhormonal change\b", "[MEDICAL_REDACTED]"),
    (r"\bhormonal changes\b", "[MEDICAL_REDACTED]"),
    (r"\bgender affirming\b", "[MEDICAL_REDACTED]"),
    (r"\bgender affirmation\b", "[MEDICAL_REDACTED]"),
    (r"\bgender transition\b", "[MEDICAL_REDACTED]"),
    (r"\bgender affirming care\b", "[MEDICAL_REDACTED]"),
    (r"\bgender affirming surgery\b", "[MEDICAL_REDACTED]"),
    (r"\bgender confirmation\b", "[MEDICAL_REDACTED]"),
    (r"\bgender confirming\b", "[MEDICAL_REDACTED]"),
    (r"\bestrogen\b", "[MEDICAL_REDACTED]"),
    (r"\bestrogens\b", "[MEDICAL_REDACTED]"),
    (r"\bestrogenic\b", "[MEDICAL_REDACTED]"),
    (r"\btestosterone\b", "[MEDICAL_REDACTED]"),
    (r"\btestosterones\b", "[MEDICAL_REDACTED]"),
    (r"\bandrogen\b", "[MEDICAL_REDACTED]"),
    (r"\bandrogens\b", "[MEDICAL_REDACTED]"),
    (r"\bandrogenic\b", "[MEDICAL_REDACTED]"),
    (r"\bgender reassignment\b", "[MEDICAL_REDACTED]"),
    (r"\bsex reassignment\b", "[MEDICAL_REDACTED]"),
    (r"\bSRS\b", "[MEDICAL_REDACTED]"),
    (r"\bGRS\b", "[MEDICAL_REDACTED]"),
    (r"\bgender dysphoria\b", "[MEDICAL_REDACTED]"),
    (r"\bdysphoria\b", "[MEDICAL_REDACTED]"),
    (r"\bdysphoric\b", "[MEDICAL_REDACTED]"),
    (r"\bgender incongruence\b", "[MEDICAL_REDACTED]"),
    (r"\bincongruence\b", "[MEDICAL_REDACTED]"),
    (r"\btransgender\b", "[MEDICAL_REDACTED]"),
    (r"\bcross-sex\b", "[MEDICAL_REDACTED]"),
    (r"\bcross sex\b", "[MEDICAL_REDACTED]"),
    (r"\bsex change\b", "[MEDICAL_REDACTED]"),
]

# Category 2 — Substance Use
SUBSTANCE_TERMS: list[tuple[str, str]] = [
    (r"\bweed\b", "[SUBSTANCE_REDACTED]"),
    (r"\bmarijuana\b", "[SUBSTANCE_REDACTED]"),
    (r"\bcannabis\b", "[SUBSTANCE_REDACTED]"),
    (r"\bthc\b", "[SUBSTANCE_REDACTED]"),
    (r"\bcbd\b", "[SUBSTANCE_REDACTED]"),
    (r"\bstoned\b", "[SUBSTANCE_REDACTED]"),
    (r"\bedibles?\b", "[SUBSTANCE_REDACTED]"),
    (r"\bsmoking weed\b", "[SUBSTANCE_REDACTED]"),
    (r"\bsmoke weed\b", "[SUBSTANCE_REDACTED]"),
    (r"\bget(?:ting)? high\b", "[SUBSTANCE_REDACTED]"),
]

# Category 3 — Diagnosis
DIAGNOSIS_TERMS: list[tuple[str, str]] = [
    (r"\bselective mutism\b", "[DIAGNOSIS_REDACTED]"),
    (r"\bselective mute\b", "[DIAGNOSIS_REDACTED]"),
    (r"\bselectively mute\b", "[DIAGNOSIS_REDACTED]"),
]

# Category 4 — Profanity
PROFANITY_TERMS: list[tuple[str, str]] = [
    (r"\bfuck(?:ing|ed)?\b", "[PROFANITY_REDACTED]"),
    (r"\bshit(?:ty)?\b", "[PROFANITY_REDACTED]"),
    (r"\bdamn\b", "[PROFANITY_REDACTED]"),
    (r"\bbitch\b", "[PROFANITY_REDACTED]"),
    (r"\bass(?!ign|ert|ess|ume|et|oci|ist)\b", "[PROFANITY_REDACTED]"),
    (r"\basshole\b", "[PROFANITY_REDACTED]"),
]

# Category 5 — Personal Names (specific to this repo's contamination scope)
PERSONAL_NAME_TERMS: list[tuple[str, str]] = [
    (r"\bAllain\b", "[NAME_REDACTED]"),
    (r"\bPomeroy\b", "[NAME_REDACTED]"),
    (r"\bCarlisle\b", "[NAME_REDACTED]"),
    (r"\bYoungblood\b", "[NAME_REDACTED]"),
    (r"\bCowart\b", "[NAME_REDACTED]"),
    (r"\bCozad\b", "[NAME_REDACTED]"),
    (r"\bEmery\b", "[NAME_REDACTED]"),
    (r"\bHess\b", "[NAME_REDACTED]"),
    (r"\bZam\b", "[NAME_REDACTED]"),
]

# Category 6 — NSFW/Sexual Content
# Context-aware: exclude clinical/medical compound phrases.
NSFW_TERMS: list[tuple[str, str]] = [
    (r"\bporn(?:ography)?\b", "[NSFW_REDACTED]"),
    (r"\bxxx\b", "[NSFW_REDACTED]"),
    (r"\bnsfw\b", "[NSFW_REDACTED]"),
    # \bsex\b — exclude clinical compounds (sex hormone, sex assigned, etc.)
    (
        r"\bsex\b(?!\s*(?:hormone|education|assigned|characteristic|reassignment|change|offender|abuse|ual\b))",
        "[NSFW_REDACTED]",
    ),
    (r"\bnude\b", "[NSFW_REDACTED]"),
    (r"\bnudity\b", "[NSFW_REDACTED]"),
    (r"\bnaked\b", "[NSFW_REDACTED]"),
    # \bexplicit\b — exclude engineering uses
    (
        r"\bexplicit\b(?!\s*(?:content\s+flag|parameter|argument|instruction|keyword|type))",
        "[NSFW_REDACTED]",
    ),
]

ALL_CATEGORIES: list[tuple[str, list[tuple[str, str]]]] = [
    ("hrt", HRT_TERMS),
    ("substance", SUBSTANCE_TERMS),
    ("diagnosis", DIAGNOSIS_TERMS),
    ("profanity", PROFANITY_TERMS),
    ("personal_name", PERSONAL_NAME_TERMS),
    ("nsfw", NSFW_TERMS),
]

# ---------------------------------------------------------------------------
# Directories and file types
# ---------------------------------------------------------------------------

PROCESS_EXTENSIONS: set[str] = {
    ".json", ".jsonl", ".md", ".txt", ".csv", ".mm", ".rst",
}

# Directories that must never be touched (engineering content)
PROTECTED_DIRS: tuple[str, ...] = (
    "ontology/",
    "analysis/taxonomy/",
    "yeshua_system/",
    "core/labor/",
    "core/semiotics/",
    "tests/",
    "docs/METHODOLOGY_GUIDE.md",
    "hrt_sanitization_backups/",
    "sanitization_backups/",
)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _is_protected(rel_path: str) -> bool:
    """Return True if rel_path is inside a protected directory."""
    for prefix in PROTECTED_DIRS:
        if rel_path.startswith(prefix) or rel_path == prefix.rstrip("/"):
            return True
    return False


def _hash_term(term: str) -> str:
    """Return SHA-256 hex digest of term (never store the term itself)."""
    return hashlib.sha256(term.encode("utf-8")).hexdigest()


def _read_text(path: Path) -> Optional[str]:
    """Read file as UTF-8, falling back to latin-1. Returns None for binary."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None


def sanitize_content(content: str) -> Tuple[str, List[Dict]]:
    """
    Apply all 6 category term lists to `content`.
    Returns (sanitized_content, list_of_redaction_records).
    Each record: {category, tag, original_term_hash, count}.
    """
    result = content
    records: list[Dict] = []

    for category, terms in ALL_CATEGORIES:
        for pattern, tag in terms:
            # Already-tagged strings should not be double-replaced
            skip_tag = tag  # e.g. [MEDICAL_REDACTED]

            def _replace(m: re.Match, _tag: str = tag, _cat: str = category,
                         _skip: str = skip_tag) -> str:
                matched = m.group(0)
                if matched.startswith("[") and matched.endswith("]"):
                    return matched
                records.append({
                    "category": _cat,
                    "tag": _tag,
                    "original_term_sha256": _hash_term(matched),
                })
                return _tag

            result = re.sub(pattern, _replace, result, flags=re.IGNORECASE)

    return result, records


def sanitize_file_content(path: Path, content: str) -> Tuple[str, List[Dict]]:
    """Sanitize and attach file path to each record."""
    sanitized, records = sanitize_content(content)
    for r in records:
        r["file"] = str(path)
    return sanitized, records


def has_pii(content: str) -> bool:
    """Return True if content contains any PII from any category."""
    for _category, terms in ALL_CATEGORIES:
        for pattern, _tag in terms:
            if re.search(pattern, content, flags=re.IGNORECASE):
                return True
    return False


# ---------------------------------------------------------------------------
# Sanitizer class
# ---------------------------------------------------------------------------

class PIISanitizer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.all_records: list[Dict] = []
        self.files_sanitized: list[str] = []
        self.backup_dir: Optional[Path] = None

    # ------------------------------------------------------------------ scan

    def _should_process(self, path: Path) -> bool:
        if path.suffix.lower() not in PROCESS_EXTENSIONS:
            return False
        rel = str(path.relative_to(self.repo_root))
        if _is_protected(rel):
            return False
        return True

    def find_pii_files(self, paths: Optional[List[Path]] = None) -> List[Path]:
        search = paths or [self.repo_root]
        found: list[Path] = []
        for sp in search:
            if sp.is_file():
                if self._should_process(sp):
                    content = _read_text(sp)
                    if content and has_pii(content):
                        found.append(sp)
            else:
                for ext in PROCESS_EXTENSIONS:
                    for fp in sp.rglob(f"*{ext}"):
                        if self._should_process(fp):
                            content = _read_text(fp)
                            if content and has_pii(content):
                                found.append(fp)
        return sorted(set(found))

    # ----------------------------------------------------------------- write

    def _backup(self, path: Path) -> None:
        if self.backup_dir is None:
            self.backup_dir = (
                self.repo_root
                / "sanitization_backups"
                / datetime.now().strftime("%Y%m%d_%H%M%S")
            )
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        rel = path.relative_to(self.repo_root)
        dest = self.backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

    def process_file(self, path: Path, apply: bool) -> List[Dict]:
        content = _read_text(path)
        if content is None:
            return []

        sanitized, records = sanitize_file_content(path, content)
        if not records:
            return []

        rel = str(path.relative_to(self.repo_root))
        if apply:
            self._backup(path)
            path.write_text(sanitized, encoding="utf-8")
            print(f"  [SANITIZED] {rel} — {len(records)} redaction(s)")
        else:
            print(f"  [DRY RUN]   {rel} — would redact {len(records)} term(s)")

        return records

    # ------------------------------------------------------------------- run

    def run(
        self,
        paths: Optional[List[Path]],
        apply: bool,
        ci: bool,
    ) -> Dict:
        pii_files = self.find_pii_files(paths)

        if not pii_files:
            print("No PII found.")
            return {"status": "clean", "files": [], "redactions": 0}

        mode = "APPLY" if apply else "DRY RUN"
        print(f"\n[{mode}] Found {len(pii_files)} file(s) with PII:")
        for fp in pii_files:
            print(f"  - {fp.relative_to(self.repo_root)}")

        if ci and not apply:
            print("\n[CI] PII detected — exiting with code 1.")
            sys.exit(1)

        total_records: list[Dict] = []
        sanitized_files: list[str] = []

        for fp in pii_files:
            records = self.process_file(fp, apply=apply)
            total_records.extend(records)
            if records and apply:
                sanitized_files.append(str(fp.relative_to(self.repo_root)))

        # Summary by category
        by_cat: Dict[str, int] = {}
        for r in total_records:
            by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1

        audit: Dict = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "repo_root": str(self.repo_root),
            "files_with_pii": [str(fp.relative_to(self.repo_root)) for fp in pii_files],
            "files_sanitized": sanitized_files,
            "total_redactions": len(total_records),
            "by_category": by_cat,
            "records": total_records,
        }

        if apply:
            audit_path = self.repo_root / "sanitization_audit.json"
            audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
            print(f"\nAudit log written to: {audit_path.relative_to(self.repo_root)}")

        return audit


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repo-wide PII sanitizer (HRT, substance, diagnosis, profanity, names, NSFW)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply sanitization (write files). Default is dry-run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without modifying files (default).",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit 1 if any PII is found (implies dry-run).",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Specific files or directories to scan (default: entire repo).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd).",
    )
    args = parser.parse_args()

    apply = args.apply and not args.ci
    repo_root = args.repo_root.resolve()

    target_paths: Optional[List[Path]] = None
    if args.paths:
        target_paths = [repo_root / p for p in args.paths]
        for p in target_paths:
            if not p.exists():
                print(f"Error: path not found: {p}", file=sys.stderr)
                sys.exit(2)

    sanitizer = PIISanitizer(repo_root)
    result = sanitizer.run(paths=target_paths, apply=apply, ci=args.ci)

    print("\n" + "=" * 60)
    print("PII SANITIZATION SUMMARY")
    print("=" * 60)
    print(f"Mode          : {'APPLY' if apply else 'DRY RUN'}")
    print(f"Files with PII: {len(result.get('files_with_pii', []))}")
    print(f"Total redacted: {result.get('total_redactions', 0)}")
    if result.get("by_category"):
        print("By category:")
        for cat, count in result["by_category"].items():
            print(f"  {cat:<15}: {count}")
    if not apply:
        print("\nNOTE: dry-run mode. Pass --apply to write changes.")


if __name__ == "__main__":
    main()
