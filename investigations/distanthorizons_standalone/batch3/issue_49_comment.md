## Investigation: /dh Pregen Commands Don't Work

Hi @DarkShadow44, I've found the command issue.

### Root Cause
**No command registration exists in the codebase!** 

The `PregenManager` class has all the pregeneration logic:

```java
// PregenManager.java:39-60
public CompletableFuture<Void> startPregen(
        IServerLevelWrapper levelWrapper,
        DhBlockPos2D origin,
        int chunkRadius
)
```

But there's no `ICommand` implementation to connect this to `/dh` commands.

### The Fix

**Create:** `src/main/java/com/seibel/distanthorizons/forge/DhCommand.java`

```java
public class DhCommand implements ICommand {
    @Override
    public String getCommandName() { return "dh"; }
    
    @Override
    public void processCommand(ICommandSender sender, String[] args) {
        if (args.length > 0 && args[0].equalsIgnoreCase("pregen")) {
            if (args[1].equalsIgnoreCase("start")) {
                // Get PregenManager and start
                PregenManager pregen = ...;
                pregen.startPregen(level, origin, radius);
                sender.addChatMessage(new ChatComponentText("Pregeneration started"));
            }
        }
    }
    // ... other required methods
}
```

**Modify:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

```java
@SubscribeEvent
public void serverStarting(FMLServerStartingEvent event) {
    event.registerServerCommand(new DhCommand());
}
```

### Why Commands Are Missing
The mod appears to rely on config-based "chat commands" (SessionConfig.java:35) rather than traditional Minecraft commands. This may be a design choice or incomplete implementation.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
