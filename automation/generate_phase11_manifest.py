"""
Phase 11 Cryptographic Manifest Update Script

Generates SHA256 manifest for Phase 11 artifacts and links back to Phase 9 and Phase 8.
Implements Phase 11 A7 requirements.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Phase11ManifestGenerator:
    """
    Generates cryptographic manifest for Phase 11 artifacts.

    Implements Phase 11 A7 requirements:
    - Recompute SHA256 for all artifacts
    - Append Phase 11 section to manifest
    - Link hashes back to Phase 9 and Phase 8
    """

    def __init__(self):
        """Initialize manifest generator."""
        self.manifest_path = (
            Path("documentation") / "sha256_manifests" / "phase11_manifest.json"
        )
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        # Phase 11 artifacts
        self.phase11_artifacts = [
            # A1: Failure Persistence Layer
            "toolkit/oe/failure_ledger.py",
            # A2: Adversarial Replay Engine
            "toolkit/oe/replay_engine.py",
            # A3: Suppressed Signal Detector
            "toolkit/oe/suppressed_signal_detector.py",
            # A4: IDE Behavior Accounting
            "toolkit/oe/ide_behavior_accounting.py",
            # A6: Verification Script
            "automation/verify_phase11_atomicity.py",
            # This script
            "automation/generate_phase11_manifest.py",
            # Phase 11 directories
            "logs/failure_ledger/",
            "logs/replay_engine/",
            "logs/signal_captures/",
            "logs/ide_actions/",
        ]

        # Load existing manifests if available
        self.phase8_manifest = self._load_phase_manifest(8)
        self.phase9_manifest = self._load_phase_manifest(9)

    def _load_phase_manifest(self, phase: int) -> Optional[Dict[str, Any]]:
        """Load manifest for a specific phase."""
        manifest_path = (
            Path("documentation") / "sha256_manifests" / f"phase{phase}_manifest.json"
        )

        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _calculate_directory_hash(self, dir_path: Path) -> str:
        """Calculate combined hash of all files in a directory."""
        if not dir_path.exists() or not dir_path.is_dir():
            return "DIRECTORY_NOT_FOUND"

        file_hashes = []
        for file_path in sorted(dir_path.rglob("*")):
            if file_path.is_file():
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    relative_path = file_path.relative_to(dir_path)
                    file_hashes.append(f"{relative_path}:{file_hash}")
                except Exception:
                    continue

        if not file_hashes:
            return "EMPTY_DIRECTORY"

        combined = "\n".join(file_hashes)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def _get_artifact_info(self, artifact_path: str) -> Dict[str, Any]:
        """Get information about an artifact."""
        path = Path(artifact_path)

        info = {
            "artifact": artifact_path,
            "exists": path.exists(),
            "type": "unknown",
        }

        if path.exists():
            if path.is_file():
                info["type"] = "file"
                info["size"] = path.stat().st_size
                info["sha256"] = self._calculate_file_hash(path)
                info["modified"] = datetime.fromtimestamp(
                    path.stat().st_mtime, tz=timezone.utc
                ).isoformat()
            elif path.is_dir():
                info["type"] = "directory"
                info["sha256"] = self._calculate_directory_hash(path)
                info["file_count"] = len(list(path.rglob("*")))

        return info

    def _get_phase8_linkage(self) -> Dict[str, Any]:
        """Get cryptographic linkage to Phase 8."""
        linkage = {
            "phase": 8,
            "linkage_type": "methodological_foundation",
            "description": "Phase 11 builds upon Phase 8 atomic workflow foundation",
            "verified": False,
            "artifacts": [],
        }

        if self.phase8_manifest:
            linkage["verified"] = True
            linkage["manifest_hash"] = self.phase8_manifest.get("manifest_hash")
            linkage["generated_at"] = self.phase8_manifest.get("generated_at")

            # Link to key Phase 8 artifacts
            key_artifacts = [
                "automation/phase8_atomic_workflow.py",
                "automation/run_full_audit_with_trace.py",
                "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
            ]

            for artifact in key_artifacts:
                if artifact in self.phase8_manifest.get("artifacts", {}):
                    linkage["artifacts"].append(
                        {
                            "artifact": artifact,
                            "phase8_hash": self.phase8_manifest["artifacts"][
                                artifact
                            ].get("sha256"),
                            "exists": Path(artifact).exists(),
                            "current_hash": self._calculate_file_hash(Path(artifact))
                            if Path(artifact).exists()
                            else "MISSING",
                        }
                    )

        return linkage

    def _get_phase9_linkage(self) -> Dict[str, Any]:
        """Get cryptographic linkage to Phase 9."""
        linkage = {
            "phase": 9,
            "linkage_type": "methodological_expansion",
            "description": "Phase 11 extends Phase 9 advanced causal analysis capabilities",
            "verified": False,
            "artifacts": [],
        }

        if self.phase9_manifest:
            linkage["verified"] = True
            linkage["manifest_hash"] = self.phase9_manifest.get("manifest_hash")
            linkage["generated_at"] = self.phase9_manifest.get("generated_at")

            # Link to key Phase 9 artifacts
            key_artifacts = [
                "toolkit/oe/advanced_evidence.py",
                "toolkit/oe/causal_analyzer.py",
                "toolkit/oe/workflow_dsl.py",
                "glass-box/GLASS_BOX_BOUNDARY_v1.12.html",
            ]

            for artifact in key_artifacts:
                if artifact in self.phase9_manifest.get("artifacts", {}):
                    linkage["artifacts"].append(
                        {
                            "artifact": artifact,
                            "phase9_hash": self.phase9_manifest["artifacts"][
                                artifact
                            ].get("sha256"),
                            "exists": Path(artifact).exists(),
                            "current_hash": self._calculate_file_hash(Path(artifact))
                            if Path(artifact).exists()
                            else "MISSING",
                        }
                    )

        return linkage

    def generate_manifest(self) -> Dict[str, Any]:
        """Generate Phase 11 manifest."""
        print("Generating Phase 11 Cryptographic Manifest...")
        print("=" * 60)

        # Collect artifact information
        artifacts = {}
        total_size = 0
        files_hashed = 0

        for artifact_path in self.phase11_artifacts:
            print(f"Processing: {artifact_path}")
            info = self._get_artifact_info(artifact_path)
            artifacts[artifact_path] = info

            if info["exists"] and info["type"] == "file":
                total_size += info.get("size", 0)
                files_hashed += 1

        # Get cryptographic linkages
        phase8_linkage = self._get_phase8_linkage()
        phase9_linkage = self._get_phase9_linkage()

        # Create final manifest
        manifest = {
            "manifest_id": f"PHASE11-MANIFEST-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "schema_version": "1.13",
            "phase": 11,
            "description": "Phase 11: Autonomous Failure Accounting & Adversarial Lock-In",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": artifacts,
            "statistics": {
                "total_artifacts": len(self.phase11_artifacts),
                "artifacts_found": sum(1 for a in artifacts.values() if a["exists"]),
                "artifacts_missing": sum(
                    1 for a in artifacts.values() if not a["exists"]
                ),
                "files_hashed": files_hashed,
                "total_size_bytes": total_size,
                "directories_included": sum(
                    1 for a in artifacts.values() if a.get("type") == "directory"
                ),
            },
            "cryptographic_linkage": {
                "phase8": phase8_linkage,
                "phase9": phase9_linkage,
                "chain_integrity": phase8_linkage["verified"]
                and phase9_linkage["verified"],
            },
            "verification": {
                "method": "SHA256",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "verified_by": "Phase11ManifestGenerator",
            },
        }

        # Calculate manifest hash (on the manifest WITHOUT the hash field)
        manifest_json = json.dumps(
            manifest, indent=2, sort_keys=True, ensure_ascii=False
        )
        manifest_hash = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()

        # Add the hash to the manifest
        manifest["manifest_hash"] = manifest_hash

        # Save manifest
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"\nManifest saved to: {self.manifest_path}")
        print(f"Manifest ID: {manifest['manifest_id']}")
        print(f"Manifest Hash: {manifest_hash}")
        print(
            f"Artifacts processed: {manifest['statistics']['artifacts_found']}/{manifest['statistics']['total_artifacts']}"
        )
        print(
            f"Cryptographic chain integrity: {manifest['cryptographic_linkage']['chain_integrity']}"
        )
        print("=" * 60)

        return manifest

    def verify_manifest(self) -> Dict[str, Any]:
        """Verify manifest integrity."""
        if not self.manifest_path.exists():
            return {"valid": False, "error": "Manifest file not found"}

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Get stored hash
            stored_hash = manifest.get("manifest_hash")

            # Create a copy without the manifest_hash field for verification
            manifest_copy = manifest.copy()
            manifest_copy.pop("manifest_hash", None)

            # Calculate hash on the copy (same as during generation)
            manifest_json = json.dumps(
                manifest_copy, indent=2, sort_keys=True, ensure_ascii=False
            )
            calculated_hash = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()

            valid = stored_hash == calculated_hash

            result = {
                "valid": valid,
                "stored_hash": stored_hash,
                "calculated_hash": calculated_hash,
                "hash_match": valid,
                "manifest_id": manifest.get("manifest_id"),
                "phase": manifest.get("phase"),
            }

            if not valid:
                result["error"] = "Hash mismatch"

            return result

        except Exception as e:
            return {"valid": False, "error": str(e)}


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 11 Cryptographic Manifest Generator"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing manifest instead of generating new one",
    )

    parser.add_argument(
        "--output", type=str, help="Custom output path for manifest file"
    )

    args = parser.parse_args()

    generator = Phase11ManifestGenerator()

    if args.output:
        generator.manifest_path = Path(args.output)
        generator.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if args.verify:
        print("Verifying Phase 11 Manifest...")
        result = generator.verify_manifest()

        if result["valid"]:
            print(f"✓ Manifest is valid")
            print(f"  Manifest ID: {result['manifest_id']}")
            print(f"  Phase: {result['phase']}")
            print(f"  Hash: {result['stored_hash'][:16]}...")
            return 0
        else:
            print(f"✗ Manifest verification failed")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            if "stored_hash" in result and "calculated_hash" in result:
                print(f"  Stored hash: {result['stored_hash'][:16]}...")
                print(f"  Calculated hash: {result['calculated_hash'][:16]}...")
            return 1
    else:
        manifest = generator.generate_manifest()

        # Verify immediately after generation
        print("\nVerifying generated manifest...")
        verification = generator.verify_manifest()

        if verification["valid"]:
            print("✓ Manifest generated and verified successfully")
            return 0
        else:
            print("✗ Manifest verification failed after generation")
            print(f"  Error: {verification.get('error', 'Unknown error')}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
