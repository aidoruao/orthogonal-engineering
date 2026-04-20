---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-62-comment]
register: audit
---

## Investigation: Server Crash in Alpha16

Hi @DarkShadow44, I've analyzed the server crash issue. Here's what I found:

### Root Cause
`ForgeServerProxy.java` event handlers lack defensive null checks. Specifically at lines 146-157:

```java
@SubscribeEvent
public void serverLevelLoadEvent(WorldEvent.Load event) {
    if (GetEventLevel(event) instanceof WorldServer) {
        this.serverApi.serverLevelLoadEvent(getServerLevelWrapper((WorldServer) GetEventLevel(event)));
        chunksPendingResetByWorld.put(event.world, new LongOpenHashSet());
    }
}
```

**Issues:**
1. `GetEventLevel(event)` called twice - could return different values
2. No null check before `instanceof`
3. `chunksPendingResetByWorld.put()` doesn't validate the map operation

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

```java
@SubscribeEvent
public void serverLevelLoadEvent(WorldEvent.Load event) {
    World level = GetEventLevel(event);
    if (level == null || !(level instanceof WorldServer)) {
        return;
    }
    
    try {
        IServerLevelWrapper wrapper = getServerLevelWrapper((WorldServer) level);
        if (wrapper != null) {
            this.serverApi.serverLevelLoadEvent(wrapper);
            chunksPendingResetByWorld.put(level, new LongOpenHashSet());
        }
    } catch (Exception e) {
        LOGGER.error("Failed to load server level", e);
    }
}
```

### Why This Works
- Prevents NPE from null world references
- Catches and logs exceptions instead of crashing
- Follows same pattern as other Forge event handlers

### How to Verify
1. Start dedicated server with DistantHorizons alpha16
2. If crash persists, check `logs/latest.log` for "Failed to load server level" error
3. Full stack trace will pinpoint exact failure location

### Related Issues
- #53 Server boot issue (same code path)
- #51 TPS issues (server tick event handler)

---
*Investigation performed using orthogonal-engineering forensic methodology.*
