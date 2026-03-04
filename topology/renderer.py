#!/usr/bin/env python3
"""
Renderer for PERCEIVABLE_INFINITY Schema
========================================

Generates interactive HTML visualization of covenant-aware topology graph.

Authority: PERCEIVABLE_INFINITY_SCHEMA.yaml
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, List

import yaml


class Renderer:
    """
    Renders topology graph as interactive HTML.
    """
    
    def __init__(self, schema_path: str, graph_path: str):
        """
        Initialize renderer.
        
        Args:
            schema_path: Path to PERCEIVABLE_INFINITY_SCHEMA.yaml
            graph_path: Path to topology_graph.json
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
        """Load graph."""
        with open(self.graph_path, "r") as f:
            return json.load(f)
    
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
        """Generate complete HTML document."""
        nodes = self.graph.get("nodes", {})
        edges = self.graph.get("edges", [])
        stats = self.graph.get("statistics", {})
        metadata = self.graph.get("metadata", {})
        
        # Get rendering config from schema
        node_colors = self.schema.get("rendering_layers", {}).get("node_layer", {}).get("visual_mapping", {}).get("node_class_to_color", {})
        edge_styles = self.schema.get("rendering_layers", {}).get("edge_layer", {}).get("visual_mapping", {}).get("edge_class_to_line_style", {})
        
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
    </style>
