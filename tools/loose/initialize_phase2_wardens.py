#!/usr/bin/env python3
"""
Phase 2 Wardens Initialization Script

This script initializes all Phase 2 wardens, scans their assigned folders,
generates metadata, and updates the AI registry with current information.
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def count_files(folder_path: str) -> int:
    """Count files recursively in a folder, skipping hidden and cache directories."""
    count = 0
    if not os.path.exists(folder_path):
        return 0

    for root, dirs, files in os.walk(folder_path):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        count += len(files)
    return count


def generate_hash_manifest(folder_path: str) -> dict:
    """Generate SHA256 hash manifest for files in a folder."""
    hash_manifest = {}

    if not os.path.exists(folder_path):
        return hash_manifest

    for root, dirs, files in os.walk(folder_path):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                # Store relative path
                rel_path = os.path.relpath(file_path, folder_path)
                hash_manifest[rel_path] = file_hash

            except Exception as e:
                logger.warning(f"Could not hash file {file_path}: {e}")

    return hash_manifest


def analyze_folder_structure(folder_path: str, folder_type: str) -> dict:
    """Analyze folder structure based on folder type."""
    analysis = {
        "folder_type": folder_type,
        "exists": os.path.exists(folder_path),
        "readable": os.access(folder_path, os.R_OK)
        if os.path.exists(folder_path)
        else False,
        "file_count": 0,
        "file_types": {},
        "total_size_bytes": 0,
        "last_modified": None,
    }

    if not analysis["exists"]:
        return analysis

    try:
        file_count = 0
        total_size = 0
        last_modified = 0

        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

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
                        analysis["file_types"][ext] = (
                            analysis["file_types"].get(ext, 0) + 1
                        )
                    else:
                        analysis["file_types"]["no_extension"] = (
                            analysis["file_types"].get("no_extension", 0) + 1
                        )

                except Exception as e:
                    logger.warning(f"Could not stat file {file_path}: {e}")

        analysis["file_count"] = file_count
        analysis["total_size_bytes"] = total_size
        if last_modified > 0:
            analysis["last_modified"] = datetime.fromtimestamp(
                last_modified
            ).isoformat()

        # Add folder-specific analysis
        if folder_type == "automation":
            analysis["python_files"] = analysis["file_types"].get(".py", 0)
            analysis["json_files"] = analysis["file_types"].get(".json", 0)

        elif folder_type == "toolkit":
            analysis["python_files"] = analysis["file_types"].get(".py", 0)
            analysis["init_files"] = any(
                f.endswith("__init__.py")
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            )

        elif folder_type == "documentation":
            analysis["markdown_files"] = analysis["file_types"].get(
                ".md", 0
            ) + analysis["file_types"].get(".markdown", 0)
            analysis["html_files"] = analysis["file_types"].get(".html", 0) + analysis[
                "file_types"
            ].get(".htm", 0)
            analysis["json_files"] = analysis["file_types"].get(".json", 0)

    except Exception as e:
        logger.error(f"Failed to analyze folder {folder_path}: {e}")

    return analysis


def update_ai_registry(registry_path: str, warden_updates: dict) -> bool:
    """Update the AI registry with warden metadata."""
    try:
        # Read current registry
        with open(registry_path, "r") as f:
            registry = json.load(f)

        # Update warden entries
        for warden_name, warden_data in warden_updates.items():
            if warden_name in registry.get("wardens", {}):
                registry["wardens"][warden_name]["metadata"].update(
                    warden_data["metadata"]
                )
                registry["wardens"][warden_name]["health"].update(warden_data["health"])
                registry["wardens"][warden_name]["status"] = warden_data["status"]

        # Update system metrics
        registry["system_metrics"]["last_registry_update"] = datetime.now().isoformat()
        registry["system_metrics"]["total_wardens"] = len(registry.get("wardens", {}))

        # Write updated registry
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)

        # Create backup
        backup_dir = os.path.join(
            os.path.dirname(registry_path), ".ai_registry_backups"
        )
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(
            backup_dir,
            f"registry_backup_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(backup_path, "w") as f:
            json.dump(registry, f, indent=2)

        logger.info(f"Registry updated and backed up to {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to update AI registry: {e}")
        return False


def save_warden_metadata(metadata_dir: str, warden_name: str, metadata: dict):
    """Save warden metadata to file."""
    try:
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_path = os.path.join(metadata_dir, f"{warden_name}_metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved for {warden_name} to {metadata_path}")

    except Exception as e:
        logger.error(f"Failed to save metadata for {warden_name}: {e}")


def initialize_phase2_wardens():
    """Main function to initialize Phase 2 wardens."""
    start_time = time.time()
    logger.info("Starting Phase 2 Wardens Initialization")

    # Define wardens configuration
    wardens_config = {
        "automation_warden": {
            "folder_path": "automation",
            "model_name": "llama3.2:3b",
            "capabilities": [
                "code_analysis",
                "boundary_enforcement",
                "trace_generation",
            ],
        },
        "toolkit_warden": {
            "folder_path": "toolkit/oe",
            "model_name": "codellama:7b",
            "capabilities": [
                "autofix_engine",
                "boundary_spellcheck",
                "ide_integration",
            ],
        },
        "documentation_warden": {
            "folder_path": "documentation",
            "model_name": "mistral:7b",
            "capabilities": ["document_analysis", "blueprint_validation"],
        },
    }

    # Initialize each warden
    warden_updates = {}
    all_metadata = {}

    for warden_name, config in wardens_config.items():
        warden_start = time.time()
        folder_path = config["folder_path"]
        folder_type = warden_name.split("_")[0]  # automation, toolkit, documentation

        logger.info(f"Initializing {warden_name} for folder: {folder_path}")

        # Check folder existence
        if not os.path.exists(folder_path):
            logger.warning(
                f"Folder not found: {folder_path}. Warden will be marked as pending."
            )
            status = "pending"
            file_count = 0
            hash_manifest = {}
            folder_analysis = {"exists": False, "readable": False}
        else:
            status = "active"

            # Count files
            file_count = count_files(folder_path)

            # Generate hash manifest
            hash_manifest = generate_hash_manifest(folder_path)

            # Analyze folder structure
            folder_analysis = analyze_folder_structure(folder_path, folder_type)

            logger.info(f"  Found {file_count} files in {folder_path}")
            logger.info(f"  Generated hash manifest with {len(hash_manifest)} entries")

        # Prepare metadata for registry update
        warden_updates[warden_name] = {
            "status": status,
            "metadata": {
                "file_count": file_count,
                "last_hash_manifest": hash_manifest if hash_manifest else None,
                "semantic_embedding": None,  # Placeholder for future implementation
                "capabilities": config["capabilities"],
                "folder_analysis": folder_analysis,
            },
            "health": {
                "last_query": None,
                "response_time_ms": None,
                "success_rate": None,
                "last_health_check": datetime.now().isoformat(),
                "initialization_time_seconds": time.time() - warden_start,
            },
        }

        # Prepare detailed metadata for storage
        all_metadata[warden_name] = {
            "warden_name": warden_name,
            "folder_path": folder_path,
            "model_name": config["model_name"],
            "status": status,
            "initialization_timestamp": datetime.now().isoformat(),
            "file_count": file_count,
            "hash_manifest": hash_manifest,
            "folder_analysis": folder_analysis,
            "initialization_time_seconds": time.time() - warden_start,
        }

        logger.info(
            f"  {warden_name} initialization completed in {time.time() - warden_start:.2f} seconds"
        )

    # Save metadata to files
    metadata_dir = "wardens_metadata"
    for warden_name, metadata in all_metadata.items():
        save_warden_metadata(metadata_dir, warden_name, metadata)

    # Update AI registry
    registry_path = ".ai_registry.json"
    if update_ai_registry(registry_path, warden_updates):
        logger.info("AI registry updated successfully")
    else:
        logger.error("Failed to update AI registry")

    # Generate audit hash for Phase 2 deployment
    audit_data = {
        "phase": 2,
        "deployment_timestamp": datetime.now().isoformat(),
        "wardens_initialized": list(wardens_config.keys()),
        "total_files_scanned": sum(m["file_count"] for m in all_metadata.values()),
        "total_initialization_time_seconds": time.time() - start_time,
    }

    audit_hash = hashlib.sha256(
        json.dumps(audit_data, sort_keys=True).encode()
    ).hexdigest()
    audit_data["audit_hash"] = audit_hash

    # Save audit data
    audit_path = os.path.join(metadata_dir, "phase2_deployment_audit.json")
    with open(audit_path, "w") as f:
        json.dump(audit_data, f, indent=2)

    logger.info(f"Phase 2 deployment audit saved to {audit_path}")
    logger.info(f"Audit hash: {audit_hash}")

    # Print summary
    print("\n" + "=" * 60)
    print("PHASE 2 WARDENS DEPLOYMENT - INITIALIZATION SUMMARY")
    print("=" * 60)

    for warden_name, metadata in all_metadata.items():
        status_symbol = "✅" if metadata["status"] == "active" else "⚠️"
        print(f"\n{status_symbol} {warden_name}:")
        print(f"  Folder: {metadata['folder_path']}")
        print(f"  Status: {metadata['status']}")
        print(f"  Files: {metadata['file_count']}")
        print(f"  Model: {metadata['model_name']}")
        print(f"  Init time: {metadata['initialization_time_seconds']:.2f}s")

    print(f"\n📊 Total files scanned: {audit_data['total_files_scanned']}")
    print(
        f"⏱️  Total initialization time: {audit_data['total_initialization_time_seconds']:.2f}s"
    )
    print(f"🔐 Audit hash: {audit_hash[:16]}...")
    print("=" * 60)
    print("Phase 2 wardens deployment completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = initialize_phase2_wardens()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled error during initialization: {e}")
        sys.exit(1)
