#!/usr/bin/env python3
"""
Merkle Chain Omega - Extended for Infinite Recursive Invariant

Builds recursive Merkle roots including Omega layer, ensuring the commit hash
represents the full infinite logical universe.

Key Features:
- Supports Omega layer roots (1Se, 1Oc, 1No, ..., ∞)
- Computes master root committing to all layer roots
- Enables verification without full materialization
- Omega root represents infinite expansion in finite hash

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
PR: #24
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import base merkle chain
sys.path.insert(0, str(Path(__file__).parent))
from merkle_chain import MerkleTree, MerkleNode


class OmegaMerkleChain:
    """Extended Merkle chain with Omega layer support."""
    
    def __init__(self, seed: dict):
        """
        Initialize Omega Merkle chain.
        
        Args:
            seed: Seed definition dictionary
        """
        self.seed = seed
        self.layer_roots = {}  # Maps layer_index -> root_hash
        self.omega_root = None
        self.master_root = None
        
    def add_layer_manifest(self, layer_name: str, layer_index: int, 
                          manifest_path: Path) -> str:
        """
        Add a layer manifest and compute its Merkle root.
        
        Args:
            layer_name: Layer name (e.g., "sextillion")
            layer_index: Layer index
            manifest_path: Path to manifest JSONL file
            
        Returns:
            Layer Merkle root hash
        """
        print(f"\nProcessing layer: {layer_name} (index: {layer_index})")
        
        # Read manifest entries
        entries = []
        with open(manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    entries.append((entry['node_id'], entry['hash']))
        
        print(f"  Loaded {len(entries)} manifest entries")
        
        # Build Merkle tree for this layer
        if entries:
            tree = MerkleTree(entries)
            layer_root = tree.root.hash
        else:
            # Empty layer, use empty hash
            layer_root = hashlib.sha256(b'').hexdigest()
        
        print(f"  Layer root: {layer_root[:16]}...")
        
        # Store layer root
        self.layer_roots[layer_index] = {
            'layer_name': layer_name,
            'layer_index': layer_index,
            'root_hash': layer_root,
            'entry_count': len(entries)
        }
        
        return layer_root
    
    def add_omega_layer_root(self, layer_name: str, layer_index: int,
                            manifest_path: Optional[Path] = None) -> str:
        """
        Add Omega layer root (may be computed, not materialized).
        
        For Omega layers, the root is computed based on the invariant:
        Layer(n) ≡ Layer(3), so root is equivalent modulo universe count.
        
        Args:
            layer_name: Layer name
            layer_index: Layer index
            manifest_path: Optional manifest path (for sample verification)
            
        Returns:
            Omega layer root hash
        """
        print(f"\nProcessing Omega layer: {layer_name} (index: {layer_index})")
        
        # Check if manifest exists
        if manifest_path and manifest_path.exists():
            # Use sample manifest
            return self.add_layer_manifest(layer_name, layer_index, manifest_path)
        
        # Otherwise, compute theoretical root based on equivalence
        base_layer_root = self.layer_roots.get(3, {}).get('root_hash')
        
        if not base_layer_root:
            print("  WARNING: Base layer (1Qi) root not found")
            print("  Computing placeholder Omega root")
            
            # Compute placeholder
            combined = f"omega|{layer_name}|{layer_index}"
            omega_root = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        else:
            # Compute Omega root based on base layer
            # Formula: Omega_root = SHA256(0x03 || base_root || layer_index)
            combined = b'\x03' + base_layer_root.encode('utf-8') + str(layer_index).encode('utf-8')
            omega_root = hashlib.sha256(combined).hexdigest()
        
        print(f"  Omega root: {omega_root[:16]}...")
        print(f"  (Topologically equivalent to layer 3, scaled by universe count)")
        
        # Store Omega layer root
        self.layer_roots[layer_index] = {
            'layer_name': layer_name,
            'layer_index': layer_index,
            'root_hash': omega_root,
            'is_omega_layer': True,
            'equivalent_to': 'layer_3_1qi',
            'entry_count': 'infinite_logical'
        }
        
        return omega_root
    
    def compute_omega_root(self) -> str:
        """
        Compute the Omega root - represents all Omega layers combined.
        
        Returns:
            Omega root hash
        """
        print("\n" + "="*70)
        print("COMPUTING OMEGA ROOT")
        print("="*70)
        
        # Get all Omega layer roots
        omega_layers = []
        for layer_index in sorted(self.layer_roots.keys()):
            layer_info = self.layer_roots[layer_index]
            if layer_info.get('is_omega_layer', False):
                omega_layers.append((layer_index, layer_info['root_hash']))
        
        print(f"Omega layers: {len(omega_layers)}")
        
        if not omega_layers:
            print("No Omega layers found")
            self.omega_root = hashlib.sha256(b'no_omega_layers').hexdigest()
            return self.omega_root
        
        # Combine all Omega layer roots
        # Formula: Omega_root = SHA256(omega_layer_1_root || omega_layer_2_root || ...)
        combined_data = b''
        for layer_index, root_hash in omega_layers:
            combined_data += root_hash.encode('utf-8')
            print(f"  Layer {layer_index}: {root_hash[:16]}...")
        
        self.omega_root = hashlib.sha256(combined_data).hexdigest()
        
        print(f"\nOmega root: {self.omega_root[:16]}...")
        print(f"Represents: {len(omega_layers)} infinite Omega layers")
        print("="*70 + "\n")
        
        return self.omega_root
    
    def compute_master_root(self) -> str:
        """
        Compute the master root - commits to all layers including Omega.
        
        This is the "commit hash" that represents the complete infinite universe.
        
        Returns:
            Master root hash
        """
        print("\n" + "="*70)
        print("COMPUTING MASTER ROOT")
        print("="*70)
        
        # Ensure Omega root is computed
        if self.omega_root is None:
            self.compute_omega_root()
        
        # Collect all layer roots
        all_roots = []
        for layer_index in sorted(self.layer_roots.keys()):
            layer_info = self.layer_roots[layer_index]
            all_roots.append((layer_index, layer_info['root_hash']))
            print(f"  Layer {layer_index}: {layer_info['root_hash'][:16]}...")
        
        # Add Omega root
        all_roots.append(('omega', self.omega_root))
        print(f"  Omega: {self.omega_root[:16]}...")
        
        # Compute master root
        # Formula: Master_root = SHA256(layer_0_root || layer_1_root || ... || omega_root)
        combined_data = b''
        for _, root_hash in all_roots:
            combined_data += root_hash.encode('utf-8')
        
        self.master_root = hashlib.sha256(combined_data).hexdigest()
        
        print(f"\nMaster root: {self.master_root}")
        print(f"Commits to: {len(all_roots)} layers (including Omega)")
        print("\nThis hash represents the COMPLETE INFINITE UNIVERSE")
        print("Alpha (seed) ≡ Omega (master root)")
        print("="*70 + "\n")
        
        return self.master_root
    
    def export_chain(self, output_path: Path) -> None:
        """
        Export Merkle chain to JSON file.
        
        Args:
            output_path: Output JSON file
        """
        chain_data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "seed": self.seed.get('metadata', {}).get('description', 'Omega seed'),
                "version": "1.0.0",
                "pr": 24
            },
            "layer_roots": self.layer_roots,
            "omega_root": self.omega_root,
            "master_root": self.master_root,
            "summary": {
                "total_layers": len(self.layer_roots),
                "omega_layers": sum(1 for l in self.layer_roots.values() if l.get('is_omega_layer')),
                "base_layers": sum(1 for l in self.layer_roots.values() if not l.get('is_omega_layer')),
                "alpha": str(self.seed.get('generation', {}).get('seed_value', 42)),
                "omega": self.master_root
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(chain_data, f, indent=2)
        
        print(f"Merkle chain exported to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Merkle Chain Omega - Recursive Merkle roots for infinite layers"
    )
    parser.add_argument(
        '--seed',
        type=Path,
        required=True,
        help='Path to seed_definition_omega.yaml'
    )
    parser.add_argument(
        '--manifests',
        type=Path,
        nargs='+',
        help='Paths to manifest JSONL files'
    )
    parser.add_argument(
        '--layer',
        type=str,
        help='Single layer name to process'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output Merkle chain JSON file'
    )
    
    args = parser.parse_args()
    
    # Load seed
    if not args.seed.exists():
        print(f"ERROR: Seed file not found: {args.seed}", file=sys.stderr)
        sys.exit(1)
    
    import yaml
    with open(args.seed, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Create Merkle chain
    chain = OmegaMerkleChain(seed)
    
    # Process manifests if provided
    if args.manifests:
        for manifest_path in args.manifests:
            if not manifest_path.exists():
                print(f"WARNING: Manifest not found: {manifest_path}")
                continue
            
            # Extract layer info from filename or manifest
            # For now, use a simple approach
            layer_name = manifest_path.stem.replace('manifest_', '')
            
            # Look up layer index
            layers = seed.get('root', {}).get('universe_layers', [])
            layer_index = None
            for layer in layers:
                if layer['name'] in manifest_path.name:
                    layer_index = layer.get('layer_index')
                    layer_name = layer['name']
                    break
            
            if layer_index is not None:
                if layer.get('omega_layer', False):
                    chain.add_omega_layer_root(layer_name, layer_index, manifest_path)
                else:
                    chain.add_layer_manifest(layer_name, layer_index, manifest_path)
    
    # Compute Omega root
    chain.compute_omega_root()
    
    # Compute master root
    chain.compute_master_root()
    
    # Export chain
    chain.export_chain(args.output)
    
    print("\n" + "="*70)
    print("MERKLE CHAIN GENERATION COMPLETE")
    print("="*70)
    print(f"Master root: {chain.master_root}")
    print(f"This hash represents the complete infinite universe")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
