#!/usr/bin/env python3
"""
Food Cart Fractal Dataset Generator
====================================

Generates a deterministic, content-addressed DAG from the Food Cart Universe seed.

Implements Canonical Schema Closure principles:
- Universe seed defines ontology
- DAG nodes define structure  
- Views are projections

Authority: seed/food_cart_universe.yaml
Version: 1.0.0
"""

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


class FoodCartNode:
    """Represents a single node in the Food Cart DAG."""
    
    def __init__(self, node_id: str, parent_node: Optional[str], level: str, 
                 index: int, name: str, seed_ref: str, expansion_rule: str,
                 generator_version: str, commit: str = "unknown"):
        self.node_id = node_id
        self.parent_node = parent_node
        self.level = level
        self.index = index
        self.name = name
        self.seed_ref = seed_ref
        self.expansion_rule = expansion_rule
        self.created_by = generator_version
        self.commit = commit
        self.children: List[str] = []
        self.content_hash: Optional[str] = None
        
    def compute_content_hash(self) -> str:
        """
        Compute canonical content hash for this node.
        
        INV-NODE-002: content_hash MUST equal canonical serialized node content.
        """
        content = {
            "node_id": self.node_id,
            "parent_node": self.parent_node,
            "level": self.level,
            "index": self.index,
            "name": self.name,
            "children": sorted(self.children),  # Canonical ordering
            "seed_ref": self.seed_ref,
            "expansion_rule": self.expansion_rule,
            "created_by": self.created_by
        }
        # Use canonical JSON serialization
        canonical_json = json.dumps(content, sort_keys=True, separators=(',', ':'))
        self.content_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        return self.content_hash
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "node_id": self.node_id,
            "parent_node": self.parent_node,
            "level": self.level,
            "index": self.index,
            "name": self.name,
            "content_hash": self.content_hash,
            "seed_ref": self.seed_ref,
            "expansion_rule": self.expansion_rule,
            "created_by": self.created_by,
            "commit": self.commit,
            "children": self.children
        }


