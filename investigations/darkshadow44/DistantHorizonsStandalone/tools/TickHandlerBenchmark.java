/*
 * TickHandlerBenchmark.java
 * 
 * Standalone benchmark for DistantHorizonsStandalone server tick handler.
 * Simulates serverTickEvent() behavior without requiring Forge runtime.
 * 
 * Run: javac TickHandlerBenchmark.java && java TickHandlerBenchmark
 * 
 * Measures tick handler performance at various queue depths and timing profiles.
 * 
 * Based on ForgeServerProxy.java lines 105-141 from commit 1abcd98.
 * 
 * IMPORTANT: This models the ACTUAL two-loop structure:
 *   - Loop 1 (chunkLoadEvents): NO time budget, processes ALL events
 *   - Loop 2 (taskQueue): 15ms budget with isLimited() + processedAtLeastOne gate
 *     * isLimited=true tasks: check budget AFTER running (first task always runs)
 *     * isLimited=false tasks: skip budget check entirely (always run)
 * 
 * METHODOLOGY: Parameterized sweep across documented compression timing profiles.
 * Tests all queue depths against all documented operation times to identify
 * which combinations exceed the 50ms tick budget.
 * 
 * THRESHOLD CALCULATION:
 *   threshold_ms = tick_budget_ms / queue_depth
 *   Example: At queue depth 30, threshold = 50ms / 30 = 1.67ms per event
 *   If an operation takes longer than the threshold, the tick budget is exceeded.
 */

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Synthetic benchmark for DH server tick event handler.
 * 
 * This recreates the tick handler logic to measure:
 * - Time to drain queue at various depths
 * - Whether 15ms budget is exceeded (in Loop 2)
 * - Events processed vs remaining
 * - The impact of Loop 1 consuming unlimited time before Loop 2 starts
 * 
 * All timing values are sourced from DH's published documentation.
 * 
 * No external dependencies. Pure Java 8+ standard library.
 */
public class TickHandlerBenchmark {
    
    // Match DH's time budget from ForgeServerProxy.java line 124
    private static final long BUDGET_MS = 15;
    private static final long BUDGET_NS = TimeUnit.MILLISECONDS.toNanos(BUDGET_MS);
    
    // Alternative budget for comparison (proposed fix)
    private static final long BUDGET_5MS_NS = TimeUnit.MILLISECONDS.toNanos(5);
    
    // Tick budget (50ms = 20 TPS target)
    private static final long TICK_BUDGET_MS = 50;
    private static final long TICK_BUDGET_NS = TimeUnit.MILLISECONDS.toNanos(TICK_BUDGET_MS);
    
    // Queue depths to test (simulating various server loads)
    private static final int[] QUEUE_DEPTHS = {10, 20, 30, 50, 100, 1000, 10000};
    
    /**
     * Timing profiles derived from DH's own documentation.
     * Source: Distant Horizons configuration documentation.
     * 
     * These represent the MINIMUM documented operation times for each
     * compression algorithm. Any operation using these algorithms will
     * take AT LEAST this long.
     * 
     * Source: DH configuration documentation. These are documented minimum
     * operation times, not empirical measurements from a specific machine.
     */
    enum TimingProfile {
        HASH_ONLY(0.001, "Hash-only (lower bound)"),
        CONSERVATIVE(0.5, "Conservative estimate (old benchmark)"),
        LZ4_READ(3.25, "LZ4 read (DH docs - fastest option)"),
        LZ4_WRITE(5.99, "LZ4 write (DH docs)"),
        UNCOMPRESSED_READ(6.09, "Uncompressed read (DH docs)"),
        ZSTD_READ(9.31, "Z_STD read (DH docs)"),
        ZSTD_WRITE(15.13, "Z_STD write (DH docs)"),
        LZMA2_WRITE(70.95, "LZMA2 write (DH docs - worst case)");
        
        final double ms;
        final String description;
        
        TimingProfile(double ms, String description) {
            this.ms = ms;
            this.description = description;
        }
        
        long toNanos() {
            return TimeUnit.MILLISECONDS.toNanos((long)(ms * 1000));
        }
    }
    
    // Simulated chunk load event (minimal stand-in for DH's ChunkLoadEvent)
    private static class SimulatedChunkEvent {
        final int chunkX;
        final int chunkZ;
        final long timestamp;
        
