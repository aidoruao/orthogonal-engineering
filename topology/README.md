# PERCEIVABLE_INFINITY - Covenant-Aware Topology Graph

This module implements the PERCEIVABLE_INFINITY schema for rendering repository topology as an interactive, covenant-aware visualization.

## Overview

The PERCEIVABLE_INFINITY schema transforms a 66k-file repository into an interactive topology graph by:
1. **Classifying files** into 10 covenant-aware node classes
2. **Mapping dependencies** into 8 typed edge classes
3. **Organizing nodes** into 7 navigation zones + unclassified
4. **Rendering** as interactive HTML with 3 zoom levels

This is **not** a directory tree visualization - it's a formal topology graph based on covenant principles defined in `sigma-lora-covenant`.

## Quick Start

```bash
# Generate the visualization
python3 generate_perceivable_infinity.py .

# Open in browser
open PERCEIVABLE_INFINITY.html
```

## Architecture

### Schema Files

- `PERCEIVABLE_INFINITY_SCHEMA.yaml` - Master rendering schema
- `topology/graph_schema.yaml` - 10 node classes, 8 edge classes, 7 axes, 10 invariants
- `topology/forbidden.yaml` - 10 forbidden patterns + 5 forbidden rendering patterns

### Python Modules

- `topology/topology_scanner.py` - 5-phase classification pipeline
- `topology/graph_loader.py` - Graph loading and query interface
- `topology/renderer.py` - Interactive HTML generation
- `generate_perceivable_infinity.py` - Main orchestrator

### Output Files

- `topology_graph.json` - Serialized graph data (can be re-rendered without re-scanning)
- `PERCEIVABLE_INFINITY.html` - Interactive visualization

## Classification Pipeline

The scanner implements a 5-phase pipeline:

### Phase 1: Census
- Enumerate all files in repository
- Apply ignore patterns (`.git`, `__pycache__`, `node_modules`, etc.)
- Extract file metadata (size, extension, depth, last modified)

### Phase 2: Dependency Extraction
- Extract imports from Python files (`import`, `from ... import`)
- Extract requires from JavaScript/TypeScript files
- Extract path references from YAML files

### Phase 3: Node Classification
Classify files into 10 node classes based on path patterns:

| Node Class | Examples | Authority | Temporal |
|------------|----------|-----------|----------|
| `COVENANT_ROOT` | `covenant.yaml`, `INVARIANTS.json`, `AI_INSTRUCTIONS.md` | EXTERNAL_ONLY | GENESIS |
| `PRINCIPLE_MODULE` | `src/principles.py` | VALIDATED | FOUNDATION |
| `OPERATIONAL_MODE_ENFORCER` | `src/operational_modes.py` | VALIDATED | FOUNDATION |
| `GUARDIAN_SYSTEM` | `JESUS_REALITY_GUARDIAN.py`, `*guardian*.py` | VALIDATED | SUBSTRATE |
| `CORRESPONDENCE_BRIDGE` | `correspondence_bridge/`, `correspondence_*.py` | VALIDATED | SUBSTRATE |
| `FORGIVENESS_MODULE` | `forgiveness_system/`, `*forgiveness*.py` | UNRESTRICTED | OVERLAY |
| `VIOLATION_LOG` | `.ontological_violations/`, `.jesus_reality_violations/` | IMMUTABLE | EPHEMERAL |
| `EVIDENCE_ARTIFACT` | `evidence/`, `canonical_evidence/`, `sha256_*.json` | IMMUTABLE | EPHEMERAL |
| `INFRASTRUCTURE_REGISTRY` | `src/infrastructure.py` | UNRESTRICTED | FOUNDATION |
| `DOCUMENTATION_INDEX` | `README.md`, `_START_HERE.md`, `index.html` | UNRESTRICTED | OVERLAY |
| `UNCLASSIFIED` | All other files | UNRESTRICTED | OVERLAY |

### Phase 4: Edge Classification
Classify dependencies into 8 edge classes based on source/target node types:

| Edge Class | From | To | Line Style |
|------------|------|-----|------------|
| `COVENANT_BINDING` | COVENANT_ROOT | PRINCIPLE_MODULE, GUARDIAN_SYSTEM | Thick solid |
| `DEPENDENCY_IMPORT` | Any | Any | Thin solid |
| `VERIFICATION_CHAIN` | Any | EVIDENCE_ARTIFACT | Dotted |
| `MODE_RESTRICTION` | OPERATIONAL_MODE_ENFORCER | Any | Dashed |
| `GUARDIAN_WATCH` | GUARDIAN_SYSTEM | Any | Thin dashed |
| `CORRESPONDENCE_MAPPING` | CORRESPONDENCE_BRIDGE | Any | Double line |
| `VIOLATION_REFERENCE` | Any | VIOLATION_LOG | Wavy |
| `SPATIAL_CONTAINMENT` | Any | Any | Hidden |

### Phase 5: Zone Assignment
Assign nodes to 8 navigation zones:

