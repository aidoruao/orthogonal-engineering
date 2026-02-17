#!/usr/bin/env python3
"""
Batch Materializer for 1B LOC Architecture

Materializes specific batches/shards from DAG with lazy generation.
Supports depth-aware materialization across universe layers.
Computes hashes and verifies against manifests.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 2.0.0 (PR #23)
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Import our fractal expander
sys.path.insert(0, str(Path(__file__).parent))
from fractal_expander import FractalExpander


class BatchMaterializer:
    """Materializes batches with verification."""
    
    def __init__(self, seed: dict, dag: dict, layer_index: int = 0, universe_index: int = 0):
        self.seed = seed
        self.dag = dag
        self.layer_index = layer_index
        self.universe_index = universe_index
        self.expander = FractalExpander(seed, dag, layer_index)
        
    def materialize_batch(
        self,
        batch_index: int,
        output_dir: Optional[str] = None,
        verify: bool = False,
        max_files: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Materialize a specific batch.
        
        Args:
            batch_index: Index of batch to materialize (0-99)
            output_dir: Directory to write files (None = don't write)
            verify: Whether to verify against manifest
            max_files: Maximum files to generate (for testing)
            
        Returns:
            Dictionary with statistics
        """
        batch_id = f"root/batch_{batch_index:06d}"
        
        if batch_id not in self.dag['nodes']:
            raise ValueError(f"Batch not found: {batch_id}")
        
        batch_node = self.dag['nodes'][batch_id]
        
        print(f"Materializing batch {batch_index}...")
        print(f"  Batch ID: {batch_id}")
        print(f"  Layer: {self.layer_index}")
        print(f"  Universe: {self.universe_index}")
        print(f"  Modules: {len(batch_node.get('children', []))}")
        
        # Check if this batch can spawn sub-universes
        sub_dag_hash = batch_node.get('sub_dag_hash')
        if sub_dag_hash:
            print(f"  Sub-universe spawn point: {sub_dag_hash[:16]}...")
        
        stats = {
            "batch_index": batch_index,
            "batch_id": batch_id,
            "layer_index": self.layer_index,
            "universe_index": self.universe_index,
            "files_generated": 0,
            "total_size": 0,
            "hashes": {},
            "sub_dag_hash": sub_dag_hash
        }
        
        # Process each module
        files_generated_count = 0
        for module_id in batch_node.get('children', []):
            module_node = self.dag['nodes'][module_id]
            
            # Create module directory if writing
            if output_dir:
                module_path = Path(output_dir) / module_id.split('/', 1)[1]
                module_path.mkdir(parents=True, exist_ok=True)
                
                # Generate __init__.py
                init_content = self.expander.expand_node(module_id)
                init_file = module_path / '__init__.py'
                init_file.write_text(init_content)
                stats["files_generated"] += 1
                stats["total_size"] += len(init_content)
            
            # Process each file
            for file_id in module_node.get('children', []):
                # Check max_files limit
                if max_files and files_generated_count >= max_files:
                    print(f"  Reached max_files limit ({max_files})")
                    break
                
                file_content = self.expander.expand_node(file_id)
                file_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()
                
                stats["hashes"][file_id] = file_hash
                stats["total_size"] += len(file_content)
                stats["files_generated"] += 1
                files_generated_count += 1
                
                # Write file if output_dir specified
                if output_dir:
                    file_path = Path(output_dir) / file_id.split('/', 1)[1].replace('/', Path.sep)
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Add .py extension if not present
                    if not file_path.suffix:
                        file_path = file_path.with_suffix('.py')
                    
                    file_path.write_text(file_content)
            
            # Break outer loop if max reached
            if max_files and files_generated_count >= max_files:
                break
        
        print(f"\nBatch {batch_index} materialization complete:")
        print(f"  Files generated: {stats['files_generated']}")
        print(f"  Total size: {stats['total_size']:,} bytes")
        
        return stats
    
    def materialize_single_node(
        self,
        node_id: str,
        output_file: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Materialize a single node.
        
        Args:
            node_id: Full node ID
            output_file: Optional file to write to
            
        Returns:
            Tuple of (content, hash)
        """
        content = self.expander.expand_node(node_id)
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(content)
        
        return content, content_hash
    
    def verify_against_manifest(
        self,
        batch_index: int,
        manifest_file: str
    ) -> bool:
        """
        Verify batch against manifest.
        
        Args:
            batch_index: Batch to verify
            manifest_file: Path to manifest JSONL
            
        Returns:
            True if all hashes match
        """
        print(f"Verifying batch {batch_index} against manifest...")
        
        # Load manifest
        manifest = {}
        with open(manifest_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                manifest[entry['node_id']] = entry['hash']
        
        # Materialize and compare
        stats = self.materialize_batch(batch_index, output_dir=None, verify=False)
        
        mismatches = []
        for node_id, computed_hash in stats['hashes'].items():
            if node_id in manifest:
                expected_hash = manifest[node_id]
                if computed_hash != expected_hash:
                    mismatches.append({
                        'node_id': node_id,
                        'expected': expected_hash,
                        'computed': computed_hash
                    })
        
        if mismatches:
            print(f"\n❌ Verification FAILED: {len(mismatches)} hash mismatches")
            for mismatch in mismatches[:5]:  # Show first 5
                print(f"  {mismatch['node_id']}")
                print(f"    Expected: {mismatch['expected']}")
                print(f"    Computed: {mismatch['computed']}")
            return False
        else:
            print(f"✓ Verification PASSED: All hashes match")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Materialize batches from DAG (Yeshua Standard)"
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
        help="Batch index to materialize (0-99)"
    )
    parser.add_argument(
        "--node",
        type=str,
        help="Specific node ID to materialize"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory or file"
    )
    parser.add_argument(
        "--verify",
        type=str,
        help="Verify against manifest file"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print content to stdout instead of file"
    )
    parser.add_argument(
        "--layer-index",
        type=int,
        default=0,
        help="Universe layer index (0=1B, 1=1T, 2=1Qa, 3=1Qi)"
    )
    parser.add_argument(
        "--universe-index",
        type=int,
        default=0,
        help="Universe index within layer"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum files to generate (for testing)"
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
    
    # Create materializer
    materializer = BatchMaterializer(
        seed, 
        dag, 
        layer_index=args.layer_index,
        universe_index=args.universe_index
    )
    
    # Materialize based on arguments
    if args.batch is not None:
        # Materialize batch
        stats = materializer.materialize_batch(
            args.batch,
            output_dir=args.output,
            max_files=args.max_files
        )
        
        # Verify if requested
        if args.verify:
            materializer.verify_against_manifest(args.batch, args.verify)
    
    elif args.node:
        # Materialize single node
        output_file = args.output if not args.stdout else None
        content, hash_value = materializer.materialize_single_node(
            args.node,
            output_file=output_file
        )
        
        if args.stdout:
            print(content)
        else:
            print(f"Node materialized: {args.node}")
            print(f"  Hash: {hash_value}")
            if args.output:
                print(f"  Output: {args.output}")
    
    else:
        print("ERROR: Must specify --batch or --node", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
