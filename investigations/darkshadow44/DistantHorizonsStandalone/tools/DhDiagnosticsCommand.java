/*
 * DhDiagnosticsCommand.java
 * 
 * Forge server command for DistantHorizonsStandalone real-time diagnostics.
 * 
 * Usage: Add to ForgeServerProxy.java:
 *   @EventHandler
 *   public void onServerStarting(FMLServerStartingEvent event) {
 *       DhDiagnosticsCommand.register(event);  // Registers as /dhdiag
 *   }
 * 
 * In-game command: /dhdiag diagnostics
 * 
 * Outputs:
 *   - Chunk event queue size
 *   - Task queue size  
 *   - Last tick duration
 *   - Events processed last tick
 *   - Status: OK / WARNING / CRITICAL
 * 
 * Based on ForgeServerProxy.java from commit 1abcd98.
 */

package com.seibel.distanthorizons.forge;

import net.minecraft.command.CommandBase;
import net.minecraft.command.ICommandSender;
import net.minecraft.util.ChatComponentText;
import net.minecraft.util.EnumChatFormatting;
import cpw.mods.fml.common.event.FMLServerStartingEvent;

import java.lang.reflect.Field;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReferenceArray;

/**
 * Server command for DH performance diagnostics.
 * 
 * This command uses reflection to access ForgeServerProxy's private fields
 * and report real-time queue depths and tick timing.
 * 
 * INSTALLATION: Requires 3 lines added to ForgeServerProxy.java:
 *   1. DhDiagnosticsCommand.setProxyInstance(this); in constructor
 *   2. DhDiagnosticsCommand.register(event); in onServerStarting()
 *   3. (Optional) DhDiagnosticsCommand.recordTickTiming() in serverTickEvent()
 * 
 * Default command is /dhdiag to avoid collision with DH's existing /dh command.
 */
public class DhDiagnosticsCommand extends CommandBase {
    
    // Default to "dhdiag" to avoid collision with DH's existing "/dh" command
    // If you prefer "/dh diagnostics", use registerWithName(event, "dh")
    private static final String COMMAND_NAME = "dhdiag";
    private static final String SUBCOMMAND = "diagnostics";
    
    // Thresholds for status determination
    private static final int CHUNK_QUEUE_WARNING = 100;
    private static final int CHUNK_QUEUE_CRITICAL = 1000;
    private static final int TASK_QUEUE_WARNING = 50;
    private static final int TASK_QUEUE_CRITICAL = 500;
    private static final long TICK_TIME_WARNING_MS = 10;  // 10ms (66% of 15ms budget)
    private static final long TICK_TIME_CRITICAL_MS = 15; // 15ms (100% of budget)
    
    // Reflection fields (cached after first access)
    private static Field chunkLoadEventsField;
    private static Field taskQueueField;
    private static Object forgeServerProxyInstance;
    
    // Track tick timing (would be populated by ForgeServerProxy instrumentation)
    private static final AtomicLong lastTickDurationNanos = new AtomicLong(0);
    private static final AtomicLong lastTickEventsProcessed = new AtomicLong(0);
    
    // Phase 4: Tick history ring buffer (last 20 ticks)
    private static final int HISTORY_SIZE = 20;
    private static final AtomicReferenceArray<Long> tickHistory = new AtomicReferenceArray<>(HISTORY_SIZE);
    private static final AtomicInteger historyIndex = new AtomicInteger(0);
    
    // Phase 4: Queue growth rate tracking
    private static final AtomicLong lastChunkQueueSize = new AtomicLong(-1);
    private static final AtomicLong lastTaskQueueSize = new AtomicLong(-1);
    private static final AtomicLong lastSampleTime = new AtomicLong(0);
    
    /**
     * Registers this command as "/dhdiag" with the server.
     * Call from FMLServerStartingEvent handler.
     * 
     * Default is "dhdiag" to avoid collision with DH's existing "/dh" command.
     */
    public static void register(FMLServerStartingEvent event) {
        event.registerServerCommand(new DhDiagnosticsCommand());
    }
    
    /**
     * Registers with a custom command name.
     * Use this if you want "/dh" instead of "/dhdiag".
     * WARNING: DH already has a "/dh" command (issues #49, #57) - collision likely.
     * 
     * @param event The server starting event
     * @param name The command name (e.g., "dh" for "/dh diagnostics")
     */
    public static void registerWithName(FMLServerStartingEvent event, String name) {
        event.registerServerCommand(new DhDiagnosticsCommand(name));
    }
    
