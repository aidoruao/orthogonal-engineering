---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch3, issue-20-comment]
register: audit
---

## Investigation: Missing LOD Chunks

Hi @DarkShadow44, I've analyzed the missing chunk issue.

### Root Cause
`LodQuadTree` tracks missing positions but generation may fail silently:

```java
// LodQuadTree.java:742-755
CompletableFuture<DataSourceRetrievalResult> genFuture = 
    this.fullDataSourceProvider.queuePositionForRetrieval(missingPos);
genFuture.whenComplete((result, exception) -> {
    if (exception != null) {
        // Returns to missing set on exception
        this.queuedGenerationPosSet.remove(missingPos);
        this.missingGenerationPosSet.add(missingPos);
    }
});
```

**Issues:**
1. No retry limit - may retry infinitely
2. No timeout for generation attempts
3. Failed positions may never get re-queued

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/core/render/QuadTree/LodQuadTree.java`

```java
// Add retry tracking
private final ConcurrentHashMap<Long, Integer> retryCountMap = new ConcurrentHashMap<>();
private static final int MAX_RETRIES = 3;
private static final long GENERATION_TIMEOUT_MS = 60000; // 60 seconds

private void queueGenerationForMissingPos() {
    // ...
    genFuture.whenComplete((result, exception) -> {
        if (exception != null) {
            int retries = retryCountMap.getOrDefault(missingPos, 0) + 1;
            retryCountMap.put(missingPos, retries);
            
            if (retries <= MAX_RETRIES) {
                LOGGER.warn("Generation failed for {} (retry {}/{})", 
                    missingPos, retries, MAX_RETRIES);
                this.queuedGenerationPosSet.remove(missingPos);
                this.missingGenerationPosSet.add(missingPos);
            } else {
                LOGGER.error("Generation failed for {} after {} retries", 
                    missingPos, MAX_RETRIES);
                retryCountMap.remove(missingPos);
            }
        } else {
            retryCountMap.remove(missingPos);
        }
    });
}
```

### Workaround

Press F3+A to reload chunks, which forces re-generation of missing LODs.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