class FoodCartGenerator:
    """Generates the Food Cart Universe DAG from seed definition."""
    
    def __init__(self, seed_path: str, git_commit: str = "unknown"):
        """
        Initialize generator with seed file.
        
        Args:
            seed_path: Path to seed/food_cart_universe.yaml
            git_commit: Current git commit SHA
        """
        self.seed_path = Path(seed_path)
        self.git_commit = git_commit
        
        # Load seed
        with open(self.seed_path, 'r') as f:
            self.seed = yaml.safe_load(f)
            
        # Extract configuration
        self.universe_id = self.seed['universe']['id']
        self.levels = self.seed['universe']['expansion']['levels']
        self.seed_value = self.seed['sample_universe']['seed_value']
        
        # Sample data
        self.dishes = self.seed['sample_universe']['menu']['dishes']
        self.phases = self.seed['sample_universe']['phases']
        self.steps_per_phase = self.seed['sample_universe']['steps_per_phase']
        
        # Storage
        self.nodes: Dict[str, FoodCartNode] = {}
        self.root_node_id: Optional[str] = None
        
    def _compute_node_id(self, seed_component: str, parent_node: Optional[str], 
                        expansion_config: str) -> str:
        """
        Compute deterministic node ID.
        
        INV-NODE-001: node_id MUST equal SHA256(seed || parent_node || expansion_config)
        
        Args:
            seed_component: Seed value component
            parent_node: Parent node ID or None
            expansion_config: Configuration for this expansion
            
        Returns:
            SHA256 hash as hex string
        """
        components = [
            seed_component,
            parent_node or "null",
            expansion_config
        ]
        combined = "||".join(components)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
    def generate(self) -> None:
        """
        Generate the complete DAG structure.
        
        Implements INV-FU-001: Universe must regenerate identical DAG from identical seed.
        """
        print(f"🌱 Generating Food Cart Universe from seed...")
        print(f"   Seed: {self.seed_path}")
        print(f"   Levels: {' → '.join(self.levels)}")
        print()
        
        # Level 0: Menu (root)
        self._generate_menu()
        
        # Level 1: Dishes
        self._generate_dishes()
        
        # Level 2: Phases
        self._generate_phases()
        
        # Level 3: Steps
        self._generate_steps()
        
        # Compute content hashes
        self._compute_all_content_hashes()
        
        print(f"✅ Generated {len(self.nodes)} nodes")
        print()
        
    def _generate_menu(self) -> None:
        """Generate menu node (root)."""
        expansion_config = json.dumps({
            "level": "menu",
            "universe_id": self.universe_id
        }, sort_keys=True)
        
        node_id = self._compute_node_id(
            str(self.seed_value),
            None,
            expansion_config
        )
        
        node = FoodCartNode(
            node_id=node_id,
            parent_node=None,
            level="menu",
            index=0,
            name="food_cart_menu",
            seed_ref=str(self.seed_path),
            expansion_rule="root",
            generator_version="1",
            commit=self.git_commit
        )
        
        self.nodes[node_id] = node
        self.root_node_id = node_id
        
        print(f"📋 Menu node: {node_id[:16]}...")
        
    def _generate_dishes(self) -> None:
        """Generate dish nodes."""
        menu_node = self.nodes[self.root_node_id]
        
        for idx, dish_name in enumerate(self.dishes):
            expansion_config = json.dumps({
                "level": "dish",
                "dish_name": dish_name,
                "index": idx
            }, sort_keys=True)
            
            node_id = self._compute_node_id(
                str(self.seed_value),
                self.root_node_id,
                expansion_config
            )
            
            node = FoodCartNode(
                node_id=node_id,
                parent_node=self.root_node_id,
                level="dish",
                index=idx,
                name=dish_name,
                seed_ref=str(self.seed_path),
                expansion_rule=f"dish[{idx}]",
                generator_version="1",
                commit=self.git_commit
            )
            
            self.nodes[node_id] = node
            menu_node.children.append(node_id)
            
        print(f"🍽️  Generated {len(self.dishes)} dish nodes")
        
    def _generate_phases(self) -> None:
        """Generate phase nodes for each dish."""
        dish_nodes = [n for n in self.nodes.values() if n.level == "dish"]
        total_phases = 0
        
        for dish_node in dish_nodes:
            for phase_idx, phase_name in enumerate(self.phases):
                expansion_config = json.dumps({
                    "level": "phase",
                    "dish": dish_node.name,
                    "phase_name": phase_name,
                    "index": phase_idx
                }, sort_keys=True)
                
                node_id = self._compute_node_id(
                    str(self.seed_value),
                    dish_node.node_id,
                    expansion_config
                )
                
                node = FoodCartNode(
                    node_id=node_id,
                    parent_node=dish_node.node_id,
                    level="phase",
                    index=phase_idx,
                    name=f"{dish_node.name}_{phase_name}",
                    seed_ref=str(self.seed_path),
                    expansion_rule=f"dish[{dish_node.index}].phase[{phase_idx}]",
                    generator_version="1",
                    commit=self.git_commit
                )
                
                self.nodes[node_id] = node
                dish_node.children.append(node_id)
                total_phases += 1
                
        print(f"⚙️  Generated {total_phases} phase nodes")
        
    def _generate_steps(self) -> None:
        """Generate step nodes for each phase."""
        phase_nodes = [n for n in self.nodes.values() if n.level == "phase"]
        total_steps = 0
        
        for phase_node in phase_nodes:
            # Extract phase type from name
            phase_type = phase_node.name.split('_')[-1]
            step_count = self.steps_per_phase.get(phase_type, 3)
            
            for step_idx in range(step_count):
                expansion_config = json.dumps({
                    "level": "step",
                    "phase": phase_node.name,
                    "step_index": step_idx
                }, sort_keys=True)
                
                node_id = self._compute_node_id(
                    str(self.seed_value),
                    phase_node.node_id,
                    expansion_config
                )
                
                node = FoodCartNode(
                    node_id=node_id,
                    parent_node=phase_node.node_id,
                    level="step",
                    index=step_idx,
                    name=f"{phase_node.name}_step_{step_idx}",
                    seed_ref=str(self.seed_path),
                    expansion_rule=f"{phase_node.expansion_rule}.step[{step_idx}]",
                    generator_version="1",
                    commit=self.git_commit
                )
                
                self.nodes[node_id] = node
                phase_node.children.append(node_id)
                total_steps += 1
                
        print(f"📝 Generated {total_steps} step nodes")
        
    def _compute_all_content_hashes(self) -> None:
        """
        Compute content hashes for all nodes.
        
        Implements INV-NODE-002: content_hash MUST equal canonical serialized node content.
        """
        print(f"🔐 Computing content hashes...")
        for node in self.nodes.values():
            node.compute_content_hash()
            
    def save_dag(self, output_path: str) -> None:
        """Save the complete DAG to JSON file."""
        output = {
            "metadata": {
                "universe_id": self.universe_id,
                "seed_ref": str(self.seed_path),
                "generator_version": "1",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "commit": self.git_commit,
                "total_nodes": len(self.nodes),
                "root_node": self.root_node_id
            },
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, sort_keys=True)
            
        print(f"💾 Saved DAG to {output_path}")
        
    def get_statistics(self) -> dict:
        """Get generation statistics."""
        level_counts = {}
        for node in self.nodes.values():
            level_counts[node.level] = level_counts.get(node.level, 0) + 1
            
        return {
            "total_nodes": len(self.nodes),
            "root_node": self.root_node_id,
            "level_counts": level_counts
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Food Cart Universe DAG from seed"
    )
    parser.add_argument(
        "--seed",
        default="seed/food_cart_universe.yaml",
        help="Path to universe seed file"
    )
    parser.add_argument(
        "--output",
        default="out/food_cart_dag.json",
        help="Output path for DAG JSON"
    )
    parser.add_argument(
        "--commit",
        default="unknown",
        help="Git commit SHA"
    )
    
    args = parser.parse_args()
    
    # Generate
    generator = FoodCartGenerator(args.seed, args.commit)
    generator.generate()
    
    # Save
    generator.save_dag(args.output)
    
    # Statistics
    stats = generator.get_statistics()
    print()
    print("📊 Statistics:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
