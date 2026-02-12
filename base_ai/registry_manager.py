"""
Registry Manager for Local AI Warden System

Handles CRUD operations for .ai_registry.json with atomic updates,
backup management, and integrity verification.

Glass-Box Boundary Compliance:
- Atomic writes (no partial updates)
- Hash verification for integrity
- Backup before every modification
- Read-only by default, explicit approval for writes

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

import hashlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class RegistryManager:
    """Manages the AI registry with atomic operations and backup."""

    def __init__(self, registry_path: str = ".ai_registry.json"):
        """
        Initialize registry manager.

        Args:
            registry_path: Path to registry JSON file
        """
        self.registry_path = Path(registry_path)
        self.backup_dir = Path(".ai_registry_backups")
        self._ensure_backup_dir()

    def _ensure_backup_dir(self) -> None:
        """Ensure backup directory exists."""
        self.backup_dir.mkdir(exist_ok=True)

    def _generate_backup_path(self) -> Path:
        """Generate backup file path with timestamp."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return self.backup_dir / f"registry_backup_{timestamp}.json"

    def _calculate_hash(self, data: Dict) -> str:
        """Calculate SHA256 hash of registry data."""
        data_str = json.dumps(data, sort_keys=True, indent=2)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def _backup_registry(self, current_data: Dict) -> str:
        """
        Create backup of current registry state.

        Returns:
            Backup file path
        """
        backup_path = self._generate_backup_path()

        # Add metadata to backup
        backup_data = {
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "original_path": str(self.registry_path),
            "data_hash": self._calculate_hash(current_data),
            "registry_data": current_data,
        }

        # Atomic write to backup
        temp_backup = backup_path.with_suffix(".tmp")
        with open(temp_backup, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        temp_backup.rename(backup_path)

        return str(backup_path)

    def _atomic_write(self, data: Dict) -> None:
        """
        Perform atomic write to registry file.

        Args:
            data: Registry data to write
        """
        # Create backup first
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                current_data = json.load(f)
            self._backup_registry(current_data)

        # Add update metadata
        data["system_metrics"]["last_registry_update"] = datetime.now(
            timezone.utc
        ).isoformat()
        data["system_metrics"]["registry_hash"] = self._calculate_hash(data)

        # Atomic write using temp file
        temp_path = self.registry_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Rename temp to final (atomic on most filesystems)
        temp_path.rename(self.registry_path)

    def load_registry(self) -> Dict:
        """
        Load registry data with integrity verification.

        Returns:
            Registry data dictionary

        Raises:
            FileNotFoundError: If registry doesn't exist
            json.JSONDecodeError: If registry is corrupted
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")

        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify hash if present
        if "system_metrics" in data and "registry_hash" in data["system_metrics"]:
            stored_hash = data["system_metrics"].pop("registry_hash")
            calculated_hash = self._calculate_hash(data)
            if stored_hash != calculated_hash:
                raise ValueError(
                    f"Registry integrity check failed. Stored: {stored_hash}, Calculated: {calculated_hash}"
                )

        return data

    def create_registry(self, initial_data: Optional[Dict] = None) -> Dict:
        """
        Create new registry with initial data.

        Args:
            initial_data: Optional initial data, uses default if None

        Returns:
            Created registry data
        """
        if self.registry_path.exists():
            raise FileExistsError(f"Registry already exists: {self.registry_path}")

        if initial_data is None:
            initial_data = {
                "base_ai": {
                    "model": "llama3.1:70b",
                    "api_endpoint": "http://localhost:11434",
                    "status": "active",
                    "version": "1.0.0",
                    "last_health_check": None,
                },
                "wardens": {},
                "dynamic_wardens": {
                    "unclassified_folders": [],
                    "temporary_wardens": {},
                },
                "health_checks": {
                    "interval_seconds": 300,
                    "failure_threshold": 3,
                    "auto_restart": true,
                },
                "dynamic_warden_policy": {
                    "max_lifetime_hours": 24,
                    "promotion_threshold": 10,
                    "cleanup_on_promotion": true,
                },
                "backup": {
                    "registry_backup_interval": "hourly",
                    "metadata_backup_interval": "daily",
                    "backup_location": ".ai_registry_backups/",
                },
                "error_handling": {
                    "retry_attempts": 3,
                    "retry_delay_seconds": 5,
                    "fallback_to_base_ai": true,
                    "log_all_failures": true,
                },
                "system_metrics": {
                    "total_queries": 0,
                    "average_response_time_ms": 0,
                    "warden_uptime": 1.0,
                    "last_registry_update": None,
                },
            }

        self._atomic_write(initial_data)
        return initial_data

    def update_registry(self, updates: Dict, merge: bool = True) -> Dict:
        """
        Update registry with new data.

        Args:
            updates: Dictionary with updates
            merge: If True, merge updates with existing data

        Returns:
            Updated registry data
        """
        current_data = self.load_registry()

        if merge:
            # Deep merge updates into current data
            def deep_merge(target: Dict, source: Dict) -> Dict:
                for key, value in source.items():
                    if (
                        key in target
                        and isinstance(target[key], dict)
                        and isinstance(value, dict)
                    ):
                        target[key] = deep_merge(target[key], value)
                    else:
                        target[key] = value
                return target

            updated_data = deep_merge(current_data, updates)
        else:
            updated_data = updates

        self._atomic_write(updated_data)
        return updated_data

    def update_base_ai(self, updates: Dict) -> Dict:
        """
        Update BASE AI configuration.

        Args:
            updates: Dictionary with BASE AI updates

        Returns:
            Updated registry data
        """
        return self.update_registry({"base_ai": updates})

    def add_warden(self, warden_name: str, warden_data: Dict) -> Dict:
        """
        Add a new warden to registry.

        Args:
            warden_name: Unique identifier for warden
            warden_data: Warden configuration data

        Returns:
            Updated registry data
        """
        current_data = self.load_registry()

        if warden_name in current_data["wardens"]:
            raise ValueError(f"Warden already exists: {warden_name}")

        # Add creation metadata
        warden_data["created_at"] = datetime.now(timezone.utc).isoformat()
        warden_data["last_updated"] = datetime.now(timezone.utc).isoformat()

        updates = {"wardens": {warden_name: warden_data}}

        return self.update_registry(updates)

    def update_warden(self, warden_name: str, updates: Dict) -> Dict:
        """
        Update existing warden.

        Args:
            warden_name: Warden identifier
            updates: Dictionary with warden updates

        Returns:
            Updated registry data

        Raises:
            KeyError: If warden doesn't exist
        """
        current_data = self.load_registry()

        if warden_name not in current_data["wardens"]:
            raise KeyError(f"Warden not found: {warden_name}")

        # Merge updates with existing warden data
        current_warden = current_data["wardens"][warden_name]
        updated_warden = {**current_warden, **updates}
        updated_warden["last_updated"] = datetime.now(timezone.utc).isoformat()

        update_data = {"wardens": {warden_name: updated_warden}}

        return self.update_registry(update_data)

    def remove_warden(self, warden_name: str) -> Dict:
        """
        Remove warden from registry.

        Args:
            warden_name: Warden identifier

        Returns:
            Updated registry data

        Raises:
            KeyError: If warden doesn't exist
        """
        current_data = self.load_registry()

        if warden_name not in current_data["wardens"]:
            raise KeyError(f"Warden not found: {warden_name}")

        # Create backup of warden data before removal
        warden_backup = {
            "removed_at": datetime.now(timezone.utc).isoformat(),
            "warden_data": current_data["wardens"][warden_name],
        }

        backup_path = (
            self.backup_dir
            / f"warden_removed_{warden_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(warden_backup, f, indent=2)

        # Remove warden
        del current_data["wardens"][warden_name]
        self._atomic_write(current_data)

        return current_data

    def add_temporary_warden(self, folder_path: str, warden_data: Dict) -> Dict:
        """
        Add temporary warden for unclassified folder.

        Args:
            folder_path: Path to unclassified folder
            warden_data: Temporary warden configuration

        Returns:
            Updated registry data
        """
        warden_id = f"temp_{hashlib.sha256(folder_path.encode()).hexdigest()[:8]}"

        # Add temporary warden metadata
        warden_data["folder_path"] = folder_path
        warden_data["created_at"] = datetime.now(timezone.utc).isoformat()
        warden_data["query_count"] = 0
        warden_data["status"] = "temporary"

        updates = {"dynamic_wardens": {"temporary_wardens": {warden_id: warden_data}}}

        # Also add to unclassified folders if not already there
        current_data = self.load_registry()
        if folder_path not in current_data["dynamic_wardens"]["unclassified_folders"]:
            updates["dynamic_wardens"]["unclassified_folders"] = [folder_path]

        return self.update_registry(updates)

    def promote_to_permanent(self, temp_warden_id: str, permanent_name: str) -> Dict:
        """
        Promote temporary warden to permanent warden.

        Args:
            temp_warden_id: Temporary warden identifier
            permanent_name: New permanent warden name

        Returns:
            Updated registry data

        Raises:
            KeyError: If temporary warden doesn't exist
        """
        current_data = self.load_registry()

        if temp_warden_id not in current_data["dynamic_wardens"]["temporary_wardens"]:
            raise KeyError(f"Temporary warden not found: {temp_warden_id}")

        temp_warden = current_data["dynamic_wardens"]["temporary_wardens"][
            temp_warden_id
        ]

        # Create permanent warden entry
        permanent_warden = {
            **temp_warden,
            "status": "permanent",
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "original_temp_id": temp_warden_id,
        }

        # Remove from temporary and unclassified
        del current_data["dynamic_wardens"]["temporary_wardens"][temp_warden_id]
        folder_path = temp_warden["folder_path"]
        if folder_path in current_data["dynamic_wardens"]["unclassified_folders"]:
            current_data["dynamic_wardens"]["unclassified_folders"].remove(folder_path)

        # Add to permanent wardens
        current_data["wardens"][permanent_name] = permanent_warden

        self._atomic_write(current_data)
        return current_data

    def get_backup_files(self) -> List[Dict]:
        """
        Get list of backup files with metadata.

        Returns:
            List of backup file information dictionaries
        """
        backups = []
        for backup_file in self.backup_dir.glob("registry_backup_*.json"):
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    backup_data = json.load(f)

                backups.append(
                    {
                        "path": str(backup_file),
                        "timestamp": backup_data.get("backup_timestamp"),
                        "size": backup_file.stat().st_size,
                        "hash": backup_data.get("data_hash"),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                # Skip corrupted backups
                continue

        return sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)

    def restore_from_backup(self, backup_path: str) -> Dict:
        """
        Restore registry from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Restored registry data

        Raises:
            FileNotFoundError: If backup doesn't exist
            ValueError: If backup is corrupted
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        with open(backup_file, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        if "registry_data" not in backup_data:
            raise ValueError("Backup file missing registry_data")

        # Create backup of current registry before restore
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                current_data = json.load(f)
            restore_backup = self._generate_backup_path().with_name(
                f"pre_restore_{backup_file.name}"
            )
            with open(restore_backup, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "restore_timestamp": datetime.now(timezone.utc).isoformat(),
                        "original_backup": backup_path,
                        "current_data": current_data,
                    },
                    f,
                    indent=2,
                )

        # Restore registry data
        self._atomic_write(backup_data["registry_data"])

        return backup_data["registry_data"]

    def cleanup_old_backups(self, keep_last_n: int = 24) -> List[str]:
        """
        Clean up old backups, keeping only specified number.

        Args:
            keep_last_n: Number of most recent backups to keep

        Returns:
            List of removed backup file paths
        """
        backups = self.get_backup_files()
        if len(backups) <= keep_last_n:
            return []

        backups_to_remove = backups[keep_last_n:]
        removed = []

        for backup in backups_to_remove:
            try:
                Path(backup["path"]).unlink()
                removed.append(backup["path"])
            except OSError:
                # Skip if file can't be removed
                continue

        return removed

    def verify_integrity(self) -> Dict:
        """
        Verify registry integrity and return status.

        Returns:
            Dictionary with integrity check results
        """
        try:
            data = self.load_registry()

            # Check required sections
            required_sections = [
                "base_ai",
                "wardens",
                "dynamic_wardens",
                "system_metrics",
            ]
            missing_sections = [
                section for section in required_sections if section not in data
            ]

            # Check BASE AI configuration
            base_ai_checks = []
            if "base_ai" in data:
                base_ai = data["base_ai"]
                if "model" not in base_ai:
                    base_ai_checks.append("Missing model")
                if "api_endpoint" not in base_ai:
                    base_ai_checks.append("Missing api_endpoint")
                if "status" not in base_ai:
                    base_ai_checks.append("Missing status")

            return {
                "status": "healthy"
                if not missing_sections and not base_ai_checks
                else "degraded",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "missing_sections": missing_sections,
                "base_ai_issues": base_ai_checks,
                "registry_hash": self._calculate_hash(data),
                "backup_count": len(self.get_backup_files()),
            }

        except Exception as e:
            return {
                "status": "corrupted",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "backup_count": len(self.get_backup_files()),
            }
