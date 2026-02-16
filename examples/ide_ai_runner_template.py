#!/usr/bin/env python3
"""
IDE AI Runner Template

This template demonstrates how to use the CAS system for IDE AI workflows.
Follows safety-first principles: dry-run default, mandatory backups, no auto-push.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backup import BackupManager
from core.alpha_omega_finalizer import AlphaOmegaFinalizer
from handling_pipeline import HandlingPipeline
from logger import get_logger
from manifest import Manifest


def main():
    """Main runner function."""
    
    # Initialize logger
    logger = get_logger("ide_ai_runner")
    logger.info("Starting IDE AI runner")
    
    # Configuration
    DRY_RUN = True  # ALWAYS start with dry-run
    VAULT_PATH = Path("C:/Users/Aidor/Downloads/ai_exports")  # Local-only vault
    
    # Example files to process (adjust as needed)
    source_files = [
        "example_file1.txt",
        "example_file2.py",
    ]
    
    # Step 1: Initialize components
    logger.info("Initializing components")
    pipeline = HandlingPipeline(dry_run=DRY_RUN)
    backup_manager = BackupManager()
    finalizer = AlphaOmegaFinalizer(name="ide_ai_session")
    
    # Step 2: Alpha phase - Capture initial state
    logger.info("Alpha phase: Capturing initial state")
    existing_files = [f for f in source_files if Path(f).exists()]
    
    if not existing_files:
        logger.warning("No existing files found to process")
        return
    
    finalizer.alpha(
        existing_files,
        metadata={
            "session": "ide_ai_runner",
            "dry_run": DRY_RUN,
            "vault_path": str(VAULT_PATH)
        }
    )
    
    # Step 3: Create manifest before processing
    logger.info("Creating manifest")
    manifest = Manifest(name="ide_ai_session")
    for filepath in existing_files:
        manifest.add_entry(filepath)
    
    manifest_path = Path("manifests/ide_ai_session_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest.save(manifest_path)
    logger.info(f"Manifest saved to {manifest_path}")
    
    # Step 4: Process files through pipeline
    logger.info(f"Processing {len(existing_files)} files (dry_run={DRY_RUN})")
    results = []
    
    for filepath in existing_files:
        try:
            result = pipeline.process_file(filepath, create_backup=True)
            results.append(result)
            
            # Log result
            status = "✓" if all(
                s.get("status") in ["success", "skipped"]
                for s in result.get("stages", {}).values()
            ) else "✗"
            
            logger.info(f"{status} Processed: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            results.append({"filepath": str(filepath), "error": str(e)})
    
    # Step 5: Omega phase - Verify final state
    logger.info("Omega phase: Verifying final state")
    omega_result = finalizer.omega(verify=True)
    
    if omega_result["verification"]["verified"]:
        logger.info("✓ Verification PASSED - Files unchanged (as expected in dry-run)")
    else:
        logger.error("✗ Verification FAILED")
        logger.error(f"Issues: {omega_result['verification']['issues']}")
    
    # Step 6: Save finalization report
    report_path = Path("reports/ide_ai_session_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    finalizer.save_report(report_path)
    logger.info(f"Finalization report saved to {report_path}")
    
    # Step 7: Summary
    logger.info("=" * 60)
    logger.info("Session Summary:")
    logger.info(f"  Mode: {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    logger.info(f"  Files processed: {len(results)}")
    logger.info(f"  Verification: {'PASSED' if omega_result['verification']['verified'] else 'FAILED'}")
    logger.info(f"  Manifest: {manifest_path}")
    logger.info(f"  Report: {report_path}")
    
    if DRY_RUN:
        logger.info("")
        logger.info("To run in LIVE mode:")
        logger.info("  1. Review dry-run results")
        logger.info("  2. Set DRY_RUN = False")
        logger.info("  3. Re-run this script")
        logger.info("  WARNING: Live mode creates backups and modifies files")
    
    logger.info("=" * 60)


def example_usage_patterns():
    """
    Example usage patterns for common scenarios.
    
    This function is not executed - it's here for documentation.
    """
    
    # Pattern 1: Simple file hashing
    from hasher import hash_file
    file_hash = hash_file("myfile.txt")
    print(f"Hash: {file_hash}")
    
    # Pattern 2: Create backup before modification
    from backup import BackupManager
    bm = BackupManager()
    backup_path = bm.create_backup("important.txt")
    # Now safe to modify important.txt
    
    # Pattern 3: Verify file integrity
    from manifest import Manifest
    manifest = Manifest.load("manifest.json")
    verification = manifest.verify()
    if verification["verified"]:
        print("All files verified!")
    
    # Pattern 4: Alpha-Omega verification for critical operations
    from core.alpha_omega_finalizer import AlphaOmegaFinalizer
    finalizer = AlphaOmegaFinalizer(name="critical")
    finalizer.alpha(["file1.txt", "file2.txt"])
    # ... perform operations ...
    result = finalizer.omega(verify=True)
    if not result["verification"]["verified"]:
        print("ERROR: Verification failed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = get_logger("ide_ai_runner")
        logger.error(f"Unexpected error: {e}")
        raise
