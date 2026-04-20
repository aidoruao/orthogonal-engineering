---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch2, issue-42-comment]
register: audit
---

## Investigation: Blindness/Underwater Overlay Opacity

Hi @DarkShadow44, I've found the cause of the overlay transparency issue.

### Root Cause
`RenderHelper.drawLods()` unconditionally disables `GL_BLEND`:

```java
// RenderHelper.java:22-37
public static void drawLods() {
    // ...
    ClientApi.INSTANCE.renderLods();
    GL32.glDepthFunc(GL32.GL_LEQUAL);
    if (ForgeMain.angelicaCompat == null) {
        GL32.glEnable(GL32.GL_ALPHA_TEST);
    }
    GL32.glDisable(GL32.GL_BLEND);  // Line 37 - breaks overlays!
    // ...
}
```

Minecraft's blindness and underwater overlays rely on `GL_BLEND` being enabled for transparency. DH disables it without restoring.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/RenderHelper.java`

```java
public static void drawLods() {
    // ... setup code ...
    
    // Save current blend state
    boolean blendEnabled = GL11.glIsEnabled(GL32.GL_BLEND);
    
    // DH rendering
    ClientApi.INSTANCE.renderLods();
    
    GL32.glDepthFunc(GL32.GL_LEQUAL);
    
    // Restore blend state instead of unconditionally disabling
    if (blendEnabled) {
        GL32.glEnable(GL32.GL_BLEND);
    } else {
        GL32.glDisable(GL32.GL_BLEND);
    }
    
    // ... rest of cleanup ...
}
```

Same fix needed for `drawLodsFade()` method.

### Why This Works
- Preserves Minecraft's blend state for overlays
- DH's rendering still works correctly
- Other mods' transparency effects are preserved

### Related Issue
Same root cause as #56 (black screen without Angelica) - OpenGL state management.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
