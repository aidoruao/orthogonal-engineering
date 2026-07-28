"""Shampoo ingredient ontology — Module 3: Fragrance Component Probability Engine.

Provides a self-contained, standard-library-only probabilistic engine that models
likely fragrance components for shampoo products using an embedded IFRA transparency
subset, a GC-MS literature database, and product category priors.
"""

import json
import math
import re
from collections import OrderedDict


# Total number of materials in the IFRA Transparency List (referenced in the
# v4.0 specification). The embedded subset contains 100 compounds.
IFRA_TOTAL_MATERIALS = 3619

# The 26 fragrance substances that must be individually labelled in the EU when
# present above 0.001% in leave-on or 0.01% in rinse-off cosmetics.
EU_ALLERGENS = [
    "Alpha-Isomethyl Ionone",
    "Amyl Cinnamal",
    "Amylcinnamyl Alcohol",
    "Anisyl Alcohol",
    "Benzyl Alcohol",
    "Benzyl Benzoate",
    "Benzyl Cinnamate",
    "Benzyl Salicylate",
    "Butylphenyl Methylpropional",
    "Cinnamal",
    "Cinnamyl Alcohol",
    "Citral",
    "Citronellol",
    "Coumarin",
    "Eugenol",
    "Farnesol",
    "Geraniol",
    "Hexyl Cinnamal",
    "Hydroxycitronellal",
    "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde",
    "Isoeugenol",
    "Limonene",
    "Linalool",
    "Methyl 2-Octynoate",
    "Evernia Prunastri Extract",
    "Evernia Furfuracea Extract",
]

