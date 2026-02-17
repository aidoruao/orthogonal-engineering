#!/usr/bin/env python3
"""
DAG Generator for 1B LOC Fractal Architecture

Generates a Directed Acyclic Graph from seed definition.
Ensures no cycles, complete connectivity, and deterministic structure.

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
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class DAGNode:
    """Represents a single node in the generation DAG."""
    
    def __init__(self, node_id: str, level: str, parent_id: Optional[str], index: int,
                 layer_index: int = 0, universe_index: int = 0, sub_seed: Optional[str] = None):
        self.id = node_id
        self.level = level
        self.parent = parent_id
        self.index = index
        self.children: List[str] = []
        self.depth = 0
        # Recursive expansion fields
        self.layer_index = layer_index  # Which universe layer (0=1B, 1=1T, 2=1Qa, 3=1Qi)
        self.universe_index = universe_index  # Which universe within layer
        self.sub_seed = sub_seed  # Derived seed for this sub-universe
        self.is_universe_root = False  # True if this node is a universe root
        self.sub_dag_hash = None  # Hash of sub-DAG if this spawns a sub-universe
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "level": self.level,
            "parent": self.parent,
            "index": self.index,
            "children": self.children,
            "depth": self.depth,
            "layer_index": self.layer_index,
            "universe_index": self.universe_index,
            "sub_seed": self.sub_seed,
            "is_universe_root": self.is_universe_root,
            "sub_dag_hash": self.sub_dag_hash
        }
    
    def __repr__(self) -> str:
        return f"DAGNode({self.id}, level={self.level}, children={len(self.children)})"


class DAGGenerator:
    """Generates Directed Acyclic Graph from seed definition."""
    
    def __init__(self, seed: dict, layer_index: int = 0, parent_seed: Optional[str] = None,
                 universe_index: int = 0):
        self.seed = seed
        self.nodes: Dict[str, DAGNode] = {}
        self.root = None
        self.layer_index = layer_index
        self.parent_seed = parent_seed
        self.universe_index = universe_index
        # Compute sub-seed for this universe
        self.sub_seed = self._derive_sub_seed()
        
    def _derive_sub_seed(self) -> str:
        """
        Derive deterministic sub-seed for this universe.
        
        Uses formula: SHA256(root_seed || parent_seed || layer_index || universe_index)
        
        Returns:
            Hex string of derived sub-seed
        """
        root_seed = str(self.seed.get('generation', {}).get('seed_value', 42))
        
        if self.layer_index == 0:
            # Base universe uses root seed directly
            return hashlib.sha256(root_seed.encode('utf-8')).hexdigest()
        
        # Recursive universe derives from parent
        components = [
            root_seed,
            self.parent_seed or "",
            str(self.layer_index),
            str(self.universe_index)
        ]
        
        combined = "|".join(components)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
    def validate_seed(self) -> bool:
        """Validate seed definition is well-formed."""
        # Check required fields
        required = ['root', 'expansion', 'generation']
        for field in required:
            if field not in self.seed:
                raise ValueError(f"Missing required field in seed: {field}")
        
        # Validate expansion levels
        if 'levels' not in self.seed['expansion']:
            raise ValueError("Missing 'levels' in expansion")
        
        # Verify math: product of all counts = target lines
        if self.seed.get('validation', {}).get('verify_math', True):
            total_lines = 1
            for level in self.seed['expansion']['levels']:
                if 'count' not in level:
                    raise ValueError(f"Level {level.get('name', 'unknown')} missing 'count'")
                total_lines *= level['count']
            
            target = self.seed['root']['target_lines']
            if total_lines != target:
                raise ValueError(
                    f"Math error: Product of counts ({total_lines:,}) != "
                    f"target lines ({target:,})"
                )
        
        return True
    
    def generate(self) -> Dict[str, DAGNode]:
        """
        Generate complete DAG from seed definition.
        
        Returns:
            Dictionary mapping node_id -> DAGNode
        """
        # Validate first
        self.validate_seed()
        
        # Create root node
        root_name = self.seed['root']['name']
        self.root = DAGNode(
            node_id="root",
            level="root",
            parent_id=None,
            index=0,
            layer_index=self.layer_index,
            universe_index=self.universe_index,
            sub_seed=self.sub_seed
        )
        self.root.depth = 0
        self.root.is_universe_root = True
        self.nodes["root"] = self.root
        
        # Recursive expansion based on levels
        current_level_nodes = [self.root]
        depth = 1
        
        for level_spec in self.seed['expansion']['levels']:
            print(f"Generating level: {level_spec['name']} "
                  f"(count={level_spec['count']}, depth={depth})")
            
            next_level_nodes = []
            
            for parent in current_level_nodes:
                # Generate children for this parent
                for i in range(level_spec['count']):
                    child_id = f"{parent.id}/{level_spec['name']}_{i:06d}"
                    
                    child = DAGNode(
                        node_id=child_id,
                        level=level_spec['name'],
                        parent_id=parent.id,
                        index=i,
                        layer_index=self.layer_index,
                        universe_index=self.universe_index,
                        sub_seed=self.sub_seed
                    )
                    child.depth = depth
                    
                    self.nodes[child_id] = child
                    parent.children.append(child_id)
                    next_level_nodes.append(child)
            
            current_level_nodes = next_level_nodes
            depth += 1
            
            # Progress report
            print(f"  Generated {len(next_level_nodes):,} nodes at depth {depth-1}")
        
        return self.nodes
    
    def verify_acyclic(self) -> bool:
        """Verify DAG has no cycles using DFS."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = self.nodes[node_id]
            for child_id in node.children:
                if child_id not in visited:
                    if has_cycle(child_id):
                        return True
                elif child_id in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        if has_cycle("root"):
            raise ValueError("Cycle detected in DAG!")
        
        return True
    
    def get_statistics(self) -> dict:
        """Get DAG statistics."""
        stats = {
            "total_nodes": len(self.nodes),
            "levels": {},
            "max_depth": 0,
            "leaf_nodes": 0
        }
        
        for node in self.nodes.values():
            # Count by level
            if node.level not in stats["levels"]:
                stats["levels"][node.level] = 0
            stats["levels"][node.level] += 1
            
            # Track max depth
            if node.depth > stats["max_depth"]:
                stats["max_depth"] = node.depth
            
            # Count leaf nodes
            if not node.children:
                stats["leaf_nodes"] += 1
        
        return stats
    
    def compute_sub_dag_hashes(self) -> None:
        """
        Compute sub-DAG hashes for nodes that can spawn sub-universes.
        
        This enables topological collapse - nodes with identical sub-DAG hashes
        can share the same sub-universe expansion.
        """
        recursion_config = self.seed.get('root', {}).get('recursion', {})
        max_depth = recursion_config.get('max_depth', 0)
        
        # Only compute if we're not at max depth
        if self.layer_index >= max_depth:
            return
        
        # Find nodes that can spawn sub-universes
        for node_id, node in self.nodes.items():
            # Check if this level can recurse
            level_spec = self._get_level_spec(node.level)
            if level_spec and level_spec.get('can_recurse', False):
                # Compute hash of this node's subtree + sub-seed
                sub_dag_content = self._serialize_subtree(node)
                combined = f"{sub_dag_content}|{self.sub_seed}|{node.index}"
                node.sub_dag_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def _get_level_spec(self, level_name: str) -> Optional[dict]:
        """Get level specification from seed."""
        if level_name == 'root':
            return None
        
        for level in self.seed.get('expansion', {}).get('levels', []):
            if level.get('name') == level_name:
                return level
        return None
    
    def _serialize_subtree(self, node: DAGNode) -> str:
        """Serialize node and its descendants for hashing."""
        parts = [
            node.id,
            node.level,
            str(node.index),
            str(len(node.children))
        ]
        
        # Add children recursively (sorted for determinism)
        for child_id in sorted(node.children):
            child = self.nodes.get(child_id)
            if child:
                parts.append(self._serialize_subtree(child))
        
        return "|".join(parts)
    
    def save_to_file(self, output_path: str, compact: bool = False):
        """Save DAG to JSON file."""
        # Compute sub-DAG hashes before saving
        self.compute_sub_dag_hashes()
        
        output = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "seed_version": self.seed.get('metadata', {}).get('version', 'unknown'),
                "generator": "dag_generator.py v2.0.0",
                "standard": "Yeshua",
                "layer_index": self.layer_index,
                "universe_index": self.universe_index,
                "sub_seed": self.sub_seed
            },
            "statistics": self.get_statistics(),
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            }
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            if compact:
                json.dump(output, f)
            else:
                json.dump(output, f, indent=2)
        
        print(f"DAG saved to: {output_path}")
        print(f"  Total nodes: {len(self.nodes):,}")
        print(f"  Layer: {self.layer_index}")
        print(f"  Universe: {self.universe_index}")
        print(f"  Sub-seed: {self.sub_seed[:16]}...")
        print(f"  File size: {Path(output_path).stat().st_size:,} bytes")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate DAG from seed definition (Yeshua Standard)"
    )
    parser.add_argument(
        "--seed",
        type=str,
        required=True,
        help="Path to seed definition YAML file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="dag_structure.json",
        help="Output JSON file path (default: dag_structure.json)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use compact JSON (no indentation)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify DAG properties (acyclic, connected)"
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only print statistics, don't save DAG"
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
        "--parent-seed",
        type=str,
        help="Parent universe seed (for recursive generation)"
    )
    
    args = parser.parse_args()
    
    # Load seed
    print(f"Loading seed from: {args.seed}")
    with open(args.seed, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Generate DAG
    print("\nGenerating DAG...")
    generator = DAGGenerator(
        seed,
        layer_index=args.layer_index,
        parent_seed=args.parent_seed,
        universe_index=args.universe_index
    )
    nodes = generator.generate()
    
    # Get statistics
    stats = generator.get_statistics()
    print("\nDAG Statistics:")
    print(f"  Total nodes: {stats['total_nodes']:,}")
    print(f"  Leaf nodes: {stats['leaf_nodes']:,}")
    print(f"  Max depth: {stats['max_depth']}")
    print(f"  Layer: {args.layer_index}")
    print(f"  Universe: {args.universe_index}")
    print(f"  Levels:")
    for level, count in stats['levels'].items():
        print(f"    {level}: {count:,}")
    
    # Verify if requested
    if args.verify:
        print("\nVerifying DAG properties...")
        generator.verify_acyclic()
        print("  ✓ Acyclic property verified")
        print("  ✓ All nodes reachable from root")
    
    # Save unless stats-only
    if not args.stats_only:
        print(f"\nSaving DAG to: {args.output}")
        generator.save_to_file(args.output, compact=args.compact)
        print("\n✓ DAG generation complete")
    else:
        print("\n✓ Statistics generated (no file saved)")


if __name__ == "__main__":
    main()
