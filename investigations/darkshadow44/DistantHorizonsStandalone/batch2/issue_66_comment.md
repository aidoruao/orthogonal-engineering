---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch2, issue-66-comment]
register: audit
---

## Investigation: Solas Shader Compatibility

Hi @DarkShadow44, this issue is related to #65 (Photon shaders).

### Analysis
Solas shader pack has similar compatibility issues with DH's rendering pipeline.

### Recommendation
Implement a unified shader compatibility system that handles:
- Photon shaders (#65)
- Solas shaders (#66)
- Other shader packs

See #65 for detailed fix proposal.

### Immediate Workaround
Try the same workarounds as #65:
1. Disable shadow pass frustum culling
2. Reduce LOD render distance
3. Toggle deferred rendering mode

---
*Investigation performed using orthogonal-engineering forensic methodology.*
