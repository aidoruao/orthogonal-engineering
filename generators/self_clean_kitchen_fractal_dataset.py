#!/usr/bin/env python3
"""
Self-Cleaning Kitchen Fractal Dataset Generator
================================================

Generates a deterministic, content-addressed DAG from the Self-Cleaning Kitchen Universe seed.

Implements Canonical Schema Closure with Yeshua/Chaldean/Kenosis principles:
- Universe seed defines ontology
- DAG nodes define structure with safety constraints
- Views are projections

Authority: seed/self_clean_kitchen_universe.yaml
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


class KitchenNode:
    """Represents a single node in the Kitchen DAG with safety metadata."""
    
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
        
        # Kitchen-specific metadata
        self.sensors: Optional[Dict] = None
        self.actuators: Optional[Dict] = None
        self.ai_module: Optional[Dict] = None
        self.physical_properties: Optional[Dict] = None
        self.safety_constraints: Optional[Dict] = None
        
    def set_device_capabilities(self, capabilities: Dict):
        """Set device capabilities from seed."""
        self.sensors = capabilities.get('sensors', {})
        self.actuators = capabilities.get('actuators', {})
        self.ai_module = capabilities.get('ai_module', {})
        self.physical_properties = capabilities.get('physical_properties', {})
        
    def set_safety_constraints(self, constraints: Dict):
        """Set safety constraints from universe."""
        self.safety_constraints = constraints
        
    def compute_content_hash(self) -> str:
        """
        Compute canonical content hash for this node.
        
        INV-DEV-004: Node content hash must match manifest entry.
        """
        content = {
            "node_id": self.node_id,
            "parent_node": self.parent_node,
            "level": self.level,
            "index": self.index,
            "name": self.name,
            "children": sorted(self.children),
            "seed_ref": self.seed_ref,
            "expansion_rule": self.expansion_rule,
            "created_by": self.created_by
        }
        
        # Add device-specific metadata if present
        if self.sensors:
            content["sensors"] = self.sensors
        if self.actuators:
            content["actuators"] = self.actuators
        if self.ai_module:
            content["ai_module"] = self.ai_module
        if self.physical_properties:
            content["physical_properties"] = self.physical_properties
        if self.safety_constraints:
            content["safety_constraints"] = self.safety_constraints
            
        # Use canonical JSON serialization
        canonical_json = json.dumps(content, sort_keys=True, separators=(',', ':'))
        self.content_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        return self.content_hash
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
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
        
        # Add kitchen-specific metadata
        if self.sensors:
            result["sensors"] = self.sensors
        if self.actuators:
            result["actuators"] = self.actuators
        if self.ai_module:
            result["ai_module"] = self.ai_module
        if self.physical_properties:
            result["physical_properties"] = self.physical_properties
        if self.safety_constraints:
            result["safety_constraints"] = self.safety_constraints
            
        return result


class KitchenGenerator:
    """Generates the Self-Cleaning Kitchen Universe DAG from seed definition."""
    
    def __init__(self, seed_path: str, git_commit: str = "unknown"):
        """
        Initialize generator with seed file.
        
        Args:
            seed_path: Path to seed/self_clean_kitchen_universe.yaml
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
        self.safety = self.seed['universe']['safety']
        
        # Sample data
        self.zones = self.seed['sample_universe']['zones']
        self.devices_per_zone = self.seed['sample_universe']['devices_per_zone']
        self.tasks_per_device = self.seed['sample_universe']['tasks_per_device']
        self.microactions_per_task = self.seed['sample_universe']['microactions_per_task']
        self.device_capabilities = self.seed.get('device_capabilities', {})
        
        # Storage
        self.nodes: Dict[str, KitchenNode] = {}
        self.root_node_id: Optional[str] = None
        
    def _compute_node_id(self, seed_component: str, parent_node: Optional[str], 
                        level: str, index: int, expansion_config: str) -> str:
        """
        Compute deterministic node ID.
        
        INV-DEV-001: node_id deterministic from seed, level, index.
        INV-KU-002: Node IDs derived from seed + level + index.
        
        Args:
            seed_component: Seed value component
            parent_node: Parent node ID or None
            level: Node level
            index: Node index
            expansion_config: Configuration for this expansion
            
        Returns:
            SHA256 hash as hex string
        """
        components = [
            seed_component,
            parent_node or "null",
            level,
            str(index),
            expansion_config
        ]
        combined = "||".join(components)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
    def generate(self) -> None:
        """
        Generate the complete DAG structure.
        
        Implements INV-KU-001: Universe regenerates deterministically from identical seed.
        """
        print(f"🧹 Generating Self-Cleaning Kitchen Universe from seed...")
        print(f"   Seed: {self.seed_path}")
        print(f"   Levels: {' → '.join(self.levels)}")
        print()
        
        # Level 0: Root (implicit kitchen)
        self._generate_root()
        
        # Level 1: Zones
        self._generate_zones()
        
        # Level 2: Devices
        self._generate_devices()
        
        # Level 3: Tasks
        self._generate_tasks()
        
        # Level 4: Microactions
        self._generate_microactions()
        
        # Compute content hashes
        self._compute_all_content_hashes()
        
        print(f"✅ Generated {len(self.nodes)} nodes")
        print()
        
    def _generate_root(self) -> None:
        """Generate root node (kitchen)."""
        expansion_config = json.dumps({
            "level": "kitchen_root",
            "universe_id": self.universe_id
        }, sort_keys=True)
        
        node_id = self._compute_node_id(
            str(self.seed_value),
            None,
            "kitchen_root",
            0,
            expansion_config
        )
        
        node = KitchenNode(
            node_id=node_id,
            parent_node=None,
            level="kitchen_root",
            index=0,
            name="self_cleaning_kitchen",
            seed_ref=str(self.seed_path),
            expansion_rule="root",
            generator_version="1",
            commit=self.git_commit
        )
        
        # Add safety constraints
        node.set_safety_constraints(self.safety)
        
        self.nodes[node_id] = node
        self.root_node_id = node_id
        
        print(f"🏠 Kitchen root node: {node_id[:16]}...")
        
    def _generate_zones(self) -> None:
        """Generate zone nodes."""
        root_node = self.nodes[self.root_node_id]
        
        for idx, zone_name in enumerate(self.zones):
            expansion_config = json.dumps({
                "level": "zone",
                "zone_name": zone_name,
                "index": idx
            }, sort_keys=True)
            
            node_id = self._compute_node_id(
                str(self.seed_value),
                self.root_node_id,
                "zone",
                idx,
                expansion_config
            )
            
            node = KitchenNode(
                node_id=node_id,
                parent_node=self.root_node_id,
                level="zone",
                index=idx,
                name=zone_name,
                seed_ref=str(self.seed_path),
                expansion_rule=f"zone[{idx}]",
                generator_version="1",
                commit=self.git_commit
            )
            
            node.set_safety_constraints(self.safety)
            
            self.nodes[node_id] = node
            root_node.children.append(node_id)
            
        print(f"🗺️  Generated {len(self.zones)} zone nodes")
        
    def _generate_devices(self) -> None:
        """Generate device nodes for each zone."""
        zone_nodes = [n for n in self.nodes.values() if n.level == "zone"]
        total_devices = 0
        
        for zone_node in zone_nodes:
            zone_devices = self.devices_per_zone.get(zone_node.name, [])
            
            for device_idx, device_name in enumerate(zone_devices):
                expansion_config = json.dumps({
                    "level": "device",
                    "zone": zone_node.name,
                    "device_name": device_name,
                    "index": device_idx
                }, sort_keys=True)
                
                node_id = self._compute_node_id(
                    str(self.seed_value),
                    zone_node.node_id,
                    "device",
                    device_idx,
                    expansion_config
                )
                
                node = KitchenNode(
                    node_id=node_id,
                    parent_node=zone_node.node_id,
                    level="device",
                    index=device_idx,
                    name=f"{zone_node.name}_{device_name}",
                    seed_ref=str(self.seed_path),
                    expansion_rule=f"zone[{zone_node.index}].device[{device_idx}]",
                    generator_version="1",
                    commit=self.git_commit
                )
                
                # Set device capabilities if available
                if device_name in self.device_capabilities:
                    node.set_device_capabilities(self.device_capabilities[device_name])
                    
                node.set_safety_constraints(self.safety)
                
                self.nodes[node_id] = node
                zone_node.children.append(node_id)
                total_devices += 1
                
        print(f"🤖 Generated {total_devices} device nodes")
        
    def _generate_tasks(self) -> None:
        """Generate task nodes for each device."""
        device_nodes = [n for n in self.nodes.values() if n.level == "device"]
        total_tasks = 0
        
        for device_node in device_nodes:
            # Extract device type from name
            device_type = device_node.name.split('_', 1)[1] if '_' in device_node.name else device_node.name
            tasks = self.tasks_per_device.get(device_type, [])
            
            for task_idx, task_name in enumerate(tasks):
                expansion_config = json.dumps({
                    "level": "task",
                    "device": device_node.name,
                    "task_name": task_name,
                    "index": task_idx
                }, sort_keys=True)
                
                node_id = self._compute_node_id(
                    str(self.seed_value),
                    device_node.node_id,
                    "task",
                    task_idx,
                    expansion_config
                )
                
                node = KitchenNode(
                    node_id=node_id,
                    parent_node=device_node.node_id,
                    level="task",
                    index=task_idx,
                    name=f"{device_node.name}_{task_name}",
                    seed_ref=str(self.seed_path),
                    expansion_rule=f"{device_node.expansion_rule}.task[{task_idx}]",
                    generator_version="1",
                    commit=self.git_commit
                )
                
                node.set_safety_constraints(self.safety)
                
                self.nodes[node_id] = node
                device_node.children.append(node_id)
                total_tasks += 1
                
        print(f"📋 Generated {total_tasks} task nodes")
        
    def _generate_microactions(self) -> None:
        """Generate microaction nodes for each task."""
        task_nodes = [n for n in self.nodes.values() if n.level == "task"]
        total_microactions = 0
        
        for task_node in task_nodes:
            # Extract task type from name
            parts = task_node.name.split('_')
            task_type = '_'.join(parts[2:]) if len(parts) > 2 else task_node.name
            microaction_count = self.microactions_per_task.get(task_type, 3)
            
            for micro_idx in range(microaction_count):
                expansion_config = json.dumps({
                    "level": "microaction",
                    "task": task_node.name,
                    "microaction_index": micro_idx
                }, sort_keys=True)
                
                node_id = self._compute_node_id(
                    str(self.seed_value),
                    task_node.node_id,
                    "microaction",
                    micro_idx,
                    expansion_config
                )
                
                node = KitchenNode(
                    node_id=node_id,
                    parent_node=task_node.node_id,
                    level="microaction",
                    index=micro_idx,
                    name=f"{task_node.name}_micro_{micro_idx}",
                    seed_ref=str(self.seed_path),
                    expansion_rule=f"{task_node.expansion_rule}.micro[{micro_idx}]",
                    generator_version="1",
                    commit=self.git_commit
                )
                
                node.set_safety_constraints(self.safety)
                
                self.nodes[node_id] = node
                task_node.children.append(node_id)
                total_microactions += 1
                
        print(f"⚡ Generated {total_microactions} microaction nodes")
        
    def _compute_all_content_hashes(self) -> None:
        """
        Compute content hashes for all nodes.
        
        Implements INV-DEV-004: Node content hash must match manifest entry.
        """
        print(f"🔐 Computing content hashes...")
        for node in self.nodes.values():
            node.compute_content_hash()
            
    def verify_dag_acyclic(self) -> bool:
        """
        Verify DAG has no cycles.
        
        Implements INV-DEV-005: DAG acyclic.
        """
        visited = set()
        stack = set()
        
        def has_cycle(node_id: str) -> bool:
            if node_id in stack:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            stack.add(node_id)
            node = self.nodes.get(node_id)
            if node:
                for child_id in node.children:
                    if has_cycle(child_id):
                        return True
            stack.remove(node_id)
            return False
            
        return not has_cycle(self.root_node_id)
            
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
                "root_node": self.root_node_id,
                "safety_constraints": self.safety
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
            "level_counts": level_counts,
            "dag_acyclic": self.verify_dag_acyclic()
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Self-Cleaning Kitchen Universe DAG from seed"
    )
    parser.add_argument(
        "--seed",
        default="seed/self_clean_kitchen_universe.yaml",
        help="Path to universe seed file"
    )
    parser.add_argument(
        "--output",
        default="out/self_clean_kitchen_dag.json",
        help="Output path for DAG JSON"
    )
    parser.add_argument(
        "--commit",
        default="unknown",
        help="Git commit SHA"
    )
    
    args = parser.parse_args()
    
    # Generate
    generator = KitchenGenerator(args.seed, args.commit)
    generator.generate()
    
    # Verify
    stats = generator.get_statistics()
    if not stats['dag_acyclic']:
        print("❌ ERROR: DAG contains cycles!")
        sys.exit(1)
    
    # Save
    generator.save_dag(args.output)
    
    # Statistics
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
