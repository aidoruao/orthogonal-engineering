#!/usr/bin/env python3
"""
Dynamic Warden Tool for BASE AI

This tool enables BASE AI to handle unclassified folders by:
1. Analyzing new/unclassified folders
2. Creating temporary dynamic wardens
3. Monitoring folder activity
4. Recommending promotion to permanent warden
5. Cleaning up temporary wardens

Part of Phase 2 deployment for Local AI Warden System.
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DynamicWardenTool:
    """Dynamic warden tool for BASE AI to handle unclassified folders."""

    def __init__(self, registry_path: str = ".ai_registry.json"):
        """
        Initialize the dynamic warden tool.

        Args:
            registry_path: Path to the AI registry JSON file
        """
        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.dynamic_config = self.registry.get("dynamic_wardens", {})
        self.policy = self.registry.get("dynamic_warden_policy", {})
        self.warden_templates = self._load_warden_templates()

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

    def _load_warden_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load warden templates for different folder types."""
        return {
            "automation": {
                "model_name": "llama3.2:3b",
                "capabilities": [
                    "code_analysis",
                    "boundary_enforcement",
                    "trace_generation",
                ],
                "description": "Automation scripts and workflows",
                "priority": "high",
            },
            "toolkit": {
                "model_name": "codellama:7b",
                "capabilities": [
                    "autofix_engine",
                    "boundary_spellcheck",
                    "ide_integration",
                ],
                "description": "Toolkit and utility modules",
                "priority": "high",
            },
            "documentation": {
                "model_name": "mistral:7b",
                "capabilities": ["document_analysis", "blueprint_validation"],
                "description": "Documentation and specifications",
                "priority": "medium",
            },
            "logs": {
                "model_name": "llama3.2:3b",
                "capabilities": [
                    "log_analysis",
                    "pattern_detection",
                    "anomaly_detection",
                ],
                "description": "Log files and audit trails",
                "priority": "medium",
            },
            "tests": {
                "model_name": "codellama:7b",
                "capabilities": [
                    "test_analysis",
                    "coverage_tracking",
                    "failure_analysis",
                ],
                "description": "Test files and test suites",
                "priority": "medium",
            },
            "data": {
                "model_name": "mistral:7b",
                "capabilities": ["data_analysis", "schema_validation", "quality_check"],
                "description": "Data files and datasets",
                "priority": "low",
            },
            "config": {
                "model_name": "llama3.2:3b",
                "capabilities": ["config_analysis", "validation", "compliance_check"],
                "description": "Configuration files",
                "priority": "high",
            },
        }

    def scan_for_unclassified_folders(
        self, root_path: str = "."
    ) -> List[Dict[str, Any]]:
        """
        Scan for unclassified folders in the project.

        Args:
            root_path: Root path to scan from

        Returns:
            List of unclassified folders with metadata
        """
        logger.info(f"Scanning for unclassified folders in {root_path}")

        # Get existing warden folders
        existing_warden_folders = set()
        for warden_name, warden_config in self.registry.get("wardens", {}).items():
            folder_path = warden_config.get("folder_path")
            if folder_path:
                existing_warden_folders.add(folder_path)

        # Get temporary warden folders
        temporary_wardens = self.dynamic_config.get("temporary_wardens", {})
        for warden_name, warden_info in temporary_wardens.items():
            folder_path = warden_info.get("folder_path")
            if folder_path:
                existing_warden_folders.add(folder_path)

        # Scan for new folders
        unclassified_folders = []
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)

            # Skip if not a directory
            if not os.path.isdir(item_path):
                continue

            # Skip hidden directories
            if item.startswith("."):
                continue

            # Skip if already managed by a warden
            if item_path in existing_warden_folders:
                continue

            # Skip common directories that don't need wardens
            if item in [
                "__pycache__",
                "node_modules",
                ".git",
                ".idea",
                ".vscode",
                "venv",
                "env",
            ]:
                continue

            # Analyze the folder
            folder_analysis = self._analyze_folder(item_path)

            # Classify the folder
            classification = self._classify_folder(item_path, folder_analysis)

            unclassified_folders.append(
                {
                    "folder_name": item,
                    "folder_path": item_path,
                    "analysis": folder_analysis,
                    "classification": classification,
                    "discovered_time": datetime.now().isoformat(),
                }
            )

        # Update registry
        self.dynamic_config["unclassified_folders"] = [
            {
                "folder_name": f["folder_name"],
                "folder_path": f["folder_path"],
                "discovered_time": f["discovered_time"],
            }
            for f in unclassified_folders
        ]
        self.registry["dynamic_wardens"] = self.dynamic_config
        self._save_registry()

        logger.info(f"Found {len(unclassified_folders)} unclassified folders")
        return unclassified_folders

    def _analyze_folder(self, folder_path: str) -> Dict[str, Any]:
        """Analyze a folder to determine its characteristics."""
        analysis = {
            "exists": os.path.exists(folder_path),
            "readable": os.access(folder_path, os.R_OK)
            if os.path.exists(folder_path)
            else False,
            "file_count": 0,
            "file_types": {},
            "total_size_bytes": 0,
            "last_modified": None,
            "subfolder_count": 0,
            "dominant_file_type": None,
            "folder_age_days": None,
        }

        if not analysis["exists"]:
            return analysis

        try:
            file_count = 0
            total_size = 0
            last_modified = 0
            subfolders = 0
            file_type_counts = {}

            for root, dirs, files in os.walk(folder_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                # Count subfolders (excluding hidden)
                if root != folder_path:
                    subfolders += len(dirs)

                for file in files:
                    file_count += 1
                    file_path = os.path.join(root, file)

                    try:
                        stat = os.stat(file_path)
                        total_size += stat.st_size
                        last_modified = max(last_modified, stat.st_mtime)

                        # Categorize by file extension
                        ext = os.path.splitext(file)[1].lower()
                        if ext:
                            file_type_counts[ext] = file_type_counts.get(ext, 0) + 1
                        else:
                            file_type_counts["no_extension"] = (
                                file_type_counts.get("no_extension", 0) + 1
                            )

                    except Exception as e:
                        logger.warning(f"Could not stat file {file_path}: {e}")

            analysis["file_count"] = file_count
            analysis["total_size_bytes"] = total_size
            analysis["subfolder_count"] = subfolders
            analysis["file_types"] = file_type_counts

            if file_type_counts:
                analysis["dominant_file_type"] = max(
                    file_type_counts.items(), key=lambda x: x[1]
                )[0]

            if last_modified > 0:
                analysis["last_modified"] = datetime.fromtimestamp(
                    last_modified
                ).isoformat()

                # Calculate folder age
                folder_stat = os.stat(folder_path)
                folder_age = (time.time() - folder_stat.st_ctime) / (
                    24 * 60 * 60
                )  # in days
                analysis["folder_age_days"] = round(folder_age, 2)

        except Exception as e:
            logger.error(f"Failed to analyze folder {folder_path}: {e}")

        return analysis

    def _classify_folder(
        self, folder_path: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify a folder based on its contents."""
        folder_name = os.path.basename(folder_path).lower()
        file_types = analysis.get("file_types", {})

        # Check folder name patterns
        classification = {
            "type": "unknown",
            "confidence": 0.0,
            "suggested_template": None,
            "reasons": [],
        }

        # Check for known patterns
        patterns = {
            "automation": ["automation", "scripts", "workflows", "pipeline"],
            "toolkit": ["toolkit", "tools", "utils", "utilities", "lib", "library"],
            "documentation": ["docs", "documentation", "readme", "manual", "guide"],
            "logs": ["logs", "audit", "traces", "history"],
            "tests": ["tests", "test", "spec", "specs", "fixtures"],
            "data": ["data", "dataset", "storage", "cache", "temp"],
            "config": ["config", "configuration", "settings", "env", "properties"],
        }

        # Check folder name
        for folder_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in folder_name:
                    classification["type"] = folder_type
                    classification["confidence"] = 0.8
                    classification["suggested_template"] = folder_type
                    classification["reasons"].append(
                        f"Folder name contains '{pattern}'"
                    )
                    break
            if classification["type"] != "unknown":
                break

        # Check file types if still unknown
        if classification["type"] == "unknown":
            # Check for Python files
            if file_types.get(".py", 0) > 0:
                if file_types.get(".py", 0) > file_types.get(".md", 0):
                    classification["type"] = "automation"
                    classification["confidence"] = 0.7
                    classification["suggested_template"] = "automation"
                    classification["reasons"].append("Contains Python files")
                else:
                    classification["type"] = "documentation"
                    classification["confidence"] = 0.6
                    classification["suggested_template"] = "documentation"
                    classification["reasons"].append(
                        "Contains Python and documentation files"
                    )

            # Check for markdown files
            elif file_types.get(".md", 0) > 0 or file_types.get(".markdown", 0) > 0:
                classification["type"] = "documentation"
                classification["confidence"] = 0.9
                classification["suggested_template"] = "documentation"
                classification["reasons"].append("Contains markdown files")

            # Check for JSON files
            elif file_types.get(".json", 0) > 0:
                classification["type"] = "config"
                classification["confidence"] = 0.7
                classification["suggested_template"] = "config"
                classification["reasons"].append("Contains JSON files")

            # Check for log files
            elif file_types.get(".log", 0) > 0 or file_types.get(".txt", 0) > 0:
                classification["type"] = "logs"
                classification["confidence"] = 0.8
                classification["suggested_template"] = "logs"
                classification["reasons"].append("Contains log/text files")

        # Adjust confidence based on file count
        file_count = analysis.get("file_count", 0)
        if file_count > 10:
            classification["confidence"] = min(1.0, classification["confidence"] + 0.1)
            classification["reasons"].append(
                f"Has {file_count} files (substantial content)"
            )
        elif file_count == 0:
            classification["confidence"] = 0.1
            classification["reasons"].append("Empty folder")

        return classification

    def create_temporary_warden(
        self, folder_path: str, classification: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a temporary dynamic warden for an unclassified folder.

        Args:
            folder_path: Path to the folder
            classification: Folder classification results

        Returns:
            Warden ID if created, None otherwise
        """
        folder_name = os.path.basename(folder_path)
        warden_id = f"dynamic_{folder_name}_{int(time.time())}"

        # Get template based on classification
        template_type = classification.get("suggested_template", "automation")
        template = self.warden_templates.get(
            template_type, self.warden_templates["automation"]
        )

        # Create warden configuration
        temporary_warden = {
            "warden_id": warden_id,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "classification": classification,
            "template": template_type,
            "model_name": template["model_name"],
            "capabilities": template["capabilities"],
            "description": template["description"],
            "created_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "query_count": 0,
            "status": "active",
            "metadata": {
                "file_count": 0,
                "last_hash_manifest": None,
                "semantic_embedding": None,
            },
            "health": {
                "last_query": None,
                "response_time_ms": None,
                "success_rate": None,
            },
        }

        # Add to registry
        if "temporary_wardens" not in self.dynamic_config:
            self.dynamic_config["temporary_wardens"] = {}

        self.dynamic_config["temporary_wardens"][warden_id] = temporary_warden

        # Remove from unclassified folders
        self.dynamic_config["unclassified_folders"] = [
            f
            for f in self.dynamic_config.get("unclassified_folders", [])
            if f.get("folder_path") != folder_path
        ]

        self.registry["dynamic_wardens"] = self.dynamic_config
        self._save_registry()

        logger.info(f"Created temporary warden {warden_id} for {folder_path}")
        return warden_id

    def process_unclassified_folders(self) -> Dict[str, Any]:
        """
        Process all unclassified folders and create temporary wardens.

        Returns:
            Processing results
        """
        results = {
            "scanned_folders": 0,
            "new_unclassified": 0,
            "created_wardens": 0,
            "warden_ids": [],
            "errors": [],
        }

        try:
            # Scan for unclassified folders
            unclassified_folders = self.scan_for_unclassified_folders()
            results["scanned_folders"] = len(unclassified_folders)
            results["new_unclassified"] = len(unclassified_folders)

            # Process each unclassified folder
            for folder_info in unclassified_folders:
                folder_path = folder_info["folder_path"]
                classification = folder_info["classification"]

                # Only create warden if confidence is above threshold
                confidence = classification.get("confidence", 0)
                if confidence > 0.3:  # Minimum confidence threshold
                    try:
                        warden_id = self.create_temporary_warden(
                            folder_path, classification
                        )
                        if warden_id:
                            results["created_wardens"] += 1
                            results["warden_ids"].append(warden_id)
                    except Exception as e:
                        error_msg = f"Failed to create warden for {folder_path}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)

        except Exception as e:
            error_msg = f"Failed to process unclassified folders: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def update_warden_activity(self, warden_id: str, query_success: bool = True):
        """
        Update activity metrics for a temporary warden.

        Args:
            warden_id: ID of the temporary warden
            query_success: Whether the query was successful
        """
        if warden_id not in self.dynamic_config.get("temporary_wardens", {}):
            logger.warning(f"Temporary warden not found: {warden_id}")
            return

        warden = self.dynamic_config["temporary_wardens"][warden_id]
        warden["last_activity"] = datetime.now().isoformat()
        warden["query_count"] = warden.get("query_count", 0) + 1

        # Update health metrics
        if "health" not in warden:
            warden["health"] = {}

        warden["health"]["last_query"] = datetime.now().isoformat()
        warden["health"]["success_rate"] = warden.get("health", {}).get(
            "success_rate", 1.0
        )

        # Simple success rate calculation
        if query_success:
            current_rate = warden["health"]["success_rate"]
            warden["health"]["success_rate"] = (
                min(1.0, current_rate + 0.1) if current_rate < 1.0 else 1.0
            )
        else:
            current_rate = warden["health"]["success_rate"]
            warden["health"]["success_rate"] = max(0.0, current_rate - 0.2)

        self.registry["dynamic_wardens"] = self.dynamic_config
        self._save_registry()

        logger.debug(
            f"Updated activity for warden {warden_id}: query_count={warden['query_count']}"
        )

    def check_for_promotion(self, warden_id: str) -> bool:
        """
        Check if a temporary warden should be promoted to permanent.

        Args:
            warden_id: ID of the temporary warden

        Returns:
            True if should be promoted, False otherwise
        """
        if warden_id not in self.dynamic_config.get("temporary_wardens", {}):
            return False

        warden = self.dynamic_config["temporary_wardens"][warden_id]

        # Check promotion criteria
        query_count = warden.get("query_count", 0)
        promotion_threshold = self.policy.get("promotion_threshold", 10)

        # Check success rate
        success_rate = warden.get("health", {}).get("success_rate", 0)

        # Check age
        created_time = warden.get("created_time")
        if created_time:
            try:
                created_dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                age_hours = (datetime.now() - created_dt).total_seconds() / 3600
                max_lifetime = self.policy.get("max_lifetime_hours", 24)

                # Promote if query count meets threshold and success rate is good
                if query_count >= promotion_threshold and success_rate >= 0.7:
                    logger.info(
                        f"Warden {warden_id} eligible for promotion: queries={query_count}, success={success_rate:.1%}"
                    )
                    return True
                # Or if nearing lifetime limit
                elif age_hours > max_lifetime * 0.8:  # 80% of max lifetime
                    logger.info(
                        f"Warden {warden_id} nearing lifetime limit: {age_hours:.1f}h"
                    )
                    return True
            except Exception as e:
                logger.warning(
                    f"Could not parse created time for warden {warden_id}: {e}"
                )

        return False

    def promote_to_permanent(self, warden_id: str) -> Optional[str]:
        """
        Promote a temporary warden to permanent.

        Args:
            warden_id: ID of the temporary warden

        Returns:
            New permanent warden name if promoted, None otherwise
        """
        if warden_id not in self.dynamic_config.get("temporary_wardens", {}):
            logger.error(f"Cannot promote: temporary warden not found: {warden_id}")
            return None

        warden = self.dynamic_config["temporary_wardens"][warden_id]
        folder_path = warden.get("folder_path")
        folder_name = warden.get("folder_name")

        if not folder_path or not folder_name:
            logger.error(
                f"Cannot promote: missing folder information for warden {warden_id}"
            )
            return None

        # Generate permanent warden name
        permanent_name = f"{folder_name}_warden"

        # Check if warden with this name already exists
        if permanent_name in self.registry.get("wardens", {}):
            # Add suffix to make it unique
            suffix = 1
            while f"{folder_name}_warden_{suffix}" in self.registry.get("wardens", {}):
                suffix += 1
            permanent_name = f"{folder_name}_warden_{suffix}"

        # Create permanent warden configuration
        permanent_warden = {
            "folder_path": folder_path,
            "model_name": warden.get("model_name", "llama3.2:3b"),
            "api_key": "local_ollama",
            "status": "active",
            "metadata": {
                "file_count": 0,
                "last_hash_manifest": None,
                "semantic_embedding": None,
                "capabilities": warden.get("capabilities", []),
                "promoted_from": warden_id,
                "promotion_time": datetime.now().isoformat(),
            },
            "health": {
                "last_query": None,
                "response_time_ms": None,
                "success_rate": None,
            },
        }

        # Add to permanent wardens
        if "wardens" not in self.registry:
            self.registry["wardens"] = {}

        self.registry["wardens"][permanent_name] = permanent_warden

        # Remove temporary warden if cleanup is enabled
        if self.policy.get("cleanup_on_promotion", True):
            del self.dynamic_config["temporary_wardens"][warden_id]
            logger.info(f"Removed temporary warden {warden_id} after promotion")
        else:
            # Mark as promoted
            warden["status"] = "promoted"
            warden["promoted_to"] = permanent_name
            warden["promotion_time"] = datetime.now().isoformat()

        # Update registry
        self.registry["dynamic_wardens"] = self.dynamic_config
        self._save_registry()

        logger.info(f"Promoted warden {warden_id} to permanent warden {permanent_name}")
        return permanent_name

    def cleanup_stale_wardens(self) -> Dict[str, Any]:
        """
        Clean up stale temporary wardens.

        Returns:
            Cleanup results
        """
        results = {"checked_wardens": 0, "cleaned_up": 0, "promoted": 0, "errors": []}

        temporary_wardens = self.dynamic_config.get("temporary_wardens", {}).copy()

        for warden_id, warden in temporary_wardens.items():
            results["checked_wardens"] += 1

            try:
                # Check if warden should be promoted
                if self.check_for_promotion(warden_id):
                    promoted_name = self.promote_to_permanent(warden_id)
                    if promoted_name:
                        results["promoted"] += 1
                    continue

                # Check if warden is stale
                created_time = warden.get("created_time")
                if not created_time:
                    continue

                created_dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                age_hours = (datetime.now() - created_dt).total_seconds() / 3600
                max_lifetime = self.policy.get("max_lifetime_hours", 24)

                if age_hours > max_lifetime:
                    # Remove stale warden
                    del self.dynamic_config["temporary_wardens"][warden_id]
                    results["cleaned_up"] += 1
                    logger.info(
                        f"Cleaned up stale warden {warden_id} (age: {age_hours:.1f}h)"
                    )

            except Exception as e:
                error_msg = f"Error processing warden {warden_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Update registry if changes were made
        if results["cleaned_up"] > 0 or results["promoted"] > 0:
            self.registry["dynamic_wardens"] = self.dynamic_config
            self._save_registry()

        return results

    def get_dynamic_warden_status(self) -> Dict[str, Any]:
        """
        Get status of dynamic wardens system.

        Returns:
            Status information
        """
        temporary_wardens = self.dynamic_config.get("temporary_wardens", {})
        unclassified_folders = self.dynamic_config.get("unclassified_folders", [])

        # Calculate statistics
        warden_stats = {
            "total": len(temporary_wardens),
            "by_status": {},
            "by_template": {},
            "average_queries": 0,
            "average_age_hours": 0,
        }

        total_queries = 0
        total_age_hours = 0
        valid_wardens = 0

        for warden_id, warden in temporary_wardens.items():
            # Count by status
            status = warden.get("status", "unknown")
            warden_stats["by_status"][status] = (
                warden_stats["by_status"].get(status, 0) + 1
            )

            # Count by template
            template = warden.get("template", "unknown")
            warden_stats["by_template"][template] = (
                warden_stats["by_template"].get(template, 0) + 1
            )

            # Accumulate queries
            query_count = warden.get("query_count", 0)
            total_queries += query_count

            # Calculate age
            created_time = warden.get("created_time")
            if created_time:
                try:
                    created_dt = datetime.fromisoformat(
                        created_time.replace("Z", "+00:00")
                    )
                    age_hours = (datetime.now() - created_dt).total_seconds() / 3600
                    total_age_hours += age_hours
                    valid_wardens += 1
                except:
                    pass

        # Calculate averages
        if len(temporary_wardens) > 0:
            warden_stats["average_queries"] = total_queries / len(temporary_wardens)
        if valid_wardens > 0:
            warden_stats["average_age_hours"] = total_age_hours / valid_wardens

        return {
            "temporary_wardens": warden_stats,
            "unclassified_folders": len(unclassified_folders),
            "policy": self.policy,
            "timestamp": datetime.now().isoformat(),
        }

    def run_maintenance_cycle(self) -> Dict[str, Any]:
        """
        Run a complete maintenance cycle.

        Returns:
            Maintenance results
        """
        logger.info("Starting dynamic warden maintenance cycle")

        results = {
            "scan_results": {},
            "cleanup_results": {},
            "status": {},
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 1. Process unclassified folders
            scan_results = self.process_unclassified_folders()
            results["scan_results"] = scan_results

            # 2. Clean up stale wardens
            cleanup_results = self.cleanup_stale_wardens()
            results["cleanup_results"] = cleanup_results

            # 3. Get current status
            status = self.get_dynamic_warden_status()
            results["status"] = status

            logger.info(
                f"Maintenance cycle completed: {scan_results['created_wardens']} new wardens, {cleanup_results['cleaned_up']} cleaned up, {cleanup_results['promoted']} promoted"
            )

        except Exception as e:
            error_msg = f"Maintenance cycle failed: {e}"
            logger.error(error_msg)
            results["error"] = error_msg

        return results


def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic Warden Tool for BASE AI")
    parser.add_argument(
        "--scan", action="store_true", help="Scan for unclassified folders"
    )
    parser.add_argument(
        "--process", action="store_true", help="Process unclassified folders"
    )
    parser.add_argument("--cleanup", action="store_true", help="Clean up stale wardens")
    parser.add_argument(
        "--status", action="store_true", help="Get dynamic warden status"
    )
    parser.add_argument(
        "--maintenance", action="store_true", help="Run complete maintenance cycle"
    )
    parser.add_argument(
        "--registry", default=".ai_registry.json", help="Path to AI registry"
    )

    args = parser.parse_args()

    # Initialize dynamic warden tool
    tool = DynamicWardenTool(args.registry)

    if args.scan:
        folders = tool.scan_for_unclassified_folders()
        print(f"Found {len(folders)} unclassified folders:")
        for folder in folders:
            print(
                f"  - {folder['folder_name']}: {folder['classification']['type']} (confidence: {folder['classification']['confidence']:.1%})"
            )

    elif args.process:
        results = tool.process_unclassified_folders()
        print(f"Processed {results['scanned_folders']} folders:")
        print(f"  Created {results['created_wardens']} temporary wardens")
        if results["warden_ids"]:
            print(f"  Warden IDs: {', '.join(results['warden_ids'])}")
        if results["errors"]:
            print(f"  Errors: {len(results['errors'])}")

    elif args.cleanup:
        results = tool.cleanup_stale_wardens()
        print(f"Cleanup results:")
        print(f"  Checked {results['checked_wardens']} wardens")
        print(f"  Cleaned up {results['cleaned_up']} stale wardens")
        print(f"  Promoted {results['promoted']} wardens")
        if results["errors"]:
            print(f"  Errors: {len(results['errors'])}")

    elif args.status:
        status = tool.get_dynamic_warden_status()
        print(f"Dynamic Warden Status:")
        print(f"  Temporary wardens: {status['temporary_wardens']['total']}")
        print(f"  Unclassified folders: {status['unclassified_folders']}")
        print(
            f"  Average queries: {status['temporary_wardens']['average_queries']:.1f}"
        )
        print(f"  Average age: {status['temporary_wardens']['average_age_hours']:.1f}h")

        if status["temporary_wardens"]["by_status"]:
            print(f"  By status:")
            for s, count in status["temporary_wardens"]["by_status"].items():
                print(f"    {s}: {count}")

    elif args.maintenance:
        results = tool.run_maintenance_cycle()
        print(f"Maintenance Cycle Results:")
        print(
            f"  Scan: {results['scan_results'].get('created_wardens', 0)} new wardens"
        )
        print(
            f"  Cleanup: {results['cleanup_results'].get('cleaned_up', 0)} cleaned up"
        )
        print(f"  Promotion: {results['cleanup_results'].get('promoted', 0)} promoted")
        print(
            f"  Current: {results['status'].get('temporary_wardens', {}).get('total', 0)} temporary wardens"
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
