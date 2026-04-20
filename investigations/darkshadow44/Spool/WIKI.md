---
tags: [investigations, darkshadow44, spool, wiki]
register: audit
---

# Spool - Multithreading for Minecraft 1.7.10

## Overview

Spool is a Forge mod that brings "the joys of multithreading" to Minecraft 1.7.10 by parallelizing server tick processing. It reimplements core tick loops to allow dimensions, chunks, entities, and block updates to execute concurrently across multiple threads.

**Repository:** https://github.com/DarkShadow44/Spool  
**License:** LGPL-3.0  
**Total Files:** 145 Java files (~20,195 LOC)

---

## Threading Architecture

### Three Primary Threading Modes

#### 1. Dimension Threading (Most Stable)
```java
// From MinecraftServerMixin.java
if (ThreadsConfig.isDimensionThreadingEnabled()) {
    KeyedPoolThreadManager dimensionManager = 
        (KeyedPoolThreadManager) SpoolManagerOrchestrator.REGISTERED_THREAD_MANAGERS
            .get(ManagerNames.DIMENSION.ordinal());
    
    for (final int id : ids) {
        dimensionManager.execute(id, this::spool$dimensionTask, id);
    }
}
```

Each Minecraft dimension (Overworld, Nether, End, mod dimensions) ticks on its own thread. This provides excellent isolation and is the most stable threading mode.

**Key Components:**
- `KeyedPoolThreadManager` - Creates per-dimension `ExecutorService` instances
- `spool$dimensionTask()` - Encapsulates all dimension tick work
- `waitUntilAllTasksDone()` - Barrier synchronization at tick end

#### 2. Distance Threading (For Spread-Out Servers)
```java
// From DistanceThreadingUtil.java
public static int getThread(EntityPlayer player) {
    Nearby nearby = DistanceThreadingPlayerUtil.getNearestPlayers(player, false);
    if (nearby.nearby.isEmpty()) {
        // Solo player - assign unique thread
        int hash = DistanceThreadingPlayerUtil.playerHashcode(player);
        keyedPool.addKeyedThread(hash, "Distance-Executor-" + hash);
        playerExecutorMap.put(player, hash);
        return hash;
    }
    // Group nearby players on same thread
    return synchronizePlayersToPlayerExecutor(nearby.nearby, player);
}
```

Groups players by spatial proximity. Players near each other share a thread; distant players get separate threads. Chunks are assigned to the nearest player's thread.

**Key Components:**
- `DistanceThreadingUtil` - Thread assignment logic
- `playerExecutorMap` - Synchronized `Object2IntMap<EntityPlayer>`
- `chunkExecutorMap` - Synchronized `Long2IntMap` for chunk→thread mapping
- `BusLatch` - Event ordering across dimension threads

#### 3. Experimental Threading (Highest Risk)
Uses `ForkJoinPool` with work-stealing for entity and block ticking. Can cause issues with mods expecting synchronous execution.

**Key Components:**
- `ForkThreadManager` - Work-stealing thread pool
- `Entity` and `Block` tasks submitted to pool
- `awaitQuiescence()` for synchronization

---

## Core Thread Safety Mechanisms

### 1. Atomic Chunk State (ConcurrentChunk)

Replaces vanilla `Chunk` field types:

| Vanilla Field | Spool Replacement |
|--------------|-------------------|
| `boolean isTerrainPopulated` | `AtomicBoolean isTerrainPopulated` |
| `boolean isModified` | `AtomicBoolean isModified` |
| `int[] heightMap` | `AtomicIntegerArray heightMap` |
| `ExtendedBlockStorage[] storageArrays` | `AtomicReferenceArray<ConcurrentExtendedBlockStorage> storageArrays` |
| `HashMap chunkTileEntityMap` | `ConcurrentHashMap` |
| `List[] entityLists` | `ObjectLists.synchronize(new ObjectArrayList<>())[]` |

### 2. Atomic Block Storage (ConcurrentExtendedBlockStorage)

```java
public final AtomicInteger blockRefCount = new AtomicInteger(0);
public final AtomicInteger tickRefCount = new AtomicInteger(0);
public final AtomicReference<byte[]> blockLSBArray;
public final AtomicReference<AtomicNibbleArray> blockMSBArray;
public final AtomicReference<AtomicNibbleArray> blockMetadataArray;
```

