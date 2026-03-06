#!/usr/bin/env python3
"""
Kitchen Task Projection Generator
==================================

Generates task projection views from the Kitchen DAG.
Views reference nodes but don't define ontology.

Authority: out/self_clean_kitchen_dag.json
Version: 1.0.0
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)


class TaskProjectionGenerator:
    """Generates task projection views from DAG."""
    
    def __init__(self, dag_path: str, manifest_path: str):
        self.dag_path = Path(dag_path)
        self.manifest_path = Path(manifest_path)
        
        with open(self.dag_path, 'r') as f:
            self.dag = json.load(f)
            
        self.metadata = self.dag['metadata']
        self.nodes = self.dag['nodes']
        
    def generate_all_tasks(self, output_dir: str) -> None:
        """Generate projection files for all tasks."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all task nodes
        task_nodes = [
            (node_id, node) 
            for node_id, node in self.nodes.items() 
            if node['level'] == 'task'
        ]
        
        print(f"📋 Generating {len(task_nodes)} task projections...")
        
        for task_node_id, task_node in task_nodes:
            self._generate_task_projection(task_node_id, task_node, output_path)
            
        print(f"✅ Generated {len(task_nodes)} task projection files")
        
    def _generate_task_projection(self, task_node_id: str, task_node: dict, 
                                  output_path: Path) -> None:
        """Generate a single task projection view."""
        task_name = task_node['name']
        
        # Get device node (parent)
        device_node_id = task_node['parent_node']
        device_node = self.nodes.get(device_node_id, {})
        
        # Build microactions structure
        microactions = []
        for micro_node_id in task_node['children']:
            micro_node = self.nodes[micro_node_id]
            
            micro_data = {
                "node_id": micro_node_id,
                "name": micro_node['name'],
                "index": micro_node['index'],
                "action": self._infer_action_type(micro_node['name']),
                "parameters": {"duration_sec": 1.0, "intensity": 1.0},
                "media": {"reference_video": "", "reference_frames": []},
                "state_in": {},
                "state_out": {}
            }
            microactions.append(micro_data)
            
        # Create projection structure
        projection = {
            "projection_type": "task_view",
            "node_id": task_node_id,
            "name": task_name,
            "device_node": device_node_id,
            "device_name": device_node.get('name', 'unknown'),
            "steps": microactions,
            "content_hash": task_node['content_hash'],
            "manifest_ref": str(self.manifest_path),
            "generator_version": self.metadata['generator_version'],
            "commit": self.metadata['commit'],
            "safety_constraints": task_node.get('safety_constraints', {})
        }
        
        # Write to file
        output_file = output_path / f"{task_name}.json"
        with open(output_file, 'w') as f:
            json.dump(projection, f, indent=2, sort_keys=True)
            
        print(f"   📄 {task_name}.json")
        
    def _infer_action_type(self, micro_name: str) -> str:
        """Infer action type from microaction name."""
        name_lower = micro_name.lower()
        if 'wipe' in name_lower:
            return 'wipe'
        elif 'spray' in name_lower or 'dispense' in name_lower:
            return 'dispense_soap'
        elif 'polish' in name_lower:
            return 'polish'
        elif 'vacuum' in name_lower:
            return 'vacuum'
        elif 'mop' in name_lower:
            return 'mop'
        elif 'brush' in name_lower or 'scrub' in name_lower:
            return 'brush'
        elif 'uv' in name_lower or 'sterilize' in name_lower:
            return 'uv_expose'
        else:
            return 'generic_action'


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate task projection views from Kitchen DAG"
    )
    parser.add_argument(
        "--dag",
        default="out/self_clean_kitchen_dag.json",
        help="Path to DAG JSON file"
    )
    parser.add_argument(
        "--output",
        default="data/kitchen_tasks",
        help="Output directory for task projections"
    )
    parser.add_argument(
        "--manifest",
        default="out/self_clean_kitchen_manifest.jsonl",
        help="Path to manifest file"
    )
    
    args = parser.parse_args()
    
    generator = TaskProjectionGenerator(args.dag, args.manifest)
    generator.generate_all_tasks(args.output)


if __name__ == "__main__":
    main()
