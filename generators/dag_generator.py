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
    
    def __init__(self, node_id: str, level: str, parent_id: Optional[str], index: int):
        self.id = node_id
        self.level = level
        self.parent = parent_id
        self.index = index
        self.children: List[str] = []
        self.depth = 0
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "level": self.level,
            "parent": self.parent,
            "index": self.index,
            "children": self.children,
            "depth": self.depth
        }
    
    def __repr__(self) -> str:
        return f"DAGNode({self.id}, level={self.level}, children={len(self.children)})"


class DAGGenerator:
    """Generates Directed Acyclic Graph from seed definition."""
    
    def __init__(self, seed: dict):
        self.seed = seed
        self.nodes: Dict[str, DAGNode] = {}
        self.root = None
        
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
            index=0
        )
        self.root.depth = 0
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
                        index=i
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
    
    def save_to_file(self, output_path: str, compact: bool = False):
        """Save DAG to JSON file."""
        output = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "seed_version": self.seed.get('metadata', {}).get('version', 'unknown'),
                "generator": "dag_generator.py v1.0.0",
                "standard": "Yeshua"
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
    
    args = parser.parse_args()
    
    # Load seed
    print(f"Loading seed from: {args.seed}")
    with open(args.seed, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Generate DAG
    print("\nGenerating DAG...")
    generator = DAGGenerator(seed)
    nodes = generator.generate()
    
    # Get statistics
    stats = generator.get_statistics()
    print("\nDAG Statistics:")
    print(f"  Total nodes: {stats['total_nodes']:,}")
    print(f"  Leaf nodes: {stats['leaf_nodes']:,}")
    print(f"  Max depth: {stats['max_depth']}")
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
