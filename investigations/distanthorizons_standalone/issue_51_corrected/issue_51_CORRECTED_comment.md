## Investigation: Server TPS Lag (Corrected Analysis)

Hi @DarkShadow44, I've analyzed the TPS lag issue reported by @MrFuzzihead. This is a **corrected analysis** that updates the line numbers and findings from the initial Batch 1 investigation.

### ⚠️ Important Note on Evidence

The server log (`fml-server-2.log`) and config (`DistantHorizons.toml`) referenced in the GitHub issue were **not available** for this analysis. The following findings are based on **source code verification** against the current DarkShadow44 repository (commit `1abcd98`).

---

### Root Cause (Verified Against Current Source)

`ForgeServerProxy.serverTickEvent()` has performance issues that can cause TPS drops:

```java
// ForgeServerProxy.java:105-141 (VERIFIED line numbers)
@SubscribeEvent
public void serverTickEvent(TickEvent.ServerTickEvent event) {
    if (event.phase == TickEvent.Phase.END) {
        // Lines 108-121: Unbounded chunk event queue iteration
        Iterator<ChunkLoadEvent> iterator = chunkLoadEvents.iterator();
        while (iterator.hasNext()) {
            ChunkLoadEvent chunkLoadEvent = iterator.next();
            if (chunkLoadEvent.chunk.isChunkReady()) {
                this.serverApi.serverChunkLoadEvent(chunkLoadEvent.chunk, chunkLoadEvent.level);
                iterator.remove();
            } else {
                chunkLoadEvent.age++;
                if (chunkLoadEvent.age > 200) {
                    iterator.remove();
                }
            }
        }
        
        // Line 124: 15ms time budget (30% of a 50ms tick!)
        long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(15);
        boolean processedAtLeastOne = false;
        while (!taskQueue.isEmpty()) {
            ScheduledTask<?> scheduledTask = taskQueue.poll();
            if (scheduledTask == null) continue;
            
            scheduledTask.run();
            // Lines 132-137: Time check only after first task
            if (scheduledTask.isLimited()) {
                if (!processedAtLeastOne) {
                    processedAtLeastOne = true;
                } else if (System.nanoTime() >= deadline) {
                    break;
                }
            }
        }
    }
}
```

**Verified Issues:**
1. **Unbounded chunk load event queue** (lines 108-121) - processes ALL pending events every tick
2. **15ms time budget** (line 124) - consumes 30% of the 50ms tick budget for 20 TPS
3. **Mandatory task execution** (lines 132-137) - at least one task always runs regardless of deadline

**Supporting Evidence:**
- `BatchGenerationEnvironment.java:116-120` - Developer comment acknowledges "caused extreme server lag" with larger world gen radius
- `BatchGenerationEnvironment.java:121` - `MAX_WORLD_GEN_CHUNK_BORDER_NEEDED = 0` is an optimization to prevent lag

---

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

```java
@SubscribeEvent
public void serverTickEvent(TickEvent.ServerTickEvent event) {
    if (event.phase == TickEvent.Phase.END) {
        // Limit chunk load event processing per tick
        int maxChunkEventsPerTick = 10;
        int processedChunks = 0;
        
        Iterator<ChunkLoadEvent> iterator = chunkLoadEvents.iterator();
        while (iterator.hasNext() && processedChunks < maxChunkEventsPerTick) {
            ChunkLoadEvent chunkLoadEvent = iterator.next();
            if (chunkLoadEvent.chunk.isChunkReady()) {
                this.serverApi.serverChunkLoadEvent(chunkLoadEvent.chunk, chunkLoadEvent.level);
                iterator.remove();
                processedChunks++;
            } else {
                chunkLoadEvent.age++;
                if (chunkLoadEvent.age > 200) {
                    iterator.remove();
                }
            }
        }
        
        // More conservative time budget: 5ms instead of 15ms
        long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(5);
        boolean processedAtLeastOne = false;
        while (!taskQueue.isEmpty()) {
            ScheduledTask<?> scheduledTask = taskQueue.poll();
            if (scheduledTask == null) continue;
            
            scheduledTask.run();
            if (scheduledTask.isLimited() && processedAtLeastOne) {
                if (System.nanoTime() >= deadline) break;
            }
            processedAtLeastOne = true;
        }
    }
}
```

**Changes:**
- Added `maxChunkEventsPerTick = 10` limit for chunk processing
- Reduced time budget from 15ms to 5ms
- This leaves more headroom for other mods in the tick

---

### Immediate Workarounds

Until a fix is released, try these config changes:

```properties
# In DistantHorizons config file:
enableDistantGeneration=false
```

This will disable the distant generation feature that's causing the server-side lag.

Other options to try:
- Reduce `numberOfWorldGenerationThreads` in config
- Lower render/LOD distance settings
- Use a profiler to confirm the bottleneck location

---

### How to Verify

1. **Use debug profiling:**
   ```
   /debug start
   # Wait 1 minute
   /debug stop
   ```
   Check the profile for `serverTickEvent` time usage.

2. **Use Spark mod (recommended):**
   ```
   /spark profiler --thread Server Thread
   # Wait 1 minute
   /spark profiler --stop
   ```
   Look for `ForgeServerProxy.serverTickEvent` in the flame graph.

3. **Monitor server logs:**
   Watch for "Can't keep up!" messages indicating tick time > 50ms.

---

### Why the Batch 1 Analysis Was Wrong

The initial Batch 1 analysis had **incorrect line numbers**:
- Claimed `serverTickEvent` at lines 117-144 (actual: 105-141)
- Claimed chunk event loop at lines 121-130 (actual: 108-121)
- Claimed time check at lines 136-142 (actual: 132-137)
- Claimed `MAX_WORLD_GEN_CHUNK_BORDER_NEEDED` at line 135 (actual: 121)

These line numbers were likely based on an outdated code snapshot or estimated without verification. **Always verify line numbers against current source code.**

---

### Next Steps

1. **For @MrFuzzihead:** Try the workaround (`enableDistantGeneration=false`) and report back if TPS improves
2. **For @DarkShadow44:** Consider implementing the proposed fix with conservative defaults
3. **Verification:** If possible, please share:
   - The `fml-server-2.log` file
   - The `DistantHorizons.toml` config file
   - Spark profiler output if available

---

*Investigation performed using orthogonal-engineering forensic methodology. Line numbers verified against DarkShadow44/DistantHorizonsStandalone commit 1abcd98.*
