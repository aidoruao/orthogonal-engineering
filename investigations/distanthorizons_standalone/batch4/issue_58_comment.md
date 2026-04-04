## Investigation: Dimension White/Blacklist System

Hi @DarkShadow44, this is a feature request for dimension filtering.

### Current Behavior
DH initializes for every dimension/world without filtering.

### Requested Behavior
Allow users to specify which dimensions should use DH via whitelist or blacklist.

### Implementation

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`

```java
public static class WorldFilter {
    public static final ConfigEntry<String> mode = new ConfigEntry.Builder<String>()
        .set("DISABLED")  // DISABLED, WHITELIST, BLACKLIST
        .comment("Dimension filter mode: DISABLED, WHITELIST, or BLACKLIST")
        .build();
    
    public static final ConfigEntry<List<String>> whitelist = new ConfigEntry.Builder<List<String>>()
        .set(Arrays.asList("Overworld"))
        .comment("Dimensions to enable DH for (if mode=WHITELIST)")
        .build();
    
    public static final ConfigEntry<List<String>> blacklist = new ConfigEntry.Builder<List<String>>()
        .set(Arrays.asList())
        .comment("Dimensions to disable DH for (if mode=BLACKLIST)")
        .build();
}
```

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

```java
@SubscribeEvent
public void serverLevelLoadEvent(WorldEvent.Load event) {
    World level = GetEventLevel(event);
    if (!(level instanceof WorldServer)) return;
    
    // Check dimension filter
    String dimName = level.provider.getDimensionName();
    if (!isDimensionAllowed(dimName)) {
        LOGGER.info("Skipping DH for dimension: " + dimName);
        return;
    }
    
    this.serverApi.serverLevelLoadEvent(...);
}

private boolean isDimensionAllowed(String dimName) {
    String mode = Config.Common.WorldFilter.mode.get();
    if (mode.equals("DISABLED")) return true;
    
    List<String> list = mode.equals("WHITELIST") 
        ? Config.Common.WorldFilter.whitelist.get()
        : Config.Common.WorldFilter.blacklist.get();
    
    boolean inList = list.contains(dimName);
    return mode.equals("WHITELIST") ? inList : !inList;
}
```

---
*Investigation performed using orthogonal-engineering forensic methodology.*