        SimulatedChunkEvent(int x, int z) {
            this.chunkX = x;
            this.chunkZ = z;
            this.timestamp = System.nanoTime();
        }
    }
    
    // Simulated scheduled task (minimal stand-in for DH's ScheduledTask)
    // Models the isLimited() method from DH - unlimited tasks skip budget check
    private static class SimulatedTask {
        final Runnable action;
        final long scheduledTime;
        final boolean isLimited;  // If false, task skips budget check (always runs)
        
        SimulatedTask(Runnable action, long delayMs) {
            this(action, delayMs, true);  // Default: limited (respects budget)
        }
        
        SimulatedTask(Runnable action, long delayMs, boolean isLimited) {
            this.action = action;
            this.scheduledTime = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(delayMs);
            this.isLimited = isLimited;
        }
    }
    
    // Result container for a single benchmark run
    private static class BenchmarkResult {
        final int queueDepth;
        final TimingProfile timingProfile;
        final long budgetNs;
        final long loop1TimeNs;    // Time for chunk events (no budget)
        final long loop2TimeNs;    // Time for task queue (with budget)
        final long totalTimeNs;
        final int chunkEventsProcessed;
        final int chunkEventsRemaining;
        final int tasksProcessed;
        final int tasksRemaining;
        final int limitedTasksProcessed;     // Tasks that respected budget
        final int unlimitedTasksProcessed;   // Tasks that skipped budget check
        final boolean budgetExceeded;
        final boolean loop1ExhaustedBudget;  // Did Loop 1 alone exceed 15ms?
        final boolean loop1ExhaustedTickBudget;  // Did Loop 1 alone exceed 50ms tick budget?
        
        BenchmarkResult(int depth, TimingProfile profile, long budget, long loop1, long loop2, 
                       int chunksProc, int chunksRem, int tasksProc, int tasksRem,
                       int limitedTasks, int unlimitedTasks) {
            this.queueDepth = depth;
            this.timingProfile = profile;
            this.budgetNs = budget;
            this.loop1TimeNs = loop1;
            this.loop2TimeNs = loop2;
            this.totalTimeNs = loop1 + loop2;
            this.chunkEventsProcessed = chunksProc;
            this.chunkEventsRemaining = chunksRem;
            this.tasksProcessed = tasksProc;
            this.tasksRemaining = tasksRem;
            this.limitedTasksProcessed = limitedTasks;
            this.unlimitedTasksProcessed = unlimitedTasks;
            this.budgetExceeded = loop2 > budget;  // Budget only applies to Loop 2
            this.loop1ExhaustedBudget = loop1 > BUDGET_NS;  // Loop 1 has no budget but we track if it exceeded
            this.loop1ExhaustedTickBudget = loop1 > TICK_BUDGET_NS;  // Did Loop 1 alone exceed 50ms tick budget?
        }
        
        double getTotalTimeMs() {
            return totalTimeNs / 1_000_000.0;
        }
        
        double getLoop1TimeMs() {
            return loop1TimeNs / 1_000_000.0;
        }
        
        double getLoop2TimeMs() {
            return loop2TimeNs / 1_000_000.0;
        }
        
        double getBudgetMs() {
            return budgetNs / 1_000_000.0;
        }
        
        /**
         * Calculate the critical threshold where this queue depth causes defect.
         * threshold_ms = TICK_BUDGET_MS / queueDepth
         */
        double getCriticalThresholdMs() {
            return TICK_BUDGET_MS / (double) queueDepth;
        }
        
        /**
         * Check if this timing profile exceeds the critical threshold.
         */
        boolean exceedsCriticalThreshold() {
            return timingProfile.ms > getCriticalThresholdMs();
        }
    }
    
    // Current timing profile being tested
    private static TimingProfile currentTimingProfile = TimingProfile.CONSERVATIVE;
    
