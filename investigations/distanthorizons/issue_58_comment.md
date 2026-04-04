Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

No per-dimension whitelist/blacklist or per-dimension LOD radius configuration exists; DH applies uniform settings to all dimensions.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/config/Config.java`
- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

## The Fix

Add a dimension-keyed config map (dimensionWhitelist, dimensionBlacklist, dimensionMaxRadius) to Config; in ForgeServerProxy.serverLevelLoadEvent(), skip DH initialization for blacklisted dimensions and apply per-dimension radius limits.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

None identified.

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: LOW. Full gap analysis available upon request.*
