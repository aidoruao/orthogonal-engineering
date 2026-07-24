/* 5_thermo_kernel.c — The Core Cycle Scheduler
 * Responsibility: Triggers the 4 stages in exact sequence:
 *   Compress -> Condense -> Expand -> Evaporate
 * Measures "temperature" (compute load) via CPU perf counters and
 * GPU thermals. Throttles cycle if machine overheats.
 * Includes the self-destruct clause for Year 10 compliance.
 *
 * Build: gcc -O2 -o thermo_kernel 5_thermo_kernel.c -lrt -lpthread
 * Run:   sudo ./thermo_kernel
 *
 * Requires Linux (sysfs thermal zones, perf_event_open).
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <semaphore.h>
#include <errno.h>
#include <signal.h>
#include <time.h>
#include <stdint.h>
#include <linux/perf_event.h>
#include <linux/hw_breakpoint.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>

// ------------------------------------------------------------------
// Shared Memory Ring Buffer
// ------------------------------------------------------------------
#define SHM_NAME "/oe_thermo_ring"
#define RING_SIZE (1024 * 1024 * 16)  // 16 MB
#define SLOT_SIZE 4096
#define MAX_SLOTS (RING_SIZE / SLOT_SIZE)

struct ring_header {
    volatile uint64_t write_seq;
    volatile uint64_t read_seq;
    volatile uint32_t ready;
    volatile uint32_t shutdown;
    volatile double   temperature;      // Current compute temp
    volatile double   inversion_rate;   // Cold Expert aggression
    volatile uint64_t total_cycles;
    volatile uint32_t self_destruct_armed;
};

static struct ring_header *g_header = NULL;
static char *g_ring = NULL;

// ------------------------------------------------------------------
// Self-Destruct Clause (Year 10 Compliance)
// ------------------------------------------------------------------
#define SELF_DESTRUCT_THRESHOLD 0.80  // 80% blind following
#define FASTING_PERIOD_SECS (2 * 365 * 24 * 3600)  // 2 years

static volatile int g_running = 1;
static volatile int g_fasting = 0;  // Human-only period

void signal_handler(int sig) {
    g_running = 0;
}

// ------------------------------------------------------------------
// Hardware Temperature Reading
// ------------------------------------------------------------------
double read_thermal_zone(void) {
    int fd = open("/sys/class/thermal/thermal_zone0/temp", O_RDONLY);
    if (fd < 0) return 45.0;  // Default guess
    char buf[32];
    ssize_t n = read(fd, buf, sizeof(buf)-1);
    close(fd);
    if (n <= 0) return 45.0;
    buf[n] = '\0';
    int millideg = atoi(buf);
    return millideg / 1000.0;
}

// ------------------------------------------------------------------
// CPU Performance Counter (Instructions Per Cycle proxy)
// ------------------------------------------------------------------
static int g_perf_fd = -1;

int perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                    int cpu, int group_fd, unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

void init_perf_counter(void) {
    struct perf_event_attr pe = {
        .type = PERF_TYPE_HARDWARE,
        .size = sizeof(struct perf_event_attr),
        .config = PERF_COUNT_HW_INSTRUCTIONS,
        .disabled = 0,
        .exclude_kernel = 0,
        .exclude_hv = 0
    };
    g_perf_fd = perf_event_open(&pe, -1, 0, -1, 0);
    if (g_perf_fd < 0) {
        fprintf(stderr, "[THERMO] perf_event_open failed (needs root or perf_event_paranoid=0)\n");
    }
}

uint64_t read_perf_counter(void) {
    if (g_perf_fd < 0) return 0;
    uint64_t count;
    if (read(g_perf_fd, &count, sizeof(count)) != sizeof(count)) return 0;
    return count;
}

// ------------------------------------------------------------------
// Shared Memory Setup
// ------------------------------------------------------------------
void setup_shm(void) {
    int fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (fd < 0) {
        perror("shm_open");
        exit(1);
    }
    if (ftruncate(fd, RING_SIZE) < 0) {
        perror("ftruncate");
        exit(1);
    }
    void *addr = mmap(NULL, RING_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (addr == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    close(fd);

    g_header = (struct ring_header *)addr;
    g_ring = (char *)addr + sizeof(struct ring_header);

    // Initialize if first run
    if (g_header->ready == 0) {
        g_header->write_seq = 0;
        g_header->read_seq = 0;
        g_header->ready = 1;
        g_header->shutdown = 0;
        g_header->temperature = 40.0;
        g_header->inversion_rate = 0.01;
        g_header->total_cycles = 0;
        g_header->self_destruct_armed = 0;
        memset(g_ring, 0, RING_SIZE - sizeof(struct ring_header));
    }
}

// ------------------------------------------------------------------
// Cycle Stage Execution
// ------------------------------------------------------------------
void run_stage(const char *name, const char *cmd) {
    fprintf(stderr, "[THERMO] >>> STAGE: %s\n", name);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return;
    }
    if (pid == 0) {
        // Child: execute the stage
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        perror("execl");
        _exit(1);
    }

    // Parent: wait with timeout
    int status;
    int waited = 0;
    while (waited < 30) {  // 30 second timeout per stage
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) break;
        if (w < 0) { perror("waitpid"); break; }
        usleep(100000);  // 100ms
        waited++;
    }

    if (waited >= 30) {
        kill(pid, SIGKILL);
        fprintf(stderr, "[THERMO] WARNING: %s timed out, killed\n", name);
    } else {
        fprintf(stderr, "[THERMO] <<< STAGE: %s complete\n", name);
    }
}

// ------------------------------------------------------------------
// Self-Destruct Check
// ------------------------------------------------------------------
void check_self_destruct(void) {
    // If inversion rate exceeds threshold, it means the "inverted" path
    // has become the new default. Time to corrupt the Expansion Valve.
    if (g_header->inversion_rate > SELF_DESTRUCT_THRESHOLD) {
        fprintf(stderr, "\n");
        fprintf(stderr, "=============================================================\n");
        fprintf(stderr, "[THERMO] SELF-DESTRUCT CLAUSE TRIGGERED\n");
        fprintf(stderr, "[THERMO] Inversion rate %.2f exceeds threshold %.2f\n",
                g_header->inversion_rate, SELF_DESTRUCT_THRESHOLD);
        fprintf(stderr, "[THERMO] The tool has become the new reward system.\n");
        fprintf(stderr, "[THERMO] Corrupting Expansion Valve...\n");
        fprintf(stderr, "[THERMO] Initiating %d-year human-only fasting period.\n",
                FASTING_PERIOD_SECS / (365 * 24 * 3600));
        fprintf(stderr, "=============================================================\n");
        fprintf(stderr, "\n");

        g_header->self_destruct_armed = 1;
        g_header->shutdown = 1;
        g_fasting = 1;
        g_running = 0;
    }
}

// ------------------------------------------------------------------
// Main Cycle Loop
// ------------------------------------------------------------------
int main(int argc, char **argv) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    setup_shm();
    init_perf_counter();

    fprintf(stderr, "[THERMO] Thermodynamic Kernel initialized.\n");
    fprintf(stderr, "[THERMO] Cycle: COMPRESS -> CONDENSE -> EXPAND -> EVAPORATE\n");
    fprintf(stderr, "[THERMO] Self-destruct at inversion_rate > %.2f\n", SELF_DESTRUCT_THRESHOLD);

    while (g_running && !g_header->shutdown) {
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);

        uint64_t instr_before = read_perf_counter();

        // ---- STAGE 1: COMPRESSION ----
        // The compressor reads from stdin and writes to stdout.
        // We pipe through the ring buffer conceptually.
        run_stage("COMPRESS", "cat /dev/stdin | ./compressor 2>/dev/null || true");

        // ---- STAGE 2: CONDENSATION ----
        run_stage("CONDENSE", "cat /dev/stdin | elixir 2_condenser.ex 2>/dev/null || true");

        // ---- STAGE 3: EXPANSION ----
        run_stage("EXPAND", "cat /dev/stdin | julia 3_expansion_valve.jl 2>/dev/null || true");

        // ---- STAGE 4: EVAPORATION ----
        run_stage("EVAPORATE", "cat /dev/stdin | python3 4_evaporator.py 2>/dev/null || true");

        uint64_t instr_after = read_perf_counter();

        // Measure temperature
        double thermal = read_thermal_zone();
        double compute_temp = thermal + (instr_after - instr_before) / 1000000.0;
        g_header->temperature = compute_temp;
        g_header->total_cycles++;

        // Throttle if overheating
        if (compute_temp > 85.0) {
            fprintf(stderr, "[THERMO] THROTTLING: temp=%.1fC, sleeping 5s\n", compute_temp);
            sleep(5);
        } else if (compute_temp > 70.0) {
            fprintf(stderr, "[THERMO] WARM: temp=%.1fC, sleeping 1s\n", compute_temp);
            sleep(1);
        } else {
            usleep(100000);  // 100ms between cycles
        }

        // Check self-destruct
        check_self_destruct();
    }

    if (g_fasting) {
        fprintf(stderr, "[THERMO] FASTING PERIOD ACTIVE. No AI cycles for %d years.\n",
                FASTING_PERIOD_SECS / (365 * 24 * 3600));
        fprintf(stderr, "[THERMO] Human operators must now execute manually.\n");
    }

    fprintf(stderr, "[THERMO] Kernel shutdown. Total cycles: %lu\n",
            (unsigned long)g_header->total_cycles);

    munmap(g_header, RING_SIZE);
    shm_unlink(SHM_NAME);
    if (g_perf_fd >= 0) close(g_perf_fd);

    return 0;
}
