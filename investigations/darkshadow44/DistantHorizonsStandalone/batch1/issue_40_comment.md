---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-40-comment]
register: audit
---

## Investigation: Nether Chunk Generation Stuck

Hi @DarkShadow44, I've analyzed the Nether chunk generation hang.

### Root Cause
The `BatchGenerationEnvironment` uses a `LinkedBlockingQueue<GenerationEvent>` that can grow unbounded:

```java
// BatchGenerationEnvironment.java:241-253
public final LinkedBlockingQueue<GenerationEvent> generationEventQueue = new LinkedBlockingQueue<>();

@Override
public CompletableFuture<Void> queueGenEvent(...) {
    GenerationEvent genEvent = GenerationEvent.start(...);
    this.generationEventQueue.add(genEvent);  // No size limit!
    return genEvent.future;
}
```

**Nether-specific issues:**
1. No dimension-specific handling (unlike TerraFirmaCraft detection at line 102-112)
2. Generation may fail silently for Nether chunks, leaving futures incomplete
3. Queue grows without bound if generation can't complete

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/common/wrappers/worldGeneration/BatchGenerationEnvironment.java`

```java
public class BatchGenerationEnvironment implements IBatchGeneratorEnvironmentWrapper {
    // Change to bounded queue
    public final LinkedBlockingQueue<GenerationEvent> generationEventQueue = 
        new LinkedBlockingQueue<>(100);  // Max 100 pending events
    
    // Add timeout for generation events
    private static final long GEN_EVENT_TIMEOUT_MS = 30000;  // 30 seconds
    
    // In updateAllFutures() or similar:
    public void updateAllFutures() {
        Iterator<GenerationEvent> iter = this.generationEventQueue.iterator();
        while (iter.hasNext()) {
            GenerationEvent event = iter.next();
            
            // Check for stuck events
            long age = System.currentTimeMillis() - event.creationTime;
            if (age > GEN_EVENT_TIMEOUT_MS && !event.future.isDone()) {
                LOGGER.warn("Generation event timed out after {}ms: {}", age, event);
                event.future.cancel(true);
                iter.remove();
                continue;
            }
            
            if (event.future.isDone()) {
                // ... existing handling ...
                iter.remove();
            }
        }
    }
}
```

### Immediate Workaround

Disable distant generation in Nether dimension via config (if available), or disable entirely:
```properties
enableDistantGeneration=false
```

### Why This Works
- Bounded queue prevents memory exhaustion
- Timeout prevents indefinite hanging
- Failed events are logged and cleaned up

### How to Verify
1. Enter Nether with fix applied
2. Monitor logs for "Generation event timed out" messages
3. If timeouts occur, generation logic needs Nether-specific fixes

---
*Investigation performed using orthogonal-engineering forensic methodology.*
