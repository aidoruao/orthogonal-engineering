#!/usr/bin/env python3
"""
integrate_claude_analysis.py - Integrate Claude's Analysis Files

Purpose: Copy and integrate the critical analysis files from Claude's conversation
into the Orthogonal Engineering repository as canonical evidence.

Version: 1.0
Schema ID: CLAUDE-INTEGRATION-1.0
Generated: 2026-01-22
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ClaudeAnalysisIntegrator:
    """Integrate Claude's analysis files into the repository"""

    def __init__(self, downloads_path: str, repo_path: str):
        self.downloads = Path(downloads_path)
        self.repo = Path(repo_path)
        self.integration_log = []
        self.timestamp = datetime.utcnow().isoformat()

    def validate_source_files(self) -> Dict:
        """Validate that all required Claude analysis files exist"""
        required_files = {
            "CLAUDE.txt": "Complete Claude conversation about AI state amnesia",
            "ULTIMATE REPOSITORY JESUS CANON 1.txt": "Canonical articulation of established proofs",
            "audit chatgpt 1.txt": "ChatGPT audit and boundary enforcement",
            "Jesus Math Formula Custom 1.txt": "Formal mathematical proof",
        }

        results = {
            "timestamp": self.timestamp,
            "source_validation": {},
            "missing_files": [],
            "all_present": False,
        }

        for filename, description in required_files.items():
            file_path = self.downloads / filename
            if file_path.exists():
                file_size = file_path.stat().st_size
                results["source_validation"][filename] = {
                    "status": "PRESENT",
                    "size_bytes": file_size,
                    "description": description,
                    "path": str(file_path),
                }
                self.integration_log.append(f"✓ Found: {filename} ({file_size} bytes)")
            else:
                results["source_validation"][filename] = {
                    "status": "MISSING",
                    "description": description,
                }
                results["missing_files"].append(filename)
                self.integration_log.append(f"✗ Missing: {filename}")

        results["all_present"] = len(results["missing_files"]) == 0
        return results

    def create_canonical_structure(self) -> Dict:
        """Create canonical directory structure for Claude analysis"""
        canonical_dirs = [
            "canonical_evidence/claude_analysis",
            "canonical_evidence/mathematical_proofs",
            "canonical_evidence/ai_interaction_patterns",
            "canonical_evidence/boundary_enforcement",
            "logs/claude_integration",
        ]

        results = {"directories_created": [], "directories_existing": [], "errors": []}

        for dir_path in canonical_dirs:
            full_path = self.repo / dir_path
            try:
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    results["directories_created"].append(dir_path)
                    self.integration_log.append(f"Created directory: {dir_path}")
                else:
                    results["directories_existing"].append(dir_path)
            except Exception as e:
                results["errors"].append(f"Failed to create {dir_path}: {str(e)}")
                self.integration_log.append(f"Error creating {dir_path}: {str(e)}")

        return results

    def copy_and_annotate_file(
        self, source_filename: str, target_subdir: str, annotation: Dict
    ) -> Dict:
        """Copy a file and add annotation metadata"""
        source_path = self.downloads / source_filename
        target_dir = self.repo / "canonical_evidence" / target_subdir
        target_path = target_dir / source_filename

        # Create metadata filename
        metadata_filename = source_filename.replace(".txt", ".metadata.json")
        metadata_path = target_dir / metadata_filename

        result = {
            "source": str(source_path),
            "target": str(target_path),
            "metadata": str(metadata_path),
            "success": False,
            "error": None,
            "bytes_copied": 0,
        }

        try:
            # Copy the file
            shutil.copy2(source_path, target_path)
            result["bytes_copied"] = target_path.stat().st_size

            # Create metadata
            metadata = {
                "original_filename": source_filename,
                "integration_timestamp": self.timestamp,
                "source_description": annotation.get("description", ""),
                "canonical_category": target_subdir,
                "provenance": "Claude AI Analysis",
                "integration_purpose": annotation.get("purpose", ""),
                "file_hash": self._calculate_file_hash(target_path),
                "size_bytes": result["bytes_copied"],
                "related_files": annotation.get("related_files", []),
                "extracted_insights": annotation.get("insights", []),
            }

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            result["success"] = True
            self.integration_log.append(
                f"Copied and annotated: {source_filename} → {target_subdir}"
            )

        except Exception as e:
            result["error"] = str(e)
            self.integration_log.append(f"Error copying {source_filename}: {str(e)}")

        return result

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file"""
        import hashlib

        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return "hash_calculation_failed"

    def extract_key_insights(self, filepath: Path) -> List[str]:
        """Extract key insights from Claude's analysis files"""
        insights = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for key patterns in Claude's analysis
            patterns = [
                r"AI state amnesia",
                r"phase.*(misclassification|recognition)",
                r"compilation mode",
                r"established.*proofs",
                r"re-derivation.*forbidden",
                r"selective mutism",
                r"boundary violation",
                r"Λ ≡ Jesus",
                r"Logos axiom",
                r"mathematical proof",
            ]

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Extract context around the match
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in list(matches)[:3]:  # Limit to first 3 matches
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end].replace("\n", " ").strip()
                        insights.append(f"{pattern}: ...{context}...")

            # Limit insights to most relevant
            return insights[:10]

        except Exception as e:
            return [f"Error extracting insights: {str(e)}"]

    def integrate_all_files(self) -> Dict:
        """Integrate all Claude analysis files"""
        integration_results = {
            "timestamp": self.timestamp,
            "overall_status": "IN_PROGRESS",
            "files_integrated": {},
            "summary": {},
            "integration_log": self.integration_log,
        }

        # Validate source files
        validation = self.validate_source_files()
        if not validation["all_present"]:
            integration_results["overall_status"] = "FAILED"
            integration_results["error"] = (
                f"Missing files: {validation['missing_files']}"
            )
            return integration_results

        # Create directory structure
        dir_structure = self.create_canonical_structure()
        if dir_structure["errors"]:
            integration_results["overall_status"] = "PARTIAL"

        # Define file annotations
        file_annotations = {
            "CLAUDE.txt": {
                "description": "Complete Claude conversation analyzing AI state amnesia and phase recognition",
                "purpose": "Canonical evidence of AI interaction pattern analysis",
                "target_subdir": "claude_analysis",
                "insights": [
                    "AI state amnesia pattern identification",
                    "Phase misclassification analysis",
                    "Compilation vs evaluation mode distinction",
                    "Selective mutism trigger recognition",
                ],
            },
            "ULTIMATE REPOSITORY JESUS CANON 1.txt": {
                "description": "Canonical articulation of established proofs and phase completion",
                "purpose": "Authoritative statement of system state and closed derivations",
                "target_subdir": "ai_interaction_patterns",
                "insights": [
                    "Interface language vs truth content distinction",
                    "Phase recognition as key unlock",
                    "Post-derivation invariant-locked state",
                    "Translation vs teaching requirement",
                ],
            },
            "audit chatgpt 1.txt": {
                "description": "ChatGPT audit and boundary enforcement implementation",
                "purpose": "Evidence of practical boundary enforcement and AI compliance",
                "target_subdir": "boundary_enforcement",
                "insights": [
                    "Boundary violation detection patterns",
                    "Exit code enforcement strategy",
                    "AI compliance verification",
                    "Practical enforcement implementation",
                ],
            },
            "Jesus Math Formula Custom 1.txt": {
                "description": "Formal mathematical proof of Logos identity theorem",
                "purpose": "Mathematical foundation for system axioms and theorems",
                "target_subdir": "mathematical_proofs",
                "insights": [
                    "Formal Λ ≡ Jesus derivation",
                    "Falsification point specification",
                    "Mathematical proof structure",
                    "Axiomatic foundation establishment",
                ],
            },
        }

        # Copy and annotate each file
        files_integrated = {}
        for filename, annotation in file_annotations.items():
            # Extract insights from the actual file content
            source_path = self.downloads / filename
            if source_path.exists():
                annotation["insights"] = self.extract_key_insights(source_path)

            # Copy and annotate
            result = self.copy_and_annotate_file(
                filename, annotation["target_subdir"], annotation
            )

            files_integrated[filename] = result

            # Add to summary
            if result["success"]:
                integration_results["summary"][filename] = {
                    "status": "INTEGRATED",
                    "size_bytes": result["bytes_copied"],
                    "category": annotation["target_subdir"],
                }
            else:
                integration_results["summary"][filename] = {
                    "status": "FAILED",
                    "error": result["error"],
                }

        integration_results["files_integrated"] = files_integrated

        # Determine overall status
        successful = sum(1 for f in files_integrated.values() if f["success"])
        total = len(files_integrated)

        if successful == total:
            integration_results["overall_status"] = "COMPLETE"
        elif successful > 0:
            integration_results["overall_status"] = "PARTIAL"
        else:
            integration_results["overall_status"] = "FAILED"

        # Create integration report
        self._create_integration_report(integration_results)

        return integration_results

    def _create_integration_report(self, results: Dict):
        """Create a human-readable integration report"""
        report_path = (
            self.repo
            / "logs"
            / "claude_integration"
            / f"integration_report_{self.timestamp[:10]}.md"
        )

        report_content = f"""# Claude Analysis Integration Report

**Timestamp:** {results["timestamp"]}
**Overall Status:** {results["overall_status"]}

## Summary

Integrated {len(results["summary"])} files from Claude's analysis into canonical evidence structure.

## Files Integrated

"""

        for filename, info in results["summary"].items():
            status = info.get("status", "UNKNOWN")
            status_symbol = "✅" if status == "INTEGRATED" else "❌"
            report_content += f"{status_symbol} **{filename}**\n"
            report_content += f"  - Status: {status}\n"
            if "size_bytes" in info:
                report_content += f"  - Size: {info['size_bytes']} bytes\n"
            if "category" in info:
                report_content += f"  - Category: {info['category']}\n"
            if "error" in info:
                report_content += f"  - Error: {info['error']}\n"
            report_content += "\n"

        report_content += "## Integration Log\n\n"
        for log_entry in self.integration_log:
            report_content += f"- {log_entry}\n"

        report_content += f"""

## Next Steps

1. Review integrated files in `canonical_evidence/`
2. Update `STATE.md` to reference new canonical evidence
3. Incorporate insights into `AI_INTERACTION_CONTRACT.md`
4. Run system validation to ensure consistency

## Verification

```bash
# Verify integrated files
find canonical_evidence/ -name "*.metadata.json" | wc -l

# Check file integrity
python scripts/validate_canonical_evidence.py
```

---

*Integration completed by Claude Analysis Integrator v1.0*
"""

        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)

            self.integration_log.append(f"Created integration report: {report_path}")
        except Exception as e:
            self.integration_log.append(f"Failed to create report: {str(e)}")

    def generate_verification_script(self):
        """Generate a verification script for the integrated files"""
        script_path = self.repo / "scripts" / "validate_canonical_evidence.py"

        script_content = '''#!/usr/bin/env python3
"""
validate_canonical_evidence.py - Validate Canonical Evidence Integrity

Purpose: Verify the integrity and consistency of canonical evidence files
integrated from Claude's analysis.

Version: 1.0
"""

import hashlib
import json
import os
from pathlib import Path

def validate_canonical_evidence():
    """Validate all canonical evidence files"""
    repo_root = Path(__file__).parent.parent
    evidence_dir = repo_root / "canonical_evidence"

    if not evidence_dir.exists():
        print("❌ canonical_evidence directory not found")
        return False

    validation_results = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "directories": {},
        "files_validated": 0,
        "errors": []
    }

    # Check each subdirectory
    for subdir in ["claude_analysis", "mathematical_proofs",
                   "ai_interaction_patterns", "boundary_enforcement"]:
        subdir_path = evidence_dir / subdir
        validation_results["directories"][subdir] = {
            "exists": subdir_path.exists(),
            "file_count": 0,
            "metadata_count": 0
        }

        if subdir_path.exists():
            files = list(subdir_path.glob("*"))
            validation_results["directories"][subdir]["file_count"] = len(files)

            # Count metadata files
            metadata_files = list(subdir_path.glob("*.metadata.json"))
            validation_results["directories"][subdir]["metadata_count"] = len(metadata_files)

            # Validate each file has metadata
            for file in files:
                if file.suffix not in [".json", ".metadata.json"]:
                    metadata_file = file.with_name(file.name.replace(file.suffix, ".metadata.json"))
                    if not metadata_file.exists():
                        validation_results["errors"].append(f"Missing metadata for: {file.name}")

    # Generate report
    print("=" * 60)
    print("CANONICAL EVIDENCE VALIDATION REPORT")
    print("=" * 60)

    all_valid = True
    for dir_name, info in validation_results["directories"].items():
        if info["exists"]:
            status = "✅" if info["file_count"] > 0 else "⚠️"
            print(f"{status} {dir_name}: {info['file_count']} files, {info['metadata_count']} metadata")
        else:
            print(f"❌ {dir_name}: Directory missing")
            all_valid = False

    if validation_results["errors"]:
        print("\\n🚨 ERRORS:")
        for error in validation_results["errors"]:
            print(f"  • {error}")
        all_valid = False

    print(f"\\nOverall Status: {'✅ PASS' if all_valid else '❌ FAIL'}")
    return all_valid

if __name__ == "__main__":
    import sys
    success = validate_canonical_evidence()
    sys.exit(0 if success else 1)
'''

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # Make executable
            os.chmod(script_path, 0o755)

            self.integration_log.append(f"Generated verification script: {script_path}")
        except Exception as e:
            self.integration_log.append(
                f"Failed to generate verification script: {str(e)}"
            )


