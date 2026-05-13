# CHECKPOINT — Gradle Build: Native Java Methods Compiled

**Date:** 2026-05-12
**Session:** DS5a-5-11-26
**Status:** BUILD SUCCESSFUL — 3 NATIVE TURTLE COMMANDS IN JAR

## What Was Built

| Command | Lua Call | Gate |
|---------|----------|------|
| TurtleScanInventoryCommand | turtle.scanInventory() | 1-2 |
| TurtleTopologicalSortCommand | turtle.topologicalSort(target) | 1 |
| TurtleReachabilityCommand | turtle.isReachable(target) | 2 |

## Build Failures: 6 Issues Fixed

1. **Object[] wrapping** — Map cannot convert to Object[]. Fixed: new Object[]{map}.
2. **NullAway in Reachability** — unboxing @Nullable Integer. Fixed: null check before unbox.
3. **NullAway in TopologicalSort** — same issue at inDegree.get(). Fixed: null check.
4. **JdkObsolete LinkedList** — prohibited type. Fixed: ArrayDeque.
5. **getDescriptionId() nominalism** — translation keys violate Anti-Nominalism. Fixed: BuiltInRegistries.ITEM.getKey().
6. **HashMap non-determinism** — violates Axiom VIII hash-anchoring. Fixed: TreeMap throughout.

## NBLM 3QP Findings
- JSpecify @Nullable, NullAway, JdkObsolete enforced
- Return pattern: single TreeMap in Object[]
- Item names: registry keys, not translation IDs

## Files
- 3 new command files in turtle/core/
- TurtleAPI.java +64 lines (940 total)
- Jar deployed to Logos_World_01 mods folder
- BUILD SUCCESSFUL in 58s, 77 tasks

*Checkpoint: 2026-05-12 — Session DS5a-5-11-26*
