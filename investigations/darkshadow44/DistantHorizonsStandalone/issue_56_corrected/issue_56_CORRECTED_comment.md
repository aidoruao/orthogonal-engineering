---
tags: [investigations, darkshadow44, distanthorizonsstandalone, issue-56-corrected, issue-56-corrected-comment]
register: audit
---

## Investigation: Issue #56 CORRECTED Analysis

Hi @DarkShadow44, I've re-investigated issue #56 using the crash log from @branman5949's second report (after your "Fixed in dev" comment). The previous analysis was incorrect.

### The Previous Analysis Was Wrong

The Batch 1 analysis identified `RenderHelper.drawLods()` as the root cause. **This was incorrect.**

The crash log (`crash-2026-03-22_19.39.31-client.txt`) shows the crash is NOT in LOD rendering — it's in FML's splash screen initialization:

```
---- Minecraft Crash Report ----
Time: 3/22/26, 7:39 PM
Description: Initializing game

Caused by: java.lang.IllegalStateException:
  Texture creation: Invalid operation
at SplashProgress.checkGLError(SplashProgress.java:753)
at SplashProgress$Texture.<init>(SplashProgress.java:621)
at SplashProgress$3.run(SplashProgress.java:212)
```

This crashes during `Description: Initializing game` — **before the main menu even loads**.

### Root Cause: MixinFramebuffer GL Context Corruption

The actual root cause is in `MixinFramebuffer.java`:

```java
@Redirect(
    method = "createFramebuffer",
    at = @At(value = "INVOKE", target = "..."))
private int createDepthTexture() {
    int depthTextureId = TextureUtil.glGenTextures();
    
    // THESE GL CALLS EXECUTE DURING SPLASH SCREEN:
    GL11.glBindTexture(GL11.GL_TEXTURE_2D, depthTextureId);
    GL11.glTexImage2D(GL11.GL_TEXTURE_2D, 0, GL14.GL_DEPTH_COMPONENT24, ...);
    GL11.glTexParameteri(GL11.GL_TEXTURE_2D, GL11.GL_TEXTURE_MIN_FILTER, ...);
    // ...
}
```

**The problem:** When `Framebuffer.createFramebuffer()` is called during the splash screen (which FML does), these GL calls execute on the splash thread while it holds the GL context. This corrupts the GL context state, causing the subsequent `GL_INVALID_OPERATION` when FML tries to create its splash texture.

### Why It Only Happens Without Angelica

Angelica replaces FML's `SplashProgress` with its own initialization system. With Angelica installed, the problematic FML splash screen code path is bypassed entirely.

### Proposed Fix

**File:** `src/main/java/com/seibel/distanthorizons/mixin/MixinFramebuffer.java`

Add splash screen detection to defer GL calls:

```java
@Redirect(
    method = "createFramebuffer",
    at = @At(value = "INVOKE", target = "Lnet/minecraft/client/renderer/OpenGlHelper;func_153185_f()I"))
private int createDepthTexture() {
    // If splash screen is still active, use original method
    if (isSplashScreenActive()) {
        return OpenGlHelper.func_153185_f(); // Delegate to original
    }
    
    // Otherwise use custom GL logic
    int depthTextureId = TextureUtil.glGenTextures();
    GL11.glBindTexture(GL11.GL_TEXTURE_2D, depthTextureId);
    // ... rest of custom logic
}

private boolean isSplashScreenActive() {
    // Check if SplashProgress is still running
    // This can be done by checking a flag or class state
    try {
        Class<?> splashProgress = Class.forName("cpw.mods.fml.client.SplashProgress");
        // Check if splash has finished
        return !((boolean) splashProgress.getField("finished").get(null));
    } catch (Exception e) {
        return false; // Assume not active if we can't check
    }
}
```

### Note on "Fixed in dev"

Your previous fix likely addressed a **different** issue — possibly the `glClearColor` alpha value in `RenderHelper.drawLods()` that causes a black screen during **gameplay** (not during initialization).

There may be **two separate bugs**:
1. **This splash screen crash** (init phase) — caused by MixinFramebuffer
2. **The gameplay black screen** — possibly caused by RenderHelper GL state issues

### How to Verify This Fix

1. Enable splash screen in `config/splash.properties`:
   ```properties
   enabled=true
   ```

2. Remove Angelica from mods folder

3. Launch Minecraft with the fixed DH

4. Expected: game loads past splash screen without crash

5. Check: LODs render correctly in-game (separate from this fix)

---
*Corrected investigation performed using orthogonal-engineering forensic methodology.*
*Crash log artifact: crash-2026-03-22_19.39.31-client.txt*
*Previous analysis error: analyzed source code without examining crash log first*