def main():
    parser = argparse.ArgumentParser(description="Integrate Claude's analysis files")
    parser.add_argument(
        "--downloads",
        default="C:\\Users\\Aidor\\Downloads",
        help="Path to Downloads directory (default: C:\\Users\\Aidor\\Downloads)",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to Orthogonal Engineering repository (default: current directory)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify files exist, don't integrate",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    integrator = ClaudeAnalysisIntegrator(args.downloads, args.repo)

    if args.verify_only:
        # Just validate files
        validation = integrator.validate_source_files()
        if args.json:
            print(json.dumps(validation, indent=2))
        else:
            print(f"Files present: {len(validation['source_validation'])}")
            print(f"Missing files: {validation['missing_files']}")
            print(f"All present: {validation['all_present']}")
        sys.exit(0 if validation["all_present"] else 1)

    # Run full integration
    results = integrator.integrate_all_files()

    # Generate verification script
    integrator.generate_verification_script()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Integration Status: {results['overall_status']}")
        print(f"Files Integrated: {len(results['summary'])}")
        print(f"Integration Log: {len(results['integration_log'])} entries")

        # Show summary
        print("\nIntegration Summary:")
        for filename, info in results["summary"].items():
            status = info.get("status", "UNKNOWN")
            symbol = "✅" if status == "INTEGRATED" else "❌"
            print(f"  {symbol} {filename}: {status}")

    # Exit with appropriate code
    if results["overall_status"] == "COMPLETE":
        sys.exit(0)
    elif results["overall_status"] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)
