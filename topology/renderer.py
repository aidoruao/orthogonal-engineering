#!/usr/bin/env python3
"""
Renderer for PERCEIVABLE_INFINITY Schema
========================================

Generates interactive HTML visualization of covenant-aware topology graph.
Produces a lightweight HTML shell that loads graph data from an external JSON
file via fetch() — never embeds the full node list in the HTML.

Zoom levels:
  Level 0 — Zones only (aggregated cards, no individual nodes visible)
  Level 1 — Classified nodes per zone (UNCLASSIFIED excluded; max 200/zone)
  Level 2 — Full detail with viewport-capped nodes loaded from JSON

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 2.0.0
"""

import html as _html
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# HTML-escape helper: escapes content sourced from YAML/git before embedding in HTML.
_esc = _html.escape

# Maximum nodes rendered per zone at each zoom level to avoid DOM overload.
MAX_NODES_PER_ZONE_LEVEL1 = 200
MAX_NODES_PER_ZONE_LEVEL2 = 500


class Renderer:
    """
    Renders topology graph as interactive HTML.

    The rendered HTML fetches graph data at runtime via fetch(graphDataUrl).
    Only summary statistics and schema-derived colours are baked into the HTML.
    """

    def __init__(self, schema_path: str, graph_path: str):
        """
        Initialize renderer.

        Args:
            schema_path: Path to PERCEIVABLE_INFINITY_SCHEMA.yaml
            graph_path: Path to topology_graph.json (used for metadata/stats
                        baked into the shell; the browser loads it at runtime).
        """
        self.schema_path = Path(schema_path)
        self.graph_path = Path(graph_path)

        # Load data
        self.schema = self._load_schema()
        self.graph = self._load_graph()

    def _load_schema(self) -> Dict:
        """Load schema."""
        with open(self.schema_path, "r") as f:
            return yaml.safe_load(f)

    def _load_graph(self) -> Dict:
        """Load graph (metadata + stats only; full nodes are fetched at runtime)."""
        with open(self.graph_path, "r") as f:
            return json.load(f)

    def _load_universe_seeds(self) -> Dict[str, Dict]:
        """Load universe seed files for PRs #60, #61, #62.

        Returns a dict keyed by domain name with seed YAML content.
        Gracefully returns empty dict for each seed that cannot be loaded.
        """
        root = self.schema_path.parent
        seed_map = {
            "food_cart": root / "seed" / "food_cart_universe.yaml",
            "uncharted": root / "seed" / "uncharted_multiplayer_universe.yaml",
            "skate4": root / "seed" / "skate4_multiplayer_universe.yaml",
        }
        seeds: Dict[str, Dict] = {}
        for domain, path in seed_map.items():
            if path.exists():
                with open(path, "r") as f:
                    seeds[domain] = yaml.safe_load(f) or {}
            else:
                seeds[domain] = {}
        return seeds

    def _get_commit_info(self) -> Dict[str, str]:
        """Retrieve latest commit metadata from git.

        Returns a dict with sha, subject, author, date.  All values fall back
        to 'N/A' when git is unavailable or the working directory is not a
        repo, so the HTML always renders cleanly.

        Values are HTML-escaped before being stored so callers can embed them
        directly into HTML without further escaping.
        """
        fields = {"sha": "N/A", "subject": "N/A", "author": "N/A", "date": "N/A"}
        # Locate git via PATH to avoid hard-coding a platform-specific path;
        # shutil.which returns None if git is not found, so we bail early.
        git_exe = shutil.which("git")
        if git_exe is None:
            return fields
        try:
            result = subprocess.run(
                [git_exe, "log", "-1", "--pretty=format:%H%n%s%n%an%n%ai"],
                capture_output=True,
                text=True,
                cwd=self.schema_path.parent,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().splitlines()
                keys = ["sha", "subject", "author", "date"]
                for key, line in zip(keys, lines):
                    fields[key] = _esc(line.strip())
        except Exception:
            pass
        return fields

    def render(self, output_path: str):
        """
        Render interactive HTML visualization.

        Args:
            output_path: Output HTML file path
        """
        print(f"🎨 Rendering PERCEIVABLE_INFINITY visualization...")

        html = self._generate_html()

        output_file = Path(output_path)
        with open(output_file, "w") as f:
            f.write(html)

        print(f"✅ Saved visualization to: {output_file}")
    
    def _generate_html(self) -> str:
        """Generate complete HTML document.

        The HTML shell contains only metadata and schema-derived constants.
        Node/edge data is loaded at runtime via fetch(graphDataUrl) — this
        keeps the file small regardless of repository scale.

        New in PR #62 sync:
        - Commit Info section baked at render time
        - Substrate Domain panels for Food Cart (#60), Uncharted (#61), Skate 4 (#62)
        - Active invariants + Merkle root placeholders per universe
        - Inelasticity visualization (Skate 4 microtransaction structural nullification)
        - ARIA roles and WCAG 2.1 AA compliance
        - LOD fractal rendering description
        """
        stats = self.graph.get("statistics", {})
        metadata = self.graph.get("metadata", {})

        # Get rendering config from schema
        node_colors = (
            self.schema
            .get("rendering_layers", {})
            .get("node_layer", {})
            .get("visual_mapping", {})
            .get("node_class_to_color", {})
        )

        # Graph URL — browser fetches this relative path at runtime.
        # The HTML is expected to be served/opened from the same directory as
        # the JSON artifact.  When opened via file://, most modern browsers
        # allow same-origin fetch; the UI shows an explicit warning if it fails.
        graph_url = self.graph_path.name

        # Bake only compact summary stats + node colors into the HTML shell.
        stats_json = json.dumps(stats)
        node_colors_json = json.dumps(node_colors)

        # Universe seeds (PRs #60, #61, #62) — baked-in domain panels
        seeds = self._load_universe_seeds()
        domain_panels_html = self._generate_domain_panels(seeds)

        # Commit info — baked at render time as a Static Witness
        commit = self._get_commit_info()
        commit_sha_short = commit["sha"][:12] if commit["sha"] != "N/A" else "N/A"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PERCEIVABLE_INFINITY - Covenant Topology Graph</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid #2a2a3e;
        }}
        
        h1 {{
            color: #00d4ff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #888;
            font-size: 1.1em;
        }}
        
        .controls {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #2a2a3e;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .control-group {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        label {{
            color: #888;
            font-size: 0.9em;
        }}
        
        select, input[type="text"] {{
            background: #0d0d0d;
            color: #e0e0e0;
            border: 1px solid #2a2a3e;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        button {{
            background: #00d4ff;
            color: #0a0a0a;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }}
        
        button:hover {{
            background: #00b8e6;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #2a2a3e;
        }}
        
        .stat-value {{
            font-size: 2em;
            color: #00d4ff;
            font-weight: bold;
        }}
        
        .stat-label {{
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .visualization {{
            background: #1a1a2e;
            border-radius: 8px;
            border: 1px solid #2a2a3e;
            padding: 20px;
            min-height: 600px;
            position: relative;
        }}
        
        .zone {{
            background: rgba(26, 26, 46, 0.5);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 2px solid;
        }}
        
        .zone-header {{
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .zone-content {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        
        .node-card {{
            background: #0d0d0d;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .node-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 212, 255, 0.3);
        }}
        
        .node-name {{
            font-size: 0.9em;
            word-break: break-all;
            margin-bottom: 5px;
        }}
        
        .node-class {{
            font-size: 0.75em;
            color: #888;
        }}
        
        .legend {{
            background: #1a1a2e;
            border-radius: 8px;
            border: 1px solid #2a2a3e;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .legend-title {{
            color: #00d4ff;
            font-weight: bold;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        
        .legend-text {{
            font-size: 0.85em;
        }}
        
        .detail-panel {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a2e;
            border: 2px solid #00d4ff;
            border-radius: 8px;
            padding: 25px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            display: none;
            z-index: 1000;
        }}
        
        .detail-panel.active {{
            display: block;
        }}
        
        .detail-close {{
            float: right;
            cursor: pointer;
            font-size: 1.5em;
            color: #888;
        }}
        
        .detail-close:hover {{
            color: #00d4ff;
        }}
        
        .detail-field {{
            margin-bottom: 15px;
        }}
        
        .detail-field-label {{
            color: #888;
            font-size: 0.85em;
            margin-bottom: 3px;
        }}
        
        .detail-field-value {{
            color: #e0e0e0;
            font-family: 'Consolas', monospace;
            background: #0d0d0d;
            padding: 8px;
            border-radius: 4px;
        }}
        
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: none;
            z-index: 999;
        }}
        
        .overlay.active {{
            display: block;
        }}
        
        .collapsed {{
            display: none;
        }}
        
        .zoom-info {{
            background: #16213e;
            padding: 10px 15px;
            border-radius: 4px;
            color: #00d4ff;
            font-weight: bold;
        }}
        
        .loading-msg {{
            text-align: center;
            padding: 60px 20px;
            color: #888;
            font-size: 1.2em;
        }}
        
        .error-msg {{
            text-align: center;
            padding: 40px 20px;
            color: #ff4444;
            background: #1a0a0a;
            border-radius: 8px;
            border: 1px solid #ff4444;
            font-family: monospace;
        }}
        
        .truncation-notice {{
            text-align: center;
            padding: 8px;
            color: #ffaa00;
            font-size: 0.85em;
            background: #1a1a0a;
            border-radius: 4px;
            margin-top: 8px;
        }}

        /* ── Commit Info Section ──────────────────────────────────────────── */
        .commit-info {{
            background: #0f1a0f;
            border: 1px solid #1a4a1a;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
        }}

        .commit-info-title {{
            color: #00ff88;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1em;
        }}

        .commit-info-row {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .commit-info-field {{
            display: flex;
            flex-direction: column;
        }}

        .commit-info-label {{
            color: #888;
            font-size: 0.8em;
        }}

        .commit-info-value {{
            color: #e0e0e0;
        }}

        /* ── Substrate Domain Panels ──────────────────────────────────────── */
        .domains-section {{
            margin-bottom: 20px;
        }}

        .domains-section-title {{
            color: #00d4ff;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
        }}

        .domain-panels {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 15px;
        }}

        .domain-panel {{
            background: #1a1a2e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #2a2a3e;
        }}

        .domain-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .domain-panel-title {{
            font-weight: bold;
            font-size: 1.05em;
        }}

        .domain-panel-pr-badge {{
            font-size: 0.75em;
            padding: 3px 8px;
            border-radius: 12px;
            border: 1px solid;
            font-family: monospace;
        }}

        .domain-panel-levels {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 12px;
        }}

        .level-tag {{
            font-size: 0.75em;
            padding: 2px 8px;
            border-radius: 3px;
            background: #0d0d2a;
            border: 1px solid #2a2a4a;
            color: #aaaacc;
            font-family: monospace;
        }}

        .domain-invariants {{
            margin-bottom: 12px;
        }}

        .domain-invariants-title {{
            color: #888;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }}

        .invariant-item {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 4px 0;
            border-bottom: 1px solid #1a1a3a;
            font-size: 0.82em;
        }}

        .invariant-item:last-child {{
            border-bottom: none;
        }}

        .invariant-id {{
            color: #00d4ff;
            font-family: monospace;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .invariant-desc {{
            color: #cccccc;
        }}

        /* ── Inelasticity / Structural Nullification ─────────────────────── */
        .inelasticity-block {{
            background: #1a0a0a;
            border: 1px solid #3a1a1a;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }}

        .inelasticity-title {{
            color: #ff4444;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .nullified-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 3px 0;
            font-size: 0.82em;
        }}

        .nullified-label {{
            color: #888;
            text-decoration: line-through;
        }}

        .nullified-badge {{
            font-size: 0.72em;
            padding: 1px 6px;
            background: #2a0a0a;
            border: 1px solid #ff4444;
            border-radius: 10px;
            color: #ff4444;
            font-family: monospace;
        }}

        /* ── Merkle Root Placeholder ──────────────────────────────────────── */
        .merkle-block {{
            background: #0a0a1a;
            border: 1px solid #2a2a4a;
            border-radius: 6px;
            padding: 10px 12px;
            font-family: monospace;
            font-size: 0.8em;
        }}

        .merkle-title {{
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 5px;
            font-size: 0.75em;
        }}

        .merkle-value {{
            color: #00aaff;
            word-break: break-all;
        }}

        .merkle-status {{
            margin-top: 4px;
            font-size: 0.75em;
        }}

        .merkle-status.pending {{
            color: #ffaa00;
        }}

        .merkle-status.verified {{
            color: #00ff88;
        }}

        /* ── LOD / Seed-Driven Info ───────────────────────────────────────── */
        .lod-section {{
            background: #0f0f1a;
            border: 1px solid #2a2a4a;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
        }}

        .lod-section-title {{
            color: #00d4ff;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .lod-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}

        .lod-item {{
            background: #1a1a2e;
            border-radius: 6px;
            padding: 10px;
            border: 1px solid #2a2a3e;
        }}

        .lod-item-label {{
            color: #888;
            font-size: 0.8em;
            margin-bottom: 4px;
        }}

        .lod-item-value {{
            color: #e0e0e0;
            font-family: monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="overlay" id="overlay" aria-hidden="true"></div>
    <div class="detail-panel" id="detailPanel" role="dialog" aria-modal="true" aria-labelledby="detailPanelTitle">
        <span class="detail-close" onclick="closeDetail()" role="button" aria-label="Close detail panel" tabindex="0">&times;</span>
        <div id="detailContent">
            <h2 id="detailPanelTitle" style="color:#00d4ff;margin-bottom:20px;">Node Details</h2>
        </div>
    </div>
    
    <div class="container">
        <header role="banner">
            <h1>⚛️ PERCEIVABLE_INFINITY</h1>
            <p class="subtitle">Covenant-Aware Topology Graph — Sabbath-Complete Schema Manifestation</p>
            <p class="subtitle">Repository: {metadata.get('root_path', 'N/A')} | Scan: {metadata.get('scan_timestamp', 'N/A')}</p>
        </header>

        <!-- Commit Info Section: Static Witness to the latest substrate commit -->
        <section class="commit-info" aria-label="Latest commit information">
            <div class="commit-info-title">📌 Substrate Commit (Latest Applied)</div>
            <div class="commit-info-row">
                <div class="commit-info-field">
                    <span class="commit-info-label">Commit SHA (short)</span>
                    <span class="commit-info-value">{commit_sha_short}</span>
                </div>
                <div class="commit-info-field">
                    <span class="commit-info-label">Subject</span>
                    <span class="commit-info-value">{commit["subject"]}</span>
                </div>
                <div class="commit-info-field">
                    <span class="commit-info-label">Author</span>
                    <span class="commit-info-value">{commit["author"]}</span>
                </div>
                <div class="commit-info-field">
                    <span class="commit-info-label">Date</span>
                    <span class="commit-info-value">{commit["date"]}</span>
                </div>
            </div>
        </section>

        <!-- LOD / Seed-Driven Rendering Info -->
        <section class="lod-section" aria-label="Fractal rendering and seed-driven state">
            <div class="lod-section-title">🌀 Fractal Rendering Engine — LOD State</div>
            <div class="lod-grid">
                <div class="lod-item">
                    <div class="lod-item-label">Rendering Strategy</div>
                    <div class="lod-item-value">Fractal LOD — O(1) cost / node volume</div>
                </div>
                <div class="lod-item">
                    <div class="lod-item-label">Zoom Levels</div>
                    <div class="lod-item-value">L0 (zones) → L1 (classified) → L2 (all)</div>
                </div>
                <div class="lod-item">
                    <div class="lod-item-label">Node Cap (L1 / L2)</div>
                    <div class="lod-item-value">{MAX_NODES_PER_ZONE_LEVEL1} / {MAX_NODES_PER_ZONE_LEVEL2} per zone</div>
                </div>
                <div class="lod-item">
                    <div class="lod-item-label">Data Source</div>
                    <div class="lod-item-value">fetch('{graph_url}') — never embedded</div>
                </div>
                <div class="lod-item">
                    <div class="lod-item-label">Determinism</div>
                    <div class="lod-item-value">Seed-driven — same seed → same tree</div>
                </div>
                <div class="lod-item">
                    <div class="lod-item-label">Scale Target</div>
                    <div class="lod-item-value">53 nodes → 1B nodes (invariant cost)</div>
                </div>
            </div>
        </section>

        <!-- Substrate Domain Panels: Food Cart (#60), Uncharted (#61), Skate 4 (#62) -->
        <section class="domains-section" aria-label="Substrate domain panels">
            <div class="domains-section-title">🧬 Ontological Substrate Domains</div>
            <div class="domain-panels">
                {domain_panels_html}
            </div>
        </section>
        
        <div class="controls" role="toolbar" aria-label="Visualization controls">
            <div class="control-group">
                <label for="zoomLevel">Zoom Level:</label>
                <select id="zoomLevel" onchange="changeZoomLevel()">
                    <option value="0">Level 0: Zones Only</option>
                    <option value="1" selected>Level 1: Classified Nodes</option>
                    <option value="2">Level 2: All Nodes</option>
                </select>
            </div>
            <div class="control-group">
                <label for="zoneFilter">Filter by Zone:</label>
                <select id="zoneFilter" onchange="applyFilters()">
                    <option value="all">All Zones</option>
                    <option value="zone_1_immutable_authority">Zone 1: Immutable Authority</option>
                    <option value="zone_2_detection_enforcement">Zone 2: Detection/Enforcement</option>
                    <option value="zone_3_correspondence_bridge">Zone 3: Correspondence Bridge</option>
                    <option value="zone_4_forgiveness_grace">Zone 4: Forgiveness/Grace</option>
                    <option value="zone_5_analysis_reporting">Zone 5: Analysis/Reporting</option>
                    <option value="zone_6_deployment_orchestration">Zone 6: Deployment/Orchestration</option>
                    <option value="zone_7_documentation">Zone 7: Documentation</option>
                    <option value="zone_8_unclassified">Zone 8: Unclassified</option>
                </select>
            </div>
            <div class="control-group">
                <label for="searchBox">Search:</label>
                <input type="text" id="searchBox" placeholder="Search nodes..." oninput="searchNodes()" aria-label="Search nodes">
            </div>
            <div class="control-group">
                <span class="zoom-info" id="zoomInfo" aria-live="polite">Zoom Level 1: Classified Nodes</span>
            </div>
        </div>
        
        <div class="stats" id="statsBar" aria-label="Repository statistics">
            <div class="stat-card">
                <div class="stat-value" id="statTotal">{stats.get('total_files', 0):,}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statClassified">{stats.get('classified_nodes', 0):,}</div>
                <div class="stat-label">Classified Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statUnclassified">{stats.get('unclassified_nodes', 0):,}</div>
                <div class="stat-label">Unclassified Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statEdges">{stats.get('edges_created', 0):,}</div>
                <div class="stat-label">Edges</div>
            </div>
        </div>
        
        <main class="visualization" id="visualization" role="main" aria-label="Topology visualization" aria-live="polite">
            <div class="loading-msg">⏳ Loading graph data from <code>{graph_url}</code>…</div>
        </main>
        
        <aside class="legend" aria-label="Node class legend">
            <div class="legend-title">Node Classes</div>
            <div class="legend-grid">
                {self._generate_legend(node_colors)}
            </div>
        </aside>
    </div>
    
    <script>
        // ── Constants baked in at render time ──────────────────────────────
        const GRAPH_URL = '{graph_url}';
        const NODE_COLORS = {node_colors_json};
        const MAX_NODES_LEVEL1 = {MAX_NODES_PER_ZONE_LEVEL1};
        const MAX_NODES_LEVEL2 = {MAX_NODES_PER_ZONE_LEVEL2};

        // ── Runtime state ─────────────────────────────────────────────────
        let graphData = null;
        let currentZoomLevel = 1;
        let currentZoneFilter = 'all';
        let currentSearchQuery = '';

        // ── Data loading ──────────────────────────────────────────────────
        /**
         * Fetch the graph JSON at runtime.  The full node list is never baked
         * into the HTML; this keeps the HTML small for 67k+ repos.
         */
        async function loadGraph() {{
            try {{
                const resp = await fetch(GRAPH_URL);
                if (!resp.ok) throw new Error(`HTTP ${{resp.status}}: ${{resp.statusText}}`);
                graphData = await resp.json();
                // Overwrite baked-in stats with live values from the JSON
                const s = graphData.statistics || {{}};
                document.getElementById('statTotal').textContent = (s.total_files || 0).toLocaleString();
                document.getElementById('statClassified').textContent = (s.classified_nodes || 0).toLocaleString();
                document.getElementById('statUnclassified').textContent = (s.unclassified_nodes || 0).toLocaleString();
                document.getElementById('statEdges').textContent = (s.edges_created || 0).toLocaleString();
                renderVisualization();
            }} catch (err) {{
                const viz = document.getElementById('visualization');
                viz.innerHTML = `
                    <div class="error-msg">
                        <strong>⚠ Could not load graph data</strong><br><br>
                        ${{err.message}}<br><br>
                        <small>Expected: <code>${{GRAPH_URL}}</code> in the same directory as this HTML file.<br>
                        If opening via file://, run a local HTTP server:<br>
                        <code>python3 -m http.server 8080</code></small>
                    </div>`;
            }}
        }}

        // ── Zoom / filter controls ────────────────────────────────────────
        function changeZoomLevel() {{
            currentZoomLevel = parseInt(document.getElementById('zoomLevel').value);
            const labels = {{
                0: 'Zoom Level 0: Zones Only',
                1: 'Zoom Level 1: Classified Nodes',
                2: 'Zoom Level 2: All Nodes',
            }};
            document.getElementById('zoomInfo').textContent = labels[currentZoomLevel] || '';
            renderVisualization();
        }}

        function applyFilters() {{
            currentZoneFilter = document.getElementById('zoneFilter').value;
            renderVisualization();
        }}

        function searchNodes() {{
            currentSearchQuery = document.getElementById('searchBox').value.toLowerCase();
            renderVisualization();
        }}

        // ── Core renderer ─────────────────────────────────────────────────
        /**
         * Render the topology visualization into #visualization.
         *
         * Level 0 — zone cards only (no individual nodes).
         * Level 1 — classified nodes per zone (UNCLASSIFIED excluded),
         *           capped at MAX_NODES_LEVEL1 per zone.
         * Level 2 — all nodes per zone, capped at MAX_NODES_LEVEL2 per zone.
         *
         * Never silently drops evidence: truncation is always announced with
         * the true count so the viewer knows more nodes exist.
         */
        function renderVisualization() {{
            if (!graphData) return;
            const viz = document.getElementById('visualization');
            const nodes = graphData.nodes || {{}};

            // ── Group nodes by zone, applying filters ──────────────────
            const zoneMap = {{}};
            for (const [nodeId, node] of Object.entries(nodes)) {{
                const zone = node.zone || 'zone_8_unclassified';
                if (currentZoneFilter !== 'all' && zone !== currentZoneFilter) continue;
                if (currentSearchQuery && !nodeId.toLowerCase().includes(currentSearchQuery)) continue;
                if (currentZoomLevel === 1 && node.node_class === 'UNCLASSIFIED') continue;
                if (!zoneMap[zone]) zoneMap[zone] = [];
                zoneMap[zone].push(node);
            }}

            // ── Render each zone ───────────────────────────────────────
            viz.innerHTML = Object.keys(zoneMap).sort().map(zoneId => {{
                const allNodes = zoneMap[zoneId];
                const borderColor = getZoneBorderColor(zoneId);

                if (currentZoomLevel === 0) {{
                    // Level 0: aggregated zone card only
                    return `<div class="zone" style="border-color:${{borderColor}}">
                        <div class="zone-header">
                            <span>${{humanZone(zoneId)}}</span>
                            <span>${{allNodes.length.toLocaleString()}} nodes</span>
                        </div>
                    </div>`;
                }}

                // Level 1 / 2: nodes visible, with cap
                const cap = currentZoomLevel === 1 ? MAX_NODES_LEVEL1 : MAX_NODES_LEVEL2;
                const visible = allNodes.slice(0, cap);
                const truncated = allNodes.length > cap;

                return `<div class="zone" style="border-color:${{borderColor}}">
                    <div class="zone-header" onclick="toggleZone('${{zoneId}}')">
                        <span>${{humanZone(zoneId)}}</span>
                        <span>${{allNodes.length.toLocaleString()}} nodes</span>
                    </div>
                    <div class="zone-content" id="zone-${{zoneId}}">
                        ${{visible.map(n => renderNode(n)).join('')}}
                        ${{truncated ? `<div class="truncation-notice">⚠ Showing ${{cap.toLocaleString()}} of ${{allNodes.length.toLocaleString()}} nodes — use Search or zoom level 0 for full overview</div>` : ''}}
                    </div>
                </div>`;
            }}).join('');

            if (Object.keys(zoneMap).length === 0) {{
                viz.innerHTML = '<div class="loading-msg">No nodes match current filters.</div>';
            }}
        }}

        function renderNode(node) {{
            const color = NODE_COLORS[node.node_class] || '#666666';
            // Use JSON.stringify to safely embed the ID in an onclick attribute,
            // regardless of special characters (single quotes, backslashes, etc.).
            const encodedId = JSON.stringify(node.file_id || '');
            return `<div class="node-card" style="border-color:${{color}}" onclick="showDetail(${{encodedId}})">
                <div class="node-name">${{node.file_path || node.file_id}}</div>
                <div class="node-class">${{node.node_class}}</div>
            </div>`;
        }}

        // ── Colour helpers ────────────────────────────────────────────────
        function getZoneBorderColor(zoneId) {{
            const colors = {{
                'zone_1_immutable_authority': '#ff4444',
                'zone_2_detection_enforcement': '#ffaa00',
                'zone_3_correspondence_bridge': '#00aaff',
                'zone_4_forgiveness_grace': '#aa00ff',
                'zone_5_analysis_reporting': '#00ff88',
                'zone_6_deployment_orchestration': '#888888',
                'zone_7_documentation': '#ffffff',
                'zone_8_unclassified': '#666666',
            }};
            return colors[zoneId] || '#2a2a3e';
        }}

        function humanZone(zoneId) {{
            return zoneId.replace(/_/g, ' ').toUpperCase();
        }}

        // ── Zone toggle ───────────────────────────────────────────────────
        function toggleZone(zoneId) {{
            const content = document.getElementById('zone-' + zoneId);
            if (content) content.classList.toggle('collapsed');
        }}

        // ── Node detail panel ─────────────────────────────────────────────
        function showDetail(nodeId) {{
            if (!graphData) return;
            const node = graphData.nodes[nodeId];
            if (!node) return;

            const edges = graphData.edges || [];
            const incoming = edges.filter(e => e.target === nodeId);
            const outgoing = edges.filter(e => e.source === nodeId);

            const field = (label, value) =>
                `<div class="detail-field">
                    <div class="detail-field-label">${{label}}</div>
                    <div class="detail-field-value">${{value}}</div>
                </div>`;

            document.getElementById('detailContent').innerHTML =
                `<h2 id="detailPanelTitle" style="color:#00d4ff;margin-bottom:20px;">Node Details</h2>` +
                field('File Path',    node.file_path || node.file_id) +
                field('Node Class',   node.node_class) +
                field('Zone',         node.zone) +
                field('Authority',    node.authority) +
                field('Temporal',     node.temporal) +
                field('Verification', node.verification) +
                field('File Size',    formatBytes(node.file_size || 0)) +
                field('Depth',        node.depth) +
                field('SHA-256',      node.sha256 || 'not computed') +
                field('Incoming Edges', incoming.length) +
                field('Outgoing Edges', outgoing.length);

            document.getElementById('detailPanel').classList.add('active');
            document.getElementById('overlay').classList.add('active');
        }}

        function closeDetail() {{
            document.getElementById('detailPanel').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
        }}

        function formatBytes(bytes) {{
            if (!bytes) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }}

        document.getElementById('overlay').onclick = closeDetail;

        // ── Bootstrap ─────────────────────────────────────────────────────
        loadGraph();
    </script>
</body>
</html>"""

        return html

    def _generate_legend(self, node_colors: Dict) -> str:
        """Generate legend HTML."""
        legend_items = []
        for node_class, color in node_colors.items():
            legend_items.append(
                f'<div class="legend-item">'
                f'<div class="legend-color" style="background:{color}"></div>'
                f'<div class="legend-text">{node_class}</div>'
                f'</div>'
            )
        return '\n'.join(legend_items)

    def _generate_domain_panels(self, seeds: Dict[str, Dict]) -> str:
        """Generate HTML panels for substrate domains from PRs #60, #61, #62.

        Each panel shows:
        - Domain title and PR badge
        - Expansion levels (fractal hierarchy "Kinds")
        - Active invariants list
        - Inelasticity / structural nullification block (Skate 4 only)
        - Merkle root verification placeholder

        Backend extensions: When the generator pipeline provides computed Merkle
        roots in out/<domain>_manifest.jsonl, replace the placeholder value below
        with a runtime-verified hash. Use VERIFICATION_PIPELINE.yaml for the
        canonical verification steps.
        """
        domain_meta = {
            "food_cart": {
                "title": "Food Cart Universe",
                "pr": "#60",
                "color": "#ffaa00",
                "icon": "🍽️",
                "kind": "Physical",
                "merkle_placeholder": "Pending — run generators/food_cart_fractal_dataset.py",
                "node_class": "FOOD_DISH_UNIVERSE",
            },
            "uncharted": {
                "title": "Uncharted Multiplayer Universe",
                "pr": "#61",
                "color": "#00aaff",
                "icon": "🗺️",
                "kind": "Digital",
                "merkle_placeholder": "Pending — run generators/uncharted_multiplayer_fractal_dataset.py",
                "node_class": "MULTIPLAYER_GAME_UNIVERSE",
            },
            "skate4": {
                "title": "Skate 4 Multiplayer Universe",
                "pr": "#62",
                "color": "#aa00ff",
                "icon": "🛹",
                "kind": "Graphical",
                "merkle_placeholder": "Pending — run generators/skate4_multiplayer_fractal_dataset.py",
                "node_class": "MULTIPLAYER_SKATE4_UNIVERSE",
            },
        }

        panels = []
        for domain, meta in domain_meta.items():
            seed_data = seeds.get(domain, {})
            universe = seed_data.get("universe", {})
            levels: List[str] = universe.get("expansion", {}).get("levels", [])
            invariants: Dict = seed_data.get("invariants", {})
            color = meta["color"]
            pr = meta["pr"]
            title = meta["title"]
            icon = meta["icon"]
            kind = meta["kind"]
            merkle_ph = meta["merkle_placeholder"]

            # Expansion level tags — escape YAML values before embedding
            level_tags = "".join(
                f'<span class="level-tag">{_esc(str(lvl))}</span>' for lvl in levels
            )

            # Invariants — show all, sorted; HTML-escape all YAML-sourced strings
            inv_html = ""
            if invariants:
                items = []
                for inv_id, inv_val in sorted(invariants.items()):
                    desc = inv_val.get("description", "") if isinstance(inv_val, dict) else str(inv_val)
                    items.append(
                        f'<div class="invariant-item">'
                        f'<span class="invariant-id">{_esc(str(inv_id))}</span>'
                        f'<span class="invariant-desc">{_esc(str(desc))}</span>'
                        f'</div>'
                    )
                inv_html = (
                    '<div class="domain-invariants">'
                    '<div class="domain-invariants-title">Active Invariants</div>'
                    + "".join(items)
                    + "</div>"
                )

            # Inelasticity block — Skate 4 microtransaction structural nullification
            inelasticity_html = ""
            if domain == "skate4":
                corp = universe.get("corporate_contingencies", {})
                null_items = "".join(
                    f'<div class="nullified-item">'
                    f'<span class="nullified-label">{_esc(str(k).replace("_", " "))}</span>'
                    f'<span class="nullified-badge">VOID — {_esc(str(v))}</span>'
                    f'</div>'
                    for k, v in corp.items()
                )
                # Also show graphics pipeline from seed
                gfx = seed_data.get("graphics", {})
                gfx_pipeline = _esc(str(gfx.get("pipeline", "N/A")))
                inelasticity_html = (
                    '<div class="inelasticity-block" aria-label="Structural nullification of microtransactions">'
                    '<div class="inelasticity-title">⛔ Structural Nullification — Moral Physics</div>'
                    + null_items
                    + f'<div class="nullified-item" style="margin-top:6px;border-top:1px solid #3a1a1a;padding-top:6px;">'
                    f'<span style="color:#888;font-size:0.82em;">Graphics Pipeline:</span>'
                    f'<span style="color:#cc88ff;font-family:monospace;font-size:0.82em;margin-left:6px;">{gfx_pipeline}</span>'
                    f'</div>'
                    "</div>"
                )

            # Merkle root placeholder
            # TODO(backend): Replace placeholder with verified hash from manifest
            # once generators produce out/<domain>_manifest.jsonl.
            # Verification: canonical/hash_manifest.json → merkle_root field.
            merkle_html = (
                '<div class="merkle-block" aria-label="Merkle root verification">'
                '<div class="merkle-title">Merkle Root (Substrate Verification)</div>'
                f'<div class="merkle-value">{_esc(merkle_ph)}</div>'
                '<div class="merkle-status pending">⏳ Awaiting backend hash computation</div>'
                "</div>"
            )

            panels.append(
                f'<article class="domain-panel" aria-label="{_esc(title)} domain panel">'
                f'<div class="domain-panel-header">'
                f'<div class="domain-panel-title" style="color:{color}">{icon} {title}</div>'
                f'<span class="domain-panel-pr-badge" style="color:{color};border-color:{color}">PR {pr} · {kind}</span>'
                f'</div>'
                f'<div class="domain-panel-levels" aria-label="Expansion levels">{level_tags}</div>'
                + inv_html
                + inelasticity_html
                + merkle_html
                + f'</article>'
            )

        return "\n".join(panels)


def main():
    """Main entry point for renderer."""
    import sys

    schema_path = sys.argv[1] if len(sys.argv) > 1 else "PERCEIVABLE_INFINITY_SCHEMA.yaml"
    graph_path = sys.argv[2] if len(sys.argv) > 2 else "topology_graph.json"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "PERCEIVABLE_INFINITY.html"

    renderer = Renderer(schema_path, graph_path)
    renderer.render(output_path)


if __name__ == "__main__":
    main()