### 3. Event Bus Synchronization (BusLatch)

Ensures events are processed in order across dimension threads using `Phaser`:

```java
public static void preEvent(Class<? extends Event> event, int dim) {
    for (BusLatch busLatch : perWorldBusLatches.get(dim)) {
        busLatch.pre.forEach(latch -> {
            if (event != latch.event && busLatch.post.event == event) 
                latch.await();  // Wait for prerequisites
        });
    }
}
```

### 4. Thread-Safe Tick Lists (PendingTickList)

Replaces vanilla `TreeSet` + `HashSet` combo:
```java
private final ObjectAVLTreeSet<V> set = new ObjectAVLTreeSet<>();      // Ordering
private final ObjectOpenHashSet<V> hashSet = new ObjectOpenHashSet<>(); // Fast lookup
```

---

## Tick Loop Modifications

### Server Tick Flow

```
Vanilla:
  MinecraftServer.tick()
    → updateTimeLightAndEntities() [Sequential dimension loop]
      → WorldServer.tick() per dimension
        → updateEntities() [Sequential entity loop]
        → tickUpdates() [Sequential block tick]

Spool (Dimension Threading):
  MinecraftServer.tick()
    → updateTimeLightAndEntities() [OVERWRITTEN]
      → Submit dimension tasks to KeyedPoolThreadManager
      → spool$finishTick()
        → waitUntilAllTasksDone() [BARRIER WAIT]
```

### Synchronization Points

1. **End of `updateTimeLightAndEntities`** - Waits for all dimension threads
2. **End of server tick** - Final barrier before next tick begins
3. **Entity update completion** - Within `World.updateEntities()` for experimental mode

---

## Impact on 50ms Tick Budget

### The Standard Assumption
Minecraft assumes a 50ms tick budget (20 TPS). All work must complete within this window.

### Spool's Modifications

**Positive Impacts:**
- **Parallelization** - Dimension/entity/block work distributed across cores
- **Reduced main thread load** - Worker threads handle computation
- **Better CPU utilization** - Multiple cores engaged during tick

**Negative Impacts:**
- **Synchronization overhead** - `waitUntilAllTasksDone()` blocks main thread
- **Contention** - Synchronized collection access adds latency
- **Critical path limitation** - Tick rate limited by slowest worker

### Time Budgets

```java
// From ThreadManagerConfig.java
@Config.DefaultInt(2000)
public static int globalRunningSingleThreadTimeout;     // 2 seconds per task

@Config.DefaultInt(50000)
public static int globalTerminatingSingleThreadTimeout; // 50 seconds for shutdown
```

### Configuration for Tick Budget

| Config | Default | Impact on Budget |
|--------|---------|------------------|
| `allowProcessingDuringSleep` | false | If true, tasks continue during tick sleep phase |
| `dropTasksOnTimeout` | false | If true, drops tasks exceeding timeout |
| `useLoadBalancingDimensionThreadManager` | true | Balances dimension load across limited threads |

---

## Interaction with DistantHorizons

### ConcurrentLinkedQueue Usage Comparison

**DistantHorizons:**
```java
// DH's approach - unbounded queue growth risk
ConcurrentLinkedQueue<ChunkLoadEvent> chunkLoadEvents;
ConcurrentLinkedQueue<ScheduledTask<?>> taskQueue;
```

**Spool:**
```java
// Spool's approach - with overflow handling
public final Queue<Runnable> toExecuteLater = new ConcurrentLinkedQueue<>();

// In waitUntilAllTasksDone():
for (Runnable runnable : toExecuteLater) {
    futures.enqueue(pool.submit(runnable));
}
```

### Key Differences

| Aspect | DistantHorizons | Spool |
|--------|----------------|-------|
| Queue draining | No explicit limit | Processes overflow queue at barrier |
| Synchronization | Fire-and-forget | `waitUntilAllTasksDone()` barrier |
| Timeout handling | None | Configurable per-task timeout |
| Overflow strategy | Unbounded growth | Drains to `toExecuteLater` |

