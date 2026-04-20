---
tags: [investigations, darkshadow44, seasonalhorizons, wiki]
register: audit
---

# SeasonalHorizons Wiki

## Overview

**SeasonalHorizons** is DarkShadow44's original Minecraft 1.7.10 mod that implements seasonal transitions with snow accumulation/thaw mechanics and biome color changes. This is his own creative work (not a fork), making it the best reference for understanding his personal coding patterns and architectural preferences.

## Key Insight: Why This Matters

Unlike his work on DistantHorizons (which involves maintaining compatibility with existing codebases), SeasonalHorizons represents DarkShadow44's **own architectural decisions from scratch**. This reveals:

1. His preferred patterns when unconstrained by existing code
2. How he structures a complete mod lifecycle
3. What he considers "good enough" for production code
4. His tolerance for complexity vs simplicity tradeoffs

---

## Architectural Patterns

### 1. The Proxy Pattern (SidedProxy)

**Pattern:** Standard Forge SidedProxy with extension hierarchy

```java
// Base proxy handles common initialization
public class CommonProxy {
    public void preInit(FMLPreInitializationEvent event) {
        MinecraftForge.EVENT_BUS.register(this);
        FMLCommonHandler.instance().bus().register(this);
        Config.synchronizeConfiguration(event.getSuggestedConfigurationFile());
        NetworkHandler.register();
    }
}

// Client proxy extends and adds client-only features
public class ClientProxy extends CommonProxy {
    @Override
    public void preInit(FMLPreInitializationEvent event) {
        super.preInit(event);
        // Client-only resource loading
    }
}
```

**Key observations:**
- Event bus registration in common proxy (shared)
- Resource loading in client proxy only
- Clean extension rather than duplication

---

### 2. Event Handler Structure

**Pattern:** Self-registration with explicit side guards

```java
@SubscribeEvent
public void onChunkLoad(ChunkEvent.Load event) {
    Chunk chunk = event.getChunk();
    if (event.world.isRemote || !chunk.isChunkLoaded || !chunk.isTerrainPopulated) {
        return;  // Early return pattern
    }
    // ... processing
}
```

**Key observations:**
- Register with `MinecraftForge.EVENT_BUS.register(this)`
- Always check `isRemote` for server-only logic
- Early return guards for invalid states
- Multiple event buses: `MinecraftForge.EVENT_BUS` + `FMLCommonHandler.instance().bus()`

---

### 3. Mixin Patterns

**Naming Convention:** All unique mixin members use `seasonalHorizons$` prefix

```java
@Mixin(WorldServer.class)
public abstract class MixinWorldServer extends World implements IMixinWorldServer {
    @Unique
    private SnowHandler seasonalHorizons$snowHandler;
    
    @Unique
    private SeasonWorldData seasonalHorizons$seasonWorldData;
}
```

**Interface Exposure Pattern:**

```java
// 1. Define interface
public interface IMixinWorldServer {
    SeasonWorldData seasonalHorizons$getSeasonWorldData();
    SnowHandler seasonalHorizons$getSnowHandler();
}

// 2. Implement in mixin
@Mixin(WorldServer.class)
public abstract class MixinWorldServer extends World implements IMixinWorldServer {
    @Override
    public SeasonWorldData seasonalHorizons$getSeasonWorldData() {
        return seasonalHorizons$seasonWorldData;
    }
}

// 3. Cast to use
IMixinWorldServer mixinWorldServer = (IMixinWorldServer) world;
SnowHandler snowHandler = mixinWorldServer.seasonalHorizons$getSnowHandler();
```

**Mixin Types Used:**

| Type | Usage | Example |
|------|-------|---------|
| `@Inject` at `TAIL` | Constructor extensions | `MixinWorldServer.<init>` |
| `@Redirect` | Replace method calls | `MixinWorld.canSnowAtBody` |
| `@WrapMethod` (MixinExtras) | Wrap existing methods | `MixinBiomeGenBase.getFloatTemperature` |
| `@Unique` | Private mixin fields/methods | All injected fields |