| Zone | Node Classes | Change Policy | Border Color |
|------|--------------|---------------|--------------|
| `zone_1_immutable_authority` | COVENANT_ROOT, GUARDIAN_SYSTEM | EXTERNAL_AUTHORITY_ONLY | Red |
| `zone_2_detection_enforcement` | VIOLATION_LOG | TIGHTEN_ONLY | Orange |
| `zone_3_correspondence_bridge` | CORRESPONDENCE_BRIDGE | PRESERVE_BIJECTION | Blue |
| `zone_4_forgiveness_grace` | FORGIVENESS_MODULE | NO_COERCION_INTRODUCTION | Purple |
| `zone_5_analysis_reporting` | EVIDENCE_ARTIFACT | ADDITIVE_ONLY | Green |
| `zone_6_deployment_orchestration` | (path-based) | HONOR_UPSTREAM_CONSTRAINTS | Gray |
| `zone_7_documentation` | DOCUMENTATION_INDEX | REFLECT_ACTUAL_STATE | White |
| `zone_8_unclassified` | UNCLASSIFIED | UNRESTRICTED | Dark gray |

## Interactive Visualization

### 3 Zoom Levels

1. **Level 0: Zones Only** - Shows 7 zones as collapsed regions
2. **Level 1: Classified Nodes** - Shows ~50-100 classified nodes (default view)
3. **Level 2: All Nodes** - Shows all 2,743+ nodes including unclassified

### Features

- **Search**: Find nodes by file path or ID
- **Filter by Zone**: Show only specific zones
- **Node Details**: Click any node to see metadata panel with:
  - File path, size, class, authority, temporal
  - Zone membership
  - Incoming/outgoing edge counts
  - Verification status
- **Legend**: Color-coded node class reference

### Forbidden Rendering Patterns

The visualization enforces 5 forbidden rendering patterns:

1. `SIZE_AS_IMPORTANCE` - Node size ≠ file size or import count
2. `CENTRALITY_AS_AUTHORITY` - Layout position ≠ authority
3. `COLOR_AS_CONSTRAINT` - Color ≠ constraint layer (colors = node class)
4. `ANIMATION_AS_EXECUTION` - No animated flows (static topology)
5. `DYNAMIC_EDGE_ROUTING` - Edge paths fixed at render time

## Programmatic Usage

### Scan and Save

```python
from topology.topology_scanner import TopologyScanner

scanner = TopologyScanner(".", "PERCEIVABLE_INFINITY_SCHEMA.yaml")
scanner.scan()
scanner.save("topology_graph.json")
```

### Load and Query

```python
from topology.graph_loader import GraphLoader

loader = GraphLoader("topology_graph.json")
loader.load()

# Query by node class
covenant_roots = loader.get_nodes_by_class("COVENANT_ROOT")

# Query by zone
zone_1_nodes = loader.get_nodes_by_zone("zone_1_immutable_authority")

# Search nodes
matches = loader.search_nodes("guardian")

# Get edges
incoming = loader.get_incoming_edges("INVARIANTS.json")
outgoing = loader.get_outgoing_edges("src/principles.py")
```

### Render HTML

```python
from topology.renderer import Renderer

renderer = Renderer("PERCEIVABLE_INFINITY_SCHEMA.yaml", "topology_graph.json")
renderer.render("PERCEIVABLE_INFINITY.html")
```

## Statistics

Sample output from scanning this repository:

```
Total files scanned:     2743
Ignored files:           10
Classified nodes:        783
Unclassified nodes:      1960
Edges created:           623

Node Classes:
  UNCLASSIFIED                     1960
  FORGIVENESS_MODULE                693
  DOCUMENTATION_INDEX                43
  EVIDENCE_ARTIFACT                  39
  VIOLATION_LOG                       3
  COVENANT_ROOT                       2
  CORRESPONDENCE_BRIDGE               2
  GUARDIAN_SYSTEM                     1

Edge Classes:
  DEPENDENCY_IMPORT                 621
  CORRESPONDENCE_MAPPING              1
  VERIFICATION_CHAIN                  1

Zones:
  zone_1_immutable_authority          3
  zone_2_detection_enforcement        8
  zone_3_correspondence_bridge        2
  zone_4_forgiveness_grace          693
  zone_5_analysis_reporting          83
  zone_6_deployment_orchestration     69
  zone_7_documentation              125
  zone_8_unclassified              1760
```

## Testing

Run tests with:

```bash
pytest tests/test_perceivable_infinity.py -v
```

Tests cover:
- Scanner initialization
- Census phase (file enumeration)
- Node classification
- Dependency extraction (Python, JS, YAML)
- Zone assignment
- Graph loading and queries

## Authority

This implementation derives authority from:
- `PERCEIVABLE_INFINITY_SCHEMA.yaml` - Master rendering specification
- `topology/graph_schema.yaml` - Formal node/edge/axis definitions
- `topology/forbidden.yaml` - Prohibited patterns
- `TOPOLOGY_MAP.yaml` - Repository-specific node/zone mappings

## Version

Schema Version: 1.0.0  
Implementation Date: 2026-03-04  
Authority: sigma-lora-covenant topology principles
