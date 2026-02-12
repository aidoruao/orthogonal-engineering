#!/usr/bin/env python3
"""
partial_log_backup.py — Partial log backup contingency
Simplified version of evidence_store.py for backup operations.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


class PartialLogBackup:
    """Partial log backup implementation for contingency scenarios."""

    def __init__(self):
        self.backup_dir = Path("logs") / "partial_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def backup_logs(self, log_dirs=None):
        """Backup log directories."""
        if log_dirs is None:
            log_dirs = [
                "logs/traces",
                "logs/violations",
                "logs/audit",
                "logs/autofix",
                "logs/spellcheck",
            ]

        print("📦 Running partial log backup...")

        backup_info = {
            "backup_id": f"PARTIAL-BACKUP-{self.backup_timestamp}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "backup_type": "partial_log_backup",
            "directories_backed_up": [],
            "files_backed_up": [],
            "total_size_bytes": 0,
            "status": "in_progress",
        }

        for log_dir in log_dirs:
            dir_path = Path(log_dir)
            if not dir_path.exists():
                print(f"  ⚠ Directory not found: {log_dir}")
                continue

            # Create backup subdirectory
            backup_subdir = (
                self.backup_dir / self.backup_timestamp / log_dir.replace("/", "_")
            )
            backup_subdir.mkdir(parents=True, exist_ok=True)

            print(f"\nBacking up {log_dir}/:")

            # Copy files (limit to recent 10 files per directory)
            try:
                files = list(dir_path.glob("*"))
                files.sort(
                    key=lambda x: x.stat().st_mtime if x.is_file() else 0, reverse=True
                )

                copied_files = 0
                for file_path in files[:10]:  # Limit to 10 most recent files
                    if file_path.is_file():
                        try:
                            target_path = backup_subdir / file_path.name
                            shutil.copy2(file_path, target_path)

                            file_size = file_path.stat().st_size
                            backup_info["total_size_bytes"] += file_size
                            backup_info["files_backed_up"].append(
                                {
                                    "source": str(file_path),
                                    "backup": str(target_path),
                                    "size_bytes": file_size,
                                    "modified": datetime.fromtimestamp(
                                        file_path.stat().st_mtime
                                    ).isoformat(),
                                }
                            )

                            copied_files += 1
                            print(f"  ✓ {file_path.name} ({file_size / 1024:.1f} KB)")

                        except Exception as e:
                            print(f"  ✗ {file_path.name}: {str(e)}")

                if copied_files > 0:
                    backup_info["directories_backed_up"].append(
                        {
                            "directory": log_dir,
                            "files_copied": copied_files,
                            "backup_location": str(backup_subdir),
                        }
                    )
                    print(f"  Copied {copied_files} files from {log_dir}")

            except Exception as e:
                print(f"  ✗ Error backing up {log_dir}: {str(e)}")

        # Save backup manifest
        backup_info["status"] = "complete"
        backup_info["completion_time"] = datetime.utcnow().isoformat() + "Z"

        manifest_file = (
            self.backup_dir
            / self.backup_timestamp
            / f"backup_manifest_{self.backup_timestamp}.json"
        )
        manifest_file.parent.mkdir(parents=True, exist_ok=True)

        with open(manifest_file, "w") as f:
            json.dump(backup_info, f, indent=2)

        return backup_info, manifest_file

    def generate_summary(self, backup_info, manifest_file):
        """Generate backup summary."""
        total_files = len(backup_info["files_backed_up"])
        total_dirs = len(backup_info["directories_backed_up"])
        total_size_mb = backup_info["total_size_bytes"] / (1024 * 1024)

        summary = {
            "summary": {
                "backup_id": backup_info["backup_id"],
                "timestamp": backup_info["timestamp"],
                "total_directories": total_dirs,
                "total_files": total_files,
                "total_size_mb": round(total_size_mb, 2),
                "manifest_file": str(manifest_file),
                "backup_location": str(self.backup_dir / self.backup_timestamp),
                "status": "partial_backup_complete",
            },
            "directories": backup_info["directories_backed_up"],
            "largest_files": sorted(
                backup_info["files_backed_up"],
                key=lambda x: x["size_bytes"],
                reverse=True,
            )[:5],
            "notes": [
                "This is a partial backup for contingency scenarios.",
                "Only recent files were backed up (max 10 per directory).",
                "For full backups, use the evidence_store.py module.",
                "Backup location is preserved for recovery operations.",
            ],
            "recovery_instructions": [
                f"To restore from backup: copy files from {self.backup_dir / self.backup_timestamp}",
                "Check backup manifest for file locations and metadata",
                "Verify file integrity after restoration",
                "Update timestamps if needed for chronological ordering",
            ],
        }

        return summary

    def save_summary(self, summary):
        """Save summary to file."""
        summary_file = (
            self.backup_dir
            / self.backup_timestamp
            / f"backup_summary_{self.backup_timestamp}.json"
        )

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary_file


def main():
    """Main entry point for partial log backup."""
    print("=" * 60)
    print("PARTIAL LOG BACKUP - CONTINGENCY OPERATION")
    print("=" * 60)

    try:
        # Initialize backup
        backup = PartialLogBackup()

        # Run backup
        backup_info, manifest_file = backup.backup_logs()

        # Generate summary
        summary = backup.generate_summary(backup_info, manifest_file)

        # Save summary
        summary_file = backup.save_summary(summary)

        # Print results
        print(f"\n{'=' * 60}")
        print("PARTIAL LOG BACKUP COMPLETE")
        print(f"{'=' * 60}")
        print(f"Backup ID: {summary['summary']['backup_id']}")
        print(f"Directories backed up: {summary['summary']['total_directories']}")
        print(f"Total files backed up: {summary['summary']['total_files']}")
        print(f"Total size: {summary['summary']['total_size_mb']} MB")
        print(f"\nBackup location: {summary['summary']['backup_location']}")
        print(f"Manifest file: {summary['summary']['manifest_file']}")
        print(f"Summary file: {summary_file}")

        if summary["largest_files"]:
            print(f"\nLargest files backed up:")
            for file_info in summary["largest_files"]:
                size_kb = file_info["size_bytes"] / 1024
                print(f"  • {Path(file_info['source']).name}: {size_kb:.1f} KB")

        print(f"\n📦 Backup complete. Files are ready for recovery if needed.")
        print(f"{'=' * 60}")

        return 0

    except Exception as e:
        print(f"\n❌ Backup failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
