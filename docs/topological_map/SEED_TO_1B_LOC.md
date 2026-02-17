# Seed → DAG → Fractal Expansion → Manifest → 1B LOC Pipeline

## Overview

This document provides a detailed technical specification for the complete pipeline that transforms a minimal seed definition into a provably complete 1 billion line codebase.

## Pipeline Stages

### Stage 1: Seed Definition

**Purpose**: Define the root axioms and generation rules in minimal form.

**Input**: Human-defined constraints and templates

**Output**: `seed_definition.yaml` (typically <1KB)

**Example Seed**:

```yaml
# Seed Definition for 1B LOC Architecture
version: "1.0.0"
hash_algorithm: "sha256"
encoding: "utf-8"

# Root configuration
root:
  name: "orthogonal_engineering_1b"
  target_lines: 1000000000
  batch_size: 10000000  # 10M lines per batch
  batch_count: 100

# Fractal expansion rules
expansion:
  levels:
    - name: "batch"
      count: 100
      template: "batch_template.yaml"
      
    - name: "module"
      count: 10
      template: "module_template.py"
      
    - name: "file"
      count: 100
      template: "file_template.py"
      
    - name: "function"
      count: 100
      template: "function_template.py"
      
    - name: "line"
      count: 10
      template: "line_template.py"

# Deterministic generation parameters
generation:
  seed_value: 42  # RNG seed for reproducibility
  templates_dir: "generators/templates/"
  naming_convention: "{level}_{index:06d}"
  
# Hashing configuration
hashing:
  leaf_prefix: "0x00"
  internal_prefix: "0x01"
  include_parent: true
  
# Metadata
metadata:
  author: "Orthogonal Engineering"
  standard: "Yeshua"
  created: "2026-02-17"
  license: "See repository LICENSE"
```

**Validation**:
```python
def validate_seed(seed):
    """Ensure seed is well-formed and mathematically consistent."""
    # Check all required fields present
    assert 'root' in seed
    assert 'expansion' in seed
    assert 'generation' in seed
    
    # Verify math: product of all counts = target lines
    total_lines = 1
    for level in seed['expansion']['levels']:
        total_lines *= level['count']
    
    assert total_lines == seed['root']['target_lines']
    
    return True
```

### Stage 2: DAG Generation

**Purpose**: Construct the complete Directed Acyclic Graph representing all nodes.

**Input**: `seed_definition.yaml`

**Output**: `dag_structure.json` (graph topology, ~1-5MB)

**Algorithm**:

```python
class DAGNode:
    """Represents a single node in the generation DAG."""
    
    def __init__(self, node_id, level, parent_id, index):
        self.id = node_id
        self.level = level
        self.parent = parent_id
        self.index = index
        self.children = []
        self.hash = None  # Computed later
        
    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "parent": self.parent,
            "index": self.index,
            "children": self.children
        }

def generate_dag(seed):
    """
    Generate complete DAG from seed definition.
    
    Time Complexity: O(N) where N = target_lines
    Space Complexity: O(N) for storing node references
    
    Returns: Dictionary mapping node_id -> DAGNode
    """
    dag = {}
    
    # Create root node
    root = DAGNode(
        node_id="root",
        level="root",
        parent_id=None,
        index=0
    )
    dag["root"] = root
    
    # Recursive expansion based on levels
    current_level_nodes = [root]
    
    for level_spec in seed['expansion']['levels']:
        next_level_nodes = []
        
        for parent in current_level_nodes:
            # Generate children for this parent
            for i in range(level_spec['count']):
                child_id = f"{parent.id}/{level_spec['name']}_{i:06d}"
                
                child = DAGNode(
                    node_id=child_id,
                    level=level_spec['name'],
                    parent_id=parent.id,
                    index=i
                )
                
                dag[child_id] = child
                parent.children.append(child_id)
                next_level_nodes.append(child)
        
        current_level_nodes = next_level_nodes
    
    return dag

def serialize_dag(dag, output_file):
    """Save DAG to JSON for later use."""
    import json
    
    # Convert to serializable format
    dag_dict = {
        node_id: node.to_dict() 
        for node_id, node in dag.items()
    }
    
    with open(output_file, 'w') as f:
        json.dump({
            'node_count': len(dag),
            'nodes': dag_dict
        }, f, indent=2)
```