    private final String commandName;
    
    public DhDiagnosticsCommand() {
        this.commandName = COMMAND_NAME;
    }
    
    public DhDiagnosticsCommand(String name) {
        this.commandName = name;
    }
    
    /**
     * Sets the ForgeServerProxy instance for reflection access.
     * Call this from ForgeServerProxy constructor or init.
     */
    public static void setProxyInstance(Object instance) {
        forgeServerProxyInstance = instance;
        cacheReflectionFields(instance.getClass());
    }
    
    /**
     * Records tick timing data.
     * Call this from serverTickEvent() to enable timing reports.
     */
    public static void recordTickTiming(long durationNanos, int eventsProcessed) {
        lastTickDurationNanos.set(durationNanos);
        lastTickEventsProcessed.set(eventsProcessed);
        
        // Phase 4: Add to history ring buffer
        int idx = historyIndex.getAndUpdate(i -> (i + 1) % HISTORY_SIZE);
        tickHistory.set(idx, durationNanos);
    }
    
    /**
     * Records queue sizes for growth rate calculation.
     * Call this from serverTickEvent() to enable rate tracking.
     */
    public static void recordQueueSizes(int chunkQueueSize, int taskQueueSize) {
        lastChunkQueueSize.set(chunkQueueSize);
        lastTaskQueueSize.set(taskQueueSize);
        lastSampleTime.set(System.nanoTime());
    }
    
    @Override
    public String getCommandName() {
        return commandName;
    }
    
    @Override
    public String getCommandUsage(ICommandSender sender) {
        return "/" + commandName + " <diagnostics|history|config|queue-rate> - Show DH performance diagnostics";
    }
    
    @Override
    public int getRequiredPermissionLevel() {
        return 2; // OP level 2 (can use most commands)
    }
    
    @Override
    public void processCommand(ICommandSender sender, String[] args) {
        if (args.length == 0) {
            sendMessage(sender, "Usage: " + getCommandUsage(sender), EnumChatFormatting.RED);
            return;
        }
        
        String subcommand = args[0].toLowerCase();
        
        switch (subcommand) {
            case "diagnostics":
                handleDiagnostics(sender);
                break;
            case "history":
                handleHistory(sender);
                break;
            case "config":
                handleConfig(sender);
                break;
            case "queue-rate":
                handleQueueRate(sender);
                break;
            default:
                sendMessage(sender, "Unknown subcommand: " + subcommand, EnumChatFormatting.RED);
                sendMessage(sender, "Usage: " + getCommandUsage(sender), EnumChatFormatting.RED);
        }
    }
    
    /**
     * Handles the 'diagnostics' subcommand.
     */
    private void handleDiagnostics(ICommandSender sender) {
        sendMessage(sender, "=== DistantHorizons Diagnostics ===", EnumChatFormatting.GREEN);
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        
        // Get queue information via reflection
        QueueInfo queueInfo = getQueueInfo();
        
        // Determine status
        Status status = determineStatus(queueInfo);
        
        // Report chunk event queue
        String chunkStatus = formatStatus(queueInfo.chunkQueueSize, 
            CHUNK_QUEUE_WARNING, CHUNK_QUEUE_CRITICAL);
        sendMessage(sender, 
            String.format("Chunk Event Queue: %d events %s", 
                queueInfo.chunkQueueSize, chunkStatus),
            getStatusColor(queueInfo.chunkQueueSize, 
                CHUNK_QUEUE_WARNING, CHUNK_QUEUE_CRITICAL));
        
        // Report task queue
        String taskStatus = formatStatus(queueInfo.taskQueueSize,
            TASK_QUEUE_WARNING, TASK_QUEUE_CRITICAL);
        sendMessage(sender,
            String.format("Task Queue: %d tasks %s",
                queueInfo.taskQueueSize, taskStatus),
            getStatusColor(queueInfo.taskQueueSize,
                TASK_QUEUE_WARNING, TASK_QUEUE_CRITICAL));
        
        // Report tick timing if available
        long tickDurationMs = lastTickDurationNanos.get() / 1_000_000;
        if (tickDurationMs > 0) {
            String timeStatus = formatStatus(tickDurationMs,
                TICK_TIME_WARNING_MS, TICK_TIME_CRITICAL_MS);
            sendMessage(sender,
                String.format("Last Tick: %d ms %s (budget: 15ms)",
                    tickDurationMs, timeStatus),
                getStatusColor(tickDurationMs,
                    TICK_TIME_WARNING_MS, TICK_TIME_CRITICAL_MS));
            
            long eventsProcessed = lastTickEventsProcessed.get();
            sendMessage(sender,
                String.format("Events Processed: %d", eventsProcessed),
                EnumChatFormatting.WHITE);
        } else {
            sendMessage(sender, "Tick timing: Not available (instrumentation required)",
                EnumChatFormatting.GRAY);
        }
        
        // Overall status
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, 
            String.format("Overall Status: %s", status.name()),
            status.color);
        