### Thread Safety Guarantees

Spool provides stronger guarantees:
1. **Barrier synchronization** - All tasks complete before tick ends
2. **Timeout detection** - Warns/drops tasks exceeding budget
3. **Deadlock detection** - Spool Watchdog monitors thread health

---

## Configuration Guide

### Recommended Settings

**Small Server (< 10 players, compact base):**
```java
enableDimensionThreading = true    // Stable, good improvement
enableDistanceThreading = false    // Not needed for compact players
enableExperimentalThreading = false // Risk not worth it
```

**Large Server (> 20 players, spread out):**
```java
enableDimensionThreading = true    // Base stability
enableDistanceThreading = true     // Major benefit for spread players
distanceMaxThreads = 16            // Adjust based on CPU
dimensionMaxThreads = 8
```

**Performance Troubleshooting:**
```java
enableSpoolWatchdog = true         // Detect deadlocks
betterTaskProfiling = true         // Debug timing issues
allowProcessingDuringSleep = false // Mod compatibility
```

### Thread Count Guidelines

| Config | Default | Max | Guidance |
|--------|---------|-----|----------|
| `dimensionMaxThreads` | 4 | 64 | ≤ number of dimensions |
| `distanceMaxThreads` | 8 | 64 | ≤ number of player groups |
| `entityThreads` | 4 | 16 | For experimental mode only |
| `blockThreads` | 4 | 16 | For experimental mode only |
| `chunkLoadingThreads` | 1 | 8 | Keep low - world gen issues |

---

## Compatibility Notes

### Mods That May Conflict

**High Risk:**
- Mods accessing `World` from multiple threads without synchronization
- Mods assuming single-threaded chunk access
- Mods with custom entity AI expecting main thread

**Mitigations:**
- `BusLatch` system for event ordering
- `ConcurrentChunk` atomic state
- Synchronized entity/tile entity lists

### Compatible Mods

Spool includes explicit compatibility for:
- **EndlessIDs** - Extended block ID support in `ConcurrentExtendedBlockStorageWrapper`
- **HodgePodge** - Mixin compatibility patches
- **ChunkAPI** - Custom chunk loading hooks

---

## Error Handling

### Common Issues

**1. Pool Timeout Warnings**
```
Pool (dimensionManager) did not finish all tasks in time!
```
- **Cause:** Task execution exceeded `globalRunningSingleThreadTimeout`
- **Solution:** Increase timeout, reduce thread count, or enable `dropTasksOnTimeout`

**2. Executor Map Instability**
```
Player executor map does not match player count!
```
- **Cause:** Player count changed unexpectedly
- **Solution:** Spool auto-rebuilds maps if `DistanceThreadingConfig.resolveConflicts = true`

**3. ConcurrentModificationException**
```
Spool Concurrency Error
```
- **Cause:** Mod accessing unsynchronized collection
- **Solution:** Report to mod author; Spool wraps most vanilla collections

---

## Performance Monitoring

### Debug Commands

Use `/spool` command (if available) or check debug screen (F3):
```
Spool Stats
Experimental threading: false
Distance threading: true
Dimension threading: true
Entity AI threading: true
Chunk threading: false
```

### Crash Reports

Spool registers crash callable providing thread pool status:
```
Spool Info
  dimensionManager
    Pool manager: KeyedPoolThreadManager
    Pool active: true
    Thread count: 3
    Used keys: [0, -1, 1]
```

---

## Implementation Notes

### Why 1.7.10?

Minecraft 1.7.10 is a popular modding version with significant performance limitations that Spool addresses:
- Single-threaded dimension ticking
- Synchronous chunk loading
- No native work-stealing for entity updates

### Key Design Decisions

1. **Overwrite vs Inject** - Core tick methods overwritten for complete control
2. **Atomic vs Synchronized** - Atomic variables preferred for chunk state
3. **Phaser vs CountDownLatch** - Phaser chosen for reusable barrier
4. **NonBlockingHashMapLong** - JCTools used for lock-free keyed pool

---

## References

- `SOURCE_INDEX.json` - Complete file and class index
- `VENDOR_MANIFEST.json` - Dependency information
- `ATTRIBUTION.md` - Credits and licenses