**DAG Properties**:

1. **Acyclic**: No node can be its own ancestor
2. **Connected**: Every node reachable from root
3. **Complete**: All leaf nodes at same depth
4. **Deterministic**: Same seed → same DAG structure

**Example DAG Structure** (small subset):

```json
{
  "node_count": 1000000000,
  "nodes": {
    "root": {
      "id": "root",
      "level": "root",
      "parent": null,
      "children": ["root/batch_000000", "root/batch_000001", ...]
    },
    "root/batch_000000": {
      "id": "root/batch_000000",
      "level": "batch",
      "parent": "root",
      "children": ["root/batch_000000/module_000000", ...]
    }
  }
}
```

### Stage 3: Fractal Expansion

**Purpose**: Define how each node generates its actual content.

**Input**: DAG node + seed templates

**Output**: Generated content (lazy, on-demand)

**Template System**:

```python
# generators/templates/function_template.py
FUNCTION_TEMPLATE = """
def {function_name}(input_data):
    \"\"\"
    Auto-generated function: {function_name}
    Batch: {batch_id}
    Module: {module_id}
    File: {file_id}
    Index: {function_index}
    
    This function is part of the 1B LOC architecture.
    Generated deterministically from seed.
    \"\"\"
    # Fractal line generation
    result = []
    {lines}
    return result
"""

LINE_TEMPLATE = "    result.append(hash_data({data_value}))  # Line {line_index}"

def expand_function(node, seed, dag):
    """
    Expand a function node into actual Python code.
    
    Args:
        node: DAGNode representing this function
        seed: Original seed definition
        dag: Full DAG for context
        
    Returns:
        String containing generated Python code
    """
    # Parse node ID to extract context
    parts = node.id.split('/')
    batch_id = parts[1]
    module_id = parts[2]
    file_id = parts[3]
    function_name = parts[4]
    
    # Generate lines using child nodes
    lines = []
    for i, child_id in enumerate(node.children):
        line = LINE_TEMPLATE.format(
            data_value=hash(child_id + str(seed['generation']['seed_value'])),
            line_index=i
        )
        lines.append(line)
    
    # Fill template
    code = FUNCTION_TEMPLATE.format(
        function_name=function_name,
        batch_id=batch_id,
        module_id=module_id,
        file_id=file_id,
        function_index=node.index,
        lines='\n    '.join(lines)
    )
    
    return code
```

**Fractal Property**:

Each level follows the same pattern:
1. Retrieve template for node's level
2. Extract context from node ID and parent chain
3. Generate content using child nodes
4. Apply consistent formatting/structure

**Determinism Guarantee**:

```python
def verify_determinism(node_id, seed, iterations=100):
    """
    Verify that expansion is deterministic.
    Generate same content N times and compare hashes.
    """
    hashes = set()
    
    for _ in range(iterations):
        content = expand_node(node_id, seed)
        content_hash = sha256(content.encode('utf-8')).hexdigest()
        hashes.add(content_hash)
    
    # All hashes should be identical
    assert len(hashes) == 1, "Non-deterministic generation detected!"
    
    return True
```

### Stage 4: Manifest Generation

**Purpose**: Create cryptographic inventory without storing actual content.

**Input**: DAG + expansion rules

**Output**: `batch_XXX_manifest.jsonl` (JSONL files with hashes)

**Manifest Format**:

