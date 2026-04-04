## Investigation: Severe TPS Lag on Server

Hi @DarkShadow44, I've identified the likely cause of server TPS lag.

### Root Cause
`ForgeServerProxy.serverTickEvent()` has aggressive time management that can exceed server tick budget:

```java
// ForgeServerProxy.java:117-144
@SubscribeEvent
public void serverTickEvent(TickEvent.ServerTickEvent event) {
    if (event.phase == TickEvent.Phase.END) {
        // Process chunk load events - unbounded iteration!
        Iterator<ChunkLoadEvent> iterator = chunkLoadEvents.iterator();
        while (iterator.hasNext()) {
            // ... processing ...
        }
        
        // Time budget: only 15ms!
        long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(15);
        // ... task processing ...
    }
}
```

**Issues:**
1. **15ms time budget** is too aggressive (server tick is 50ms for 20 TPS)
2. **Unbounded chunk load event queue** - iterates all events every tick
3. **Time check only after first task** - at least one task always runs

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

### Immediate Workaround

Add to server config to disable distant generation:
```properties
# In DistantHorizons config
enableDistantGeneration=false
```

### Why This Works
- Limits chunk event processing per tick
- Conservative 5ms budget leaves headroom for other mods
- Prevents single tick from consuming too much time

### How to Verify
1. Use `/debug start` then `/debug stop` after 1 minute
2. Check debug profile for `serverTickEvent` time usage
3. Or use Spark mod: `/spark profiler --thread Server Thread`

---
*Investigation performed using orthogonal-engineering forensic methodology.*
