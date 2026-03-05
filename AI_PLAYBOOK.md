# AI_PLAYBOOK.md
# ================
# Session-level guidance for AI agents working in this repository.
# Read this AFTER the mandatory schema files listed in COPILOT_ONBOARDING_SCHEMA.yaml.
#
# Authority: COVENANT.md
# Version: 2.0.0 (PR #60.5 — adds memory-bounded protocol and 3-zone rule)

## Purpose

This playbook records operational patterns for AI agents so that each session
can pick up efficiently where the previous one left off.

---

## Session start checklist

1. **Read the mandatory files** (in order from `COPILOT_ONBOARDING_SCHEMA.yaml`).
2. **Run successor readiness tests** before touching any code:
   ```bash
   python3 -m pytest tests/test_successor_readiness.py tests/test_perceivable_infinity.py tests/test_pr60_topology_sanity.py -v
   ```
3. **Check the latest `topology_graph.json`** for current node counts and zone distribution.
4. **Open `HANDOFF_TEMPLATE.md`** for notes left by the previous session.
5. **Read `SUCCESSOR_VERIFICATION.yaml`** to understand the session continuity protocol.

---

## Memory-Bounded Operation (for 2M+ files)

You are a finite instance. You cannot hold 2M files in memory. Follow this protocol:

### Zone Affinity

- Identify your **current zone** from `PERCEIVABLE_INFINITY.html` (zoom level 1 shows classified nodes by zone).
- Load **only files in your current zone** into working memory for detailed reasoning.
- For **cross-zone queries**, use the `clusters` section of `topology_graph.json` for lossy summaries — do not load full node lists for distant zones.

### The 3-Zone Rule

| Zone type | Detail level | How to access |
|-----------|-------------|---------------|
| **Current zone** | Full detail | Load individual `FileNode` objects |
| **2 neighboring zones** | Lossy summary | Read from `topology_graph.json → clusters[zone_id]` |
| **All other zones** | Zone card only | Count + representative_sample from cluster |

> **Example:** If you are working in `zone_4_forgiveness_grace`, you keep zone 4 in full detail,
> zones 3 and 5 as cluster summaries, and all other zones as zone cards only.

### When to Expand

To examine a distant zone in detail, you must:
1. Log the expansion request in `STATE.md`
2. Read the zone's cluster summary first (`clusters[zone_id]`)
3. If full detail is needed, request it explicitly and justify it in the commit message

### Reading Cluster Summaries

The `topology_graph.json` now includes a `clusters` key (Phase 7 output):
```json
{
  "clusters": {
    "zone_4_forgiveness_grace": {
      "zone_id": "zone_4_forgiveness_grace",
      "total_node_count": 693,
      "hash_verified_count": 0,
      "class_distribution": {"FORGIVENESS_MODULE": 693},
      "representative_sample": ["fix_forgiveness_system.py", ...]
    }
  }
}
```

---

## Key invariants to preserve

| Invariant | Quick check |
|-----------|-------------|
| `PERCEIVABLE_INFINITY.html` must not embed full `graphData` | `grep -c "graphData = {" PERCEIVABLE_INFINITY.html` must be 0 |
| COVENANT_ROOT must exist | Zone 1 node count > 0 in `topology_graph.json` |
| GUARDIAN_SYSTEM must exist | `JESUS_REALITY_GUARDIAN.py` classified correctly |
| Hash manifest exists | `canonical/hash_manifest.json` must exist after pipeline run |
| Successor tests pass | `pytest tests/test_successor_readiness.py` — all green |
| Tests must pass | `pytest tests/test_perceivable_infinity.py tests/test_pr60_topology_sanity.py` — all green |

---

## How to add a new node class

1. Add the class definition (with `intent`, `teleology`, `success_criteria`) to `ONTOLOGY_SCHEMA.yaml`.
2. Add a node definition to `topology/graph_schema.yaml` (under `nodes:`).
3. Add a classification rule to `PERCEIVABLE_INFINITY_SCHEMA.yaml`
   (under `classification_pipeline.classification.rules`).
4. Add a zone assignment rule if the class belongs in a specific zone.
5. Run `python3 generate_perceivable_infinity.py .` to regenerate the graph + manifest.
6. Add a test in `tests/test_pr60_topology_sanity.py` for the known mapping.
7. Update `COVENANT_INVARIANTS.yaml → INV-C-001.known_mappings` with examples.
8. Add successor tests for the new class to `tests/test_successor_readiness.py`.

---

## How to update the visualization

The renderer (`topology/renderer.py`) generates `PERCEIVABLE_INFINITY.html`.
The HTML shell loads `topology_graph.json` at runtime via `fetch()`.

**Never** embed `graphData = { ... }` in the HTML — this causes 57k-line files
and breaks at 67k-scale.  The invariant `INV-R-001` enforces this.

The `clusters` key in `topology_graph.json` provides the Level 0 (zones only)
and Level 1 data without needing to iterate all nodes.

To change the visual appearance:
- Edit the CSS in `topology/renderer.py → _generate_html()`.
- Colour mappings live in `PERCEIVABLE_INFINITY_SCHEMA.yaml → rendering_layers`.
- After any renderer change, re-run: `python3 generate_perceivable_infinity.py .`

---

## How to run a full census scan

```bash
# Full pipeline (scan + classify + hash-verify + cluster + render + manifest):
python3 generate_perceivable_infinity.py .

# With full SHA-256 (slow — hashes every file, not just covenant-critical):
python3 generate_perceivable_infinity.py . --full-hash

# Scan only (produces topology_graph.json, skips HTML render):
python3 -m topology.topology_scanner . topology_graph.json

# View the result (requires local HTTP server for fetch() to work):
python3 -m http.server 8080
# Open http://localhost:8080/PERCEIVABLE_INFINITY.html
```

---

## Handling scale (67k+ files)

- The scanner uses `os.walk()` — no full file list held in memory.
- SHA-256 is computed selectively (only COVENANT_ROOT, GUARDIAN_SYSTEM, EVIDENCE_ARTIFACT)
  unless `--full-hash` is passed.
- Cluster summaries (Phase 7) provide lossy zone/class aggregations for AI perception at scale.
- The HTML visualization caps nodes per zone at the levels defined in
  `SCALING_STRATEGY.yaml`.  Truncation is always announced with the true count.
- If the scan takes > 60 s, consider skipping the dependency extraction phase
  (set `max_file_size_for_deps = 0`).

---

## Session end checklist

1. **Fill `HANDOFF_TEMPLATE.md`** with:
   - What was changed and why.
   - Current test status.
   - Open issues or next steps.
2. **Add ≥3 successor verification tests** to `tests/test_successor_readiness.py`
   (per `SUCCESSOR_VERIFICATION.yaml`).
3. **Update `STATE.md`** with session summary (files modified, tests added, open issues).
4. **Run the full test suite** one last time (all tests must pass).
5. Commit and push.

---

## Forbidden patterns (never do these)

| Pattern | Reason |
|---------|--------|
| Embed `graphData = {...}` in HTML | 57k+ line files, breaks at 67k scale |
| Modify `.jesus_reality_guardian_state.json` without covenant authority | COVENANT_ROOT — immutable |
| Delete entries from `.ontological_violations/` | VIOLATION_LOG — append-only |
| Weaken any `COVENANT_INVARIANTS.yaml` entry | Invariants are tightened, never weakened |
| Silently truncate node output | Always show true count with truncation notice |
| Mutate a node without reading its `intent` + `teleology` in `ONTOLOGY_SCHEMA.yaml` | Teleological alignment required |
| Load full node list for distant zones | Use cluster summaries (3-zone rule) |

