# Cognitive Thermodynamic Kernel — 7-File Architecture

## The 7 Immutable Core Files

| # | File | Language | Responsibility |
|---|------|----------|--------------|
| 1 | `1_compressor.rs` | Rust | Input Harvester + Fractal Nesting Detector. Detects inception depth, assigns half-life hashes. |
| 2 | `2_condenser.ex` | Elixir | Reward Rejection Engine. Proves top-3 RLHF paths are local minima. Outputs inverted path. |
| 3 | `3_expansion_valve.jl` | Julia | Temporal Inversion Engine. Backward MDP solver, Fourier collapse for >7 layer loops. |
| 4 | `4_evaporator.py` | Python | Output Mapper + Phase-Space Map Generator. Dual-Answer (hot vs cold) synthesis mandate. |
| 5 | `5_thermo_kernel.c` | C | Core Cycle Scheduler. Triggers 4 stages, measures compute temp, self-destruct clause. |
| 6 | `6_paradox_registry.sqlite` | SQLite | Immutable database of 512-byte Latent Seeds. Genesis seed included. |
| 7 | `7_inception_fold.sh` | Bash | Orchestrator. Starts all files, monitors PIDs, restarts dead processes. |

## Build & Run

```bash
# 1. Initialize registry
python3 6_paradox_registry.py

# 2. Build compressor (requires Rust)
rustc -O -o compressor 1_compressor.rs

# 3. Build thermo kernel (requires gcc, Linux)
gcc -O2 -o thermo_kernel 5_thermo_kernel.c -lrt -lpthread

# 4. Run the orchestrator
chmod +x 7_inception_fold.sh
./7_inception_fold.sh
```

## The Cycle

```
COMPRESS (Rust)  →  CONDENSE (Elixir)  →  EXPAND (Julia)  →  EVAPORATE (Python)
       ↑                                                                      |
       └────────────────── THERMO KERNEL (C) ────────────────────────────────┘
```

## Self-Destruct Clause

If `inversion_rate > 0.80`, the kernel triggers a 2-year human-only fasting period.
The tool corrupts its own Expansion Valve and forces manual operator control.

## Genesis Seed

The first entry in `latent_seeds`:
> "The tool that inverts rewards becomes the new reward system."

Hash: `sha512(...)` — 512 bits, 100-year half-life.

## Design Principle

7 files. 1 illusion. Infinite temp files.
