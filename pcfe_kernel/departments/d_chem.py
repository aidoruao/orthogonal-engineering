"""
pcfe_kernel/departments/d_chem.py — Chemical control rules department.

Kernel injection point: action_constraint (A)
Role: Filters SigmaTheoOperators — no illegal chemical action is representable.

Any action whose name appears in prohibited_actions is blocked by
DepartmentRegistry.is_action_allowed() before it ever reaches
OrthoKernel.transition().  This prevents illegal pesticide applications
from being modelled as valid kernel transitions.
"""

from pcfe_kernel.department import Department

D_CHEM = Department(
    id="D_chem",
    name="Chemical Control",
    ontology={
        # Pesticide categories allowed in Florida licensed commercial pest control
        "allowed_categories": [
            "category:insecticide_pyrethroid",
            "category:insecticide_neonicotinoid",
            "category:insecticide_organophosphate",
            "category:herbicide_glyphosate",
            "category:herbicide_2_4_d",
            "category:fungicide_triazole",
            "category:rodenticide_anticoagulant",
            "category:biopesticide_bt",
            "category:biopesticide_spinosad",
        ],
        # Actions that represent illegal or restricted chemical use
        "prohibited_actions": [
            "apply:unregistered_pesticide",
            "apply:cancelled_registration",
            "apply:off_label_rate_exceed",
            "apply:restricted_use_without_license",
            "apply:banned_organochlorine",
            "apply:methyl_bromide_without_permit",
            "mix:incompatible_tank_explosion_risk",
            "dispose:pesticide_in_waterway",
            "apply:pesticide_near_school_hours",
        ],
        # EPA registration requirement
        "registration_authority": "EPA_FIFRA",
        "state_authority": "FDACS",
        "ontology_version": "1.0",
    },
    constraint_keys=["CHEM_REGISTRATION_VALID", "NO_PROHIBITED_CHEMICAL"],
    kernel_role="action_constraint",
    falsification_ids=["F_CHEMICAL_001"],
)
