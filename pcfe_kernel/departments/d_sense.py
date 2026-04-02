"""
pcfe_kernel/departments/d_sense.py — Inspection/observation department.

Kernel injection point: state_input (S)
Role: Converts raw inspection observations into OrthoState.manifest fields.

Inspection entities represent the observable phenomena a pest control operator
records during a site survey.  These entities are injected into
OrthoState.manifest, enabling the kernel to reason about the current
infestation state before selecting an action.
"""

from pcfe_kernel.department import Department

D_SENSE = Department(
    id="D_sense",
    name="Inspection / Observation",
    ontology={
        "entities": [
            # Physical evidence categories
            "observation:live_insect_sighting",
            "observation:dead_insect_evidence",
            "observation:frass_presence",
            "observation:mud_tubes",
            "observation:gnaw_marks",
            "observation:droppings",
            "observation:damaged_wood_hollow_sound",
            "observation:burrow_holes",
            "observation:egg_cases",
            "observation:cast_skins",
            "observation:staining_grease_marks",
            # Environmental conditions
            "condition:moisture_elevated",
            "condition:temperature_above_threshold",
            "condition:harborage_cluttered",
            "condition:entry_point_identified",
            "condition:sanitation_deficiency",
            # Monitoring device readings
            "monitor:pheromone_trap_catch",
            "monitor:sticky_trap_count",
            "monitor:bait_station_consumption",
            "monitor:rodent_snap_trap_strike",
        ],
        "inspection_protocol": "IPM_STANDARD_SURVEY",
        "ontology_version": "1.0",
    },
    constraint_keys=["OBSERVATION_RECORDED", "IPM_SURVEY_COMPLETE"],
    kernel_role="state_input",
    falsification_ids=["F_CRUSADER_008"],
)
