## Investigation: Photon Shader Compatibility

Hi @DarkShadow44, I've investigated the Photon shader rendering issue.

### Root Cause
Different shader packs have different rendering requirements. DH's shader integration uses a generic approach that may not work correctly with Photon shaders' specific rendering pipeline.

### Key Areas of Concern

1. **Depth Buffer Format**: Photon may expect different depth buffer format than DH provides
2. **Transparency Order**: Photon's transparency handling may conflict with DH's deferred rendering
3. **Uniform Variables**: Photon-specific uniforms may not be set correctly

### Proposed Fix

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`

Add shader-specific compatibility options:

```java
public static class ShaderCompatibility {
    public static final ConfigEntry<String> shaderPackCompatibility = new ConfigEntry<>();
    // Options: "AUTO", "GENERIC", "PHOTON", "SOLAS", "COMPATIBILITY"
    
    public static final ConfigEntry<Boolean> useAlternateDepthBuffer = new ConfigEntry<>();
    public static final ConfigEntry<Boolean> disableTransparentLodRendering = new ConfigEntry<>();
}
```

**File:** `src/main/java/com/seibel/distanthorizons/common/render/openGl/GlDhTerrainShaderProgram.java`

Add shader detection in render setup:

```java
private void configureForShaderPack() {
    IIrisAccessor iris = ModAccessorInjector.INSTANCE.get(IIrisAccessor.class);
    if (iris == null || !iris.isShaderPackInUse()) return;
    
    String shaderPackName = getCurrentShaderPackName(); // via Iris API
    
    switch (shaderPackName.toLowerCase()) {
        case "photon":
            // Photon-specific settings
            GL11.glEnable(GL11.GL_DEPTH_TEST);
            // Adjust depth buffer handling
            break;
        case "solas":
            // Solas-specific settings
            break;
    }
}
```

### Immediate Workaround

Try these settings in DH config:
1. Set `Graphics > Advanced > Culling > disableShadowPassFrustumCulling` to `true`
2. Reduce LOD render distance temporarily
3. Use "COMPATIBILITY" renderer mode if available

### Testing Needed

To properly fix this, I need:
1. Screenshot of the rendering issue with Photon
2. Comparison with vanilla (no shaders) and other shader packs
3. Any errors in `logs/latest.log` related to shader compilation

---
*Investigation performed using orthogonal-engineering forensic methodology.*
