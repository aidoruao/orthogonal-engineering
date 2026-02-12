"""
Dynamic Warden Tool for Local AI Warden System

Tool used by BASE AI to handle unclassified folders:
1. Classifies new/unclassified folders
2. Creates temporary wardens for analysis
3. Tracks query count and lifetime
4. Reports classification to BASE AI
5. Promotes to permanent warden if threshold met

Key Principles:
- Dynamic warden is a TOOL, not an independent warden
- Operates under BASE AI supervision
- Read-only analysis of folder contents
- Atomic operations with traceability
- Automatic cleanup of temporary wardens

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

import hashlib
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import ollama


class FolderType(Enum):
    """Classification of folder types."""

    CODE = "code"  # Python, JavaScript, etc.
    DOCUMENTATION = "documentation"  # Markdown, HTML, docs
    LOGS = "logs"  # Log files, traces, audit logs
    DATA = "data"  # JSON, CSV, databases
    CONFIG = "config"  # Configuration files
    TESTS = "tests"  # Test files
    UNKNOWN = "unknown"  # Unclassified
    MIXED = "mixed"  # Multiple types


class FilePattern:
    """Patterns for file type detection."""

    CODE_PATTERNS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "c++",
        ".c": "c",
        ".rs": "rust",
        ".go": "go",
        ".rb": "ruby",
        ".php": "php",
    }

    DOCUMENTATION_PATTERNS = {
        ".md": "markdown",
        ".html": "html",
        ".htm": "html",
        ".txt": "text",
        ".rst": "restructuredtext",
        ".tex": "latex",
    }

    DATA_PATTERNS = {
        ".json": "json",
        ".csv": "csv",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
    }

    LOG_PATTERNS = {
        ".log": "log",
        ".txt": "text_log",
        ".csv": "csv_log",
    }

    CONFIG_PATTERNS = {
        ".cfg": "config",
        ".conf": "config",
        ".config": "config",
        ".properties": "properties",
    }


class DynamicWardenTool:
    """Tool for handling unclassified folders."""

    def __init__(self, orchestrator: Any):
        """
        Initialize dynamic warden tool.

        Args:
            orchestrator: Reference to BASE AI orchestrator
        """
        self.orchestrator = orchestrator
        self.registry_manager = orchestrator.registry_manager
        self.logger = logging.getLogger("dynamic_warden_tool")

        # Classification cache
        self.classification_cache: Dict[str, Dict] = {}

        # Model for classification (use a small, fast model)
        self.classification_model = "gemma3:1b"  # 815 MB, fast for classification

        self.logger.info("Dynamic Warden Tool initialized")

    def process_unclassified_folder(self, folder_path: str) -> Dict:
        """
        Process an unclassified folder.

        Args:
            folder_path: Path to unclassified folder

        Returns:
            Processing results
        """
        self.logger.info(f"Processing unclassified folder: {folder_path}")

        # Generate trace
        trace_data = {
            "folder_path": folder_path,
            "operation": "process_unclassified_folder",
        }
        self.orchestrator._generate_trace("dynamic_warden_process", trace_data)

        try:
            # 1. Check if already in unclassified list
            registry = self.registry_manager.load_registry()
            unclassified_folders = registry.get("dynamic_wardens", {}).get(
                "unclassified_folders", []
            )

            if folder_path in unclassified_folders:
                self.logger.info(f"Folder already in unclassified list: {folder_path}")

                # Check for existing temporary warden
                temp_wardens = registry.get("dynamic_wardens", {}).get(
                    "temporary_wardens", {}
                )
                for warden_id, warden_data in temp_wardens.items():
                    if warden_data.get("folder_path") == folder_path:
                        return {
                            "status": "already_processing",
                            "temp_warden_id": warden_id,
                            "folder_path": folder_path,
                        }

            # 2. Analyze folder
            analysis = self._analyze_folder(folder_path)

            # 3. Create temporary warden
            temp_warden_id = self._create_temporary_warden(folder_path, analysis)

            # 4. Add to unclassified folders
            self._add_to_unclassified_folders(folder_path)

            result = {
                "status": "processing_started",
                "temp_warden_id": temp_warden_id,
                "folder_path": folder_path,
                "analysis": analysis,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.logger.info(
                f"Started processing folder {folder_path} with temp warden {temp_warden_id}"
            )
            return result

        except Exception as e:
            self.logger.error(
                f"Failed to process unclassified folder {folder_path}: {e}"
            )
            return {
                "status": "failed",
                "folder_path": folder_path,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _analyze_folder(self, folder_path: str) -> Dict:
        """
        Analyze folder contents and determine type.

        Args:
            folder_path: Path to folder

        Returns:
            Analysis results
        """
        path = Path(folder_path)

        if not path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        # Basic analysis
        file_count = 0
        total_size = 0
        file_types: Dict[str, int] = {}
        folder_types: Set[str] = set()

        # Walk through folder (limit depth for performance)
        for root, dirs, files in os.walk(path, topdown=True):
            # Limit to 3 levels deep for initial analysis
            depth = root[len(str(path)) :].count(os.sep)
            if depth > 2:
                continue

            for file in files:
                file_count += 1
                file_path = Path(root) / file

                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size

                    # Determine file type
                    file_type = self._classify_file(file_path)
                    file_types[file_type] = file_types.get(file_type, 0) + 1

                    # Add to folder type classification
                    folder_type = self._file_type_to_folder_type(file_type)
                    if folder_type:
                        folder_types.add(folder_type.value)

                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue

        # Determine primary folder type
        primary_type = self._determine_primary_type(folder_types, file_types)

        # Get suggested model based on folder type
        suggested_model = self._get_suggested_model(primary_type)

        # Generate folder hash for identification
        folder_hash = self._generate_folder_hash(path)

        return {
            "folder_path": str(path.resolve()),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "folder_types": list(folder_types),
            "primary_type": primary_type.value,
            "suggested_model": suggested_model,
            "folder_hash": folder_hash,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _classify_file(self, file_path: Path) -> str:
        """
        Classify a file by its extension.

        Args:
            file_path: Path to file

        Returns:
            File type classification
        """
        suffix = file_path.suffix.lower()

        # Check patterns in order of specificity
        if suffix in FilePattern.CODE_PATTERNS:
            return f"code_{FilePattern.CODE_PATTERNS[suffix]}"
        elif suffix in FilePattern.DOCUMENTATION_PATTERNS:
            return f"doc_{FilePattern.DOCUMENTATION_PATTERNS[suffix]}"
        elif suffix in FilePattern.DATA_PATTERNS:
            return f"data_{FilePattern.DATA_PATTERNS[suffix]}"
        elif suffix in FilePattern.LOG_PATTERNS:
            return f"log_{FilePattern.LOG_PATTERNS[suffix]}"
        elif suffix in FilePattern.CONFIG_PATTERNS:
            return f"config_{FilePattern.CONFIG_PATTERNS[suffix]}"
        elif file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
            return "test"
        elif "README" in file_path.name.upper():
            return "readme"
        elif "LICENSE" in file_path.name.upper():
            return "license"
        elif ".git" in str(file_path):
            return "git"
        else:
            return "unknown"

    def _file_type_to_folder_type(self, file_type: str) -> Optional[FolderType]:
        """
        Map file type to folder type.

        Args:
            file_type: File type classification

        Returns:
            Corresponding FolderType or None
        """
        if file_type.startswith("code_"):
            return FolderType.CODE
        elif file_type.startswith("doc_"):
            return FolderType.DOCUMENTATION
        elif file_type.startswith("data_"):
            return FolderType.DATA
        elif file_type.startswith("log_"):
            return FolderType.LOGS
        elif file_type.startswith("config_"):
            return FolderType.CONFIG
        elif file_type == "test":
            return FolderType.TESTS
        else:
            return None

    def _determine_primary_type(
        self, folder_types: Set[str], file_types: Dict[str, int]
    ) -> FolderType:
        """
        Determine primary folder type from analysis.

        Args:
            folder_types: Set of folder type strings
            file_types: Dictionary of file type counts

        Returns:
            Primary FolderType
        """
        if not folder_types:
            return FolderType.UNKNOWN

        if len(folder_types) == 1:
            return FolderType(list(folder_types)[0])

        # Count occurrences of each type in file_types
        type_counts: Dict[str, int] = {}
        for file_type, count in file_types.items():
            folder_type = self._file_type_to_folder_type(file_type)
            if folder_type:
                type_counts[folder_type.value] = (
                    type_counts.get(folder_type.value, 0) + count
                )

        if type_counts:
            # Return type with highest count
            primary_type = max(type_counts.items(), key=lambda x: x[1])[0]
            return FolderType(primary_type)

        # If mixed but can't determine primary, return MIXED
        return FolderType.MIXED

    def _get_suggested_model(self, folder_type: FolderType) -> str:
        """
        Get suggested Ollama model for folder type.

        Args:
            folder_type: Folder type

        Returns:
            Suggested model name
        """
        model_mapping = {
            FolderType.CODE: "codellama:7b",  # Code-specific model
            FolderType.DOCUMENTATION: "mistral:7b",  # Good for text/documentation
            FolderType.LOGS: "qwen2.5:7b",  # Good for pattern recognition
            FolderType.DATA: "llama3.2:3b",  # Balanced for structured data
            FolderType.CONFIG: "llama3.2:3b",  # Small and fast for configs
            FolderType.TESTS: "codellama:7b",  # Code understanding for tests
            FolderType.UNKNOWN: "gemma3:1b",  # Small general-purpose
            FolderType.MIXED: "llama3.2:3b",  # Balanced for mixed content
        }

        return model_mapping.get(folder_type, "gemma3:1b")

    def _generate_folder_hash(self, folder_path: Path) -> str:
        """
        Generate hash for folder identification.

        Args:
            folder_path: Path to folder

        Returns:
            SHA256 hash of folder metadata
        """
        metadata = {
            "path": str(folder_path.resolve()),
            "name": folder_path.name,
            "parent": str(folder_path.parent),
            "exists": folder_path.exists(),
            "is_dir": folder_path.is_dir() if folder_path.exists() else False,
        }

        metadata_str = json.dumps(metadata, sort_keys=True)
        return hashlib.sha256(metadata_str.encode()).hexdigest()[:16]

    def _create_temporary_warden(self, folder_path: str, analysis: Dict) -> str:
        """
        Create temporary warden for folder analysis.

        Args:
            folder_path: Path to folder
            analysis: Folder analysis results

        Returns:
            Temporary warden ID
        """
        # Generate warden ID
        warden_id = f"temp_{hashlib.sha256(folder_path.encode()).hexdigest()[:8]}"

        warden_data = {
            "folder_path": folder_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "analysis": analysis,
            "query_count": 0,
            "last_query": None,
            "status": "temporary",
            "model": analysis.get("suggested_model", "gemma3:1b"),
            "capabilities": [
                "folder_analysis",
                "content_summary",
                "file_type_detection",
            ],
            "metadata": {
                "file_count": analysis.get("file_count", 0),
                "total_size_mb": analysis.get("total_size_mb", 0),
                "primary_type": analysis.get("primary_type", "unknown"),
                "folder_hash": analysis.get("folder_hash"),
            },
        }

        # Add to registry
        self.registry_manager.add_temporary_warden(folder_path, warden_data)

        self.logger.info(
            f"Created temporary warden {warden_id} for folder {folder_path}"
        )
        return warden_id

    def _add_to_unclassified_folders(self, folder_path: str) -> None:
        """
        Add folder to unclassified folders list.

        Args:
            folder_path: Path to folder
        """
        registry = self.registry_manager.load_registry()
        unclassified_folders = registry.get("dynamic_wardens", {}).get(
            "unclassified_folders", []
        )

        if folder_path not in unclassified_folders:
            updates = {
                "dynamic_wardens": {
                    "unclassified_folders": unclassified_folders + [folder_path]
                }
            }
            self.registry_manager.update_registry(updates)
            self.logger.info(f"Added {folder_path} to unclassified folders")

    def increment_query_count(self, temp_warden_id: str) -> Dict:
        """
        Increment query count for temporary warden.

        Args:
            temp_warden_id: Temporary warden ID

        Returns:
            Updated warden data
        """
        try:
            registry = self.registry_manager.load_registry()
            temp_wardens = registry.get("dynamic_wardens", {}).get(
                "temporary_wardens", {}
            )

            if temp_warden_id not in temp_wardens:
                raise KeyError(f"Temporary warden not found: {temp_warden_id}")

            warden_data = temp_wardens[temp_warden_id]
            current_count = warden_data.get("query_count", 0)

            updates = {
                "query_count": current_count + 1,
                "last_query": datetime.now(timezone.utc).isoformat(),
            }

            # Check if should be promoted
            if current_count + 1 >= registry.get("dynamic_warden_policy", {}).get(
                "promotion_threshold", 10
            ):
                updates["status"] = "ready_for_promotion"
                self.logger.info(
                    f"Temporary warden {temp_warden_id} ready for promotion"
                )

            # Update warden
            return self.registry_manager.update_warden(temp_warden_id, updates)

        except Exception as e:
            self.logger.error(
                f"Failed to increment query count for {temp_warden_id}: {e}"
            )
            raise

    def check_promotion_candidates(self) -> List[Dict]:
        """
        Check for temporary wardens ready for promotion.

        Returns:
            List of promotion candidates
        """
        candidates = []

        try:
            registry = self.registry_manager.load_registry()
            temp_wardens = registry.get("dynamic_wardens", {}).get(
                "temporary_wardens", {}
            )
            policy = registry.get("dynamic_warden_policy", {})

            promotion_threshold = policy.get("promotion_threshold", 10)

            for warden_id, warden_data in temp_wardens.items():
                query_count = warden_data.get("query_count", 0)
                status = warden_data.get("status", "temporary")

                if (
                    query_count >= promotion_threshold
                    or status == "ready_for_promotion"
                ):
                    candidates.append(
                        {
                            "temp_warden_id": warden_id,
                            "folder_path": warden_data.get("folder_path"),
                            "query_count": query_count,
                            "created_at": warden_data.get("created_at"),
                            "analysis": warden_data.get("analysis", {}),
                            "status": status,
                        }
                    )

            self.logger.info(f"Found {len(candidates)} promotion candidates")
            return candidates

        except Exception as e:
            self.logger.error(f"Failed to check promotion candidates: {e}")
            return []

    def cleanup_expired_temporary_wardens(self) -> Dict:
        """
        Clean up expired temporary wardens.

        Returns:
            Cleanup results
        """
        try:
            registry = self.registry_manager.load_registry()
            temp_wardens = registry.get("dynamic_wardens", {}).get(
                "temporary_wardens", {}
            )
            policy = registry.get("dynamic_warden_policy", {})

            max_lifetime_hours = policy.get("max_lifetime_hours", 24)
            current_time = datetime.now(timezone.utc)

            expired_wardens = []
            for warden_id, warden_data in temp_wardens.items():
                created_at_str = warden_data.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(
                            created_at_str.replace("Z", "+00:00")
                        )
                        age_hours = (current_time - created_at).total_seconds() / 3600

                        if age_hours > max_lifetime_hours:
                            expired_wardens.append(
                                {
                                    "warden_id": warden_id,
                                    "folder_path": warden_data.get("folder_path"),
                                    "age_hours": round(age_hours, 2),
                                    "query_count": warden_data.get("query_count", 0),
                                }
                            )
                    except (ValueError, TypeError):
                        continue

            # Remove expired wardens
            cleaned = []
            for warden_info in expired_wardens:
                warden_id = warden_info["warden_id"]
                try:
                    # Remove from temporary wardens
                    if warden_id in temp_wardens:
                        del temp_wardens[warden_id]

                    # Remove from unclassified folders if present
                    folder_path = warden_info["folder_path"]
                    unclassified_folders = registry.get("dynamic_wardens", {}).get(
                        "unclassified_folders", []
                    )
                    if folder_path in unclassified_folders:
                        unclassified_folders.remove(folder_path)

                    cleaned.append(warden_id)
                    self.logger.info(
                        f"Cleaned up expired temporary warden: {warden_id}"
                    )
                except Exception as e:
                    self.logger.error(f"Failed to clean up warden {warden_id}: {e}")

            # Update registry if any wardens were cleaned
            if cleaned:
                registry["dynamic_wardens"]["temporary_wardens"] = temp_wardens
                self.registry_manager._atomic_write(registry)

            return {
                "cleaned_count": len(cleaned),
                "expired_count": len(expired_wardens),
                "cleaned_wardens": cleaned,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired temporary wardens: {e}")
            return {
                "cleaned_count": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
