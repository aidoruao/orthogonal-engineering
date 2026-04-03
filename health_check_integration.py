#!/usr/bin/env python3
"""
Health Check Integration for Phase 2 Wardens

This script integrates Phase 2 wardens into BASE AI health checks,
monitors warden health, and provides comprehensive health reporting.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

VALID_WARDEN_STATUSES = ["active", "pending", "error", "disabled"]
SECONDS_PER_HOUR = 3600


class HealthCheckIntegration:
    """Health check integration for Phase 2 wardens."""

    def __init__(self, registry_path: str = ".ai_registry.json"):
        """
        Initialize health check integration.

        Args:
            registry_path: Path to the AI registry JSON file
        """
        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.health_check_results = {}
        self.last_check_time = None
        self.health_check_interval = self.registry.get("health_checks", {}).get(
            "interval_seconds", 300
        )

    def _load_registry(self) -> Dict[str, Any]:
        """Load the AI registry."""
        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load AI registry: {e}")
            return {}

    def _save_registry(self):
        """Save the updated AI registry."""
        try:
            with open(self.registry_path, "w") as f:
                json.dump(self.registry, f, indent=2)
            logger.debug("Registry saved successfully")
        except Exception as e:
            logger.error(f"Failed to save AI registry: {e}")

    def _resolve_repo_path(self, path_value: Optional[str]) -> Optional[Path]:
        """Resolve a path relative to the registry location."""
        if not path_value:
            return None

        path = Path(path_value)
        if path.is_absolute():
            return path

        return Path(self.registry_path).resolve().parent / path

    def _elevate_status(self, current_status: str, candidate_status: str) -> str:
        """Return the more severe health status."""
        priority = {"healthy": 0, "warning": 1, "critical": 2}
        current_priority = priority.get(current_status, 0)
        candidate_priority = priority.get(candidate_status, 0)
        return candidate_status if candidate_priority > current_priority else current_status

    def _parse_iso_timestamp(self, timestamp_value: Optional[str]) -> Optional[datetime]:
        """Parse ISO timestamps with optional Z suffix."""
        if not timestamp_value:
            return None

        try:
            parsed = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _load_cloud_report(self, report_path: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[Path]]:
        """Load a cloud warden JSON report if present."""
        resolved_path = self._resolve_repo_path(report_path)
        if resolved_path is None or not resolved_path.exists():
            return None, resolved_path

        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                return json.load(f), resolved_path
        except Exception as e:
            logger.warning(f"Failed to load cloud warden report {resolved_path}: {e}")
            return None, resolved_path

    def _check_cloud_warden(
        self, warden_name: str, warden_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check health of a cloud warden that reports through workflow artifacts."""
        metadata = warden_config.get("metadata", {})
        health_config = warden_config.get("health", {})
        workflow_path = (
            warden_config.get("workflow_path")
            or metadata.get("workflow_path")
            or f".github/workflows/{warden_name}.yml"
        )
        report_path = (
            health_config.get("artifact_report_path")
            or metadata.get("artifact_report_path")
            or f"logs/health_checks/cloud_wardens/{warden_name}_status.json"
        )
        max_report_age_hours = health_config.get("max_report_age_hours", 36)

        health = {
            "warden_name": warden_name,
            "status": "healthy",
            "folder_path": warden_config.get("folder_path", "repo-wide"),
            "model_name": warden_config.get("model_name", "unknown"),
            "checks": {
                "runtime": warden_config.get("runtime", "unknown"),
                "workflow_path": workflow_path,
                "artifact_report_path": report_path,
            },
            "issues": [],
            "recommendations": [],
        }

        workflow_file = self._resolve_repo_path(workflow_path)
        workflow_exists = workflow_file is not None and workflow_file.exists()
        health["checks"]["workflow_exists"] = workflow_exists
        if not workflow_exists:
            health["status"] = "critical"
            health["issues"].append(f"Workflow not found: {workflow_path}")
            health["recommendations"].append(
                f"Create or restore workflow: {workflow_path}"
            )

        report, resolved_report_path = self._load_cloud_report(report_path)
        health["checks"]["report_exists"] = report is not None
        health["checks"]["resolved_report_path"] = (
            str(resolved_report_path) if resolved_report_path else None
        )

        if report is None:
            health["status"] = self._elevate_status(health["status"], "warning")
            health["issues"].append(f"Cloud report not found: {report_path}")
            health["recommendations"].append(
                "Run the cloud warden workflow or download its latest artifact locally"
            )
        else:
            report_status = report.get("status", "healthy")
            findings = report.get("findings", [])
            report_timestamp = self._parse_iso_timestamp(
                report.get("timestamp")
                or report.get("completed_at")
                or report.get("scan", {}).get("timestamp")
            )

            health["checks"]["report_status"] = report_status
            health["checks"]["finding_count"] = len(findings)
            health["checks"]["last_report_timestamp"] = (
                report_timestamp.isoformat() if report_timestamp else None
            )

            if report_timestamp is None:
                health["status"] = self._elevate_status(health["status"], "warning")
                health["issues"].append("Cloud report timestamp missing or invalid")
            else:
                report_age = datetime.now(timezone.utc) - report_timestamp
                report_age_in_hours = report_age.total_seconds() / SECONDS_PER_HOUR
                health["checks"]["report_age_hours"] = round(report_age_in_hours, 3)
                health["checks"]["report_fresh"] = (
                    report_age <= timedelta(hours=max_report_age_hours)
                )

                if not health["checks"]["report_fresh"]:
                    health["status"] = self._elevate_status(health["status"], "warning")
                    health["issues"].append(
                        f"Cloud report is stale ({report_age_in_hours:.1f}h old)"
                    )
                    health["recommendations"].append(
                        "Re-run the cloud warden workflow to refresh its status artifact"
                    )

            if report_status in {"warning", "degraded"}:
                health["status"] = self._elevate_status(health["status"], "warning")
            elif report_status in {"critical", "error", "failed"}:
                health["status"] = self._elevate_status(health["status"], "critical")

            for issue in report.get("issues", []):
                if issue not in health["issues"]:
                    health["issues"].append(issue)

            for recommendation in report.get("recommendations", []):
                if recommendation not in health["recommendations"]:
                    health["recommendations"].append(recommendation)

        warden_status = warden_config.get("status", "unknown")
        health["checks"]["warden_status"] = warden_status
        if warden_status not in VALID_WARDEN_STATUSES:
            health["status"] = self._elevate_status(health["status"], "warning")
            health["issues"].append(
                f"Warden status '{warden_status}' is not a valid status"
            )
        elif warden_status != "active":
            health["status"] = self._elevate_status(health["status"], "warning")
            health["issues"].append(
                f"Warden status is '{warden_status}', should be 'active' for optimal operation"
            )

        health["checks"]["last_query"] = health_config.get("last_query")
        health["checks"]["response_time_ms"] = health_config.get("response_time_ms")
        health["checks"]["success_rate"] = health_config.get("success_rate")

        if "health" in warden_config:
            warden_config["health"]["last_health_check"] = datetime.now(
                timezone.utc
            ).isoformat()
            if report is not None:
                warden_config["health"]["last_artifact_timestamp"] = (
                    report.get("timestamp")
                    or report.get("completed_at")
                    or report.get("scan", {}).get("timestamp")
                )

        return health

    def run_health_checks(self) -> Dict[str, Any]:
        """
        Run comprehensive health checks for all wardens.

        Returns:
            Dictionary with health check results
        """
        start_time = time.time()
        self.last_check_time = datetime.now().isoformat()

        logger.info("Starting comprehensive health checks for Phase 2 wardens")

        # Initialize results structure
        results = {
            "timestamp": self.last_check_time,
            "overall_health": "healthy",
            "wardens": {},
            "base_ai": {},
            "dynamic_wardens": {},
            "system_metrics": {},
            "issues": [],
            "recommendations": [],
        }

        # Check BASE AI
        base_ai_health = self._check_base_ai()
        results["base_ai"] = base_ai_health
        if base_ai_health["status"] != "healthy":
            results["overall_health"] = "degraded"
            results["issues"].append(f"BASE AI: {base_ai_health['status']}")

        # Check Phase 2 wardens
        warden_results = {}
        for warden_name, warden_config in self.registry.get("wardens", {}).items():
            warden_health = self._check_warden(warden_name, warden_config)
            warden_results[warden_name] = warden_health

            # Update overall health based on warden status
            if warden_health["status"] == "critical":
                results["overall_health"] = "critical"
                results["issues"].append(f"{warden_name}: {warden_health['status']}")
            elif (
                warden_health["status"] == "warning"
                and results["overall_health"] == "healthy"
            ):
                results["overall_health"] = "warning"

        results["wardens"] = warden_results

        # Check dynamic wardens
        dynamic_warden_health = self._check_dynamic_wardens()
        results["dynamic_wardens"] = dynamic_warden_health
        if dynamic_warden_health["status"] != "healthy":
            if results["overall_health"] == "healthy":
                results["overall_health"] = "warning"
            results["issues"].append(
                f"Dynamic wardens: {dynamic_warden_health['status']}"
            )

        # Update system metrics
        system_metrics = self._update_system_metrics(results)
        results["system_metrics"] = system_metrics

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        # Update registry with health check results
        self._update_registry_health(results)

        # Save health check results
        self._save_health_check_results(results)

        check_duration = time.time() - start_time
        results["check_duration_seconds"] = check_duration

        logger.info(f"Health checks completed in {check_duration:.2f}s")
        logger.info(f"Overall health: {results['overall_health']}")

        return results

    def _check_base_ai(self) -> Dict[str, Any]:
        """Check BASE AI health."""
        base_ai_config = self.registry.get("base_ai", {})

        health = {
            "status": "healthy",
            "model": base_ai_config.get("model", "unknown"),
            "api_endpoint": base_ai_config.get("api_endpoint", "unknown"),
            "version": base_ai_config.get("version", "unknown"),
            "last_health_check": base_ai_config.get("last_health_check"),
            "checks": {},
            "issues": [],
        }

        # Check if BASE AI configuration exists
        if not base_ai_config:
            health["status"] = "critical"
            health["issues"].append("BASE AI configuration missing")
            return health

        # Check model configuration
        if not base_ai_config.get("model"):
            health["status"] = "warning"
            health["issues"].append("BASE AI model not specified")

        # Check API endpoint
        api_endpoint = base_ai_config.get("api_endpoint")
        if not api_endpoint:
            health["status"] = "critical"
            health["issues"].append("API endpoint not specified")
        elif not api_endpoint.startswith(("http://", "https://")):
            health["status"] = "warning"
            health["issues"].append(
                f"API endpoint format may be invalid: {api_endpoint}"
            )

        # Update last health check time
        self.registry["base_ai"]["last_health_check"] = datetime.now().isoformat()

        return health

    def _check_warden(
        self, warden_name: str, warden_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check health of a specific warden."""
        if warden_config.get("runtime") == "github_actions":
            return self._check_cloud_warden(warden_name, warden_config)

        health = {
            "warden_name": warden_name,
            "status": "healthy",
            "folder_path": warden_config.get("folder_path", "unknown"),
            "model_name": warden_config.get("model_name", "unknown"),
            "checks": {},
            "issues": [],
            "recommendations": [],
        }

        metadata = warden_config.get("metadata", {})
        monitored_paths = metadata.get("monitored_paths") or []
        resolved_paths = []
        if monitored_paths:
            for path_value in monitored_paths:
                resolved = self._resolve_repo_path(path_value)
                if resolved is not None:
                    resolved_paths.append(resolved)
        else:
            folder_path = warden_config.get("folder_path")
            resolved = self._resolve_repo_path(folder_path)
            if resolved is not None:
                resolved_paths.append(resolved)

        # Check folder existence and accessibility
        if not resolved_paths:
            health["status"] = "critical"
            health["issues"].append("Folder path not specified")
            return health

        path_checks = []
        folder_exists = True
        folder_readable = True
        for resolved_path in resolved_paths:
            exists = resolved_path.exists()
            readable = os.access(resolved_path, os.R_OK) if exists else False
            path_checks.append(
                {
                    "path": str(resolved_path),
                    "exists": exists,
                    "readable": readable,
                }
            )
            folder_exists = folder_exists and exists
            folder_readable = folder_readable and readable

        health["checks"]["path_checks"] = path_checks
        health["checks"]["folder_exists"] = folder_exists
        health["checks"]["folder_readable"] = folder_readable

        if not folder_exists:
            health["status"] = "critical"
            missing_paths = [check["path"] for check in path_checks if not check["exists"]]
            health["issues"].append(f"Folder not found: {', '.join(missing_paths)}")
            health["recommendations"].append(f"Create folder(s): {', '.join(missing_paths)}")
        else:
            if not folder_readable:
                health["status"] = "critical"
                unreadable_paths = [
                    check["path"] for check in path_checks if not check["readable"]
                ]
                health["issues"].append(
                    f"Folder not readable: {', '.join(unreadable_paths)}"
                )
                health["recommendations"].append(
                    f"Check folder permissions: {', '.join(unreadable_paths)}"
                )

            # Check file count consistency
            stored_file_count = metadata.get("file_count")

            if stored_file_count is not None:
                try:
                    actual_file_count = sum(
                        self._count_files(str(resolved_path))
                        for resolved_path in resolved_paths
                    )
                    health["checks"]["file_count"] = actual_file_count
                    health["checks"]["stored_file_count"] = stored_file_count
                    health["checks"]["file_count_match"] = (
                        actual_file_count == stored_file_count
                    )

                    if actual_file_count != stored_file_count:
                        health["status"] = "warning"
                        health["issues"].append(
                            f"File count mismatch: stored={stored_file_count}, actual={actual_file_count}"
                        )
                        health["recommendations"].append(
                            f"Run scan for {warden_name} to update file count"
                        )
                except Exception as e:
                    health["status"] = "warning"
                    health["issues"].append(f"Could not count files: {e}")

        # Check warden status
        warden_status = warden_config.get("status", "unknown")
        health["checks"]["warden_status"] = warden_status

        if warden_status not in VALID_WARDEN_STATUSES:
            if health["status"] == "healthy":
                health["status"] = "warning"
            health["issues"].append(
                f"Warden status '{warden_status}' is not a valid status"
            )
        elif warden_status != "active":
            if health["status"] == "healthy":
                health["status"] = "warning"
            health["issues"].append(
                f"Warden status is '{warden_status}', should be 'active' for optimal operation"
            )

        # Check health metrics
        warden_health = warden_config.get("health", {})
        health["checks"]["last_query"] = warden_health.get("last_query")
        health["checks"]["response_time_ms"] = warden_health.get("response_time_ms")
        health["checks"]["success_rate"] = warden_health.get("success_rate")

        # Update last health check time
        if "health" in warden_config:
            warden_config["health"]["last_health_check"] = datetime.now().isoformat()

        return health

    def _check_dynamic_wardens(self) -> Dict[str, Any]:
        """Check health of dynamic wardens."""
        dynamic_config = self.registry.get("dynamic_wardens", {})

        health = {
            "status": "healthy",
            "unclassified_folders": len(dynamic_config.get("unclassified_folders", [])),
            "temporary_wardens": len(dynamic_config.get("temporary_wardens", {})),
            "checks": {},
            "issues": [],
        }

        # Check for stale temporary wardens
        temporary_wardens = dynamic_config.get("temporary_wardens", {})
        stale_count = 0

        for warden_name, warden_info in temporary_wardens.items():
            created_time = warden_info.get("created_time")
            if created_time:
                try:
                    created_dt = datetime.fromisoformat(
                        created_time.replace("Z", "+00:00")
                    )
                    age_hours = (datetime.now() - created_dt).total_seconds() / 3600

                    max_lifetime = self.registry.get("dynamic_warden_policy", {}).get(
                        "max_lifetime_hours", 24
                    )
                    if age_hours > max_lifetime:
                        stale_count += 1
                except:
                    pass

        health["checks"]["stale_temporary_wardens"] = stale_count

        if stale_count > 0:
            health["status"] = "warning"
            health["issues"].append(
                f"{stale_count} stale temporary wardens need cleanup"
            )

        # Check unclassified folders
        unclassified_folders = dynamic_config.get("unclassified_folders", [])
        if len(unclassified_folders) > 10:
            health["status"] = "warning"
            health["issues"].append(
                f"Many unclassified folders: {len(unclassified_folders)}"
            )

        return health

    def _count_files(self, folder_path: str) -> int:
        """Count files in a folder, skipping hidden and cache directories."""
        count = 0
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            count += len(files)
        return count

    def _update_system_metrics(self, health_results: Dict[str, Any]) -> Dict[str, Any]:
        """Update system metrics based on health check results."""
        system_metrics = self.registry.get("system_metrics", {})

        # Calculate warden health statistics
        warden_results = health_results.get("wardens", {})
        total_wardens = len(warden_results)
        healthy_wardens = sum(
            1 for w in warden_results.values() if w.get("status") == "healthy"
        )
        warning_wardens = sum(
            1 for w in warden_results.values() if w.get("status") == "warning"
        )
        critical_wardens = sum(
            1 for w in warden_results.values() if w.get("status") == "critical"
        )

        # Update metrics
        updated_metrics = {
            "total_wardens": total_wardens,
            "healthy_wardens": healthy_wardens,
            "warning_wardens": warning_wardens,
            "critical_wardens": critical_wardens,
            "warden_uptime": healthy_wardens / total_wardens
            if total_wardens > 0
            else 0,
            "last_health_check": datetime.now().isoformat(),
            "health_check_count": system_metrics.get("health_check_count", 0) + 1,
            "overall_health": health_results.get("overall_health", "unknown"),
        }

        # Merge with existing metrics
        system_metrics.update(updated_metrics)
        self.registry["system_metrics"] = system_metrics

        return updated_metrics

    def _generate_recommendations(self, health_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health check results."""
        recommendations = []

        # Check for critical wardens
        for warden_name, warden_health in health_results.get("wardens", {}).items():
            if warden_health.get("status") == "critical":
                folder_path = warden_health.get("folder_path", "unknown")
                recommendations.append(
                    f"Investigate critical warden: {warden_name} (folder: {folder_path})"
                )

        # Check for warning wardens
        warning_wardens = [
            w
            for w, h in health_results.get("wardens", {}).items()
            if h.get("status") == "warning"
        ]
        if warning_wardens:
            recommendations.append(
                f"Address warning wardens: {', '.join(warning_wardens)}"
            )

        # Check BASE AI
        base_ai_health = health_results.get("base_ai", {})
        if base_ai_health.get("status") != "healthy":
            recommendations.append("Check BASE AI configuration and connectivity")

        # Check dynamic wardens
        dynamic_health = health_results.get("dynamic_wardens", {})
        if dynamic_health.get("checks", {}).get("stale_temporary_wardens", 0) > 0:
            recommendations.append("Clean up stale temporary wardens")

        # Check health check frequency
        last_check = self.registry.get("system_metrics", {}).get("last_registry_update")
        if last_check:
            try:
                last_check_dt = datetime.fromisoformat(
                    last_check.replace("Z", "+00:00")
                )
                hours_since_update = (
                    datetime.now() - last_check_dt
                ).total_seconds() / 3600
                if hours_since_update > 24:
                    recommendations.append(
                        "Registry hasn't been updated in over 24 hours"
                    )
            except:
                pass

        return recommendations

    def _update_registry_health(self, health_results: Dict[str, Any]):
        """Update registry with health check results."""
        # Update warden health metrics
        for warden_name, warden_health in health_results.get("wardens", {}).items():
            if warden_name in self.registry.get("wardens", {}):
                warden_config = self.registry["wardens"][warden_name]

                # Update status if different - but only update to valid statuses
                current_status = warden_config.get("status")
                new_status = warden_health.get("status")

                if new_status in VALID_WARDEN_STATUSES and current_status != new_status:
                    warden_config["status"] = new_status
                    logger.info(
                        f"Updated {warden_name} status: {current_status} -> {new_status}"
                    )
                elif new_status not in VALID_WARDEN_STATUSES:
                    # Don't update to invalid statuses like "healthy", "warning", "critical"
                    logger.warning(
                        f"Not updating {warden_name} to invalid status: {new_status}"
                    )

                # Update health metrics
                if "health" in warden_config:
                    warden_config["health"]["last_health_check"] = (
                        datetime.now().isoformat()
                    )
                    warden_config["health"]["overall_status"] = new_status

        # Update system metrics
        self.registry["system_metrics"].update(health_results.get("system_metrics", {}))

        # Save registry
        self._save_registry()

    def _save_health_check_results(self, results: Dict[str, Any]):
        """Save health check results to file."""
        try:
            # Create health check directory
            health_dir = "logs/health_checks"
            os.makedirs(health_dir, exist_ok=True)

            # Save detailed results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_check_{timestamp}.json"
            filepath = os.path.join(health_dir, filename)

            with open(filepath, "w") as f:
                json.dump(results, f, indent=2)

            logger.info(f"Health check results saved to {filepath}")

            # Update latest health check
            latest_path = os.path.join(health_dir, "latest_health_check.json")
            with open(latest_path, "w") as f:
                json.dump(results, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save health check results: {e}")

    def generate_health_report(self) -> str:
        """Generate a human-readable health report."""
        results = self.run_health_checks()

        report = []
        report.append("=" * 60)
        report.append("PHASE 2 WARDENS HEALTH REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Overall Health: {results['overall_health'].upper()}")
        report.append(
            f"Check Duration: {results.get('check_duration_seconds', 0):.2f}s"
        )
        report.append("")

        # BASE AI Status
        base_ai = results.get("base_ai", {})
        report.append("BASE AI:")
        report.append(f"  Status: {base_ai.get('status', 'unknown')}")
        report.append(f"  Model: {base_ai.get('model', 'unknown')}")
        report.append(f"  Version: {base_ai.get('version', 'unknown')}")
        if base_ai.get("issues"):
            report.append("  Issues:")
            for issue in base_ai.get("issues", []):
                report.append(f"    - {issue}")
        report.append("")

        # Phase 2 Wardens Status
        report.append("PHASE 2 WARDENS:")
        warden_results = results.get("wardens", {})
        for warden_name, warden_health in warden_results.items():
            # Get the actual warden status from registry, not health check status
            warden_status = warden_health.get("checks", {}).get(
                "warden_status", "unknown"
            )
            health_status = warden_health.get("status", "unknown")

            status_symbol = (
                "✅"
                if warden_status == "active" and health_status == "healthy"
                else "⚠️"
                if warden_status == "active" and health_status == "warning"
                else "❌"
                if warden_status in ["error", "disabled"]
                else "⏳"
                if warden_status == "pending"
                else "❓"
            )
            report.append(f"{status_symbol} {warden_name}:")
            report.append(f"  Warden Status: {warden_status}")
            report.append(f"  Health Status: {health_status}")
            report.append(f"  Folder: {warden_health.get('folder_path', 'unknown')}")
            report.append(f"  Model: {warden_health.get('model_name', 'unknown')}")

            if warden_health.get("checks", {}).get("file_count"):
                report.append(f"  Files: {warden_health['checks']['file_count']}")

            if warden_health.get("issues"):
                report.append("  Issues:")
                for issue in warden_health.get("issues", []):
                    report.append(f"    - {issue}")
            report.append("")

        # Dynamic Wardens Status
        dynamic_health = results.get("dynamic_wardens", {})
        report.append("DYNAMIC WARDENS:")
        report.append(f"  Status: {dynamic_health.get('status', 'unknown')}")
        report.append(
            f"  Unclassified folders: {dynamic_health.get('unclassified_folders', 0)}"
        )
        report.append(
            f"  Temporary wardens: {dynamic_health.get('temporary_wardens', 0)}"
        )
        if dynamic_health.get("stale_temporary_wardens", 0) > 0:
            report.append(
                f"  Stale wardens: {dynamic_health['stale_temporary_wardens']}"
            )
        report.append("")

        # System Metrics
        system_metrics = results.get("system_metrics", {})
        report.append("SYSTEM METRICS:")
        report.append(f"  Total wardens: {system_metrics.get('total_wardens', 0)}")
        report.append(f"  Healthy: {system_metrics.get('healthy_wardens', 0)}")
        report.append(f"  Warning: {system_metrics.get('warning_wardens', 0)}")
        report.append(f"  Critical: {system_metrics.get('critical_wardens', 0)}")
        report.append(f"  Uptime: {system_metrics.get('warden_uptime', 0):.1%}")
        report.append("")

        # Issues and Recommendations
        if results.get("issues"):
            report.append("ISSUES:")
            for issue in results.get("issues", []):
                report.append(f"  - {issue}")
            report.append("")

        if results.get("recommendations"):
            report.append("RECOMMENDATIONS:")
            for rec in results.get("recommendations", []):
                report.append(f"  - {rec}")
            report.append("")

        report.append("=" * 60)
        report.append(f"Overall System Health: {results['overall_health'].upper()}")
        report.append("=" * 60)

        return "\n".join(report)

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """
        Run continuous health monitoring.

        Args:
            interval_minutes: Minutes between health checks
        """
        logger.info(
            f"Starting continuous monitoring (interval: {interval_minutes} minutes)"
        )

        try:
            while True:
                # Run health check
                results = self.run_health_checks()

                # Generate and print report
                report = self.generate_health_report()
                print(report)

                # Log to file
                self._log_monitoring_results(results)

                # Wait for next check
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logger.info("Continuous monitoring stopped by user")
        except Exception as e:
            logger.error(f"Continuous monitoring failed: {e}")

    def _log_monitoring_results(self, results: Dict[str, Any]):
        """Log monitoring results to file."""
        try:
            log_dir = "logs/monitoring"
            os.makedirs(log_dir, exist_ok=True)

            # Daily log file
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"monitoring_{date_str}.log")

            with open(log_file, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{timestamp}] Health Check\n")
                f.write(f"Overall Health: {results.get('overall_health', 'unknown')}\n")

                # Log warden statuses
                for warden_name, warden_health in results.get("wardens", {}).items():
                    status = warden_health.get("status", "unknown")
                    f.write(f"  {warden_name}: {status}\n")

                f.write("-" * 40 + "\n")

        except Exception as e:
            logger.error(f"Failed to log monitoring results: {e}")


def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Health Check Integration for Phase 2 Wardens"
    )
    parser.add_argument("--run", action="store_true", help="Run health checks once")
    parser.add_argument(
        "--monitor", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Monitoring interval in minutes"
    )
    parser.add_argument(
        "--registry", default=".ai_registry.json", help="Path to AI registry"
    )

    args = parser.parse_args()

    # Initialize health check integration
    health_check = HealthCheckIntegration(args.registry)

    if args.monitor:
        health_check.run_continuous_monitoring(args.interval)
    elif args.run:
        results = health_check.run_health_checks()
        report = health_check.generate_health_report()
        print(report)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
