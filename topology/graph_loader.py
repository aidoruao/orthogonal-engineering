#!/usr/bin/env python3
"""
Graph Loader for PERCEIVABLE_INFINITY Schema
============================================

Loads topology graph from JSON and provides query interface.

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class GraphLoader:
    """
    Loads and queries topology graph.
    """
    
    def __init__(self, graph_path: str):
        """
        Initialize loader.
        
        Args:
            graph_path: Path to topology_graph.json
        """
        self.graph_path = Path(graph_path)
        self.graph = None
        self.nodes = {}
        self.edges = []
        self.metadata = {}
        self.statistics = {}
    
    def load(self) -> Dict:
        """
        Load topology graph from JSON.
        
        Returns:
            Graph dictionary
        """
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Graph not found: {self.graph_path}")
        
        with open(self.graph_path, "r") as f:
            self.graph = json.load(f)
        
        self.nodes = self.graph.get("nodes", {})
        self.edges = self.graph.get("edges", [])
        self.metadata = self.graph.get("metadata", {})
        self.statistics = self.graph.get("statistics", {})
        
        print(f"✅ Loaded topology graph: {self.graph_path}")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.edges)}")
        
        return self.graph
    
    def get_nodes_by_class(self, node_class: str) -> List[Dict]:
        """Get all nodes of a specific class."""
        return [
            node for node in self.nodes.values()
            if node.get("node_class") == node_class
        ]
    
    def get_nodes_by_zone(self, zone: str) -> List[Dict]:
        """Get all nodes in a specific zone."""
        return [
            node for node in self.nodes.values()
            if node.get("zone") == zone
        ]
    
    def get_edges_by_class(self, edge_class: str) -> List[Dict]:
        """Get all edges of a specific class."""
        return [
            edge for edge in self.edges
            if edge.get("edge_class") == edge_class
        ]
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_incoming_edges(self, node_id: str) -> List[Dict]:
        """Get all edges pointing to this node."""
        return [
            edge for edge in self.edges
            if edge.get("target") == node_id
        ]
    
    def get_outgoing_edges(self, node_id: str) -> List[Dict]:
        """Get all edges starting from this node."""
        return [
            edge for edge in self.edges
            if edge.get("source") == node_id
        ]
    
    def get_classified_nodes(self) -> List[Dict]:
        """Get all classified nodes (not UNCLASSIFIED)."""
        return [
            node for node in self.nodes.values()
            if node.get("node_class") != "UNCLASSIFIED"
        ]
    
    def get_unclassified_nodes(self) -> List[Dict]:
        """Get all unclassified nodes."""
        return [
            node for node in self.nodes.values()
            if node.get("node_class") == "UNCLASSIFIED"
        ]
    
    def search_nodes(self, query: str) -> List[Dict]:
        """
        Search nodes by file path or node ID.
        
        Args:
            query: Search query
            
        Returns:
            Matching nodes
        """
        query_lower = query.lower()
        return [
            node for node in self.nodes.values()
            if query_lower in node.get("file_id", "").lower() or
               query_lower in node.get("file_path", "").lower()
        ]
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        return self.statistics
    
    def get_metadata(self) -> Dict:
        """Get graph metadata."""
        # TODO: Expand get_metadata() - stub detected by Yeshua Agent
        return self.metadata


def main():
    """Main entry point for graph loader."""
    import sys
    
    graph_path = sys.argv[1] if len(sys.argv) > 1 else "topology_graph.json"
    
    loader = GraphLoader(graph_path)
    loader.load()
    
    # Print summary
    print("\n📊 Graph Summary:")
    stats = loader.get_statistics()
    print(f"   Total files:        {stats.get('total_files', 0)}")
    print(f"   Classified nodes:   {stats.get('classified_nodes', 0)}")
    print(f"   Unclassified nodes: {stats.get('unclassified_nodes', 0)}")
    print(f"   Total edges:        {stats.get('edges_created', 0)}")


if __name__ == "__main__":
    main()
