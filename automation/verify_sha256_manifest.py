#!/usr/bin/env python3
"""
SHA256 MANIFEST VERIFIER - PHASE 8 ARTIFACT VERIFICATION

Purpose: Verify SHA256 hashes of all files in the Orthogonal Engineering repository
against the stored manifest to ensure file integrity and detect unauthorized modifications.

Methodological Principle: Complete transparency verification. Every artifact must match
its recorded SHA256 hash. Any mismatch indicates corruption or unauthorized modification.

Author: Orthogonal Engineering System
Date: 2026-01-20
Version: 1.0.0
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SHA256ManifestVerifier:
    """Verify SHA256 manifest for repository files."""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.exclude_patterns = [
            ".git",
            "__pycache__",
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".DS_Store",
            "Thumbs.db",
            "node_modules",
            "venv",
            "env",
            ".env",
            ".venv",
        ]

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from verification."""
        path_str = str(path)

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True

        # Check if it's a directory
        if path.is_dir():
            return True

        # Check file size (skip very large files)
        try:
            if path.stat().st_size > 100 * 1024 * 1024:  # 100MB
                return True
        except (OSError, ValueError):
            return True

        return False

    def calculate_sha256(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of a file."""
        try:
            sha256_hash = hashlib.sha256()

            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            return sha256_hash.hexdigest()

        except Exception as e:
            print(f"  Error hashing {file_path.relative_to(self.repo_root)}: {e}")
            return None

    def load_manifest(self, manifest_path: Optional[Path] = None) -> Dict:
        """Load SHA256 manifest from file."""
        if manifest_path is None:
            # Look for latest manifest
            manifest_dir = self.repo_root / "documentation" / "sha256_manifests"
            if manifest_dir.exists():
                json_files = list(manifest_dir.glob("artifact_manifest_*.json"))
                if json_files:
                    # Get latest by timestamp
                    json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    manifest_path = json_files[0]
                else:
                    # Try main manifest
                    main_manifest = (
                        self.repo_root / "documentation" / "ARTIFACT_MANIFEST_SHA256.md"
                    )
                    if main_manifest.exists():
                        # Parse from markdown (simplified)
                        return self.parse_markdown_manifest(main_manifest)
            else:
                # Try main manifest directly
                main_manifest = (
                    self.repo_root / "documentation" / "ARTIFACT_MANIFEST_SHA256.md"
                )
                if main_manifest.exists():
                    return self.parse_markdown_manifest(main_manifest)

        if manifest_path is None or not manifest_path.exists():
            raise FileNotFoundError(
                f"No SHA256 manifest found. Generate one first with: "
                f"python automation/generate_sha256_manifest.py"
            )

        print(f"Loading manifest: {manifest_path.relative_to(self.repo_root)}")

        if manifest_path.suffix == ".json":
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            return manifest_data
        else:
            return self.parse_markdown_manifest(manifest_path)

    def parse_markdown_manifest(self, manifest_path: Path) -> Dict:
        """Parse SHA256 manifest from markdown format."""
        print(f"Parsing markdown manifest: {manifest_path.relative_to(self.repo_root)}")

        manifest_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": str(manifest_path),
                "format": "markdown",
            },
            "files": {},
        }

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple parsing for markdown table
            import re

            # Look for the file table
            table_pattern = r"\| Phase \| File \| SHA256 Hash \| Size \| Modified \|\n\|[- ]+\|[- ]+\|[- ]+\|[- ]+\|[- ]+\|\n(.*?)\n\n"
            table_match = re.search(table_pattern, content, re.DOTALL)

            if table_match:
                table_content = table_match.group(1)
                rows = table_content.strip().split("\n")

                for row in rows:
                    if row.startswith("|"):
                        cells = [cell.strip() for cell in row.split("|")[1:-1]]
                        if len(cells) >= 5:
                            phase = cells[0]
                            file_path = cells[1].strip("`")
                            sha256 = cells[2].strip("`")
                            size = cells[3]
                            modified = cells[4]

                            # Clean up file path
                            if file_path.startswith("..."):
                                # This is a truncated path, we can't verify it
                                continue

                            manifest_data["files"][file_path] = {
                                "sha256": sha256,
                                "phase": phase,
                                "path": file_path,
                                "size": size,
                                "modified": modified,
                            }

            print(f"Parsed {len(manifest_data['files'])} files from markdown manifest")
            return manifest_data

        except Exception as e:
            print(f"Warning: Could not parse markdown manifest: {e}")
            return manifest_data

    def scan_repository(self) -> List[Path]:
        """Scan repository for all files to verify."""
        files_to_verify = []

        for root, dirs, filenames in os.walk(self.repo_root):
            root_path = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            for filename in filenames:
                file_path = root_path / filename

                if not self.should_exclude(file_path):
                    files_to_verify.append(file_path)

        # Sort by path for consistent output
        files_to_verify.sort(key=lambda x: str(x.relative_to(self.repo_root)))

        return files_to_verify

    def verify_files(self, manifest: Dict, files: List[Path]) -> Dict[str, List]:
        """Verify files against manifest."""
        manifest_files = manifest.get("files", {})
        results = {
            "verified": [],
            "mismatched": [],
            "missing_in_repo": [],
            "missing_in_manifest": [],
            "errors": [],
        }

        print(f"\nVerifying {len(files)} files against manifest...")
        print("-" * 80)

        # Check files in repository
        for i, file_path in enumerate(files, 1):
            rel_path = str(file_path.relative_to(self.repo_root))

            # Show progress
            if i % 50 == 0 or i == len(files):
                print(f"  Verified {i}/{len(files)} files...")

            if rel_path in manifest_files:
                expected_hash = manifest_files[rel_path].get("sha256")

                if not expected_hash:
                    results["errors"].append(
                        {
                            "path": rel_path,
                            "error": "No hash in manifest",
                        }
                    )
                    continue

                actual_hash = self.calculate_sha256(file_path)

                if actual_hash is None:
                    results["errors"].append(
                        {
                            "path": rel_path,
                            "error": "Could not calculate hash",
                        }
                    )
                elif actual_hash == expected_hash:
                    results["verified"].append(
                        {
                            "path": rel_path,
                            "hash": actual_hash,
                            "phase": manifest_files[rel_path].get("phase", "Unknown"),
                        }
                    )
                else:
                    results["mismatched"].append(
                        {
                            "path": rel_path,
                            "expected": expected_hash,
                            "actual": actual_hash,
                            "phase": manifest_files[rel_path].get("phase", "Unknown"),
                        }
                    )
            else:
                results["missing_in_manifest"].append(
                    {
                        "path": rel_path,
                        "error": "File not in manifest",
                    }
                )

        # Check for files in manifest but not in repository
        manifest_paths = set(manifest_files.keys())
        repo_paths = {str(f.relative_to(self.repo_root)) for f in files}

        missing_paths = manifest_paths - repo_paths
        for path in missing_paths:
            results["missing_in_repo"].append(
                {
                    "path": path,
                    "expected_hash": manifest_files[path].get("sha256"),
                    "phase": manifest_files[path].get("phase", "Unknown"),
                }
            )

        return results

    def print_results(self, results: Dict[str, List], manifest: Dict) -> None:
        """Print verification results."""
        total_verified = len(results["verified"])
        total_mismatched = len(results["mismatched"])
        total_missing_repo = len(results["missing_in_repo"])
        total_missing_manifest = len(results["missing_in_manifest"])
        total_errors = len(results["errors"])

        total_files = (
            total_verified + total_mismatched + total_missing_manifest + total_errors
        )
        manifest_files = len(manifest.get("files", {}))

        print("\n" + "=" * 80)
        print("SHA256 MANIFEST VERIFICATION RESULTS")
        print("=" * 80)
        print(f"Verification date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Files in repository: {total_files}")
        print(f"Files in manifest: {manifest_files}")
        print()

        # Summary
        print("SUMMARY")
        print("-" * 40)
        print(f"[OK] Verified:        {total_verified}")
        print(f"[X] Mismatched:      {total_mismatched}")
        print(f"[i] Missing in repo: {total_missing_repo}")
        print(f"[i] Missing in manifest: {total_missing_manifest}")
        print(f"[!] Errors:          {total_errors}")
        print()

        # Calculate verification percentage
        if total_files > 0:
            verification_percentage = (total_verified / total_files) * 100
            print(f"Verification rate: {verification_percentage:.1f}%")

            if verification_percentage == 100 and total_mismatched == 0:
                print("[OK] ALL FILES VERIFIED SUCCESSFULLY")
            elif verification_percentage >= 95:
                print("[!] MOST FILES VERIFIED (minor issues)")
            else:
                print("[X] SIGNIFICANT VERIFICATION ISSUES")
        print()

        # Detailed results
        if results["mismatched"]:
            print("HASH MISMATCHES (POTENTIAL TAMPERING)")
            print("-" * 40)
            for item in results["mismatched"][:10]:  # Show first 10
                print(f"  {item['path']}")
                print(f"    Expected: {item['expected'][:16]}...")
                print(f"    Actual:   {item['actual'][:16]}...")
                print(f"    Phase:    {item['phase']}")
                print()

            if len(results["mismatched"]) > 10:
                print(f"  ... and {len(results['mismatched']) - 10} more mismatches")
            print()

        if results["missing_in_repo"]:
            print("FILES IN MANIFEST BUT NOT IN REPOSITORY")
            print("-" * 40)
            for item in results["missing_in_repo"][:10]:
                print(f"  {item['path']} (Phase: {item['phase']})")

            if len(results["missing_in_repo"]) > 10:
                print(
                    f"  ... and {len(results['missing_in_repo']) - 10} more missing files"
                )
            print()

        if results["missing_in_manifest"]:
            print("FILES IN REPOSITORY BUT NOT IN MANIFEST")
            print("-" * 40)
            for item in results["missing_in_manifest"][:10]:
                print(f"  {item['path']}")

            if len(results["missing_in_manifest"]) > 10:
                print(
                    f"  ... and {len(results['missing_in_manifest']) - 10} more unmanifested files"
                )
            print()

        if results["errors"]:
            print("VERIFICATION ERRORS")
            print("-" * 40)
            for item in results["errors"][:5]:
                print(f"  {item['path']}: {item['error']}")

            if len(results["errors"]) > 5:
                print(f"  ... and {len(results['errors']) - 5} more errors")
            print()

        # Recommendations
        print("RECOMMENDATIONS")
        print("-" * 40)

        if total_mismatched > 0:
            print("❌ CRITICAL: Hash mismatches detected!")
            print("   This indicates file corruption or unauthorized modification.")
            print("   Review mismatched files immediately.")

        if total_missing_repo > 0:
            print(
                "⚠️  WARNING: Files referenced in manifest but not found in repository."
            )
            print("   These files may have been deleted or moved.")

        if total_missing_manifest > 0:
            print("📝 NOTE: New files detected that are not in manifest.")
            print(
                "   Consider regenerating the manifest: python automation/generate_sha256_manifest.py"
            )

        if total_verified == total_files and total_mismatched == 0:
            print("[OK] SUCCESS: All files verified successfully.")
            print("   Repository integrity confirmed.")

    def save_results(self, results: Dict[str, List], manifest: Dict) -> Path:
        """Save verification results to file."""
        output_dir = self.repo_root / "logs" / "audit_logs"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"sha256_verification_{timestamp}.json"

        output_data = {
            "metadata": {
                "verification_date": datetime.now().isoformat(),
                "system": "Orthogonal Engineering Phase 8",
                "version": "1.0.0",
                "manifest_source": manifest.get("metadata", {}).get(
                    "source", "unknown"
                ),
            },
            "summary": {
                "verified": len(results["verified"]),
                "mismatched": len(results["mismatched"]),
                "missing_in_repo": len(results["missing_in_repo"]),
                "missing_in_manifest": len(results["missing_in_manifest"]),
                "errors": len(results["errors"]),
                "total_files": len(results["verified"])
                + len(results["mismatched"])
                + len(results["missing_in_manifest"])
                + len(results["errors"]),
            },
            "details": {
                "verified": results["verified"],
                "mismatched": results["mismatched"],
                "missing_in_repo": results["missing_in_repo"],
                "missing_in_manifest": results["missing_in_manifest"],
                "errors": results["errors"],
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"\nVerification results saved to: {output_file.relative_to(self.repo_root)}"
        )
        return output_file

    def run(self, manifest_path: Optional[Path] = None) -> bool:
        """Run the complete SHA256 manifest verification."""
        print("=" * 80)
        print("ORTHOGONAL ENGINEERING - SHA256 MANIFEST VERIFICATION")
        print("=" * 80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Repository: {self.repo_root}")
        print()

        try:
            # Load manifest
            manifest = self.load_manifest(manifest_path)

            # Scan repository
            files = self.scan_repository()
            print(f"Found {len(files)} files in repository")

            # Verify files
            results = self.verify_files(manifest, files)

            # Print results
            self.print_results(results, manifest)

            # Save results
            self.save_results(results, manifest)

            # Return success status
            return len(results["mismatched"]) == 0 and len(results["errors"]) == 0

        except Exception as e:
            print(f"\n❌ Verification failed: {e}", file=sys.stderr)
            return False


def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Verify SHA256 manifest for Orthogonal Engineering repository"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--manifest",
        help="Path to specific manifest file (default: auto-detect latest)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        # Create verifier
        verifier = SHA256ManifestVerifier(args.repo_root)

        # Run verification
        manifest_path = Path(args.manifest) if args.manifest else None
        success = verifier.run(manifest_path)

        if success:
            print("\n[OK] SHA256 manifest verification successful!")
            return 0
        else:
            print("\n[X] SHA256 manifest verification failed!")
            return 1

    except Exception as e:
        print(f"\n❌ Error during SHA256 verification: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
