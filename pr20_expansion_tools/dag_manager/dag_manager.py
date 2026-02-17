#!/usr/bin/env python3
"""
DAG Manager - PR #20 Deterministic Expansion Tool

Maintains dependency graph of every file, module, and shard.
Validates acyclic topologies and updates DAG manifests.
"""

import json
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class DAGManager:
    """Manages directed acyclic graph of file and module dependencies."""
    
    def __init__(self, dag_file: str = 'dag_manifest.json'):
        """Initialize DAG manager."""
        self.dag_file = Path(dag_file)
        self.nodes = {}  # node_id -> node_data
        self.edges = defaultdict(set)  # from_id -> set of to_ids
        self.reverse_edges = defaultdict(set)  # to_id -> set of from_ids
        
        if self.dag_file.exists():
            self.load()
    
    def add_node(self, node_id: str, node_data: Dict) -> None:
        """Add a node to the DAG."""
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        self.nodes[node_id] = {
            **node_data,
            'added_at': datetime.now(timezone.utc).isoformat(),
        }
    
    def add_edge(self, from_id: str, to_id: str, edge_type: str = 'depends_on') -> None:
        """Add an edge between two nodes."""
        if from_id not in self.nodes:
            raise ValueError(f"Source node {from_id} does not exist")
        if to_id not in self.nodes:
            raise ValueError(f"Target node {to_id} does not exist")
        
        # Check for cycles before adding
        if self._would_create_cycle(from_id, to_id):
            raise ValueError(f"Adding edge {from_id} -> {to_id} would create a cycle")
        
        self.edges[from_id].add(to_id)
        self.reverse_edges[to_id].add(from_id)
    
    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """Check if adding an edge would create a cycle."""
        # If we can reach from_id starting from to_id, we have a cycle
        visited = set()
        queue = deque([to_id])
        
        while queue:
            current = queue.popleft()
            if current == from_id:
                return True
            
            if current in visited:
                continue
            
            visited.add(current)
            queue.extend(self.edges.get(current, []))
        
        return False
    
    def validate_acyclic(self) -> Tuple[bool, Optional[List[str]]]:
        """Validate that the DAG is acyclic. Returns (is_valid, cycle_path)."""
        # Use Kahn's algorithm for topological sort
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for node_id in self.nodes:
            in_degree[node_id] = len(self.reverse_edges.get(node_id, set()))
        
        # Queue nodes with no incoming edges
        queue = deque([node_id for node_id in self.nodes if in_degree[node_id] == 0])
        processed = []
        
        while queue:
            current = queue.popleft()
            processed.append(current)
            
            # Reduce in-degree of neighbors
            for neighbor in self.edges.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we processed all nodes, the graph is acyclic
        if len(processed) == len(self.nodes):
            return True, None
        
        # Find a cycle for reporting
        unprocessed = set(self.nodes.keys()) - set(processed)
        cycle = self._find_cycle(unprocessed)
        return False, cycle
    
    def _find_cycle(self, nodes: Set[str]) -> List[str]:
        """Find a cycle in the given set of nodes."""
        visited = set()
        path = []
        
        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            path.append(node)
            
            for neighbor in self.edges.get(node, []):
                if neighbor in nodes:
                    result = dfs(neighbor)
                    if result:
                        return result
            
            path.pop()
            return None
        
        for node in nodes:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle
        
        return []
    
    def topological_sort(self) -> List[str]:
        """Return a topological sort of the DAG."""
        is_valid, cycle = self.validate_acyclic()
        if not is_valid:
            raise ValueError(f"DAG contains cycle: {' -> '.join(cycle)}")
        
        in_degree = defaultdict(int)
        for node_id in self.nodes:
            in_degree[node_id] = len(self.reverse_edges.get(node_id, set()))
        
        queue = deque([node_id for node_id in self.nodes if in_degree[node_id] == 0])
        sorted_nodes = []
        
        while queue:
            current = queue.popleft()
            sorted_nodes.append(current)
            
            for neighbor in self.edges.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return sorted_nodes
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get all direct dependencies of a node."""
        return self.edges.get(node_id, set())
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """Get all nodes that depend on this node."""
        return self.reverse_edges.get(node_id, set())
    
    def get_transitive_dependencies(self, node_id: str) -> Set[str]:
        """Get all transitive dependencies of a node."""
        dependencies = set()
        queue = deque([node_id])
        
        while queue:
            current = queue.popleft()
            for dep in self.edges.get(current, []):
                if dep not in dependencies:
                    dependencies.add(dep)
                    queue.append(dep)
        
        return dependencies
    
    def compute_dag_hash(self) -> str:
        """Compute a deterministic hash of the entire DAG."""
        # Sort nodes and edges for determinism
        sorted_nodes = sorted(self.nodes.items())
        sorted_edges = sorted((k, sorted(v)) for k, v in self.edges.items())
        
        dag_repr = json.dumps({
            'nodes': sorted_nodes,
            'edges': sorted_edges,
        }, sort_keys=True)
        
        return hashlib.sha256(dag_repr.encode('utf-8')).hexdigest()
    
    def export_graphviz(self, output_file: str = 'dag_graph.dot') -> None:
        """Export DAG to Graphviz DOT format."""
        lines = ['digraph DAG {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box];')
        
        # Add nodes
        for node_id, node_data in sorted(self.nodes.items()):
            label = node_data.get('label', node_id)
            node_type = node_data.get('type', 'unknown')
            lines.append(f'  "{node_id}" [label="{label}", tooltip="{node_type}"];')
        
        # Add edges
        for from_id, to_ids in sorted(self.edges.items()):
            for to_id in sorted(to_ids):
                lines.append(f'  "{from_id}" -> "{to_id}";')
        
        lines.append('}')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def save(self, output_file: Optional[str] = None) -> None:
        """Save DAG to JSON file."""
        if output_file is None:
            output_file = self.dag_file
        
        # Convert sets to lists for JSON serialization
        edges_list = {k: list(v) for k, v in self.edges.items()}
        
        dag_data = {
            'nodes': self.nodes,
            'edges': edges_list,
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': sum(len(v) for v in self.edges.values()),
                'dag_hash': self.compute_dag_hash(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dag_data, f, indent=2)
    
    def load(self, input_file: Optional[str] = None) -> None:
        """Load DAG from JSON file."""
        if input_file is None:
            input_file = self.dag_file
        
        with open(input_file, 'r', encoding='utf-8') as f:
            dag_data = json.load(f)
        
        self.nodes = dag_data['nodes']
        
        # Convert lists back to sets
        self.edges = defaultdict(set)
        for from_id, to_ids in dag_data['edges'].items():
            self.edges[from_id] = set(to_ids)
        
        # Rebuild reverse edges
        self.reverse_edges = defaultdict(set)
        for from_id, to_ids in self.edges.items():
            for to_id in to_ids:
                self.reverse_edges[to_id].add(from_id)
    
    def add_shard(self, shard_id: str, shard_data: Dict, dependencies: Optional[List[str]] = None) -> None:
        """Add a complete shard to the DAG."""
        # Add shard node
        self.add_node(shard_id, {
            'type': 'shard',
            'label': shard_id,
            **shard_data,
        })
        
        # Add file nodes
        for file_info in shard_data.get('files', []):
            file_id = file_info['file_id']
            self.add_node(file_id, {
                'type': 'file',
                'label': file_info['filename'],
                **file_info,
            })
            
            # Link file to shard
            self.add_edge(file_id, shard_id, 'belongs_to')
        
        # Add dependencies to other shards
        if dependencies:
            for dep_id in dependencies:
                self.add_edge(shard_id, dep_id, 'depends_on')
    
    def get_stats(self) -> Dict:
        """Get DAG statistics."""
        return {
            'node_count': len(self.nodes),
            'edge_count': sum(len(v) for v in self.edges.values()),
            'shard_count': sum(1 for n in self.nodes.values() if n.get('type') == 'shard'),
            'file_count': sum(1 for n in self.nodes.values() if n.get('type') == 'file'),
            'dag_hash': self.compute_dag_hash(),
            'is_valid': self.validate_acyclic()[0],
        }


def main():
    """Main function for testing DAG manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage DAG of shards and files')
    parser.add_argument('--dag-file', type=str, default='dag_manifest.json', help='DAG manifest file')
    parser.add_argument('--action', choices=['validate', 'export', 'stats'], default='stats', help='Action to perform')
    parser.add_argument('--output', type=str, help='Output file for export')
    
    args = parser.parse_args()
    
    dag = DAGManager(args.dag_file)
    
    if args.action == 'validate':
        is_valid, cycle = dag.validate_acyclic()
        if is_valid:
            print("✓ DAG is valid (acyclic)")
        else:
            print(f"✗ DAG contains cycle: {' -> '.join(cycle)}")
    
    elif args.action == 'export':
        output_file = args.output or 'dag_graph.dot'
        dag.export_graphviz(output_file)
        print(f"DAG exported to {output_file}")
    
    elif args.action == 'stats':
        stats = dag.get_stats()
        print("DAG Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
