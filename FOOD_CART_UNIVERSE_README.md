---
tags: [food-cart-universe-readme]
register: documentation
---

# Food Cart Universe

**Canonical Schema Implementation for Orthogonal Engineering**

Version: 1.0.0  
Status: ✅ Complete  
Authority: [Canonical Schema Closure Specification](https://github.com/aidoruao/orthogonal-engineering/issues/XX)

---

## Overview

The Food Cart Universe is a reference implementation of the **Canonical Schema Closure** principles for orthogonal engineering. It demonstrates the three non-negotiable architectural principles:

```
1. Universe seed defines ontology
2. DAG nodes define structure  
3. Views are projections
```

This implementation creates a deterministic, content-addressed fractal dataset that integrates seamlessly with the PERCEIVABLE_INFINITY topology system.

---

## Architecture

### Fractal Expansion

```
Universe Seed
   ↓
Deterministic Fractal Expansion
   ↓
Content-addressed DAG Nodes
   ↓
Projections / Views (dish, phase, step)
   ↓
Topology Graph + Manifest + Artifacts
```

### Hierarchy

```
Menu (Root)
├── Dish 1 (tacos)
│   ├── Phase 1 (prep)
│   │   ├── Step 0
│   │   ├── Step 1
│   │   └── Step 2
│   ├── Phase 2 (cook)
│   │   ├── Step 0
│   │   ├── Step 1
│   │   ├── Step 2
│   │   └── Step 3
│   └── Phase 3 (plate)
│       ├── Step 0
│       └── Step 1
├── Dish 2 (ramen)
│   └── ... (similar structure)
├── Dish 3 (pizza)
│   └── ... (similar structure)
└── Dish 4 (burger)
    └── ... (similar structure)
```

**Total Nodes:** 53 (1 menu + 4 dishes + 12 phases + 36 steps)

---

## Key Components

### 1. Universe Seed (`seed/food_cart_universe.yaml`)

Defines the ontology and expansion rules:
- **Expansion levels:** menu → dish → phase → step
- **Deterministic:** Fixed seed ensures reproducibility
- **Content-addressed:** Node IDs derived from content
- **Invariants:** INV-FU-001 through INV-FU-004

### 2. DAG Generator (`generators/food_cart_fractal_dataset.py`)

Generates the complete node graph:
- **Content-addressed node IDs:** `SHA256(seed || parent_node || expansion_config)`
- **Acyclic structure:** No cycles, verified by tests
- **Reproducible:** Same seed → same DAG every time
- **Output:** `out/food_cart_dag.json` (53 nodes)

### 3. Dish Projections (`data/dishes/*.json`)

Views that reference DAG nodes (not ontology roots):
- **Files:** `tacos.json`, `ramen.json`, `pizza.json`, `burger.json`
- **Structure:** Projection type, node references, phases, steps
- **Invariants:** INV-DISH-001 through INV-DISH-003

### 4. Manifest (`out/food_cart_manifest.jsonl`)

Canonical manifest of all nodes:
- **Format:** JSONL (one JSON object per line)
- **Ordering:** Deterministic (sorted by node_id)
- **Completeness:** Every DAG node has an entry
- **Invariants:** INV-MAN-001 through INV-MAN-003

### 5. Merkle Root (`out/food_cart_merkle_root.txt`)

Cryptographic verification of the entire universe:
- **Algorithm:** Merkle tree from manifest content hashes
- **Root:** `6031713d45dc5e9b443fb5f7d16fbe05f5253e533676246875c903481a91e205`
- **Invariants:** INV-MERKLE-001 through INV-MERKLE-002

### 6. Topology Integration

Integrated into PERCEIVABLE_INFINITY system:
- **Node Class:** `FOOD_DISH_UNIVERSE`
- **Zone:** `zone_5_analysis_reporting`
- **Count:** 4 nodes (one per dish)
- **Authority:** `VALIDATED`
- **Temporal:** `SUBSTRATE`

---

## Usage

### Generate the Universe

```bash
# Step 1: Generate DAG from seed
python3 generators/food_cart_fractal_dataset.py \
  --seed seed/food_cart_universe.yaml \
  --output out/food_cart_dag.json

# Step 2: Generate dish projections
python3 generators/dish_projection_generator.py \
  --dag out/food_cart_dag.json \
  --output data/dishes

# Step 3: Generate manifest
python3 generators/food_cart_manifest_generator.py \
  --dag out/food_cart_dag.json \
  --output out/food_cart_manifest.jsonl

# Step 4: Generate Merkle root
python3 generators/food_cart_merkle_generator.py \
  --manifest out/food_cart_manifest.jsonl \
  --output out/food_cart_merkle_root.txt

# Step 5: Regenerate topology (includes food nodes)
python3 generate_perceivable_infinity.py .
```

### Validate

```bash
# Run all invariant validations
python3 validators/validate_food_cart_universe.py --root .

# Run comprehensive tests
pytest tests/test_food_cart_universe.py -v
```

---

## Invariants

### Universe Seed (INV-FU-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-FU-001 | Universe must regenerate identical DAG from identical seed | ✅ |
| INV-FU-002 | All node IDs derived deterministically | ✅ |
| INV-FU-003 | Node hashes must be reproducible across runs | ✅ |
| INV-FU-004 | Universe must produce a canonical manifest | ✅ |

### DAG Nodes (INV-NODE-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-NODE-001 | node_id MUST equal SHA256(seed ‖ parent_node ‖ expansion_config) | ✅ |
| INV-NODE-002 | content_hash MUST equal canonical serialized node content | ✅ |
| INV-NODE-003 | Nodes must form an acyclic DAG | ✅ |
| INV-NODE-004 | Nodes must be reproducible from seed | ✅ |

### Dish Projections (INV-DISH-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-DISH-001 | node_id must correspond to a valid DAG node | ✅ |
| INV-DISH-002 | Dish content_hash must match manifest entry | ✅ |
| INV-DISH-003 | Phases and steps must correspond to valid DAG nodes | ✅ |

### Manifest (INV-MAN-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-MAN-001 | Manifest must contain every DAG node | ✅ |
| INV-MAN-002 | Merkle root must be derivable from manifest | ✅ |
| INV-MAN-003 | Manifest must regenerate deterministically | ✅ |

### Merkle Root (INV-MERKLE-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-MERKLE-001 | Merkle root must match manifest | ✅ |
| INV-MERKLE-002 | Changing any node changes root | ✅ |

### Topology (INV-TOPO-*)

| ID | Description | Status |
|----|-------------|--------|
| INV-TOPO-001 | All food nodes must have authority and verification edges | ✅ |

---

## Test Results

✅ **30 / 30 tests passing**

```
tests/test_food_cart_universe.py::TestUniverseSeed (5 tests)
tests/test_food_cart_universe.py::TestDAGStructure (6 tests)
tests/test_food_cart_universe.py::TestDishProjections (6 tests)
tests/test_food_cart_universe.py::TestManifest (4 tests)
tests/test_food_cart_universe.py::TestMerkleRoot (2 tests)
tests/test_food_cart_universe.py::TestTopologyIntegration (5 tests)
tests/test_food_cart_universe.py::TestSchemaIntegration (2 tests)
```

---

## Files Generated

| Path | Description | Size |
|------|-------------|------|
| `seed/food_cart_universe.yaml` | Universe seed definition | 2.3 KB |
| `out/food_cart_dag.json` | Complete DAG (53 nodes) | ~30 KB |
| `data/dishes/tacos.json` | Tacos dish projection | 3.0 KB |
| `data/dishes/ramen.json` | Ramen dish projection | 3.0 KB |
| `data/dishes/pizza.json` | Pizza dish projection | 3.0 KB |
| `data/dishes/burger.json` | Burger dish projection | 3.0 KB |
| `out/food_cart_manifest.jsonl` | Canonical manifest (53 entries) | ~10 KB |
| `out/food_cart_merkle_root.txt` | Merkle root hash | 65 bytes |

---

## Integration with PERCEIVABLE_INFINITY

The Food Cart Universe is fully integrated into the repository's topology visualization:

1. **Node Classification:** Dish files classified as `FOOD_DISH_UNIVERSE`
2. **Zone Assignment:** All food nodes in `zone_5_analysis_reporting`
3. **Visual Mapping:** Custom "plate" shape in visualization
4. **Schema Definition:** Full node class definition in `topology/graph_schema.yaml`

To view in the interactive visualization:
1. Open `PERCEIVABLE_INFINITY.html` in a browser
2. Navigate to Zone 5 (Analysis & Reporting)
3. See 4 food dish nodes with their metadata

---

## Extending the Universe

To add more dishes:

1. Edit `seed/food_cart_universe.yaml` → add dish to `sample_universe.menu.dishes`
2. Regenerate: `python3 generators/food_cart_fractal_dataset.py ...`
3. Regenerate projections, manifest, and Merkle root
4. Regenerate topology
5. Run tests to verify invariants

---

## References

- **Canonical Schema Proposal:** ChatGPT Canonical Schema Closure Specification
- **PERCEIVABLE_INFINITY:** `PERCEIVABLE_INFINITY_SCHEMA.yaml`
- **Graph Schema:** `topology/graph_schema.yaml`
- **Tests:** `tests/test_food_cart_universe.py`
- **Validators:** `validators/validate_food_cart_universe.py`

---

## Principles Demonstrated

✅ **Universe seed defines ontology** - Seed is the single source of truth  
✅ **DAG nodes define structure** - All structure derives from content-addressed nodes  
✅ **Views are projections** - Dish files reference nodes, don't define them  
✅ **Content-addressed** - Node IDs are deterministic hashes  
✅ **Reproducible** - Same seed always generates same DAG  
✅ **Verifiable** - Merkle root enables cryptographic verification  
✅ **Integrated** - Seamlessly part of PERCEIVABLE_INFINITY topology  

---

**Status:** Production-ready ✅  
**Test Coverage:** 100% ✅  
**Invariants:** All satisfied ✅
