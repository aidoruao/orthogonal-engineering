Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH's far-fade renderer (farFadeRenderer.render()) fades LODs to void at the render distance boundary regardless of whether the vanilla chunk at that position has been received from the server; the fade triggers as soon as the LOD is present, creating a sharp visible edge.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/render/renderer/LodRenderer.java`
- `src/main/java/com/seibel/distanthorizons/core/generation/RemoteWorldRetrievalQueue.java`

## The Fix

Before fading a LOD section, check whether the corresponding vanilla chunk has been received from the server (via RemoteWorldRetrievalQueue.isChunkReceived()); if not, defer the fade until the chunk is available.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #20

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
