#!/usr/bin/env python3
"""
Toolkit Warden for the Local AI Warden System - Phase 2

This warden is responsible for monitoring and managing the toolkit/oe/ folder.
Model: codellama:7b
Capabilities: autofix_engine, boundary_spellcheck, ide_integration
"""

import hashlib
import json
import logging
import os
import re
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


class ToolkitWarden:
    """Warden for the toolkit/oe/ folder."""

    def __init__(self, folder_path: str = "toolkit/oe"):
        """
        Initialize the Toolkit Warden.

        Args:
            folder_path: Path to the toolkit/oe folder (relative to project root)
        """
        self.folder_path = folder_path
        self.status = "pending"  # pending, active, error, disabled
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "autofix_engine",
                "boundary_spellcheck",
                "ide_integration",
            ],
            "model_name": "codellama:7b",
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
        self.autofix_patterns = self._load_autofix_patterns()
        self.boundary_patterns = self._load_boundary_patterns()

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

            # Load toolkit-specific metadata
            toolkit_metadata = self._analyze_toolkit_structure()
            self.metadata.update(toolkit_metadata)

            # Update status
            self.status = "active"
            self.initialized = True
            self.error_message = None

            initialization_time = time.time() - start_time

            logger.info(
                f"Toolkit Warden initialized successfully. Found {file_count} files."
            )

            return {
                "success": True,
                "file_count": file_count,
                "hash_manifest": hash_manifest,
                "toolkit_metadata": toolkit_metadata,
                "initialization_time_seconds": initialization_time,
                "status": self.status,
            }

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            logger.error(f"Failed to initialize Toolkit Warden: {e}")
            return {"success": False, "error": str(e), "status": self.status}

    def query(
        self, task: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle BASE AI requests for the toolkit/oe folder.

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

            # Check for critical toolkit files
            critical_files = self._check_critical_files()

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
                "critical_files": critical_files,
                "health_metrics": self.health.copy(),
                "error_message": self.error_message,
                "check_time_seconds": time.time() - check_start,
            }

            # Determine overall health status
            if not folder_exists or not can_read:
                health_status["overall_health"] = "critical"
            elif not all(critical_files.values()):
                health_status["overall_health"] = "warning"
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
            "warden_type": "toolkit_warden",
            "folder_path": self.folder_path,
            "status": self.status,
            "metadata": self.metadata.copy(),
            "health": self.health.copy(),
            "initialized": self.initialized,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def _count_files(self) -> int:
        """Count files recursively in the toolkit/oe folder."""
        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            count += len(files)
        return count

    def _generate_hash_manifest(self) -> Dict[str, str]:
        """
        Generate SHA256 hash manifest for files in the toolkit/oe folder.

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

    def _analyze_toolkit_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the toolkit/oe folder."""
        analysis = {
            "python_files": 0,
            "core_components": [],
            "module_dependencies": {},
            "autofix_components": [],
            "boundary_components": [],
            "ide_components": [],
        }

        python_files = self._find_python_files()

        for file_path in python_files:
            file_name = os.path.basename(file_path)

            # Categorize files by capability
            if "autofix" in file_name.lower():
                analysis["autofix_components"].append(file_name)
            elif "boundary" in file_name.lower():
                analysis["boundary_components"].append(file_name)
            elif "ide" in file_name.lower():
                analysis["ide_components"].append(file_name)
            elif file_name in ["__init__.py", "__main__.py", "cli.py"]:
                analysis["core_components"].append(file_name)
            else:
                analysis["python_files"] += 1

            # Analyze imports for dependencies
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract imports
                import_lines = [
                    line.strip() for line in content.split("\n")
                    if line.strip().startswith("import") or line.strip().startswith("from")
                ]

                if import_lines:
                    analysis["module_dependencies"][file_name] = import_lines[:5]  # Limit to 5

            except Exception as e:
                logger.warning(f"Could not analyze dependencies for {file_path}: {e}")

        return analysis

    def _load_autofix_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load autofix patterns for code analysis."""
        return {
            "missing_decorator": {
                "pattern": r"def\s+\w+\([^)]*\):[^@\n]*\n(?!\s*@)",
                "description": "Function missing boundary decorator",
                "fix": "Add @glass_box_boundary decorator",
                "severity": "high"
            },
            "broad_exception": {
                "pattern": r"except\s+(Exception|BaseException|):",
                "description": "Broad exception catching",
                "fix": "Replace with specific exception types",
                "severity": "medium"
            },
            "direct_io": {
                "pattern": r"open\([^)]*\)[^)]*(write|read|append)",
                "description": "Direct file I/O without gateway",
                "fix": "Use gateway interface pattern",
                "severity": "high"
            },
            "missing_validation": {
                "pattern": r"def\s+\w+\([^)]*\):[^:]*\n\s*(?!.*#.*validation)",
                "description": "Function missing input validation",
                "fix": "Add input validation schema",
                "severity": "medium"
            }
        }

    def _load_boundary_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load boundary violation patterns for spell-check."""
        return {
            "ui_database_path": {
                "pattern": r"(ui|frontend).*?(database|db).*?\.(py|js|ts)",
                "description": "UI to database direct path",
                "fix": "Refactor to use gateway pattern",
                "severity": "critical"
            },
            "suppressed_warnings": {
                "pattern": r'warnings\.(filterwarnings|simplefilter)\("ignore"\)',
                "description": "Suppressed warnings",
                "fix": "Remove warning suppression or log warnings",
                "severity": "medium"
            },
            "missing_logging": {
                "pattern": r"def\s+\w+\([^)]*\):[^:]*\n(?!.*logging\.|.*logger\.)",
                "description": "Function missing logging",
                "fix": "Add logging infrastructure",
                "severity": "low"
            }
        }

    def _handle_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle specific tasks for the toolkit/oe folder.

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
            toolkit_metadata = self._analyze_toolkit_structure()

            self.metadata["file_count"] = file_count
            self.metadata["last_hash_manifest"] = hash_manifest
            self.metadata.update(toolkit_metadata)

            return {
                "task": "scan",
                "file_count": file_count,
                "hash_manifest_size": len(hash_manifest),
                "toolkit_metadata": toolkit_metadata,
                "message": f"Scanned {file_count} files in toolkit/oe",
            }

        elif task == "analyze_autofix":
            # Analyze autofix capabilities
            autofix_analysis = self._analyze_autofix_capabilities()

            return {
                "task": "analyze_autofix",
                "autofix_files": autofix_analysis["files"],
                "patterns_loaded": len(self.autofix_patterns),
                "capabilities": autofix_analysis["capabilities"],
                "message": f"Analyzed {len(autofix_analysis['files'])} autofix components"
            }

        elif task == "check_boundary_spellcheck":
            # Run boundary spell-check on toolkit files
            violations = self._run_boundary_spellcheck()

            return {
                "task": "check_boundary_spellcheck",
                "violation_count": len(violations),
                "violations": violations[:20],  # Limit to 20 violations
                "patterns_checked": len(self.boundary_patterns),
                "message": f"Found {len(violations)} boundary violations"
            }

        elif task == "analyze_ide_integration":
            # Analyze IDE integration components
            ide_analysis = self._analyze_ide_integration()

            return {
                "task": "analyze_ide_integration",
                "ide_files": ide_analysis["files"],
                "integration_points": ide_analysis["integration_points"],
                "capabilities": ide_analysis["capabilities"],
                "message": f"Analyzed {len(ide_analysis['files'])} IDE integration components"
            }

        elif task == "suggest_autofix":
            # Suggest autofixes for specific code
            if "code" not in parameters:
                return {
                    "task": "suggest_autofix",
                    "error": "Missing 'code' parameter",
                    "suggestion": "Provide 'code' parameter with code to analyze"
                }

            suggestions = self._suggest_autofixes(parameters["code"])

            return {
                "task": "suggest_autofix",
                "suggestion_count": len(suggestions),
                "suggestions": suggestions,
                "message": f"Generated {len(suggestions)} autofix suggestions"
            }

        elif task == "get_component_status":
            # Get status of toolkit components
            component_status = self._get_component_status()

            return {
                "task": "get_component_status",
                "components": component_status,
                "total_components": len(component_status),
                "message": f"Retrieved status for {len(component_status)} components"
            }

        elif task == "verify_toolkit_integrity":
            # Verify toolkit integrity
            integrity_check = self._verify_toolkit_integrity()

            return {
                "task": "verify_toolkit_integrity",
                "integrity_check": integrity_check,
                "message": f"Toolkit integrity check {'passed' if integrity_check['passed'] else 'failed'}"
            }

        else:
            # Default task handler
            return {
                "task": task,
                "message": f"Task '{task}' received but not specifically implemented",
                "parameters": parameters,
                "suggestion": "Available tasks: scan, analyze_autofix, check_boundary_spellcheck, analyze_ide_integration, suggest_autofix, get_component_status, verify
