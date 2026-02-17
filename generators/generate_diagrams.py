#!/usr/bin/env python3
"""
Generate SVG diagrams for topological map documentation.

Creates visual representations of:
- DAG topology
- Fractal expansion
- Merkle chain

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

def generate_topological_map_svg():
    """Generate high-level DAG visualization."""
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <title>Topological Map: 1B LOC DAG Structure</title>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="400" y="30" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
    Topological Map: 1B LOC DAG Structure (Yeshua Standard)
  </text>
  
  <!-- Root Seed -->
  <circle cx="400" cy="80" r="25" fill="#28a745" stroke="#155724" stroke-width="2"/>
  <text x="400" y="85" font-family="monospace" font-size="12" fill="white" text-anchor="middle">SEED</text>
  
  <!-- DAG Layer -->
  <line x1="400" y1="105" x2="400" y2="140" stroke="#6c757d" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <rect x="300" y="140" width="200" height="60" rx="5" fill="#007bff" stroke="#0056b3" stroke-width="2"/>
  <text x="400" y="165" font-family="monospace" font-size="14" fill="white" text-anchor="middle" font-weight="bold">
    DAG GENERATION
  </text>
  <text x="400" y="185" font-family="Arial, sans-serif" font-size="11" fill="white" text-anchor="middle">
    100 batches × 10 modules × 100 files
  </text>
  
  <!-- Fractal Expansion Layer -->
  <line x1="400" y1="200" x2="400" y2="240" stroke="#6c757d" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <rect x="300" y="240" width="200" height="60" rx="5" fill="#fd7e14" stroke="#e66000" stroke-width="2"/>
  <text x="400" y="265" font-family="monospace" font-size="14" fill="white" text-anchor="middle" font-weight="bold">
    FRACTAL EXPANSION
  </text>
  <text x="400" y="285" font-family="Arial, sans-serif" font-size="11" fill="white" text-anchor="middle">
    100 functions × 10 lines each
  </text>
  
  <!-- Manifest Layer -->
  <line x1="400" y1="300" x2="400" y2="340" stroke="#6c757d" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <rect x="300" y="340" width="200" height="60" rx="5" fill="#6f42c1" stroke="#5a32a3" stroke-width="2"/>
  <text x="400" y="365" font-family="monospace" font-size="14" fill="white" text-anchor="middle" font-weight="bold">
    MANIFEST (Hashes)
  </text>
  <text x="400" y="385" font-family="Arial, sans-serif" font-size="11" fill="white" text-anchor="middle">
    Hash inventory, no content
  </text>
  
  <!-- Merkle Tree Layer -->
  <line x1="400" y1="400" x2="400" y2="440" stroke="#6c757d" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <rect x="300" y="440" width="200" height="60" rx="5" fill="#dc3545" stroke="#bd2130" stroke-width="2"/>
  <text x="400" y="465" font-family="monospace" font-size="14" fill="white" text-anchor="middle" font-weight="bold">
    MERKLE TREE
  </text>
  <text x="400" y="485" font-family="Arial, sans-serif" font-size="11" fill="white" text-anchor="middle">
    Single root hash (64 bytes)
  </text>
  
  <!-- 1B LOC Proof -->
  <line x1="400" y1="500" x2="400" y2="535" stroke="#6c757d" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <ellipse cx="400" cy="560" rx="100" ry="25" fill="#ffc107" stroke="#e0a800" stroke-width="2"/>
  <text x="400" y="565" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle">
    1B LOC PROVEN
  </text>
  
  <!-- Side annotations -->
  <text x="620" y="90" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    ~1 KB
  </text>
  <text x="620" y="170" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    ~5 MB (structure)
  </text>
  <text x="620" y="270" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    ~100 KB (generators)
  </text>
  <text x="620" y="370" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    ~100 MB (hashes)
  </text>
  <text x="620" y="470" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    64 bytes (root)
  </text>
  
  <text x="50" y="170" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    Deterministic
  </text>
  <text x="50" y="270" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    Self-similar
  </text>
  <text x="50" y="370" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    Lazy eval
  </text>
  <text x="50" y="470" font-family="Arial, sans-serif" font-size="10" fill="#6c757d">
    Cryptographic
  </text>
  
  <!-- Arrow marker -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#6c757d"/>
    </marker>
  </defs>
</svg>'''
    
    with open('docs/topological_map/topological_map.svg', 'w') as f:
        f.write(svg)
    
    print("Generated: docs/topological_map/topological_map.svg")


def generate_fractal_expansion_svg():
    """Generate fractal expansion illustration."""
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
  <title>Fractal Expansion Pattern</title>
  
  <!-- Background -->
  <rect width="800" height="500" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="400" y="30" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
    Fractal Expansion: Self-Similar Pattern at All Scales
  </text>
  
  <!-- Batch Level -->
  <rect x="50" y="60" width="160" height="80" rx="5" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
  <text x="130" y="85" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    BATCH
  </text>
  <text x="130" y="105" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">
    Contains 10 modules
  </text>
  <text x="130" y="125" font-family="Arial, sans-serif" font-size="9" fill="#666" text-anchor="middle">
    10M lines each
  </text>
  
  <!-- Module Level -->
  <rect x="250" y="60" width="160" height="80" rx="5" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2"/>
  <text x="330" y="85" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    MODULE
  </text>
  <text x="330" y="105" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">
    Contains 100 files
  </text>
  <text x="330" y="125" font-family="Arial, sans-serif" font-size="9" fill="#666" text-anchor="middle">
    1M lines each
  </text>
  
  <!-- File Level -->
  <rect x="450" y="60" width="160" height="80" rx="5" fill="#fff3e0" stroke="#e65100" stroke-width="2"/>
  <text x="530" y="85" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    FILE
  </text>
  <text x="530" y="105" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">
    Contains 100 functions
  </text>
  <text x="530" y="125" font-family="Arial, sans-serif" font-size="9" fill="#666" text-anchor="middle">
    10K lines each
  </text>
  
  <!-- Function Level -->
  <rect x="150" y="180" width="160" height="80" rx="5" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
  <text x="230" y="205" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    FUNCTION
  </text>
  <text x="230" y="225" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">
    Contains 10 lines
  </text>
  <text x="230" y="245" font-family="Arial, sans-serif" font-size="9" fill="#666" text-anchor="middle">
    100 lines each
  </text>
  
  <!-- Line Level (Leaf) -->
  <rect x="350" y="180" width="160" height="80" rx="5" fill="#ffebee" stroke="#c62828" stroke-width="2"/>
  <text x="430" y="205" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    LINE (LEAF)
  </text>
  <text x="430" y="225" font-family="Arial, sans-serif" font-size="10" text-anchor="middle">
    Actual code
  </text>
  <text x="430" y="245" font-family="Arial, sans-serif" font-size="9" fill="#666" text-anchor="middle">
    Terminal node
  </text>
  
  <!-- Self-similarity annotation -->
  <text x="400" y="310" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#dc3545">
    Same expansion pattern at every level ↻
  </text>
  
  <!-- Formula -->
  <text x="400" y="350" font-family="monospace" font-size="12" text-anchor="middle">
    100 batches × 10 modules × 100 files × 100 functions × 10 lines
  </text>
  <text x="400" y="370" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#28a745">
    = 1,000,000,000 lines
  </text>
  
  <!-- Properties -->
  <rect x="100" y="400" width="600" height="80" rx="5" fill="#fff" stroke="#dee2e6" stroke-width="1"/>
  <text x="400" y="420" font-family="Arial, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
    Fractal Properties:
  </text>
  <text x="150" y="440" font-family="Arial, sans-serif" font-size="10">
    • Deterministic: Same seed → same output
  </text>
  <text x="150" y="460" font-family="Arial, sans-serif" font-size="10">
    • Self-similar: Pattern repeats at all scales
  </text>
  <text x="450" y="440" font-family="Arial, sans-serif" font-size="10">
    • Recursive: Each level generates children
  </text>
  <text x="450" y="460" font-family="Arial, sans-serif" font-size="10">
    • Scalable: Change one parameter → infinite scale
  </text>
</svg>'''
    
    with open('docs/topological_map/fractal_expansion.svg', 'w') as f:
        f.write(svg)
    
    print("Generated: docs/topological_map/fractal_expansion.svg")


def generate_merkle_chain_svg():
    """Generate Merkle chain diagram."""
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <title>Merkle Chain: Cryptographic Witness</title>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="400" y="30" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
    Merkle Chain: Cryptographic Witness of Ancestry
  </text>
  
  <!-- Merkle Root -->
  <circle cx="400" cy="80" r="30" fill="#dc3545" stroke="#bd2130" stroke-width="2"/>
  <text x="400" y="85" font-family="monospace" font-size="10" fill="white" text-anchor="middle" font-weight="bold">
    ROOT
  </text>
  <text x="400" y="125" font-family="monospace" font-size="9" text-anchor="middle" fill="#666">
    7f83b1657ff1...
  </text>
  
  <!-- Level 1 -->
  <line x1="400" y1="110" x2="300" y2="170" stroke="#6c757d" stroke-width="1.5"/>
  <line x1="400" y1="110" x2="500" y2="170" stroke="#6c757d" stroke-width="1.5"/>
  
  <circle cx="300" cy="180" r="25" fill="#fd7e14" stroke="#e66000" stroke-width="2"/>
  <text x="300" y="185" font-family="monospace" font-size="9" fill="white" text-anchor="middle">H1</text>
  
  <circle cx="500" cy="180" r="25" fill="#fd7e14" stroke="#e66000" stroke-width="2"/>
  <text x="500" y="185" font-family="monospace" font-size="9" fill="white" text-anchor="middle">H2</text>
  
  <!-- Level 2 -->
  <line x1="300" y1="205" x2="250" y2="265" stroke="#6c757d" stroke-width="1.5"/>
  <line x1="300" y1="205" x2="350" y2="265" stroke="#6c757d" stroke-width="1.5"/>
  <line x1="500" y1="205" x2="450" y2="265" stroke="#6c757d" stroke-width="1.5"/>
  <line x1="500" y1="205" x2="550" y2="265" stroke="#6c757d" stroke-width="1.5"/>
  
  <circle cx="250" cy="275" r="20" fill="#ffc107" stroke="#e0a800" stroke-width="2"/>
  <text x="250" y="280" font-family="monospace" font-size="8" text-anchor="middle">H3</text>
  
  <circle cx="350" cy="275" r="20" fill="#ffc107" stroke="#e0a800" stroke-width="2"/>
  <text x="350" y="280" font-family="monospace" font-size="8" text-anchor="middle">H4</text>
  
  <circle cx="450" cy="275" r="20" fill="#ffc107" stroke="#e0a800" stroke-width="2"/>
  <text x="450" y="280" font-family="monospace" font-size="8" text-anchor="middle">H5</text>
  
  <circle cx="550" cy="275" r="20" fill="#ffc107" stroke="#e0a800" stroke-width="2"/>
  <text x="550" y="280" font-family="monospace" font-size="8" text-anchor="middle">H6</text>
  
  <!-- Leaves -->
  <line x1="250" y1="295" x2="225" y2="350" stroke="#6c757d" stroke-width="1"/>
  <line x1="250" y1="295" x2="275" y2="350" stroke="#6c757d" stroke-width="1"/>
  <line x1="350" y1="295" x2="325" y2="350" stroke="#6c757d" stroke-width="1"/>
  <line x1="350" y1="295" x2="375" y2="350" stroke="#6c757d" stroke-width="1"/>
  
  <rect x="210" y="355" width="30" height="30" rx="3" fill="#28a745" stroke="#155724" stroke-width="1"/>
  <text x="225" y="373" font-family="monospace" font-size="7" fill="white" text-anchor="middle">L1</text>
  
  <rect x="260" y="355" width="30" height="30" rx="3" fill="#28a745" stroke="#155724" stroke-width="1"/>
  <text x="275" y="373" font-family="monospace" font-size="7" fill="white" text-anchor="middle">L2</text>
  
  <rect x="310" y="355" width="30" height="30" rx="3" fill="#28a745" stroke="#155724" stroke-width="1"/>
  <text x="325" y="373" font-family="monospace" font-size="7" fill="white" text-anchor="middle">L3</text>
  
  <rect x="360" y="355" width="30" height="30" rx="3" fill="#28a745" stroke="#155724" stroke-width="1"/>
  <text x="375" y="373" font-family="monospace" font-size="7" fill="white" text-anchor="middle">L4</text>
  
  <text x="400" y="370" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#666">
    ... (1 billion leaf nodes) ...
  </text>
  
  <!-- Inclusion proof example -->
  <rect x="50" y="420" width="700" height="150" rx="5" fill="#fff" stroke="#dee2e6" stroke-width="1"/>
  <text x="400" y="440" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
    Inclusion Proof Example (for Line 542,617,891):
  </text>
  
  <text x="70" y="465" font-family="monospace" font-size="10">
    1. Leaf hash: H(0x00 || "result.append(...)")
  </text>
  <text x="70" y="485" font-family="monospace" font-size="10">
    2. Sibling hash: H_sibling
  </text>
  <text x="70" y="505" font-family="monospace" font-size="10">
    3. Parent hash: H(0x01 || H_leaf || H_sibling)
  </text>
  <text x="70" y="525" font-family="monospace" font-size="10">
    4. Repeat up to root... → Verify ROOT matches stored root
  </text>
  
  <text x="70" y="555" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#28a745">
    ✓ If ROOT matches → Line proven to exist in 1B LOC tree
  </text>
</svg>'''
    
    with open('docs/topological_map/merkle_chain.svg', 'w') as f:
        f.write(svg)
    
    print("Generated: docs/topological_map/merkle_chain.svg")


if __name__ == "__main__":
    print("Generating SVG diagrams...")
    generate_topological_map_svg()
    generate_fractal_expansion_svg()
    generate_merkle_chain_svg()
    print("\n✓ All diagrams generated")
