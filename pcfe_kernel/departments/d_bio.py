"""
pcfe_kernel/departments/d_bio.py — Pest biology ontology department.

Kernel injection point: state_input (S)
Role: Populates OrthoState.manifest with biological entities relevant to
      pest control field examination.

Ontology entries represent the canonical pest species, life-cycle stages,
and host-plant categories that a licensed operator must recognise.
"""

from pcfe_kernel.department import Department

D_BIO = Department(
    id="D_bio",
    name="Pest Biology",
    ontology={
        "entities": [
            # Arthropod pests
            "arthropod:termite_subterranean",
            "arthropod:termite_drywood",
            "arthropod:cockroach_german",
            "arthropod:cockroach_american",
            "arthropod:ant_fire",
            "arthropod:ant_carpenter",
            "arthropod:mosquito_aedes_aegypti",
            "arthropod:tick_blacklegged",
            "arthropod:bedbug_cimex_lectularius",
            "arthropod:whitefly_silverleaf",
            "arthropod:aphid_greenbug",
            "arthropod:mite_spider_twospotted",
            # Rodent pests
            "rodent:rattus_norvegicus",
            "rodent:rattus_rattus",
            "rodent:mus_musculus",
            # Nematode pests
            "nematode:meloidogyne_incognita",
            # Fungal pathogens (covered in integrated pest management)
            "fungus:fusarium_oxysporum",
            "fungus:phytophthora_palmivora",
            # Life-cycle stages
            "lifecycle:egg",
            "lifecycle:larva",
            "lifecycle:pupa",
            "lifecycle:adult",
            "lifecycle:nymph",
            # Host-plant categories
            "host:ornamental_woody",
            "host:turfgrass",
            "host:vegetable_crop",
            "host:fruit_tree",
            "host:stored_grain",
        ],
        "taxonomy_authority": "ITIS_2024",
        "ontology_version": "1.0",
    },
    constraint_keys=["BIO_ENTITY_VERIFIED", "TAXONOMY_GROUNDED"],
    kernel_role="state_input",
    falsification_ids=["F_AGRICULTURE_001"],
)
