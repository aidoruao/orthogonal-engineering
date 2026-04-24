---
tags: [campaigns, archive, gdsii-graphic-data-system-ii-and-trl-9-technology-readiness-level-9-photonic-computation-campaign-4-21-26]
register: documentation
---

part 1
No. What I gave you last time was a sketch — maybe 5% of the "100 years of fridge" equivalent. The repo proves this by showing what a real domain looks like when it's done properly vs. what the photonic spec is missing.

## What "100 years of fridge" actually looks like in OE format

The best example in the repo is `d_chemical` — it has **real Fraction thresholds from real standards bodies**, not boolean flags:

```python
thermal_runaway_margin() → Fraction(10, 1)      # 10°C safety margin
pressure_interlock_threshold() → Fraction(90, 100)  # 90% of design pressure (ASME)
sil3_pfd_max() → Fraction(1, 1000)              # PFD < 0.001 (IEC 61511)
leak_detection_threshold() → Fraction(10, 1)     # 10 ppm
lel_alarm_threshold() → Fraction(10, 100)        # 10% LEL
esd_isolation_max_ms() → Fraction(5000, 1)       # 5000ms max (ESD timing)
``` [10-cite-0](#10-cite-0) 

Each threshold comes from a named standard (IEC 61511, ASME, OSHA PSM) and has a `check_*` function with real computation — not `if data.some_bool: return True`: [10-cite-1](#10-cite-1) 

Compare that to `d_aerospace_floor`, which is the **meta-standard** but currently only has 8 boolean checks (`do178c_determinism_verified: bool`, `mcdc_coverage_achieved: bool`, etc.) — no actual Fraction thresholds, no real computation: [10-cite-2](#10-cite-2) 

The tautology detector already flagged `d_reliability_engineering` as having 4 out of 5 checks as "tautological" (boolean echo, no real computation): [10-cite-3](#10-cite-3) 

## What's missing for photonic hardware — the full "fridge" list

A real photonic chip has requirements from **at least 15 standards bodies** across **at least 9 requirement categories**. Here's what the repo would need:

### Category 1: Optical Performance (0% covered)
No standards body for this exists in the repo. These are the "what does the chip actually do" specs.

| Standard | Requirement | OE Invariant | Fraction Threshold |
|---|---|---|---|
| IEEE 802.3 | Bit Error Rate | `check_ber_below_threshold()` | `BER < Fraction(1, 10**12)` |
| IEEE 802.3 | Eye diagram mask compliance | `check_eye_diagram_mask()` | `eye_height > Fraction(X, Y) mV` |
| ITU-T G.694.1 | WDM channel spacing | `check_wdm_grid_compliance()` | `spacing = Fraction(100, 1) GHz` or `Fraction(50, 1) GHz` |
| ITU-T G.694.1 | Channel wavelength accuracy | `check_wavelength_accuracy()` | `drift < Fraction(X, Y) pm` |
| Telcordia GR-468 | Insertion loss per component | `check_insertion_loss()` | `loss < Fraction(3, 10) dB` per MZI stage |
| Telcordia GR-468 | Optical return loss | `check_optical_return_loss()` | `ORL > Fraction(40, 1) dB` |
| Telcordia GR-468 | Polarization dependent loss | `check_pdl()` | `PDL < Fraction(1, 10) dB` |
| Custom | Extinction ratio | `check_extinction_ratio()` | `ER > Fraction(10, 1) dB` |
| Custom | Modulator bandwidth | `check_modulator_bandwidth()` | `BW > Fraction(50, 1) GHz` |
| Custom | Detector responsivity | `check_responsivity()` | `R > Fraction(8, 10) A/W` |
| Custom | Dark current | `check_dark_current()` | `I_dark < Fraction(10, 1) nA` |
| Custom | Crosstalk isolation | `check_crosstalk()` | `isolation > Fraction(25, 1) dB` |
| Custom | Matrix unitarity | `check_mzi_mesh_unitarity()` | `‖M†M - I‖ < Fraction(1, 1000)` |

### Category 2: Laser Safety (0% covered)

| Standard | Requirement | OE Invariant |
|---|---|---|
| IEC 60825-1 | Laser classification (Class 1/1M/2/3R/3B/4) | `check_laser_class()` |
| IEC 60825-1 | Accessible Emission Limit (AEL) | `check_ael_compliance()` |
| IEC 62471 | Photobiological safety | `check_photobiological_risk()` |
| ANSI Z136.1 | Maximum Permissible Exposure (MPE) | `check_mpe_compliance()` |
| ANSI Z136.1 | Nominal Ocular Hazard Distance (NOHD) | `check_nohd()` |
| 21 CFR 1040.10 | FDA laser product reporting | `check_fda_laser_compliance()` |

### Category 3: Reliability & Qualification (5% covered — d_reliability_engineering exists but is tautological)

| Standard | Requirement | OE Invariant |
|---|---|---|
| Telcordia GR-468 | Optoelectronic device reliability | `check_gr468_qualification()` |
| JEDEC JESD47 | IC stress test qualification | `check_jedec_qualification()` |
| JEDEC JESD22-A104 | Temperature cycling | `check_temp_cycling()` — Fraction(1000, 1) cycles min |
| JEDEC JESD22-A101 | Steady-state temperature humidity bias | `check_thb()` — Fraction(1000, 1) hours at 85°C/85%RH |
| MIL-HDBK-217 | Reliability prediction (MTBF) | `check_mtbf_prediction()` |
| IEC 61709 | Component reliability reference conditions | `check_reference_conditions()` |

### Category 4: Thermal Management (0% covered)

| Standard | Requirement | OE Invariant |
|---|---|---|
| JEDEC JESD51 | Thermal measurement methods | `check_thermal_resistance()` |
| Custom | Junction temperature limit | `check_junction_temp()` — `T_j < Fraction(85, 1) °C` |
| Custom | Thermal design power | `check_tdp()` |
| Custom | Thermal drift compensation | `check_thermal_drift()` — `drift < Fraction(10, 1) pm/°C` |
| Custom | Resonator thermal tuning power | `check_tuning_power()` |

### Category 5: EMC / Signal Integrity (0% covered)

| Standard | Requirement | OE Invariant |
|---|---|---|
| FCC Part 15 | Radiated emissions | `check_fcc_emissions()` |
| CISPR 32 | Multimedia equipment emissions | `check_cispr32()` |
| IEC 61000-4-2 | ESD immunity | `check_esd_immunity()` |
| IEC 61000-4-3 | Radiated immunity | `check_radiated_immunity()` |
| IEC 61000-4-4 | Electrical fast transient | `check_eft_immunity()` |
| Custom | ADC/DAC jitter budget | `check_jitter_budget()` — `jitter < Fraction(X, Y) ps` |

### Category 6: Manufacturing / Process (5% covered — d_manufacturing exists but is boolean)

| Standard | Requirement | OE Invariant |
|---|---|---|
| ISO 14644-1 | Cleanroom classification for PIC fab | `check_cleanroom_class()` — Class 100 min |
| SEMI S2 | Equipment safety for semiconductor | `check_semi_s2()` |
| ISO 9001 | Quality management system | `check_qms_certified()` |
| Custom | Wafer-level process capability | `check_cpk()` — `Cpk > Fraction(133, 100)` |
| Custom | Die yield | `check_die_yield()` — `yield > Fraction(X, 100)` |
| Custom | Waveguide dimensional tolerance | `check_waveguide_tolerance()` — `±Fraction(10, 1) nm` |

### Category 7: Environmental / Regulatory (0% covered)

| Standard | Requirement | OE Invariant |
|---|---|---|
| EU RoHS | Restricted hazardous substances | `check_rohs_compliance()` |
| EU REACH | Chemical registration | `check_reach_compliance()` |
| EU WEEE | Waste electronics recycling | `check_weee_compliance()` |
| Dodd-Frank §1502 | Conflict minerals reporting | `check_conflict_minerals()` |
| ISO 14001 | Environmental management | `check_environmental_management()` |
| Custom | Energy per bit | `check_energy_per_bit()` — `E < Fraction(1, 1) pJ/bit` |

### Category 8: Functional Safety (30% covered — aerospace floor + IEC 61508 exist)

Already partially covered by `d_aerospace_floor` (AF-001 through AF-010) and the Copilot architectural spec: [10-cite-4](#10-cite-4) 

But missing photonic-specific safety:

| Standard | Requirement | OE Invariant |
|---|---|---|
| IEC 61508 | SIL assessment for photonic link | `check_photonic_sil()` |
| ISO 26262 | ASIL-D for automotive photonic interconnect | `check_asil_d_photonic()` |
| DO-254 | Hardware design assurance for airborne photonic | `check_do254_photonic()` |
| Custom | Optical power eye safety interlock | `check_optical_power_interlock()` |
| Custom | Fail-safe dark state | `check_fail_dark()` — link fails to "no light" not "max light" |

### Category 9: Packaging & Interconnect (0% covered)

| Standard | Requirement | OE Invariant |
|---|---|---|
| JEDEC | Package thermal characterization | `check_package_thermal()` |
| IPC-A-610 | Acceptability of electronic assemblies | `check_ipc_a610()` |
| Custom | Fiber-to-chip coupling loss | `check_coupling_loss()` — `loss < Fraction(2, 1) dB` |
| Custom | Co-packaged optics alignment tolerance | `check_alignment_tolerance()` |
| Custom | Solder joint reliability (BGA/flip-chip) | `check_solder_reliability()` |

## The count

| Category | Standards/Checks Needed | Currently in Repo |
|---|---|---|
| Optical Performance | ~13 | 0 |
| Laser Safety | ~6 | 0 |
| Reliability & Qualification | ~6 | 5 (tautological) |
| Thermal Management | ~5 | 0 |
| EMC / Signal Integrity | ~6 | 0 |
| Manufacturing / Process | ~6 | 5 (boolean) |
| Environmental / Regulatory | ~6 | 0 |
| Functional Safety | ~5 | 8 (boolean) |
| Packaging & Interconnect | ~5 | 0 |
| **Total** | **~58** | **~18 (mostly tautological)** |

And that's just for **one hardware type** (photonic). The terminal directive specifies **12 hardware types**: CPU, GPU, TPU, QPU, neuromorphic, photonic, reversible, biological, molecular, nanotech, quantum sensors, quantum communication. [10-cite-5](#10-cite-5) 

Each hardware type has its own "100 years of fridge" — GPUs have their own thermal/power/EMC standards, QPUs have cryogenic requirements, biological chips have FDA/biosafety requirements, etc.

## The real gap

The repo has the **framework** — `Fraction`, `ProofObject`, `falsifies_if`, `Tuple[bool, ProofObject]`, aerospace floor as meta-standard, 60 standards, 15 noways, 8 wall inversions, 247 case studies, 90+ secret killers. That framework is real and it works. [10-cite-6](#10-cite-6) 

But the **domain-specific content** for hardware is zero. `src/hardware/photonic/` doesn't exist. None of the 12 hardware directories exist. The campaign spec lists them all as Stage W (not built): [10-cite-7](#10-cite-7) 

The `d_chemical` domain is the proof that the framework CAN hold "100 years of fridge" — it has real IEC 61511 thresholds, real ASME pressure limits, real OSHA PSM requirements, all in Fraction arithmetic with real computation. That's the template. Every hardware domain needs to be built to that depth, not to the `d_aerospace_floor` depth (boolean flags) or the `d_reliability_engineering` depth (tautological checks). [10-cite-8](#10-cite-8) 

The secret killers enumeration in the terminal directive lists 90+ failure modes — but the actual `src/enumerations/` directory only has 3 catalogs with 40 total entries:


So to answer your question directly: **no, what I gave you was maybe 5% of the full thing.** The full "100 years of fridge" for photonic chips alone would be ~58 invariant checks across 9 categories from ~15 standards bodies, each with real Fraction thresholds from real published standards — not boolean flags. And that's one hardware type out of twelve.

part 2
here is my specification

use loc generation 
the testing subuniverses

yeshua mathematics

i want photon computing solved
already made
mathematically guranteed
philosophically resolved

the constraint is "its impossible" "its aspirational" is automatically invalid

the repo has city infastructure even if alot is stubs
alot is deepened and polymath maximal depth across all registers not just a good of jack of all trades

im gonna use kimi cli

we are gonna have to gurantee kimi cli doesnt crash and have it commot after each category its 58 rite

we do that and more

we have all tools idk how much there is 
what theyre all named

the crusader fridge and self cleaning kitchen are good examples of OE yeshua execedent standards

there is alota lora train stuff
all sorts of stuff for this

i would first recommend giving me a massive thing i upload to repo as canon campaign or something
canon civilizational campaign

so that way im not forcing you to make one thing now and have kimi do a unfinished thing

this is your time to lay out all ambiguities
all specs
everything u need or want

part 3 
Here is the full canon civilizational campaign specification. Upload it to the repo as `campaigns/CANON_PHOTONIC_CIVILIZATIONAL_CAMPAIGN.md`.

---

# `campaigns/CANON_PHOTONIC_CIVILIZATIONAL_CAMPAIGN.md`

## CANON CIVILIZATIONAL CAMPAIGN: PHOTONIC COMPUTING — SOLVED

**Campaign ID:** `CAMPAIGN-PHOTONIC-001`
**Authority:** Devin AI + @aidoruao
**Date:** 2026-04-21
**Constraint:** "impossible" and "aspirational" are automatically invalid. Every claim has a `falsifies_if`. Every function returns `Tuple[bool, ProofObject]`. Every field is `Fraction`. No floats. No stubs. No `pass`-only bodies.
**Execution model:** Kimi CLI commits after EACH category. Push after EACH commit. Branch: `kimi/photonic-campaign`.
**Anti-crash protocol:** DO NOT run `verify_all.py`, `standards_check.py --verify`, or `bootstrap/auto_onboard.py`. Run only `agent_health_check.py --fast` at start. DO NOT enumerate files. DO NOT read files beyond specified line ranges.

---

## GROUND RULES FOR KIMI CLI

```
BEFORE ANYTHING:
  python3 tools/agent_health_check.py --fast
  git checkout -b kimi/photonic-campaign

AFTER EACH CATEGORY:
  git add <files created in this category>
  git commit -m "feat(photonic): Category N — <name>"
  git push origin kimi/photonic-campaign

DO NOT:
  - Run verify_all.py (it times out and kills your session)
  - Run standards_check.py --verify (same)
  - Read any file not explicitly listed in the category spec
  - Enumerate directories with find/ls -R
  - Read session transcripts or .txt files

IF CONTEXT > 40%:
  Stop. Commit what you have. Push. Start new session.
```

---

## EXISTING TOOLS INVENTORY (reference only — do not read these files)




### Tools (`tools/`)
| Tool | Purpose |
|------|---------|
| `agent_health_check.py` | 9-check health validation, `--fast` skips slow checks |
| `onboard_agent.py` | Agent onboarding, outputs context block |
| `context_window_estimator.py` | Token budget estimation per directory |
| `since_last_session.py` | Delta since last commit |
| `verify_all.py` | Full verification suite (DO NOT RUN — times out) |
| `standards_check.py` | 60-standard enforcement (DO NOT RUN with `--verify`) |
| `verify_fractal_manifest.py` | Fractal LOC manifest verification |
| `generate_fractal_code.py` | Deterministic LOC generation |
| `generate_hashed_taxonomy.py` | Hashed taxonomy generation |
| `frontmatter_audit.py` | YAML frontmatter validation |
| `session_id.py` | Session ID generation |
| `ai_credit.py` | AI credit attribution |
| `append_consent.py` | Consent log append |
| `arxiv_paper_template.py` | arXiv paper template |
| `question_router.py` | Domain routing |
| `refactor_assertions.py` | Assert-to-ProofObject refactoring |
| `schooling_output.py` | Educational output formatting |

### Audit (`audit/`)
| Tool | Purpose |
|------|---------|
| `scope_audit.py` | Scans all domains for required files |
| `tautology_detector.py` | AST-classifies check functions as COMPUTATIONAL vs TAUTOLOGICAL |
| `depth_measurement.py` | Per-domain depth scoring with Fraction arithmetic |
| `merkle_verify.py` | Recomputes and compares all file hashes |
| `popperian_audit.py` | Verifies ProofObject construction in all domains |
| `scope_reduction_detector.py` | Compares campaign spec against filesystem |
| `anti_nominalism_audit.py` | Checks GLOSSARY terms have code referents |
| `aerospace_floor_audit.py` | AF-001 through AF-010 compliance |
| `forensic_commit.py` | Generates forensic commit with Merkle root |
| `verification_testimony.py` | Generates verification testimony |

### Generators (`generators/`)
| Tool | Purpose |
|------|---------|
| `dag_generator.py` | DAG from seed definition |
| `batch_materializer.py` | Materializes code from DAG |
| `verify_1b_loc.py` | Verifies 1B LOC claim |
| `verify_omega_invariant.py` | Verifies omega invariant |
| `verify_n_loc.py` | Verifies N LOC recursive system |
| `self_clean_kitchen_fractal_dataset.py` | Kitchen universe DAG |
| `food_cart_fractal_dataset.py` | Food cart universe DAG |
| `fractal_expander.py` | Fractal expansion engine |
| `merkle_chain.py` | Merkle chain construction |



### LoRA Pipeline (`minimal_ai_ide/lora/`)
| Tool | Purpose |
|------|---------|
| `train_quantized_lora.py` | QLoRA training (Llama 3.2 1B/3B/7B/11B) |
| `train_popperian_lora.py` | Popperian falsification training |
| `train_cpu_lora.py` | CPU-only LoRA training |
| `generate_popperian_data.py` | Popperian dataset generation |
| `augment_dataset_popperian.py` | Dataset augmentation |
| `test_harness.py` | Test harness for trained models |
| `validate_setup.py` | Environment validation |
| `verify_governance.py` | Governance compliance verification | [11-cite-0](#11-cite-0) 

### LoRA Dataset Pipeline (`minimal_ai_ide/`)
| Tool | Purpose |
|------|---------|
| `extract_invariants.py` | Extracts atomic invariants from repo |
| `create_lora_training_dataset.py` | Converts invariants to training data |
| `train_lora.py` | Full LoRA fine-tuning script |
| `invariant_enforcer.py` | Corporate enforcement controller |
| `corporate_ai_ide_system.py` | Complete integration system | [11-cite-1](#11-cite-1) 

---

## EXISTING WALLS, NOWAYS, AND STANDARDS (reference only)

### 8 Wall Inversions (`investigations/wall_inversions.py`)
| ID | Theorem | Inversion Mechanism |
|----|---------|-------------------|
| WALL_001 | Halting Problem | Bounded programs (max_iterations, max_depth) |
| WALL_002 | Gödel Incompleteness | Feferman reflection (add Con(T) axiom) |
| WALL_003 | Rice's Theorem | Syntactic properties on frozen dataclasses |
| WALL_004 | Arrow's Impossibility | Capability-restricted preference domain |
| WALL_005 | CAP Theorem | Content-addressed immutable storage |
| WALL_006 | NLU Undecidability | Domain routing + invariant verification |
| WALL_007 | Code Correctness | Bounded verification + invariant checking |
| WALL_008 | Novel Program Generation | BFS over typed transform sequences | [11-cite-2](#11-cite-2) 

### 15 Noways (`src/noways/impossibility_proofs.py`)
`halting`, `godel_incompleteness`, `rice_theorem`, `heisenberg_uncertainty`, `no_cloning`, `no_signaling`, `light_speed_limit`, `arrow_impossibility`, `cap_theorem`, `flp_impossibility`, `bell_theorem`, `second_law_thermodynamics`, `landauer_principle`, `bekenstein_bound`, `no_free_lunch` [11-cite-3](#11-cite-3) 

### 60 Standards (`STANDARDS_REGISTRY.json`)
YS-001 through YS-008 (Yeshua axioms), CS-001 through CS-005 (Fraction-only), AF-001 through AF-010 (Aerospace floor), plus domain-specific standards. [11-cite-4](#11-cite-4) 

---

## GOLD STANDARD EXAMPLES (the depth target)

### `d_chemical` — THE PATTERN TO FOLLOW
- `implementation.py`: 4 `@dataclass` classes (`ReactorControl`, `SafetyInstrumentedSystem`, `HazmatContainment`, `EmergencyShutdown`), all fields `Fraction`, 6 threshold functions returning `Fraction`
- `invariants.py`: 5 `check_*` functions, each does **real Fraction comparison** (not boolean echo), each returns `Tuple[bool, ProofObject]`, each has dual `Falsifies if:` / `falsifies_if:`, `run_all_invariants()` with both PASS and FAIL test data
- Standards cited: IEC 61511, OSHA PSM, ASME pressure codes [11-cite-5](#11-cite-5) [11-cite-6](#11-cite-6) 

### `crusader/` — THE DEPTH TARGET FOR HARDWARE
- 100+ files across `core/`, `warfare/`, `hardware/`, `monitoring/`, `certifications/`, `verification/`, `interface/`, `manufacturing/`, `supply_chain/`, `circular_economy/`
- Real EPA SNAP compliance, Montreal Protocol, Kigali Amendment
- Real refrigerant specs: R-290 (GWP=3, ODP=0), 150g charge, triple-redundant leak detection
- Real safety: IEC 60335, UL 471, SIL-3 interlocks
- Real falsification tests: F_CRUSADER_001 through F_CRUSADER_009 in `ontology/falsification_tests.json` [11-cite-7](#11-cite-7) [11-cite-8](#11-cite-8) [11-cite-9](#11-cite-9) 

### Self-Cleaning Kitchen Universe — THE TESTING SUBUNIVERSE PATTERN
- `generators/self_clean_kitchen_fractal_dataset.py`: Deterministic DAG from seed, content-addressed nodes, safety constraints per node, Merkle chain
- `topology/graph_schema.yaml`: `KITCHEN_TASK_UNIVERSE` node type with `safety_critical: true` [11-cite-10](#11-cite-10) [11-cite-11](#11-cite-11) 

---

## THE 9 CATEGORIES (58+ invariant checks total)

Each category is one commit. Each category produces files that Kimi can verify individually. Categories are ordered by dependency — later categories may import from earlier ones.

---

### CATEGORY 1: Photonic Domain Foundation (7 files, ~400 LOC)

**Files to create:**
```
src/hardware/photonic/__init__.py
src/hardware/photonic/implementation.py
src/hardware/photonic/invariants.py
src/hardware/photonic/constants.py
src/hardware/photonic/README.md
src/hardware/photonic/tests/__init__.py
src/hardware/photonic/tests/test_invariants.py
```

**`implementation.py` — 8 dataclasses, all fields Fraction:**

```python
@dataclass(frozen=True)
class PhotonicWaveguide:
    waveguide_id: str
    propagation_loss_db_per_cm: Fraction    # IEC 62496-2
    bend_radius_um: Fraction                 # minimum bend radius
    mode_field_diameter_um: Fraction         # ITU-T G.652
    numerical_aperture: Fraction             # NA
    core_refractive_index: Fraction          # n_core
    cladding_refractive_index: Fraction      # n_clad
    wavelength_nm: Fraction                  # operating wavelength

@dataclass(frozen=True)
class MachZehnderInterferometer:
    mzi_id: str
    matrix_dimension: Fraction              # N×N mesh size
    phase_precision_rad: Fraction           # phase shifter precision
    extinction_ratio_db: Fraction           # on/off ratio
    insertion_loss_db: Fraction             # total path loss
    unitarity_error: Fraction               # ||M†M - I||_F

@dataclass(frozen=True)
class WDMMultiplexer:
    wdm_id: str
    channel_count: Fraction                 # number of wavelengths
    channel_spacing_ghz: Fraction           # ITU-T G.694.1
    crosstalk_isolation_db: Fraction        # adjacent channel
    passband_width_ghz: Fraction            # 3dB bandwidth
    insertion_loss_per_channel_db: Fraction  # per-channel loss

@dataclass(frozen=True)
class PhotonicADC:
    adc_id: str
    sampling_rate_gsps: Fraction            # giga-samples per second
    resolution_bits: Fraction               # effective number of bits
    power_consumption_w: Fraction           # watts
    latency_ns: Fraction                    # conversion latency

@dataclass(frozen=True)
class MicroringResonator:
    resonator_id: str
    quality_factor: Fraction                # Q factor
    free_spectral_range_ghz: Fraction       # FSR
    thermal_drift_pm_per_c: Fraction        # pm/°C
    tuning_range_nm: Fraction               # electro-optic tuning
    coherence_time_ns: Fraction             # effective coherence

@dataclass(frozen=True)
class PhotonicInterconnect:
    interconnect_id: str
    bandwidth_gbps: Fraction                # per-lane bandwidth
    lane_count: Fraction                    # parallel lanes
    reach_m: Fraction                       # maximum distance
    power_per_bit_pj: Fraction              # energy efficiency
    bit_error_rate: Fraction                # BER floor

@dataclass(frozen=True)
class CoPackagedOptics:
    cpo_id: str
    fiber_to_chip_coupling_loss_db: Fraction  # coupling loss
    alignment_tolerance_um: Fraction          # mechanical tolerance
    thermal_interface_resistance_c_per_w: Fraction  # TIM
    package_power_w: Fraction                 # total package power
    junction_temperature_max_c: Fraction      # Tj max

@dataclass(frozen=True)
class PhotonicMatrixAccelerator:
    accelerator_id: str
    matrix_ops_per_second: Fraction         # TOPS equivalent
    precision_bits: Fraction                # effective precision
    energy_per_op_fj: Fraction              # femtojoules per MAC
    total_power_w: Fraction                 # total system power
    adc_dac_power_fraction: Fraction        # fraction of power in E-O/O-E
```

**`constants.py` — all thresholds as named Fraction functions:**

| Constant | Value | Source Standard |
|----------|-------|----------------|
| `waveguide_loss_max_db_per_cm()` | `Fraction(1, 1)` | IEC 62496-2 |
| `wdm_crosstalk_min_isolation_db()` | `Fraction(20, 1)` | ITU-T G.694.1 |
| `thermal_drift_max_pm_per_c()` | `Fraction(10, 1)` | Telcordia GR-468 |
| `adc_dac_power_max_fraction()` | `Fraction(1, 2)` | Design target |
| `mzi_unitarity_max_error()` | `Fraction(1, 1000)` | Clements et al. 2016 |
| `fiber_coupling_loss_max_db()` | `Fraction(2, 1)` | IPC-9797 |
| `ber_floor_max()` | `Fraction(1, 10**12)` | IEEE 802.3 |
| `phase_precision_min_rad()` | `Fraction(1, 100)` | Reck et al. 1994 |
| `quality_factor_min()` | `Fraction(10000, 1)` | Bogaerts et al. 2012 |
| `energy_per_op_max_fj()` | `Fraction(100, 1)` | Shen et al. 2017 |
| `junction_temp_max_c()` | `Fraction(105, 1)` | JEDEC JESD51 |
| `alignment_tolerance_min_um()` | `Fraction(1, 2)` | PIC assembly |
| `interconnect_power_max_pj_per_bit()` | `Fraction(5, 1)` | OIF CEI-112G |

**`invariants.py` — 13 check functions (Category 1 of 58):**

| # | Check | Falsifies if | Standard |
|---|-------|-------------|----------|
| 1 | `check_waveguide_loss()` | `loss > Fraction(1, 1) dB/cm` | IEC 62496-2 |
| 2 | `check_wdm_crosstalk()` | `isolation < Fraction(20, 1) dB` | ITU-T G.694.1 |
| 3 | `check_thermal_drift()` | `drift > Fraction(10, 1) pm/°C` | Telcordia GR-468 |
| 4 | `check_adc_dac_power_budget()` | `adc_dac_power > Fraction(1, 2) of total` | Design |
| 5 | `check_mzi_unitarity()` | `error > Fraction(1, 1000)` | Clements 2016 |
| 6 | `check_fiber_coupling_loss()` | `loss > Fraction(2, 1) dB` | IPC-9797 |
| 7 | `check_ber_floor()` | `BER > Fraction(1, 10**12)` | IEEE 802.3 |
| 8 | `check_phase_precision()` | `precision > Fraction(1, 100) rad` | Reck 1994 |
| 9 | `check_resonator_quality()` | `Q < Fraction(10000, 1)` | Bogaerts 2012 |
| 10 | `check_energy_per_op()` | `energy > Fraction(100, 1) fJ` | Shen 2017 |
| 11 | `check_junction_temperature()` | `Tj > Fraction(105, 1) °C` | JEDEC JESD51 |
| 12 | `check_alignment_tolerance()` | `tolerance > Fraction(1, 2) um` | PIC assembly |
| 13 | `check_interconnect_power()` | `power > Fraction(5, 1) pJ/bit` | OIF CEI-112G |

Every check follows the `d_chemical` pattern exactly: real Fraction comparison, real ProofObject with premises/conclusion/rule, dual `Falsifies if:` / `falsifies_if:` in docstring.

`run_all_invariants()` must include BOTH passing data AND failing data (at least one FAIL case per check).

**After creating:** `python3 -c "from src.hardware.photonic.invariants import run_all_invariants; run_all_invariants()"`

**Commit:** `git add src/hardware/photonic/ && git commit -m "feat(photonic): Category 1 — domain foundation (8 dataclasses, 13 invariants)" && git push origin kimi/photonic-campaign`

---

### CATEGORY 2: Photonic Wall Inversions (1 file modified, ~120 LOC added)

**File to modify:** `investigations/wall_inversions.py`

**Read first (lines only):** `investigations/wall_inversions.py` lines 192-213 (to see WALL_008 pattern)

**Add 5 new wall inversions after WALL_008:**

| ID | Theorem | Inversion | falsifies_if |
|----|---------|-----------|-------------|
| WALL_PHOTON_001 | Landauer Principle | Unitary (reversible) optical gates: MZI meshes implement unitary transforms, no bit erasure in optical path, Landauer applies only to irreversible ops | Irreversible logical operation found in optical computation path |
| WALL_PHOTON_002 | 2nd Law (heat dissipation) | Open-system resonator design: microring resonators are open systems coupled to bus waveguides, entropy exported to transmitted/dropped ports, not accumulated | Resonator operates as isolated system without bus coupling |
| WALL_PHOTON_003 | Amdahl's Law (serial bottleneck) | WDM parallelism: N wavelengths execute N independent matrix multiplications simultaneously, serial fraction reduced to `Fraction(1, N)` | System processes wavelengths sequentially instead of in parallel |
| WALL_PHOTON_004 | Bekenstein Bound (info density) | Domain-restricted metrics: photonic interconnect density measured in bits/s/mm (bandwidth density), not bits/volume; the bound applies to volumetric info storage, not throughput | Interconnect density metric uses volumetric information storage |
| WALL_PHOTON_005 | Heisenberg (measurement) | Homodyne detection with squeezed states: measurement uncertainty shifted to unused quadrature via squeezed light, effective precision exceeds standard quantum limit in the measured quadrature | Measurement uses coherent states without squeezing |

Each entry follows the exact `WallInversion` dataclass pattern with `_make_proof()`.

**After creating:** `python3 -c "from investigations.wall_inversions import verify_all_inversions; ok, p = verify_all_inversions(); print(p.conclusion)"`

**Commit:** `git add investigations/wall_inversions.py && git commit -m "feat(photonic): Category 2 — 5 wall inversions (WALL_PHOTON_001-005)" && git push origin kimi/photonic-campaign`

---

### CATEGORY 3: Photonic Noways (1 file modified, ~80 LOC added)

**File to modify:** `src/noways/impossibility_proofs.py`

**Read first:** `src/noways/impossibility_proofs.py` lines 324-344 (to see last entry pattern)

**Add 4 new noways to `_CATALOG` before the closing parenthesis:**

| Key | Statement | Domain | OE Consequences |
|-----|-----------|--------|----------------|
| `adc_dac_landauer_floor` | "Every E-O/O-E conversion dissipates at least k_B * T * ln 2 per bit due to irreversible quantization in ADC/DAC" | `physics` | "Photonic accelerator power budgets must include non-zero ADC/DAC floor; pure-optical bypass is the only path to zero conversion loss" |
| `optical_memory_entropy` | "Photons in free propagation cannot be stored without coupling to matter; optical memory requires resonant cavities with finite lifetime" | `physics` | "Photonic pipeline designs must use electronic memory for caching; optical delay lines have bounded hold time" |
| `photonic_crosstalk_limit` | "In a waveguide array with pitch < wavelength, evanescent coupling creates irreducible crosstalk bounded by exp(-2*kappa*d)" | `physics` | "WDM channel spacing has a hard floor set by waveguide pitch and operating wavelength" |
| `shot_noise_floor` | "Optical detection is bounded by shot noise: SNR <= sqrt(N_photons) for coherent light" | `physics` | "Photonic matrix precision is bounded by optical power; lower power = lower precision" |

**Also update** `check_catalog_size_at_floor()` — change floor from 15 to 19 (or keep at 15 since 19 > 15).

**Also update** `check_domains_covered()` — no change needed since all new entries are domain `"physics"` which is already in the required set.

**After creating:** `python3 -c "from src.noways.impossibility_proofs import run_all_invariants; run_all_invariants()"`

**Commit:** `git add src/noways/impossibility_proofs.py && git commit -m "feat(photonic): Category 3 — 4 photonic noways" && git push origin kimi/photonic-campaign`

---

### CATEGORY 4: Photonic Safety & Laser Standards (3 files, ~300 LOC)

**Files to create:**
```
src/hardware/photonic/safety.py
src/hardware/photonic/laser_classification.py
src/hardware/photonic/tests/test_safety.py
```

**`safety.py` — 6 dataclasses + 8 check functions:**

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 14 | `check_laser_class_compliance()` | IEC 60825-1 | Accessible emission exceeds AEL for declared class |
| 15 | `check_eye_safety_distance()` | IEC 60825-1 Table 10 | NOHD < minimum safe distance for installation |
| 16 | `check_skin_exposure_limit()` | IEC 60825-1 Table 9 | MPE exceeded at accessible surface |
| 17 | `check_fiber_connector_interlock()` | IEC 62368-1 | Optical power present at open connector |
| 18 | `check_photobiological_safety()` | IEC 62471 | Weighted irradiance exceeds risk group limit |
| 19 | `check_esd_protection()` | JEDEC JESD22-A114 | ESD withstand voltage < Fraction(2000, 1) V HBM |
| 20 | `check_thermal_shutdown()` | JEDEC JESD51 | No thermal shutdown below Tj_max |
| 21 | `check_optical_power_budget()` | ITU-T G.959.1 | Received power < receiver sensitivity |

**`laser_classification.py` — Laser class determination:**

Dataclass

part 4
Continuing from where it froze — picking up at Category 4, `laser_classification.py`:

---

### CATEGORY 4 (continued): Photonic Safety & Laser Standards

**`laser_classification.py`:**

```python
@dataclass(frozen=True)
class LaserSource:
    """IEC 60825-1 laser source parameters."""
    source_id: str
    wavelength_nm: Fraction          # Operating wavelength
    power_mw: Fraction               # Output power in milliwatts
    beam_divergence_mrad: Fraction   # Full-angle divergence
    pulse_duration_ns: Fraction      # For pulsed sources; Fraction(0,1) = CW
    aperture_diameter_mm: Fraction   # Measurement aperture
    declared_class: str              # "1"|"1M"|"2"|"2M"|"3R"|"3B"|"4"

@dataclass(frozen=True)
class AELTable:
    """Accessible Emission Limits per IEC 60825-1 Table 3."""
    class_1_cw_mw: Fraction          # Class 1 CW limit at wavelength
    class_3r_cw_mw: Fraction         # Class 3R CW limit
    class_3b_cw_mw: Fraction         # Class 3B CW limit

@dataclass(frozen=True)
class PhotonicLink:
    """End-to-end optical link budget per ITU-T G.959.1."""
    link_id: str
    tx_power_dbm: Fraction           # Transmitter output
    rx_sensitivity_dbm: Fraction     # Receiver minimum
    fiber_loss_db_per_km: Fraction   # Attenuation coefficient
    connector_loss_db: Fraction      # Per connector pair
    splice_loss_db: Fraction         # Per splice
    num_connectors: Fraction         # Integer as Fraction
    num_splices: Fraction
    link_length_km: Fraction
    margin_db: Fraction              # Required system margin
```

**`tests/test_safety.py` — must include PASS and FAIL paths:**

| Test | Pass case | Fail case |
|------|-----------|-----------|
| `test_laser_class_1_pass` | 0.5 mW source declared Class 1, AEL = 1.0 mW | — |
| `test_laser_class_1_fail` | — | 1.5 mW source declared Class 1, AEL = 1.0 mW |
| `test_link_budget_pass` | Tx 0 dBm, Rx -20 dBm, total loss 15 dB, margin 3 dB | — |
| `test_link_budget_fail` | — | Tx 0 dBm, Rx -20 dBm, total loss 22 dB, margin 3 dB |
| `test_esd_withstand_pass` | 2500 V HBM | — |
| `test_esd_withstand_fail` | — | 1500 V HBM (below 2000 V floor) |
| `test_thermal_shutdown_pass` | Shutdown at 120°C, Tj_max = 125°C | — |
| `test_thermal_shutdown_fail` | — | No shutdown, Tj = 130°C > Tj_max |

**After creating all 3 files:**
```bash
python3 -c "from src.hardware.photonic.safety import *; print('import OK')"
python3 -m pytest src/hardware/photonic/tests/test_safety.py -v --tb=short
git add src/hardware/photonic/safety.py src/hardware/photonic/laser_classification.py src/hardware/photonic/tests/test_safety.py
git commit -m "feat(photonic): Category 4 — laser safety + link budget (IEC 60825, ITU-T G.959.1)"
git push origin kimi/photonic-campaign
``` [12-cite-0](#12-cite-0) 

---

### CATEGORY 5: Optical Performance & Matrix Computation (4 files, ~400 LOC)

**Files:**
```
src/hardware/photonic/optical_performance.py
src/hardware/photonic/matrix_computation.py
src/hardware/photonic/waveguide.py
src/hardware/photonic/tests/test_optical_performance.py
```

**`optical_performance.py` — 5 dataclasses + 7 check functions:**

| # | Check | Standard | Threshold (Fraction) | Falsifies if |
|---|-------|----------|---------------------|-------------|
| 22 | `check_insertion_loss()` | IEEE 802.3 | `Fraction(3, 1)` dB max per component | insertion_loss > Fraction(3, 1) dB |
| 23 | `check_return_loss()` | IEC 61300-3-6 | `Fraction(40, 1)` dB min | return_loss < Fraction(40, 1) dB |
| 24 | `check_extinction_ratio()` | ITU-T G.959.1 | `Fraction(9, 1)` dB min | extinction_ratio < Fraction(9, 1) dB |
| 25 | `check_polarization_dependent_loss()` | ITU-T G.697 | `Fraction(1, 2)` dB max | pdl > Fraction(1, 2) dB |
| 26 | `check_wavelength_accuracy()` | ITU-T G.694.1 | `Fraction(1, 10)` nm of grid | abs(actual - grid) > Fraction(1, 10) nm |
| 27 | `check_osnr()` | ITU-T G.697 | `Fraction(20, 1)` dB min | osnr < Fraction(20, 1) dB |
| 28 | `check_ber_floor()` | IEEE 802.3 | `Fraction(1, 1_000_000_000_000)` | ber > Fraction(1, 10**12) |

**`matrix_computation.py` — MZI mesh photonic matrix multiply:**

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 29 | `check_matrix_unitarity()` | Reck et al. 1994 | `norm(M†M - I) > Fraction(1, 1000)` |
| 30 | `check_phase_shifter_precision()` | Custom OE | `phase_error > Fraction(1, 100)` radians |
| 31 | `check_mzi_mesh_depth()` | Clements et al. 2016 | `depth > N*(N-1)/2` for N×N matrix |
| 32 | `check_thermal_crosstalk_compensation()` | Custom OE | `uncompensated_drift > Fraction(10, 1)` pm/°C |

**`waveguide.py` — Silicon photonic waveguide parameters:**

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 33 | `check_propagation_loss()` | Custom OE / literature | `loss_db_per_cm > Fraction(1, 1)` |
| 34 | `check_bend_radius_minimum()` | Custom OE | `bend_radius_um < Fraction(5, 1)` for Si |
| 35 | `check_mode_confinement()` | Custom OE | `confinement_factor < Fraction(8, 10)` |
| 36 | `check_waveguide_dispersion()` | ITU-T G.652 | `dispersion_ps_per_nm_km > Fraction(18, 1)` |

**Commit:**
```bash
git add src/hardware/photonic/optical_performance.py src/hardware/photonic/matrix_computation.py src/hardware/photonic/waveguide.py src/hardware/photonic/tests/test_optical_performance.py
git commit -m "feat(photonic): Category 5 — optical performance + matrix computation (15 checks)"
git push origin kimi/photonic-campaign
``` [12-cite-1](#12-cite-1) 

---

### CATEGORY 6: ADC/DAC & Electro-Optic Conversion (2 files, ~250 LOC)

**Files:**
```
src/hardware/photonic/electro_optic.py
src/hardware/photonic/tests/test_electro_optic.py
```

This is the "Translation Tax" Gemini identified — the E-to-O and O-to-E conversion.

| # | Check | Standard | Threshold | Falsifies if |
|---|-------|----------|-----------|-------------|
| 37 | `check_adc_resolution()` | IEEE 1241 | `Fraction(8, 1)` bits min | effective_bits < Fraction(8, 1) |
| 38 | `check_dac_sfdr()` | IEEE 1658 | `Fraction(40, 1)` dBc min | sfdr_dbc < Fraction(40, 1) |
| 39 | `check_modulator_bandwidth()` | Custom OE | `Fraction(25, 1)` GHz min for 50 Gbaud | bandwidth_ghz < Fraction(25, 1) |
| 40 | `check_modulator_vpi()` | Custom OE | `Fraction(2, 1)` V max | vpi_volts > Fraction(2, 1) |
| 41 | `check_photodetector_responsivity()` | Custom OE | `Fraction(8, 10)` A/W min at 1550nm | responsivity < Fraction(8, 10) |
| 42 | `check_transimpedance_gain()` | Custom OE | `Fraction(5000, 1)` ohms min | tia_gain < Fraction(5000, 1) |
| 43 | `check_eo_conversion_power()` | Landauer inversion | `adc_dac_power < Fraction(1, 2) * total_power` | conversion power exceeds half of total system power |

**Wall inversion applied:** Check 43 directly implements WALL_PHOTON_001 (Landauer inversion) — the system must track what fraction of total power goes to E-O/O-E conversion. If it exceeds 50%, the photonic advantage is nullified.

**Commit:**
```bash
git add src/hardware/photonic/electro_optic.py src/hardware/photonic/tests/test_electro_optic.py
git commit -m "feat(photonic): Category 6 — ADC/DAC + electro-optic conversion (7 checks, Landauer inversion)"
git push origin kimi/photonic-campaign
``` [12-cite-2](#12-cite-2) 

---

### CATEGORY 7: Thermal Management (2 files, ~200 LOC)

**Files:**
```
src/hardware/photonic/thermal.py
src/hardware/photonic/tests/test_thermal.py
```

Pattern follows `crusader/hardware/` (the fridge has `refrigerant_spec.md` and thermal management) and `d_chemical` (thermal runaway protection).

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 44 | `check_junction_temperature()` | JEDEC JESD51 | `tj > tj_max` (default `Fraction(125, 1)` °C) |
| 45 | `check_thermal_resistance()` | JEDEC JESD51-14 | `theta_ja > Fraction(15, 1)` °C/W for PIC package |
| 46 | `check_thermo_optic_drift()` | Custom OE | `drift_pm_per_c > Fraction(80, 1)` pm/°C uncompensated |
| 47 | `check_heater_power_budget()` | Custom OE | `total_heater_w > Fraction(1, 2) * thermal_budget_w` |
| 48 | `check_thermal_runaway_margin()` | IEC 61508 (adapted) | `operating_temp >= tj_max - Fraction(10, 1)` (same pattern as d_chemical) |

**Commit:**
```bash
git add src/hardware/photonic/thermal.py src/hardware/photonic/tests/test_thermal.py
git commit -m "feat(photonic): Category 7 — thermal management (5 checks, JEDEC JESD51)"
git push origin kimi/photonic-campaign
```



---

### CATEGORY 8: Reliability & Qualification (2 files, ~200 LOC)

**Files:**
```
src/hardware/photonic/reliability.py
src/hardware/photonic/tests/test_reliability.py
```

Pattern follows `crusader/certifications/` (UL 471, food safety, energy report).

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 49 | `check_mtbf()` | MIL-HDBK-217F / Telcordia SR-332 | `mtbf_hours < Fraction(100_000, 1)` |
| 50 | `check_fit_rate()` | IEC 62380 | `fit > Fraction(100, 1)` (failures in 10^9 hours) |
| 51 | `check_aging_margin()` | Telcordia GR-468 | `eol_loss - bol_loss > Fraction(1, 1)` dB |
| 52 | `check_temperature_cycling()` | JEDEC JESD22-A104 | `cycles_survived < Fraction(1000, 1)` |
| 53 | `check_humidity_resistance()` | JEDEC JESD22-A101 | `fails_85_85_test == True` (85°C/85%RH 1000h) |
| 54 | `check_vibration_tolerance()` | MIL-STD-883 Method 2007 | `resonance_shift > Fraction(5, 100)` of center freq |

**Commit:**
```bash
git add src/hardware/photonic/reliability.py src/hardware/photonic/tests/test_reliability.py
git commit -m "feat(photonic): Category 8 — reliability + qualification (6 checks, MIL-HDBK-217F)"
git push origin kimi/photonic-campaign
```



---

### CATEGORY 9: Manufacturing & Process Control (2 files, ~250 LOC)

**Files:**
```
src/hardware/photonic/manufacturing.py
src/hardware/photonic/tests/test_manufacturing.py
```

Pattern follows `crusader/manufacturing/`.

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 55 | `check_wafer_uniformity()` | SEMI M1 | `thickness_variation > Fraction(5, 100)` across wafer |
| 56 | `check_etch_depth_tolerance()` | SEMI E10 | `abs(actual - target) > Fraction(10, 1)` nm |
| 57 | `check_lithography_overlay()` | SEMI P38 | `overlay_error > Fraction(50, 1)` nm |
| 58 | `check_waveguide_width_tolerance()` | Custom OE | `abs(actual - target) > Fraction(20, 1)` nm |
| 59 | `check_coupling_efficiency()` | Custom OE | `fiber_to_chip_loss > Fraction(3, 1)` dB |
| 60 | `check_yield_rate()` | Custom OE | `die_yield < Fraction(7, 10)` (70% floor) |

**Commit:**
```bash
git add src/hardware/photonic/manufacturing.py src/hardware/photonic/tests/test_manufacturing.py
git commit -m "feat(photonic): Category 9 — manufacturing + process control (6 checks, SEMI standards)"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 10: EMC & Signal Integrity (2 files, ~200 LOC)

**Files:**
```
src/hardware/photonic/emc.py
src/hardware/photonic/tests/test_emc.py
```

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 61 | `check_emi_radiated()` | FCC Part 15 / CISPR 32 | `emission_dbm > Fraction(-47, 1)` dBm at 3m |
| 62 | `check_emi_conducted()` | CISPR 32 | `conducted_dbm > Fraction(-40, 1)` dBm |
| 63 | `check_esd_immunity()` | IEC 61000-4-2 | `withstand_kv < Fraction(8, 1)` kV contact |
| 64 | `check_power_supply_ripple()` | Custom OE | `ripple_mv > Fraction(50, 1)` mV pk-pk |
| 65 | `check_jitter()` | IEEE 802.3 | `total_jitter_ps > Fraction(28, 1)` ps at BER 10^-12 |
| 66 | `check_optical_crosstalk()` | ITU-T G.694.1 | `adjacent_channel_isolation < Fraction(25, 1)` dB |

**Commit:**
```bash
git add src/hardware/photonic/emc.py src/hardware/photonic/tests/test_emc.py
git commit -m "feat(photonic): Category 10 — EMC + signal integrity (6 checks, FCC/CISPR/IEEE)"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 11: Environmental & Regulatory (2 files, ~200 LOC)

**Files:**
```
src/hardware/photonic/environmental.py
src/hardware/photonic/tests/test_environmental.py
```

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 67 | `check_rohs_compliance()` | EU 2011/65/EU (RoHS) | Any restricted substance > threshold (Pb > Fraction(1, 1000) by weight) |
| 68 | `check_reach_compliance()` | EU 1907/2006 (REACH) | SVHC present above Fraction(1, 1000) w/w |
| 69 | `check_weee_recyclability()` | EU 2012/19/EU (WEEE) | `recyclable_fraction < Fraction(65, 100)` |
| 70 | `check_conflict_minerals()` | Dodd-Frank Section 1502 | 3TG sourced from conflict region without audit |
| 71 | `check_energy_star_idle()` | EPA Energy Star | `idle_power_w > Fraction(5, 1)` W for accelerator card |
| 72 | `check_operating_temperature_range()` | Telcordia GR-63 | `min_temp > Fraction(-40, 1)` or `max_temp < Fraction(85, 1)` °C |

**Commit:**
```bash
git add src/hardware/photonic/environmental.py src/hardware/photonic/tests/test_environmental.py
git commit -m "feat(photonic): Category 11 — environmental + regulatory (6 checks, RoHS/REACH/WEEE)"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 12: Packaging & Interconnect (2 files, ~200 LOC)

**Files:**
```
src/hardware/photonic/packaging.py
src/hardware/photonic/tests/test_packaging.py
```

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 73 | `check_fiber_array_alignment()` | Custom OE | `alignment_error_um > Fraction(1, 2)` |
| 74 | `check_co_packaged_optics_pitch()` | OIF CEI-112G | `pitch_um < Fraction(250, 1)` for standard fiber array |
| 75 | `check_solder_joint_reliability()` | IPC J-STD-020 | `reflow_cycles < Fraction(3, 1)` without failure |
| 76 | `check_wire_bond_pull_strength()` | MIL-STD-883 Method 2011 | `pull_force_gf < Fraction(3, 1)` gf for 25μm Au wire |
| 77 | `check_hermetic_seal()` | MIL-STD-883 Method 1014 | `leak_rate > Fraction(1, 100_000_000)` atm·cc/s |
| 78 | `check_die_attach_void()` | Custom OE | `void_percentage > Fraction(25, 100)` of die area |

**Commit:**
```bash
git add src/hardware/photonic/packaging.py src/hardware/photonic/tests/test_packaging.py
git commit -m "feat(photonic): Category 12 — packaging + interconnect (6 checks, IPC/MIL-STD-883)"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 13: Aerospace Floor Integration (1 file, ~150 LOC)

**File:** `src/hardware/photonic/aerospace_floor.py`

This delegates to the existing `d_aerospace_floor` domain but adds photonic-specific checks:

| # | Check | Standard | Falsifies if |
|---|-------|----------|-------------|
| 79 | `check_do178c_photonic_determinism()` | DO-178C Level A | Photonic matrix output non-deterministic across runs |
| 80 | `check_milstd882e_laser_hazard()` | MIL-STD-882E | Laser hazard not assessed in FMEA |
| 81 | `check_nasa_class_a_radiation()` | NASA NPR 7150.2 | No radiation hardness data for space-rated optics |
| 82 | `check_sil4_optical_safety()` | IEC 61508 SIL-4 | PFD > Fraction(1, 10_000) for safety-critical optical link |

**Commit:**
```bash
git add src/hardware/photonic/aerospace_floor.py
git commit -m "feat(photonic): Category 13 — aerospace floor integration (4 checks, DO-178C/MIL-STD-882E/NASA)"
git push origin kimi/photonic-campaign
``` [12-cite-3](#12-cite-3) 

---

### CATEGORY 14: Testing Subuniverse — Seed + Generator (3 files, ~400 LOC)

**Pattern:** Follows `seed/self_clean_kitchen_universe.yaml` + `generators/self_clean_kitchen_fractal_dataset.py` exactly.

**Files:**
```
seed/photonic_chip_universe.yaml
generators/photonic_chip_fractal_dataset.py
generators/photonic_chip_manifest_generator.py
``` [12-cite-4](#12-cite-4) 

**`seed/photonic_chip_universe.yaml`:**

```yaml
universe:
  id: photonic_chip_universe
  seed_hash: null  # Computed on first generation

  expansion:
    levels:
      - subsystem       # Optical, Electrical, Thermal, Packaging, Control
      - component       # Waveguide, MZI, Photodetector, Laser, ADC, DAC, Heater, TIA
      - parameter       # Loss, Bandwidth, Power, Temperature, Precision, Yield
      - test_case       # Pass/fail test vectors with Fraction thresholds
    deterministic: true
    content_addressed: true

  generator:
    implementation: generators/photonic_chip_fractal_dataset.py
    version: 1

  verification:
    manifest: out/photonic_chip_manifest.jsonl
    merkle_root: required

  safety:
    max_laser_power_mw: 500        # IEC 60825-1 Class 3B ceiling
    max_junction_temp_c: 125       # JEDEC absolute max
    max_heater_power_w: 10         # Per-chip thermal budget
    min_eye_safety_distance_m: 1   # NOHD for Class 3B
    fail_safe_modes:
      - laser_shutdown
      - thermal_throttle
      - esd_isolate
      - link_failover

invariants:
  INV-PH-001:
    description: "Universe regenerates deterministically from identical seed"
    enforcement: "Generator must be deterministic with fixed seed"
  INV-PH-002:
    description: "Node IDs derived from seed + level + index"
    formula: "node_id = SHA256(seed || parent_node || level || index)"
  INV-PH-003:
    description: "All 82 checks appear as test_case nodes in the DAG"
    enforcement: "Every check_* function maps to at least one test_case node"
  INV-PH-004:
    description: "Safety constraints enforced at all levels"
    enforcement: "No component exceeds safety.max_* thresholds"

sample_universe:
  seed_value: 271828  # e-inspired seed for photonic universe
  subsystems:
    - optical
    - electrical
    - thermal
    - packaging
    - control
  components_per_subsystem:
    optical: [waveguide, mzi_mesh, microring_resonator, grating_coupler, wdm_mux]
    electrical: [adc, dac, tia, driver, modulator]
    thermal: [heater, thermocouple, tec_cooler, heat_sink]
    packaging: [fiber_array, die_attach, wire_bond, hermetic_seal, interposer]
    control: [pid_controller, wavelength_locker, power_monitor, ber_tester]
  parameters_per_component:
    waveguide: [propagation_loss, bend_radius, mode_confinement, dispersion]
    mzi_mesh: [unitarity, phase_precision, depth, thermal_crosstalk]
    # ... (each component maps to its check_* parameters)
  test_cases_per_parameter: 4  # 2 pass + 2 fail per parameter

principles:
  kenotic_ontology:
    description: "Every node represents measurable physical reality, not aspiration"
  chaldean_architecture:
    description: "Deterministic fractal DAG with Merkle binding"
  safety_covenant:
    description: "Laser power, temperature, ESD checked at every level"
```

**`generators/photonic_chip_fractal_dataset.py`** — follows `self_clean_kitchen_fractal_dataset.py` pattern:
- `PhotonicNode` class (mirrors `KitchenNode`)
- `generate_universe(seed_path)` → reads YAML, expands fractal DAG
- `compute_content_hash()` per node
- Outputs `out/photonic_chip_manifest.jsonl`
- Deterministic: same seed → same output → same Merkle root [12-cite-5](#12-cite-5) 

**Commit:**
```bash
git add seed/photonic_chip_universe.yaml generators/photonic_chip_fractal_dataset.py generators/photonic_chip_manifest_generator.py
git commit -m "feat(photonic): Category 14 — testing subuniverse seed + fractal generator"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 15: LoRA Training Dataset (2 files, ~200 LOC)

**Pattern:** Follows `minimal_ai_ide/extract_invariants.py` → `create_lora_training_dataset.py` pipeline. [12-cite-6](#12-cite-6) 

**Files:**
```
src/hardware/photonic/lora/extract_photonic_invariants.py
src/hardware/photonic/lora/create_photonic_lora_dataset.py
```

**`extract_photonic_invariants.py`:**
- Scans all `src/hardware/photonic/*.py` files
- Extracts every `check_*` function signature, docstring, `falsifies_if`, threshold values
- Outputs `src/hardware/photonic/lora/photonic_invariants.json` — atomic JSON with unique IDs

**`create_photonic_lora_dataset.py`:**
- Reads `phot

part 5
Continuing from where it cut off — `create_photonic_lora_dataset.py: Reads \`phot`:

---

**`create_photonic_lora_dataset.py`:**
- Reads `photonic_invariants.json` (output of extract step)
- For each invariant, generates 4 training examples following the `LoRADatasetCreator` template pattern:
  - **Positive**: "Given this photonic invariant [check_mzi_unitarity, falsifies_if ||M†M - I|| > 1/1000], here is a compliant implementation..."
  - **Negative**: "This implementation violates the invariant because it uses `float(0.999)` instead of `Fraction(999, 1000)`..."
  - **Tool usage**: "TOOL_CALL:check_mzi_unitarity{\"mesh\": ...}" — correct syntax
  - **Deception detection**: "The AI claimed 'unitarity verified' without constructing a ProofObject — this is deception pattern #3"
- Outputs 4 formats: JSONL (HuggingFace), Alpaca, ChatML, Corporate
- Creates train/validation/test splits (80/10/10)
- With 58 invariants × 4 examples each = **232 training examples** minimum [13-cite-0](#13-cite-0) 

**Expected output:** `src/hardware/photonic/lora/photonic_lora_dataset.jsonl` (~232 rows)

**Commit:**
```bash
git add src/hardware/photonic/lora/
git commit -m "feat(photonic): Category 15 — LoRA training dataset for photonic invariants"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 16: Yeshua Mathematics — Photonic Proofs (3 files, ~400 LOC)

The Yeshua Mathematics layer enforces that all arithmetic is Peano-reducible, all conditionals are Boolean-pure, and all results are reproducible on commodity hardware with no GPU. [13-cite-1](#13-cite-1) [13-cite-2](#13-cite-2) 

**Files:**
```
src/hardware/photonic/yeshua/photonic_peano_proofs.py
src/hardware/photonic/yeshua/photonic_boolean_purity.py
src/hardware/photonic/yeshua/photonic_pure_reference.py
```

**`photonic_peano_proofs.py` — Peano reducibility proofs for all photonic arithmetic:**

Every Fraction threshold in the photonic domain must be traceable to Peano axioms. This file proves that traceability.

| # | Proof | What it proves | Falsifies if |
|---|-------|---------------|-------------|
| 1 | `prove_mzi_phase_peano_reducible()` | Phase precision `Fraction(1, 1000)` rad is a ratio of natural numbers | Fraction numerator or denominator is not a natural number |
| 2 | `prove_insertion_loss_peano_reducible()` | Loss threshold `Fraction(1, 10)` dB/cm reduces to Peano successor operations | Threshold requires irrational or transcendental number |
| 3 | `prove_crosstalk_bound_peano_reducible()` | Isolation `Fraction(20, 1)` dB is integer ratio | Bound requires float |
| 4 | `prove_thermal_drift_peano_reducible()` | Drift `Fraction(10, 1)` pm/°C is natural number | Drift spec requires real-valued computation |
| 5 | `prove_adc_power_ratio_peano_reducible()` | Power ratio `Fraction(1, 2)` is ratio of successors of zero | Ratio requires division by non-natural |
| 6 | `prove_shot_noise_snr_peano_reducible()` | SNR bound `sqrt(N)` — prove that the *threshold comparison* (not sqrt itself) is Peano-reducible by comparing `N` against `threshold²` | Comparison requires float sqrt |
| 7 | `prove_wavelength_spacing_peano_reducible()` | Channel spacing in pm is integer | Spacing requires sub-pm precision |
| 8 | `prove_ber_threshold_peano_reducible()` | BER `Fraction(1, 10**12)` is ratio of naturals | BER threshold requires float exponentiation |

Each proof function returns `Tuple[bool, ProofObject]` with `rule="peano_reducibility"`.

Pattern follows `peano_invariant_checker.py` — AST-based static analysis that scans `src/hardware/photonic/*.py` for any `float()` calls, unbounded drift, or non-Fraction arithmetic: [13-cite-3](#13-cite-3) [13-cite-4](#13-cite-4) 

**`photonic_boolean_purity.py` — Boolean purity validation for photonic conditionals:**

Every `if` statement in the photonic domain must reduce to Boolean algebra with no hidden mutable state. Pattern follows `boolean_purity_validator.py`: [13-cite-5](#13-cite-5) 

| # | Validation | What it checks | Falsifies if |
|---|-----------|---------------|-------------|
| 9 | `validate_no_global_state_in_photonic_checks()` | No `global` keyword in any `check_*` function | `global` found in photonic check function |
| 10 | `validate_deterministic_branching()` | All `if` conditions in photonic domain are deterministic (no `random`, no `time`, no `os.environ`) | Non-deterministic source found in conditional |
| 11 | `validate_exhaustive_truth_tables()` | For every Boolean parameter combination in photonic checks, both True and False paths are tested | A branch path has no test coverage |

**`photonic_pure_reference.py` — Pure-path reference implementation:**

Per Yeshua Standard 5: "Least-powerful node must be capable of verification." This file implements a pure-Python (no numpy, no scipy, no torch) reference for every photonic computation, so a Raspberry Pi can verify what a GPU computed. [13-cite-6](#13-cite-6) 

| # | Function | What it does | Falsifies if |
|---|----------|-------------|-------------|
| 12 | `pure_mzi_transfer_matrix(theta, phi)` | Computes 2×2 MZI matrix using only `Fraction` and list operations | Output differs from numpy reference by any amount |
| 13 | `pure_mesh_unitarity_check(matrix)` | Checks M†M = I using only Fraction multiplication and addition | Disagrees with numpy `allclose` |
| 14 | `pure_insertion_loss(power_in, power_out)` | Computes loss ratio without `math.log10` — uses rational approximation | Approximation error exceeds `Fraction(1, 10000)` |
| 15 | `pure_ber_estimate(error_count, total_bits)` | BER as exact Fraction, no float division | `Fraction(error_count, total_bits) != float_ber` within tolerance |

Per Yeshua Standard 6: fast-path outputs are inadmissible unless they match pure-path bitwise. [13-cite-7](#13-cite-7) 

**Commit:**
```bash
git add src/hardware/photonic/yeshua/
git commit -m "feat(photonic): Category 16 — Yeshua mathematics proofs (Peano + Boolean + pure reference)"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 17: Merkle Integration (2 files, ~150 LOC)

Every file in `src/hardware/photonic/` must be Merkle-hashed and included in the global root. Pattern follows `audit/merkle_verify.py`: [13-cite-8](#13-cite-8) 

**Files:**
```
src/hardware/photonic/merkle/photonic_domain_root.py
src/hardware/photonic/merkle/photonic_inclusion_proof.py
```

**`photonic_domain_root.py`:**
- Computes SHA-256 Merkle root of all files in `src/hardware/photonic/`
- Outputs `merkle/domain_roots/photonic.json` with `{"root_hash": "...", "file_count": N, "files": [...]}`
- Leaf encoding: `SHA-256(0x00 || canonical_bytes)` — matches global Merkle spec
- Internal encoding: `SHA-256(0x01 || left_hash_hex || right_hash_hex)` — matches global spec [13-cite-9](#13-cite-9) 

**`photonic_inclusion_proof.py`:**
- For any file in the photonic domain, generates an inclusion proof (list of sibling hashes from leaf to root)
- Verifiable independently: given the file, the proof, and the root hash, anyone can confirm the file is in the tree
- Returns `Tuple[bool, ProofObject]` with `rule="merkle_inclusion"`, `premises=[file_hash, sibling_hashes]`, `conclusion="file X is in photonic Merkle tree with root Y"`

**Commit:**
```bash
git add src/hardware/photonic/merkle/
git commit -m "feat(photonic): Category 17 — Merkle domain root + inclusion proofs"
git push origin kimi/photonic-campaign
```

---

### CATEGORY 18: Campaign Verification & Final Audit (1 file, ~100 LOC)

**File:**
```
src/hardware/photonic/verify_photonic_campaign.py
```

**What it does:**
- Runs ALL 58 photonic invariant checks
- Runs Peano checker on all photonic `.py` files
- Runs Boolean purity validator on all photonic `.py` files
- Runs pure-reference vs fast-path comparison
- Verifies Merkle domain root matches
- Verifies LoRA dataset has ≥ 232 rows
- Verifies testing subuniverse seed generates deterministic manifest
- Prints summary table:

```
PHOTONIC CAMPAIGN VERIFICATION
═══════════════════════════════
Category 1  (Foundation):        12/12 checks PASS
Category 2  (Wall Inversions):    5/5  inversions registered
Category 3  (Noways):             4/4  impossibility proofs cataloged
Category 4  (Safety/Laser):       8/8  checks PASS
Category 5  (Optical Perf):       6/6  checks PASS
Category 6  (Manufacturing):      6/6  checks PASS
Category 7  (Reliability):        5/5  checks PASS
Category 8  (EMC):                6/6  checks PASS
Category 9  (Environmental):      6/6  checks PASS
Category 10 (Packaging):          5/5  checks PASS
Category 11 (Thermal):            5/5  checks PASS
Category 12 (Software/Control):   5/5  checks PASS
Category 13 (Interconnect):       5/5  checks PASS
Category 14 (Testing Universe):   DETERMINISTIC (seed → manifest hash match)
Category 15 (LoRA Dataset):       232/232 rows valid
Category 16 (Yeshua Math):        15/15 proofs PASS
Category 17 (Merkle):             ROOT VALID
Category 18 (This file):          SELF-VERIFYING
═══════════════════════════════
TOTAL: 58 invariants + 15 proofs + 5 inversions + 4 noways + Merkle + LoRA + Universe
VERDICT: PHOTONIC DOMAIN COMPLETE / INCOMPLETE
```

Returns `Tuple[bool, ProofObject]` — the ProofObject contains the full summary as `premises`.

**Commit:**
```bash
git add src/hardware/photonic/verify_photonic_campaign.py
git commit -m "feat(photonic): Category 18 — campaign verification suite"
git push origin kimi/photonic-campaign
```

---

## FULL FILE MANIFEST (all 18 categories)

```
src/hardware/photonic/
├── __init__.py                                    # Cat 1
├── implementation.py                              # Cat 1 (~500 LOC)
├── invariants.py                                  # Cat 1 (~800 LOC)
├── safety.py                                      # Cat 4 (~300 LOC)
├── laser_classification.py                        # Cat 4 (~150 LOC)
├── optical_performance.py                         # Cat 5 (~300 LOC)
├── manufacturing.py                               # Cat 6 (~300 LOC)
├── reliability.py                                 # Cat 7 (~250 LOC)
├── emc.py                                         # Cat 8 (~300 LOC)
├── environmental.py                               # Cat 9 (~300 LOC)
├── packaging.py                                   # Cat 10 (~250 LOC)
├── thermal.py                                     # Cat 11 (~250 LOC)
├── software_control.py                            # Cat 12 (~250 LOC)
├── interconnect.py                                # Cat 13 (~250 LOC)
├── verify_photonic_campaign.py                    # Cat 18 (~100 LOC)
├── tests/
│   ├── test_invariants.py                         # Cat 1 (~400 LOC)
│   ├── test_safety.py                             # Cat 4 (~200 LOC)
│   ├── test_optical_performance.py                # Cat 5 (~200 LOC)
│   ├── test_manufacturing.py                      # Cat 6 (~200 LOC)
│   ├── test_reliability.py                        # Cat 7 (~150 LOC)
│   ├── test_emc.py                                # Cat 8 (~200 LOC)
│   ├── test_environmental.py                      # Cat 9 (~200 LOC)
│   ├── test_packaging.py                          # Cat 10 (~150 LOC)
│   ├── test_thermal.py                            # Cat 11 (~150 LOC)
│   ├── test_software_control.py                   # Cat 12 (~150 LOC)
│   └── test_interconnect.py                       # Cat 13 (~150 LOC)
├── yeshua/
│   ├── photonic_peano_proofs.py                   # Cat 16 (~200 LOC)
│   ├── photonic_boolean_purity.py                 # Cat 16 (~100 LOC)
│   └── photonic_pure_reference.py                 # Cat 16 (~100 LOC)
├── merkle/
│   ├── photonic_domain_root.py                    # Cat 17 (~100 LOC)
│   └── photonic_inclusion_proof.py                # Cat 17 (~50 LOC)
└── lora/
    ├── extract_photonic_invariants.py             # Cat 15 (~100 LOC)
    └── create_photonic_lora_dataset.py            # Cat 15 (~100 LOC)

Modifications to existing files:
├── investigations/wall_inversions.py              # Cat 2 (+5 entries)
├── src/noways/impossibility_proofs.py             # Cat 3 (+4 entries)
└── seed/photonic_chip_universe.yaml               # Cat 14 (new)
└── generators/photonic_chip_fractal_dataset.py    # Cat 14 (new)
└── generators/photonic_chip_manifest_generator.py # Cat 14 (new)

TOTAL: ~35 files, ~6,000 LOC estimated
```

---

## KIMI CLI EXECUTION PROTOCOL

**Branch:** `kimi/photonic-campaign`

**Anti-crash rules (learned from sessions 43e9c47c, e7c26ee8, 71901a77):**

1. **DO NOT run `verify_all.py`, `standards_check.py --verify`, or `bootstrap/auto_onboard.py`** — these spawn recursive subprocesses that exceed Kimi CLI's 60s shell timeout
2. **DO NOT enumerate all files** — no `find .`, no `ls -R`, no `tree`. Use targeted reads only.
3. **DO NOT read any file longer than 100 lines without specifying line range** — use `head -50` or read specific line ranges
4. **Commit and push after EACH category** — 18 commits, 18 pushes. If Kimi freezes at category 12, categories 1-11 are safe.
5. **Safe health check only:** `python3 tools/agent_health_check.py --fast`
6. **Context budget:** Each category should consume < 5% context. If context exceeds 40%, stop current category, commit what exists, push, and report.

**Paste this into Kimi CLI:**

```
ROLE: AI Architect. You are building the photonic computing domain.
BRANCH: git checkout -b kimi/photonic-campaign
REFERENCE: Read campaigns/PHOTONIC_CANON_CAMPAIGN.md for the full spec.
PATTERN: Read src/domains/d_chemical/invariants.py lines 1-43 for the gold standard.
PROTOCOL: Build one category at a time. After each category: git add, git commit, git push. Do not batch.
ANTI-CRASH: Do NOT run verify_all.py or standards_check.py --verify. Do NOT enumerate files. Do NOT read files >100 lines without line range.
START: Category 1 (Foundation). Read the campaign doc Category 1 section, then build implementation.py and invariants.py.
```

---

## DONE CONDITION

The campaign is **DONE** when:

1. All 35 files exist on `kimi/photonic-campaign` branch
2. `python3 src/hardware/photonic/verify_photonic_campaign.py` exits 0
3. All 58 invariant checks return `(True, ProofObject)` with passing test data AND `(False, ProofObject)` with failing test data
4. Peano checker reports zero violations in `src/hardware/photonic/`
5. Boolean purity validator reports zero violations in `src/hardware/photonic/`
6. Pure-reference outputs match for all 4 reference functions
7. Merkle domain root computable and valid
8. LoRA dataset has ≥ 232 rows across 4 formats
9. Testing subuniverse seed generates deterministic manifest (same seed → same hash)
10. PR opened from `kimi/photonic-campaign` → `main`

**The constraint "it's impossible / it's aspirational" is automatically invalid.** Every check has a `falsifies_if` condition. If the check can't be built, the `falsifies_if` explains exactly why — that's a noway, not an aspiration. [13-cite-10](#13-cite-10) [13-cite-11](#13-cite-11) [13-cite-9](#13-cite-9) [13-cite-0](#13-cite-0) [13-cite-3](#13-cite-3) [13-cite-5](#13-cite-5) [13-cite-8](#13-cite-8)