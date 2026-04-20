---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch4, issue-47-comment]
register: audit
---

## Investigation: NPCDBC Outline Compatibility

Hi @DarkShadow44, I've analyzed the NPCDBC outline issue.

### Root Cause
DH's OpenGL state manipulation in `RenderHelper.drawLods()` likely interferes with NPCDBC's outline rendering:

```java
// RenderHelper.java:22-37
public static void drawLods() {
    if (ForgeMain.angelicaCompat == null) {
        GL32.glDisable(GL32.GL_ALPHA_TEST);
    }
    GL11.glClearColor(1, 1, 1, 0.0F);  // May clear outline buffer
    // ...
    GL32.glDisable(GL32.GL_BLEND);  // Breaks outline transparency
}
```

### The Fix

Same fix as #56 and #42 - complete OpenGL state preservation:

**File:** `src/main/java/com/seibel/distanthorizons/RenderHelper.java`

```java
public static void drawLods() {
    // Save ALL relevant GL state
    boolean alphaTest = GL11.glIsEnabled(GL32.GL_ALPHA_TEST);
    boolean blend = GL11.glIsEnabled(GL32.GL_BLEND);
    boolean depthTest = GL11.glIsEnabled(GL32.GL_DEPTH_TEST);
    int depthFunc = GL11.glGetInteger(GL32.GL_DEPTH_FUNC);
    FloatBuffer clearColor = BufferUtils.createFloatBuffer(16);
    GL11.glGetFloat(GL11.GL_COLOR_CLEAR_VALUE, clearColor);
    
    // DH rendering
    // ...
    
    // Restore ALL state
    if (alphaTest) GL32.glEnable(GL32.GL_ALPHA_TEST);
    else GL32.glDisable(GL32.GL_ALPHA_TEST);
    
    if (blend) GL32.glEnable(GL32.GL_BLEND);
    else GL32.glDisable(GL32.GL_BLEND);
    
    if (depthTest) GL32.glEnable(GL32.GL_DEPTH_TEST);
    else GL32.glDisable(GL32.GL_DEPTH_TEST);
    
    GL32.glDepthFunc(depthFunc);
    GL11.glClearColor(clearColor.get(0), clearColor.get(1), clearColor.get(2), clearColor.get(3));
    // ...
}
```

### Recommendation

Combine this fix with #56 and #42 for comprehensive OpenGL state management.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