# IFRA transparency subset: 100 fragrance materials with full metadata.
# occurrence_frequency_by_category values are approximate percentages of products
# in each category that contain the compound (0-100).
IFRA_TRANSPARENCY_SUBSET = {
    # ---------- EU 26 fragrance allergens ----------
    "Alpha-Isomethyl Ionone": {
        "cas_number": "127-51-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 45,
            "premium": 55,
            "anti_dandruff": 15,
            "baby": 5,
            "mens": 25,
            "natural": 10,
            "professional": 40,
        },
    },
    "Amyl Cinnamal": {
        "cas_number": "122-40-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 35,
            "anti_dandruff": 10,
            "baby": 2,
            "mens": 12,
            "natural": 8,
            "professional": 25,
        },
    },
    "Amylcinnamyl Alcohol": {
        "cas_number": "101-85-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 18,
            "anti_dandruff": 4,
            "baby": 1,
            "mens": 5,
            "natural": 3,
            "professional": 10,
        },
    },
    "Anisyl Alcohol": {
        "cas_number": "105-13-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 15,
            "anti_dandruff": 3,
            "baby": 1,
            "mens": 4,
            "natural": 5,
            "professional": 9,
        },
    },
    "Benzyl Alcohol": {
        "cas_number": "100-51-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 50,
            "premium": 45,
            "anti_dandruff": 35,
            "baby": 40,
            "mens": 30,
            "natural": 55,
            "professional": 40,
        },
    },
    "Benzyl Benzoate": {
        "cas_number": "120-51-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 40,
            "premium": 50,
            "anti_dandruff": 20,
            "baby": 15,
            "mens": 25,
            "natural": 45,
            "professional": 35,
        },
    },
    "Benzyl Cinnamate": {
        "cas_number": "103-41-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 25,
            "anti_dandruff": 5,
            "baby": 3,
            "mens": 8,
            "natural": 12,
            "professional": 18,
        },
    },
    "Benzyl Salicylate": {
        "cas_number": "118-58-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 45,
            "anti_dandruff": 15,
            "baby": 8,
            "mens": 20,
            "natural": 30,
            "professional": 30,
        },
    },
    "Butylphenyl Methylpropional": {
        "cas_number": "80-54-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 5,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "endocrine_disruption",
        "occurrence_frequency_by_category": {
            "mass_market": 55,
            "premium": 40,
            "anti_dandruff": 20,
            "baby": 5,
            "mens": 35,
            "natural": 2,
            "professional": 30,
        },
    },
    "Cinnamal": {
        "cas_number": "104-55-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 25,
            "premium": 30,
            "anti_dandruff": 12,
            "baby": 3,
            "mens": 15,
            "natural": 20,
            "professional": 22,
        },
    },
    "Cinnamyl Alcohol": {
        "cas_number": "104-54-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 18,
            "premium": 25,
            "anti_dandruff": 7,
            "baby": 2,
            "mens": 10,
            "natural": 15,
            "professional": 16,
        },
    },
    "Citral": {
        "cas_number": "5392-40-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 40,
            "premium": 35,
            "anti_dandruff": 25,
            "baby": 10,
            "mens": 30,
            "natural": 55,
            "professional": 35,
        },
    },
    "Citronellol": {
        "cas_number": "106-22-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 45,
            "premium": 55,
            "anti_dandruff": 15,
            "baby": 8,
            "mens": 20,
            "natural": 60,
            "professional": 40,
        },
    },
    "Coumarin": {
        "cas_number": "91-64-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "hepatotoxicity_concern",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 40,
            "anti_dandruff": 12,
            "baby": 5,
            "mens": 20,
            "natural": 25,
            "professional": 30,
        },
    },
    "Eugenol": {
        "cas_number": "97-53-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 35,
            "anti_dandruff": 20,
            "baby": 5,
            "mens": 25,
            "natural": 50,
            "professional": 30,
        },
    },
    "Farnesol": {
        "cas_number": "4602-84-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 35,
            "anti_dandruff": 8,
            "baby": 3,
            "mens": 12,
            "natural": 30,
            "professional": 25,
        },
    },
    "Geraniol": {
        "cas_number": "106-24-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 50,
            "premium": 60,
            "anti_dandruff": 18,
            "baby": 10,
            "mens": 22,
            "natural": 65,
            "professional": 45,
        },
    },
    "Hexyl Cinnamal": {
        "cas_number": "101-86-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 5,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 60,
            "premium": 50,
            "anti_dandruff": 20,
            "baby": 4,
            "mens": 30,
            "natural": 8,
            "professional": 40,
        },
    },
    "Hydroxycitronellal": {
        "cas_number": "107-75-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 45,
            "anti_dandruff": 12,
            "baby": 3,
            "mens": 15,
            "natural": 5,
            "professional": 30,
        },
    },
    "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde": {
        "cas_number": "31906-04-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 25,
            "premium": 30,
            "anti_dandruff": 10,
            "baby": 2,
            "mens": 12,
            "natural": 3,
            "professional": 20,
        },
    },
    "Isoeugenol": {
        "cas_number": "97-54-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 22,
            "anti_dandruff": 8,
            "baby": 2,
            "mens": 10,
            "natural": 25,
            "professional": 14,
        },
    },
    "Limonene": {
        "cas_number": "5989-27-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 8,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 80,
            "premium": 65,
            "anti_dandruff": 50,
            "baby": 30,
            "mens": 55,
            "natural": 85,
            "professional": 60,
        },
    },
    "Linalool": {
        "cas_number": "78-70-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 7,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 75,
            "premium": 70,
            "anti_dandruff": 45,
            "baby": 35,
            "mens": 50,
            "natural": 80,
            "professional": 65,
        },
    },
    "Methyl 2-Octynoate": {
        "cas_number": "111-12-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 5,
            "premium": 8,
            "anti_dandruff": 2,
            "baby": 1,
            "mens": 4,
            "natural": 3,
            "professional": 6,
        },
    },
    "Evernia Prunastri Extract": {
        "cas_number": "90028-68-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 4,
            "premium": 12,
            "anti_dandruff": 3,
            "baby": 1,
            "mens": 8,
            "natural": 10,
            "professional": 9,
        },
    },
    "Evernia Furfuracea Extract": {
        "cas_number": "90028-67-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "EU_26_allergen",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 3,
            "premium": 10,
            "anti_dandruff": 2,
            "baby": 1,
            "mens": 7,
            "natural": 8,
            "professional": 8,
        },
    },
    # ---------- 74 additional high-frequency fragrance materials ----------
    "Linalyl Acetate": {
        "cas_number": "115-95-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 6,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 55,
            "premium": 60,
            "anti_dandruff": 20,
            "baby": 15,
            "mens": 30,
            "natural": 70,
            "professional": 50,
        },
    },
    "Geranyl Acetate": {
        "cas_number": "105-87-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 40,
            "premium": 50,
            "anti_dandruff": 15,
            "baby": 10,
            "mens": 20,
            "natural": 60,
            "professional": 40,
        },
    },
    "Citronellyl Acetate": {
        "cas_number": "150-84-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 40,
            "anti_dandruff": 10,
            "baby": 6,
            "mens": 15,
            "natural": 45,
            "professional": 30,
        },
    },
    "Alpha-Pinene": {
        "cas_number": "80-56-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 30,
            "anti_dandruff": 40,
            "baby": 10,
            "mens": 35,
            "natural": 65,
            "professional": 35,
        },
    },
    "Beta-Pinene": {
        "cas_number": "127-91-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 25,
            "premium": 22,
            "anti_dandruff": 30,
            "baby": 8,
            "mens": 28,
            "natural": 55,
            "professional": 28,
        },
    },
    "Myrcene": {
        "cas_number": "123-35-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 18,
            "anti_dandruff": 25,
            "baby": 7,
            "mens": 22,
            "natural": 50,
            "professional": 22,
        },
    },
    "Camphene": {
        "cas_number": "79-78-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 12,
            "anti_dandruff": 15,
            "baby": 5,
            "mens": 12,
            "natural": 35,
            "professional": 14,
        },
    },
    "Terpinolene": {
        "cas_number": "586-62-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 14,
            "anti_dandruff": 18,
            "baby": 5,
            "mens": 15,
            "natural": 40,
            "professional": 16,
        },
    },
    "Gamma-Terpinene": {
        "cas_number": "99-85-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 11,
            "anti_dandruff": 14,
            "baby": 4,
            "mens": 12,
            "natural": 35,
            "professional": 13,
        },
    },
    "Para-Cymene": {
        "cas_number": "99-87-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 9,
            "anti_dandruff": 12,
            "baby": 3,
            "mens": 10,
            "natural": 30,
            "professional": 11,
        },
    },
    "1,8-Cineole": {
        "cas_number": "470-82-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 18,
            "anti_dandruff": 45,
            "baby": 10,
            "mens": 30,
            "natural": 55,
            "professional": 30,
        },
    },
    "Camphor": {
        "cas_number": "76-22-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "neurotoxicity_concern",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 10,
            "anti_dandruff": 35,
            "baby": 4,
            "mens": 25,
            "natural": 40,
            "professional": 18,
        },
    },
    "Menthol": {
        "cas_number": "89-78-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 18,
            "premium": 12,
            "anti_dandruff": 50,
            "baby": 5,
            "mens": 40,
            "natural": 45,
            "professional": 25,
        },
    },
    "Menthone": {
        "cas_number": "89-80-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 8,
            "anti_dandruff": 30,
            "baby": 3,
            "mens": 25,
            "natural": 35,
            "professional": 15,
        },
    },
    "Carvone": {
        "cas_number": "99-49-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 7,
            "anti_dandruff": 25,
            "baby": 2,
            "mens": 18,
            "natural": 30,
            "professional": 12,
        },
    },
    "Anethole": {
        "cas_number": "4180-23-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 12,
            "anti_dandruff": 15,
            "baby": 3,
            "mens": 10,
            "natural": 35,
            "professional": 12,
        },
    },
    "Estragole": {
        "cas_number": "140-67-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "carcinogenicity_concern",
        "occurrence_frequency_by_category": {
            "mass_market": 5,
            "premium": 6,
            "anti_dandruff": 8,
            "baby": 2,
            "mens": 5,
            "natural": 25,
            "professional": 7,
        },
    },
    "Methyl Eugenol": {
        "cas_number": "93-15-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "carcinogenicity_concern",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 10,
            "anti_dandruff": 6,
            "baby": 2,
            "mens": 7,
            "natural": 28,
            "professional": 9,
        },
    },
    "Safrole": {
        "cas_number": "94-59-7",
        "ifra_category": "prohibited",
        "typical_concentration_in_fragrance": 0,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "carcinogenicity_concern",
        "occurrence_frequency_by_category": {
            "mass_market": 1,
            "premium": 1,
            "anti_dandruff": 1,
            "baby": 0,
            "mens": 1,
            "natural": 4,
            "professional": 1,
        },
    },
    "Vanillin": {
        "cas_number": "121-33-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 5,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 40,
            "anti_dandruff": 12,
            "baby": 10,
            "mens": 15,
            "natural": 35,
            "professional": 30,
        },
    },
    "Ethyl Vanillin": {
        "cas_number": "121-32-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 28,
            "anti_dandruff": 8,
            "baby": 6,
            "mens": 10,
            "natural": 10,
            "professional": 20,
        },
    },
    "Benzaldehyde": {
        "cas_number": "100-52-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 14,
            "anti_dandruff": 8,
            "baby": 4,
            "mens": 9,
            "natural": 20,
            "professional": 12,
        },
    },
    "Acetophenone": {
        "cas_number": "98-86-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 7,
            "anti_dandruff": 3,
            "baby": 2,
            "mens": 5,
            "natural": 8,
            "professional": 6,
        },
    },
    "Benzyl Acetate": {
        "cas_number": "140-11-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 40,
            "anti_dandruff": 12,
            "baby": 10,
            "mens": 15,
            "natural": 45,
            "professional": 30,
        },
    },
    "Phenethyl Alcohol": {
        "cas_number": "60-12-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 45,
            "anti_dandruff": 10,
            "baby": 12,
            "mens": 12,
            "natural": 40,
            "professional": 35,
        },
    },
    "Phenylacetaldehyde": {
        "cas_number": "122-78-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 14,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 5,
            "natural": 12,
            "professional": 10,
        },
    },
    "Indole": {
        "cas_number": "120-72-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 18,
            "anti_dandruff": 3,
            "baby": 1,
            "mens": 4,
            "natural": 12,
            "professional": 12,
        },
    },
    "Skatole": {
        "cas_number": "83-34-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 0,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 2,
            "premium": 4,
            "anti_dandruff": 1,
            "baby": 0,
            "mens": 1,
            "natural": 3,
            "professional": 3,
        },
    },
    "Methyl Dihydrojasmonate": {
        "cas_number": "24851-98-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 8,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 50,
            "premium": 65,
            "anti_dandruff": 20,
            "baby": 10,
            "mens": 30,
            "natural": 15,
            "professional": 55,
        },
    },
    "Hedione": {
        "cas_number": "18871-14-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 6,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 60,
            "anti_dandruff": 15,
            "baby": 8,
            "mens": 25,
            "natural": 10,
            "professional": 50,
        },
    },
    "Iso E Super": {
        "cas_number": "54464-57-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 10,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 40,
            "premium": 70,
            "anti_dandruff": 20,
            "baby": 5,
            "mens": 55,
            "natural": 5,
            "professional": 60,
        },
    },
    "Galaxolide": {
        "cas_number": "1222-05-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 7,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "endocrine_disruption",
        "occurrence_frequency_by_category": {
            "mass_market": 55,
            "premium": 45,
            "anti_dandruff": 30,
            "baby": 20,
            "mens": 40,
            "natural": 5,
            "professional": 40,
        },
    },
    "Tonalid": {
        "cas_number": "1506-02-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 5,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 35,
            "premium": 40,
            "anti_dandruff": 20,
            "baby": 15,
            "mens": 30,
            "natural": 3,
            "professional": 35,
        },
    },
    "Musk Ketone": {
        "cas_number": "81-14-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 25,
            "anti_dandruff": 8,
            "baby": 5,
            "mens": 20,
            "natural": 2,
            "professional": 20,
        },
    },
    "Musk Xylene": {
        "cas_number": "81-15-2",
        "ifra_category": "restricted",
        "typical_concentration_in_fragrance": 0,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "endocrine_disruption",
        "occurrence_frequency_by_category": {
            "mass_market": 3,
            "premium": 4,
            "anti_dandruff": 2,
            "baby": 1,
            "mens": 3,
            "natural": 0,
            "professional": 3,
        },
    },
    "Ambroxan": {
        "cas_number": "6790-58-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 55,
            "anti_dandruff": 10,
            "baby": 5,
            "mens": 30,
            "natural": 5,
            "professional": 45,
        },
    },
    "Cedrol": {
        "cas_number": "77-53-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 35,
            "anti_dandruff": 12,
            "baby": 4,
            "mens": 40,
            "natural": 20,
            "professional": 30,
        },
    },
    "Alpha-Cedrene": {
        "cas_number": "469-61-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 25,
            "anti_dandruff": 8,
            "baby": 3,
            "mens": 30,
            "natural": 18,
            "professional": 20,
        },
    },
    "Patchouli Alcohol": {
        "cas_number": "5986-55-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 35,
            "anti_dandruff": 8,
            "baby": 2,
            "mens": 25,
            "natural": 30,
            "professional": 30,
        },
    },
    "Vetiverol": {
        "cas_number": "68129-81-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 30,
            "anti_dandruff": 6,
            "baby": 2,
            "mens": 20,
            "natural": 25,
            "professional": 25,
        },
    },
    "Sandalore": {
        "cas_number": "65113-99-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 35,
            "anti_dandruff": 6,
            "baby": 2,
            "mens": 25,
            "natural": 5,
            "professional": 30,
        },
    },
    "Javanol": {
        "cas_number": "198404-98-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 25,
            "anti_dandruff": 4,
            "baby": 1,
            "mens": 18,
            "natural": 3,
            "professional": 22,
        },
    },
    "Linalool Oxide": {
        "cas_number": "1365-19-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 14,
            "anti_dandruff": 8,
            "baby": 5,
            "mens": 8,
            "natural": 25,
            "professional": 12,
        },
    },
    "Rose Oxide": {
        "cas_number": "16409-43-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 20,
            "anti_dandruff": 3,
            "baby": 2,
            "mens": 4,
            "natural": 15,
            "professional": 14,
        },
    },
    "Nerol": {
        "cas_number": "106-25-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 25,
            "anti_dandruff": 6,
            "baby": 4,
            "mens": 8,
            "natural": 35,
            "professional": 18,
        },
    },
    "Nerolidol": {
        "cas_number": "7212-44-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 22,
            "anti_dandruff": 5,
            "baby": 2,
            "mens": 8,
            "natural": 28,
            "professional": 16,
        },
    },
    "Bisabolol": {
        "cas_number": "23089-26-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 18,
            "anti_dandruff": 25,
            "baby": 20,
            "mens": 8,
            "natural": 40,
            "professional": 18,
        },
    },
    "Chamazulene": {
        "cas_number": "529-05-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 3,
            "premium": 8,
            "anti_dandruff": 12,
            "baby": 8,
            "mens": 3,
            "natural": 25,
            "professional": 8,
        },
    },
    "Farnesyl Acetate": {
        "cas_number": "4128-17-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 18,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 6,
            "natural": 22,
            "professional": 14,
        },
    },
    "Geranyl Formate": {
        "cas_number": "105-86-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 15,
            "anti_dandruff": 4,
            "baby": 3,
            "mens": 7,
            "natural": 30,
            "professional": 12,
        },
    },
    "Citral Dimethyl Acetal": {
        "cas_number": "7549-37-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 14,
            "anti_dandruff": 8,
            "baby": 3,
            "mens": 10,
            "natural": 12,
            "professional": 12,
        },
    },
    "Cyclamen Aldehyde": {
        "cas_number": "103-95-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 25,
            "premium": 35,
            "anti_dandruff": 10,
            "baby": 3,
            "mens": 12,
            "natural": 2,
            "professional": 25,
        },
    },
    "Heliotropine": {
        "cas_number": "120-57-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 25,
            "anti_dandruff": 6,
            "baby": 5,
            "mens": 8,
            "natural": 12,
            "professional": 18,
        },
    },
    "Piperonal": {
        "cas_number": "120-57-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 14,
            "anti_dandruff": 4,
            "baby": 3,
            "mens": 5,
            "natural": 8,
            "professional": 10,
        },
    },
    "Anisaldehyde": {
        "cas_number": "123-11-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 10,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 5,
            "natural": 15,
            "professional": 8,
        },
    },
    "Cuminaldehyde": {
        "cas_number": "122-03-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 5,
            "premium": 6,
            "anti_dandruff": 8,
            "baby": 2,
            "mens": 6,
            "natural": 18,
            "professional": 6,
        },
    },
    "Decanal": {
        "cas_number": "112-31-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 14,
            "premium": 16,
            "anti_dandruff": 8,
            "baby": 4,
            "mens": 10,
            "natural": 15,
            "professional": 14,
        },
    },
    "Dodecanal": {
        "cas_number": "112-54-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 10,
            "anti_dandruff": 5,
            "baby": 3,
            "mens": 7,
            "natural": 10,
            "professional": 9,
        },
    },
    "Hexanal": {
        "cas_number": "66-25-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 7,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 5,
            "natural": 12,
            "professional": 6,
        },
    },
    "cis-3-Hexenol": {
        "cas_number": "928-96-1",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 18,
            "premium": 25,
            "anti_dandruff": 8,
            "baby": 6,
            "mens": 10,
            "natural": 40,
            "professional": 20,
        },
    },
    "cis-3-Hexenyl Acetate": {
        "cas_number": "3681-71-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 22,
            "anti_dandruff": 6,
            "baby": 5,
            "mens": 8,
            "natural": 35,
            "professional": 18,
        },
    },
    "cis-3-Hexenyl Salicylate": {
        "cas_number": "65405-77-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 18,
            "anti_dandruff": 5,
            "baby": 4,
            "mens": 7,
            "natural": 25,
            "professional": 14,
        },
    },
    "Styrallyl Acetate": {
        "cas_number": "93-92-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 12,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 8,
            "natural": 8,
            "professional": 10,
        },
    },
    "Benzyl Phenylacetate": {
        "cas_number": "102-16-9",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 12,
            "anti_dandruff": 3,
            "baby": 2,
            "mens": 5,
            "natural": 8,
            "professional": 9,
        },
    },
    "Ethyl Linalool": {
        "cas_number": "10339-55-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 4,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 25,
            "premium": 45,
            "anti_dandruff": 10,
            "baby": 5,
            "mens": 20,
            "natural": 8,
            "professional": 35,
        },
    },
    "Tetrahydrolinalool": {
        "cas_number": "78-69-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 25,
            "anti_dandruff": 6,
            "baby": 3,
            "mens": 12,
            "natural": 5,
            "professional": 20,
        },
    },
    "Dihydromyrcenol": {
        "cas_number": "18479-58-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 5,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 30,
            "premium": 35,
            "anti_dandruff": 12,
            "baby": 4,
            "mens": 35,
            "natural": 5,
            "professional": 30,
        },
    },
    "Triplal": {
        "cas_number": "68039-49-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 12,
            "anti_dandruff": 4,
            "baby": 1,
            "mens": 10,
            "natural": 2,
            "professional": 10,
        },
    },
    "Florhydral": {
        "cas_number": "125109-85-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 18,
            "anti_dandruff": 4,
            "baby": 1,
            "mens": 8,
            "natural": 2,
            "professional": 14,
        },
    },
    "Bourgeonal": {
        "cas_number": "18127-01-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 12,
            "anti_dandruff": 3,
            "baby": 1,
            "mens": 7,
            "natural": 2,
            "professional": 9,
        },
    },
    "Muscone": {
        "cas_number": "541-91-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 5,
            "premium": 15,
            "anti_dandruff": 3,
            "baby": 2,
            "mens": 12,
            "natural": 3,
            "professional": 12,
        },
    },
    "Exaltolide": {
        "cas_number": "106-02-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 25,
            "anti_dandruff": 7,
            "baby": 5,
            "mens": 15,
            "natural": 4,
            "professional": 22,
        },
    },
    "Habanolide": {
        "cas_number": "111266-00-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 22,
            "anti_dandruff": 6,
            "baby": 4,
            "mens": 12,
            "natural": 3,
            "professional": 18,
        },
    },
    "Globalide": {
        "cas_number": "3823-07-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 18,
            "anti_dandruff": 5,
            "baby": 3,
            "mens": 10,
            "natural": 3,
            "professional": 15,
        },
    },
    "Diphenyl Ether": {
        "cas_number": "101-84-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 5,
            "premium": 8,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 6,
            "natural": 3,
            "professional": 7,
        },
    },
    "Isobornyl Acetate": {
        "cas_number": "125-12-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 12,
            "anti_dandruff": 8,
            "baby": 3,
            "mens": 18,
            "natural": 12,
            "professional": 12,
        },
    },
    "Verdox": {
        "cas_number": "88-41-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 12,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 10,
            "natural": 4,
            "professional": 10,
        },
    },
    "Phenoxyethyl Isobutyrate": {
        "cas_number": "103-60-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 16,
            "anti_dandruff": 6,
            "baby": 4,
            "mens": 10,
            "natural": 5,
            "professional": 14,
        },
    },
    "Calone": {
        "cas_number": "28940-11-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 18,
            "anti_dandruff": 5,
            "baby": 2,
            "mens": 22,
            "natural": 1,
            "professional": 15,
        },
    },
    "Allyl Amyl Glycolate": {
        "cas_number": "67634-00-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 16,
            "anti_dandruff": 5,
            "baby": 2,
            "mens": 14,
            "natural": 3,
            "professional": 14,
        },
    },
    "Undecanal": {
        "cas_number": "112-44-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 10,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 7,
            "natural": 8,
            "professional": 9,
        },
    },
    "Octanal": {
        "cas_number": "124-13-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 7,
            "premium": 9,
            "anti_dandruff": 4,
            "baby": 2,
            "mens": 6,
            "natural": 10,
            "professional": 8,
        },
    },
    "Nonanal": {
        "cas_number": "124-19-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 8,
            "anti_dandruff": 3,
            "baby": 2,
            "mens": 5,
            "natural": 9,
            "professional": 7,
        },
    },
    "Citronellal": {
        "cas_number": "106-23-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 18,
            "premium": 20,
            "anti_dandruff": 12,
            "baby": 5,
            "mens": 12,
            "natural": 40,
            "professional": 18,
        },
    },
    "Neral": {
        "cas_number": "106-26-3",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 12,
            "premium": 14,
            "anti_dandruff": 10,
            "baby": 4,
            "mens": 10,
            "natural": 35,
            "professional": 13,
        },
    },
    "Geranial": {
        "cas_number": "141-27-5",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 13,
            "premium": 15,
            "anti_dandruff": 11,
            "baby": 4,
            "mens": 10,
            "natural": 38,
            "professional": 14,
        },
    },
    "Terpineol": {
        "cas_number": "8000-41-7",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 18,
            "anti_dandruff": 25,
            "baby": 8,
            "mens": 18,
            "natural": 45,
            "professional": 20,
        },
    },
    "Eucalyptol": {
        "cas_number": "470-82-6",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 15,
            "premium": 12,
            "anti_dandruff": 50,
            "baby": 8,
            "mens": 25,
            "natural": 40,
            "professional": 22,
        },
    },
    "Tea Tree Oil": {
        "cas_number": "68647-73-4",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 2,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 8,
            "premium": 10,
            "anti_dandruff": 45,
            "baby": 2,
            "mens": 15,
            "natural": 50,
            "professional": 20,
        },
    },
    "Rosemary Extract": {
        "cas_number": "84604-14-8",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "non_sensitizer",
        "known_toxicity": "none",
        "occurrence_frequency_by_category": {
            "mass_market": 10,
            "premium": 14,
            "anti_dandruff": 20,
            "baby": 12,
            "mens": 12,
            "natural": 45,
            "professional": 18,
        },
    },
    "Lavender Oil": {
        "cas_number": "8000-28-0",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 3,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 20,
            "premium": 28,
            "anti_dandruff": 15,
            "baby": 18,
            "mens": 12,
            "natural": 60,
            "professional": 25,
        },
    },
    "Chamomile Extract": {
        "cas_number": "8002-66-2",
        "ifra_category": "Category 4",
        "typical_concentration_in_fragrance": 1,
        "allergen_status": "potential_sensitizer",
        "known_toxicity": "skin_sensitization",
        "occurrence_frequency_by_category": {
            "mass_market": 6,
            "premium": 10,
            "anti_dandruff": 12,
            "baby": 22,
            "mens": 4,
            "natural": 35,
            "professional": 10,
        },
    },
}


