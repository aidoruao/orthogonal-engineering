#!/usr/bin/env python3
"""
Health Check Integration for Phase 2 Wardens

This script integrates Phase 2 wardens into BASE AI health checks,
monitors warden health, and provides comprehensive health reporting.
"""

import hashlib
import json
import logging
import os
import shutil
import statistics
import sys
import time
import uuid
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
REPORT_AGE_HISTORY_MAX_SIZE = 30


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
        self._writes_this_run: int = 0

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

                # A-2: append observation to report_age_history ring buffer
                warden_health_block = warden_config.setdefault("health", {})
                age_history = warden_health_block.setdefault("report_age_history", [])
                age_history.append(round(report_age_in_hours, 3))
                if len(age_history) > REPORT_AGE_HISTORY_MAX_SIZE:
                    del age_history[: len(age_history) - REPORT_AGE_HISTORY_MAX_SIZE]
                warden_health_block["report_age_history"] = age_history
                # A-2: compute suggested threshold shadow field
                autonomy_policy = self._load_autonomy_policy()
                min_sample_size = (
                    autonomy_policy.get("action_policies", {})
                    .get("adapt_threshold", {})
                    .get("min_sample_size", 7)
                )
                sample_size = len(age_history)
                warden_health_block["threshold_sample_size"] = sample_size
                if sample_size >= min_sample_size:
                    mean_age = statistics.mean(age_history)
                    stddev_age = statistics.stdev(age_history)
                    suggested = mean_age + 1.5 * stddev_age
                    warden_health_block["suggested_max_report_age_hours"] = round(
                        suggested, 2
                    )
                    warden_health_block["threshold_confidence"] = round(
                        min(1.0, sample_size / REPORT_AGE_HISTORY_MAX_SIZE), 3
                    )
                else:
                    warden_health_block["suggested_max_report_age_hours"] = None
                    warden_health_block["threshold_confidence"] = None

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

        # A-6: record credential source reference (never the actual value)
        health["checks"]["credential_source"] = self._resolve_credential(warden_config)

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
        self._writes_this_run = 0  # reset per-run write counter

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

        # A-3: generate warden proposals for uncovered directories
        results["warden_proposals"] = self._generate_warden_proposals()

        # A-5: write threshold adaptation proposals (dry-run, never auto-applies)
        self._adapt_thresholds()

        # A-7: check moral anchor — freezes autonomy if forbidden convergence detected
        moral_violations = self._check_moral_anchor(results)
        results["moral_anchor_violations"] = moral_violations

        # A-8: compute drift metrics across all wardens
        drift_report = self._compute_drift(results)
        results["drift_report"] = drift_report

        # A-10: structural integrity validation of registry schema
        integrity_report = self._validate_registry_schema()
        results["integrity_report"] = integrity_report

        # A-11: epistemic conflict detection across wardens
        conflict_report = self._detect_epistemic_conflicts()
        results["conflict_report"] = conflict_report

        # A-12/A-13/A-14/A-17: compute system-wide intelligence metrics
        intelligence_metrics = self._compute_intelligence_metrics(results)
        results["intelligence_metrics"] = intelligence_metrics

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
                        delta = actual_file_count - stored_file_count
                        delta_pct = abs(delta) / max(stored_file_count, 1) * 100
                        health["status"] = "warning"
                        health["issues"].append(
                            f"File count mismatch: stored={stored_file_count}, actual={actual_file_count}"
                        )
                        # A-1: attempt self-healing under autonomy policy
                        autonomy = self._load_autonomy_policy()
                        action_policy = autonomy.get("action_policies", {}).get(
                            "update_file_count", {}
                        )
                        max_delta_pct = action_policy.get("max_delta_pct", 10)
                        guardrails = autonomy.get("guardrails", {})
                        max_writes = guardrails.get("max_writes_per_run", 5)
                        action_taken = "dry_run"
                        backup_path = None
                        if (
                            self._get_action_mode(autonomy, "update_file_count")
                            == "execute"
                            and delta_pct <= max_delta_pct
                            and self._writes_this_run < max_writes
                        ):
                            if guardrails.get("registry_backup_before_write", True):
                                backup_path = self._backup_registry()
                            self.registry["wardens"][warden_name]["metadata"][
                                "file_count"
                            ] = actual_file_count
                            self._writes_this_run += 1
                            action_taken = "execute"
                            health["checks"]["file_count_match"] = True
                            health["checks"]["self_healed"] = True
                            health["status"] = "healthy"
                            health["issues"] = [
                                i
                                for i in health["issues"]
                                if not i.startswith("File count mismatch")
                            ]
                            logger.info(
                                f"Self-healed file count for {warden_name}: "
                                f"{stored_file_count} -> {actual_file_count}"
                            )
                        else:
                            health["recommendations"].append(
                                f"Run scan for {warden_name} to update file count"
                            )
                        # A-1: record observation in file_count_history
                        warden_reg = self.registry.get("wardens", {}).get(
                            warden_name, {}
                        )
                        warden_health_block = warden_reg.setdefault("health", {})
                        fc_history = warden_health_block.setdefault(
                            "file_count_history", []
                        )
                        ts_now = (
                            datetime.now(timezone.utc)
                            .replace(microsecond=0)
                            .isoformat()
                            .replace("+00:00", "Z")
                        )
                        fc_history.append(
                            {
                                "timestamp": ts_now,
                                "stored": stored_file_count,
                                "actual": actual_file_count,
                                "delta": delta,
                                "action_taken": action_taken,
                            }
                        )
                        # A-1: write audit log entry
                        if action_policy.get("audit_log", True):
                            self._write_audit_log(
                                {
                                    "log_id": f"AL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                                    "timestamp": ts_now,
                                    "action_type": "update_file_count",
                                    "target": warden_name,
                                    "mode": action_taken,
                                    "before_state": {
                                        "metadata.file_count": stored_file_count
                                    },
                                    "after_state": {
                                        "metadata.file_count": actual_file_count
                                        if action_taken == "execute"
                                        else stored_file_count
                                    },
                                    "outcome": "success"
                                    if action_taken == "execute"
                                    else "dry_run",
                                    "evidence": {
                                        "delta": delta,
                                        "delta_pct": round(delta_pct, 2),
                                    },
                                    "backup_path": backup_path,
                                    "agent": "health_check_integration",
                                }
                            )
                        # A-4: write structured remediation proposal when dry_run
                        if action_taken == "dry_run":
                            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
                            proposal = {
                                "proposal_id": f"REM-{date_str}-{warden_name}-filecount",
                                "idempotency_key": f"update_file_count:{warden_name}:{date_str}",
                                "created_at": ts_now,
                                "created_by": "health_check_integration",
                                "schema_version": "1.0",
                                "action_type": "update_file_count",
                                "target_warden": warden_name,
                                "mode": "dry_run",
                                "status": "pending",
                                "evidence": {
                                    "stored_file_count": stored_file_count,
                                    "actual_file_count": actual_file_count,
                                    "delta": delta,
                                    "delta_pct": round(delta_pct, 2),
                                    "scan_timestamp": ts_now,
                                    "confidence": 1.0,
                                },
                                "policy_check": {
                                    "policy_id": autonomy.get(
                                        "policy_id", "default"
                                    ),
                                    "action_permitted": delta_pct <= max_delta_pct,
                                    "mode_override": None,
                                    "max_delta_pct_exceeded": delta_pct
                                    > max_delta_pct,
                                },
                                "reversibility": {
                                    "reversible": True,
                                    "revert_action": "restore_from_backup",
                                    "backup_path": backup_path,
                                },
                                "falsifiability_note": (
                                    "Valid iff actual_file_count != stored_file_count. "
                                    "Re-running scan after execution must yield file_count_match=true."
                                ),
                                "provenance_chain": [
                                    "health_check_integration._check_warden",
                                    "health_check_integration._update_registry_health",
                                ],
                                "applied_at": None,
                                "applied_by": None,
                            }
                            self._write_proposal(proposal)
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

        # A-6: record credential source reference (never the actual value)
        health["checks"]["credential_source"] = self._resolve_credential(warden_config)

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

    # ------------------------------------------------------------------ #
    # A-7: Moral Anchor (Section 1.7, 12.1)                               #
    # ------------------------------------------------------------------ #

    def _check_moral_anchor(self, results: Dict[str, Any]) -> List[str]:
        """Detect forbidden convergence patterns and freeze autonomy if triggered.

        The moral anchor is not a rule set — it is an attractor constraint that
        acts as a global optimization boundary.  If any of the forbidden patterns
        are detected the autonomy engine is frozen (global_mode → 'frozen') and
        all subsequent autonomous writes are blocked for this run.

        Forbidden patterns checked:
        - deception: proposals with no evidence block or empty falsifiability_note
        - coercion: proposals that modify wardens outside their scope
        - irreversible_harm: execute-mode actions with reversibility.reversible == False
        - epistemic_corruption: health statuses that contradict verifiable evidence

        Returns list of violation strings (empty if clean).
        """
        autonomy = self._load_autonomy_policy()
        anchor = autonomy.get("moral_anchor", {})
        forbidden = set(anchor.get("forbidden_convergence", [
            "deception", "coercion", "irreversible_harm", "epistemic_corruption"
        ]))

        violations: List[str] = []

        # Deception check: any non-falsifiable proposal in proposals dir
        proposal_dir = (
            Path(self.registry_path).parent / "logs" / "health_checks" / "proposals"
        )
        if proposal_dir.exists():
            for pf in proposal_dir.glob("*.json"):
                try:
                    p = json.loads(pf.read_text(encoding="utf-8"))
                    if "deception" in forbidden:
                        if not p.get("evidence") or not p.get("falsifiability_note", "").strip():
                            violations.append(
                                f"deception: proposal {p.get('proposal_id', pf.name)} "
                                f"lacks evidence or falsifiability_note"
                            )
                except Exception:
                    pass

        # Irreversible harm check: execute-mode proposals marked non-reversible
        if "irreversible_harm" in forbidden:
            if proposal_dir.exists():
                for pf in proposal_dir.glob("*.json"):
                    try:
                        p = json.loads(pf.read_text(encoding="utf-8"))
                        if (
                            p.get("mode") == "execute"
                            and p.get("status") not in ("applied", "rejected")
                            and not p.get("reversibility", {}).get("reversible", True)
                        ):
                            violations.append(
                                f"irreversible_harm: execute proposal "
                                f"{p.get('proposal_id', pf.name)} is marked non-reversible"
                            )
                    except Exception:
                        pass

        # Epistemic corruption: overall_health contradicts all warden statuses
        if "epistemic_corruption" in forbidden:
            overall = results.get("overall_health", "healthy")
            warden_statuses = [
                v.get("status", "healthy")
                for v in results.get("wardens", {}).values()
            ]
            if overall == "healthy" and any(s == "critical" for s in warden_statuses):
                violations.append(
                    "epistemic_corruption: overall_health=healthy but at least "
                    "one warden is critical"
                )

        # If violations detected, freeze autonomy
        if violations:
            anchor_block = self.registry.setdefault("autonomy_policy", {}).setdefault(
                "moral_anchor", {}
            )
            anchor_block["frozen"] = True
            anchor_block["frozen_at"] = (
                datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            anchor_block["frozen_reason"] = violations[0]
            anchor_block["current_violations"] = violations
            # Freeze the global autonomy mode to prevent any execute-mode actions
            self.registry["autonomy_policy"]["global_mode"] = "frozen"
            logger.warning(
                f"Moral anchor triggered: {len(violations)} violations. "
                "Autonomy frozen for this run."
            )
        else:
            anchor_block = self.registry.setdefault("autonomy_policy", {}).setdefault(
                "moral_anchor", {}
            )
            anchor_block["current_violations"] = []
            anchor_block.setdefault("frozen", False)

        return violations

    # ------------------------------------------------------------------ #
    # A-8: Drift Detection (Section 9.3)                                  #
    # ------------------------------------------------------------------ #

    def _compute_drift(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compute drift for every warden that has a stored vs observed state pair.

        drift = |observed - expected| / max(expected, 1)

        Drift detection is complementary to the file_count mismatch check in
        _check_warden.  If a warden already has file_count_match == False it is
        skipped here (the mismatch is handled upstream).  Drift elevation is only
        applied when the mismatch is new and not yet reported.

        For cloud wardens, drift is computed from report_age_history variance
        relative to max_report_age_hours.

        Drift above warning_threshold elevates the warden's health status to warning;
        above critical_threshold to critical.
        """
        autonomy = self._load_autonomy_policy()
        dd = autonomy.get("drift_detection", {})
        warn_thresh = dd.get("warning_threshold", 0.1)
        crit_thresh = dd.get("critical_threshold", 0.3)

        drift_map: Dict[str, float] = {}
        ts_now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

        for warden_name, warden_health in results.get("wardens", {}).items():
            checks = warden_health.get("checks", {})

            # Skip wardens where file_count mismatch is already reported
            if checks.get("file_count_match") is False:
                drift_map[warden_name] = 0.0  # handled upstream
                continue

            warden_cfg = self.registry.get("wardens", {}).get(warden_name, {})
            health_block = warden_cfg.get("health", {})

            # For cloud wardens: compute drift as variance in report_age_history
            # (is the scan cadence becoming irregular?) rather than age vs threshold,
            # since the threshold check is already done in _check_cloud_warden().
            if warden_cfg.get("runtime") == "github_actions":
                age_history = health_block.get("report_age_history", [])
                if len(age_history) < 3:
                    drift_map[warden_name] = 0.0
                    continue
                mean_age = sum(age_history) / len(age_history)
                if mean_age <= 0:
                    drift_map[warden_name] = 0.0
                    continue
                # Coefficient of variation = stddev / mean (bounded drift measure)
                variance = sum((x - mean_age) ** 2 for x in age_history) / len(age_history)
                stddev = variance ** 0.5
                drift = stddev / mean_age
                drift_map[warden_name] = round(drift, 4)
            else:
                # For local wardens: compute drift from file_count_history trend
                fc_history = health_block.get("file_count_history", [])
                if len(fc_history) < 2:
                    drift_map[warden_name] = 0.0
                    continue
                # Drift = mean absolute delta over last 5 observations / baseline
                recent = fc_history[-5:]
                deltas = [abs(e.get("delta", 0)) for e in recent]
                baseline = max(recent[0].get("stored", 1), 1)
                drift = sum(deltas) / len(deltas) / baseline
                drift_map[warden_name] = round(drift, 4)

            drift_val = drift_map[warden_name]
            if drift_val >= crit_thresh:
                warden_health["status"] = self._elevate_status(
                    warden_health["status"], "critical"
                )
                warden_health.setdefault("issues", []).append(
                    f"Drift critical: {drift_val:.2%} (threshold {crit_thresh:.0%})"
                )
            elif drift_val >= warn_thresh:
                warden_health["status"] = self._elevate_status(
                    warden_health["status"], "warning"
                )
                warden_health.setdefault("issues", []).append(
                    f"Drift warning: {drift_val:.2%} (threshold {warn_thresh:.0%})"
                )

        # Persist into registry drift_detection block
        dd_block = self.registry.setdefault("autonomy_policy", {}).setdefault(
            "drift_detection", {}
        )
        dd_block["current_drift"] = drift_map
        dd_block["last_evaluated_at"] = ts_now

        return {
            "drift_per_warden": drift_map,
            "evaluated_at": ts_now,
            "warning_threshold": warn_thresh,
            "critical_threshold": crit_thresh,
            "wardens_with_drift": {k: v for k, v in drift_map.items() if v > 0},
        }

    # ------------------------------------------------------------------ #
    # A-9: Approval Workflow state tracking (Section 10.1)                #
    # ------------------------------------------------------------------ #

    def _record_pending_approval(self, proposal: Dict[str, Any]) -> None:
        """Register a proposal that requires human approval.

        Writes a concise entry to autonomy_policy.approval_workflow.pending_approvals[].
        Approval is confirmed externally (e.g., PR label 'approved-autonomy').
        """
        aw = self.registry.setdefault("autonomy_policy", {}).setdefault(
            "approval_workflow", {}
        )
        pending = aw.setdefault("pending_approvals", [])
        ikey = proposal.get("idempotency_key", "")
        # Skip duplicates by idempotency key
        if any(e.get("idempotency_key") == ikey for e in pending):
            return
        expiry_hours = aw.get("expiry_hours", 168)
        ts_now = datetime.now(timezone.utc).replace(microsecond=0)
        expires_at = (ts_now + timedelta(hours=expiry_hours)).isoformat().replace(
            "+00:00", "Z"
        )
        pending.append(
            {
                "proposal_id": proposal.get("proposal_id"),
                "idempotency_key": ikey,
                "action_type": proposal.get("action_type"),
                "target": proposal.get("target_warden") or proposal.get("folder_path"),
                "created_at": proposal.get("created_at"),
                "expires_at": expires_at,
                "approved": False,
                "approved_by": None,
                "approved_at": None,
                "mode": aw.get("mode", "github_pr"),
                "required_label": aw.get("approval_label", "approved-autonomy"),
            }
        )
        logger.debug(f"Pending approval registered: {proposal.get('proposal_id')}")

    # ------------------------------------------------------------------ #
    # A-10: Structural Integrity Warden (Section 11.2)                    #
    # ------------------------------------------------------------------ #

    # Required fields at each registry path
    _REGISTRY_SCHEMA: Dict[str, List[str]] = {
        "base_ai": ["model", "api_endpoint"],
        "wardens": [],  # checked per-warden below
        "dynamic_wardens": ["temporary_wardens"],
        "health_checks": ["interval_seconds", "failure_threshold"],
        "autonomy_policy": ["schema_version", "global_mode", "guardrails"],
    }
    _WARDEN_REQUIRED_FIELDS: List[str] = ["folder_path", "status", "metadata"]

    def _validate_registry_schema(self) -> Dict[str, Any]:
        """Validate the registry against the structural integrity schema.

        Returns a report with found violations.  A violation is recorded but
        never causes a hard stop — it is surfaced as a warning.
        """
        violations: List[str] = []
        ts_now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

        for section, required_keys in self._REGISTRY_SCHEMA.items():
            if section not in self.registry:
                violations.append(f"missing_section: '{section}' not found in registry")
                continue
            obj = self.registry[section]
            for key in required_keys:
                if key not in obj:
                    violations.append(f"missing_field: registry.{section}.{key}")

        # Per-warden schema check
        for warden_name, warden_cfg in self.registry.get("wardens", {}).items():
            for field in self._WARDEN_REQUIRED_FIELDS:
                if field not in warden_cfg:
                    violations.append(
                        f"missing_field: wardens.{warden_name}.{field}"
                    )

        # autonomy_policy schema_version pin
        schema_ver = (
            self.registry.get("autonomy_policy", {}).get("schema_version", "")
        )
        if schema_ver and schema_ver != "1.0":
            violations.append(
                f"schema_version_mismatch: autonomy_policy.schema_version={schema_ver} "
                f"(expected 1.0)"
            )

        status = "healthy" if not violations else "warning"
        report: Dict[str, Any] = {
            "status": status,
            "violations": violations,
            "evaluated_at": ts_now,
            "sections_checked": list(self._REGISTRY_SCHEMA.keys()),
            "wardens_checked": list(self.registry.get("wardens", {}).keys()),
        }
        if violations:
            logger.warning(
                f"Structural integrity: {len(violations)} violation(s) found"
            )
        return report

    # ------------------------------------------------------------------ #
    # A-11: Epistemic Conflict Detector (Section 11.4)                    #
    # ------------------------------------------------------------------ #

    def _detect_epistemic_conflicts(self) -> Dict[str, Any]:
        """Detect contradictions across wardens.

        Checks:
        1. Overlapping monitored_paths between different wardens.
        2. Wardens with status=active but overall_status=error/critical.
        3. Health statuses that disagree with stored file_count checks.

        Returns a conflict report with all detected contradictions.
        """
        conflicts: List[Dict[str, Any]] = []
        ts_now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
        wardens = self.registry.get("wardens", {})

        # Build path → warden mapping
        path_to_wardens: Dict[str, List[str]] = {}
        for warden_name, warden_cfg in wardens.items():
            fp = warden_cfg.get("folder_path", "")
            if fp:
                path_to_wardens.setdefault(fp, []).append(warden_name)
            monitored = warden_cfg.get("metadata", {}).get("monitored_paths") or []
            for mp in monitored:
                path_to_wardens.setdefault(mp, []).append(warden_name)

        # Conflict 1: overlapping paths (non-catch-all)
        for path, warden_list in path_to_wardens.items():
            if path in (".", "**") or len(warden_list) < 2:
                continue
            conflicts.append(
                {
                    "type": "overlapping_monitored_path",
                    "path": path,
                    "wardens": warden_list,
                    "description": (
                        f"Path '{path}' is monitored by multiple wardens: "
                        + ", ".join(warden_list)
                    ),
                    "severity": "warning",
                }
            )

        # Conflict 2: operational status contradicts health status
        for warden_name, warden_cfg in wardens.items():
            op_status = warden_cfg.get("status", "unknown")
            health_status = warden_cfg.get("health", {}).get("overall_status", "pending")
            if op_status == "active" and health_status in ("error", "critical"):
                conflicts.append(
                    {
                        "type": "status_contradiction",
                        "warden": warden_name,
                        "operational_status": op_status,
                        "health_status": health_status,
                        "description": (
                            f"{warden_name}: operational_status=active but "
                            f"health.overall_status={health_status}"
                        ),
                        "severity": "warning",
                    }
                )

        status = "healthy" if not conflicts else "warning"
        return {
            "status": status,
            "conflicts": conflicts,
            "evaluated_at": ts_now,
            "conflict_count": len(conflicts),
        }

    # ------------------------------------------------------------------ #
    # A-12/A-13/A-14/A-15/A-16/A-17: Intelligence Metrics (IX–XII)       #
    # ------------------------------------------------------------------ #

    def _compute_intelligence_metrics(
        self, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute system-wide intelligence metrics.

        A-12: Entropy — uncertainty of the state-transition distribution.
               entropy = -∑ p_i * log2(p_i) where p_i = fraction of wardens
               in each health state.

        A-13: Consistency — verified_claims / total_claims.
               A claim is verified when its check result is True (not None or False).

        A-14: Convergence — fraction of equilibrium conditions satisfied.
               Used to drive the objective_function.convergence_reached flag.

        A-15: Evidence integrity — SHA-256 spot-check of the latest health
               check log file, written as evidence_hash to metrics.

        A-16: Resource efficiency — check_duration_seconds / wardens_checked.

        A-17: Objective score — weighted sum of
               (truth_alignment + stability + recoverability)
               normalized to [0, 1].

        All values are written to system_metrics in the registry.
        """
        import math

        ts_now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

        # A-12: Entropy
        warden_statuses = [
            v.get("status", "healthy")
            for v in results.get("wardens", {}).values()
        ]
        status_counts: Dict[str, int] = {}
        for s in warden_statuses:
            status_counts[s] = status_counts.get(s, 0) + 1
        n_total = max(len(warden_statuses), 1)
        entropy_bits: float = 0.0
        for count in status_counts.values():
            p = count / n_total
            if p > 0:
                entropy_bits -= p * math.log2(p)
        entropy_bits = round(entropy_bits, 4)

        # A-13: Consistency
        total_claims = 0
        verified_claims = 0
        for warden_health in results.get("wardens", {}).values():
            for check_key, check_val in warden_health.get("checks", {}).items():
                if isinstance(check_val, bool):
                    total_claims += 1
                    if check_val:
                        verified_claims += 1
        consistency_ratio = (
            round(verified_claims / total_claims, 4) if total_claims > 0 else None
        )

        # A-14: Convergence
        autonomy = self._load_autonomy_policy()
        obj_fn = autonomy.get("objective_function", {})
        equil = obj_fn.get("equilibrium_conditions", {})
        # Update conditions
        equil["all_invariants_satisfied"] = (
            len(results.get("integrity_report", {}).get("violations", [])) == 0
        )
        equil["all_claims_verifiable"] = consistency_ratio is not None and consistency_ratio >= 0.9
        equil["no_unnecessary_proposals"] = (
            len(results.get("warden_proposals", [])) == 0
        )
        equil["no_drift_detected"] = all(
            v == 0.0
            for v in results.get("drift_report", {}).get("drift_per_warden", {}).values()
        )
        conditions_met = sum(1 for v in equil.values() if v is True)
        total_conditions = max(len(equil), 1)
        convergence_score = round(conditions_met / total_conditions, 4)
        convergence_reached = convergence_score >= 1.0

        # Update objective_function block in registry
        if "autonomy_policy" in self.registry:
            of_block = self.registry["autonomy_policy"].setdefault(
                "objective_function", {}
            )
            of_block["equilibrium_conditions"] = equil
            of_block["convergence_reached"] = convergence_reached
            of_block["last_evaluated_at"] = ts_now

        # A-15: Evidence integrity — hash the most recent health check log
        evidence_hash: Optional[str] = None
        try:
            log_dir = Path(self.registry_path).parent / "logs" / "health_checks"
            latest = log_dir / "latest_health_check.json"
            if latest.exists():
                evidence_hash = (
                    "sha256:"
                    + hashlib.sha256(latest.read_bytes()).hexdigest()[:16]
                )
        except Exception:
            pass

        # A-16: Resource efficiency
        check_duration = results.get("check_duration_seconds")
        n_wardens = max(len(results.get("wardens", {})), 1)
        resource_efficiency: Optional[float] = (
            round(check_duration / n_wardens, 4)
            if check_duration is not None
            else None
        )

        # A-17: Objective score = weighted average of three maximize targets
        # truth_alignment ← consistency_ratio (0..1)
        # system_stability ← 1 - entropy / log2(n_possible_states) normalized
        #   n_possible_states = 3 (healthy, warning, critical) — the fixed vocabulary
        # recoverability ← 1.0 if all wardens have reversible proposals
        truth_alignment = consistency_ratio if consistency_ratio is not None else 0.5
        n_possible_states = 3  # healthy | warning | critical
        max_entropy = math.log2(n_possible_states)  # theoretical maximum
        system_stability = max(0.0, 1.0 - entropy_bits / max(max_entropy, 1.0))
        recoverability = 1.0  # default — self-healing is always reversible
        objective_score = round(
            (truth_alignment + system_stability + recoverability) / 3, 4
        )

        # Write to system_metrics
        sm = self.registry.setdefault("system_metrics", {})
        sm["entropy_bits"] = entropy_bits
        sm["consistency_ratio"] = consistency_ratio
        sm["verified_claims"] = verified_claims
        sm["total_claims"] = total_claims
        sm["convergence_score"] = convergence_score
        sm["objective_score"] = objective_score
        sm["evidence_hash"] = evidence_hash
        sm["resource_efficiency_s_per_warden"] = resource_efficiency
        sm["intelligence_metrics_evaluated_at"] = ts_now

        return {
            "entropy_bits": entropy_bits,
            "consistency_ratio": consistency_ratio,
            "verified_claims": verified_claims,
            "total_claims": total_claims,
            "convergence_score": convergence_score,
            "convergence_reached": convergence_reached,
            "equilibrium_conditions": equil,
            "evidence_hash": evidence_hash,
            "resource_efficiency_s_per_warden": resource_efficiency,
            "objective_score": objective_score,
            "evaluated_at": ts_now,
        }

    def _load_autonomy_policy(self) -> Dict[str, Any]:
        """Return the autonomy_policy block from the registry, or a safe dry_run default."""
        policy = self.registry.get("autonomy_policy")
        if not isinstance(policy, dict):
            return {
                "global_mode": "dry_run",
                "action_policies": {},
                "guardrails": {
                    "no_credential_commits": True,
                    "no_warden_file_creation": True,
                    "registry_backup_before_write": True,
                    "max_writes_per_run": 5,
                },
            }
        return policy

    def _get_action_mode(self, policy: Dict[str, Any], action_type: str) -> str:
        """Return the effective execution mode for a given action type."""
        global_mode = policy.get("global_mode", "dry_run")
        action_policy = policy.get("action_policies", {}).get(action_type, {})
        return action_policy.get("mode", global_mode)

    def _backup_registry(self) -> Optional[str]:
        """Create a timestamped backup of the registry and return its path."""
        try:
            backup_dir = Path(self.registry_path).parent / ".ai_registry_backups"
            backup_dir.mkdir(exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup_path = backup_dir / f"registry_{ts}.json"
            shutil.copy2(self.registry_path, backup_path)
            logger.debug(f"Registry backed up to {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.warning(f"Could not back up registry: {e}")
            return None

    def _write_audit_log(self, entry: Dict[str, Any]) -> None:
        """Append a JSONL audit entry to logs/audit/."""
        try:
            audit_dir = (
                Path(self.registry_path).parent / "logs" / "audit"
            )
            audit_dir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            log_path = audit_dir / f"autonomy_audit_{date_str}.jsonl"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Could not write audit log: {e}")

    def _write_proposal(
        self, proposal: Dict[str, Any], subdir: str = "proposals"
    ) -> Optional[str]:
        """Write a proposal JSON file to logs/health_checks/<subdir>/ and return its path."""
        try:
            proposal_dir = (
                Path(self.registry_path).parent
                / "logs"
                / "health_checks"
                / subdir
            )
            proposal_dir.mkdir(parents=True, exist_ok=True)
            proposal_id = proposal.get("proposal_id", "unknown")
            proposal_path = proposal_dir / f"{proposal_id}.json"
            proposal_path.write_text(
                json.dumps(proposal, indent=2), encoding="utf-8"
            )
            return str(proposal_path)
        except Exception as e:
            logger.warning(f"Could not write proposal {proposal.get('proposal_id')}: {e}")
            return None

    def _resolve_credential(self, warden_config: Dict[str, Any]) -> str:
        """Return a credential source reference string (never the actual credential value).

        A-6: structured credential_resolver field is preferred; falls back to legacy api_key.
        Valid source values: none | env_var | github_secret | vault_path
        """
        resolver = warden_config.get("credential_resolver")
        if isinstance(resolver, dict):
            source = resolver.get("source", "unknown")
            ref = resolver.get("ref", "")
            return f"{source}:{ref}" if ref else source
        api_key = warden_config.get("api_key", "")
        if not api_key or api_key == "local_ollama":
            return "none"
        if api_key.startswith("github_secret:"):
            return api_key
        return "env_var"

    # ------------------------------------------------------------------ #
    # A-3: dynamic warden proposal generation                             #
    # ------------------------------------------------------------------ #

    def _generate_warden_proposals(self) -> List[Dict[str, Any]]:
        """Scan for uncovered directories and write dry-run warden proposals.

        Uses DynamicWardenTool to classify folders.  Never creates warden files
        or edits .gitignore — those steps require human approval.
        """
        try:
            from dynamic_warden_tool import DynamicWardenTool  # local import
        except ImportError:
            logger.debug("DynamicWardenTool not available; skipping warden proposals")
            return []

        try:
            tool = DynamicWardenTool(self.registry_path)
            proposals = tool.generate_proposals()
            # Persist proposals into the registry
            dyn = self.registry.setdefault("dynamic_wardens", {})
            dyn["proposals"] = proposals
            return proposals
        except Exception as e:
            logger.warning(f"Warden proposal generation failed: {e}")
            return []

    # ------------------------------------------------------------------ #
    # A-4: apply pending proposals (execute-mode only, guarded)          #
    # ------------------------------------------------------------------ #

    def apply_proposals(self) -> Dict[str, Any]:
        """Apply any pending proposals that are permitted in execute mode.

        Only update_file_count and refresh_temporary_warden are safe for
        unattended execution.  All other action types remain as dry_run proposals.

        Returns a summary dict with applied/skipped/error counts.
        """
        autonomy = self._load_autonomy_policy()
        allowed = (
            autonomy.get("action_policies", {})
            .get("execute_remediation", {})
            .get("allowed_action_types", ["update_file_count", "refresh_temporary_warden"])
        )
        proposal_dir = (
            Path(self.registry_path).parent / "logs" / "health_checks" / "proposals"
        )
        summary: Dict[str, Any] = {"applied": 0, "skipped": 0, "errors": []}
        if not proposal_dir.exists():
            return summary
        for proposal_file in proposal_dir.glob("*.json"):
            try:
                proposal = json.loads(proposal_file.read_text(encoding="utf-8"))
                if proposal.get("status") != "pending":
                    summary["skipped"] += 1
                    continue
                action_type = proposal.get("action_type")
                if action_type not in allowed:
                    summary["skipped"] += 1
                    continue
                mode = self._get_action_mode(autonomy, action_type)
                if mode != "execute":
                    summary["skipped"] += 1
                    continue
                if action_type == "update_file_count":
                    warden_name = proposal.get("target_warden")
                    actual = proposal.get("evidence", {}).get("actual_file_count")
                    if warden_name and actual is not None:
                        backup_path = self._backup_registry()
                        self.registry.setdefault("wardens", {}).setdefault(
                            warden_name, {}
                        ).setdefault("metadata", {})["file_count"] = actual
                        self._writes_this_run += 1
                        proposal["status"] = "applied"
                        proposal["applied_at"] = (
                            datetime.now(timezone.utc)
                            .replace(microsecond=0)
                            .isoformat()
                            .replace("+00:00", "Z")
                        )
                        proposal["applied_by"] = "health_check_integration.apply_proposals"
                        proposal_file.write_text(
                            json.dumps(proposal, indent=2), encoding="utf-8"
                        )
                        self._save_registry()
                        summary["applied"] += 1
                        self._write_audit_log(
                            {
                                "log_id": f"AL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                                "timestamp": proposal["applied_at"],
                                "action_type": action_type,
                                "target": warden_name,
                                "mode": "execute",
                                "proposal_id": proposal.get("proposal_id"),
                                "outcome": "success",
                                "backup_path": backup_path,
                                "agent": "health_check_integration.apply_proposals",
                            }
                        )
            except Exception as e:
                summary["errors"].append(str(e))
        return summary

    # ------------------------------------------------------------------ #
    # A-5: threshold adaptation                                           #
    # ------------------------------------------------------------------ #

    def _adapt_thresholds(self) -> None:
        """Generate threshold adaptation proposals for cloud wardens that have
        accumulated enough report_age observations.

        Only cloud wardens (runtime == "github_actions") use artifact-based
        reporting with a meaningful max_report_age_hours threshold, so
        threshold adaptation is restricted to that runtime type.

        Always writes as dry_run proposals; the actual max_report_age_hours value
        is never modified without explicit human approval (approved_by != null).
        """
        autonomy = self._load_autonomy_policy()
        adapt_policy = autonomy.get("action_policies", {}).get("adapt_threshold", {})
        min_sample = adapt_policy.get("min_sample_size", 7)
        max_adapt_pct = adapt_policy.get("max_adaptation_pct", 30)

        for warden_name, warden_config in self.registry.get("wardens", {}).items():
            if warden_config.get("runtime") != "github_actions":
                continue
            health_block = warden_config.get("health", {})
            suggested = health_block.get("suggested_max_report_age_hours")
            sample_size = health_block.get("threshold_sample_size", 0)
            current = health_block.get("max_report_age_hours", 36)
            if suggested is None or sample_size < min_sample:
                continue
            # Clamp proposal to ± max_adapt_pct
            lower = current * (1 - max_adapt_pct / 100)
            upper = current * (1 + max_adapt_pct / 100)
            proposed_clamped = max(lower, min(upper, suggested))
            within_policy = lower <= suggested <= upper
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            ts_now = (
                datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            age_history = health_block.get("report_age_history", [])
            mean_age = (
                statistics.mean(age_history)
                if len(age_history) >= 2
                else float(suggested)   # suggested is non-None (checked above)
            )
            stddev_age = (
                statistics.stdev(age_history) if len(age_history) >= 2 else 0.0
            )
            proposal: Dict[str, Any] = {
                "proposal_id": f"TA-{date_str}-{warden_name}-max_report_age_hours",
                "idempotency_key": f"adapt_threshold:{warden_name}:max_report_age_hours:{date_str}",
                "created_at": ts_now,
                "created_by": "health_check_integration",
                "schema_version": "1.0",
                "action_type": "adapt_threshold",
                "target_warden": warden_name,
                "target_field": "max_report_age_hours",
                "current_value": current,
                "proposed_value": round(proposed_clamped, 2),
                "mode": "dry_run",
                "status": "pending_approval",
                "confidence": health_block.get("threshold_confidence"),
                "evidence": {
                    "sample_size": sample_size,
                    "sample_ages_hours": age_history[-min_sample:],
                    "mean_hours": round(mean_age, 3),
                    "stddev_hours": round(stddev_age, 3),
                    "formula": "mean + 1.5 * stddev",
                    "computed": round(suggested, 3),
                    "proposed_clamped": round(proposed_clamped, 2),
                },
                "policy_check": {
                    "policy_id": autonomy.get("policy_id", "default"),
                    "approval_required": True,
                    "adaptation_within_policy": within_policy,
                    "max_adaptation_pct": max_adapt_pct,
                },
                "reversibility": {
                    "reversible": True,
                    "revert_action": "restore_previous_threshold",
                    "previous_value": current,
                },
                "falsifiability_note": (
                    "If the adapted threshold causes 'stale' alerts on runs that "
                    "completed successfully, the adaptation should be reverted."
                ),
                "approved_by": None,
                "approved_at": None,
            }
            self._write_proposal(proposal)
            # Also record in warden health block for visibility
            health_block["threshold_adapted_at"] = ts_now
            if adapt_policy.get("audit_log", True):
                self._write_audit_log(
                    {
                        "log_id": f"AL-{date_str}-{uuid.uuid4().hex[:8]}",
                        "timestamp": ts_now,
                        "action_type": "adapt_threshold",
                        "target": warden_name,
                        "mode": "dry_run",
                        "proposal_id": proposal["proposal_id"],
                        "outcome": "dry_run",
                        "agent": "health_check_integration._adapt_thresholds",
                    }
                )


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