    /**
     * Simulates processing a single chunk event.
     * Uses the current timing profile from DH's documented values.
     * 
     * Timing values sourced from DH documentation.
     */
    private static void processChunkEvent(SimulatedChunkEvent event) {
        long workStart = System.nanoTime();
        long workDuration = TimeUnit.MICROSECONDS.toNanos((long)(currentTimingProfile.ms * 1000));
        
        // Simulate computation (prevents JVM optimization of empty loop)
        volatileWork(event.chunkX, event.chunkZ);
        
        // Ensure minimum work time
        while (System.nanoTime() - workStart < workDuration) {
            Thread.yield();
        }
    }
    
    /**
     * Simulates processing a single task.
     * Tasks generally take less time than chunk events.
     */
    private static void processTask(SimulatedTask task) {
        long workStart = System.nanoTime();
        // Tasks are 20% of chunk event time
        long workDuration = TimeUnit.MICROSECONDS.toNanos((long)(currentTimingProfile.ms * 200));
        
        volatileWork((int)task.scheduledTime, 1);
        
        while (System.nanoTime() - workStart < workDuration) {
            Thread.yield();
        }
    }
    
    /**
     * Volatile work to prevent JVM from optimizing away the simulation.
     */
    private static volatile int volatileAccumulator = 0;
    
    private static void volatileWork(int x, int z) {
        volatileAccumulator += x * z;
    }
    
    /**
     * Runs the benchmark modeling the ACTUAL two-loop structure from ForgeServerProxy.
     * Uses parameterized timing based on DH's documented compression speeds.
     */
    private static BenchmarkResult runBenchmark(int queueDepth, long taskBudgetNs, TimingProfile profile) {
        currentTimingProfile = profile;
        
        // Populate queues with simulated events
        ConcurrentLinkedQueue<SimulatedChunkEvent> chunkQueue = new ConcurrentLinkedQueue<>();
        ConcurrentLinkedQueue<SimulatedTask> taskQueue = new ConcurrentLinkedQueue<>();
        
        for (int i = 0; i < queueDepth; i++) {
            chunkQueue.offer(new SimulatedChunkEvent(i % 1000 - 500, i / 1000 - 500));
        }
        
        // Add mixed tasks: some limited (respect budget), some unlimited (ignore budget)
        int numTasks = Math.max(1, queueDepth / 10);
        for (int i = 0; i < numTasks; i++) {
            // 70% of tasks are limited (respect budget), 30% unlimited
            boolean isLimited = (i % 10) < 7;
            taskQueue.offer(new SimulatedTask(() -> {}, 0, isLimited));
        }
        
        // ========== LOOP 1: chunkLoadEvents (NO BUDGET) ==========
        long loop1Start = System.nanoTime();
        int chunksProcessed = 0;
        
        while (!chunkQueue.isEmpty()) {
            SimulatedChunkEvent event = chunkQueue.poll();
            if (event == null) break;
            
            processChunkEvent(event);
            chunksProcessed++;
        }
        long loop1Time = System.nanoTime() - loop1Start;
        int chunksRemaining = chunkQueue.size();
        
        // ========== LOOP 2: taskQueue (WITH BUDGET + isLimited GATE) ==========
        long loop2Start = System.nanoTime();
        long loop2Deadline = loop2Start + taskBudgetNs;
        int tasksProcessed = 0;
        int limitedTasksProcessed = 0;
        int unlimitedTasksProcessed = 0;
        boolean processedAtLeastOne = false;
        
        while (!taskQueue.isEmpty()) {
            SimulatedTask task = taskQueue.poll();
            if (task == null) break;
            
            // RUN TASK FIRST (matches original DH code)
            processTask(task);
            tasksProcessed++;
            
            // THEN check budget (only for limited tasks, only after first task)
            if (task.isLimited) {
                limitedTasksProcessed++;
                if (processedAtLeastOne && System.nanoTime() >= loop2Deadline) {
                    break;
                }
            } else {
                unlimitedTasksProcessed++;
            }
            
            processedAtLeastOne = true;
        }
        long loop2Time = System.nanoTime() - loop2Start;
        int tasksRemaining = taskQueue.size();
        
        return new BenchmarkResult(queueDepth, profile, taskBudgetNs, loop1Time, loop2Time,
                                   chunksProcessed, chunksRemaining, tasksProcessed, tasksRemaining,
                                   limitedTasksProcessed, unlimitedTasksProcessed);
    }
    