---

### 4. Config Handling

**Pattern:** Minimal stub with save-on-change

```java
public class Config {
    public static void synchronizeConfiguration(File configFile) {
        Configuration configuration = new Configuration(configFile);
        // Config options would go here
        if (configuration.hasChanged()) {
            configuration.save();
        }
    }
}
```

**Key observations:**
- Placeholder structure (no actual config options yet)
- Always save if changed
- Called during `preInit`

---

### 5. Error Handling Patterns

**Programming Errors → RuntimeException:**

```java
public static Season getSeasonForWorld(World world) {
    if (world instanceof WorldServer) {
        // ... handle
    }
    if (world instanceof WorldClient) {
        // ... handle  
    }
    throw new RuntimeException("Failed to get season for world type: " + world.getClass());
}
```

**Expected Missing Data → Optional<>:**

```java
public static Optional<Season> getSeasonById(String id) {
    return Arrays.stream(Season.values())
        .filter(x -> x.getId().equals(id))
        .findAny();  // Returns Optional<Season>
}
```

**Null Safety → Early Returns:**

```java
public void handleSnowServerTick(Chunk chunk) {
    if (seasonalHorizons$snowHandler != null) {
        seasonalHorizons$snowHandler.handleSnowServerTick(chunk);
    }
}
```

**Key observations:**
- `RuntimeException` for "should never happen" cases
- `Optional<>` for lookups that may legitimately fail
- Null checks before operations
- Comment explanations for null cases: `// Can happen during initial world generation`

---

### 6. Data Persistence

**World-Saved Data Pattern:**

```java
public class SeasonWorldData extends WorldSavedData {
    public Season season = Season.SPRING_EARLY;
    public int seasonTicks;
    public List<SeasonEvent> snowEvents = new ArrayList<>();
    
    @Override
    public void writeToNBT(NBTTagCompound tag) {
        tag.setByte("season", (byte) season.ordinal());
        tag.setInteger("seasonTicks", seasonTicks);
        // ... more fields
    }
}
```

**Chunk Data Pattern (FalsePattern API):**

```java
public class AdditionalChunkData implements DataManager.ChunkDataManager {
    @Override
    public void writeChunkToNBT(Chunk chunk, NBTTagCompound nbt) {
        long time = ((IMixinChunk) chunk).seasonalHorizons$getLastSaveTime();
        nbt.setLong("seasonLastSaveTime", time);
    }
}
```

**Key observations:**
- NBT tag names are descriptive
- Uses byte for enum ordinals (compact)
- List serialization with helper methods
- Integrates with FalsePattern's Chunk API

---

### 7. Networking Pattern

**SimpleImpl Setup:**

```java
public class NetworkHandler {
    public static final SimpleNetworkWrapper channel = 
        NetworkRegistry.INSTANCE.newSimpleChannel(SeasonalHorizons.MODID);
    
    public static void register() {
        channel.registerMessage(MessageSeasonChange.class, MessageSeasonChange.class, 10, Side.CLIENT);
    }
}
```

**Message Handler (combined class):**

```java
public class MessageSeasonChange implements IMessage, IMessageHandler<MessageSeasonChange, IMessage> {
    public int season;
    public int dimension;
    
    @Override
    public void fromBytes(ByteBuf buf) { /* deserialize */ }
    
    @Override  
    public void toBytes(ByteBuf buf) { /* serialize */ }
    
    @Override
    public IMessage onMessage(MessageSeasonChange message, MessageContext ctx) {
        if (ctx.side == Side.CLIENT) {
            // Process only on client
        }
        return null;  // No response
    }
}
```

**Key observations:**
- Combined IMessage + IMessageHandler (simpler for one-way packets)
- Packet ID 10 (arbitrary, no apparent schema)
- Dimension filtering on client side
- `null` return for no response

---

## Code Quality Indicators

### What DarkShadow44 Values

