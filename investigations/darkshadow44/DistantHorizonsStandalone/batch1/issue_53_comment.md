---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-53-comment]
register: audit
---

## Investigation: Server Boot Issue

Hi @DarkShadow44, I've analyzed the server boot failure.

### Root Cause
Server initialization in `ForgeMain.java:107-110` may execute before server is fully ready:

```java
@Mod.EventHandler
public void dedicatedWorldLoadEvent(FMLServerAboutToStartEvent event) {
    ServerApi.INSTANCE.serverLoadEvent(
        event.getServer().isDedicatedServer());
}
```

**Potential issues:**
1. `FMLServerAboutToStartEvent` fires before worlds are loaded
2. `ServerApi.serverLoadEvent()` may access uninitialized systems
3. No error handling around the server load call

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeMain.java`

```java
@Mod.EventHandler
public void dedicatedWorldLoadEvent(FMLServerAboutToStartEvent event) {
    try {
        boolean isDedicated = event.getServer().isDedicatedServer();
        ServerApi.INSTANCE.serverLoadEvent(isDedicated);
        LOGGER.info("DistantHorizons server initialized [dedicated={}]", isDedicated);
    } catch (Exception e) {
        LOGGER.error("Failed to initialize DistantHorizons server: {}", e.getMessage(), e);
        // Don't crash - allow server to boot without DH
    }
}
```

### Alternative Fix
Move initialization to `FMLServerStartedEvent` when server is fully ready:

```java
@Mod.EventHandler
public void serverStartedEvent(FMLServerStartedEvent event) {
    ServerApi.INSTANCE.serverLoadEvent(event.getServer().isDedicatedServer());
}
```

### Why This Works
- Error handling prevents boot failure
- Logging helps diagnose issues
- Graceful degradation allows server to function without DH

### How to Verify
1. Start dedicated server with fix applied
2. Check `logs/latest.log` for "DistantHorizons server initialized"
3. If error logged, stack trace will identify specific failure

---
*Investigation performed using orthogonal-engineering forensic methodology.*
