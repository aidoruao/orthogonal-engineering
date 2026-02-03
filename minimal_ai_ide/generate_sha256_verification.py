#!/usr/bin/env python3
"""
SHA-256 VERIFICATION GENERATOR
==============================

Generates comprehensive SHA-256 hashes for all files in the orthogonal-engineering
repository to verify the integrity of all work done.

This script:
1. Walks through the entire repository
2. Calculates SHA-256 hashes for all files
3. Creates a verification manifest with timestamps
4. Generates a master checksum of all hashes
5. Creates a human-readable verification report

USAGE:
    python generate_sha256_verification.py

OUTPUT:
    - sha256_verification_manifest.json
    - sha256_verification_report.md
    - sha256_master_checksum.txt
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SHA256VerificationGenerator:
    """Generates SHA-256 verification for repository files"""

    def __init__(self, root_dir: Optional[str] = None):
        """Initialize with repository root directory"""
        if root_dir is None:
            # Default to the directory containing this script
            self.root_dir = Path(__file__).parent.parent
        else:
            self.root_dir = Path(root_dir)

        self.exclude_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env",
            "dist",
            "build",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "*.tmp",
            "*.temp",
        ]

        self.verification_data = {
            "metadata": {},
            "files": {},
            "directories": {},
            "statistics": {},
            "master_checksum": "",
        }

        print(f"🔍 SHA-256 Verification Generator")
        print(f"📁 Root directory: {self.root_dir}")
        print(f"⏰ Started at: {datetime.now().isoformat()}")
        print("=" * 70)

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from verification"""
        path_str = str(path)

        # Check for exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                # File extension pattern
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True

        # Check if it's a directory that should be excluded
        if path.is_dir():
            for part in path.parts:
                if part in self.exclude_patterns:
                    return True

        return False

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            return sha256_hash.hexdigest()

        except Exception as e:
            print(f"⚠️  Error calculating hash for {file_path}: {e}")
            return f"ERROR: {str(e)}"

    def get_file_metadata(self, file_path: Path) -> Dict:
        """Get metadata for a file"""
        try:
            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": True,
                "is_dir": False,
            }
        except Exception as e:
            return {
                "size": 0,
                "created": "ERROR",
                "modified": "ERROR",
                "accessed": "ERROR",
                "is_file": True,
                "is_dir": False,
                "error": str(e),
            }

    def get_directory_metadata(self, dir_path: Path) -> Dict:
        """Get metadata for a directory"""
        try:
            stat = dir_path.stat()
            return {
                "size": 0,  # Directories don't have size in traditional sense
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": False,
                "is_dir": True,
                "file_count": sum(1 for _ in dir_path.rglob("*") if _.is_file()),
                "dir_count": sum(1 for _ in dir_path.rglob("*") if _.is_dir()),
            }
        except Exception as e:
            return {
                "size": 0,
                "created": "ERROR",
                "modified": "ERROR",
                "accessed": "ERROR",
                "is_file": False,
                "is_dir": True,
                "error": str(e),
            }

    def scan_repository(self) -> Tuple[int, int]:
        """Scan the repository and collect file/directory information"""
        print("📊 Scanning repository...")

        file_count = 0
        dir_count = 0
        total_size = 0

        # Walk through the repository
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            # Process current directory
            if not self.should_exclude(root_path):
                rel_path = root_path.relative_to(self.root_dir)
                self.verification_data["directories"][str(rel_path)] = (
                    self.get_directory_metadata(root_path)
                )
                dir_count += 1

            # Process files in current directory
            for file in files:
                file_path = root_path / file

                if not self.should_exclude(file_path):
                    rel_path = file_path.relative_to(self.root_dir)

                    # Calculate hash and get metadata
                    file_hash = self.calculate_file_hash(file_path)
                    file_metadata = self.get_file_metadata(file_path)

                    # Store in verification data
                    self.verification_data["files"][str(rel_path)] = {
                        "sha256": file_hash,
                        **file_metadata,
                    }

                    file_count += 1
                    total_size += file_metadata.get("size", 0)

                    # Progress indicator
                    if file_count % 100 == 0:
                        print(f"  Processed {file_count} files...")

        # Update statistics
        self.verification_data["statistics"] = {
            "total_files": file_count,
            "total_directories": dir_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "scan_timestamp": datetime.now().isoformat(),
        }

        print(f"✅ Scan complete: {file_count} files, {dir_count} directories")
        return file_count, dir_count

    def generate_master_checksum(self) -> str:
        """Generate a master SHA-256 checksum of all file hashes"""
        print("🔐 Generating master checksum...")

        # Create a string of all file hashes sorted by filename
        all_hashes = []
        for filename in sorted(self.verification_data["files"].keys()):
            file_data = self.verification_data["files"][filename]
            all_hashes.append(f"{filename}:{file_data['sha256']}")

        # Combine all hashes
        combined = "\n".join(all_hashes)

        # Calculate master hash
        master_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        self.verification_data["master_checksum"] = master_hash

        print(f"✅ Master checksum: {master_hash}")
        return master_hash

    def save_verification_manifest(self) -> Path:
        """Save verification data as JSON manifest"""
        output_file = self.root_dir / "sha256_verification_manifest.json"

        # Add metadata
        self.verification_data["metadata"] = {
            "generator": "generate_sha256_verification.py",
            "generated_at": datetime.now().isoformat(),
            "repository_root": str(self.root_dir),
            "python_version": sys.version,
            "platform": sys.platform,
        }

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.verification_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Verification manifest saved to: {output_file}")
        return output_file

    def generate_verification_report(self) -> Path:
        """Generate a human-readable verification report"""
        output_file = self.root_dir / "sha256_verification_report.md"

        report = f"""# SHA-256 Verification Report

## 📋 Overview

- **Repository**: {self.root_dir.name}
- **Generated**: {datetime.now().isoformat()}
- **Total Files**: {self.verification_data["statistics"]["total_files"]:,}
- **Total Directories**: {self.verification_data["statistics"]["total_directories"]:,}
- **Total Size**: {self.verification_data["statistics"]["total_size_mb"]:.2f} MB
- **Master Checksum**: `{self.verification_data["master_checksum"]}`

## 🔍 Statistics

| Metric | Value |
|--------|-------|
| Files Processed | {self.verification_data["statistics"]["total_files"]:,} |
| Directories Processed | {self.verification_data["statistics"]["total_directories"]:,} |
| Total Size | {self.verification_data["statistics"]["total_size_mb"]:.2f} MB |
| Scan Timestamp | {self.verification_data["statistics"]["scan_timestamp"]} |

## 📁 Key Directories

| Directory | Files | Description |
|-----------|-------|-------------|
"""

        # Add key directories
        key_dirs = [
            ("minimal_ai_ide", "AI IDE System"),
            ("GTAIV", "GTA IV Modding System"),
            ("lora", "LoRA Training System"),
            ("logs", "System Logs"),
            ("analysis", "Analysis Tools"),
        ]

        for dir_name, description in key_dirs:
            dir_path = str(Path(dir_name))
            if dir_path in self.verification_data["directories"]:
                metadata = self.verification_data["directories"][dir_path]
                report += f"| `{dir_name}` | {metadata.get('file_count', 0)} | {description} |\n"

        report += "\n## 📄 Key Files\n\n"

        # Add key files (top 20 by size)
        files_by_size = sorted(
            self.verification_data["files"].items(),
            key=lambda x: x[1].get("size", 0),
            reverse=True,
        )[:20]

        report += "| File | Size | SHA-256 | Modified |\n"
        report += "|------|------|---------|----------|\n"

        for filename, data in files_by_size:
            size_kb = data.get("size", 0) / 1024
            sha256_short = data.get("sha256", "")[:16] + "..."
            modified = data.get("modified", "").split("T")[0]

            report += (
                f"| `{filename}` | {size_kb:.1f} KB | `{sha256_short}` | {modified} |\n"
            )

        report += f"""

## 🔐 Master Checksum Verification

The master checksum is calculated from all individual file hashes:

```
{self.verification_data["master_checksum"]}
```

To verify the integrity of any file:

```python
import hashlib

def verify_file(filepath, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest() == expected_hash
```

## 📊 File Type Distribution

"""

        # Count files by extension
        ext_counts = {}
        for filename in self.verification_data["files"].keys():
            ext = Path(filename).suffix.lower()
            if ext:
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

        report += "| Extension | Count |\n"
        report += "|-----------|-------|\n"

        for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]:
            report += f"| `{ext}` | {count:,} |\n"

        report += f"""

## ⚠️ Excluded Patterns

The following patterns were excluded from verification:

- `.git/*` (Version control)
- `__pycache__/*` (Python cache)
- `node_modules/*` (Node.js dependencies)
- `*.pyc`, `*.pyo`, `*.pyd` (Python compiled files)
- `*.log`, `*.tmp`, `*.temp` (Temporary files)
- System files (`.DS_Store`, `Thumbs.db`)

## 🔗 Related Files

- **Verification Manifest**: `sha256_verification_manifest.json`
- **Master Checksum**: `sha256_master_checksum.txt`
- **This Report**: `sha256_verification_report.md`

---

*Generated by SHA-256 Verification Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        # Save report
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 Verification report saved to: {output_file}")
        return output_file

    def save_master_checksum(self) -> Path:
        """Save master checksum to a separate file"""
        output_file = self.root_dir / "sha256_master_checksum.txt"

        content = f"""MASTER SHA-256 CHECKSUM