1. **Deterministic Algorithms**
   - SnowHandler uses hash-based scheduling (not random)
   - Reproducible behavior across sessions

2. **Side Safety**
   - Consistent `isRemote` checks
   - Separate client/server code paths
   - Network packets dimension-aware

3. **Clean Boundaries**
   - Package separation by concern
   - Interface contracts for mixin access
   - Handler classes for complex logic

4. **Minimal Boilerplate**
   - No getters/setters where not needed
   - Direct field access within package
   - Simple enum compositions

5. **Defensive Programming**
   - Null checks before casts
   - Optional for lookups
   - Early returns for edge cases

### What He Tolerates

1. **Incomplete Features**
   - Empty `readFromNBT` in SeasonWorldData
   - Config stub with no options
   - Basic command without full argument handling

2. **Minimal Documentation**
   - Only complex algorithms get comments
   - No Javadoc on most methods
   - Self-documenting code preferred

3. **Static State**
   - `currentSeasonClient` static field
   - Acceptable for client-only state

---

## Patches He'll Likely Accept

Based on his own patterns in this codebase:

### ✅ YES - Aligns with existing patterns

```java
// Following the mixin interface pattern
public interface IMixinNewFeature {
    void seasonalHorizons$newMethod();
}

// Adding config options
public class Config {
    public static boolean enableNewFeature;
    
    public static void synchronizeConfiguration(File configFile) {
        Configuration configuration = new Configuration(configFile);
        enableNewFeature = configuration.getBoolean("enableNewFeature", ...);
        // ...
    }
}

// Using Optional for lookups
public static Optional<NewThing> findThing(String id) {
    return things.stream().filter(t -> t.id.equals(id)).findAny();
}

// Proper side checking
@SubscribeEvent
public void onEvent(SomeEvent event) {
    if (event.world.isRemote) {
        return;
    }
    // ...
}
```

### ⚠️ MAYBE - Needs discussion

- **New dependencies**: He uses FalsePattern libs, but new deps need justification
- **Major refactoring**: Code works; don't fix what isn't broken
- **Breaking changes**: This affects existing worlds

### ❌ NO - Violates his patterns

```java
// Don't use null returns
public Season getSeason(String id) {
    return seasonMap.get(id);  // Returns null if missing - BAD
}

// Don't forget @Unique
@Mixin(SomeClass.class)
public class MixinSomeClass {
    private Object myField;  // BAD - not @Unique
}

// Don't skip side checks
@SubscribeEvent
public void onTick(TickEvent event) {
    // Server logic without checking side - BAD
}
```

---

## SnowHandler Deep Dive

The most complex code in the mod - shows his approach to performance-critical systems:

### Algorithm Overview

1. **Deterministic Scheduling**: Uses hash mixing to create reproducible block update schedules
2. **Event Tracking**: Maintains snow/thaw event lists with limits
3. **Sparse Arrays**: Uses `ScheduleEntry[]` instead of `int[]` for iteration efficiency
4. **Chunk-based Processing**: Updates spread across ticks to avoid lag spikes

### Key Technique: Hash Mixing

```java
private static int mix(int x) {
    x ^= x >>> 16;
    x *= 0x85ebca6b;
    x ^= x >>> 13;
    x *= 0xc2b2ae35;
    x ^= x >>> 16;
    return x;
}
```

This is MurmurHash3's finalizer - provides good distribution for scheduling.

---

## Summary for Contributors

**DarkShadow44's Style Summary:**

| Aspect | Preference |
|--------|------------|
| Architecture | Clean separation, proxy pattern |
| Mixins | @Unique naming, interface exposure |
| Error handling | RuntimeException for bugs, Optional for lookups |
| Documentation | Minimal, code should be self-explanatory |
| Complexity | Functional but not over-engineered |
| Side safety | Explicit isRemote checks everywhere |
| Dependencies | Accepts FalsePattern libs, others need justification |

**Bottom line**: He values working code that follows established patterns over elaborate abstractions. Keep it simple, follow his conventions, and don't break existing worlds.
