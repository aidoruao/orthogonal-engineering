---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch4, issue-32-comment]
register: audit
---

## Investigation: Fade Effect Wait for Remote Chunks

Hi @DarkShadow44, this is a feature request for the fade effect.

### Current Behavior
The fade effect (smooth transition between vanilla and LOD terrain) renders based on distance only, without checking if LOD chunks are fully loaded.

### Requested Behavior
Fade should wait for remote chunks to be fully loaded before becoming visible.

### Implementation

**File:** `src/main/java/com/seibel/distanthorizons/common/render/openGl/postProcessing/fade/GlVanillaFadeRenderer.java`

```java
public void render(RenderParams renderParams) {
    // For each fade position
    for (LodRenderSection section : visibleSections) {
        // Check if section is ready
        if (!section.isRenderBufferReady()) {
            continue;  // Skip fade for incomplete sections
        }
        
        // Render fade
        // ...
    }
}
```

**Add to LodRenderSection:**

```java
public boolean isRenderBufferReady() {
    return this.renderBufferContainer != null && 
           this.bufferUploadFutureRef.get() != null &&
           this.bufferUploadFutureRef.get().isDone();
}
```

### Config Option

```java
public static ConfigEntry<Boolean> fadeWaitForChunkLoad = new ConfigEntry.Builder<Boolean>()
    .set(true)
    .comment("Wait for chunks to fully load before fading")
    .build();
```

---
*Investigation performed using orthogonal-engineering forensic methodology.*
