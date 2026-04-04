Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

ForgeServerProxy.serverTickEvent processes the chunkLoadEvents queue and taskQueue each tick; under high chunk-load conditions the ConcurrentLinkedQueue is drained in a tight loop on the server thread causing a deadlock or stack overflow when BatchGenerationEnvironment accesses world state.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`
- `src/main/java/com/seibel/distanthorizons/common/wrappers/worldGeneration/BatchGenerationEnvironment.java`

## The Fix

Add a maximum iteration cap to the serverTickEvent chunk-load drain loop and catch/log exceptions per task rather than letting them propagate; bound taskQueue drain to the 15 ms time budget already coded but verify it isn't bypassed for non-limited tasks.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #51
- #53

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