        // Recommendations
        if (status == Status.CRITICAL) {
            sendMessage(sender, "", EnumChatFormatting.WHITE);
            sendMessage(sender, "RECOMMENDATIONS:", EnumChatFormatting.YELLOW);
            sendMessage(sender, "1. Reduce maxGenerationRequestDistance in config",
                EnumChatFormatting.YELLOW);
            sendMessage(sender, "2. Restart server to clear queues",
                EnumChatFormatting.YELLOW);
            sendMessage(sender, "3. Consider pre-generating chunks",
                EnumChatFormatting.YELLOW);
        } else if (status == Status.WARNING) {
            sendMessage(sender, "", EnumChatFormatting.WHITE);
            sendMessage(sender, "Monitor queue sizes - may degrade over time",
                EnumChatFormatting.YELLOW);
        }
        
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, "=================================", EnumChatFormatting.GREEN);
    }
    
    /**
     * Handles the 'history' subcommand.
     * Shows tick timing history (last 20 ticks).
     */
    private void handleHistory(ICommandSender sender) {
        sendMessage(sender, "=== Tick Timing History (last 20 ticks) ===", EnumChatFormatting.GREEN);
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        
        // Collect non-null values
        long[] values = new long[HISTORY_SIZE];
        int count = 0;
        long sum = 0;
        long min = Long.MAX_VALUE;
        long max = Long.MIN_VALUE;
        
        for (int i = 0; i < HISTORY_SIZE; i++) {
            Long val = tickHistory.get(i);
            if (val != null) {
                values[count++] = val;
                sum += val;
                if (val < min) min = val;
                if (val > max) max = val;
            }
        }
        
        if (count == 0) {
            sendMessage(sender, "No history available. Instrumentation required.", EnumChatFormatting.GRAY);
            return;
        }
        
        // Calculate statistics
        double avgMs = (sum / count) / 1_000_000.0;
        double minMs = min / 1_000_000.0;
        double maxMs = max / 1_000_000.0;
        
        // Calculate p95
        java.util.Arrays.sort(values, 0, count);
        int p95Index = (int)(count * 0.95);
        double p95Ms = values[p95Index] / 1_000_000.0;
        
        sendMessage(sender, String.format("Samples: %d", count), EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("Min: %.2f ms", minMs), EnumChatFormatting.GREEN);
        sendMessage(sender, String.format("Max: %.2f ms", maxMs), 
            maxMs > 50 ? EnumChatFormatting.RED : (maxMs > 15 ? EnumChatFormatting.YELLOW : EnumChatFormatting.GREEN));
        sendMessage(sender, String.format("Avg: %.2f ms", avgMs), EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("P95: %.2f ms", p95Ms), 
            p95Ms > 50 ? EnumChatFormatting.RED : (p95Ms > 15 ? EnumChatFormatting.YELLOW : EnumChatFormatting.GREEN));
        
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, "Recent tick times (ms):", EnumChatFormatting.GRAY);
        
        // Show last 10 values
        StringBuilder sb = new StringBuilder();
        int startIdx = Math.max(0, count - 10);
        for (int i = startIdx; i < count; i++) {
            if (i > startIdx) sb.append(", ");
            sb.append(String.format("%.1f", values[i] / 1_000_000.0));
        }
        sendMessage(sender, sb.toString(), EnumChatFormatting.WHITE);
    }
    
    /**
     * Handles the 'config' subcommand.
     * Reads maxGenerationRequestDistance and computes area.
     */
    private void handleConfig(ICommandSender sender) {
        sendMessage(sender, "=== DH Configuration Analysis ===", EnumChatFormatting.GREEN);
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        
        // Try to read config via reflection
        Integer maxGenDistance = readConfigValue("maxGenerationRequestDistance");
        Integer maxChunkRadius = readConfigValue("generationMaxChunkRadius");
        
        if (maxGenDistance != null) {
            double area = Math.PI * maxGenDistance * maxGenDistance;
            double area10Players = area * 10;
            
            sendMessage(sender, "maxGenerationRequestDistance: " + maxGenDistance, EnumChatFormatting.WHITE);
            sendMessage(sender, String.format("Generation area per player: π × %d² = %.0f blocks²", 
                maxGenDistance, area), EnumChatFormatting.WHITE);
            sendMessage(sender, String.format("With 10 players: %.0f blocks²", area10Players), 
                area10Players > 10_000_000 ? EnumChatFormatting.YELLOW : EnumChatFormatting.WHITE);
            
            // Estimate events (assume 1 event per 1000 blocks²)
            int estimatedEvents = (int)(area / 1000);
            sendMessage(sender, String.format("Estimated events per player: ~%d", estimatedEvents), 
                EnumChatFormatting.GRAY);
        } else {
            sendMessage(sender, "maxGenerationRequestDistance: Not available via reflection", EnumChatFormatting.GRAY);
        }
        
        if (maxChunkRadius != null) {
            sendMessage(sender, "generationMaxChunkRadius: " + maxChunkRadius, EnumChatFormatting.WHITE);
            if (maxChunkRadius == 0) {
                sendMessage(sender, "Warning: 0 means unbounded generation", EnumChatFormatting.YELLOW);
            }
        } else {
            sendMessage(sender, "generationMaxChunkRadius: Not available", EnumChatFormatting.GRAY);
        }
        
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, "Recommendation: maxGenerationRequestDistance ≤ 1024", EnumChatFormatting.GREEN);
    }
    
    /**
     * Attempts to read a config value via reflection.
     */
    private Integer readConfigValue(String fieldName) {
        try {
            // Try common config class locations
            String[] classNames = {
                "com.seibel.distanthorizons.core.config.Config",
                "com.seibel.distanthorizons.config.Config",
                "com.seibel.distanthorizons.Config"
            };
            
            for (String className : classNames) {
                try {
                    Class<?> configClass = Class.forName(className);
                    Field field = configClass.getDeclaredField(fieldName);
                    field.setAccessible(true);
                    return (Integer) field.get(null);
                } catch (ClassNotFoundException | NoSuchFieldException e) {
                    // Try next class
                }
            }
        } catch (Exception e) {
            // Reflection failed
        }
        return null;
    }
    
    /**
     * Handles the 'queue-rate' subcommand.
     * Shows queue growth rate.
     */
    private void handleQueueRate(ICommandSender sender) {
        sendMessage(sender, "=== Queue Growth Rate ===", EnumChatFormatting.GREEN);
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        
        QueueInfo current = getQueueInfo();
        long currentTime = System.nanoTime();
        long lastTime = lastSampleTime.get();
        
        if (lastTime == 0 || lastChunkQueueSize.get() < 0) {
            // First sample, store and report
            recordQueueSizes(current.chunkQueueSize, current.taskQueueSize);
            sendMessage(sender, "Initial sample recorded.", EnumChatFormatting.GRAY);
            sendMessage(sender, String.format("Chunk Queue: %d events", current.chunkQueueSize), EnumChatFormatting.WHITE);
            sendMessage(sender, String.format("Task Queue: %d tasks", current.taskQueueSize), EnumChatFormatting.WHITE);
            sendMessage(sender, "", EnumChatFormatting.GRAY);
            sendMessage(sender, "Run /dhdiag queue-rate again in a few ticks", EnumChatFormatting.GRAY);
            return;
        }
        
        long timeDeltaMs = (currentTime - lastTime) / 1_000_000;
        if (timeDeltaMs < 1) timeDeltaMs = 1; // Prevent division by zero
        
        long chunkDelta = current.chunkQueueSize - lastChunkQueueSize.get();
        long taskDelta = current.taskQueueSize - lastTaskQueueSize.get();
        
        double chunkRate = (double) chunkDelta * 1000.0 / timeDeltaMs; // events per second
        double taskRate = (double) taskDelta * 1000.0 / timeDeltaMs;   // tasks per second
        
        sendMessage(sender, String.format("Time delta: %d ms", timeDeltaMs), EnumChatFormatting.GRAY);
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        
        // Chunk queue rate
        String chunkTrend;
        EnumChatFormatting chunkColor;
        if (chunkRate > 10) {
            chunkTrend = "GROWING (backlog increasing)";
            chunkColor = EnumChatFormatting.RED;
        } else if (chunkRate > 0) {
            chunkTrend = "SLOW GROWTH";
            chunkColor = EnumChatFormatting.YELLOW;
        } else if (chunkRate < -10) {
            chunkTrend = "SHRINKING (draining)";
            chunkColor = EnumChatFormatting.GREEN;
        } else if (chunkRate < 0) {
            chunkTrend = "SLOW DRAIN";
            chunkColor = EnumChatFormatting.GREEN;
        } else {
            chunkTrend = "STABLE";
            chunkColor = EnumChatFormatting.GREEN;
        }
        
        sendMessage(sender, "Chunk Event Queue:", EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("  Current: %d events", current.chunkQueueSize), EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("  Rate: %+.1f events/sec", chunkRate), chunkColor);
        sendMessage(sender, String.format("  Trend: %s", chunkTrend), chunkColor);
        
        // Task queue rate
        String taskTrend;
        EnumChatFormatting taskColor;
        if (taskRate > 10) {
            taskTrend = "GROWING";
            taskColor = EnumChatFormatting.RED;
        } else if (taskRate > 0) {
            taskTrend = "SLOW GROWTH";
            taskColor = EnumChatFormatting.YELLOW;
        } else if (taskRate < -10) {
            taskTrend = "SHRINKING";
            taskColor = EnumChatFormatting.GREEN;
        } else if (taskRate < 0) {
            taskTrend = "SLOW DRAIN";
            taskColor = EnumChatFormatting.GREEN;
        } else {
            taskTrend = "STABLE";
            taskColor = EnumChatFormatting.GREEN;
        }
        
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, "Task Queue:", EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("  Current: %d tasks", current.taskQueueSize), EnumChatFormatting.WHITE);
        sendMessage(sender, String.format("  Rate: %+.1f tasks/sec", taskRate), taskColor);
        sendMessage(sender, String.format("  Trend: %s", taskTrend), taskColor);
        
        // Update stored values
        recordQueueSizes(current.chunkQueueSize, current.taskQueueSize);
        
        sendMessage(sender, "", EnumChatFormatting.WHITE);
        sendMessage(sender, "Interpretation:", EnumChatFormatting.GRAY);
        sendMessage(sender, "GROWING = queue building up, will cause lag", EnumChatFormatting.GRAY);
        sendMessage(sender, "STABLE/DRAINING = queue under control", EnumChatFormatting.GRAY);
    }
    
    /**
     * Data class for queue information.
     */
    private static class QueueInfo {
        final int chunkQueueSize;
        final int taskQueueSize;
        
        QueueInfo(int chunk, int task) {
            this.chunkQueueSize = chunk;
            this.taskQueueSize = task;
        }
    }
    
    /**
     * Status levels for diagnostics.
     */
    private enum Status {
        OK(EnumChatFormatting.GREEN),
        WARNING(EnumChatFormatting.YELLOW),
        CRITICAL(EnumChatFormatting.RED);
        
        final EnumChatFormatting color;
        
        Status(EnumChatFormatting color) {
            this.color = color;
        }
    }
    
    /**
     * Gets current queue sizes via reflection.
     * 
     * PERFORMANCE NOTE: ConcurrentLinkedQueue.size() is O(n) - it traverses the
     * entire queue to count elements. At 10,000+ events, this itself could add
     * measurable latency to the tick. This is a diagnostic trade-off: we accept
     * the O(n) cost for visibility into the queue state. For production use,
     * consider sampling (call size() every N ticks instead of every tick).
     */
    private QueueInfo getQueueInfo() {
        int chunkSize = 0;
        int taskSize = 0;
        
        try {
            if (forgeServerProxyInstance != null) {
                // Get chunkLoadEvents queue
                if (chunkLoadEventsField == null) {
                    cacheReflectionFields(forgeServerProxyInstance.getClass());
                }
                
                if (chunkLoadEventsField != null) {
                    @SuppressWarnings("unchecked")
                    ConcurrentLinkedQueue<Object> chunkQueue = 
                        (ConcurrentLinkedQueue<Object>) chunkLoadEventsField.get(forgeServerProxyInstance);
                    if (chunkQueue != null) {
                        // O(n) operation - see method javadoc for performance note
                        chunkSize = chunkQueue.size();
                    }
                }
                
                // Get taskQueue
                if (taskQueueField != null) {
                    @SuppressWarnings("unchecked")
                    ConcurrentLinkedQueue<Object> taskQueue =
                        (ConcurrentLinkedQueue<Object>) taskQueueField.get(forgeServerProxyInstance);
                    if (taskQueue != null) {
                        // O(n) operation - see method javadoc for performance note
                        taskSize = taskQueue.size();
                    }
                }
            }
        } catch (Exception e) {
            // Reflection failed - queues will show as 0
            // Graceful degradation: report zeros rather than crashing
        }
        
        return new QueueInfo(chunkSize, taskSize);
    }
    
    /**
     * Caches reflection fields for performance.
     */
    private static void cacheReflectionFields(Class<?> clazz) {
        try {
            // Look for chunkLoadEvents field
            try {
                chunkLoadEventsField = clazz.getDeclaredField("chunkLoadEvents");
                chunkLoadEventsField.setAccessible(true);
            } catch (NoSuchFieldException e) {
                // Try parent class
                if (clazz.getSuperclass() != null) {
                    cacheReflectionFields(clazz.getSuperclass());
                    return;
                }
            }
            
            // Look for taskQueue field
            try {
                taskQueueField = clazz.getDeclaredField("taskQueue");
                taskQueueField.setAccessible(true);
            } catch (NoSuchFieldException e) {
                // Field may not exist in all versions
            }
        } catch (Exception e) {
            // Reflection setup failed - will use fallback values
        }
    }
    
    /**
     * Determines overall status based on queue sizes.
     */
    private Status determineStatus(QueueInfo info) {
        long tickMs = lastTickDurationNanos.get() / 1_000_000;
        
        // Critical if any metric exceeds critical threshold
        if (info.chunkQueueSize >= CHUNK_QUEUE_CRITICAL ||
            info.taskQueueSize >= TASK_QUEUE_CRITICAL ||
            tickMs >= TICK_TIME_CRITICAL_MS) {
            return Status.CRITICAL;
        }
        
        // Warning if any metric exceeds warning threshold
        if (info.chunkQueueSize >= CHUNK_QUEUE_WARNING ||
            info.taskQueueSize >= TASK_QUEUE_WARNING ||
            tickMs >= TICK_TIME_WARNING_MS) {
            return Status.WARNING;
        }
        
        return Status.OK;
    }
    
    /**
     * Formats a status indicator for a value.
     */
    private String formatStatus(long value, long warning, long critical) {
        if (value >= critical) return "[CRITICAL]";
        if (value >= warning) return "[WARNING]";
        return "[OK]";
    }
    
    /**
     * Gets the appropriate color for a value.
     */
    private EnumChatFormatting getStatusColor(long value, long warning, long critical) {
        if (value >= critical) return EnumChatFormatting.RED;
        if (value >= warning) return EnumChatFormatting.YELLOW;
        return EnumChatFormatting.GREEN;
    }
    
    /**
     * Sends a chat message to the command sender.
     */
    private void sendMessage(ICommandSender sender, String message, EnumChatFormatting color) {
        ChatComponentText component = new ChatComponentText(message);
        component.getChatStyle().setColor(color);
        sender.addChatMessage(component);
    }
    
}

