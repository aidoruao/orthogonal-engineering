---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch3, issue-50-comment]
register: audit
---

## Investigation: Slow Rate Limiting

Hi @DarkShadow44, I've analyzed the rate limiting issue.

### Root Cause
`AbstractFullDataNetworkRequestQueue` uses rate limiting for multiplayer sync:

```java
// AbstractFullDataNetworkRequestQueue.java:168-171
if (!this.rateLimiter.tryAcquire()) {
    return false;  // Request blocked by rate limit
}
```

The rate limit may be too conservative for good performance.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`

Add configurable rate limit:

```java
public static class Multiplayer {
    public static final ConfigEntry<Integer> dataSyncRateLimit = new ConfigEntry<>(100);
    // Requests per second
}
```

**File:** `src/main/java/com/seibel/distanthorizons/core/multiplayer/client/SyncOnLoadRequestQueue.java`

```java
@Override
protected int getRequestRateLimit() {
    // Use config value instead of hardcoded
    return Config.Common.Multiplayer.dataSyncRateLimit.get();
}
```

### Immediate Workaround

Increase rate limit in config if option exists, or modify `SessionConfig` to increase limits.

### Why This Works
- Allows users to tune for their network speed
- Higher rates for LAN, lower for WAN

---
*Investigation performed using orthogonal-engineering forensic methodology.*
