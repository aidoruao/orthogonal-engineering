#!/usr/bin/env python3
"""
Sanitize HRT and sensitive terms in repository files.
Replaces sensitive terms with [REDACTED] in tracked repository files.

Usage:
    python sanitize_repo_hrt.py [--dry-run] [--backup-dir DIR] [--paths PATH1 PATH2...]

Example:
    python sanitize_repo_hrt.py --dry-run                    # Preview changes
    python sanitize_repo_hrt.py --backup-dir ./backups       # Create backups
    python sanitize_repo_hrt.py --paths 1B/ 2b/             # Specific paths
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class RepositorySanitizer:
    """Sanitize HRT and sensitive terms in repository files."""

    # Sensitive terms to redact (case-insensitive)
    SENSITIVE_TERMS = [
        # HRT and hormone terms
        r"\bHRT\b",
        r"\bhrt\b",
        r"\bhormone replacement\b",
        r"\bhormone therapy\b",
        # Gender/transition terms
        r"\bgender affirming\b",
        r"\bgender affirmation\b",
        r"\bgender transition\b",
        r"\btransitions\b",
        r"\btransition\b",
        r"\bgender dysphoria\b",
        r"\bdysphoria\b",
        r"\bdysphoric\b",
        r"\bgender incongruence\b",
        r"\bincongruence\b",
        r"\bgender identity\b",
        r"\btransgender\b",
        r"\btrans\b",
        r"\bcross-sex\b",
        r"\bcross sex\b",
        r"\bsex change\b",
        r"\bsex reassignment\b",
        r"\bgender reassignment\b",
        r"\bsex reassignment surgery\b",
        r"\bgender reassignment surgery\b",
        r"\bSRS\b",
        r"\bGRS\b",
        r"\bgender affirming care\b",
        r"\bgender affirming surgery\b",
        r"\bgender confirmation\b",
        r"\bgender confirming\b",
        # Sexual/biological terms
        r"\bsex\b",
        r"\bsexual\b",
        r"\bsexes\b",
        r"\bsexuality\b",
        r"\bpenis\b",
        r"\bpenises\b",
        r"\borgasm\b",
        r"\borgasms\b",
        r"\bmasturbation\b",
        r"\bmasturbations\b",
        r"\berect\b",
        r"\berection\b",
        r"\berections\b",
        r"\bfeminization\b",
        r"\bfeminizations\b",
        r"\bfeminizing\b",
        r"\bfeminize\b",
        r"\bmasculinizing\b",
        r"\bmasculinize\b",
        r"\bglans\b",
        r"\bglanses\b",
        r"\bandrogen\b",
        r"\bandrogens\b",
        r"\bandrogenic\b",
        r"\bestrogen\b",
        r"\bestrogens\b",
        r"\bestrogenic\b",
        r"\btestosterone\b",
        r"\btestosterones\b",
        r"\bphallus\b",
        r"\bphalli\b",
        r"\bgenital\b",
        r"\bgenitals\b",
        r"\bgenitalia\b",
        r"\breproductive\b",
        r"\bnude\b",
        r"\bnaked\b",
        r"\bexplicit\b",
        r"\bintimate\b",
        r"\bprivate\b",
        # Anatomical terms
        r"\bbody part\b",
        r"\bbody parts\b",
        r"\bphysical change\b",
        r"\bphysical changes\b",
        r"\bhormonal change\b",
        r"\bhormonal changes\b",
        r"\bscrotum\b",
        r"\bscrotums\b",
        r"\btestes\b",
        r"\btestis\b",
        r"\btesticles\b",
        r"\btesticular\b",
        r"\bprostate\b",
        r"\bprostates\b",
        r"\bvagina\b",
        r"\bvaginas\b",
        r"\bvulva\b",
        r"\bvulvas\b",
        r"\bclitoris\b",
        r"\bclitorises\b",
        r"\bovary\b",
        r"\bovaries\b",
        r"\bovarian\b",
        r"\buterus\b",
        r"\buteri\b",
        r"\bwomb\b",
        r"\bwombs\b",
        r"\bcervix\b",
        r"\bcervices\b",
        r"\bpenile\b",
        r"\bvaginal\b",
        r"\brectal\b",
        r"\banal\b",
        # Colloquial terms
        r"\bprivate parts\b",
        r"\bdownstairs\b",
        r"\bnether regions\b",
        r"\bgenital region\b",
        r"\bpelvic region\b",
        r"\bpelvic area\b",
        r"\bpelvis\b",
        r"\bcrotch\b",
        r"\bgroin\b",
        r"\bloin\b",
        r"\bpubic\b",
        r"\bpubis\b",
        r"\bpubic hair\b",
        r"\bpubic area\b",
        # Additional terms
        r"\bcopulation\b",
        r"\bintercourse\b",
        r"\bcoitus\b",
        r"\bcoital\b",
        r"\bfertility\b",
        r"\bconception\b",
        r"\bcontraception\b",
        r"\bcontraceptive\b",
        r"\bpregnancy\b",
        r"\bpregnant\b",
        r"\bgestation\b",
        r"\bgestational\b",
        r"\bmenstrual\b",
        r"\bmenstruation\b",
        r"\bmenstruate\b",
        r"\bperiod\b",
        r"\bperiods\b",
        r"\bmenarche\b",
        r"\bmenopause\b",
        r"\bmenopausal\b",
        r"\bovulation\b",
        r"\bovulatory\b",
        r"\bfertile\b",
        r"\bsterile\b",
        r"\bsterility\b",
        r"\bimpotence\b",
        r"\bimpotent\b",
        r"\berectile\b",
        r"\berectile dysfunction\b",
        r"\bED\b",
        r"\bpremature ejaculation\b",
        r"\bejaculation\b",
        r"\bejaculations\b",
        r"\bejaculate\b",
        r"\bsemen\b",
        r"\bseminal\b",
        r"\bsperm\b",
        r"\bspermatic\b",
        r"\bvaginal secretion\b",
        r"\bvaginal secretions\b",
        r"\bcervical mucus\b",
        r"\bdischarge\b",
        r"\bdischarges\b",
        # Modifiers and phrases
        r"\bsexual intercourse\b",
        r"\bsexual activity\b",
        r"\bsexual act\b",
        r"\bsexual acts\b",
        r"\bsexual behavior\b",
        r"\bsexual behaviours\b",
        r"\bsexual practice\b",
        r"\bsexual practices\b",
        r"\bsexual function\b",
        r"\bsexual functions\b",
        r"\bsexual health\b",
        r"\bsexual development\b",
        r"\bsexual maturity\b",
        r"\bsexual characteristics\b",
        r"\bsexual dimorphism\b",
        r"\bsexual differentiation\b",
        r"\bsex characteristic\b",
        r"\bsecondary sex characteristic\b",
        r"\bbreast\b",
        r"\bbreasts\b",
        r"\bchest\b",
        r"\bbottom\b",
        r"\btop\b",
    ]

    # File extensions to process
    PROCESS_EXTENSIONS = {".jsonl", ".json", ".md", ".txt", ".mdx", ".rst"}

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.changes: List[Dict] = []
        self.backup_dir: Optional[Path] = None

    def find_sensitive_files(self, paths: Optional[List[Path]] = None) -> List[Path]:
        """Find files containing sensitive terms."""
        sensitive_files = []
        search_paths = paths if paths else [self.repo_root]

        for search_path in search_paths:
            if search_path.is_file():
                if self._file_contains_sensitive(search_path):
                    sensitive_files.append(search_path)
            else:
                for ext in self.PROCESS_EXTENSIONS:
                    for file_path in search_path.rglob(f"*{ext}"):
                        if self._file_contains_sensitive(file_path):
                            sensitive_files.append(file_path)

        return sorted(set(sensitive_files))

    def _file_contains_sensitive(self, file_path: Path) -> bool:
        """Check if file contains sensitive terms."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except:
                # Binary file, skip
                return False

        # Check for any sensitive term
        for pattern in self.SENSITIVE_TERMS:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def sanitize_content(self, content: str) -> Tuple[str, List[Dict]]:
        """Sanitize sensitive content, replacing with [REDACTED]."""
        sanitized = content
        audit_entries = []

        for pattern in self.SENSITIVE_TERMS:
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            for match in matches:
                matched_text = match.group(0)
                # Replace with [REDACTED]
                sanitized = sanitized.replace(matched_text, "[REDACTED]")
                audit_entries.append(
                    {
                        "original": matched_text,
                        "sanitized": "[REDACTED]",
                        "pattern": pattern,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return sanitized, audit_entries

    def sanitize_jsonl_file(self, file_path: Path) -> List[Dict]:
        """Special handling for JSONL files (preserve JSON structure)."""
        audit_entries = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                lines = f.readlines()

        new_lines = []
        for i, line in enumerate(lines):
            line = line.rstrip("\n")
            if not line.strip():
                new_lines.append(line)
                continue

            try:
                data = json.loads(line)
                # Check if this is a chat message JSONL format
                if isinstance(data, dict) and "content" in data:
                    original_content = data["content"]
                    sanitized_content, line_audits = self.sanitize_content(
                        original_content
                    )

                    if sanitized_content != original_content:
                        data["content"] = sanitized_content
                        data["metadata"] = data.get("metadata", {})
                        data["metadata"]["sanitized_at"] = datetime.now().isoformat()
                        data["metadata"]["original_sha256"] = hashlib.sha256(
                            original_content.encode("utf-8")
                        ).hexdigest()

                        # Recompute hash and length if fields exist
                        if "sha256_hash" in data:
                            data["sha256_hash"] = hashlib.sha256(
                                sanitized_content.encode("utf-8")
                            ).hexdigest()
                        if "byte_length" in data:
                            data["byte_length"] = len(sanitized_content.encode("utf-8"))

                        for audit in line_audits:
                            audit["line_number"] = i + 1
                            audit["file"] = str(file_path.relative_to(self.repo_root))
                            audit_entries.append(audit)

                    new_lines.append(json.dumps(data, ensure_ascii=False))
                else:
                    # Regular JSON line, sanitize the whole line as text
                    sanitized_line, line_audits = self.sanitize_content(line)
                    new_lines.append(sanitized_line)

                    for audit in line_audits:
                        audit["line_number"] = i + 1
                        audit["file"] = str(file_path.relative_to(self.repo_root))
                        audit_entries.append(audit)

            except json.JSONDecodeError:
                # Not valid JSON, treat as plain text
                sanitized_line, line_audits = self.sanitize_content(line)
                new_lines.append(sanitized_line)

                for audit in line_audits:
                    audit["line_number"] = i + 1
                    audit["file"] = str(file_path.relative_to(self.repo_root))
                    audit_entries.append(audit)

        return new_lines, audit_entries

    def sanitize_text_file(self, file_path: Path) -> Tuple[List[str], List[Dict]]:
        """Sanitize regular text files."""
        audit_entries = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                lines = f.readlines()

        new_lines = []
        for i, line in enumerate(lines):
            sanitized_line, line_audits = self.sanitize_content(line)
            new_lines.append(sanitized_line)

            for audit in line_audits:
                audit["line_number"] = i + 1
                audit["file"] = str(file_path.relative_to(self.repo_root))
                audit_entries.append(audit)

        return new_lines, audit_entries

    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file."""
        if not self.backup_dir:
            self.backup_dir = (
                self.repo_root
                / "hrt_sanitization_backups"
                / datetime.now().strftime("%Y%m%d_%H%M%S")
            )

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        rel_path = file_path.relative_to(self.repo_root)
        backup_path = self.backup_dir / rel_path

        # Create parent directories in backup location
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        return backup_path

    def process_file(self, file_path: Path, dry_run: bool = False) -> List[Dict]:
        """Process a single file."""
        audit_entries = []

        # Determine file type
        if file_path.suffix == ".jsonl":
            new_lines, file_audits = self.sanitize_jsonl_file(file_path)
        else:
            new_lines, file_audits = self.sanitize_text_file(file_path)

        audit_entries.extend(file_audits)

        if not file_audits:
            # No changes needed
            return audit_entries

        if dry_run:
            print(
                f"  [DRY RUN] Would sanitize {len(file_audits)} terms in {file_path.relative_to(self.repo_root)}"
            )
            return audit_entries

        # Create backup
        backup_path = self.create_backup(file_path)
        print(f"  Created backup: {backup_path.relative_to(self.repo_root)}")

        # Write sanitized content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        print(
            f"  Sanitized {len(file_audits)} terms in {file_path.relative_to(self.repo_root)}"
        )

        return audit_entries

    def run(
        self,
        paths: Optional[List[Path]] = None,
        dry_run: bool = False,
        backup_dir: Optional[Path] = None,
    ) -> Dict:
        """Main sanitization process."""
        self.backup_dir = backup_dir

        print(f"Scanning for sensitive content in {self.repo_root}...")

        # Find files with sensitive content
        sensitive_files = self.find_sensitive_files(paths)

        if not sensitive_files:
            print("No files containing sensitive terms found.")
            return {"processed": 0, "changes": 0, "files": []}

        print(f"Found {len(sensitive_files)} files with sensitive content:")
        for file_path in sensitive_files:
            print(f"  - {file_path.relative_to(self.repo_root)}")

        if dry_run:
            print("\nDRY RUN MODE: No files will be modified.")
            response = input("Continue with dry run? (y/n): ")
        else:
            print("\nWARNING: This will modify files in place.")
            print(
                "Backups will be created in:",
                self.backup_dir or "./hrt_sanitization_backups/",
            )
            response = input("Continue? (y/n): ")

        if response.lower() != "y":
            print("Aborted.")
            return {"processed": 0, "changes": 0, "files": []}

        # Process files
        total_changes = 0
        processed_files = []

        for file_path in sensitive_files:
            print(f"\nProcessing {file_path.relative_to(self.repo_root)}...")
            audit_entries = self.process_file(file_path, dry_run)

            if audit_entries:
                total_changes += len(audit_entries)
                self.changes.extend(audit_entries)
                processed_files.append(str(file_path.relative_to(self.repo_root)))

        # Save audit log
        if self.changes and not dry_run:
            audit_log_path = self.repo_root / "hrt_sanitization_audit.json"
            if self.backup_dir:
                audit_log_path = self.backup_dir / "audit_log.json"

            audit_log_path.parent.mkdir(parents=True, exist_ok=True)

            audit_data = {
                "timestamp": datetime.now().isoformat(),
                "repo_root": str(self.repo_root),
                "total_changes": total_changes,
                "processed_files": processed_files,
                "changes": self.changes,
            }

            with open(audit_log_path, "w", encoding="utf-8") as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False)

            print(f"\nAudit log saved to: {audit_log_path.relative_to(self.repo_root)}")

        return {
            "processed": len(processed_files),
            "changes": total_changes,
            "files": processed_files,
            "dry_run": dry_run,
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sanitize HRT and sensitive terms in repository files."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to scan (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="Directory for backups (default: ./hrt_sanitization_backups/)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Convert paths to absolute paths
    repo_root = args.repo_root.resolve()
    paths = [repo_root / Path(p).resolve() for p in args.paths]

    # Verify paths exist
    for path in paths:
        if not path.exists():
            print(f"Error: Path not found: {path}")
            sys.exit(1)

    # Create sanitizer
    sanitizer = RepositorySanitizer(repo_root)

    # Run sanitization
    result = sanitizer.run(
        paths=paths, dry_run=args.dry_run, backup_dir=args.backup_dir
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SANITIZATION SUMMARY")
    print("=" * 60)
    print(f"Repository root: {repo_root}")
    print(f"Files processed: {result['processed']}")
    print(f"Terms sanitized: {result['changes']}")
    print(f"Dry run: {result['dry_run']}")

    if result["processed"] > 0:
        print("\nProcessed files:")
        for file_path in result["files"]:
            print(f"  - {file_path}")

    if args.dry_run:
        print("\nNOTE: This was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
