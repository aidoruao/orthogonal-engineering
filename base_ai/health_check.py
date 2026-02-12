"""
Health Check Script for Local AI Warden System

Performs comprehensive health checks:
1. Registry integrity verification
2. Ollama service availability
3. Model availability check
4. Disk space monitoring
5. Backup system verification
6. Dynamic warden cleanup

Designed to be run periodically (every 5 minutes) or on-demand.
Glass-Box Boundary compliant with trace generation.

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_ai.registry_manager import RegistryManager


class HealthChecker:
    """Comprehensive health checker for Local AI Warden System."""

    def __init__(self, registry_path: str = ".ai_registry.json"):
        """
        Initialize health checker.

        Args:
            registry_path: Path to registry JSON file
        """
        self.registry_path = Path(registry_path)
        self.registry_manager = RegistryManager(registry_path)
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = Path("logs") / "health_checks"
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("health_checker")
        logger.setLevel(logging.INFO)

        # File handler
        log_file = log_dir / f"health_{datetime.now().strftime('%Y%m%d')}.log"
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

    def run_comprehensive_check(self) -> Dict:
        """
        Run comprehensive health check.

        Returns:
            Health check results dictionary
        """
        self.logger.info("Starting comprehensive health check")

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "components": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # 1. Check registry integrity
            registry_results = self.check_registry_integrity()
            results["components"]["registry"] = registry_results

            if registry_results["status"] != "healthy":
                results["issues"].append(
                    f"Registry: {registry_results.get('error', 'Unknown issue')}"
                )
                results["overall_status"] = "degraded"

            # 2. Check Ollama service
            ollama_results = self.check_ollama_service()
            results["components"]["ollama"] = ollama_results

            if not ollama_results["available"]:
                results["issues"].append("Ollama service not available")
                results["overall_status"] = "failed"
                results["recommendations"].append(
                    "Start Ollama service: 'ollama serve'"
                )

            # 3. Check required models
            models_results = self.check_required_models()
            results["components"]["models"] = models_results

            missing_models = models_results.get("missing_models", [])
            if missing_models:
                results["issues"].append(f"Missing models: {', '.join(missing_models)}")
                results["overall_status"] = "degraded"
                for model in missing_models:
                    results["recommendations"].append(
                        f"Pull missing model: 'ollama pull {model}'"
                    )

            # 4. Check disk space
            disk_results = self.check_disk_space()
            results["components"]["disk"] = disk_results

            free_gb = disk_results.get("free_gb", 0)
            if free_gb < 10:
                results["issues"].append(f"Low disk space: {free_gb} GB free")
                results["overall_status"] = "degraded"
                results["recommendations"].append("Free up disk space or add storage")

            # 5. Check backup system
            backup_results = self.check_backup_system()
            results["components"]["backup"] = backup_results

            if backup_results.get("backup_count", 0) == 0:
                results["issues"].append("No backup files found")
                results["recommendations"].append("Perform initial registry backup")

            # 6. Check dynamic warden cleanup
            cleanup_results = self.check_dynamic_warden_cleanup()
            results["components"]["dynamic_warden_cleanup"] = cleanup_results

            expired_count = cleanup_results.get("expired_temporary_wardens", 0)
            if expired_count > 0:
                results["issues"].append(
                    f"{expired_count} expired temporary wardens need cleanup"
                )
                results["recommendations"].append(
                    "Run cleanup: 'python health_check.py --cleanup'"
                )

            # 7. Update registry with health check results
            self._update_registry_health(results)

            # 8. Generate trace
            self._generate_health_trace(results)

            self.logger.info(f"Health check completed: {results['overall_status']}")

        except Exception as e:
            results["overall_status"] = "failed"
            results["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")

        return results

    def check_registry_integrity(self) -> Dict:
        """Check registry file integrity."""
        try:
            integrity = self.registry_manager.verify_integrity()
            return integrity
        except Exception as e:
            return {
                "status": "corrupted",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def check_ollama_service(self) -> Dict:
        """Check if Ollama service is running and accessible."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Try to get version
            version = None
            try:
                version_result = subprocess.run(
                    ["ollama", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if version_result.returncode == 0:
                    version = version_result.stdout.strip()
            except:
                pass

            # Count models
            models_count = 0
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                models_count = len(lines) - 1 if len(lines) > 1 else 0

            return {
                "available": result.returncode == 0,
                "version": version,
                "models_count": models_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def check_required_models(self) -> Dict:
        """Check if required models are available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return {
                    "available": False,
                    "error": "Failed to list models",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            installed_models = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        installed_models.append(parts[0])

            # Define required models for Phase 1
            required_models = [
                "llama3.2:latest",  # For automation warden
                "mistral:7b",  # For documentation warden
                "codellama:7b",  # For toolkit warden
                "qwen2.5:7b",  # For logs warden
                "gemma3:1b",  # For dynamic warden tool
            ]

            missing_models = []
            available_models = []

            for model in required_models:
                # Check if model or any variant is installed
                model_found = False
                for installed in installed_models:
                    if model in installed or installed in model:
                        model_found = True
                        available_models.append(model)
                        break

                if not model_found:
                    missing_models.append(model)

            return {
                "available": len(missing_models) == 0,
                "installed_models": installed_models,
                "required_models": required_models,
                "available_models": available_models,
                "missing_models": missing_models,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def check_disk_space(self) -> Dict:
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

    def check_backup_system(self) -> Dict:
        """Check backup system status."""
        try:
            backup_files = self.registry_manager.get_backup_files()

            latest_backup = None
            if backup_files:
                latest_backup = backup_files[0]

            # Check backup age
            backup_age_hours = None
            if latest_backup and latest_backup.get("timestamp"):
                backup_time = datetime.fromisoformat(
                    latest_backup["timestamp"].replace("Z", "+00:00")
                )
                backup_age_hours = (
                    datetime.now(timezone.utc) - backup_time
                ).total_seconds() / 3600

            return {
                "backup_count": len(backup_files),
                "latest_backup": latest_backup,
                "backup_age_hours": round(backup_age_hours, 2)
                if backup_age_hours
                else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def check_dynamic_warden_cleanup(self) -> Dict:
        """Check for expired temporary wardens that need cleanup."""
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

            return {
                "temporary_warden_count": len(temp_wardens),
                "expired_temporary_wardens": len(expired_wardens),
                "expired_wardens": expired_wardens,
                "max_lifetime_hours": max_lifetime_hours,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def cleanup_expired_wardens(self) -> Dict:
        """Clean up expired temporary wardens."""
        try:
            cleanup_results = self.check_dynamic_warden_cleanup()
            expired_wardens = cleanup_results.get("expired_wardens", [])

            cleaned = []
            failed = []

            for warden_info in expired_wardens:
                warden_id = warden_info["warden_id"]
                try:
                    # Remove from registry
                    registry = self.registry_manager.load_registry()

                    if warden_id in registry.get("dynamic_wardens", {}).get(
                        "temporary_wardens", {}
                    ):
                        del registry["dynamic_wardens"]["temporary_wardens"][warden_id]

                        # Also remove from unclassified folders if present
                        folder_path = warden_info["folder_path"]
                        if folder_path in registry["dynamic_wardens"].get(
                            "unclassified_folders", []
                        ):
                            registry["dynamic_wardens"]["unclassified_folders"].remove(
                                folder_path
                            )

                        self.registry_manager._atomic_write(registry)
                        cleaned.append(warden_id)
                        self.logger.info(f"Cleaned up expired warden: {warden_id}")

                except Exception as e:
                    failed.append({"warden_id": warden_id, "error": str(e)})
                    self.logger.error(f"Failed to clean up warden {warden_id}: {e}")

            return {
                "cleaned_count": len(cleaned),
                "failed_count": len(failed),
                "cleaned_wardens": cleaned,
                "failed_wardens": failed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _update_registry_health(self, health_results: Dict) -> None:
        """Update registry with health check results."""
        try:
            updates = {
                "base_ai": {
                    "last_health_check": health_results["timestamp"],
                    "health_status": health_results["overall_status"],
                },
                "system_metrics": {
                    "last_health_check": health_results["timestamp"],
                    "health_status": health_results["overall_status"],
                },
            }

            self.registry_manager.update_registry(updates)

        except Exception as e:
            self.logger.error(f"Failed to update registry with health results: {e}")

    def _generate_health_trace(self, health_results: Dict) -> str:
        """Generate Glass-Box compliant trace for health check."""
        try:
            trace_id = f"HEALTH-TRACE-{hashlib.sha256(json.dumps(health_results, sort_keys=True).encode()).hexdigest()[:8].upper()}"

            trace = {
                "trace_id": trace_id,
                "operation": "health_check",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": health_results,
            }

            # Save trace
            trace_dir = Path("logs") / "traces" / "health_checks"
            trace_dir.mkdir(parents=True, exist_ok=True)
            trace_file = trace_dir / f"{trace_id}.json"

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace, f, indent=2)

            self.logger.info(f"Generated health trace: {trace_id}")
            return trace_id

        except Exception as e:
            self.logger.error(f"Failed to generate health trace: {e}")
            return ""

    def print_results(self, results: Dict, verbose: bool = False) -> None:
        """Print health check results in readable format."""
        print("\n" + "=" * 60)
        print("LOCAL AI WARDEN SYSTEM - HEALTH CHECK REPORT")
        print("=" * 60)

        status = results.get("overall_status", "unknown").upper()
        status_color = {
            "HEALTHY": "\033[92m",  # Green
            "DEGRADED": "\033[93m",  # Yellow
            "FAILED": "\033[91m",  # Red
        }.get(status, "\033[0m")

        print(f"\nOverall Status: {status_color}{status}\033[0m")
        print(f"Timestamp: {results.get('timestamp', 'unknown')}")

        # Print component status
        components = results.get("components", {})
        if components:
            print(f"\nComponent Status ({len(components)} components):")
            for component, data in components.items():
                if isinstance(data, dict):
                    comp_status = data.get("status", "unknown")
                    comp_icon = (
                        "✅"
                        if comp_status == "healthy"
                        else "⚠️"
                        if comp_status == "degraded"
                        else "❌"
                    )
                    print(f"  {comp_icon} {component}: {comp_status}")

        # Print issues
        issues = results.get("issues", [])
        if issues:
            print(f"\nIssues Found ({len(issues)}):")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"  • {issue}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")

        # Print recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print(f"\nRecommendations ({len(recommendations)}):")
            for rec in recommendations[:5]:  # Show first 5 recommendations
                print(f"  • {rec}")
            if len(recommendations) > 5:
                print(f"  ... and {len(recommendations) - 5} more")

        # Verbose mode: show all details
        if verbose:
            print(f"\nDetailed Results:")
            print(json.dumps(results, indent=2, default=str))

        print("\n" + "=" * 60)
