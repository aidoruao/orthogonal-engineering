"""
Evidence Warden - Phase 3 Deployment
Model: mistral:7b
Folder: evidence/
Capabilities: report_generation, artifact_validation, audit_tracing
"""

import hashlib
import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class EvidenceWarden:
    """Warden for monitoring and analyzing the evidence/ directory."""

    def __init__(self, folder_path: str = "evidence"):
        """
        Initialize the evidence warden.

        Args:
            folder_path: Path to the evidence directory
        """
        self.folder_path = folder_path
        self.absolute_path = os.path.abspath(folder_path)
        self.metadata = {
            "file_count": None,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "report_generation",
                "artifact_validation",
                "audit_tracing",
            ],
            "folder_analysis": None,
            "initialization_time": None,
            "status": "pending",
        }
        self.health = {
            "last_query": None,
            "response_time_ms": None,
            "success_rate": None,
            "last_health_check": None,
            "initialization_time_seconds": None,
            "overall_status": "unknown",
        }
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the warden."""
        logger = logging.getLogger(
            f"evidence_warden_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the warden by scanning the evidence folder and generating metadata.

        Returns:
            Dictionary containing initialization results
        """
        start_time = datetime.now()
        self.logger.info(f"Initializing Evidence Warden for folder: {self.folder_path}")

        try:
            # Check if folder exists
            if not os.path.exists(self.folder_path):
                self.metadata["status"] = "pending"
                self.metadata["folder_analysis"] = {
                    "folder_type": "evidence",
                    "exists": False,
                    "readable": False,
                    "file_count": 0,
                    "file_types": {},
                    "total_size_bytes": 0,
                    "last_modified": None,
                    "subfolders": [],
                    "evidence_categories": [],
                }
                self.health["overall_status"] = "warning"
                self.logger.warning(f"Folder does not exist: {self.folder_path}")
                return {
                    "success": False,
                    "error": f"Folder does not exist: {self.folder_path}",
                    "metadata": self.metadata,
                    "health": self.health,
                }

            # Count files and analyze structure
            file_count = self._count_files()
            folder_analysis = self._analyze_folder_structure()
            hash_manifest = self._generate_hash_manifest()

            # Update metadata
            self.metadata.update(
                {
                    "file_count": file_count,
                    "last_hash_manifest": hash_manifest,
                    "folder_analysis": folder_analysis,
                    "initialization_time": datetime.now().isoformat(),
                    "status": "active",
                }
            )

            # Update health
            init_time = (datetime.now() - start_time).total_seconds()
            self.health.update(
                {
                    "last_health_check": datetime.now().isoformat(),
                    "initialization_time_seconds": init_time,
                    "overall_status": "healthy",
                }
            )

            self.logger.info(
                f"Initialization complete. Found {file_count} files in {self.folder_path}"
            )

            return {
                "success": True,
                "metadata": self.metadata,
                "health": self.health,
                "initialization_time_seconds": init_time,
            }

        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            self.logger.error(traceback.format_exc())

            self.metadata["status"] = "error"
            self.health["overall_status"] = "critical"

            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "metadata": self.metadata,
                "health": self.health,
            }

    def query(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Handle BASE AI requests for the evidence folder.

        Args:
            task: The task to perform
            **kwargs: Additional parameters for the task

        Returns:
            Dictionary containing query results
        """
        start_time = datetime.now()
        self.logger.info(f"Processing query: {task}")

        try:
            # Handle different task types
            if task == "get_file_list":
                result = self._get_file_list(**kwargs)
            elif task == "generate_report":
                result = self._generate_report(**kwargs)
            elif task == "validate_artifacts":
                result = self._validate_artifacts(**kwargs)
            elif task == "trace_audit":
                result = self._trace_audit(**kwargs)
            elif task == "analyze_evidence_structure":
                result = self._analyze_evidence_structure(**kwargs)
            elif task == "search_evidence":
                result = self._search_evidence(**kwargs)
            elif task == "get_metadata":
                result = {"metadata": self.metadata}
            elif task == "health_check":
                result = self.health_check()
            else:
                result = {
                    "success": False,
                    "error": f"Unknown task: {task}",
                    "supported_tasks": [
                        "get_file_list",
                        "generate_report",
                        "validate_artifacts",
                        "trace_audit",
                        "analyze_evidence_structure",
                        "search_evidence",
                        "get_metadata",
                        "health_check",
                    ],
                }

            # Update health metrics
            response_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000  # Convert to ms
            self.health.update(
                {
                    "last_query": datetime.now().isoformat(),
                    "response_time_ms": response_time,
                }
            )

            result["response_time_ms"] = response_time
            result["timestamp"] = datetime.now().isoformat()

            return result

        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            self.logger.error(traceback.format_exc())

            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "response_time_ms": (datetime.now() - start_time).total_seconds()
                * 1000,
                "timestamp": datetime.now().isoformat(),
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the warden.

        Returns:
            Dictionary containing health status
        """
        start_time = datetime.now()

        try:
            # Check folder accessibility
            folder_exists = os.path.exists(self.folder_path)
            folder_readable = (
                os.access(self.folder_path, os.R_OK) if folder_exists else False
            )

            # Update health status
            if not folder_exists:
                status = "critical"
                message = f"Folder does not exist: {self.folder_path}"
            elif not folder_readable:
                status = "critical"
                message = f"Folder not readable: {self.folder_path}"
            else:
                status = "healthy"
                message = "Warden is healthy"

                # Verify hash manifest is up to date
                if self.metadata.get("last_hash_manifest"):
                    current_hashes = self._generate_hash_manifest()
                    if current_hashes != self.metadata["last_hash_manifest"]:
                        status = "warning"
                        message = "Hash manifest is outdated"

            # Update health metrics
            check_time = (datetime.now() - start_time).total_seconds()
            self.health.update(
                {
                    "last_health_check": datetime.now().isoformat(),
                    "overall_status": status,
                }
            )

            return {
                "success": True,
                "status": status,
                "message": message,
                "folder_exists": folder_exists,
                "folder_readable": folder_readable,
                "file_count": self.metadata.get("file_count"),
                "check_time_seconds": check_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")

            self.health["overall_status"] = "critical"

            return {
                "success": False,
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get current metadata for the warden.

        Returns:
            Dictionary containing warden metadata
        """
        return {
            "folder_path": self.folder_path,
            "absolute_path": self.absolute_path,
            "metadata": self.metadata,
            "health": self.health,
            "model_name": "mistral:7b",
            "capabilities": self.metadata["capabilities"],
            "timestamp": datetime.now().isoformat(),
        }

    def _count_files(self) -> int:
        """Count all files in the evidence directory recursively."""
        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            count += len(files)
        return count

    def _analyze_folder_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the evidence folder."""
        analysis = {
            "folder_type": "evidence",
            "exists": True,
            "readable": True,
            "file_count": 0,
            "file_types": {},
            "total_size_bytes": 0,
            "last_modified": None,
            "subfolders": [],
            "evidence_categories": [],
        }

        try:
            subfolders = []
            evidence_categories = []
            total_size = 0
            file_types = {}
            last_modified = None

            for root, dirs, files in os.walk(self.folder_path):
                # Record subfolders
                rel_root = os.path.relpath(root, self.folder_path)
                if rel_root != ".":
                    subfolders.append(rel_root)
                    # Extract evidence category from folder name
                    folder_name = os.path.basename(root)
                    if any(
                        keyword in folder_name.lower()
                        for keyword in [
                            "case",
                            "study",
                            "analysis",
                            "report",
                            "validation",
                            "audit",
                        ]
                    ):
                        evidence_categories.append(folder_name)

                # Process files
                for file in files:
                    analysis["file_count"] += 1

                    # Update file type counts
                    ext = os.path.splitext(file)[1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

                    # Calculate file size
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size

                        # Track last modified time
                        file_mtime = os.path.getmtime(file_path)
                        if last_modified is None or file_mtime > last_modified:
                            last_modified = file_mtime
                    except (OSError, PermissionError):
                        pass

            analysis.update(
                {
                    "subfolders": sorted(subfolders),
                    "evidence_categories": sorted(set(evidence_categories)),
                    "file_types": file_types,
                    "total_size_bytes": total_size,
                    "last_modified": datetime.fromtimestamp(last_modified).isoformat()
                    if last_modified
                    else None,
                }
            )

        except Exception as e:
            self.logger.error(f"Folder analysis failed: {str(e)}")
            analysis["readable"] = False

        return analysis

    def _generate_hash_manifest(self) -> Dict[str, str]:
        """Generate SHA256 hash manifest for all files in evidence directory."""
        hash_manifest = {}

        try:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_path)

                    try:
                        with open(file_path, "rb") as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            hash_manifest[rel_path] = file_hash
                    except (IOError, PermissionError) as e:
                        self.logger.warning(f"Could not hash file {rel_path}: {str(e)}")
                        hash_manifest[rel_path] = "ERROR: " + str(e)

        except Exception as e:
            self.logger.error(f"Hash generation failed: {str(e)}")

        return hash_manifest

    def _get_file_list(self, **kwargs) -> Dict[str, Any]:
        """Get list of files in evidence directory."""
        file_list = []

        try:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_path)

                    try:
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)

                        file_list.append(
                            {
                                "path": rel_path,
                                "size_bytes": file_size,
                                "modified": datetime.fromtimestamp(
                                    file_mtime
                                ).isoformat(),
                                "extension": os.path.splitext(file)[1].lower(),
                            }
                        )
                    except (OSError, PermissionError):
                        file_list.append(
                            {
                                "path": rel_path,
                                "size_bytes": None,
                                "modified": None,
                                "extension": os.path.splitext(file)[1].lower(),
                            }
                        )

            return {
                "success": True,
                "file_count": len(file_list),
                "files": file_list,
                "total_files": len(file_list),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "file_count": 0, "files": []}

    def _generate_report(
        self, report_type: str = "summary", **kwargs
    ) -> Dict[str, Any]:
        """Generate evidence report."""
        try:
            if report_type == "summary":
                report = self._generate_summary_report()
            elif report_type == "detailed":
                report = self._generate_detailed_report()
            elif report_type == "validation":
                report = self._generate_validation_report()
            else:
                return {
                    "success": False,
                    "error": f"Unknown report type: {report_type}",
                    "supported_types": ["summary", "detailed", "validation"],
                }

            report["report_type"] = report_type
            report["timestamp"] = datetime.now().isoformat()
            report["success"] = True

            return report

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report_type": report_type,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary evidence report."""
        metadata = self.get_metadata()
        folder_analysis = self.metadata.get("folder_analysis", {})

        return {
            "evidence_summary": {
                "total_files": metadata["metadata"]["file_count"],
                "total_size_bytes": folder_analysis.get("total_size_bytes", 0),
                "evidence_categories": folder_analysis.get("evidence_categories", []),
                "file_types": folder_analysis.get("file_types", {}),
                "last_modified": folder_analysis.get("last_modified"),
                "warden_status": metadata["metadata"]["status"],
                "health_status": metadata["health"]["overall_status"],
            },
            "key_findings": {
                "has_hash_manifest": bool(self.metadata.get("last_hash_manifest")),
                "hash_count": len(self.metadata.get("last_hash_manifest", {})),
                "subfolders_count": len(folder_analysis.get("subfolders", [])),
                "readable": folder_analysis.get("readable", False),
            },
        }

    def _generate_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed evidence report."""
        file_list_result = self._get_file_list()
        if not file_list_result["success"]:
            return {"error": "Could not retrieve file list"}

        files = file_list_result["files"]

        # Group files by extension
        files_by_extension = {}
        for file in files:
            ext = file["extension"]
            if ext not in files_by_extension:
                files_by_extension[ext] = []
            files_by_extension[ext].append(file)

        # Group files by modification date (recent vs old)
        recent_files = []
        old_files = []
        cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days ago

        for file in files:
            if file["modified"]:
                file_time = datetime.fromisoformat(file["modified"]).timestamp()
                if file_time > cutoff_date:
                    recent_files.append(file)
                else:
                    old_files.append(file)

        return {
            "detailed_analysis": {
                "files_by_extension": {
                    ext: len(files) for ext, files in files_by_extension.items()
                },
                "recent_files_count": len(recent_files),
                "old_files_count": len(old_files),
                "largest_files": sorted(
                    files, key=lambda x: x.get("size_bytes", 0) or 0, reverse=True
                )[:10],
                "recently_modified": sorted(
                    recent_files, key=lambda x: x.get("modified") or "", reverse=True
                )[:10],
            },
            "file_statistics": {
                "total_files": len(files),
                "files_with_size": len([f for f in files if f.get("size_bytes")]),
                "files_with_timestamp": len([f for f in files if f.get("modified")]),
                "average_size_bytes": sum(f.get("size_bytes", 0) or 0 for f in files)
                / max(len(files), 1),
            },
        }

    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate validation report for evidence artifacts."""
        hash_manifest = self.metadata.get("last_hash_manifest", {})

        validation_results = {
            "valid_files": 0,
            "invalid_files": 0,
            "missing_files": 0,
            "validation_errors": [],
            "file_validations": [],
        }

        try:
            # Validate each file in the hash manifest
            for file_path, expected_hash in hash_manifest.items():
                full_path = os.path.join(self.folder_path, file_path)

                if not os.path.exists(full_path):
                    validation_results["missing_files"] += 1
                    validation_results["validation_errors"].append(
                        {"file": file_path, "error": "File not found"}
                    )
                    continue

                try:
                    with open(full_path, "rb") as f:
                        actual_hash = hashlib.sha256(f.read()).hexdigest()

                    is_valid = actual_hash == expected_hash

                    validation_results["file_validations"].append(
                        {
                            "file": file_path,
                            "expected_hash": expected_hash,
                            "actual_hash": actual_hash,
                            "valid": is_valid,
                            "file_exists": True,
                        }
                    )

                    if is_valid:
                        validation_results["valid_files"] += 1
                    else:
                        validation_results["invalid_files"] += 1
                        validation_results["validation_errors"].append(
                            {
                                "file": file_path,
                                "error": "Hash mismatch",
                                "expected": expected_hash,
                                "actual": actual_hash,
                            }
                        )

                except (IOError, PermissionError) as e:
                    validation_results["invalid_files"] += 1
                    validation_results["validation_errors"].append(
                        {"file": file_path, "error": f"Read error: {str(e)}"}
                    )

            return validation_results

        except Exception as e:
            return {"error": str(e), "validation_results": validation_results}

    def _validate_artifacts(
        self, artifact_type: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Validate evidence artifacts."""
        try:
            validation_report = self._generate_validation_report()

            return {
                "success": True,
                "artifact_type": artifact_type,
                "validation_report": validation_report,
                "summary": {
                    "total_files": len(self.metadata.get("last_hash_manifest", {})),
                    "valid_files": validation_report.get("valid_files", 0),
                    "invalid_files": validation_report.get("invalid_files", 0),
                    "missing_files": validation_report.get("missing_files", 0),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "artifact_type": artifact_type}

    def _trace_audit(self, audit_id: str = None, **kwargs) -> Dict[str, Any]:
        """Trace audit activities in evidence."""
        try:
            # Search for audit-related files
            search_result = self._search_evidence(
                pattern="audit" if not audit_id else audit_id, **kwargs
            )

            audit_files = []
            if search_result.get("success", False):
                audit_files = search_result.get("matches", [])

            return {
                "success": True,
                "audit_id": audit_id,
                "audit_files_found": len(audit_files),
                "audit_files": audit_files[:10],  # Limit to 10 files
                "search_pattern": "audit" if not audit_id else audit_id,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "audit_id": audit_id}

    def _analyze_evidence_structure(self, **kwargs) -> Dict[str, Any]:
        """Analyze the structure of evidence files."""
        folder_analysis = self.metadata.get("folder_analysis", {})

        analysis = {
            "evidence_categories": folder_analysis.get("evidence_categories", []),
            "file_type_distribution": folder_analysis.get("file_types", {}),
            "folder_hierarchy": {
                "depth": self._calculate_folder_depth(),
                "subfolders": folder_analysis.get("subfolders", []),
            },
            "temporal_analysis": {
                "last_modified": folder_analysis.get("last_modified"),
                "file_age_distribution": self._analyze_file_ages(),
            },
        }

        return {
            "success": True,
            "analysis": analysis,
            "total_categories": len(analysis["evidence_categories"]),
            "total_file_types": len(analysis["file_type_distribution"]),
        }

    def _search_evidence(
        self, pattern: str = None, file_extension: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Search for evidence matching pattern."""
        if not pattern:
            return {
                "success": False,
                "error": "No search pattern provided",
                "matches": [],
            }

        matches = []

        try:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    if file_extension and not file.endswith(file_extension):
                        continue

                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_path)

                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                matches.append(
                                    {
                                        "file": rel_path,
                                        "pattern_found": True,
                                        "line_count": len(content.splitlines()),
                                        "file_size": os.path.getsize(file_path)
                                        if os.path.exists(file_path)
                                        else None,
                                    }
                                )
                    except (IOError, PermissionError, UnicodeDecodeError):
                        continue

            return {
                "success": True,
                "pattern": pattern,
                "matches_found": len(matches),
                "matches": matches,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pattern": pattern,
                "matches_found": 0,
                "matches": [],
            }

    def _calculate_folder_depth(self) -> int:
        """Calculate maximum folder depth."""
        max_depth = 0

        try:
            for root, dirs, files in os.walk(self.folder_path):
                depth = root[len(self.folder_path) :].count(os.sep)
                if depth > max_depth:
                    max_depth = depth
        except Exception:
            pass

        return max_depth

    def _analyze_file_ages(self) -> Dict[str, int]:
        """Analyze distribution of file ages."""
        age_distribution = {
            "less_than_day": 0,
            "less_than_week": 0,
            "less_than_month": 0,
            "less_than_year": 0,
            "more_than_year": 0,
        }

        try:
            current_time = datetime.now().timestamp()

            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)

                    try:
                        file_mtime = os.path.getmtime(file_path)
                        age_seconds = current_time - file_mtime

                        if age_seconds < 86400:  # 1 day
                            age_distribution["less_than_day"] += 1
                        elif age_seconds < 604800:  # 1 week
                            age_distribution["less_than_week"] += 1
                        elif age_seconds < 2592000:  # 30 days
                            age_distribution["less_than_month"] += 1
                        elif age_seconds < 31536000:  # 1 year
                            age_distribution["less_than_year"] += 1
                        else:
                            age_distribution["more_than_year"] += 1

                    except (OSError, PermissionError):
                        pass

        except Exception:
            pass

        return age_distribution
