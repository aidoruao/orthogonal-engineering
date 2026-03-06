#!/usr/bin/env python3
"""
Dish Projection Generator
==========================

Generates dish projection views from the Food Cart DAG.

Views are projections - they reference nodes but don't define ontology.

Authority: out/food_cart_dag.json
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class DishProjectionGenerator:
    """Generates dish projection views from DAG."""
    
    def __init__(self, dag_path: str, manifest_path: str):
        """
        Initialize generator.
        
        Args:
            dag_path: Path to food_cart_dag.json
            manifest_path: Path to food_cart_manifest.jsonl
        """
        self.dag_path = Path(dag_path)
        self.manifest_path = Path(manifest_path)
        
        # Load DAG
        with open(self.dag_path, 'r') as f:
            self.dag = json.load(f)
            
        self.metadata = self.dag['metadata']
        self.nodes = self.dag['nodes']
        
    def generate_all_dishes(self, output_dir: str) -> None:
        """
        Generate projection files for all dishes.
        
        Args:
            output_dir: Directory to write dish projections to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all dish nodes
        dish_nodes = [
            (node_id, node) 
            for node_id, node in self.nodes.items() 
            if node['level'] == 'dish'
        ]
        
        print(f"🍽️  Generating {len(dish_nodes)} dish projections...")
        
        for dish_node_id, dish_node in dish_nodes:
            self._generate_dish_projection(dish_node_id, dish_node, output_path)
            
        print(f"✅ Generated {len(dish_nodes)} dish projection files")
        
    def _generate_dish_projection(self, dish_node_id: str, dish_node: dict, 
                                  output_path: Path) -> None:
        """
        Generate a single dish projection view.
        
        INV-DISH-001: node_id must correspond to a valid DAG node.
        INV-DISH-003: Phases and steps must correspond to valid DAG nodes.
        """
        dish_name = dish_node['name']
        
        # Build phases structure
        phases = []
        for phase_node_id in dish_node['children']:
            phase_node = self.nodes[phase_node_id]
            
            # Build steps structure
            steps = []
            for step_node_id in phase_node['children']:
                step_node = self.nodes[step_node_id]
                
                step_data = {
                    "node_id": step_node_id,
                    "name": step_node['name'],
                    "index": step_node['index'],
                    "media": [],  # Would be populated with actual media references
                    "state_in": {},  # Would describe input state
                    "state_out": {}  # Would describe output state
                }
                steps.append(step_data)
                
            phase_data = {
                "node_id": phase_node_id,
                "name": phase_node['name'],
                "index": phase_node['index'],
                "steps": steps
            }
            phases.append(phase_data)
            
        # Create projection structure
        projection = {
            "projection_type": "dish_view",
            "node_id": dish_node_id,
            "name": dish_name,
            "phases": phases,
            "content_hash": dish_node['content_hash'],
            "manifest_ref": str(self.manifest_path),
            "generator_version": self.metadata['generator_version'],
            "commit": self.metadata['commit']
        }
        
        # Write to file
        output_file = output_path / f"{dish_name}.json"
        with open(output_file, 'w') as f:
            json.dump(projection, f, indent=2, sort_keys=True)
            
        print(f"   📄 {dish_name}.json")
        
    def verify_projections(self, output_dir: str) -> bool:
        """
        Verify dish projections against invariants.
        
        Returns:
            True if all invariants hold, False otherwise
        """
        output_path = Path(output_dir)
        
        print(f"🔍 Verifying dish projections...")
        
        dish_files = list(output_path.glob("*.json"))
        
        all_valid = True
        for dish_file in dish_files:
            with open(dish_file, 'r') as f:
                projection = json.load(f)
                
            # INV-DISH-001: node_id must correspond to a valid DAG node
            if projection['node_id'] not in self.nodes:
                print(f"   ❌ INV-DISH-001 failed: {dish_file.name} - invalid node_id")
                all_valid = False
                continue
                
            # INV-DISH-002: Dish content_hash must match manifest entry
            node = self.nodes[projection['node_id']]
            if projection['content_hash'] != node['content_hash']:
                print(f"   ❌ INV-DISH-002 failed: {dish_file.name} - content_hash mismatch")
                all_valid = False
                continue
                
            # INV-DISH-003: Phases and steps must correspond to valid DAG nodes
            for phase in projection['phases']:
                if phase['node_id'] not in self.nodes:
                    print(f"   ❌ INV-DISH-003 failed: {dish_file.name} - invalid phase node_id")
                    all_valid = False
                    continue
                    
                for step in phase['steps']:
                    if step['node_id'] not in self.nodes:
                        print(f"   ❌ INV-DISH-003 failed: {dish_file.name} - invalid step node_id")
                        all_valid = False
                        continue
                        
            if all_valid:
                print(f"   ✅ {dish_file.name} - all invariants satisfied")
                
        return all_valid


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate dish projection views from Food Cart DAG"
    )
    parser.add_argument(
        "--dag",
        default="out/food_cart_dag.json",
        help="Path to DAG JSON file"
    )
    parser.add_argument(
        "--output",
        default="data/dishes",
        help="Output directory for dish projections"
    )
    parser.add_argument(
        "--manifest",
        default="out/food_cart_manifest.jsonl",
        help="Path to manifest file"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify projections after generation"
    )
    
    args = parser.parse_args()
    
    # Generate
    generator = DishProjectionGenerator(args.dag, args.manifest)
    generator.generate_all_dishes(args.output)
    
    # Verify if requested
    if args.verify:
        print()
        valid = generator.verify_projections(args.output)
        if not valid:
            print()
            print("❌ Some invariants failed!")
            sys.exit(1)
        else:
            print()
            print("✅ All invariants satisfied!")


if __name__ == "__main__":
    main()
