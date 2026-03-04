#!/usr/bin/env python3
"""
Topology Scanner for PERCEIVABLE_INFINITY Schema
================================================

Scans repository and classifies files into covenant-aware topology graph.
Implements the classification pipeline defined in PERCEIVABLE_INFINITY_SCHEMA.yaml.

Phases:
1. Census - Enumerate all files with ignore patterns
2. Dependency extraction - Extract imports and references
3. Node classification - Map files to 10 node classes
4. Edge classification - Map dependencies to 8 edge classes  
5. Zone assignment - Assign nodes to 7 zones + unclassified

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 1.0.0
"""

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class FileNode:
    """A file node in the topology graph."""
    
    file_id: str
    file_path: str
    file_size: int
    file_ext: str
    depth: int
    last_modified: float
    node_class: str = "UNCLASSIFIED"
    authority: str = "UNRESTRICTED"
    temporal: str = "OVERLAY"
    constraint_layer: List[str] = field(default_factory=list)
    verification: str = "NONE"
    zone: str = "zone_8_unclassified"
    sha256: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Edge:
    """An edge in the topology graph."""
    
    edge_id: str
    source: str
    target: str
    edge_class: str = "DEPENDENCY_IMPORT"
    directionality: str = "UNI"
    axis: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TopologyScanner:
    """
    Scans repository and builds covenant-aware topology graph.
    
    Implements PERCEIVABLE_INFINITY classification pipeline.
    """
    
    def __init__(self, root_path: str, schema_path: Optional[str] = None):
        """
        Initialize scanner.
        
        Args:
            root_path: Root directory to scan
            schema_path: Path to PERCEIVABLE_INFINITY_SCHEMA.yaml
        """
        self.root_path = Path(root_path).resolve()
        self.schema_path = schema_path or self.root_path / "PERCEIVABLE_INFINITY_SCHEMA.yaml"
        
        # Load schema
        self.schema = self._load_schema()
        
        # Census data
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Edge] = []
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "ignored_files": 0,
            "classified_nodes": 0,
            "unclassified_nodes": 0,
            "edges_created": 0,
            "node_class_counts": {},
            "edge_class_counts": {},
            "zone_counts": {},
        }
    
    def _load_schema(self) -> Dict:
        """Load PERCEIVABLE_INFINITY_SCHEMA.yaml."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")
        
        with open(self.schema_path, "r") as f:
            return yaml.safe_load(f)
    
    def scan(self) -> Dict:
        """
        Run full topology scan.
        
        Returns:
            Topology graph as dictionary
        """
        print(f"🔍 Scanning repository: {self.root_path}")
        print(f"📋 Using schema: {self.schema_path}")
        
        # Phase 1: Census
        print("\n📊 Phase 1: Census...")
        self._census()
        
        # Phase 2: Dependency extraction
        print("🔗 Phase 2: Dependency extraction...")
        self._extract_dependencies()
        
        # Phase 3: Node classification
        print("🏷️  Phase 3: Node classification...")
        self._classify_nodes()
        
        # Phase 4: Edge classification
        print("↔️  Phase 4: Edge classification...")
        self._classify_edges()
        
        # Phase 5: Zone assignment
        print("🗺️  Phase 5: Zone assignment...")
        self._assign_zones()
        
        # Build output
        print("\n✅ Scan complete!")
        self._print_statistics()
        
        return self._build_output()
    
    def _census(self):
        """Phase 1: Enumerate all files with ignore patterns."""
        ignore_patterns = self.schema.get("classification_pipeline", {}).get("census", {}).get("ignore_patterns", [])
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter directories in-place to skip ignored paths
            dirs[:] = [d for d in dirs if not self._should_ignore(d, ignore_patterns)]
            
            for filename in files:
                file_path = Path(root) / filename
                
                if self._should_ignore(str(file_path), ignore_patterns):
                    self.stats["ignored_files"] += 1
                    continue
                
                # Create node
                try:
                    relative_path = file_path.relative_to(self.root_path)
                    file_id = str(relative_path)
                    
                    stat = file_path.stat()
                    
                    node = FileNode(
                        file_id=file_id,
                        file_path=str(relative_path),
                        file_size=stat.st_size,
                        file_ext=file_path.suffix,
                        depth=len(relative_path.parts),
                        last_modified=stat.st_mtime,
                    )
                    
                    self.nodes[file_id] = node
                    self.stats["total_files"] += 1
                    
                except Exception as e:
                    print(f"⚠️  Error processing {file_path}: {e}")
    
    def _should_ignore(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any ignore pattern."""
        path_lower = path.lower()
        for pattern in patterns:
            if pattern.strip('.').lower() in path_lower:
                return True
        return False
    
    def _extract_dependencies(self):
        """Phase 2: Extract imports and references from files."""
        patterns = self.schema.get("classification_pipeline", {}).get("dependencies", {}).get("patterns", {})
        
        for file_id, node in self.nodes.items():
            file_path = self.root_path / node.file_path
            
            # Only process text files
            if node.file_size > 1_000_000:  # Skip files > 1MB
                continue
            
            try:
                # Try to read as text
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Extract imports based on file type
                if node.file_ext == ".py":
                    node.imports = self._extract_python_imports(content)
                elif node.file_ext in [".js", ".ts", ".jsx", ".tsx"]:
                    node.imports = self._extract_js_imports(content)
                elif node.file_ext in [".yaml", ".yml"]:
                    node.imports = self._extract_yaml_paths(content)
                    
            except Exception as e:
                # Skip binary or unreadable files
                pass
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python imports."""
        imports = []
        patterns = [
            r"^\s*from\s+([\w.]+)\s+import",
            r"^\s*import\s+([\w.]+)",
        ]
        
        for line in content.split("\n"):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript imports."""
        imports = []
        patterns = [
            r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"]",
            r"^\s*require\(['\"]([^'\"]+)['\"]\)",
        ]
        
        for line in content.split("\n"):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _extract_yaml_paths(self, content: str) -> List[str]:
        """Extract YAML path references."""
        imports = []
        pattern = r"^\s*-?\s*path:\s*(.+)$"
        
        for line in content.split("\n"):
            match = re.match(pattern, line)
            if match:
                path = match.group(1).strip()
                imports.append(path)
        
        return imports
    
    def _classify_nodes(self):
        """Phase 3: Classify nodes into 10 node classes."""
        rules = self.schema.get("classification_pipeline", {}).get("classification", {}).get("rules", [])
        
        # Sort rules by priority (descending)
        rules_sorted = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)
        
        for file_id, node in self.nodes.items():
            # Try each rule in priority order
            for rule in rules_sorted:
                if self._match_rule(node.file_path, rule.get("match", "")):
                    node.node_class = rule.get("assign", "UNCLASSIFIED")
                    
                    # Set properties based on node class from graph_schema
                    self._set_node_properties(node)
                    break
        
        # Update statistics
        for node in self.nodes.values():
            if node.node_class != "UNCLASSIFIED":
                self.stats["classified_nodes"] += 1
            else:
                self.stats["unclassified_nodes"] += 1
            
            self.stats["node_class_counts"][node.node_class] = \
                self.stats["node_class_counts"].get(node.node_class, 0) + 1
    
    def _match_rule(self, file_path: str, match_pattern: str) -> bool:
        """Check if file path matches the classification rule."""
        if not match_pattern or match_pattern == "**/* (default)":
            return True
        
        # Handle OR conditions
        if " OR " in match_pattern:
            patterns = match_pattern.split(" OR ")
            return any(self._match_single_pattern(file_path, p.strip()) for p in patterns)
        
        return self._match_single_pattern(file_path, match_pattern)
    
    def _match_single_pattern(self, file_path: str, pattern: str) -> bool:
        """Match single pattern (supports wildcards)."""
        # Exact match
        if file_path == pattern:
            return True
        
        # Wildcard match
        if "*" in pattern:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
            if re.match(regex_pattern, file_path):
                return True
        
        # Substring match
        if pattern in file_path:
            return True
        
        return False
    
    def _set_node_properties(self, node: FileNode):
        """Set node properties based on node class from graph_schema.yaml."""
        # Load node class definitions from schema
        try:
            with open(self.root_path / "topology" / "graph_schema.yaml", "r") as f:
                graph_schema = yaml.safe_load(f)
            
            node_defs = graph_schema.get("nodes", {})
            node_def = node_defs.get(node.node_class, {})
            
            # Set authority
            node.authority = node_def.get("authority", "UNRESTRICTED")
            
            # Set temporal
            node.temporal = node_def.get("temporal", "OVERLAY")
            
            # Set verification
            node.verification = node_def.get("verification", "NONE")
            
        except Exception as e:
            # If schema not found, use defaults
            pass
    
    def _classify_edges(self):
        """Phase 4: Classify edges based on source/target node classes."""
        rules = self.schema.get("classification_pipeline", {}).get("edge_classification", {}).get("rules", [])
        
        edge_id = 0
        
        for file_id, node in self.nodes.items():
            for import_ref in node.imports:
                # Try to resolve import to a node
                target_node = self._resolve_import(import_ref)
                
                if target_node:
                    # Classify edge
                    edge_class = self._classify_edge(node.node_class, target_node.node_class, rules)
                    
                    # Create edge
                    edge = Edge(
                        edge_id=f"edge_{edge_id}",
                        source=file_id,
                        target=target_node.file_id,
                        edge_class=edge_class,
                        directionality="BI" if edge_class == "CORRESPONDENCE_MAPPING" else "UNI",
                    )
                    
                    self.edges.append(edge)
                    self.stats["edges_created"] += 1
                    self.stats["edge_class_counts"][edge_class] = \
                        self.stats["edge_class_counts"].get(edge_class, 0) + 1
                    
                    edge_id += 1
    
    def _resolve_import(self, import_ref: str) -> Optional[FileNode]:
        """Resolve import reference to a node."""
        # Try direct path match
        if import_ref in self.nodes:
            return self.nodes[import_ref]
        
        # Try with .py extension
        if f"{import_ref}.py" in self.nodes:
            return self.nodes[f"{import_ref}.py"]
        
        # Try as module path (replace . with /)
        module_path = import_ref.replace(".", "/")
        if f"{module_path}.py" in self.nodes:
            return self.nodes[f"{module_path}.py"]
        
        # Try in src/
        if f"src/{module_path}.py" in self.nodes:
            return self.nodes[f"src/{module_path}.py"]
        
        return None
    
    def _classify_edge(self, source_class: str, target_class: str, rules: List[Dict]) -> str:
        """Classify edge based on source and target node classes."""
        for rule in rules:
            if_source = rule.get("if_source")
            and_target = rule.get("and_target")
            if_target = rule.get("if_target")
            if_source_or_target = rule.get("if_source_or_target")
            
            # Check if_source and and_target
            if if_source and and_target:
                if (if_source == source_class or if_source == "*"):
                    if isinstance(and_target, list):
                        if target_class in and_target or "*" in and_target:
                            return rule.get("assign", "DEPENDENCY_IMPORT")
                    elif and_target == target_class or and_target == "*":
                        return rule.get("assign", "DEPENDENCY_IMPORT")
            
            # Check if_source_or_target
            if if_source_or_target:
                if source_class == if_source_or_target or target_class == if_source_or_target:
                    return rule.get("assign", "DEPENDENCY_IMPORT")
            
            # Check if_target
            if if_target:
                if target_class == if_target:
                    return rule.get("assign", "DEPENDENCY_IMPORT")
        
        # Default
        return "DEPENDENCY_IMPORT"
    
    def _assign_zones(self):
        """Phase 5: Assign nodes to navigation zones."""
        rules = self.schema.get("classification_pipeline", {}).get("zone_assignment", {}).get("rules", [])
        
        for file_id, node in self.nodes.items():
            # Try each zone rule
            for rule in rules:
                zone_id = rule.get("zone")
                node_classes = rule.get("node_classes", [])
                paths = rule.get("paths", [])
                
                # Check node class match
                if node.node_class in node_classes:
                    node.zone = zone_id
                    break
                
                # Check path match
                for path_pattern in paths:
                    if self._match_single_pattern(node.file_path, path_pattern):
                        node.zone = zone_id
                        break
                
                if node.zone != "zone_8_unclassified":
                    break
        
        # Update statistics
        for node in self.nodes.values():
            self.stats["zone_counts"][node.zone] = \
                self.stats["zone_counts"].get(node.zone, 0) + 1
    
    def _print_statistics(self):
        """Print scan statistics."""
        print("\n📊 Topology Scan Statistics")
        print("=" * 60)
        print(f"Total files scanned:     {self.stats['total_files']}")
        print(f"Ignored files:           {self.stats['ignored_files']}")
        print(f"Classified nodes:        {self.stats['classified_nodes']}")
        print(f"Unclassified nodes:      {self.stats['unclassified_nodes']}")
        print(f"Edges created:           {self.stats['edges_created']}")
        
        print("\n📦 Node Classes:")
        for node_class, count in sorted(self.stats["node_class_counts"].items(), key=lambda x: -x[1]):
            print(f"  {node_class:30s} {count:6d}")
        
        print("\n🔗 Edge Classes:")
        for edge_class, count in sorted(self.stats["edge_class_counts"].items(), key=lambda x: -x[1]):
            print(f"  {edge_class:30s} {count:6d}")
        
        print("\n🗺️  Zones:")
        for zone, count in sorted(self.stats["zone_counts"].items()):
            print(f"  {zone:30s} {count:6d}")
        print("=" * 60)
    
    def _build_output(self) -> Dict:
        """Build output dictionary."""
        return {
            "metadata": {
                "schema_version": self.schema.get("schema_version", "1.0.0"),
                "scan_timestamp": datetime.now().isoformat(),
                "root_path": str(self.root_path),
                "schema_path": str(self.schema_path),
            },
            "statistics": self.stats,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
        }
    
    def save(self, output_path: str):
        """Save topology graph to JSON file."""
        output = self._build_output()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved topology graph to: {output_file}")


def main():
    """Main entry point for topology scanner."""
    import sys
    
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = sys.argv[2] if len(sys.argv) > 2 else "topology_graph.json"
    
    scanner = TopologyScanner(root_path)
    scanner.scan()
    scanner.save(output_path)


if __name__ == "__main__":
    main()
