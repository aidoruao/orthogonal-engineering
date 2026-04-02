"""
pcfe_kernel/departments/d_fdacs.py — FDACS regulatory constraint AST department.

Kernel injection point: rule_filter (R)
Role: Hard constraint on which transitions OrthoKernel.transition() accepts.

The Florida Department of Agriculture and Consumer Services (FDACS) issues
licensing requirements for pest control operators.  This department encodes
those requirements as a structured constraint AST that gates kernel
transitions — the closest analogue to a formal rule filter in the existing
codebase is the anti-mimicry forbidden-term check in OrthoKernel.transition().

constraint_keys here map 1-to-1 to rule nodes in the constraint AST.
Each key must appear in an artifact's `constraints` list for Principle.verify()
to pass the regulatory gate.
"""

from pcfe_kernel.department import Department

_FDACS_CONSTRAINT_AST = {
    "ast_type": "ConjunctiveRuleSet",
    "authority": "FDACS_Chapter_482_Florida_Statutes",
    "version": "2024",
    "rules": [
        {
            "id": "FDACS_LIC_001",
            "rule": "Operator holds a current FDACS certified operator license.",
            "falsifies_if": "License number absent or expired.",
        },
        {
            "id": "FDACS_LIC_002",
            "rule": "Pesticide applications performed only by licensed applicators.",
            "falsifies_if": "Unlicensed person performs application.",
        },
        {
            "id": "FDACS_RECORD_001",
            "rule": "Application records retained for two years.",
            "falsifies_if": "Record missing pesticide name, EPA reg no., or date.",
        },
        {
            "id": "FDACS_LABEL_001",
            "rule": "Pesticide applied strictly per EPA-registered label.",
            "falsifies_if": "Application rate or site deviates from label.",
        },
        {
            "id": "FDACS_PPE_001",
            "rule": "Required PPE worn during application per label requirements.",
            "falsifies_if": "Label-required PPE not worn.",
        },
        {
            "id": "FDACS_NOTIFY_001",
            "rule": "Pre-application notification provided to sensitive-site occupants.",
            "falsifies_if": "Notification absent where required.",
        },
        {
            "id": "FDACS_REENTRY_001",
            "rule": "Re-entry interval (REI) observed after application.",
            "falsifies_if": "Occupants re-entered before REI elapsed.",
        },
        {
            "id": "FDACS_WASTE_001",
            "rule": "Pesticide waste disposed per label and state hazardous waste rules.",
            "falsifies_if": "Pesticide waste poured into storm drain or waterway.",
        },
    ],
    "evaluation": "ALL_MUST_PASS",
}

D_FDACS = Department(
    id="D_fdacs",
    name="FDACS Regulatory",
    ontology=_FDACS_CONSTRAINT_AST,
    constraint_keys=[
        "FDACS_LIC_001",
        "FDACS_LIC_002",
        "FDACS_RECORD_001",
        "FDACS_LABEL_001",
        "FDACS_PPE_001",
        "FDACS_NOTIFY_001",
        "FDACS_REENTRY_001",
        "FDACS_WASTE_001",
    ],
    kernel_role="rule_filter",
    falsification_ids=["F_CHEMICAL_001", "F_CRUSADER_008"],
)