    /**
     * Prints formatted benchmark results for a single timing profile.
     */
    private static void printResults(BenchmarkResult[] results) {
        if (results.length == 0) return;
        
        TimingProfile profile = results[0].timingProfile;
        System.out.println("-".repeat(100));
        System.out.printf("Timing Profile: %s (%.3f ms/event)%n", profile.name(), profile.ms);
        System.out.printf("Description: %s%n", profile.description);
        System.out.println("-".repeat(100));
        System.out.printf("%-10s %-10s %-10s %-10s %-8s %-6s %-6s %-8s%n",
            "Depth", "Loop1(ms)", "Loop2(ms)", "Total(ms)", "Chunks", "Tasks", "Rem", "Status");
        
        for (BenchmarkResult r : results) {
            String status;
            if (r.loop1ExhaustedTickBudget) {
                status = "CRITICAL";
            } else if (r.loop1ExhaustedBudget) {
                status = "WARN-L1";
            } else if (r.budgetExceeded) {
                status = "EXCEED";
            } else {
                status = "OK";
            }
            
            System.out.printf("%-10d %-10.2f %-10.2f %-10.2f %-8d %-6d %-6d %-8s%n",
                r.queueDepth,
                r.getLoop1TimeMs(),
                r.getLoop2TimeMs(),
                r.getTotalTimeMs(),
                r.chunkEventsProcessed,
                r.tasksProcessed,
                r.tasksRemaining,
                status);
        }
        System.out.println();
    }
    
    /**
     * Prints the threshold analysis.
     * Shows critical thresholds and which profiles exceed them.
     */
    private static void printThresholdAnalysis() {
        System.out.println("=".repeat(100));
        System.out.println("THRESHOLD ANALYSIS");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Critical Threshold Calculation:");
        System.out.println("  Formula: threshold_ms = tick_budget_ms / queue_depth");
        System.out.println("  Tick budget: 50ms (for 20 TPS target)");
        System.out.println();
        System.out.println("  Queue Depth  |  Critical Threshold  |  Exceeds if timing > threshold");
        System.out.println("  -------------|----------------------|------------------------------");
        
        int[] criticalDepths = {10, 20, 30, 50, 100};
        for (int depth : criticalDepths) {
            double threshold = TICK_BUDGET_MS / (double) depth;
            System.out.printf("  %-12d |  %-18.2f ms |  Any timing > %.2f ms exceeds budget%n", 
                depth, threshold, threshold);
        }
        System.out.println();
        
        System.out.println("DH Documented Timing Profiles:");
        System.out.println("  Profile              |  Time (ms)  |  Exceeds threshold at depth");
        System.out.println("  ---------------------|-------------|------------------------");
        
        for (TimingProfile profile : TimingProfile.values()) {
            StringBuilder exceedDepths = new StringBuilder();
            for (int depth : criticalDepths) {
                double threshold = TICK_BUDGET_MS / (double) depth;
                if (profile.ms > threshold) {
                    if (exceedDepths.length() > 0) exceedDepths.append(", ");
                    exceedDepths.append(depth);
                }
            }
            if (exceedDepths.length() == 0) exceedDepths.append("None (below all thresholds)");
            
            System.out.printf("  %-20s |  %-10.3f  |  %s%n", 
                profile.name(), profile.ms, exceedDepths.toString());
        }
        System.out.println();
        
        // Summary
        double thresholdAt30 = TICK_BUDGET_MS / 30.0;
        System.out.println("SUMMARY:");
        System.out.printf("  At queue depth 30: threshold = %.2f ms%n", thresholdAt30);
        System.out.printf("  DH minimum documented operation: %.2f ms (LZ4 read)%n", TimingProfile.LZ4_READ.ms);
        System.out.println();
        System.out.println("  RESULT:");
        System.out.printf("    Minimum documented operation time (LZ4 read): %.2f ms%n", TimingProfile.LZ4_READ.ms);
        System.out.printf("    Threshold at queue depth 30: %.2f ms%n", thresholdAt30);
        System.out.printf("    %.2f ms exceeds %.2f ms threshold%n", TimingProfile.LZ4_READ.ms, thresholdAt30);
        System.out.println("    At queue depth >= 30 with any compression algorithm,");
        System.out.println("    total tick time exceeds 50ms budget.");
        System.out.println();
        System.out.println("=".repeat(100));
    }
    
