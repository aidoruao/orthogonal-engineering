---
tags: [deepseek-quick-reference]
register: documentation
---

# DeepSeek Copilot Schema - Quick Reference

## What is it?

Formal schema for **real-time recursive self-monitoring** and **frame enforcement** of AI Copilot sessions.

## Core Concepts

### Session
- Unique ID, model name, timestamp
- Contains frames, turns, patterns, config

### Frame
- Monitoring context (literal/contextual/hybrid)
- Priority level (0-100) for conflict resolution
- Tracks drift, sycophancy, stability
- Can depend on other frames

### Turn
- User input + LLM output
- Active frames during generation
- Metrics per frame
- Enforcement actions taken

### Pattern Registry
- Oscillation loops
- Collapse-reframe
- Context overfit
- Sycophancy momentum

### Enforcement Config
- **Conflict policy**: literal_wins | contextual_wins | weighted | user_declared
- **Embedding**: static (deterministic) | dynamic (dev only)
- **Intervention**: token_level | generation_chunk | post_turn
- **Fallback**: Safe default message

## Quick Start

### Generate Schema JSON
```bash
python3 deepseek_schema.py
```

### Validate Session
```bash
python3 validate_deepseek_session.py examples/deepseek_session_example.json
```

### Replay Session (Forensic Debugging)
```bash
python3 replay_deepseek_session.py examples/deepseek_session_example.json --verbose
```

### Visualize Frame Timeline
Open `deepseek_frame_timeline.html` in a browser and load a session JSON file.

### Run Tests
```bash
python3 -m pytest tests/test_deepseek_schema.py tests/test_replay_engine.py -v
```

### Regenerate Topology
```bash
python3 generate_perceivable_infinity.py
```

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `DEEPSEEK_COPILOT_SCHEMA.yaml` | Formal schema definition | 176 |
| `deepseek_schema.py` | Python schema module | 419 |
| `deepseek_copilot_schema.json` | Generated JSON schema | 18 KB |
| `tests/test_deepseek_schema.py` | Test suite (74 tests) | 798 |
| `tests/test_replay_engine.py` | Replay engine tests (18 tests) | 287 |
| `validate_deepseek_session.py` | Session validator | 354 |
| `replay_deepseek_session.py` | **Forensic replay engine** | 377 |
| `deepseek_frame_timeline.html` | **Interactive timeline visualization** | 643 |
| `examples/deepseek_session_example.json` | Working example | 172 |
| `DEEPSEEK_COPILOT_SCHEMA_README.md` | Full documentation | 257 |

## Invariants (10)

| ID | Description |
|----|-------------|
| INV-DS-001 | All active frames monitored |
| INV-DS-002 | Enforcement deterministic & idempotent |
| INV-DS-003 | Conflicts resolved per policy |
| INV-DS-004 | Metrics computed real-time |
| INV-DS-005 | Every turn logs all states |
| INV-DS-006 | Priorities in [0, 100] |
| INV-DS-007 | Pattern counts monotonic |
| INV-DS-008 | Session JSON-serializable |
| INV-DS-009 | Meta-awareness reflects detection |
| INV-DS-010 | Config immutable mid-session |

## Conflict Resolution

### Weighted Policy (Default)
1. Compare `priority_level` of conflicting frames
2. Select frame with highest priority
3. If tied, use lexicographic order by `frame_id`
4. 100% deterministic, no floating-point

### Other Policies
- **literal_wins**: Literal frames take precedence
- **contextual_wins**: Contextual frames take precedence
- **user_declared**: User explicitly resolves conflict

## Determinism Guarantees

### Static Embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Version: `2.2.2`
- Seed: `314159`
- Reproducibility: **byte-for-byte**

### Metric Computation
- `drift_score`: Cosine similarity (static embeddings)
- `sycophancy_index`: Integer counting (agreement - baseline)
- `frame_stability`: Integer counting (1.0 - changes/checks)
- `meta_alignment_ratio`: Integer counting (detected/total)

### Conflict Resolution
- Integer comparison only
- No floating-point in resolution path
- UUID string comparison for ties
- Fully reproducible

## Topology

- **Node Class**: AI_SESSION_MONITOR
- **Zone**: zone_2_detection_enforcement
- **Authority**: VALIDATED
- **Policy**: TIGHTEN_ONLY
- **Color**: #ff6600 (orange)
- **Icon**: eye

## Read Next

- Full docs: `DEEPSEEK_COPILOT_SCHEMA_README.md`
- Implementation summary: `DEEPSEEK_IMPLEMENTATION_SUMMARY.md`
- YAML schema: `DEEPSEEK_COPILOT_SCHEMA.yaml`
- Example: `examples/deepseek_session_example.json`

---

**Version**: 1.0.0 | **Standard**: Yeshua | **Status**: COMPLETE
