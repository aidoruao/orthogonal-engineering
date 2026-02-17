#!/usr/bin/env python3
"""
Manifest Generator for 1B LOC Architecture

Generates manifests (hash inventories) for batches without storing content.
Outputs JSONL format for incremental processing.

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
from typing import Dict, List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from fractal_expander import FractalExpander


class ManifestGenerator:
    """Generates manifests with hashes for batches."""
    
    def __init__(self, seed: dict, dag: dict, layer_index: int = 0):
        self.seed = seed
        self.dag = dag
        self.expander = FractalExpander(seed, dag, layer_index)
        self.layer_index = layer_index
        self.collapse_map = {}  # Maps sub_dag_hash -> first occurrence for collapse
        
    def generate_batch_manifest(
        self,
        batch_index: int,
        output_file: str
    ) -> Dict[str, any]:
        """
        Generate manifest for a single batch.
        
        Args:
            batch_index: Index of batch (0-99)
            output_file: Output JSONL file path
            
        Returns:
            Statistics dictionary
        """
        batch_id = f"root/batch_{batch_index:06d}"
        
        if batch_id not in self.dag['nodes']:
            raise ValueError(f"Batch not found: {batch_id}")
        
        batch_node = self.dag['nodes'][batch_id]
        
        print(f"Generating manifest for batch {batch_index}...")
        
        stats = {
            "batch_index": batch_index,
            "batch_id": batch_id,
            "entries": 0,
            "total_size": 0
        }
        
        # Find all leaf nodes (lines) under this batch
        leaf_nodes = self._find_leaf_nodes(batch_node)
        
        print(f"  Found {len(leaf_nodes)} leaf nodes")
        
        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate manifest entries
        with open(output_file, 'w') as f:
            for i, leaf_id in enumerate(leaf_nodes):
                # Generate content (in memory only)
                content = self.expander.expand_node(leaf_id)
                
                # Compute hash
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                # Get node info
                node = self.dag['nodes'][leaf_id]
                
                # Check for topological collapse
                sub_dag_hash = node.get('sub_dag_hash')
                collapsed_ref = None
                
                if sub_dag_hash and self.seed.get('topological_collapse', {}).get('enabled', False):
                    if sub_dag_hash in self.collapse_map:
                        # This is a collapsed duplicate
                        collapsed_ref = self.collapse_map[sub_dag_hash]
                    else:
                        # First occurrence - add to map
                        self.collapse_map[sub_dag_hash] = leaf_id
                
                # Create manifest entry
                entry = {
                    "node_id": leaf_id,
                    "hash": content_hash,
                    "size": len(content),
                    "parent": node.get('parent'),
                    "level": node.get('level'),
                    "index": node.get('index'),
                    "layer_index": node.get('layer_index', 0),
                    "universe_index": node.get('universe_index', 0),
                    "sub_seed": node.get('sub_seed'),
                    "sub_dag_hash": sub_dag_hash,
                    "collapsed_ref": collapsed_ref  # Reference to first occurrence if collapsed
                }
                
                # Write to JSONL
                f.write(json.dumps(entry) + '\n')
                
                stats["entries"] += 1
                stats["total_size"] += len(content)
                
                # Progress indicator
                if (i + 1) % 100000 == 0:
                    print(f"    Processed {i + 1:,} / {len(leaf_nodes):,} nodes")
        
        print(f"  Manifest generated: {output_file}")
        print(f"  Entries: {stats['entries']:,}")
        print(f"  Total size: {stats['total_size']:,} bytes")
        
        return stats
    
    def _find_leaf_nodes(self, root_node: dict) -> List[str]:
        """
        Find all leaf nodes under a given root.
        
        Args:
            root_node: Root node to search from
            
        Returns:
            List of leaf node IDs
        """
        leaves = []
        
        def traverse(node_id: str):
            node = self.dag['nodes'][node_id]
            children = node.get('children', [])
            
            if not children:
                # Leaf node
                leaves.append(node_id)
            else:
                # Recurse to children
                for child_id in children:
                    traverse(child_id)
        
        traverse(root_node['id'])
        return sorted(leaves)  # Sort for deterministic ordering
    
    def generate_all_manifests(self, output_dir: str):
        """
        Generate manifests for all batches.
        
        Args:
            output_dir: Directory to write manifest files
        """
        batch_count = self.seed['root']['batch_count']
        
        print(f"Generating manifests for all {batch_count} batches...")
        
        for batch_index in range(batch_count):
            output_file = Path(output_dir) / f"batch_{batch_index:06d}_manifest.jsonl"
            
            try:
                self.generate_batch_manifest(batch_index, str(output_file))
            except Exception as e:
                print(f"ERROR generating manifest for batch {batch_index}: {e}")
                continue
        
        print(f"\n✓ All manifests generated in: {output_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate manifests for batches (Yeshua Standard)"
    )
    parser.add_argument(
        "--seed",
        type=str,
        default="generators/seed_definition.yaml",
        help="Path to seed definition YAML"
    )
    parser.add_argument(
        "--dag",
        type=str,
        default="dag_structure.json",
        help="Path to DAG JSON file"
    )
    parser.add_argument(
        "--batch",
        type=int,
        help="Batch index to generate manifest for (0-99)"
    )
    parser.add_argument(
        "--all-batches",
        action="store_true",
        help="Generate manifests for all batches"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file (for single batch) or directory (for all batches)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="manifests",
        help="Output directory for manifests (default: manifests/)"
    )
    
    args = parser.parse_args()
    
    # Load seed
    print(f"Loading seed from: {args.seed}")
    with open(args.seed, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Load DAG
    print(f"Loading DAG from: {args.dag}")
    with open(args.dag, 'r') as f:
        dag = json.load(f)
    
    # Create generator
    generator = ManifestGenerator(seed, dag)
    
    # Generate based on arguments
    if args.all_batches:
        output_dir = args.output or args.output_dir
        generator.generate_all_manifests(output_dir)
    
    elif args.batch is not None:
        if args.output:
            output_file = args.output
        else:
            output_file = f"{args.output_dir}/batch_{args.batch:06d}_manifest.jsonl"
        
        generator.generate_batch_manifest(args.batch, output_file)
    
    else:
        print("ERROR: Must specify --batch or --all-batches", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
