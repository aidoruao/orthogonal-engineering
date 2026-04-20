---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-56-comment]
register: audit
---

## Investigation: Black Screen Without Angelica

Hi @DarkShadow44, I've found the likely cause of the black screen crash when Angelica isn't present.

### Root Cause
`RenderHelper.java` manipulates OpenGL state differently when `ForgeMain.angelicaCompat == null`:

```java
// RenderHelper.java:22-37
public static void drawLods() {
    // ...
    if (ForgeMain.angelicaCompat == null) {
        GL32.glDisable(GL32.GL_ALPHA_TEST);  // Line 26
    }
    GL11.glClearColor(1, 1, 1, 0.0F);      // Line 28 - clears to transparent white!
    // ...
    if (ForgeMain.angelicaCompat == null) {
        GL32.glEnable(GL32.GL_ALPHA_TEST);   // Line 35
    }
}
```

**The problem:**
1. `glClearColor(1, 1, 1, 0.0F)` clears framebuffer to transparent white
2. Alpha test disable/enable sequence may interfere with vanilla MC rendering
3. No complete state preservation (only active texture and bound texture saved)

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/RenderHelper.java`

```java
public static void drawLods() {
    ClientApi.RENDER_STATE.mcModelViewMatrix = getModelViewMatrix();
    ClientApi.RENDER_STATE.mcProjectionMatrix = getProjectionMatrix();
    ClientApi.RENDER_STATE.clientLevelWrapper = ClientLevelWrapper.getWrapper(Minecraft.getMinecraft().theWorld);

    // Save state
    boolean alphaTestEnabled = GL11.glIsEnabled(GL32.GL_ALPHA_TEST);
    boolean blendEnabled = GL11.glIsEnabled(GL32.GL_BLEND);
    FloatBuffer clearColor = BufferUtils.createFloatBuffer(16);
    GL11.glGetFloat(GL11.GL_COLOR_CLEAR_VALUE, clearColor);
    
    if (ForgeMain.angelicaCompat == null) {
        GL32.glDisable(GL32.GL_ALPHA_TEST);
    }
    // Use opaque clear color
    GL11.glClearColor(1, 1, 1, 1.0F);
    
    int oldActiveTex = GL11.glGetInteger(GL32.GL_ACTIVE_TEXTURE);
    int oldBoundTex = GL11.glGetInteger(GL32.GL_TEXTURE_BINDING_2D);
    
    ClientApi.INSTANCE.renderLods();
    
    GL32.glDepthFunc(GL32.GL_LEQUAL);
    
    // Restore state properly
    if (ForgeMain.angelicaCompat == null && alphaTestEnabled) {
        GL32.glEnable(GL32.GL_ALPHA_TEST);
    }
    if (blendEnabled) {
        GL32.glEnable(GL32.GL_BLEND);
    }
    GL11.glClearColor(clearColor.get(0), clearColor.get(1), clearColor.get(2), clearColor.get(3));
    
    GL32.glActiveTexture(oldActiveTex);
    GL32.glBindTexture(GL32.GL_TEXTURE_2D, oldBoundTex);
}
```

### Why This Works
- Preserves original OpenGL state instead of assuming defaults
- Prevents transparent clear color from causing black screen
- Alpha test restoration respects original state

### Workaround (Immediate)
Install **Angelica 2.1.5+** - the mod is designed to work with Angelica and uses different rendering path when present.

### How to Verify
1. Apply fix and test without Angelica
2. Black screen should be resolved
3. LODs should render correctly

---
*Investigation performed using orthogonal-engineering forensic methodology.*