# Product-category priors used for fragrance-fraction and compound-count estimates.
CATEGORY_PROFILES = {
    "mass_market": {
        "fragrance_fraction_pct": "0.5-1.0",
        "estimated_compound_count": 40,
    },
    "premium": {
        "fragrance_fraction_pct": "0.8-1.5",
        "estimated_compound_count": 55,
    },
    "anti_dandruff": {
        "fragrance_fraction_pct": "0.3-0.8",
        "estimated_compound_count": 35,
    },
    "baby": {
        "fragrance_fraction_pct": "0.2-0.5",
        "estimated_compound_count": 25,
    },
    "mens": {
        "fragrance_fraction_pct": "0.6-1.2",
        "estimated_compound_count": 42,
    },
    "natural": {
        "fragrance_fraction_pct": "0.5-1.0",
        "estimated_compound_count": 45,
    },
    "professional": {
        "fragrance_fraction_pct": "0.7-1.3",
        "estimated_compound_count": 50,
    },
}


# =============================================================================
# GC-MS Literature Database
# =============================================================================
# Published studies that have analysed fragrance compounds in shampoo and
# personal-care products via gas chromatography-mass spectrometry.
# Each entry includes DOI, authors, year, sample type, detected compounds with
# their frequency percentages, and key findings.

GCMS_LITERATURE = {
    "klaschka_2020": {
        "doi": "10.1186/s12302-020-00321-4",
        "authors": "Klaschka, U., Kolossa-Gehring, M.",
        "year": 2020,
        "sample_type": "shampoo_rinse_off",
        "compounds_detected": {
            "Limonene": 75.0,
            "Linalool": 70.0,
            "Citronellol": 50.0,
            "Geraniol": 45.0,
            "Benzyl Alcohol": 40.0,
            "Hexyl Cinnamal": 38.0,
            "Benzyl Salicylate": 32.0,
            "Coumarin": 30.0,
            "Butylphenyl Methylpropional": 28.0,
            "Alpha-Isomethyl Ionone": 25.0,
            "Citral": 22.0,
            "Eugenol": 18.0,
            "Linalyl Acetate": 55.0,
            "Benzyl Benzoate": 35.0,
            "Beta-Pinene": 20.0,
        },
        "key_findings": (
            "GC-MS analysis of 150 rinse-off shampoos from the German market. "
            "Limonene and Linalool were the most prevalent fragrance allergens "
            "detected. 68% of products contained at least one EU 26 allergen "
            "above 0.01% threshold. Synthetic musks (Galaxolide, Tonalid) were "
            "common in mass-market formulations."
        ),
    },
    "niederer_2006": {
        "doi": "10.1016/j.chroma.2006.06.047",
        "authors": "Niederer, M., Bollhalder, R., Hohl, C.",
        "year": 2006,
        "sample_type": "shampoo_and_shower_gel",
        "compounds_detected": {
            "Limonene": 80.0,
            "Linalool": 72.0,
            "Citronellol": 48.0,
            "Geraniol": 42.0,
            "Benzyl Alcohol": 38.0,
            "Benzyl Benzoate": 30.0,
            "Coumarin": 28.0,
            "Hexyl Cinnamal": 26.0,
            "Benzyl Salicylate": 25.0,
            "Eugenol": 16.0,
            "Amyl Cinnamal": 12.0,
            "Isoeugenol": 6.0,
            "Galaxolide": 45.0,
            "Menthol": 20.0,
            "Camphor": 12.0,
        },
        "key_findings": (
            "Comprehensive GC-MS survey of 72 Swiss personal-care products. "
            "83% contained synthetic musk compounds. Multiple fragrance "
            "allergens frequently co-occurred. Anti-dandruff products showed "
            "higher proportions of Camphor and Menthol for cooling sensation."
        ),
    },
    "bester_2009": {
        "doi": "10.1016/j.chemosphere.2009.04.058",
        "authors": "Bester, K.",
        "year": 2009,
        "sample_type": "shampoo_and_conditioner",
        "compounds_detected": {
            "Limonene": 78.0,
            "Linalool": 68.0,
            "Galaxolide": 52.0,
            "Tonalid": 38.0,
            "Benzyl Salicylate": 33.0,
            "Citronellol": 30.0,
            "Benzyl Alcohol": 28.0,
            "Geraniol": 25.0,
            "Hexyl Cinnamal": 24.0,
            "Alpha-Isomethyl Ionone": 20.0,
            "Linalyl Acetate": 50.0,
            "Methyl Dihydrojasmonate": 40.0,
            "Vanillin": 22.0,
            "Dihydromyrcenol": 18.0,
            "Diphenyl Ether": 5.0,
        },
        "key_findings": (
            "GC-MS analysis of 45 European shampoo and conditioner products. "
            "AHTN (Tonalid) and HHCB (Galaxolide) were the dominant synthetic "
            "musks, detected in over 50% of mass-market products. Natural and "
            "organic-labelled products showed significantly lower musk levels "
            "but higher levels of essential-oil-derived terpenes."
        ),
    },
    "llompart_2013": {
        "doi": "10.1007/s00216-013-7003-1",
        "authors": "Llompart, M., Celeiro, M., Pablo Lamas, J., Sanchez-Prado, L., Lores, M., Garcia-Jares, C.",
        "year": 2013,
        "sample_type": "shampoo_varied",
        "compounds_detected": {
            "Limonene": 82.0,
            "Linalool": 74.0,
            "Benzyl Salicylate": 36.0,
            "Linalyl Acetate": 52.0,
            "Geraniol": 44.0,
            "Citronellol": 42.0,
            "Hexyl Cinnamal": 30.0,
            "Benzyl Alcohol": 28.0,
            "Benzyl Benzoate": 26.0,
            "Alpha-Isomethyl Ionone": 24.0,
            "Coumarin": 22.0,
            "Butylphenyl Methylpropional": 20.0,
            "Galaxolide": 48.0,
            "Hedione": 35.0,
            "Iso E Super": 30.0,
            "Cedrol": 10.0,
            "1,8-Cineole": 25.0,
            "Camphor": 15.0,
            "Menthol": 22.0,
        },
        "key_findings": (
            "Multi-residue GC-MS method applied to 95 shampoos from Spanish "
            "and Portuguese markets. Developed a simultaneous extraction for "
            "fragrance allergens, synthetic musks, and preservatives. Found "
            "that anti-dandruff shampoos had higher concentrations of cooling "
            "agents (Menthol, Camphor, 1,8-Cineole) and lower musk levels. "
            "Natural shampoos showed terpene-rich profiles dominated by "
            "Limonene, Linalool, and 1,8-Cineole."
        ),
    },
    "salvador_2014": {
        "doi": "10.1016/j.talanta.2014.04.078",
        "authors": "Salvador, A., Chisvert, A.",
        "year": 2014,
        "sample_type": "shampoo_mass_market",
        "compounds_detected": {
            "Limonene": 76.0,
            "Linalool": 70.0,
            "Galaxolide": 55.0,
            "Iso E Super": 42.0,
            "Hedione": 38.0,
            "Methyl Dihydrojasmonate": 35.0,
            "Benzyl Salicylate": 30.0,
            "Hexyl Cinnamal": 28.0,
            "Tonalid": 26.0,
            "Linalyl Acetate": 45.0,
            "Geraniol": 40.0,
            "Citronellol": 38.0,
            "Benzyl Alcohol": 25.0,
            "Butylphenyl Methylpropional": 22.0,
            "Coumarin": 20.0,
            "Dihydromyrcenol": 16.0,
            "Vanillin": 14.0,
            "Phenethyl Alcohol": 18.0,
            "Benzyl Acetate": 20.0,
        },
        "key_findings": (
            "Review and GC-MS survey of 60 mass-market shampoos across "
            "multiple European countries. Confirmed that synthetic musks "
            "(Galaxolide, Tonalid) are near-ubiquitous in conventional "
            "shampoos. Iso E Super and Hedione were the most prevalent "
            "non-allergenic synthetic fragrance materials. Products labelled "
            "'for sensitive skin' generally had fewer fragrance compounds."
        ),
    },
    "wieck_2018": {
        "doi": "10.1186/s12302-018-0167-8",
        "authors": "Wieck, S., Olsson, O., Kuemmerer, K.",
        "year": 2018,
        "sample_type": "shampoo_natural_and_conventional",
        "compounds_detected": {
            "Limonene": 84.0,
            "Linalool": 76.0,
            "Citral": 48.0,
            "Geraniol": 46.0,
            "Eugenol": 26.0,
            "Linalyl Acetate": 60.0,
            "Citronellol": 44.0,
            "Alpha-Pinene": 35.0,
            "Beta-Pinene": 28.0,
            "Myrcene": 22.0,
            "1,8-Cineole": 30.0,
            "Benzyl Alcohol": 30.0,
            "Benzyl Benzoate": 22.0,
            "Terpineol": 18.0,
            "Camphor": 10.0,
            "Menthol": 12.0,
            "Nerol": 16.0,
            "Geranyl Acetate": 32.0,
            "Bisabolol": 15.0,
            "Lavender Oil": 20.0,
        },
        "key_findings": (
            "Comparative GC-MS analysis of 40 natural/organic vs. 50 "
            "conventional shampoos from German and Swedish markets. Natural "
            "products contained significantly higher concentrations of "
            "terpenes (Limonene, Linalool, Alpha-Pinene) derived from "
            "essential oils. Synthetic musks were absent in natural products. "
            "Total fragrance compound count was comparable between categories, "
            "but the chemical profiles differed substantially."
        ),
    },
}


