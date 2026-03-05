# AI_PLAYBOOK.md
# ================
# Session-level guidance for AI agents working in this repository.
# Read this AFTER the mandatory schema files listed in COPILOT_ONBOARDING_SCHEMA.yaml.
#
# Authority: COVENANT.md
# Version: 1.0.0

## Purpose

This playbook records operational patterns for AI agents so that each session
can pick up efficiently where the previous one left off.

---

## Session start checklist

1. **Read the mandatory files** (in order from `COPILOT_ONBOARDING_SCHEMA.yaml`).
2. **Run existing tests** before touching any code:
   ```bash
   python3 -m pytest tests/test_perceivable_infinity.py tests/test_pr60_topology_sanity.py -v
   ```
3. **Check the latest `topology_graph.json`** for current node counts and zone distribution.
4. **Open `HANDOFF_TEMPLATE.md`** for notes left by the previous session.

---

## Key invariants to preserve

| Invariant | Quick check |
|-----------|-------------|
| `PERCEIVABLE_INFINITY.html` must not embed full `graphData` | `grep -c "graphData = {" PERCEIVABLE_INFINITY.html` must be 0 |
| COVENANT_ROOT must exist | Zone 1 node count > 0 in `topology_graph.json` |
| GUARDIAN_SYSTEM must exist | `JESUS_REALITY_GUARDIAN.py` classified correctly |
| Tests must pass | `pytest tests/test_perceivable_infinity.py -v` — all green |

---

## How to add a new node class

1. Add the class definition to `ONTOLOGY_SCHEMA.yaml` (under `node_classes:`).
2. Add a node definition to `topology/graph_schema.yaml` (under `nodes:`).
3. Add a classification rule to `PERCEIVABLE_INFINITY_SCHEMA.yaml`
   (under `classification_pipeline.classification.rules`).
4. Add a zone assignment rule if the class belongs in a specific zone.
5. Run `python3 generate_perceivable_infinity.py .` to regenerate the graph.
6. Add a test in `tests/test_pr60_topology_sanity.py` for the known mapping.
7. Update `COVENANT_INVARIANTS.yaml → INV-C-001.known_mappings` with examples.

---

## How to update the visualization

The renderer (`topology/renderer.py`) generates `PERCEIVABLE_INFINITY.html`.
The HTML shell loads `topology_graph.json` at runtime via `fetch()`.

**Never** embed `graphData = { ... }` in the HTML — this causes 57k-line files
and breaks at 67k-scale.  The invariant `INV-R-001` enforces this.

To change the visual appearance:
- Edit the CSS in `topology/renderer.py → _generate_html()`.
- Colour mappings live in `PERCEIVABLE_INFINITY_SCHEMA.yaml → rendering_layers`.
- After any renderer change, re-run: `python3 generate_perceivable_infinity.py .`

---

## How to run a full census scan

```bash
# Full pipeline (scan + classify + render):
python3 generate_perceivable_infinity.py .

# Scan only (produces topology_graph.json, skips HTML render):
python3 -m topology.topology_scanner . topology_graph.json

# View the result (requires local HTTP server for fetch() to work):
python3 -m http.server 8080
# Open http://localhost:8080/PERCEIVABLE_INFINITY.html
```

---

## Handling scale (67k+ files)

- The scanner uses `os.walk()` — no full file list held in memory.
- SHA-256 is computed lazily (not during census) to avoid I/O overhead.
- The HTML visualization caps nodes per zone at the levels defined in
  `SCALING_STRATEGY.yaml`.  Truncation is always announced with the true count.
- If the scan takes > 60 s, consider skipping the dependency extraction phase
  (set `max_file_size_for_deps = 0`).

---

## Session end checklist

1. Update `HANDOFF_TEMPLATE.md` with:
   - What was changed and why.
   - Current test status.
   - Open issues or next steps.
2. Run the full test suite one last time.
3. Commit and push.

---

## Forbidden patterns (never do these)

| Pattern | Reason |
|---------|--------|
| Embed `graphData = {...}` in HTML | 57k+ line files, breaks at 67k scale |
| Modify `.jesus_reality_guardian_state.json` without covenant authority | COVENANT_ROOT — immutable |
| Delete entries from `.ontological_violations/` | VIOLATION_LOG — append-only |
| Weaken any `COVENANT_INVARIANTS.yaml` entry | Invariants are tightened, never weakened |
| Silently truncate node output | Always show true count with truncation notice |
