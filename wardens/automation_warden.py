#!/usr/bin/env python3
"""
Automation Warden for the Local AI Warden System - Phase 2

This warden is responsible for monitoring and managing the automation/ folder.
Model: llama3.2:3b
Capabilities: code_analysis, boundary_enforcement, trace_generation
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutomationWarden:
    """Warden for the automation/ folder."""

    def __init__(self, folder_path: str = "automation"):
        """
        Initialize the Automation Warden.

        Args:
            folder_path: Path to the automation folder (relative to project root)
        """
        self.folder_path = folder_path
        self.status = "pending"  # pending, active, error, disabled
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "code_analysis",
                "boundary_enforcement",
                "trace_generation",
            ],
            "model_name": "llama3.2:3b",
            "api_key": "local_ollama",
        }
        self.health = {
            "last_query": None,
            "response_time_ms": 0,
            "success_rate": 1.0,
            "last_health_check": None,
            "total_queries": 0,
            "successful_queries": 0,
        }
        self.initialized = False
        self.error_message = None

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the warden by scanning the folder and generating metadata.

        Returns:
            Dictionary with initialization results
        """
        start_time = time.time()

        try:
            # Check if folder exists
            if not os.path.exists(self.folder_path):
                self.status = "error"
                self.error_message = f"Folder not found: {self.folder_path}"
                logger.error(self.error_message)
                return {
                    "success": False,
                    "error": self.error_message,
                    "status": self.status,
                }

            # Count files
            file_count = self._count_files()
            self.metadata["file_count"] = file_count

            # Generate hash manifest
            hash_manifest = self._generate_hash_manifest()
            self.metadata["last_hash_manifest"] = hash_manifest

            # Update status
            self.status = "active"
            self.initialized = True
            self.error_message = None

            initialization_time = time.time() - start_time

            logger.info(
                f"Automation Warden initialized successfully. Found {file_count} files."
            )

            return {
                "success": True,
                "file_count": file_count,
                "hash_manifest": hash_manifest,
                "initialization_time_seconds": initialization_time,
                "status": self.status,
            }

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            logger.error(f"Failed to initialize Automation Warden: {e}")
            return {"success": False, "error": str(e), "status": self.status}

    def query(
        self, task: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle BASE AI requests for the automation folder.

        Args:
            task: The task to perform
            parameters: Optional parameters for the task

        Returns:
            Dictionary with query results
        """
        query_start = time.time()
        self.health["total_queries"] += 1

        try:
            # Ensure warden is initialized
            if not self.initialized:
                init_result = self.initialize()
                if not init_result["success"]:
                    return {
                        "success": False,
                        "error": f"Warden not initialized: {init_result.get('error', 'Unknown error')}",
                        "task": task,
                    }

            # Handle different task types
            result = self._handle_task(task, parameters or {})

            # Update health metrics
            query_time = (time.time() - query_start) * 1000  # Convert to ms
            self.health["last_query"] = datetime.now().isoformat()
            self.health["response_time_ms"] = query_time
            self.health["successful_queries"] += 1
            self.health["success_rate"] = (
                self.health["successful_queries"] / self.health["total_queries"]
            )

            result["query_time_ms"] = query_time
            result["success"] = True

            logger.info(f"Query '{task}' completed in {query_time:.2f}ms")

            return result

        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            logger.error(f"Query '{task}' failed: {e}")

            # Update health metrics for failure
            query_time = (time.time() - query_start) * 1000
            self.health["response_time_ms"] = query_time
            self.health["success_rate"] = (
                self.health["successful_queries"] / self.health["total_queries"]
            )

            return {
                "success": False,
                "error": error_msg,
                "task": task,
                "query_time_ms": query_time,
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check and report status.

        Returns:
            Dictionary with health check results
        """
        check_start = time.time()

        try:
            # Basic health checks
            folder_exists = os.path.exists(self.folder_path)
            can_read = os.access(self.folder_path, os.R_OK) if folder_exists else False

            # Check file count consistency
            current_file_count = self._count_files() if folder_exists else 0
            metadata_file_count = self.metadata.get("file_count", 0)

            # Update health
            self.health["last_health_check"] = datetime.now().isoformat()

            health_status = {
                "status": self.status,
                "folder_exists": folder_exists,
                "folder_readable": can_read,
                "initialized": self.initialized,
                "file_count": {
                    "current": current_file_count,
                    "metadata": metadata_file_count,
                    "consistent": current_file_count == metadata_file_count,
                },
                "health_metrics": self.health.copy(),
                "error_message": self.error_message,
                "check_time_seconds": time.time() - check_start,
            }

            # Determine overall health status
            if not folder_exists or not can_read:
                health_status["overall_health"] = "critical"
            elif self.status != "active":
                health_status["overall_health"] = "warning"
            else:
                health_status["overall_health"] = "healthy"

            logger.info(f"Health check completed: {health_status['overall_health']}")

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_health": "error",
                "check_time_seconds": time.time() - check_start,
            }

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return folder information and warden metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "warden_type": "automation_warden",
            "folder_path": self.folder_path,
            "status": self.status,
            "metadata": self.metadata.copy(),
            "health": self.health.copy(),
            "initialized": self.initialized,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def _count_files(self) -> int:
        """Count files recursively in the automation folder."""
        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            count += len(files)
        return count

    def _generate_hash_manifest(self) -> Dict[str, str]:
        """
        Generate SHA256 hash manifest for files in the automation folder.

        Returns:
            Dictionary mapping file paths to SHA256 hashes
        """
        hash_manifest = {}

        for root, dirs, files in os.walk(self.folder_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()

                    # Store relative path
                    rel_path = os.path.relpath(file_path, self.folder_path)
                    hash_manifest[rel_path] = file_hash

                except Exception as e:
                    logger.warning(f"Could not hash file {file_path}: {e}")

        return hash_manifest

    def _handle_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle specific tasks for the automation folder.

        Args:
            task: The task to perform
            parameters: Task parameters

        Returns:
            Task results
        """
        task = task.lower()

        if task == "scan":
            # Perform a fresh scan
            file_count = self._count_files()
            hash_manifest = self._generate_hash_manifest()

            self.metadata["file_count"] = file_count
            self.metadata["last_hash_manifest"] = hash_manifest

            return {
                "task": "scan",
                "file_count": file_count,
                "hash_manifest_size": len(hash_manifest),
                "message": f"Scanned {file_count} files",
            }

        elif task == "analyze_code":
            # Analyze Python code in the automation folder
            python_files = self._find_python_files()
            analysis = self._analyze_python_files(python_files)

            return {
                "task": "analyze_code",
                "python_file_count": len(python_files),
                "analysis": analysis,
                "message": f"Analyzed {len(python_files)} Python files",
            }

        elif task == "check_boundary":
            # Check for boundary violations in automation scripts
            violations = self._check_boundary_violations()

            return {
                "task": "check_boundary",
                "violation_count": len(violations),
                "violations": violations,
                "message": f"Found {len(violations)} potential boundary violations",
            }

        elif task == "get_file_list":
            # Get list of files in the automation folder
            files = self._get_file_list()

            return {
                "task": "get_file_list",
                "file_count": len(files),
                "files": files[:50],  # Limit to first 50 files
                "truncated": len(files) > 50,
            }

        elif task == "verify_hash":
            # Verify current hashes against stored manifest
            if "expected_hashes" in parameters:
                verification = self._verify_hashes(parameters["expected_hashes"])
                return {
                    "task": "verify_hash",
                    "verified": verification["verified"],
                    "mismatches": verification["mismatches"],
                    "message": verification["message"],
                }
            else:
                current_hashes = self._generate_hash_manifest()
                stored_hashes = self.metadata.get("last_hash_manifest", {})
                verification = self._compare_hashes(current_hashes, stored_hashes)

                return {
                    "task": "verify_hash",
                    "verified": verification["verified"],
                    "mismatches": verification["mismatches"],
                    "message": verification["message"],
                }

        else:
            # Default task handler
            return {
                "task": task,
                "message": f"Task '{task}' received but not specifically implemented",
                "parameters": parameters,
                "suggestion": "Available tasks: scan, analyze_code, check_boundary, get_file_list, verify_hash",
            }

    def _find_python_files(self) -> List[str]:
        """Find all Python files in the automation folder."""
        python_files = []
        for root, dirs, files in os.walk(self.folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _analyze_python_files(self, python_files: List[str]) -> Dict[str, Any]:
        """Perform basic analysis on Python files."""
        analysis = {
            "total_files": len(python_files),
            "files_by_size": {},
            "import_analysis": {},
            "function_count": 0,
            "class_count": 0,
        }

        for file_path in python_files[:10]:  # Limit analysis to first 10 files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Basic metrics
                file_size = os.path.getsize(file_path)
                analysis["files_by_size"][os.path.basename(file_path)] = file_size

                # Count functions and classes (simple regex-based)
                import re

                function_matches = re.findall(r"def\s+\w+", content)
                class_matches = re.findall(r"class\s+\w+", content)

                analysis["function_count"] += len(function_matches)
                analysis["class_count"] += len(class_matches)

                # Analyze imports
                import_lines = [
                    line
                    for line in content.split("\n")
                    if line.strip().startswith("import")
                    or line.strip().startswith("from")
                ]
                for imp in import_lines[:5]:  # Limit to first 5 imports per file
                    analysis["import_analysis"].setdefault(
                        os.path.basename(file_path), []
                    ).append(imp.strip())

            except Exception as e:
                logger.warning(f"Could not analyze file {file_path}: {e}")

        return analysis

    def _check_boundary_violations(self) -> List[Dict[str, Any]]:
        """Check for potential boundary violations in automation scripts."""
        violations = []
        python_files = self._find_python_files()

        # Common boundary violation patterns
        violation_patterns = {
            "broad_exception": r"except\s*(Exception|BaseException|):",
            "warning_suppression": r'warnings\.filterwarnings\("ignore"\)',
            "direct_file_io": r"open\([^)]*\)[^)]*(write|read)",
            "missing_validation": r"def\s+\w+\([^)]*\):[^:]*\n\s*(?!.*#.*validation)",
        }

        for file_path in python_files[:5]:  # Check first 5 files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines):
                    line_num = i + 1
                    for pattern_name, pattern in violation_patterns.items():
                        import re

                        if re.search(pattern, line):
                            violations.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "line": line_num,
                                    "pattern": pattern_name,
                                    "code": line.strip(),
                                    "severity": "warning",
                                }
                            )

            except Exception as e:
                logger.warning(
                    f"Could not check boundary violations in {file_path}: {e}"
                )

        return violations

    def _get_file_list(self) -> List[Dict[str, Any]]:
        """Get detailed list of files in the automation folder."""
        files = []
        for root, dirs, file_names in os.walk(self.folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                try:
                    stat = os.stat(file_path)
                    files.append(
                        {
                            "name": file_name,
                            "path": os.path.relpath(file_path, self.folder_path),
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "type": "python" if file_name.endswith(".py") else "other",
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not stat file {file_path}: {e}")

        return files

    def _verify_hashes(self, expected_hashes: Dict[str, str]) -> Dict[str, Any]:
        """Verify current file hashes against expected hashes."""
        current_hashes = self._generate_hash_manifest()
        return self._compare_hashes(current_hashes, expected_hashes)

    def _compare_hashes(
        self, current: Dict[str, str], expected: Dict[str, str]
    ) -> Dict[str, Any]:
        """Compare two hash dictionaries."""
        mismatches = []

        # Check for missing files
        for file_path in expected:
            if file_path not in current:
                mismatches.append(
                    {
                        "file": file_path,
                        "issue": "missing",
                        "expected_hash": expected[file_path],
                        "current_hash": None,
                    }
                )

        # Check for hash mismatches
        for file_path in current:
            if file_path in expected:
                if current[file_path] != expected[file_path]:
                    mismatches.append(
                        {
                            "file": file_path,
                            "issue": "hash_mismatch",
                            "expected_hash": expected[file_path],
                            "current_hash": current[file_path],
                        }
                    )

        verified = len(mismatches) == 0

        return {
            "verified": verified,
            "mismatches": mismatches,
            "message": f"Hash verification {'passed' if verified else 'failed'} with {len(mismatches)} mismatches",
        }


# Main
