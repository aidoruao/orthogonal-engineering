## Investigation: Mineshot Camera Compatibility

Hi @DarkShadow44, I've identified the Mineshot compatibility issue.

### Root Cause
Mineshot overrides the camera position for screenshots, but DH's frustum culling uses the player position:

```java
// RenderBufferHandler.java - frustum culling
// Uses camera position which may be overridden by Mineshot
boolean enableFrustumCulling = ...;
if (isShadowPass) {
    enableFrustumCulling = !Config.Client.Advanced.Graphics.Culling.disableShadowPassFrustumCulling.get();
}
```

When Mineshot moves the camera far away for aerial shots, DH culls all LODs thinking they're out of view.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`

Add option to disable frustum culling:

```java
public static class Culling {
    public static final ConfigEntry<Boolean> disableFrustumCulling = new ConfigEntry<>();
    // For compatibility with camera mods like Mineshot
}
```

**File:** `src/main/java/com/seibel/distanthorizons/core/render/RenderBufferHandler.java`

Modify `buildRenderList()`:

```java
public void buildRenderList(RenderParams renderParams) {
    // ...
    boolean enableFrustumCulling = !Config.Client.Advanced.Graphics.Culling.disableFrustumCulling.get();
    
    if (Config.Client.Advanced.Graphics.Culling.disableFrustumCulling.get()) {
        enableFrustumCulling = false;  // Allow override
    }
    // ...
}
```

### Immediate Workaround

Add to config (if possible to edit):
```properties
# In DistantHorizons config
disableShadowPassFrustumCulling=true
```

Or use the mod's debug mode which may disable culling.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
