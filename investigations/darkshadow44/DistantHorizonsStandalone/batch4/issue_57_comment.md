---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch4, issue-57-comment]
register: audit
---

## Investigation: Restore Commands with Config Flag

Hi @DarkShadow44, this is a feature request to restore `/dh` commands.

### Current State
As identified in #49, the `/dh` commands don't exist - no `ICommand` implementation was found in the codebase. The `PregenManager` has full functionality but no command interface.

### Implementation Plan

**Step 1: Add Config Flag**

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`

```java
public static class Commands {
    public static final ConfigEntry<Boolean> enableCommands = new ConfigEntry.Builder<Boolean>()
        .set(true)
        .comment("Enable /dh admin commands")
        .build();
    
    public static final ConfigEntry<Integer> commandPermissionLevel = new ConfigEntry.Builder<Integer>()
        .set(2)  // OP level
        .comment("Required permission level for /dh commands")
        .build();
}
```

**Step 2: Create Command Class**

**Create:** `src/main/java/com/seibel/distanthorizons/forge/DhCommand.java`

```java
public class DhCommand implements ICommand {
    @Override
    public String getCommandName() { return "dh"; }
    
    @Override
    public int getRequiredPermissionLevel() {
        return Config.Common.Commands.commandPermissionLevel.get();
    }
    
    @Override
    public void processCommand(ICommandSender sender, String[] args) {
        if (args.length == 0) {
            sender.addChatMessage(new ChatComponentText("Usage: /dh pregen <start|stop|status>"));
            return;
        }
        
        if (args[0].equalsIgnoreCase("pregen")) {
            handlePregenCommand(sender, Arrays.copyOfRange(args, 1, args.length));
        }
    }
    
    private void handlePregenCommand(ICommandSender sender, String[] args) {
        PregenManager pregen = ...;  // Get from ServerApi
        
        if (args.length == 0 || args[0].equalsIgnoreCase("status")) {
            String status = pregen.getStatusString();
            sender.addChatMessage(new ChatComponentText(status));
        } else if (args[0].equalsIgnoreCase("start")) {
            // Start pregen
            pregen.startPregen(level, origin, radius);
            sender.addChatMessage(new ChatComponentText("Pregeneration started"));
        } else if (args[0].equalsIgnoreCase("stop")) {
            // Stop pregen
            pregen.stopPregen();
            sender.addChatMessage(new ChatComponentText("Pregeneration stopped"));
        }
    }
}
```

**Step 3: Register Command**

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

```java
@SubscribeEvent
public void serverStarting(FMLServerStartingEvent event) {
    if (Config.Common.Commands.enableCommands.get()) {
        event.registerServerCommand(new DhCommand());
        LOGGER.info("Registered /dh commands");
    }
}
```

---
*Investigation performed using orthogonal-engineering forensic methodology.*