</head>
<body>
    <div class="overlay" id="overlay"></div>
    <div class="detail-panel" id="detailPanel">
        <span class="detail-close" onclick="closeDetail()">&times;</span>
        <div id="detailContent"></div>
    </div>
    
    <div class="container">
        <header>
            <h1>⚛️ PERCEIVABLE_INFINITY</h1>
            <p class="subtitle">Covenant-Aware Topology Graph Visualization</p>
            <p class="subtitle">Repository: {metadata.get('root_path', 'N/A')} | Scan: {metadata.get('scan_timestamp', 'N/A')}</p>
        </header>
        
        <div class="controls">
            <div class="control-group">
                <label>Zoom Level:</label>
                <select id="zoomLevel" onchange="changeZoomLevel()">
                    <option value="0">Level 0: Zones Only</option>
                    <option value="1" selected>Level 1: Classified Nodes</option>
                    <option value="2">Level 2: All Nodes</option>
                </select>
            </div>
            <div class="control-group">
                <label>Filter by Zone:</label>
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
                <label>Search:</label>
                <input type="text" id="searchBox" placeholder="Search nodes..." oninput="searchNodes()">
            </div>
            <div class="control-group">
                <span class="zoom-info" id="zoomInfo">Zoom Level 1: Classified Nodes</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_files', 0):,}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('classified_nodes', 0):,}</div>
                <div class="stat-label">Classified Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('unclassified_nodes', 0):,}</div>
                <div class="stat-label">Unclassified Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('edges_created', 0):,}</div>
                <div class="stat-label">Edges</div>
            </div>
        </div>
        
        <div class="visualization" id="visualization">
            {self._generate_zones(nodes, node_colors)}
        </div>
        
        <div class="legend">
            <div class="legend-title">Node Classes</div>
            <div class="legend-grid">
                {self._generate_legend(node_colors)}
            </div>
        </div>
    </div>
    
    <script>
        // Graph data
        const graphData = {json.dumps(self.graph, indent=2)};
        
        let currentZoomLevel = 1;
        let currentZoneFilter = 'all';
        let currentSearchQuery = '';
        
        function changeZoomLevel() {{
            currentZoomLevel = parseInt(document.getElementById('zoomLevel').value);
            
            const zoomInfo = document.getElementById('zoomInfo');
            switch(currentZoomLevel) {{
                case 0:
                    zoomInfo.textContent = 'Zoom Level 0: Zones Only';
                    break;
                case 1:
                    zoomInfo.textContent = 'Zoom Level 1: Classified Nodes';
                    break;
                case 2:
                    zoomInfo.textContent = 'Zoom Level 2: All Nodes';
                    break;
            }}
            
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
        
        function renderVisualization() {{
            const viz = document.getElementById('visualization');
            const nodes = graphData.nodes || {{}};
            
            // Group nodes by zone
            const zones = {{}};
            for (const [nodeId, node] of Object.entries(nodes)) {{
                const zone = node.zone || 'zone_8_unclassified';
                if (!zones[zone]) zones[zone] = [];
                
                // Apply filters
                if (currentZoneFilter !== 'all' && zone !== currentZoneFilter) continue;
                if (currentSearchQuery && !nodeId.toLowerCase().includes(currentSearchQuery)) continue;
                if (currentZoomLevel === 1 && node.node_class === 'UNCLASSIFIED') continue;
                
                zones[zone].push(node);
            }}
            
            // Render zones
            viz.innerHTML = Object.keys(zones).sort().map(zoneId => {{
                const zoneNodes = zones[zoneId];
                if (zoneNodes.length === 0) return '';
                
                const borderColor = getZoneBorderColor(zoneId);
                
                if (currentZoomLevel === 0) {{
                    // Zones only
                    return `
                        <div class="zone" style="border-color: ${{borderColor}}">
                            <div class="zone-header">
                                <span>${{zoneId.replace(/_/g, ' ').toUpperCase()}}</span>
                                <span>${{zoneNodes.length}} nodes</span>
                            </div>
                        </div>
                    `;
                }} else {{
                    // Zones with nodes
                    return `
                        <div class="zone" style="border-color: ${{borderColor}}">
                            <div class="zone-header" onclick="toggleZone('${{zoneId}}')">
                                <span>${{zoneId.replace(/_/g, ' ').toUpperCase()}}</span>
                                <span>${{zoneNodes.length}} nodes</span>
                            </div>
                            <div class="zone-content" id="zone-${{zoneId}}">
                                ${{zoneNodes.map(node => renderNode(node)).join('')}}
                            </div>
                        </div>
                    `;
                }}
            }}).join('');
        }}
        
        function renderNode(node) {{
            const color = getNodeColor(node.node_class);
            return `
                <div class="node-card" style="border-color: ${{color}}" onclick="showDetail('${{node.file_id}}')">
                    <div class="node-name">${{node.file_path}}</div>
                    <div class="node-class">${{node.node_class}}</div>
                </div>
            `;
        }}
        
        function getNodeColor(nodeClass) {{
            const colors = {json.dumps(node_colors)};
            return colors[nodeClass] || '#666666';
        }}
        
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
        
        function toggleZone(zoneId) {{
            const content = document.getElementById('zone-' + zoneId);
            if (content) {{
                content.classList.toggle('collapsed');
            }}
        }}
        
        function showDetail(nodeId) {{
            const node = graphData.nodes[nodeId];
            if (!node) return;
            
            // Get edges
            const incomingEdges = graphData.edges.filter(e => e.target === nodeId);
            const outgoingEdges = graphData.edges.filter(e => e.source === nodeId);
            
            const html = `
                <h2 style="color: #00d4ff; margin-bottom: 20px;">Node Details</h2>
                <div class="detail-field">
                    <div class="detail-field-label">File Path</div>
                    <div class="detail-field-value">${{node.file_path}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Node Class</div>
                    <div class="detail-field-value">${{node.node_class}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Authority</div>
                    <div class="detail-field-value">${{node.authority}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Temporal</div>
                    <div class="detail-field-value">${{node.temporal}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Zone</div>
                    <div class="detail-field-value">${{node.zone}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">File Size</div>
                    <div class="detail-field-value">${{formatBytes(node.file_size)}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Verification</div>
                    <div class="detail-field-value">${{node.verification}}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Incoming Edges</div>
                    <div class="detail-field-value">${{incomingEdges.length}} edges</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Outgoing Edges</div>
                    <div class="detail-field-value">${{outgoingEdges.length}} edges</div>
                </div>
            `;
            
            document.getElementById('detailContent').innerHTML = html;
            document.getElementById('detailPanel').classList.add('active');
            document.getElementById('overlay').classList.add('active');
        }}
        
        function closeDetail() {{
            document.getElementById('detailPanel').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
        }}
        
        function formatBytes(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }}
        
        // Close detail on overlay click
        document.getElementById('overlay').onclick = closeDetail;
        
        // Initialize
        renderVisualization();
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_zones(self, nodes: Dict, node_colors: Dict) -> str:
        """Generate zone HTML structure."""
        # Group nodes by zone
        zones = {}
        for node_id, node in nodes.items():
            zone = node.get("zone", "zone_8_unclassified")
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(node)
        
        # Generate HTML for each zone
        zone_html = []
        for zone_id in sorted(zones.keys()):
            zone_nodes = zones[zone_id]
            zone_html.append(f'<div class="zone-placeholder" data-zone="{zone_id}">{len(zone_nodes)} nodes</div>')
        
        return '\n'.join(zone_html)
    
    def _generate_legend(self, node_colors: Dict) -> str:
        """Generate legend HTML."""
        legend_items = []
        for node_class, color in node_colors.items():
            legend_items.append(f'''
                <div class="legend-item">
                    <div class="legend-color" style="background: {color}"></div>
                    <div class="legend-text">{node_class}</div>
                </div>
            ''')
        
        return '\n'.join(legend_items)


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