/*
 * INTEGRATION INSTRUCTIONS:
 * 
 * REQUIRED MODIFICATIONS (3 lines to add):
 * 
 * 1. Copy this file to: src/main/java/com/seibel/distanthorizons/forge/
 * 
 * 2. In ForgeServerProxy.java constructor, add:
 *    DhDiagnosticsCommand.setProxyInstance(this);
 * 
 * 3. In ForgeServerProxy.java, add event handler:
 *    @EventHandler
 *    public void onServerStarting(FMLServerStartingEvent event) {
 *        DhDiagnosticsCommand.register(event);  // Uses /dhdiag
 *        // (register() defaults to /dhdiag — see COMMAND_NAME constant)
 *        // OR: DhDiagnosticsCommand.registerWithName(event, "dh");  // Uses /dh
 *    }
 * 
 * OPTIONAL (for tick timing):
 * 4. In serverTickEvent(), add timing instrumentation:
 *    long tickStart = System.nanoTime();
 *    // ... existing tick handler code ...
 *    long tickDuration = System.nanoTime() - tickStart;
 *    DhDiagnosticsCommand.recordTickTiming(tickDuration, eventsProcessed);
 * 
 * 5. Build and run. In-game, use: /dhdiag diagnostics
 *    (If you used registerWithName(event, "dh"), then use: /dh diagnostics)
 */
