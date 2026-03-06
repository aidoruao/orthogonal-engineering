#!/usr/bin/env python3
"""
Food Cart Manifest Generator
=============================

Generates canonical manifest from the Food Cart DAG.

Each node in the DAG gets an entry in the manifest.

Implements INV-MAN-001 through INV-MAN-003.

Authority: out/food_cart_dag.json
Version: 1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ManifestGenerator:
    """Generates canonical manifest from DAG."""
    
    def __init__(self, dag_path: str):
        """
        Initialize generator.
        
        Args:
            dag_path: Path to food_cart_dag.json
        """
        self.dag_path = Path(dag_path)
        
        # Load DAG
        with open(self.dag_path, 'r') as f:
            self.dag = json.load(f)
            
        self.metadata = self.dag['metadata']
        self.nodes = self.dag['nodes']
        
    def generate_manifest(self, output_path: str) -> None:
        """
        Generate canonical manifest.
        
        INV-MAN-001: Manifest must contain every DAG node.
        INV-MAN-003: Manifest must regenerate deterministically.
        
        Args:
            output_path: Path to write manifest JSONL file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 Generating manifest for {len(self.nodes)} nodes...")
        
        # Sort nodes by node_id for deterministic ordering (INV-MAN-003)
        sorted_node_ids = sorted(self.nodes.keys())
        
        entries = []
        with open(output_file, 'w') as f:
            for node_id in sorted_node_ids:
                node = self.nodes[node_id]
                
                # Determine artifact path based on level
                artifact_path = self._get_artifact_path(node)
                
                # Create manifest entry
                entry = {
                    "node_id": node_id,
                    "level": node['level'],
                    "content_hash": node['content_hash'],
                    "artifact_path": artifact_path,
                    "timestamp": self.metadata['generated_at'],
                    "generator": self.metadata['generator_version'],
                    "commit": self.metadata['commit']
                }
                
                # Write as JSONL (one JSON object per line)
                f.write(json.dumps(entry, sort_keys=True) + '\n')
                entries.append(entry)
                
        print(f"✅ Wrote {len(entries)} manifest entries to {output_path}")
        
        return entries
        
    def _get_artifact_path(self, node: dict) -> str:
        """
        Get artifact path for a node.
        
        Args:
            node: Node dictionary
            
        Returns:
            Relative path to artifact
        """
        level = node['level']
        name = node['name']
        
        if level == 'menu':
            return "out/food_cart_dag.json"
        elif level == 'dish':
            return f"data/dishes/{name}.json"
        elif level == 'phase':
            # Phases are embedded in dish projections
            return f"data/dishes/{name.split('_')[0]}.json"
        elif level == 'step':
            # Steps are embedded in dish projections
            dish_name = name.split('_')[0]
            return f"data/dishes/{dish_name}.json"
        else:
            return "out/food_cart_dag.json"
            
    def verify_manifest(self, manifest_path: str) -> bool:
        """
        Verify manifest against invariants.
        
        Returns:
            True if all invariants hold, False otherwise
        """
        manifest_file = Path(manifest_path)
        
        if not manifest_file.exists():
            print(f"❌ Manifest file not found: {manifest_path}")
            return False
            
        print(f"🔍 Verifying manifest...")
        
        # Load manifest entries
        entries = []
        with open(manifest_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                    
        # INV-MAN-001: Manifest must contain every DAG node
        manifest_node_ids = set(e['node_id'] for e in entries)
        dag_node_ids = set(self.nodes.keys())
        
        if manifest_node_ids != dag_node_ids:
            missing = dag_node_ids - manifest_node_ids
            extra = manifest_node_ids - dag_node_ids
            
            if missing:
                print(f"❌ INV-MAN-001 failed: Missing nodes: {missing}")
            if extra:
                print(f"❌ INV-MAN-001 failed: Extra nodes: {extra}")
            return False
            
        print(f"   ✅ INV-MAN-001: All {len(dag_node_ids)} nodes present")
        
        # Verify content hashes match
        for entry in entries:
            node_id = entry['node_id']
            node = self.nodes[node_id]
            
            if entry['content_hash'] != node['content_hash']:
                print(f"❌ Content hash mismatch for node {node_id}")
                return False
                
        print(f"   ✅ All content hashes match")
        
        # INV-MAN-003: Manifest must regenerate deterministically
        # Check that entries are sorted by node_id
        entry_ids = [e['node_id'] for e in entries]
        if entry_ids != sorted(entry_ids):
            print(f"❌ INV-MAN-003 failed: Entries not in deterministic order")
            return False
            
        print(f"   ✅ INV-MAN-003: Deterministic ordering")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate manifest from Food Cart DAG"
    )
    parser.add_argument(
        "--dag",
        default="out/food_cart_dag.json",
        help="Path to DAG JSON file"
    )
    parser.add_argument(
        "--output",
        default="out/food_cart_manifest.jsonl",
        help="Output path for manifest JSONL"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify manifest after generation"
    )
    
    args = parser.parse_args()
    
    # Generate
    generator = ManifestGenerator(args.dag)
    generator.generate_manifest(args.output)
    
    # Verify if requested
    if args.verify:
        print()
        valid = generator.verify_manifest(args.output)
        if not valid:
            print()
            print("❌ Manifest verification failed!")
            sys.exit(1)
        else:
            print()
            print("✅ Manifest verification passed!")


if __name__ == "__main__":
    main()
