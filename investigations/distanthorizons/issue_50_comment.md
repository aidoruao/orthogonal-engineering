Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

RemoteWorldRetrievalQueue or WorldGenerationQueue blocks the client thread when waiting for server LOD data; the ~3 minute freeze matches a timeout in PregenManager's pendingGenerations cache (2-minute expiry plus overhead). The client is spinning on a CompletableFuture.get() without a timeout.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/generation/RemoteWorldRetrievalQueue.java`
- `src/main/java/com/seibel/distanthorizons/core/generation/PregenManager.java`

## The Fix

Replace all blocking CompletableFuture.get() calls on the client thread with non-blocking callbacks; add configurable per-request timeouts to RemoteWorldRetrievalQueue.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #51

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
