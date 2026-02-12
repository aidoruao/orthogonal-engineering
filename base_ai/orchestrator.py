"""
BASE AI Orchestrator for Local AI Warden System

Main orchestrator that:
1. Manages the warden registry
2. Routes queries to appropriate wardens
3. Handles dynamic warden creation for unclassified folders
4. Performs health checks and maintenance
5. Ensures Glass-Box Boundary compliance

Key Principles:
- Exactly one BASE AI warden in root directory
- Dynamic warden is a tool, not independent
- All operations are atomic, idempotent, and traceable
- Read-only by default, explicit approval for writes

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

import hashlib
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_ai.registry_manager import RegistryManager

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================


class QueryStatus(Enum):
    """Status of query execution."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    ROUTED = "routed"
    UNCLASSIFIED = "unclassified"


class WardenType(Enum):
    """Types of wardens in the system."""

    BASE_AI = "base_ai"
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    DYNAMIC_TOOL = "dynamic_tool"


class HealthStatus(Enum):
    """Health status of system components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


# ============================================================================
# DATA MODELS
# ============================================================================


class Query:
    """Represents a query to the warden system."""

    def __init__(
        self,
        query_id: str,
        question: str,
        folder_path: Optional[str] = None,
        context: Optional[Dict] = None,
        priority: int = 1,
    ):
        self.query_id = query_id
        self.question = question
        self.folder_path = folder_path
        self.context = context or {}
        self.priority = priority
        self.status = QueryStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.assigned_warden: Optional[str] = None
        self.response: Optional[Dict] = None
        self.error: Optional[str] = None
        self.execution_time_ms: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert query to dictionary for serialization."""
        return {
            "query_id": self.query_id,
            "question": self.question,
            "folder_path": self.folder_path,
            "context": self.context,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "assigned_warden": self.assigned_warden,
            "response": self.response,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


class WardenResponse:
    """Standardized response from a warden."""

    def __init__(
        self,
        query_id: str,
        warden_id: str,
        answer: str,
        confidence: float,
        evidence: List[str],
        metadata: Optional[Dict] = None,
    ):
        self.query_id = query_id
        self.warden_id = warden_id
        self.answer = answer
        self.confidence = confidence
        self.evidence = evidence
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        """Convert response to dictionary for serialization."""
        return {
            "query_id": self.query_id,
            "warden_id": self.warden_id,
            "answer": self.answer,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================================
# BASE AI ORCHESTRATOR
# ============================================================================


class BaseAIOrchestrator:
    """Main orchestrator for the Local AI Warden System."""

    def __init__(self, registry_path: str = ".ai_registry.json"):
        """
        Initialize BASE AI orchestrator.

        Args:
            registry_path: Path to registry JSON file
        """
        self.registry_path = Path(registry_path)
        self.registry_manager = RegistryManager(registry_path)
        self.logger = self._setup_logging()

        # Load or create registry
        try:
            self.registry = self.registry_manager.load_registry()
            self.logger.info(f"Loaded existing registry from {registry_path}")
        except FileNotFoundError:
            self.registry = self.registry_manager.create_registry()
            self.logger.info(f"Created new registry at {registry_path}")

        # Initialize query tracking
        self.active_queries: Dict[str, Query] = {}
        self.query_history: List[Dict] = []

        # Health check state
        self.last_health_check: Optional[datetime] = None
        self.health_status = HealthStatus.UNKNOWN

        # Dynamic warden tool
        self.dynamic_warden_tool = DynamicWardenTool(self)

        self.logger.info("BASE AI Orchestrator initialized successfully")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = Path("logs") / "warden_system"
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("base_ai_orchestrator")
        logger.setLevel(logging.INFO)

        # File handler
        log_file = log_dir / f"base_ai_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _generate_query_id(self) -> str:
        """Generate unique query ID."""
        return f"QUERY-{uuid.uuid4().hex[:8].upper()}"

    def _generate_trace(self, operation: str, data: Dict) -> Dict:
        """
        Generate Glass-Box compliant trace for an operation.

        Args:
            operation: Name of operation
            data: Operation data

        Returns:
            Trace dictionary
        """
        trace_id = f"TRACE-{uuid.uuid4().hex[:8].upper()}"

        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "registry_hash": self.registry_manager._calculate_hash(self.registry),
            "system_state": {
                "active_queries": len(self.active_queries),
                "total_queries": len(self.query_history),
                "health_status": self.health_status.value,
            },
        }

        # Save trace
        trace_dir = Path("logs") / "traces" / "warden_system"
        trace_dir.mkdir(parents=True, exist_ok=True)
        trace_file = trace_dir / f"{trace_id}.json"

        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2)

        return trace

    def submit_query(
        self,
        question: str,
        folder_path: Optional[str] = None,
        context: Optional[Dict] = None,
        priority: int = 1,
    ) -> str:
        """
        Submit a query to the warden system.

        Args:
            question: The question to ask
            folder_path: Optional target folder path
            context: Optional context dictionary
            priority: Query priority (1=lowest, 5=highest)

        Returns:
            Query ID for tracking
        """
        query_id = self._generate_query_id()
        query = Query(query_id, question, folder_path, context, priority)

        # Generate trace
        trace_data = {
            "query_id": query_id,
            "question": question,
            "folder_path": folder_path,
            "priority": priority,
        }
        self._generate_trace("submit_query", trace_data)

        # Store query
        self.active_queries[query_id] = query
        self.logger.info(f"Submitted query {query_id}: {question[:50]}...")

        # Route query (async in real implementation)
        self._route_query(query_id)

        return query_id

    def _route_query(self, query_id: str) -> None:
        """
        Route query to appropriate warden.

        Args:
            query_id: ID of query to route
        """
        query = self.active_queries[query_id]

        try:
            # Determine target warden
            if query.folder_path:
                # Check for existing warden for this folder
                warden_id = self._find_warden_for_folder(query.folder_path)

                if warden_id:
                    # Route to existing warden
                    query.assigned_warden = warden_id
                    query.status = QueryStatus.ROUTED
                    self.logger.info(f"Routed query {query_id} to warden {warden_id}")
                else:
                    # Use dynamic warden tool for unclassified folder
                    query.assigned_warden = "dynamic_tool"
                    query.status = QueryStatus.UNCLASSIFIED
                    self.logger.info(
                        f"Using dynamic warden tool for unclassified folder: {query.folder_path}"
                    )

                    # Update dynamic warden tracking
                    self.dynamic_warden_tool.process_unclassified_folder(
                        query.folder_path
                    )
            else:
                # General query - handle with BASE AI
                query.assigned_warden = "base_ai"
                query.status = QueryStatus.ROUTED
                self.logger.info(f"Routed general query {query_id} to BASE AI")

            # Update registry with query metrics
            self._update_query_metrics()

        except Exception as e:
            query.status = QueryStatus.FAILED
            query.error = str(e)
            self.logger.error(f"Failed to route query {query_id}: {e}")

    def _find_warden_for_folder(self, folder_path: str) -> Optional[str]:
        """
        Find warden responsible for a folder.

        Args:
            folder_path: Path to folder

        Returns:
            Warden ID or None if no warden found
        """
        # Normalize path
        normalized_path = str(Path(folder_path).resolve())

        # Check permanent wardens
        for warden_id, warden_data in self.registry.get("wardens", {}).items():
            warden_path = warden_data.get("folder_path")
            if warden_path and normalized_path.startswith(
                str(Path(warden_path).resolve())
            ):
                return warden_id

        # Check temporary wardens
        temp_wardens = self.registry.get("dynamic_wardens", {}).get(
            "temporary_wardens", {}
        )
        for warden_id, warden_data in temp_wardens.items():
            warden_path = warden_data.get("folder_path")
            if warden_path and normalized_path.startswith(
                str(Path(warden_path).resolve())
            ):
                return warden_id

        return None

    def _update_query_metrics(self) -> None:
        """Update system metrics in registry."""
        total_queries = len(self.query_history) + len(self.active_queries)

        updates = {
            "system_metrics": {
                "total_queries": total_queries,
                "last_registry_update": datetime.now(timezone.utc).isoformat(),
            }
        }

        self.registry = self.registry_manager.update_registry(updates)

    def get_query_status(self, query_id: str) -> Optional[Dict]:
        """
        Get status of a query.

        Args:
            query_id: Query ID

        Returns:
            Query status dictionary or None if not found
        """
        if query_id in self.active_queries:
            return self.active_queries[query_id].to_dict()
        return None

    def perform_health_check(self) -> Dict:
        """
        Perform comprehensive health check of the system.

        Returns:
            Health check results
        """
        self.logger.info("Performing health check")

        health_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "overall_status": HealthStatus.HEALTHY.value,
            "issues": [],
        }

        try:
            # 1. Check registry integrity
            registry_health = self.registry_manager.verify_integrity()
            health_results["components"]["registry"] = registry_health

            if registry_health["status"] != "healthy":
                health_results["issues"].append(
                    f"Registry: {registry_health.get('error', 'Unknown issue')}"
                )
                health_results["overall_status"] = HealthStatus.DEGRADED.value

            # 2. Check Ollama availability
            ollama_health = self._check_ollama_health()
            health_results["components"]["ollama"] = ollama_health

            if not ollama_health["available"]:
                health_results["issues"].append("Ollama service not available")
                health_results["overall_status"] = HealthStatus.FAILED.value

            # 3. Check BASE AI model availability
            base_ai_model = self.registry.get("base_ai", {}).get("model")
            if base_ai_model:
                model_health = self._check_model_health(base_ai_model)
                health_results["components"]["base_ai_model"] = model_health

                if not model_health["available"]:
                    health_results["issues"].append(
                        f"BASE AI model {base_ai_model} not available"
                    )
                    health_results["overall_status"] = HealthStatus.DEGRADED.value

            # 4. Check disk space
            disk_health = self._check_disk_space()
            health_results["components"]["disk"] = disk_health

            if disk_health.get("free_gb", 0) < 10:
                health_results["issues"].append(
                    f"Low disk space: {disk_health.get('free_gb')} GB free"
                )
                health_results["overall_status"] = HealthStatus.DEGRADED.value

            # 5. Check backup system
            backup_files = self.registry_manager.get_backup_files()
            health_results["components"]["backups"] = {
                "count": len(backup_files),
                "latest": backup_files[0] if backup_files else None,
            }

            if len(backup_files) == 0:
                health_results["issues"].append("No backup files found")

            # Update registry with health check results
            self.registry = self.registry_manager.update_base_ai(
                {
                    "last_health_check": health_results["timestamp"],
                    "health_status": health_results["overall_status"],
                }
            )

            self.last_health_check = datetime.now(timezone.utc)
            self.health_status = HealthStatus(health_results["overall_status"])

            self.logger.info(
                f"Health check completed: {health_results['overall_status']}"
            )

        except Exception as e:
            health_results["overall_status"] = HealthStatus.FAILED.value
            health_results["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")

        return health_results

    def _check_ollama_health(self) -> Dict:
        """Check if Ollama service is available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "available": result.returncode == 0,
                "version": self._extract_ollama_version(result.stdout),
                "models_count": len(result.stdout.strip().split("\n")) - 1
                if result.stdout
                else 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _extract_ollama_version(self, output: str) -> Optional[str]:
        """Extract Ollama version from output."""
        try:
            # Try to get version from ollama --version
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def _check_model_health(self, model_name: str) -> Dict:
        """Check if a specific model is available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            available = model_name in result.stdout if result.stdout else False

            return {
                "available": available,
                "model_name": model_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "available": False,
                "model_name": model_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _check_disk_space(self) -> Dict:
        """Check available disk space."""
        try:
            if sys.platform == "win32":
                import ctypes

                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p("C:\\"),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes),
                )

                free_gb = free_bytes.value / (1024**3)
                total_gb = total_bytes.value / (1024**3)
                used_gb = total_gb - free_gb
                usage_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0

            else:
                # Linux/Mac
                import os

                stat = os.statvfs("/")
                free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
                used_gb = total_gb - free_gb
                usage_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0

            return {
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "usage_percent": round(usage_percent, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