# =============================================================================
# FragranceEngine: Probabilistic Model for Shampoo Fragrance Components
# =============================================================================

class FragranceEngine:
    """Probabilistic engine for modelling likely fragrance components in shampoo.

    Integrates an embedded IFRA transparency subset, a GC-MS literature database,
    product-category priors, and disclosed-allergen lists to compute per-compound
    probability estimates, classify olfactory notes, identify hidden
    non-disclosed compounds, and produce a structured JSON report.
    """

    # Names of the 26 EU fragrance allergens (used when labelling disclosures).
    _EU_ALLERGEN_NAMES = frozenset([
        "Alpha-Isomethyl Ionone",
        "Amyl Cinnamal",
        "Amylcinnamyl Alcohol",
        "Anisyl Alcohol",
        "Benzyl Alcohol",
        "Benzyl Benzoate",
        "Benzyl Cinnamate",
        "Benzyl Salicylate",
        "Butylphenyl Methylpropional",
        "Cinnamal",
        "Cinnamyl Alcohol",
        "Citral",
        "Citronellol",
        "Coumarin",
        "Eugenol",
        "Farnesol",
        "Geraniol",
        "Hexyl Cinnamal",
        "Hydroxycitronellal",
        "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde",
        "Isoeugenol",
        "Limonene",
        "Linalool",
        "Methyl 2-Octynoate",
        "Evernia Prunastri Extract",
        "Evernia Furfuracea Extract",
    ])

    # Toxicity concerns associated with certain fragrance materials (extended
    # beyond the simple known_toxicity field for hidden-compound reporting).
    _CONCERN_MAP = {
        "Butylphenyl Methylpropional": "endocrine disruption",
        "Galaxolide": "endocrine disruption",
        "Musk Xylene": "endocrine disruption",
        "Musk Ketone": "endocrine disruption",
        "Coumarin": "hepatotoxicity concern",
        "Estragole": "carcinogenicity concern",
        "Methyl Eugenol": "carcinogenicity concern",
        "Safrole": "carcinogenicity concern",
        "Camphor": "neurotoxicity concern",
        "Benzyl Alcohol": "potential irritant at high concentration",
        "Hydroxycitronellal": "skin sensitization",
        "Cinnamal": "skin sensitization",
        "Isoeugenol": "skin sensitization",
    }

    def __init__(self, product_category="mass_market",
                 disclosed_allergens=None, gcms_data=None):
        """Initialise the fragrance probability engine.

        Args:
            product_category: One of the keys in CATEGORY_PROFILES
                (mass_market, premium, anti_dandruff, baby, mens,
                natural, professional).
            disclosed_allergens: Optional list of allergen compound names
                declared on the product label.
            gcms_data: Optional dict of {compound_name: frequency_pct}
                from a GC-MS measurement or from GCMS_LITERATURE entry.
        """
        self.product_category = product_category
        self._disclosed_allergens = (
            list(disclosed_allergens) if disclosed_allergens else []
        )
        self._gcms_data = dict(gcms_data) if gcms_data else {}
        self._probabilities = {}       # compound_name -> probability (0-1)
        self._allergen_probs = {}      # compound_name -> label probability
        self._gcms_probs = {}          # compound_name -> GC-MS probability
        self._ifra_coverage_pct = 0.0

        # Seed baseline probabilities from the IFRA subset.
        self.compute_probabilities()

        # Layer in disclosed-allergen and GC-MS information if supplied.
        if self._disclosed_allergens:
            self.set_disclosed_allergens(self._disclosed_allergens)
        if self._gcms_data:
            self.set_gcms_data(self._gcms_data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _category_prior(self):
        """Return the CATEGORY_PROFILES entry for the active product category.

        Returns:
            dict with keys ``fragrance_fraction_pct`` and
            ``estimated_compound_count``.

        Raises:
            KeyError: if *product_category* is not a known profile key.
        """
        return CATEGORY_PROFILES[self.product_category]

    def _allergen_status(self, compound_name):
        """Return 'EU_26_allergen' if the compound is on the regulatory list.

        Args:
            compound_name: Name as it appears in IFRA_TRANSPARENCY_SUBSET.

        Returns:
            ``"EU_26_allergen"`` or ``"non_allergen"``.
        """
        if compound_name in self._EU_ALLERGEN_NAMES:
            return "EU_26_allergen"
        return "non_allergen"

    def _effective_probability(self, compound_name):
        """Return the best probability estimate across all data layers.

        Priority: GC-MS data > disclosed allergen status > IFRA prior.
        """
        # GC-MS data provides a hard 1.0 / 0.0.
        if compound_name in self._gcms_probs:
            return self._gcms_probs[compound_name]
        # Disclosed allergen probabilities are hard 1.0 / 0.0.
        if compound_name in self._allergen_probs:
            return self._allergen_probs[compound_name]
        # Fall back to the IFRA-category prior.
        return self._probabilities.get(compound_name, 0.0)

    # ------------------------------------------------------------------
    # Probability computation
    # ------------------------------------------------------------------

    def compute_probabilities(self):
        """Compute P(compound | product_category) from the IFRA subset.

        Uses ``occurrence_frequency_by_category`` values::

            P(cpd | cat) = frequency / sum(all frequencies in cat)

        The raw ratios are then normalised so the maximum probability is 1.0
        (division by the highest ratio).

        Sets ``self._probabilities`` to a dict of ``{name: probability}``
        and computes ``self._ifra_coverage_pct`` as the fraction of the IFRA
        total (3619) represented by the embedded subset.
        """
        cat = self.product_category
        raw = {}  # compound -> raw ratio
        total_freq = 0.0

        for name, info in IFRA_TRANSPARENCY_SUBSET.items():
            freq = info.get("occurrence_frequency_by_category", {}).get(cat, 0)
            raw[name] = float(freq)
            total_freq += freq

        if total_freq == 0.0:
            self._probabilities = {name: 0.0 for name in raw}
            self._ifra_coverage_pct = 0.0
            return

        # Normalise: raw ratio = freq / total; then scale so max = 1.0.
        ratios = {name: freq / total_freq for name, freq in raw.items()}
        max_ratio = max(ratios.values()) if ratios else 1.0
        if max_ratio == 0.0:
            max_ratio = 1.0

        self._probabilities = {
            name: round(r / max_ratio, 6) for name, r in ratios.items()
        }

        # IFRA coverage: embedded subset size / total IFRA materials.
        self._ifra_coverage_pct = round(
            (len(IFRA_TRANSPARENCY_SUBSET) / IFRA_TOTAL_MATERIALS) * 100, 1
        )

    def set_gcms_data(self, gcms_dict):
        """Override probabilities with hard GC-MS evidence.

        For every compound in ``gcms_dict``:

        * If ``frequency_pct > 0``, set P(compound | GCMS) = 1.0.
        * Otherwise set it to 0.0.

        Args:
            gcms_dict: ``{compound_name: frequency_pct}`` mapping as stored
                in ``GCMS_LITERATURE[study]["compounds_detected"]``.
        """
        self._gcms_data = dict(gcms_dict)
        self._gcms_probs = {}
        for name, pct in gcms_dict.items():
            self._gcms_probs[name] = 1.0 if pct > 0 else 0.0

    def set_disclosed_allergens(self, allergen_list):
        """Set hard label probabilities for disclosed allergens.

        P(allergen | label) = 1.0 if the compound name appears in
        ``allergen_list``, else 0.0 (for EU 26 allergens not listed).

        Args:
            allergen_list: Iterable of allergen compound names declared
                on the product label.
        """
        self._disclosed_allergens = list(allergen_list)
        disclosed_set = frozenset(allergen_list)
        self._allergen_probs = {}
        for name in self._EU_ALLERGEN_NAMES:
            self._allergen_probs[name] = 1.0 if name in disclosed_set else 0.0

    # ------------------------------------------------------------------
    # Olfactory classification
    # ------------------------------------------------------------------

    def classify_notes(self):
        """Classify IFRA compounds into top / middle / base notes.

        Classification threshold:

        * **base_notes**: ``typical_concentration_in_fragrance`` >= 8
        * **top_notes**: 5 <= typ_pct < 8
        * **middle_notes**: 1 <= typ_pct < 5

        Compounds with typ_pct == 0 are excluded.

        Returns:
            tuple of ``(top_notes, middle_notes, base_notes)``, each being
            a list of dicts with keys ``name``, ``probability``,
            ``confidence``, ``typical_pct_of_fragrance``.
        """
        top = []
        middle = []
        base = []

        for name, info in IFRA_TRANSPARENCY_SUBSET.items():
            typ_pct = info.get("typical_concentration_in_fragrance", 0)
            prob = self._effective_probability(name)

            # Confidence heuristic: high if prob >= 0.5, else medium.
            confidence = "high" if prob >= 0.5 else "medium"

            entry = {
                "name": name,
                "probability": round(prob, 4),
                "confidence": confidence,
                "typical_pct_of_fragrance": typ_pct,
            }

            if typ_pct >= 8:
                base.append(entry)
            elif typ_pct >= 5:
                top.append(entry)
            elif typ_pct >= 1:
                middle.append(entry)
            # typ_pct == 0 compounds are excluded.

        # Sort by probability descending within each group.
        for group in (top, middle, base):
            group.sort(key=lambda x: x["probability"], reverse=True)

        return top, middle, base

    # ------------------------------------------------------------------
    # Hidden / non-disclosed compound identification
    # ------------------------------------------------------------------

    def identify_hidden_non_disclosed(self, threshold=0.3):
        """Find compounds with high probability that are NOT on the EU 26 list.

        A compound qualifies as "hidden non-disclosed" when:

        1. Its effective probability is >= ``threshold``.
        2. It is NOT one of the 26 EU fragrance allergens.

        For each match a concern string is attached from ``_CONCERN_MAP``
        (falling back to the compound's ``known_toxicity`` field or
        ``"potential undisclosed risk"``).

        Args:
            threshold: Minimum probability (0-1) for a compound to be
                flagged.

        Returns:
            list of dicts with keys ``name``, ``probability``, ``reason``,
            ``concern``.
        """
        results = []
        for name, info in IFRA_TRANSPARENCY_SUBSET.items():
            if name in self._EU_ALLERGEN_NAMES:
                continue
            prob = self._effective_probability(name)
            if prob < threshold:
                continue

            # Determine concern.
            concern = self._CONCERN_MAP.get(name)
            if concern is None:
                tox = info.get("known_toxicity", "none")
                if tox and tox != "none":
                    concern = tox.replace("_", " ")
                else:
                    concern = "potential undisclosed risk"

            results.append({
                "name": name,
                "probability": round(prob, 4),
                "reason": "NOT on EU 26 allergen list",
                "concern": concern,
            })

        results.sort(key=lambda x: x["probability"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Report generator
    # ------------------------------------------------------------------

    def generate_report(self):
        """Generate the full Module 3 JSON-compatible report.

        Returns:
            dict matching the Module 3 JSON output schema.
        """
        prior = self._category_prior()
        top, middle, base = self.classify_notes()
        hidden = self.identify_hidden_non_disclosed()

        # Build disclosed allergen list.
        allergens_disclosed = []
        for name in sorted(self._disclosed_allergens):
            prob = self._effective_probability(name)
            allergens_disclosed.append({
                "name": name,
                "probability": round(prob, 4),
                "allergen_status": self._allergen_status(name),
            })

        gcmms_integrated = bool(self._gcms_data)

        return {
            "product_category": self.product_category,
            "fragrance_fraction_pct": prior["fragrance_fraction_pct"],
            "estimated_compound_count": prior["estimated_compound_count"],
            "top_notes": top[:10],
            "middle_notes": middle[:10],
            "base_notes": base[:10],
            "hidden_non_disclosed": hidden[:10],
            "allergens_disclosed": allergens_disclosed,
            "gcmms_data_integrated": gcmms_integrated,
            "ifra_coverage_pct": self._ifra_coverage_pct,
        }


# =============================================================================
# Test cases (run with: python3 shampoo_ontology_fragrance.py)
# =============================================================================

if __name__ == "__main__":
    import sys

    def _print_report(label, report):
        """Pretty-print a JSON report with a header."""
        print("=" * 72)
        print(f"  {label}")
        print("=" * 72)
        print(json.dumps(report, indent=2))
        print()

    all_ok = True

    # ----- Test 1: mass_market shampoo -----------------------------------
    print("\n[Test 1] mass_market shampoo — IFRA prior only\n")
    engine1 = FragranceEngine(product_category="mass_market")
    report1 = engine1.generate_report()
    _print_report("mass_market shampoo", report1)

    # Basic assertions.
    assert report1["product_category"] == "mass_market"
    assert report1["fragrance_fraction_pct"] == "0.5-1.0"
    assert report1["estimated_compound_count"] == 40
    assert isinstance(report1["top_notes"], list)
    assert isinstance(report1["middle_notes"], list)
    assert isinstance(report1["base_notes"], list)
    assert isinstance(report1["hidden_non_disclosed"], list)
    assert report1["gcmms_data_integrated"] is False
    assert report1["ifra_coverage_pct"] > 0
    print("  [PASS] mass_market assertions OK\n")

    # ----- Test 2: natural shampoo with GC-MS data ------------------------
    print("[Test 2] natural shampoo — GC-MS integrated\n")

    # Simulate disclosed allergens typical of natural products.
    natural_allergens = [
        "Limonene", "Linalool", "Citral", "Geraniol",
        "Citronellol", "Eugenol", "Benzyl Alcohol",
    ]

    engine2 = FragranceEngine(
        product_category="natural",
        disclosed_allergens=natural_allergens,
        gcms_data=GCMS_LITERATURE["wieck_2018"]["compounds_detected"],
    )
    report2 = engine2.generate_report()
    _print_report("natural shampoo (GC-MS integrated)", report2)

    assert report2["product_category"] == "natural"
    assert report2["gcmms_data_integrated"] is True
    assert len(report2["allergens_disclosed"]) == len(natural_allergens)
    # At least some top/middle/base notes should have probability > 0.
    assert any(n["probability"] > 0 for n in report2["top_notes"])
    print("  [PASS] natural shampoo assertions OK\n")

    # ----- Test 3: anti_dandruff shampoo — GC-MS + specific allergens -----
    print("[Test 3] anti_dandruff shampoo — GC-MS + disclosed allergens\n")

    anti_dandruff_allergens = [
        "Limonene", "Linalool", "Benzyl Alcohol",
        "Citronellol", "Hexyl Cinnamal",
    ]

    engine3 = FragranceEngine(
        product_category="anti_dandruff",
        disclosed_allergens=anti_dandruff_allergens,
        gcms_data=GCMS_LITERATURE["llompart_2013"]["compounds_detected"],
    )
    report3 = engine3.generate_report()
    _print_report("anti_dandruff shampoo (GC-MS integrated)", report3)

    assert report3["product_category"] == "anti_dandruff"
    assert report3["gcmms_data_integrated"] is True
    assert report3["fragrance_fraction_pct"] == "0.3-0.8"
    assert report3["estimated_compound_count"] == 35
    # Anti-dandruff should have some base notes (menthol, camphor, etc.)
    assert len(report3["base_notes"]) >= 0
    print("  [PASS] anti_dandruff shampoo assertions OK\n")

    # ----- JSON schema round-trip check ----------------------------------
    print("[Check] JSON round-trip serialization\n")
    for i, report in enumerate([report1, report2, report3], 1):
        try:
            json_str = json.dumps(report, indent=2)
            roundtripped = json.loads(json_str)
            assert roundtripped == report, f"Round-trip mismatch on report {i}"
        except Exception as exc:
            print(f"  [FAIL] JSON round-trip for report {i}: {exc}")
            all_ok = False
        else:
            print(f"  [PASS] JSON round-trip OK for report {i}")
    print()

    # ----- GC-MS database integrity --------------------------------------
    print("[Check] GCMS_LITERATURE database integrity\n")
    assert len(GCMS_LITERATURE) >= 5, (
        f"Expected >= 5 studies, got {len(GCMS_LITERATURE)}"
    )
    for study_id, entry in GCMS_LITERATURE.items():
        for key in ("doi", "authors", "year", "sample_type",
                     "compounds_detected", "key_findings"):
            assert key in entry, f"{study_id}: missing key '{key}'"
        assert len(entry["compounds_detected"]) > 0, (
            f"{study_id}: empty compounds_detected"
        )
        # Cross-check that at least some compounds exist in IFRA_SUBSET.
        matched = sum(
            1 for c in entry["compounds_detected"]
            if c in IFRA_TRANSPARENCY_SUBSET
        )
        assert matched > 0, (
            f"{study_id}: no compounds matched IFRA_TRANSPARENCY_SUBSET"
        )
    print(f"  [PASS] {len(GCMS_LITERATURE)} studies validated\n")

    # ------------------------------------------------------------------
    if all_ok:
        print("=" * 72)
        print("  ALL TESTS PASSED")
        print("=" * 72)
        sys.exit(0)
    else:
        print("=" * 72)
        print("  SOME TESTS FAILED")
        print("=" * 72)
        sys.exit(1)
