#!/usr/bin/env python3
"""
PR #25 Manifest Generator

Generates comprehensive manifest for all PR25 artifacts including:
- Seed file
- Synthetic dataset
- LoRA delta
- Generator files
- DAG structure
- Merkle root

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class PR25ManifestGenerator:
    """Generates manifest for PR25 artifacts."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize manifest generator.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.manifest = {
            "pr_id": 25,
            "name": "Deterministic Fractal LoRA Subuniverse",
            "generated_at": datetime.now().astimezone().isoformat(),
            "artifacts": {},
            "hashes": {},
        }
    
    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex-encoded SHA256 hash
        """
        hasher = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def add_artifact(self, name: str, path: Path, artifact_type: str):
        """
        Add an artifact to the manifest.
        
        Args:
            name: Artifact name
            path: Path to artifact
            artifact_type: Type of artifact (seed, dataset, generator, etc.)
        """
        if not path.exists():
            print(f"WARNING: Artifact not found: {path}")
            return
        
        # Compute hash
        file_hash = self.compute_file_hash(path)
        
        # Get relative path
        try:
            rel_path = path.relative_to(self.repo_path)
        except ValueError:
            rel_path = path
        
        # Add to manifest
        self.manifest["artifacts"][name] = {
            "type": artifact_type,
            "path": str(rel_path),
            "size_bytes": path.stat().st_size,
            "hash": file_hash,
        }
        
        self.manifest["hashes"][str(rel_path)] = file_hash
        
        print(f"✓ Added {artifact_type}: {name}")
        print(f"  Path: {rel_path}")
        print(f"  Hash: {file_hash[:16]}...")
    
    def generate_manifest(self) -> Dict[str, Any]:
        """
        Generate complete manifest for PR25.
        
        Returns:
            Manifest dictionary
        """
        print("=" * 80)
        print("PR #25 MANIFEST GENERATION")
        print("=" * 80)
        
        # Add seed file
        print("\n[1/5] Adding seed file...")
        seed_path = self.repo_path / "seed" / "pr_25_seed.yaml"
        self.add_artifact("pr25_seed", seed_path, "seed")
        
        # Add synthetic dataset
        print("\n[2/5] Adding synthetic dataset...")
        dataset_path = self.repo_path / "minimal_ai_ide" / "lora_dataset" / "pr25_synthetic_train.jsonl"
        self.add_artifact("pr25_synthetic_dataset", dataset_path, "dataset")
        
        # Add generator files
        print("\n[3/5] Adding generator files...")
        generator_files = [
            ("pr25_dataset_generator", self.repo_path / "generators" / "pr25_synthetic_dataset.py", "generator"),
            ("fractal_expander", self.repo_path / "generators" / "fractal_expander.py", "generator"),
            ("dag_generator", self.repo_path / "generators" / "dag_generator.py", "generator"),
            ("manifest_generator", self.repo_path / "generators" / "manifest_generator.py", "generator"),
            ("merkle_chain", self.repo_path / "generators" / "merkle_chain.py", "generator"),
        ]
        
        for name, path, artifact_type in generator_files:
            self.add_artifact(name, path, artifact_type)
        
        # Add Merkle root
        print("\n[4/5] Adding Merkle root...")
        merkle_path = self.repo_path / "merkle_roots" / "pr25_merkle_root.txt"
        self.add_artifact("pr25_merkle_root", merkle_path, "merkle_root")
        
        # Add activation script
        print("\n[5/5] Adding activation script...")
        activate_path = self.repo_path / "minimal_ai_ide" / "pr25_activate.py"
        self.add_artifact("pr25_activation", activate_path, "script")
        
        # Add metadata
        self.manifest["metadata"] = {
            "total_artifacts": len(self.manifest["artifacts"]),
            "deterministic": True,
            "reproducible": True,
        }
        
        print("\n" + "=" * 80)
        print(f"MANIFEST COMPLETE: {len(self.manifest['artifacts'])} artifacts")
        print("=" * 80)
        
        return self.manifest
    
    def save_manifest(self, output_path: Path):
        """
        Save manifest to file.
        
        Args:
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, sort_keys=True)
        
        print(f"\n✓ Manifest saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate manifest for PR #25 artifacts"
    )
    parser.add_argument(
        '--repo-path',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Path to repository root'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'merkle_roots' / 'pr25_manifest.json',
        help='Path to output manifest file'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = PR25ManifestGenerator(args.repo_path)
    
    # Generate manifest
    manifest = generator.generate_manifest()
    
    # Save manifest
    generator.save_manifest(args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
