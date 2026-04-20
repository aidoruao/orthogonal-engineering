---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch3, issue-52-comment]
register: audit
---

## Investigation: Pollution Fog Not Affecting LODs

Hi @DarkShadow44, I've analyzed the pollution fog issue.

### Root Cause
DH uses its own fog rendering system (`GlDhFogRenderer`) that doesn't integrate with GTNH's pollution fog:

```java
// RenderHelper.java:118-127
public static void disableFog() {
    GL11.glDisable(GL11.GL_FOG);
    // For Angelica
    GL11.glFogf(GL11.GL_FOG_START, 1024 * 1024 * 15);  // Extreme values
    GL11.glFogf(GL11.GL_FOG_END, 1024 * 1024 * 16);
}
```

DH fog is rendered separately from vanilla fog, so pollution fog modifications don't affect LODs.

### The Fix

**Option 1: Pollution Integration** (if GTNH exposes API)

**File:** `src/main/java/com/seibel/distanthorizons/common/render/openGl/postProcessing/fog/GlDhFogRenderer.java`

```java
@Override
public void renderFog(IMinecraftClientWrapper mc, float partialTicks) {
    // Check for pollution fog
    if (ForgeMain.gtCompat != null && ForgeMain.gtCompat.isPollutionActive()) {
        Color pollutionColor = ForgeMain.gtCompat.getPollutionFogColor();
        float pollutionDensity = ForgeMain.gtCompat.getPollutionFogDensity();
        
        // Apply pollution fog to DH rendering
        this.fogShader.setUniformColor(pollutionColor);
        this.fogShader.setUniformDensity(pollutionDensity);
    }
    
    // ... rest of fog rendering
}
```

**Option 2: Config to Disable DH Fog**

Add config option to use vanilla fog instead of DH fog for LODs.

### Workaround

Disable DH fog in config if option exists, or reduce LOD render distance so fog is less noticeable.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
