---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch2, issue-64-comment]
register: audit
---

## Investigation: LODs Not Rendering with Shaders at Load

Hi @DarkShadow44, I've analyzed the shader loading issue.

### Root Cause
`DhApiRenderProxy` defaults to non-deferred rendering (`deferTransparentRendering = false`):

```java
// DhApiRenderProxy.java:44
private boolean deferTransparentRendering = false;
```

When shaders are enabled at world load:
1. The render path is determined before shaders are detected
2. `LodRenderer.renderLodPass()` returns early if render mode doesn't match:

```java
// LodRenderer.java:122-124
boolean deferTransparentRendering = DhApiRenderProxy.INSTANCE.getDeferTransparentRendering();
if (runningDeferredPass && !deferTransparentRendering) {
    return;  // Early return - LODs not rendered!
}
```

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeClientProxy.java`

Add shader detection at world load:

```java
@SubscribeEvent
public void onWorldLoad(WorldEvent.Load event) {
    // Detect if shaders are active
    IIrisAccessor iris = ModAccessorInjector.INSTANCE.get(IIrisAccessor.class);
    if (iris != null && iris.isShaderPackInUse()) {
        DhApiRenderProxy.INSTANCE.setDeferTransparentRendering(true);
        LOGGER.info("Shaders detected - enabling deferred rendering for LODs");
    }
}
```

**Alternative in DhApiRenderProxy.java:**

```java
// Add initialization method
public void initializeRenderMode() {
    IIrisAccessor iris = ModAccessorInjector.INSTANCE.get(IIrisAccessor.class);
    if (iris != null) {
        this.deferTransparentRendering = iris.isShaderPackInUse();
    }
}
```

### Workaround

Disable shaders, load world, then re-enable shaders:
1. Load world without shaders
2. Enable shaders after world loads
3. LODs should render correctly

### Why This Works
- Ensures deferred rendering mode matches shader state
- Prevents render path mismatch at load time

---
*Investigation performed using orthogonal-engineering forensic methodology.*
