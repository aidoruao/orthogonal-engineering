#!/usr/bin/env python3
"""
PERCEIVABLE_INFINITY Pipeline
==============================

Main orchestrator for generating covenant-aware topology visualization.

Runs the full pipeline:
1. TopologyScanner - Scan and classify repository (7 phases including
   hash verification and cluster aggregation)
2. GraphLoader - Load and validate graph
3. Renderer - Generate interactive HTML
4. Hash manifest - Write canonical/hash_manifest.json

Usage:
    python generate_perceivable_infinity.py [root_path] [--full-hash]

    --full-hash: Compute SHA-256 for every file (slow at 67k+ scale).
                 Default: only covenant-critical node classes are hashed.

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 2.0.0
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
    # Parse arguments
    args = sys.argv[1:]
    full_hash = "--full-hash" in args
    positional = [a for a in args if not a.startswith("--")]

    root_path = positional[0] if positional else "."
    root_path = Path(root_path).resolve()

    print("=" * 80)
    print("⚛️  PERCEIVABLE_INFINITY Pipeline v2.0.0")
    print("=" * 80)
    print(f"Repository: {root_path}")
    print(f"Full-hash mode: {'enabled' if full_hash else 'disabled (covenant-critical only)'}")
    print()

    # Paths
    schema_path = root_path / "PERCEIVABLE_INFINITY_SCHEMA.yaml"
    graph_path = root_path / "topology_graph.json"
    html_path = root_path / "PERCEIVABLE_INFINITY.html"
    manifest_path = root_path / "canonical" / "hash_manifest.json"

    # Check if schema exists
    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        print("   Please ensure PERCEIVABLE_INFINITY_SCHEMA.yaml exists in the repository root.")
        sys.exit(1)

    try:
        # Step 1: Scan and classify (7 phases)
        print("🔍 Step 1: Scanning repository (7 phases)...")
        print("-" * 80)
        scanner = TopologyScanner(str(root_path), str(schema_path), full_hash=full_hash)
        scanner.scan()
        scanner.save(str(graph_path))

        # Step 2: Write hash manifest
        print()
        print("🔐 Step 2: Writing hash manifest...")
        print("-" * 80)
        scanner.save_hash_manifest(str(manifest_path))

        # Step 3: Load and validate
        print()
        print("📊 Step 3: Loading topology graph...")
        print("-" * 80)
        loader = GraphLoader(str(graph_path))
        loader.load()

        # Step 4: Render HTML
        print()
        print("🎨 Step 4: Rendering visualization...")
        print("-" * 80)
        renderer = Renderer(str(schema_path), str(graph_path))
        renderer.render(str(html_path))

        print()
        print("=" * 80)
        print("✅ Pipeline complete!")
        print("=" * 80)
        print()
        print("📁 Output files:")
        print(f"   1. {graph_path.name}              - Topology graph JSON (nodes + clusters)")
        print(f"   2. {html_path.name} - Interactive HTML visualization")
        print(f"   3. canonical/hash_manifest.json   - SHA-256 hash manifest")
        print()
        print("🌐 Open the HTML file in a browser to explore the topology:")
        print(f"   python3 -m http.server 8080  # run from repo root, then open http://localhost:8080/PERCEIVABLE_INFINITY.html")
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
