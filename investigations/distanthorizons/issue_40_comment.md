Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

WorldGenerationQueue or BatchGenerator enters an infinite loop when processing Nether chunks; the Nether's chunk generator (possibly from a ruins/structures mod) throws an exception that is caught but re-queues the same chunk, causing starvation.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/generation/WorldGenerationQueue.java`
- `src/main/java/com/seibel/distanthorizons/core/generation/BatchGenerator.java`

## The Fix

Add a per-chunk failure counter in WorldGenerationQueue; after N consecutive failures for the same chunk position, mark it as permanently failed and remove from the queue with a warning log.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #53

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
