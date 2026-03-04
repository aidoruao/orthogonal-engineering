#!/usr/bin/env python3
"""
PERCEIVABLE_INFINITY Pipeline
==============================

Main orchestrator for generating covenant-aware topology visualization.

Runs the full pipeline:
1. TopologyScanner - Scan and classify repository
2. GraphLoader - Load and validate graph
3. Renderer - Generate interactive HTML

Usage:
    python generate_perceivable_infinity.py [root_path]

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add topology module to path
sys.path.insert(0, str(Path(__file__).parent / "topology"))

from topology.topology_scanner import TopologyScanner
from topology.graph_loader import GraphLoader
from topology.renderer import Renderer


def main():
    """Main pipeline execution."""
    # Get root path
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."
    root_path = Path(root_path).resolve()
    
    print("=" * 80)
    print("⚛️  PERCEIVABLE_INFINITY Pipeline")
    print("=" * 80)
    print(f"Repository: {root_path}")
    print()
    
    # Paths
    schema_path = root_path / "PERCEIVABLE_INFINITY_SCHEMA.yaml"
    graph_path = root_path / "topology_graph.json"
    report_path = root_path / "topology_classification_report.json"
    html_path = root_path / "PERCEIVABLE_INFINITY.html"
    
    # Check if schema exists
    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        print("   Please ensure PERCEIVABLE_INFINITY_SCHEMA.yaml exists in the repository root.")
        sys.exit(1)
    
    try:
        # Phase 1: Scan and classify
        print("🔍 Step 1: Scanning repository...")
        print("-" * 80)
        scanner = TopologyScanner(str(root_path), str(schema_path))
        scanner.scan()
        scanner.save(str(graph_path))
        
        print()
        
        # Phase 2: Load and validate
        print("📊 Step 2: Loading topology graph...")
        print("-" * 80)
        loader = GraphLoader(str(graph_path))
        loader.load()
        
        print()
        
        # Phase 3: Render HTML
        print("🎨 Step 3: Rendering visualization...")
        print("-" * 80)
        renderer = Renderer(str(schema_path), str(graph_path))
        renderer.render(str(html_path))
        
        print()
        print("=" * 80)
        print("✅ Pipeline complete!")
        print("=" * 80)
        print()
        print("📁 Output files:")
        print(f"   1. {graph_path.name} - Topology graph JSON")
        print(f"   2. {html_path.name} - Interactive HTML visualization")
        print()
        print("🌐 Open the HTML file in a browser to explore the topology:")
        print(f"   file://{html_path}")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ Pipeline failed!")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