=======================

Repository: {self.root_dir.name}
Generated: {datetime.now().isoformat()}
Master Checksum: {self.verification_data["master_checksum"]}

This checksum is calculated from the SHA-256 hashes of all files
in the repository (excluding version control and cache directories).

VERIFICATION:
-------------
To verify the integrity of the repository:

1. Run: python generate_sha256_verification.py
2. Compare the generated master checksum with this one
3. If they match, the repository integrity is verified

FILES INCLUDED:
---------------
Total Files: {self.verification_data["statistics"]["total_files"]:,}
Total Size: {self.verification_data["statistics"]["total_size_mb"]:.2f} MB

CHECKSUM:
---------
{self.verification_data["master_checksum"]}

---
Generated by SHA-256 Verification Generator
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"🔐 Master checksum saved to: {output_file}")
        return output_file

    def run(self) -> Dict:
        """Run the complete verification process"""
        print("🚀 Starting SHA-256 verification process...")
        print("=" * 70)

        # Step 1: Scan repository
        file_count, dir_count = self.scan_repository()

        if file_count == 0:
            print("⚠️  No files found to verify!")
            return {}

        # Step 2: Generate master checksum
        master_checksum = self.generate_master_checksum()

        # Step 3: Save outputs
        manifest_file = self.save_verification_manifest()
        report_file = self.generate_verification_report()
        checksum_file = self.save_master_checksum()

        # Step 4: Summary
        print("=" * 70)
        print("✅ SHA-256 Verification Complete!")
        print(f"📊 Files: {file_count:,}, Directories: {dir_count:,}")
        print(f"🔐 Master Checksum: {master_checksum}")
        print(f"💾 Output Files:")
        print(f"   - {manifest_file.name}")
        print(f"   - {report_file.name}")
        print(f"   - {checksum_file.name}")
        print("=" * 70)

        return {
            "files_processed": file_count,
            "directories_processed": dir_count,
            "master_checksum": master_checksum,
            "output_files": [str(manifest_file), str(report_file), str(checksum_file)],
        }


def main():
    """Main entry point"""
    try:
        # Create generator
        generator = SHA256VerificationGenerator()

        # Run verification
        results = generator.run()

        if results:
            print("🎉 Verification successful!")
            return 0
        else:
            print("❌ Verification failed!")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