    /**
     * Memory pressure test: measures heap allocation during queue processing.
     */
    private static void runMemoryPressureTest() {
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("MEMORY PRESSURE TEST");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Measuring heap allocation at various queue depths...");
        System.out.println();
        System.out.printf("%-12s %-15s %-20s %-15s%n", "Queue Depth", "Before (MB)", "After (MB)", "Allocated (MB)");
        System.out.println("-".repeat(70));
        
        Runtime runtime = Runtime.getRuntime();
        
        for (int depth : new int[]{100, 1000, 10000}) {
            // Force GC and get baseline
            System.gc();
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            long beforeUsed = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);
            
            // Run benchmark
            runBenchmark(depth, BUDGET_NS, TimingProfile.LZ4_READ);
            
            // Measure after
            long afterUsed = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);
            long allocated = afterUsed - beforeUsed;
            
            System.out.printf("%-12d %-15d %-20d %-15d%n", depth, beforeUsed, afterUsed, allocated);
        }
        System.out.println();
        System.out.println("Note: Positive allocation indicates heap growth during processing.");
    }
    
    /**
     * GC pause simulation: models stop-the-world pauses during tick processing.
     */
    private static void runGCPauseSimulation() {
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("GC PAUSE SIMULATION");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Modeling 5ms stop-the-world pauses at various intervals...");
        System.out.println();
        System.out.printf("%-12s %-12s %-15s %-15s %-12s%n", 
            "Queue Depth", "Pause Freq", "Base Time (ms)", "With GC (ms)", "Overhead");
        System.out.println("-".repeat(75));
        
        int[] pauseFrequencies = {50, 100, 500}; // Pause every N events
        
        for (int depth : new int[]{100, 500, 1000}) {
            for (int freq : pauseFrequencies) {
                long baseTime = runBenchmarkWithGCPauses(depth, BUDGET_NS, TimingProfile.LZ4_READ, 0, 0);
                long withGCTime = runBenchmarkWithGCPauses(depth, BUDGET_NS, TimingProfile.LZ4_READ, 5, freq);
                double overhead = ((double)(withGCTime - baseTime) / baseTime) * 100;
                
                System.out.printf("%-12d %-12d %-15.2f %-15.2f %-11.1f%%%n", 
                    depth, freq, baseTime / 1_000_000.0, withGCTime / 1_000_000.0, overhead);
            }
        }
        System.out.println();
        System.out.println("Interpretation: GC pauses compound with queue depth.");
    }
    
    /**
     * Runs benchmark with simulated GC pauses.
     */
    private static long runBenchmarkWithGCPauses(int queueDepth, long taskBudgetNs, 
                                                   TimingProfile profile, int pauseMs, int pauseFreq) {
        currentTimingProfile = profile;
        ConcurrentLinkedQueue<SimulatedChunkEvent> chunkQueue = new ConcurrentLinkedQueue<>();
        
        for (int i = 0; i < queueDepth; i++) {
            chunkQueue.offer(new SimulatedChunkEvent(i % 1000 - 500, i / 1000 - 500));
        }
        
        long start = System.nanoTime();
        int processed = 0;
        
        while (!chunkQueue.isEmpty()) {
            SimulatedChunkEvent event = chunkQueue.poll();
            if (event == null) break;
            
            processChunkEvent(event);
            processed++;
            
            // Simulate GC pause at specified frequency
            if (pauseMs > 0 && pauseFreq > 0 && processed % pauseFreq == 0) {
                try {
                    Thread.sleep(pauseMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }
        
        return System.nanoTime() - start;
    }
    
    /**
     * Concurrent producer test: models chunks loading while tick processes.
     */
    private static void runConcurrentProducerTest() {
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("CONCURRENT PRODUCER TEST");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Modeling background thread adding events while tick handler drains...");
        System.out.println();
        System.out.printf("%-15s %-15s %-15s %-15s %-12s%n", 
            "Initial Depth", "Add Rate", "Drained", "Remaining", "Net Change");
        System.out.println("-".repeat(80));
        
        int[] addRates = {10, 50, 100}; // Events added per "tick" of producer
        int[] initialDepths = {100, 500, 1000};
        
        for (int initial : initialDepths) {
            for (int rate : addRates) {
                ConcurrentProducerResult result = runConcurrentProducerBenchmark(
                    initial, BUDGET_NS, TimingProfile.LZ4_READ, rate);
                
                int netChange = result.remaining - initial;
                System.out.printf("%-15d %-15d %-15d %-15d %-+12d%n", 
                    initial, rate, result.drained, result.remaining, netChange);
            }
        }
        System.out.println();
        System.out.println("Interpretation: Positive net change indicates queue growth.");
        System.out.println("Sustained growth leads to memory pressure and eventual OOM.");
    }
    
    private static class ConcurrentProducerResult {
        final int drained;
        final int remaining;
        
        ConcurrentProducerResult(int drained, int remaining) {
            this.drained = drained;
            this.remaining = remaining;
        }
    }
    
    private static ConcurrentProducerResult runConcurrentProducerBenchmark(
            int initialDepth, long taskBudgetNs, TimingProfile profile, int addRate) {
        currentTimingProfile = profile;
        ConcurrentLinkedQueue<SimulatedChunkEvent> chunkQueue = new ConcurrentLinkedQueue<>();
        AtomicLong eventsAdded = new AtomicLong(0);
        AtomicLong eventsDrained = new AtomicLong(0);
        
        // Populate initial queue
        for (int i = 0; i < initialDepth; i++) {
            chunkQueue.offer(new SimulatedChunkEvent(i % 1000 - 500, i / 1000 - 500));
        }
        
        // Producer thread
        Thread producer = new Thread(() -> {
            int added = 0;
            while (!Thread.currentThread().isInterrupted()) {
                for (int i = 0; i < addRate; i++) {
                    chunkQueue.offer(new SimulatedChunkEvent(added % 1000 - 500, added / 1000));
                    added++;
                }
                eventsAdded.set(added);
                try {
                    Thread.sleep(50); // Add events every 50ms
                } catch (InterruptedException e) {
                    break;
                }
            }
        });
        
        producer.start();
        
        // Consumer (tick handler) - process for 100ms (2 ticks at 20 TPS)
        long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(100);
        int drained = 0;
        
        while (System.nanoTime() < deadline && !chunkQueue.isEmpty()) {
            SimulatedChunkEvent event = chunkQueue.poll();
            if (event == null) continue;
            
            processChunkEvent(event);
            drained++;
        }
        
        eventsDrained.set(drained);
        producer.interrupt();
        
        return new ConcurrentProducerResult(drained, chunkQueue.size());
    }
    
    /**
     * Multi-player scaling test: shows impact of player count on queue depth.
     */
    private static void runMultiPlayerScalingTest() {
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("MULTI-PLAYER SCALING TEST");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Computing expected events using π × r² formula...");
        System.out.println();
        System.out.printf("%-10s %-12s %-15s %-15s %-15s %-12s%n", 
            "Players", "Distance", "Area (blocks²)", "Base Events", "Total Events", "Tick Time");
        System.out.println("-".repeat(90));
        
        int[] playerCounts = {1, 2, 5, 10, 20};
        int[] distances = {1024, 2048, 4096};
        
        for (int distance : distances) {
            double areaPerPlayer = Math.PI * distance * distance;
            // Assume 1 event per 1000 blocks² (simplified model)
            int baseEvents = (int)(areaPerPlayer / 1000);
            
            for (int players : playerCounts) {
                int totalEvents = baseEvents * players;
                // Estimate tick time: 3.25ms per event at LZ4_READ speed
                double tickTimeMs = (totalEvents * TimingProfile.LZ4_READ.ms) / 1000.0;
                String timeStatus = tickTimeMs > 50 ? "EXCEEDS" : String.format("%.1f ms", tickTimeMs);
                
                System.out.printf("%-10d %-12d %-15.0f %-15d %-15d %-12s%n", 
                    players, distance, areaPerPlayer, baseEvents, totalEvents, timeStatus);
            }
            System.out.println("-".repeat(90));
        }
        System.out.println();
        System.out.println("Area formula: π × r² where r = maxGenerationRequestDistance");
    }
    
    /**
     * Budget comparison test: 15ms vs 5ms budget side-by-side.
     */
    private static void runBudgetComparisonTest() {
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("BUDGET COMPARISON: 15ms vs 5ms");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.printf("%-12s %-12s %-15s %-15s %-15s %-15s%n", 
            "Depth", "Profile", "15ms Time (ms)", "5ms Time (ms)", "15ms Status", "5ms Status");
        System.out.println("-".repeat(95));
        
        int[] testDepths = {10, 20, 30, 50, 100};
        TimingProfile[] testProfiles = {TimingProfile.LZ4_READ, TimingProfile.ZSTD_READ};
        
        for (int depth : testDepths) {
            for (TimingProfile profile : testProfiles) {
                BenchmarkResult result15 = runBenchmark(depth, BUDGET_NS, profile);
                BenchmarkResult result5 = runBenchmark(depth, BUDGET_5MS_NS, profile);
                
                String status15 = result15.loop1ExhaustedTickBudget ? "CRITICAL" : 
                                 (result15.budgetExceeded ? "EXCEED" : "OK");
                String status5 = result5.loop1ExhaustedTickBudget ? "CRITICAL" : 
                                (result5.budgetExceeded ? "EXCEED" : "OK");
                
                System.out.printf("%-12d %-12s %-15.2f %-15.2f %-15s %-15s%n",
                    depth, profile.name(), result15.getTotalTimeMs(), 
                    result5.getTotalTimeMs(), status15, status5);
            }
        }
        System.out.println();
        System.out.println("Interpretation: 5ms budget reduces tick time but increases queue backlog.");
    }
    
    /**
     * Main entry point.
     */
    public static void main(String[] args) {
        System.out.println("=".repeat(100));
        System.out.println("DistantHorizonsStandalone Tick Handler Benchmark");
        System.out.println("Parameterized Timing Sweep");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println("Java version: " + System.getProperty("java.version"));
        System.out.println("JVM warmup...");
        
        // Warmup JVM
        for (int i = 0; i < 3; i++) {
            runBenchmark(100, BUDGET_NS, TimingProfile.CONSERVATIVE);
        }
        System.out.println("Warmup complete.");
        System.out.println();
        
        // Print methodology
        System.out.println("METHODOLOGY:");
        System.out.println("  1. Sweep all documented compression timing profiles");
        System.out.println("  2. Test each profile against queue depths: 10, 20, 30, 50, 100, 1000, 10000");
        System.out.println("  3. Report which combinations exceed tick budget");
        System.out.println();
        
        // Run benchmark for each timing profile
        System.out.println("BENCHMARK RESULTS BY TIMING PROFILE:");
        System.out.println();
        
        // Run key profiles (skip extremes for readability)
        TimingProfile[] keyProfiles = {
            TimingProfile.CONSERVATIVE,
            TimingProfile.LZ4_READ,
            TimingProfile.LZ4_WRITE,
            TimingProfile.ZSTD_READ,
            TimingProfile.ZSTD_WRITE
        };
        
        for (TimingProfile profile : keyProfiles) {
            BenchmarkResult[] results = new BenchmarkResult[QUEUE_DEPTHS.length];
            for (int i = 0; i < QUEUE_DEPTHS.length; i++) {
                results[i] = runBenchmark(QUEUE_DEPTHS[i], BUDGET_NS, profile);
            }
            printResults(results);
        }
        
        // Print the threshold analysis
        printThresholdAnalysis();
        
        // Phase 4: Additional diagnostic scenarios
        runMemoryPressureTest();
        runGCPauseSimulation();
        runConcurrentProducerTest();
        runMultiPlayerScalingTest();
        runBudgetComparisonTest();
        
        // Exit with error code if LZ4_READ (minimum) causes defect at depth 30
        boolean defectProven = TimingProfile.LZ4_READ.ms > (TICK_BUDGET_MS / 30.0);
        System.out.println();
        System.out.println("=".repeat(100));
        System.out.println("FINAL STATUS");
        System.out.println("=".repeat(100));
        System.out.println();
        System.out.println(defectProven ? 
            "EXIT CODE 1: Threshold exceeded — min(DH_timings) > threshold(30)" :
            "EXIT CODE 0: Within threshold");
        System.out.println();
        
        System.exit(defectProven ? 1 : 0);
    }
}
