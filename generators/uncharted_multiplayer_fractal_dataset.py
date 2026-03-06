#!/usr/bin/env python3
"""
Uncharted Multiplayer Fractal Dataset Generator
================================================

Generates a deterministic, content-addressed DAG from the Uncharted Multiplayer Universe seed.

Implements Canonical Schema Closure + Yeshua/Chaldean/Kenosis principles:
- Universe seed defines ontology
- DAG nodes define structure
- Views are projections
- Clean-room, legally compliant implementation
- Deterministic, verifiable, eternally free

Authority: seed/uncharted_multiplayer_universe.yaml
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


class MultiplayerNode:
    """Represents a single node in the Uncharted Multiplayer DAG."""
    
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
        
        INV-PROJ-003: content_hash MUST equal canonical serialized node content.
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


class MultiplayerGenerator:
    """Generates the Uncharted Multiplayer Universe DAG from seed definition."""
    
    def __init__(self, seed_path: str, git_commit: str = "unknown"):
        """
        Initialize generator with seed file.
        
        Args:
            seed_path: Path to seed/uncharted_multiplayer_universe.yaml
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
        self.experience_descriptors = self.seed['sample_universe']['experience_descriptors']
        self.mechanics = self.seed['sample_universe']['mechanics']
        self.mathematics_systems = self.seed['sample_universe']['mathematics_systems']
        self.projection_views = self.seed['sample_universe']['projection_views']
        self.microactions_per_projection = self.seed['sample_universe']['microactions_per_projection']
        
        # Node registry
        self.nodes: Dict[str, MultiplayerNode] = {}
        self.root_node: Optional[MultiplayerNode] = None
        
    def generate_node_id(self, parent_node: Optional[str], level: str, 
                        index: int, name: str) -> str:
        """
        Generate deterministic node ID.
        
        INV-UNI-002: node_id = SHA256(seed || parent_node || level || index || name)
        """
        # Canonical representation
        data = {
            "seed": self.seed_value,
            "parent_node": parent_node,
            "level": level,
            "index": index,
            "name": name
        }
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
        
    def create_node(self, parent_node: Optional[str], level: str, 
                   index: int, name: str, expansion_rule: str) -> MultiplayerNode:
        """Create a new node in the DAG."""
        node_id = self.generate_node_id(parent_node, level, index, name)
        
        node = MultiplayerNode(
            node_id=node_id,
            parent_node=parent_node,
            level=level,
            index=index,
            name=name,
            seed_ref=f"seed/uncharted_multiplayer_universe.yaml#{level}",
            expansion_rule=expansion_rule,
            generator_version="1.0.0",
            commit=self.git_commit
        )
        
        self.nodes[node_id] = node
        
        # Update parent's children
        if parent_node and parent_node in self.nodes:
            self.nodes[parent_node].children.append(node_id)
            
        return node
        
    def generate_dag(self) -> None:
        """
        Generate the complete DAG.
        
        Expansion hierarchy:
        1. Root (universe)
        2. Experience descriptors (6 nodes)
        3. Mechanics (15 nodes - 4 categories with 3-4 mechanics each)
        4. Mathematics systems (11 nodes - 3 categories with 4 systems each)
        5. Projection views (8 nodes - 2 categories with 4-5 views each)
        6. Microactions (56 nodes - variable per projection)
        
        Total: 1 + 6 + 15 + 11 + 8 + 56 = 97 nodes
        """
        print(f"Generating Uncharted Multiplayer Universe DAG...")
        print(f"Seed value: {self.seed_value}")
        
        # Level 0: Root node
        self.root_node = self.create_node(
            parent_node=None,
            level="universe",
            index=0,
            name=self.universe_id,
            expansion_rule="root"
        )
        print(f"Created root node: {self.root_node.node_id[:16]}...")
        
        # Level 1: Experience descriptors
        experience_nodes = []
        for idx, descriptor in enumerate(self.experience_descriptors):
            node = self.create_node(
                parent_node=self.root_node.node_id,
                level="experience",
                index=idx,
                name=descriptor,
                expansion_rule="experience_descriptors"
            )
            experience_nodes.append(node)
        print(f"Created {len(experience_nodes)} experience nodes")
        
        # Level 2: Mechanics (expanded from all experience nodes)
        mechanic_nodes = []
        mechanic_index = 0
        for category, mechanics_list in self.mechanics.items():
            for mechanic in mechanics_list:
                # Attach to first experience node as parent (could be more sophisticated)
                parent = experience_nodes[mechanic_index % len(experience_nodes)]
                node = self.create_node(
                    parent_node=parent.node_id,
                    level="mechanic",
                    index=mechanic_index,
                    name=f"{category}.{mechanic}",
                    expansion_rule=f"mechanics.{category}"
                )
                mechanic_nodes.append(node)
                mechanic_index += 1
        print(f"Created {len(mechanic_nodes)} mechanic nodes")
        
        # Level 3: Mathematics systems (expanded from mechanic nodes)
        math_nodes = []
        math_index = 0
        for category, systems_list in self.mathematics_systems.items():
            for system in systems_list:
                # Attach to mechanic nodes in round-robin
                parent = mechanic_nodes[math_index % len(mechanic_nodes)]
                node = self.create_node(
                    parent_node=parent.node_id,
                    level="mathematics",
                    index=math_index,
                    name=f"{category}.{system}",
                    expansion_rule=f"mathematics.{category}"
                )
                math_nodes.append(node)
                math_index += 1
        print(f"Created {len(math_nodes)} mathematics nodes")
        
        # Level 4: Projection views (expanded from mathematics nodes)
        projection_nodes = []
        projection_index = 0
        for category, views_list in self.projection_views.items():
            for view in views_list:
                # Attach to math nodes in round-robin
                parent = math_nodes[projection_index % len(math_nodes)]
                node = self.create_node(
                    parent_node=parent.node_id,
                    level="projection",
                    index=projection_index,
                    name=f"{category}.{view}",
                    expansion_rule=f"projection.{category}"
                )
                projection_nodes.append(node)
                projection_index += 1
        print(f"Created {len(projection_nodes)} projection nodes")
        
        # Level 5: Microactions (expanded from each projection)
        microaction_index = 0
        total_microactions = 0
        for proj_node in projection_nodes:
            # Extract projection name from node name (e.g., "client.graphics_pipeline" -> "graphics_pipeline")
            proj_name = proj_node.name.split('.')[-1]
            
            # Get microaction count for this projection
            microaction_count = self.microactions_per_projection.get(proj_name, 0)
            
            for i in range(microaction_count):
                node = self.create_node(
                    parent_node=proj_node.node_id,
                    level="microaction",
                    index=microaction_index,
                    name=f"{proj_name}.action_{i+1}",
                    expansion_rule=f"microaction.{proj_name}"
                )
                microaction_index += 1
                total_microactions += 1
        
        print(f"Created {total_microactions} microaction nodes")
        print(f"Total nodes: {len(self.nodes)}")
        
    def compute_all_content_hashes(self) -> None:
        """
        Compute content hashes for all nodes.
        
        INV-PROJ-003: All nodes must have content hash.
        """
        print("Computing content hashes...")
        for node_id, node in self.nodes.items():
            node.compute_content_hash()
            
    def verify_dag_acyclic(self) -> bool:
        """
        Verify DAG is acyclic.
        
        INV-TOPO-003: DAG must be acyclic.
        """
        print("Verifying DAG is acyclic...")
        
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
            
        # Check from root
        if self.root_node and has_cycle(self.root_node.node_id):
            print("ERROR: Cycle detected in DAG!")
            return False
            
        print("✓ DAG is acyclic")
        return True
        
    def write_dag(self, output_path: str) -> None:
        """Write DAG to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        dag_data = {
            "universe_id": self.universe_id,
            "seed_value": self.seed_value,
            "levels": self.levels,
            "root_node": self.root_node.node_id if self.root_node else None,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "generator_version": "1.0.0",
            "commit": self.git_commit,
            "total_nodes": len(self.nodes),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }
        
        with open(output_file, 'w') as f:
            json.dump(dag_data, f, indent=2, sort_keys=True)
            
        print(f"✓ Wrote DAG to {output_file}")
        
    def write_manifest(self, output_path: str) -> None:
        """
        Write canonical manifest.
        
        INV-MAN-001: All nodes must be in manifest.
        INV-MAN-003: Manifest must be deterministic.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print("Writing manifest...")
        
        # Sort nodes by node_id for deterministic ordering
        sorted_nodes = sorted(self.nodes.items(), key=lambda x: x[0])
        
        with open(output_file, 'w') as f:
            for node_id, node in sorted_nodes:
                manifest_entry = {
                    "node_id": node.node_id,
                    "level": node.level,
                    "content_hash": node.content_hash,
                    "artifact_path": f"out/uncharted_mp_dag.json#{node.node_id}",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "generator_version": node.created_by,
                    "commit": node.commit
                }
                f.write(json.dumps(manifest_entry, sort_keys=True, separators=(',', ':')) + '\n')
                
        print(f"✓ Wrote manifest to {output_file} ({len(sorted_nodes)} entries)")
        
    def compute_merkle_root(self, manifest_path: str, output_path: str) -> str:
        """
        Compute Merkle root from manifest.
        
        INV-MAN-002: Merkle root must be derivable from manifest.
        """
        print("Computing Merkle root...")
        
        # Read all content hashes from manifest
        hashes = []
        with open(manifest_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                hashes.append(entry['content_hash'])
                
        # Sort for determinism
        hashes.sort()
        
        # Build Merkle tree (simple implementation)
        def hash_pair(h1: str, h2: str) -> str:
            combined = h1 + h2
            return hashlib.sha256(combined.encode('utf-8')).hexdigest()
            
        level = hashes
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    next_level.append(hash_pair(level[i], level[i + 1]))
                else:
                    next_level.append(level[i])
            level = next_level
            
        merkle_root = level[0] if level else ""
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(merkle_root + '\n')
            
        print(f"✓ Merkle root: {merkle_root}")
        print(f"✓ Wrote Merkle root to {output_file}")
        
        return merkle_root


def get_git_commit() -> str:
    """Get current git commit SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def main():
    """Main entry point."""
    print("=" * 60)
    print("Uncharted Multiplayer Fractal Dataset Generator")
    print("=" * 60)
    
    # Get git commit
    commit = get_git_commit()
    print(f"Git commit: {commit[:8]}...")
    
    # Initialize generator
    seed_path = "seed/uncharted_multiplayer_universe.yaml"
    generator = MultiplayerGenerator(seed_path, commit)
    
    # Generate DAG
    generator.generate_dag()
    
    # Compute content hashes
    generator.compute_all_content_hashes()
    
    # Verify acyclic
    if not generator.verify_dag_acyclic():
        print("ERROR: DAG verification failed!")
        sys.exit(1)
        
    # Write outputs
    generator.write_dag("out/uncharted_mp_dag.json")
    generator.write_manifest("out/uncharted_mp_manifest.jsonl")
    merkle_root = generator.compute_merkle_root(
        "out/uncharted_mp_manifest.jsonl",
        "out/uncharted_mp_merkle_root.txt"
    )
    
    print("=" * 60)
    print("✓ Generation complete!")
    print(f"✓ Total nodes: {len(generator.nodes)}")
    print(f"✓ Merkle root: {merkle_root}")
    print("=" * 60)


if __name__ == "__main__":
    main()
