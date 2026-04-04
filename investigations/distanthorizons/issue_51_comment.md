Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

ForgeServerProxy.serverTickEvent drains taskQueue with a 15 ms per-tick budget, but serverChunkLoadEvent enqueues chunk wrappers that call isChunkReady() on every tick until age>200; with many players the queue grows unbounded and dominates the server tick.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`
- `src/main/java/com/seibel/distanthorizons/core/generation/WorldGenerationQueue.java`

## The Fix

Cap chunkLoadEvents queue size; add backpressure so new chunk events are dropped when the queue exceeds a configurable limit; expose a config option to disable server-side DH chunk processing entirely.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #50
- #62

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
