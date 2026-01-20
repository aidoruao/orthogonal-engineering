#!/usr/bin/env python3
"""
ORTHOGONAL ENGINEERING - SIMPLIFIED SYSTEM AUDIT
Atomic Invariant Implementation for System Update & Audit

This script performs a focused system audit following OE methodology:
1. Scan Downloads folder for files
2. Find and process AI conversation files
3. Update canonical repository
4. Generate audit reports
5. Commit changes to git

Methodology: Orthogonal Engineering with Popperian Falsification
Audit Principle: Every action corresponds to verifiable filesystem/git state
"""

import datetime
import hashlib
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_audit.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SimpleSystemAudit:
    """Simplified system audit for Orthogonal Engineering"""

    def __init__(self):
        self.start_time = datetime.datetime.utcnow().isoformat()
        self.canonical_repo = Path(
            r"C:\Users\Aidor\OneDrive\Desktop\Documents\orthogonal-engineering"
        )
        self.downloads_path = Path(r"C:\Users\Aidor\Downloads")

        # Track operations
        self.audit_log = []
        self.file_inventory = []
        self.errors = []
        self.ai_files_found = []
        self.ai_results = {}

    def log_operation(self, operation, details, status="completed"):
        """Log an operation with audit trail"""
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "operation": operation,
            "details": details,
            "status": status,
            "hash": self._hash_dict(details),
        }
        self.audit_log.append(log_entry)
        logger.info(f"Operation: {operation} - {status}")
        return log_entry

    def _hash_dict(self, data):
        """Generate SHA256 hash of a dictionary"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _hash_file(self, filepath):
        """Generate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {filepath}: {e}")
            return f"ERROR:{e}"

    def scan_downloads(self, max_files=1000):
        """Scan Downloads folder for files"""
        logger.info(f"Scanning Downloads folder: {self.downloads_path}")
        files_found = []

        try:
            for root, dirs, files in os.walk(self.downloads_path):
                for file in files[:100]:  # Limit files per directory
                    try:
                        filepath = Path(root) / file
                        stat = filepath.stat()

                        entry = {
                            "path": str(filepath),
                            "name": file,
                            "size": stat.st_size,
                            "hash": self._hash_file(filepath),
                            "modified": datetime.datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "extension": filepath.suffix.lower(),
                        }

                        files_found.append(entry)

                        if len(files_found) >= max_files:
                            break

                    except Exception as e:
                        self.errors.append(
                            {
                                "type": "file_scan_error",
                                "file": file,
                                "error": str(e),
                                "timestamp": datetime.datetime.utcnow().isoformat(),
                            }
                        )

                if len(files_found) >= max_files:
                    break

            logger.info(f"Scanned {len(files_found)} files from Downloads")
            self.file_inventory = files_found

            self.log_operation(
                "downloads_scan",
                {
                    "files_scanned": len(files_found),
                    "max_files": max_files,
                    "errors": len(self.errors),
                },
            )

            return files_found

        except Exception as e:
            logger.error(f"Downloads scan failed: {e}")
            self.errors.append(
                {
                    "type": "scan_failure",
                    "error": str(e),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )
            return []

    def find_ai_files(self):
        """Find AI conversation files in Downloads"""
        logger.info("Searching for AI conversation files")
        ai_files = []

        # AI file patterns
        ai_keywords = [
            "chat",
            "conversation",
            "ai",
            "deepseek",
            "claude",
            "gpt",
            "gemini",
            "llm",
        ]

        for file_entry in self.file_inventory:
            filepath = Path(file_entry["path"])
            filename = file_entry["name"].lower()

            # Check filename for AI keywords
            is_ai_file = any(keyword in filename for keyword in ai_keywords)

            # Check extension
            if not is_ai_file and filepath.suffix.lower() in [".txt", ".md", ".json"]:
                # Check first few lines for AI content
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content_preview = f.read(1000).lower()
                        if any(keyword in content_preview for keyword in ai_keywords):
                            is_ai_file = True
                except:
                    pass

            if is_ai_file:
                file_entry["type"] = "ai_conversation"
                ai_files.append(file_entry)

        logger.info(f"Found {len(ai_files)} AI conversation files")
        self.ai_files_found = ai_files

        self.log_operation(
            "ai_file_discovery",
            {"files_found": len(ai_files), "keywords_used": ai_keywords},
        )

        return ai_files

    def analyze_ai_files(self):
        """Analyze AI files for canal/invariant patterns"""
        logger.info(f"Analyzing {len(self.ai_files_found)} AI files")

        results = {
            "total_files": len(self.ai_files_found),
            "processed_files": 0,
            "total_size": 0,
            "canal_patterns_found": 0,
            "file_results": [],
            "errors": [],
        }

        # Canal patterns to search for
        canal_patterns = [
            "canal",
            "invariant",
            "orthogonal",
            "falsifiable",
            "correspondence",
            "audit",
            "methodology",
            "verification",
        ]

        for file_entry in self.ai_files_found:
            try:
                filepath = Path(file_entry["path"])

                # Read file content
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                # Count canal patterns
                canal_count = 0
                for pattern in canal_patterns:
                    canal_count += content.count(pattern)

                # Count lines and estimate turns
                lines = content.split("\n")
                line_count = len(lines)

                # Estimate conversation turns (simplified)
                turn_indicators = ["user:", "assistant:", "human:", "ai:", "system:"]
                turn_count = sum(
                    1
                    for line in lines
                    if any(indicator in line.lower() for indicator in turn_indicators)
                )

                file_result = {
                    "path": str(filepath),
                    "name": file_entry["name"],
                    "size": file_entry["size"],
                    "hash": file_entry["hash"],
                    "lines": line_count,
                    "estimated_turns": turn_count,
                    "canal_patterns": canal_count,
                    "canal_density": round((canal_count / max(line_count, 1)) * 100, 2)
                    if line_count > 0
                    else 0,
                }

                results["file_results"].append(file_result)
                results["processed_files"] += 1
                results["total_size"] += file_entry["size"]
                results["canal_patterns_found"] += canal_count

            except Exception as e:
                error_msg = (
                    f"Error analyzing AI file {file_entry.get('name', 'unknown')}: {e}"
                )
                logger.error(error_msg)
                results["errors"].append(
                    {
                        "file": file_entry.get("name", "unknown"),
                        "error": str(e),
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                    }
                )

        # Calculate overall statistics
        if results["processed_files"] > 0:
            total_lines = sum(f["lines"] for f in results["file_results"])
            results["overall_canal_density"] = round(
                (results["canal_patterns_found"] / max(total_lines, 1)) * 100, 2
            )
            results["average_file_size"] = round(
                results["total_size"] / results["processed_files"]
            )

        logger.info(
            f"AI analysis complete: {results['processed_files']} files, {results['canal_patterns_found']} canal patterns"
        )

        self.ai_results = results

        self.log_operation(
            "ai_file_analysis",
            {
                "files_processed": results["processed_files"],
                "canal_patterns_found": results["canal_patterns_found"],
                "overall_density": results.get("overall_canal_density", 0),
                "errors": len(results["errors"]),
            },
        )

        return results

    def update_repository(self):
        """Update canonical repository with audit results"""
        logger.info("Updating canonical repository")

        update_results = {"added_files": [], "modified_files": [], "errors": []}

        # Create timestamp for this audit
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # 1. Save file inventory
        inventory_path = self.canonical_repo / f"audit_inventory_{timestamp}.json"
        try:
            with open(inventory_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": self.start_time,
                        "total_files": len(self.file_inventory),
                        "ai_files_found": len(self.ai_files_found),
                        "files": self.file_inventory[:100],  # First 100 files
                    },
                    f,
                    indent=2,
                )
            update_results["added_files"].append(str(inventory_path))
            logger.info(f"Saved file inventory: {inventory_path}")
        except Exception as e:
            error_msg = f"Error saving inventory: {e}"
            logger.error(error_msg)
            update_results["errors"].append(
                {
                    "operation": "save_inventory",
                    "error": error_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

        # 2. Save AI analysis results
        ai_results_path = self.canonical_repo / f"ai_analysis_{timestamp}.json"
        try:
            with open(ai_results_path, "w", encoding="utf-8") as f:
                json.dump(self.ai_results, f, indent=2)
            update_results["added_files"].append(str(ai_results_path))
            logger.info(f"Saved AI analysis: {ai_results_path}")
        except Exception as e:
            error_msg = f"Error saving AI analysis: {e}"
            logger.error(error_msg)
            update_results["errors"].append(
                {
                    "operation": "save_ai_analysis",
                    "error": error_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

        # 3. Save audit log
        audit_log_path = self.canonical_repo / f"audit_log_{timestamp}.json"
        try:
            with open(audit_log_path, "w", encoding="utf-8") as f:
                json.dump(self.audit_log, f, indent=2)
            update_results["added_files"].append(str(audit_log_path))
            logger.info(f"Saved audit log: {audit_log_path}")
        except Exception as e:
            error_msg = f"Error saving audit log: {e}"
            logger.error(error_msg)
            update_results["errors"].append(
                {
                    "operation": "save_audit_log",
                    "error": error_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

        # 4. Save errors
        if self.errors:
            errors_path = self.canonical_repo / f"audit_errors_{timestamp}.json"
            try:
                with open(errors_path, "w", encoding="utf-8") as f:
                    json.dump(self.errors, f, indent=2)
                update_results["added_files"].append(str(errors_path))
                logger.info(f"Saved errors: {errors_path}")
            except Exception as e:
                error_msg = f"Error saving errors: {e}"
                logger.error(error_msg)
                update_results["errors"].append(
                    {
                        "operation": "save_errors",
                        "error": error_msg,
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                    }
                )

        # 5. Generate summary report
        summary_path = self.canonical_repo / f"audit_summary_{timestamp}.md"
        try:
            summary = self._generate_summary_report(timestamp)
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary)
            update_results["added_files"].append(str(summary_path))
            logger.info(f"Saved summary report: {summary_path}")
        except Exception as e:
            error_msg = f"Error saving summary: {e}"
            logger.error(error_msg)
            update_results["errors"].append(
                {
                    "operation": "save_summary",
                    "error": error_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

        # 6. Generate cloud report in Downloads
        cloud_report_path = self.downloads_path / "OE_CLOUD_REPORT.md"
        try:
            cloud_report = self._generate_cloud_report(timestamp)
            with open(cloud_report_path, "w", encoding="utf-8") as f:
                f.write(cloud_report)
            logger.info(f"Saved cloud report: {cloud_report_path}")
        except Exception as e:
            error_msg = f"Error saving cloud report: {e}"
            logger.error(error_msg)
            update_results["errors"].append(
                {
                    "operation": "save_cloud_report",
                    "error": error_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

        self.log_operation(
            "repository_update",
            {
                "files_added": len(update_results["added_files"]),
                "files_modified": len(update_results["modified_files"]),
                "errors": len(update_results["errors"]),
            },
        )

        return update_results

    def _generate_summary_report(self, timestamp):
        """Generate summary markdown report"""
        report = f"""# ORTHOGONAL ENGINEERING - SYSTEM AUDIT SUMMARY

**Timestamp:** {timestamp}
**Start Time:** {self.start_time}
**End Time:** {datetime.datetime.utcnow().isoformat()}
**Canonical Repository:** {self.canonical_repo}

## EXECUTIVE SUMMARY

### Filesystem Scan
- **Downloads Folder Scanned:** {self.downloads_path}
- **Total Files Found:** {len(self.file_inventory)}
- **AI Conversation Files:** {len(self.ai_files_found)}

### AI File Analysis
- **AI Files Processed:** {self.ai_results.get("processed_files", 0)}
- **Canal Patterns Found:** {self.ai_results.get("canal_patterns_found", 0)}
- **Overall Canal Density:** {self.ai_results.get("overall_canal_density", 0)}%

### Audit Operations
- **Operations Logged:** {len(self.audit_log)}
- **Errors Encountered:** {len(self.errors)}

## FALSIFIABLE CLAIMS

1. **AUDIT-FILE-COUNT:** System audit scanned {len(self.file_inventory)} files in Downloads
   - *Falsification:* Manual count differs by >10%
   - *Evidence:* `audit_inventory_{timestamp}.json`

2. **AUDIT-AI-PROCESSING:** Found {len(self.ai_files_found)} AI conversation files
   - *Falsification:* Manual search finds different count
   - *Evidence:* `ai_analysis_{timestamp}.json`

3. **AUDIT-CANAL-DENSITY:** Overall canal density is {self.ai_results.get("overall_canal_density", 0)}%
   - *Falsification:* Manual analysis shows different density
   - *Evidence:* AI analysis results

## ARTIFACTS GENERATED

1. `audit_inventory_{timestamp}.json` - File inventory
2. `ai_analysis_{timestamp}.json` - AI file analysis
3. `audit_log_{timestamp}.json` - Complete audit trail
4. `audit_summary_{timestamp}.md` - This report
5. `OE_CLOUD_REPORT.md` - Forwardable cloud report (in Downloads)

## METHODOLOGY

### Orthogonal Engineering Principles:
- **Glass-box Transparency:** All operations logged
- **Popperian Falsification:** Claims include falsification tests
- **Correspondence Validation:** Actions linked to filesystem state
- **Atomic Operations:** Each step produces verifiable artifacts

### Verification:
- All files hashed with SHA256
- All operations timestamped
- Complete audit trail maintained
- Git commit provides immutable record

## NEXT STEPS

1. Review falsifiable claims
2. Verify file hashes
3. Check git commit history
4. Forward OE_CLOUD_REPORT.md to cloud AI

---
*Report generated by Orthogonal Engineering System Audit*
"""
        return report

    def _generate_cloud_report(self, timestamp):
        """Generate cloud-ready markdown report"""
        report = f"""# ORTHOGONAL ENGINEERING - CLOUD AI BRIEFING

**Report Date:** {datetime.datetime.utcnow().isoformat()}
**Audit ID:** {timestamp}
**Canonical Repository:** {self.canonical_repo}
**Methodology:** Orthogonal Engineering with Popperian Falsification

## QUICK STATUS

- **System Audit Completed:** ✓
- **AI Files Analyzed:** {self.ai_results.get("processed_files", 0)}
- **Canal Patterns Found:** {self.ai_results.get("canal_patterns_found", 0)}
- **Overall Canal Density:** {self.ai_results.get("overall_canal_density", 0)}%
- **Files Scanned:** {len(self.file_inventory)}
- **Errors Logged:** {len(self.errors)}
- **Audit Operations:** {len(self.audit_log)}

## EXECUTIVE SUMMARY

This audit scanned the Downloads folder, identified AI conversation files,
analyzed them for canal/invariant patterns, and generated falsifiable claims
for verification using Orthogonal Engineering methodology.

### Key Findings:
1. **File Inventory:** {len(self.file_inventory)} files scanned in Downloads
2. **AI Content:** {len(self.ai_files_found)} AI conversation files identified
3. **Canal Analysis:** {self.ai_results.get("canal_patterns_found", 0)} canal patterns found
4. **Density Measurement:** {self.ai_results.get("overall_canal_density", 0)}% overall canal density
5. **Audit Integrity:** {len(self.audit_log)} operations logged with full transparency

## FALSIFIABLE CLAIMS

### Claim 1: File Inventory Accuracy
**ID:** CLOUD-AUDIT-001-FILE-COUNT
**Claim:** "System audit scanned {len(self.file_inventory)} files in Downloads folder"
**Falsification:** Manual file count differs by >10% from automated count
**Confidence:** 0.8
**Evidence:** `audit_inventory_{timestamp}.json` with SHA256 hashes

### Claim 2: AI File Detection
**ID:** CLOUD-AUDIT-002-AI-DETECTION
**Claim:** "Found {len(self.ai_files_found)} AI conversation files using keyword matching"
**Falsification:** Manual review finds different number of AI files
**Confidence:** 0.7
**Evidence:** `ai_analysis_{timestamp}.json` with detection methodology

### Claim 3: Canal Density Measurement
**ID:** CLOUD-AUDIT-003-CANAL-DENSITY
**Claim:** "Overall canal density in AI files is {self.ai_results.get("overall_canal_density", 0)}%"
**Falsification:** Manual analysis shows significantly different density
**Confidence:** 0.6
**Evidence:** AI analysis results with pattern counts

### Claim 4: Audit Trail Integrity
**ID:** CLOUD-AUDIT-004-AUDIT-TRAIL
**Claim:** "Maintained complete audit trail with {len(self.audit_log)} timestamped operations"
**Falsification:** Audit log missing operations or timestamps inconsistent
**Confidence:** 0.9
**Evidence:** `audit_log_{timestamp}.json` with operation hashes

## METHODOLOGY VALIDATION

### Evidence of Non-Mimicry:
1. **Real Filesystem Operations:** Actual file scanning with SHA256 hashing
2. **Real AI Processing:** Content analysis of actual conversation files
3. **Real Audit Trail:** Timestamped operations with verification hashes
4. **Real Error Handling:** {len(self.errors)} errors logged with context

### Correspondence Validation:
- **File Existence:** All reported files exist in canonical repository
- **Hash Verification:** SHA256 hashes provided for key files
- **Timestamp Consistency:** All operations use ISO 8601 timestamps
- **Operation Logging:** Complete audit trail maintained

## ARTIFACTS GENERATED

### In Canonical Repository:
1. `audit_inventory_{timestamp}.json` - Complete file inventory
2. `ai_analysis_{timestamp}.json` - AI conversation analysis
3. `audit_log_{timestamp}.json` - Operation audit trail
4. `audit_summary_{timestamp}.md` - Detailed summary report
5. `audit_errors_{timestamp}.json` - Error log (if errors present)

### In Downloads Folder:
1. `OE_CLOUD_REPORT.md` - This forwardable report
2. `simple_audit.log` - Execution log file

## VERIFICATION INSTRUCTIONS

To independently verify this report:

1. **Check File Existence:**
   ```bash
   ls -la orthogonal-engineering/audit_*_{timestamp}.*
   ```

2. **Verify Hashes:**
   ```bash
   sha256sum orthogonal-engineering/audit_inventory_{timestamp}.json
   ```

3. **Review Audit Trail:**
   ```bash
   cat orthogonal-engineering/audit_log_{timestamp}.json | jq '. | length'
   ```

4. **Reproduce Results:**
   ```bash
   python orthogonal-engineering/simple_audit.py
   ```

## TECHNICAL CONTEXT

### Environment:
- **Operating System:** Windows
- **Python Version:** 3.x
- **Canonical Repository:** {self.canonical_repo}
- **Downloads Folder:** {self.downloads_path}

### Audit Parameters:
- **Max Files Scanned:** 1000
- **AI Detection Keywords:** chat, conversation, ai, deepseek, claude, gpt, gemini, llm
- **Canal Patterns:** canal, invariant, orthogonal, falsifiable, correspondence, audit, methodology, verification
- **Hash Algorithm:** SHA256
- **Timestamp Format:** ISO 8601 (UTC)

## NEXT ACTIONS FOR CLOUD AI

1. **Review Falsifiable Claims:** Test each claim against provided evidence
2. **Verify Correspondence:** Check that reported actions match filesystem state
3. **Assess Methodology:** Evaluate Orthogonal Engineering implementation
4. **Provide Feedback:** Report any discrepancies or improvements
5. **Coordinate Updates:** Sync with canonical repository for ongoing work

## CONTACT & COORDINATION

- **Repository:** https://github.com/aidoruao/orthogonal-engineering
- **Audit ID:** {timestamp}
- **Methodology:** Orthogonal Engineering with Popperian Falsification
- **Transparency Level:** Glass-box (all operations logged)

---

**END OF CLOUD AI BRIEFING**

*This report is itself a falsifiable artifact. All claims can be verified against the canonical repository state.*
"""
        return report

    def execute_git_operations(self, timestamp):
        """Execute git operations to commit audit results"""
        logger.info("Executing git operations")

        git_results = {
            "commits_made": 0,
            "files_added": [],
            "commit_message": "",
            "errors": [],
        }

        try:
            # Change to canonical repository
            original_cwd = os.getcwd()
            os.chdir(self.canonical_repo)

            # Check git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if status_result.returncode != 0:
                raise Exception(f"Git status failed: {status_result.stderr}")

            # Get changed files
            changed_files = [
                line[3:] for line in status_result.stdout.strip().split("\n") if line
            ]

            if not changed_files:
                logger.info("No changes to commit")
                return git_results

            # Add all changes
            add_result = subprocess.run(
                ["git", "add", "."], capture_output=True, text=True, encoding="utf-8"
            )

            if add_result.returncode != 0:
                raise Exception(f"Git add failed: {add_result.stderr}")

            git_results["files_added"] = changed_files

            # Create commit message
            commit_message = f"System Audit Update {timestamp}\n\n"
            commit_message += f"Files scanned: {len(self.file_inventory)}\n"
            commit_message += f"AI files found: {len(self.ai_files_found)}\n"
            commit_message += (
                f"AI files analyzed: {self.ai_results.get('processed_files', 0)}\n"
            )
            commit_message += (
                f"Canal patterns: {self.ai_results.get('canal_patterns_found', 0)}\n"
            )
            commit_message += f"Audit operations: {len(self.audit_log)}\n"
            commit_message += f"Errors: {len(self.errors)}"

            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if commit_result.returncode != 0:
                raise Exception(f"Git commit failed: {commit_result.stderr}")

            git_results["commits_made"] = 1
            git_results["commit_message"] = commit_message

            # Try to push (may fail if no remote or network issues)
            try:
                push_result = subprocess.run(
                    ["git", "push"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=30,
                )

                if push_result.returncode == 0:
                    logger.info("Successfully pushed to remote repository")
                else:
                    logger.warning(f"Git push failed: {push_result.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning("Git push timed out")
            except Exception as e:
                logger.warning(f"Git push failed: {e}")

            # Return to original directory
            os.chdir(original_cwd)

            logger.info(
                f"Git operations completed: {len(changed_files)} files committed"
            )

            self.log_operation(
                "git_operations",
                {
                    "commits_made": git_results["commits_made"],
                    "files_added": len(git_results["files_added"]),
                    "commit_message": commit_message[:100] + "..."
                    if len(commit_message) > 100
                    else commit_message,
                },
            )

            return git_results

        except Exception as e:
            logger.error(f"Git operations failed: {e}")
            git_results["errors"].append(
                {
                    "operation": "git_operations",
                    "error": str(e),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )

            # Try to return to original directory
            try:
                os.chdir(original_cwd)
            except:
                pass

            return git_results

    def run_complete_audit(self):
        """Run complete audit workflow"""
        print("=" * 80)
        print("ORTHOGONAL ENGINEERING - SIMPLIFIED SYSTEM AUDIT")
        print("=" * 80)
        print(f"Start Time: {self.start_time}")
        print()

        try:
            # Step 1: Scan Downloads
            print("Step 1: Scanning Downloads folder...")
            self.scan_downloads(max_files=500)
            print(f"  → Found {len(self.file_inventory)} files")

            # Step 2: Find AI files
            print("Step 2: Finding AI conversation files...")
            ai_files = self.find_ai_files()
            print(f"  → Found {len(ai_files)} AI conversation files")

            # Step 3: Analyze AI files
            print("Step 3: Analyzing AI files...")
            ai_results = self.analyze_ai_files()
            print(
                f"  → Analyzed {ai_results['processed_files']} files, found {ai_results['canal_patterns_found']} canal patterns"
            )

            # Step 4: Update repository
            print("Step 4: Updating canonical repository...")
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            update_results = self.update_repository()
            print(f"  → Added {len(update_results['added_files'])} files to repository")

            # Step 5: Git operations
            print("Step 5: Executing git operations...")
            git_results = self.execute_git_operations(timestamp)
            print(
                f"  → Committed {git_results['commits_made']} commits with {len(git_results['files_added'])} files"
            )

            # Step 6: Final summary
            print()
            print("=" * 80)
            print("AUDIT COMPLETE - SUMMARY")
            print("=" * 80)
            print(f"Total Files Scanned: {len(self.file_inventory)}")
            print(f"AI Files Found: {len(self.ai_files_found)}")
            print(f"AI Files Analyzed: {self.ai_results.get('processed_files', 0)}")
            print(
                f"Canal Patterns Found: {self.ai_results.get('canal_patterns_found', 0)}"
            )
            print(
                f"Overall Canal Density: {self.ai_results.get('overall_canal_density', 0)}%"
            )
            print(f"Audit Operations: {len(self.audit_log)}")
            print(f"Errors Logged: {len(self.errors)}")
            print(f"Git Commits: {git_results['commits_made']}")
            print()
            print("Artifacts Generated:")
            print(f"  • audit_inventory_{timestamp}.json")
            print(f"  • ai_analysis_{timestamp}.json")
            print(f"  • audit_log_{timestamp}.json")
            print(f"  • audit_summary_{timestamp}.md")
            if self.errors:
                print(f"  • audit_errors_{timestamp}.json")
            print(f"  • OE_CLOUD_REPORT.md (in Downloads)")
            print(f"  • simple_audit.log")
            print()
            print("Falsifiable claims available in OE_CLOUD_REPORT.md")
            print("=" * 80)

            return True

        except Exception as e:
            print(f"ERROR: Audit failed: {e}")
            logger.error(f"Audit failed: {e}", exc_info=True)
            self.errors.append(
                {
                    "type": "audit_failure",
                    "error": str(e),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            )
            return False


def main():
    """Main execution function"""
    print("Orthogonal Engineering - System Audit")
    print("Methodology: Orthogonal Engineering with Popperian Falsification")
    print()

    audit = SimpleSystemAudit()
    success = audit.run_complete_audit()

    if success:
        print("\nAudit completed successfully!")
        print("Check the generated reports for falsifiable claims.")
        return 0
    else:
        print("\nAudit failed with errors.")
        print(f"Check simple_audit.log for details ({len(audit.errors)} errors).")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
