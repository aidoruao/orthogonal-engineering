"""
Logs Warden - Phase 3 Deployment
Model: qwen2.5:7b
Folder: logs/
Capabilities: pattern_detection, anomaly_alerts, operation_tracing
"""

import hashlib
import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LogsWarden:
    """Warden for monitoring and analyzing the logs/ directory."""

    def __init__(self, folder_path: str = "logs"):
        """
        Initialize the logs warden.

        Args:
            folder_path: Path to the logs directory
        """
        self.folder_path = folder_path
        self.absolute_path = os.path.abspath(folder_path)
        self.metadata = {
            "file_count": None,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "pattern_detection",
                "anomaly_alerts",
                "operation_tracing",
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
            f"logs_warden_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
        Initialize the warden by scanning the logs folder and generating metadata.

        Returns:
            Dictionary containing initialization results
        """
        start_time = datetime.now()
        self.logger.info(f"Initializing Logs Warden for folder: {self.folder_path}")

        try:
            # Check if folder exists
            if not os.path.exists(self.folder_path):
                self.metadata["status"] = "pending"
                self.metadata["folder_analysis"] = {
                    "folder_type": "logs",
                    "exists": False,
                    "readable": False,
                    "file_count": 0,
                    "file_types": {},
                    "total_size_bytes": 0,
                    "last_modified": None,
                    "subfolders": [],
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
        Handle BASE AI requests for the logs folder.

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
            elif task == "search_patterns":
                result = self._search_patterns(**kwargs)
            elif task == "analyze_log_structure":
                result = self._analyze_log_structure(**kwargs)
            elif task == "detect_anomalies":
                result = self._detect_anomalies(**kwargs)
            elif task == "trace_operations":
                result = self._trace_operations(**kwargs)
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
                        "search_patterns",
                        "analyze_log_structure",
                        "detect_anomalies",
                        "trace_operations",
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
            "model_name": "qwen2.5:7b",
            "capabilities": self.metadata["capabilities"],
            "timestamp": datetime.now().isoformat(),
        }

    def _count_files(self) -> int:
        """Count all files in the logs directory recursively."""
        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            count += len(files)
        return count

    def _analyze_folder_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the logs folder."""
        analysis = {
            "folder_type": "logs",
            "exists": True,
            "readable": True,
            "file_count": 0,
            "file_types": {},
            "total_size_bytes": 0,
            "last_modified": None,
            "subfolders": [],
            "log_categories": [],
        }

        try:
            subfolders = []
            log_categories = []
            total_size = 0
            file_types = {}
            last_modified = None

            for root, dirs, files in os.walk(self.folder_path):
                # Record subfolders
                rel_root = os.path.relpath(root, self.folder_path)
                if rel_root != ".":
                    subfolders.append(rel_root)
                    # Extract log category from folder name
                    folder_name = os.path.basename(root)
                    if any(
                        keyword in folder_name.lower()
                        for keyword in [
                            "audit",
                            "error",
                            "trace",
                            "violation",
                            "log",
                            "debug",
                        ]
                    ):
                        log_categories.append(folder_name)

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
                    "log_categories": sorted(set(log_categories)),
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
        """Generate SHA256 hash manifest for all files in logs directory."""
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
        """Get list of files in logs directory."""
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

    def _search_patterns(
        self, pattern: str = None, file_extension: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Search for patterns in log files."""
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

    def _analyze_log_structure(self, **kwargs) -> Dict[str, Any]:
        """Analyze the structure and organization of log files."""
        analysis = {
            "log_categories": {},
            "file_size_distribution": {},
            "recent_files": [],
            "oldest_files": [],
        }

        try:
            files_by_category = {}
            file_sizes = []
            file_times = []

            for root, dirs, files in os.walk(self.folder_path):
                category = os.path.basename(root)
                if category not in files_by_category:
                    files_by_category[category] = []

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_path)

                    try:
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)

                        files_by_category[category].append(
                            {
                                "file": rel_path,
                                "size_bytes": file_size,
                                "modified": datetime.fromtimestamp(
                                    file_mtime
                                ).isoformat(),
                            }
                        )

                        file_sizes.append(file_size)
                        file_times.append((file_mtime, rel_path))
                    except (OSError, PermissionError):
                        continue

            # Sort files by modification time
            file_times.sort(reverse=True)  # Most recent first
            recent_files = [
                {"file": path, "modified": datetime.fromtimestamp(time).isoformat()}
                for time, path in file_times[:10]
            ]

            file_times.sort()  # Oldest first
            oldest_files = [
                {"file": path, "modified": datetime.fromtimestamp(time).isoformat()}
                for time, path in file_times[:10]
            ]

            # Calculate size distribution
            size_ranges = {
                "tiny": 0,  # < 1KB
                "small": 0,  # 1KB - 100KB
                "medium": 0,  # 100KB - 1MB
                "large": 0,  # 1MB - 10MB
                "huge": 0,  # > 10MB
            }

            for size in file_sizes:
                if size < 1024:
                    size_ranges["tiny"] += 1
                elif size < 102400:
                    size_ranges["small"] += 1
                elif size < 1048576:
                    size_ranges["medium"] += 1
                elif size < 10485760:
                    size_ranges["large"] += 1
                else:
                    size_ranges["huge"] += 1

            analysis.update(
                {
                    "log_categories": {
                        cat: len(files) for cat, files in files_by_category.items()
                    },
                    "file_size_distribution": size_ranges,
                    "recent_files": recent_files,
                    "oldest_files": oldest_files,
                }
            )

            return {
                "success": True,
                "analysis": analysis,
                "total_categories": len(files_by_category),
                "total_files": len(file_sizes),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "analysis": analysis}

    def _detect_anomalies(self, threshold_days: int = 7, **kwargs) -> Dict[str, Any]:
        """Detect anomalies in log files."""
        anomalies = {
            "empty_files": [],
            "very_large_files": [],
            "very_old_files": [],
            "recently_modified_old_files": [],
            "suspicious_patterns": [],
        }

        try:
            current_time = datetime.now().timestamp()
            threshold_seconds = threshold_days * 24 * 60 * 60

            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_path)

                    try:
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)
                        file_age = current_time - file_mtime

                        # Check for empty files
                        if file_size == 0:
                            anomalies["empty_files"].append(
                                {"file": rel_path, "size": file_size}
                            )

                        # Check for very large files (> 10MB)
                        if file_size > 10 * 1024 * 1024:  # 10MB
                            anomalies["very_large_files"].append(
                                {
                                    "file": rel_path,
                                    "size_bytes": file_size,
                                    "size_mb": file_size / (1024 * 1024),
                                }
                            )

                        # Check for very old files (> threshold)
                        if file_age > threshold_seconds:
                            anomalies["very_old_files"].append(
                                {
                                    "file": rel_path,
                                    "age_days": file_age / (24 * 60 * 60),
                                    "last_modified": datetime.fromtimestamp(
                                        file_mtime
                                    ).isoformat(),
                                }
                            )

                        # Check for suspicious patterns in file names
                        suspicious_keywords = [
                            "error",
                            "fail",
                            "crash",
                            "exception",
                            "warning",
                        ]
                        if any(
                            keyword in file.lower() for keyword in suspicious_keywords
                        ):
                            anomalies["suspicious_patterns"].append(
                                {"file": rel_path, "pattern": "suspicious_filename"}
                            )

                    except (OSError, PermissionError):
                        continue

            # Check for recently modified old files (possible tampering)
            for old_file in anomalies["very_old_files"]:
                file_path = os.path.join(self.folder_path, old_file["file"])
                try:
                    file_mtime = os.path.getmtime(file_path)
                    # If file is old but was modified recently (within last day)
                    if current_time - file_mtime < 86400:  # 1 day
                        anomalies["recently_modified_old_files"].append(old_file)
                except (OSError, PermissionError):
                    continue

            return {
                "success": True,
                "anomalies": anomalies,
                "summary": {
                    "total_anomalies": sum(len(items) for items in anomalies.values()),
                    "empty_files": len(anomalies["empty_files"]),
                    "very_large_files": len(anomalies["very_large_files"]),
                    "very_old_files": len(anomalies["very_old_files"]),
                    "recently_modified_old_files": len(
                        anomalies["recently_modified_old_files"]
                    ),
                    "suspicious_patterns": len(anomalies["suspicious_patterns"]),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "anomalies": anomalies}

    def _trace_operations(self, operation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Trace operations in log files."""
        try:
            # Search for operation-related files
            search_pattern = operation_id if operation_id else "operation"
            search_result = self._search_patterns(pattern=search_pattern, **kwargs)

            operation_files = []
            if search_result.get("success", False):
                operation_files = search_result.get("matches", [])

            # Analyze operation patterns
            operation_patterns = self._analyze_operation_patterns(operation_files)

            return {
                "success": True,
                "operation_id": operation_id,
                "operation_files_found": len(operation_files),
                "operation_files": operation_files[:10],  # Limit to 10 files
                "operation_patterns": operation_patterns,
                "search_pattern": search_pattern,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "operation_id": operation_id}

    def _analyze_operation_patterns(
        self, operation_files: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze patterns in operation files."""
        patterns = {
            "by_extension": {},
            "by_folder": {},
            "timeline": [],
            "size_distribution": {
                "small": 0,  # < 1KB
                "medium": 0,  # 1KB - 100KB
                "large": 0,  # > 100KB
            },
        }

        try:
            for op_file in operation_files:
                file_path = op_file.get("file", "")

                # Analyze by extension
                ext = os.path.splitext(file_path)[1].lower()
                patterns["by_extension"][ext] = patterns["by_extension"].get(ext, 0) + 1

                # Analyze by folder
                folder = os.path.dirname(file_path)
                if folder:
                    patterns["by_folder"][folder] = (
                        patterns["by_folder"].get(folder, 0) + 1
                    )

                # Get file size if available
                full_path = os.path.join(self.folder_path, file_path)
                if os.path.exists(full_path):
                    try:
                        file_size = os.path.getsize(full_path)
                        if file_size < 1024:
                            patterns["size_distribution"]["small"] += 1
                        elif file_size < 102400:
                            patterns["size_distribution"]["medium"] += 1
                        else:
                            patterns["size_distribution"]["large"] += 1
                    except (OSError, PermissionError):
                        pass

            return patterns

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the warden
    warden = LogsWarden("logs")
    print("Initializing logs warden...")
    result = warden.initialize()
    print(f"Initialization result: {result.get('success', False)}")
    print(f"File count: {result.get('metadata', {}).get('file_count', 'N/A')}")

    if result.get("success", False):
        print("\nTesting queries...")
        print("1. Health check:")
        health = warden.health_check()
        print(f"   Status: {health.get('status', 'N/A')}")

        print("\n2. File list (first 5):")
        files = warden.query("get_file_list")
        if files.get("success", False):
            file_list = files.get("files", [])[:5]
            for f in file_list:
                print(
                    f"   - {f.get('path', 'N/A')} ({f.get('size_bytes', 'N/A')} bytes)"
                )

        print("\n3. Metadata:")
        metadata = warden.get_metadata()
        print(f"   Model: {metadata.get('model_name', 'N/A')}")
        print(f"   Capabilities: {', '.join(metadata.get('capabilities', []))}")