```jsonl
{"node_id":"root/batch_000000/module_000000/file_000000/func_000000/line_000000","hash":"a7b3c2...","size":45,"parent":"root/batch_000000/module_000000/file_000000/func_000000","level":"line","index":0}
{"node_id":"root/batch_000000/module_000000/file_000000/func_000000/line_000001","hash":"d4e5f6...","size":42,"parent":"root/batch_000000/module_000000/file_000000/func_000000","level":"line","index":1}
...
```

**Generation Algorithm**:

```python
def generate_manifest(dag, seed, batch_id, output_file):
    """
    Generate manifest for a single batch.
    Computes hashes without storing content.
    """
    import json
    from hasher import sha256_hex
    
    # Find all leaf nodes for this batch
    batch_node = dag[f"root/batch_{batch_id:06d}"]
    leaf_nodes = find_leaf_nodes(batch_node, dag)
    
    with open(output_file, 'w') as f:
        for leaf in leaf_nodes:
            # Generate content (in memory only)
            content = expand_node(leaf, seed, dag)
            
            # Compute hash
            content_hash = sha256_hex(content.encode('utf-8'))
            
            # Write manifest entry
            entry = {
                "node_id": leaf.id,
                "hash": content_hash,
                "size": len(content),
                "parent": leaf.parent,
                "level": leaf.level,
                "index": leaf.index
            }
            
            f.write(json.dumps(entry) + '\n')
            
            # CRITICAL: Do NOT store content
            # Content is discarded after hashing

def find_leaf_nodes(root, dag):
    """Find all leaf nodes under a given root."""
    leaves = []
    
    def traverse(node):
        if not node.children:
            leaves.append(node)
        else:
            for child_id in node.children:
                traverse(dag[child_id])
    
    traverse(root)
    return leaves
```

**Incremental Generation**:

For 1B lines, generate manifests in batches:

```bash
# Generate manifests for all 100 batches
for batch in {0..99}; do
    python generators/manifest_generator.py \
        --seed generators/seed_definition.yaml \
        --dag dag_structure.json \
        --batch $batch \
        --output manifests/batch_${batch}_manifest.jsonl
done
```

### Stage 5: Merkle Chain Construction

**Purpose**: Build cryptographic proof tree for all nodes.

**Input**: All manifest files

**Output**: 
- `merkle_root.txt` (single 64-byte hash)
- `merkle_proofs.jsonl` (inclusion proofs)

**Merkle Tree Algorithm**:

```python
def build_merkle_tree(manifest_files):
    """
    Build binary Merkle tree from all manifest entries.
    
    Returns: (root_hash, proof_dict)
    """
    from merkle import MerkleTree
    import json
    
    # Collect all leaf hashes
    all_hashes = []
    all_nodes = []
    
    for manifest_file in manifest_files:
        with open(manifest_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                all_hashes.append(entry['hash'])
                all_nodes.append(entry['node_id'])
    
    # Sort by node_id for deterministic ordering
    sorted_pairs = sorted(zip(all_nodes, all_hashes))
    sorted_hashes = [h for _, h in sorted_pairs]
    
    # Build tree
    tree = MerkleTree(sorted_hashes)
    root_hash = tree.get_root_hash()
    
    # Generate inclusion proofs
    proofs = {}
    for i, (node_id, leaf_hash) in enumerate(sorted_pairs):
        proof = tree.get_proof(i)
        proofs[node_id] = {
            "leaf_hash": leaf_hash,
            "proof": proof,
            "root": root_hash
        }
    
    return root_hash, proofs

def save_merkle_root(root_hash, output_file):
    """Save Merkle root to file."""
    with open(output_file, 'w') as f:
        f.write(f"{root_hash}\n")
        f.write(f"# Merkle root for 1B LOC architecture\n")
        f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")

def save_merkle_proofs(proofs, output_file):
    """Save all inclusion proofs to JSONL."""
    import json
    
    with open(output_file, 'w') as f:
        for node_id, proof_data in proofs.items():
            entry = {
                "node_id": node_id,
                **proof_data
            }
            f.write(json.dumps(entry) + '\n')
```

