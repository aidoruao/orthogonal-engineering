"""
pcfe_kernel/departments/d_train.py — Scenario generator department.

Kernel injection point: state_input (S) — initial state generator
Role: Generates synthetic OrthoState instances for simulation/training.

The training department's ontology defines a catalogue of scenario seeds.
CertificationSimulator.generate_scenario() draws from these seeds to produce
deterministic OrthoState instances that drive exam evaluation.

Each entity in "entities" becomes a manifest entry in the generated
OrthoState, establishing a realistic starting context for candidate
evaluation.
"""

from pcfe_kernel.department import Department

D_TRAIN = Department(
    id="D_train",
    name="Scenario Generator",
    ontology={
        "entities": [
            # Scenario type tags (injected into OrthoState.manifest)
            "scenario:residential_termite_inspection",
            "scenario:commercial_kitchen_cockroach",
            "scenario:school_grounds_ant_control",
            "scenario:warehouse_rodent_exclusion",
            "scenario:ornamental_whitefly_treatment",
            "scenario:turf_chinch_bug_assessment",
            "scenario:stored_product_pest_fumigation",
            "scenario:mosquito_larval_source_reduction",
            "scenario:bedbug_heat_treatment_hotel",
            "scenario:german_cockroach_ipm_restaurant",
        ],
        # Deterministic seed for reproducible scenario generation
        "default_seed": 314159,
        # Scoring thresholds for exam evaluation
        "pass_threshold": 1.0,
        "allow_partial_credit": False,
        "ontology_version": "1.0",
    },
    constraint_keys=["SCENARIO_DETERMINISTIC", "SEED_RECORDED"],
    kernel_role="state_input",
    falsification_ids=["F_PLATFORM_001", "F_CRUSADER_008"],
)