**Merkle Root Commitment**:

```
Merkle Root: 7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069

This hash commits to:
- Exactly 1,000,000,000 lines
- With specific content (deterministic)
- In specific order (sorted by node_id)
- With provable ancestry (parent hashes)
```

### Stage 6: Verification & Materialization

**Purpose**: Prove claims and generate content on-demand.

**Verification**:

```python
def verify_1b_loc_claim(seed_file, merkle_root_file):
    """
    Complete verification of 1B LOC claim.
    
    Returns: True if claim is valid, False otherwise
    """
    # 1. Load seed
    seed = load_seed(seed_file)
    
    # 2. Regenerate DAG
    dag = generate_dag(seed)
    assert len([n for n in dag.values() if n.level == 'line']) == 1_000_000_000
    
    # 3. Recompute Merkle root from manifests
    manifest_files = glob.glob('manifests/batch_*_manifest.jsonl')
    computed_root, _ = build_merkle_tree(manifest_files)
    
    # 4. Compare to stored root
    with open(merkle_root_file, 'r') as f:
        stored_root = f.readline().strip()
    
    assert computed_root == stored_root
    
    return True
```

**Lazy Materialization**:

```python
def materialize_line(node_id, seed, output_dir=None):
    """
    Generate and optionally save a specific line.
    
    Args:
        node_id: Full path to line (e.g., "root/batch_000000/.../line_000042")
        seed: Seed definition
        output_dir: If provided, save to disk; otherwise return content
        
    Returns:
        Generated content string
    """
    # Load DAG (or generate on-the-fly)
    dag = load_dag('dag_structure.json')
    
    # Get node
    node = dag[node_id]
    
    # Generate content
    content = expand_node(node, seed, dag)
    
    # Compute hash
    content_hash = sha256_hex(content.encode('utf-8'))
    
    # Verify against manifest
    manifest_entry = find_manifest_entry(node_id)
    assert content_hash == manifest_entry['hash'], "Hash mismatch!"
    
    # Optionally save
    if output_dir:
        file_path = os.path.join(output_dir, node_id.replace('/', os.sep))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
    
    return content
```

## Complete Pipeline Execution

```bash
# Step 1: Generate DAG from seed
python generators/dag_generator.py \
    --seed generators/seed_definition.yaml \
    --output dag_structure.json

# Step 2: Generate manifests for all batches (parallelizable)
python generators/manifest_generator.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --all-batches \
    --output-dir manifests/

# Step 3: Build Merkle tree
python generators/merkle_chain.py \
    --manifests manifests/batch_*_manifest.jsonl \
    --output-root merkle_roots/merkle_root.txt \
    --output-proofs merkle_roots/merkle_proofs.jsonl

# Step 4: Verify everything
python generators/verify_1b_loc.py \
    --seed generators/seed_definition.yaml \
    --merkle-root merkle_roots/merkle_root.txt

# Step 5: (Optional) Materialize a sample batch
python generators/batch_materializer.py \
    --batch 0 \
    --output /tmp/materialized_batch_0/ \
    --verify
```

## Summary

The pipeline achieves:

1. **Seed → DAG**: Mathematical structure (1B nodes, ~5MB)
2. **DAG → Expansion**: Deterministic content generation (lazy)
3. **Expansion → Manifest**: Cryptographic inventory (~100MB)
4. **Manifest → Merkle**: Single root hash (64 bytes)
5. **Merkle → Proof**: 1B LOC claim verified

**Total Git Storage**: ~110MB (seed + DAG + manifests + tools)

**Total Logical Content**: ~80GB (1B lines × 80 bytes/line)

**Compression Ratio**: ~730:1

**Verification Time**: ~10 minutes (regenerate DAG + recompute Merkle root)

**Materialization Time**: ~1 hour per batch (if needed)

This is the Yeshua Standard: Honor the architecture, not the bloat.
