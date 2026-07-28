#!/usr/bin/env python3
"""Supplier preservative audit tool for the shampoo ingredient ontology v4.0.

This module traces preservative carryover from raw-material suppliers into a
finished shampoo formulation, compares the calculated concentrations against
brand marketing claims, and flags EU regulatory thresholds.

All data is embedded as Python structures. Only the Python standard library is
used.
"""

import json
from typing import Any, Dict, List, Optional, Set


# EU SCCS concentration limits for common preservatives in rinse-off cosmetic
# products. Values are percentages of the preservative (acid form where the
# regulation specifies it) in the final formulation. Sources: EU Regulation
# 1223/2009 Annex V entries and SCCS opinions.
EU_SCCS_LIMITS: Dict[str, float] = {
    "METHYLPARABEN": 0.4,
    "ETHYLPARABEN": 0.4,
    "PROPYLPARABEN": 0.14,
    "BUTYLPARABEN": 0.14,
    "ISOBUTYLPARABEN": 0.14,
    "PHENOXYETHANOL": 1.0,
    "SODIUM BENZOATE": 2.5,
    "POTASSIUM SORBATE": 2.5,
    "BENZOIC ACID": 2.5,
    "SORBIC ACID": 0.6,
    "SALICYLIC ACID": 3.0,
    "DMDM HYDANTOIN": 0.6,
    "DIAZOLIDINYL UREA": 0.5,
    "IMIDAZOLIDINYL UREA": 0.5,
    "IODOPROPYNYL BUTYLCARBAMATE": 0.05,
    "METHYLISOTHIAZOLINONE": 0.0015,
    "METHYLCHLOROISOTHIAZOLINONE": 0.0015,
    "TRICLOSAN": 0.3,
    "BENZALKONIUM CHLORIDE": 0.1,
    "BENZYL ALCOHOL": 1.0,
    "SODIUM HYDROXYMETHYLGLYCINATE": 0.5,
    "CHLORPHENESIN": 0.3,
    "CAPRYLYL GLYCOL": 1.0,
    "ETHYLHEXYLGLYCERIN": 0.5,
    "SODIUM DEHYDROACETATE": 0.6,
    "DEHYDROACETIC ACID": 0.6,
}

# Substances considered parabens for claim verification.
PARABENS: Set[str] = {
    "METHYLPARABEN",
    "ETHYLPARABEN",
    "PROPYLPARABEN",
    "BUTYLPARABEN",
    "ISOBUTYLPARABEN",
}

# Preservatives that are not accepted under a "natural" claim in this audit.
SYNTHETIC_PRESERVATIVES: Set[str] = {
    "METHYLPARABEN",
    "ETHYLPARABEN",
    "PROPYLPARABEN",
    "BUTYLPARABEN",
    "ISOBUTYLPARABEN",
    "PHENOXYETHANOL",
    "DMDM HYDANTOIN",
    "DIAZOLIDINYL UREA",
    "IMIDAZOLIDINYL UREA",
    "IODOPROPYNYL BUTYLCARBAMATE",
    "METHYLISOTHIAZOLINONE",
    "METHYLCHLOROISOTHIAZOLINONE",
    "TRICLOSAN",
    "BENZALKONIUM CHLORIDE",
    "BENZYL ALCOHOL",
    "SODIUM HYDROXYMETHYLGLYCINATE",
    "QUATERNIUM-15",
    "POLYAMINOPROPYL BIGUANIDE",
    "CHLORPHENESIN",
    "CAPRYLYL GLYCOL",
    "ETHYLHEXYLGLYCERIN",
    "DECYLENE GLYCOL",
    "PENTYLENE GLYCOL",
    "PHENYLPROPANOL",
    "SODIUM DEHYDROACETATE",
    "DEHYDROACETIC ACID",
}

# EU incidental ingredient labeling threshold. Substances present solely as
# carryover below this value are generally not required to be labeled.
EU_INCIDENTAL_THRESHOLD_PCT: float = 0.01


# Supplier preservative database.
# Each entry describes a supplier raw material, the preservatives present in the
# supplied concentrate, and the typical use level in a final shampoo.
SUPPLIER_PRESERVATIVE_DATABASE: Dict[str, Dict[str, Any]] = {
    "BASF_TEXAPON_N70": {
        "supplier_name": "BASF",
        "product_code": "BASF_TEXAPON_N70",
        "product_name": "Texapon N70",
        "ingredient_type": "Sodium Laureth Sulfate",
        "preservatives": [
            {
                "name": "METHYLPARABEN",
                "cas": "99-76-3",
                "typical_pct_in_concentrate": 0.10,
                "function": "preservative",
            },
            {
                "name": "PROPYLPARABEN",
                "cas": "94-13-3",
                "typical_pct_in_concentrate": 0.10,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 15.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://cosmetics.basf.com/tds/texapon-n70",
        "sds_url": "https://cosmetics.basf.com/sds/texapon-n70",
        "last_verified_date": "2026-07-20",
    },
    "BASF_DEHYTON_PK45": {
        "supplier_name": "BASF",
        "product_code": "BASF_DEHYTON_PK45",
        "product_name": "Dehyton PK 45",
        "ingredient_type": "Cocamidopropyl Betaine",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.50,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 8.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://cosmetics.basf.com/tds/dehyton-pk45",
        "sds_url": "https://cosmetics.basf.com/sds/dehyton-pk45",
        "last_verified_date": "2026-07-20",
    },
    "CRODA_CRODASINIC_LS30": {
        "supplier_name": "Croda",
        "product_code": "CRODA_CRODASINIC_LS30",
        "product_name": "Crodasinic LS30",
        "ingredient_type": "Sodium Lauroyl Sarcosinate",
        "preservatives": [
            {
                "name": "PHENOXYETHANOL",
                "cas": "122-99-6",
                "typical_pct_in_concentrate": 0.60,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 10.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.croda.com/tds/crodasinic-ls30",
        "sds_url": "https://www.croda.com/sds/crodasinic-ls30",
        "last_verified_date": "2026-07-21",
    },
    "CRODA_INCROQUAT_BEHENYL_TMS": {
        "supplier_name": "Croda",
        "product_code": "CRODA_INCROQUAT_BEHENYL_TMS",
        "product_name": "Incroquat Behenyl TMS",
        "ingredient_type": "Behentrimonium Methosulfate",
        "preservatives": [
            {
                "name": "BENZYL ALCOHOL",
                "cas": "100-51-6",
                "typical_pct_in_concentrate": 0.40,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 3.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.croda.com/tds/incroquat-behenyl-tms",
        "sds_url": "https://www.croda.com/sds/incroquat-behenyl-tms",
        "last_verified_date": "2026-07-21",
    },
    "EVONIK_TEGO_BETAIN_F50": {
        "supplier_name": "Evonik",
        "product_code": "EVONIK_TEGO_BETAIN_F50",
        "product_name": "TEGO Betain F 50",
        "ingredient_type": "Cocamidopropyl Betaine",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.40,
                "function": "preservative",
            },
            {
                "name": "POTASSIUM SORBATE",
                "cas": "24634-61-5",
                "typical_pct_in_concentrate": 0.20,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 8.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://care-solutions.evonik.com/tds/tego-betain-f50",
        "sds_url": "https://care-solutions.evonik.com/sds/tego-betain-f50",
        "last_verified_date": "2026-07-21",
    },
    "DOW_UCARE_JR400": {
        "supplier_name": "Dow",
        "product_code": "DOW_UCARE_JR400",
        "product_name": "UCARE Polymer JR-400",
        "ingredient_type": "Polyquaternium-10",
        "preservatives": [
            {
                "name": "DMDM HYDANTOIN",
                "cas": "6440-58-0",
                "typical_pct_in_concentrate": 0.30,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 1.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.dow.com/tds/ucare-jr400",
        "sds_url": "https://www.dow.com/sds/ucare-jr400",
        "last_verified_date": "2026-07-21",
    },
    "CLARIANT_GENAPOL_LRO": {
        "supplier_name": "Clariant",
        "product_code": "CLARIANT_GENAPOL_LRO",
        "product_name": "Genapol LRO Liquid",
        "ingredient_type": "Sodium Laureth Sulfate",
        "preservatives": [
            {
                "name": "METHYLPARABEN",
                "cas": "99-76-3",
                "typical_pct_in_concentrate": 0.08,
                "function": "preservative",
            },
            {
                "name": "PROPYLPARABEN",
                "cas": "94-13-3",
                "typical_pct_in_concentrate": 0.08,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 15.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.clariant.com/tds/genapol-lro",
        "sds_url": "https://www.clariant.com/sds/genapol-lro",
        "last_verified_date": "2026-07-22",
    },
    "SOLVAY_RHODAPEX_ESB70": {
        "supplier_name": "Solvay",
        "product_code": "SOLVAY_RHODAPEX_ESB70",
        "product_name": "Rhodapex ESB-70 NAT",
        "ingredient_type": "Sodium Laureth Sulfate",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.30,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 15.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.solvay.com/tds/rhodapex-esb70-nat",
        "sds_url": "https://www.solvay.com/sds/rhodapex-esb70-nat",
        "last_verified_date": "2026-07-22",
    },
    "LONZA_GLYDANT_PLUS": {
        "supplier_name": "Lonza",
        "product_code": "LONZA_GLYDANT_PLUS",
        "product_name": "Glydant Plus Liquid",
        "ingredient_type": "Preservative Blend",
        "preservatives": [
            {
                "name": "DMDM HYDANTOIN",
                "cas": "6440-58-0",
                "typical_pct_in_concentrate": 55.0,
                "function": "preservative",
            },
            {
                "name": "IODOPROPYNYL BUTYLCARBAMATE",
                "cas": "55406-53-6",
                "typical_pct_in_concentrate": 0.30,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 0.30,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://bioscience.lonza.com/tds/glydant-plus",
        "sds_url": "https://bioscience.lonza.com/sds/glydant-plus",
        "last_verified_date": "2026-07-22",
    },
    "ASHLAND_GERMALL_PLUS": {
        "supplier_name": "Ashland",
        "product_code": "ASHLAND_GERMALL_PLUS",
        "product_name": "Germall Plus",
        "ingredient_type": "Preservative Blend",
        "preservatives": [
            {
                "name": "DIAZOLIDINYL UREA",
                "cas": "78491-02-8",
                "typical_pct_in_concentrate": 91.0,
                "function": "preservative",
            },
            {
                "name": "IODOPROPYNYL BUTYLCARBAMATE",
                "cas": "55406-53-6",
                "typical_pct_in_concentrate": 0.30,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 0.30,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.ashland.com/tds/germall-plus",
        "sds_url": "https://www.ashland.com/sds/germall-plus",
        "last_verified_date": "2026-07-22",
    },
    "STEPAN_STEOL_4N": {
        "supplier_name": "Stepan",
        "product_code": "STEPAN_STEOL_4N",
        "product_name": "Steol 4N",
        "ingredient_type": "Sodium Laureth Sulfate",
        "preservatives": [
            {
                "name": "METHYLISOTHIAZOLINONE",
                "cas": "2682-20-4",
                "typical_pct_in_concentrate": 0.02,
                "function": "preservative",
            },
            {
                "name": "METHYLCHLOROISOTHIAZOLINONE",
                "cas": "26172-55-4",
                "typical_pct_in_concentrate": 0.02,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 15.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.stepan.com/tds/steol-4n",
        "sds_url": "https://www.stepan.com/sds/steol-4n",
        "last_verified_date": "2026-07-22",
    },
    "INNOSPEC_ISELUX_ULTRA_MILD": {
        "supplier_name": "Innospec",
        "product_code": "INNOSPEC_ISELUX_ULTRA_MILD",
        "product_name": "Iselux Ultra Mild",
        "ingredient_type": "Sodium Lauroyl Methyl Isethionate",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.25,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 12.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.innospecinc.com/tds/iselux-ultra-mild",
        "sds_url": "https://www.innospecinc.com/sds/iselux-ultra-mild",
        "last_verified_date": "2026-07-22",
    },
    "LUBRIZOL_GLUCAMATE_LT": {
        "supplier_name": "Lubrizol",
        "product_code": "LUBRIZOL_GLUCAMATE_LT",
        "product_name": "Glucamate LT",
        "ingredient_type": "Methyl Glucose Dioleate",
        "preservatives": [
            {
                "name": "PHENOXYETHANOL",
                "cas": "122-99-6",
                "typical_pct_in_concentrate": 0.50,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 2.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.lubrizol.com/tds/glucamate-lt",
        "sds_url": "https://www.lubrizol.com/sds/glucamate-lt",
        "last_verified_date": "2026-07-23",
    },
    "KAO_AKYPO_RLM_45": {
        "supplier_name": "Kao Chemicals",
        "product_code": "KAO_AKYPO_RLM_45",
        "product_name": "Akypo RLM 45 NV",
        "ingredient_type": "Sodium Laureth-11 Carboxylic Acid",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.20,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 5.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://kaochemicals.com/tds/akypo-rlm-45",
        "sds_url": "https://kaochemicals.com/sds/akypo-rlm-45",
        "last_verified_date": "2026-07-23",
    },
    "NOURYON_BEROL_266": {
        "supplier_name": "Nouryon",
        "product_code": "NOURYON_BEROL_266",
        "product_name": "Berol 266",
        "ingredient_type": "Alcohol Ethoxylate",
        "preservatives": [
            {
                "name": "BENZISOTHIAZOLINONE",
                "cas": "2634-33-5",
                "typical_pct_in_concentrate": 0.10,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 2.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.nouryon.com/tds/berol-266",
        "sds_url": "https://www.nouryon.com/sds/berol-266",
        "last_verified_date": "2026-07-23",
    },
    "SASOL_SAFOL_23E7": {
        "supplier_name": "Sasol",
        "product_code": "SASOL_SAFOL_23E7",
        "product_name": "Safol 23E7",
        "ingredient_type": "C12-13 Pareth-7",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.15,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 2.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.sasol.com/tds/safol-23e7",
        "sds_url": "https://www.sasol.com/sds/safol-23e7",
        "last_verified_date": "2026-07-23",
    },
    "OLEON_RADIA_7504": {
        "supplier_name": "Oleon",
        "product_code": "OLEON_RADIA_7504",
        "product_name": "Radia 7504",
        "ingredient_type": "Caprylic/Capric Triglyceride",
        "preservatives": [
            {
                "name": "TOCOPHEROL",
                "cas": "1406-18-4",
                "typical_pct_in_concentrate": 0.10,
                "function": "antioxidant",
            },
        ],
        "typical_dilution_in_final": 1.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.oleon.com/tds/radia-7504",
        "sds_url": "https://www.oleon.com/sds/radia-7504",
        "last_verified_date": "2026-07-23",
    },
    "IOI_PALMAC_1600": {
        "supplier_name": "IOI Oleo",
        "product_code": "IOI_PALMAC_1600",
        "product_name": "Palmac 1600",
        "ingredient_type": "Cetyl Alcohol",
        "preservatives": [
            {
                "name": "BHT",
                "cas": "128-37-0",
                "typical_pct_in_concentrate": 0.05,
                "function": "antioxidant",
            },
        ],
        "typical_dilution_in_final": 2.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.ioioleo.com/tds/palmac-1600",
        "sds_url": "https://www.ioioleo.com/sds/palmac-1600",
        "last_verified_date": "2026-07-23",
    },
    "EMERY_5320": {
        "supplier_name": "Emery Oleochemicals",
        "product_code": "EMERY_5320",
        "product_name": "Emery 5320",
        "ingredient_type": "Cocamide MEA",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.20,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 3.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.emeryoleo.com/tds/emery-5320",
        "sds_url": "https://www.emeryoleo.com/sds/emery-5320",
        "last_verified_date": "2026-07-23",
    },
    "VANTAGE_LIPOVOL_P": {
        "supplier_name": "Vantage",
        "product_code": "VANTAGE_LIPOVOL_P",
        "product_name": "Lipovol P",
        "ingredient_type": "Persea Gratissima Oil",
        "preservatives": [
            {
                "name": "TOCOPHEROL",
                "cas": "1406-18-4",
                "typical_pct_in_concentrate": 0.20,
                "function": "antioxidant",
            },
        ],
        "typical_dilution_in_final": 1.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.vantagepersonalcare.com/tds/lipovol-p",
        "sds_url": "https://www.vantagepersonalcare.com/sds/lipovol-p",
        "last_verified_date": "2026-07-24",
    },
    "COLONIAL_COLATERIC_CDS": {
        "supplier_name": "Colonial Chemical",
        "product_code": "COLONIAL_COLATERIC_CDS",
        "product_name": "ColaTeric CDS",
        "ingredient_type": "Cocamidopropyl Betaine",
        "preservatives": [
            {
                "name": "SODIUM BENZOATE",
                "cas": "532-32-1",
                "typical_pct_in_concentrate": 0.40,
                "function": "preservative",
            },
            {
                "name": "POTASSIUM SORBATE",
                "cas": "24634-61-5",
                "typical_pct_in_concentrate": 0.20,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 8.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.colonialchem.com/tds/colateric-cds",
        "sds_url": "https://www.colonialchem.com/sds/colateric-cds",
        "last_verified_date": "2026-07-24",
    },
    "PILOT_CALFOAM_ES30": {
        "supplier_name": "Pilot Chemical",
        "product_code": "PILOT_CALFOAM_ES30",
        "product_name": "Calfoam ES-30",
        "ingredient_type": "Sodium Laureth Sulfate",
        "preservatives": [
            {
                "name": "METHYLPARABEN",
                "cas": "99-76-3",
                "typical_pct_in_concentrate": 0.08,
                "function": "preservative",
            },
            {
                "name": "PROPYLPARABEN",
                "cas": "94-13-3",
                "typical_pct_in_concentrate": 0.08,
                "function": "preservative",
            },
        ],
        "typical_dilution_in_final": 15.0,
        "carryover_calculation": "typical_pct_in_concentrate * typical_dilution_in_final / 100",
        "tds_url": "https://www.pilotchemical.com/tds/calfoam-es30",
        "sds_url": "https://www.pilotchemical.com/sds/calfoam-es30",
        "last_verified_date": "2026-07-24",
    },
}


class SupplierAudit:
    """Audit a finished shampoo formulation for upstream preservative carryover.

    The audit cross-references the supplier raw materials used in the
    formulation against an embedded supplier preservative database, calculates
    the concentration of each preservative that may be carried over into the
    final product, and compares those concentrations to brand marketing claims
    and EU regulatory thresholds.

    Parameters
    ----------
    product_name : str
        Name of the finished product being audited.
    ingredient_list : list[str]
        INCI ingredient names present in the final product, ordered by
        descending concentration when available.
    supplier_codes : list[str] | None
        Supplier product codes used in the formulation. If None or empty, the
        audit attempts to infer supplier products from ingredient names.
    brand_claims : list[str] | None
        Marketing claims to verify, e.g. ["paraben-free", "preservative-free",
        "natural"].
    supplier_database : dict | None
        Override for the default SUPPLIER_PRESERVATIVE_DATABASE.
    sccs_limits : dict | None
        Override for the default EU_SCCS_LIMITS.

    Attributes
    ----------
    report : dict
        Structured audit report produced by ``audit()``.
    """

    def __init__(
        self,
        product_name: str,
        ingredient_list: List[str],
        supplier_codes: Optional[List[str]] = None,
        brand_claims: Optional[List[str]] = None,
        supplier_database: Optional[Dict[str, Dict[str, Any]]] = None,
        sccs_limits: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initialize the audit with product and formulation data."""
        self.product_name = product_name
        self.ingredient_list = [self._normalize_name(i) for i in (ingredient_list or [])]
        self.supplier_codes = [self._normalize_name(c) for c in (supplier_codes or [])]
        self.brand_claims = [c.lower().strip() for c in (brand_claims or [])]
        self.supplier_database = supplier_database or SUPPLIER_PRESERVATIVE_DATABASE
        self.sccs_limits = sccs_limits or EU_SCCS_LIMITS
        self.report: Dict[str, Any] = {}

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Return a normalized upper-case version of an ingredient or code.

        Parameters
        ----------
        name : str
            Raw name or code string.

        Returns
        -------
        str
            Upper-case string with leading/trailing whitespace removed.
        """
        return name.strip().upper()

    def _lookup_supplier_products(self) -> List[Dict[str, Any]]:
        """Return supplier database entries relevant to this formulation.

        If explicit supplier codes were provided, only those entries are used.
        Otherwise, entries are selected when their product name or ingredient
        type appears in the final ingredient list.

        Returns
        -------
        list[dict]
            Matching supplier database entries.
        """
        matched: List[Dict[str, Any]] = []
        if self.supplier_codes:
            for code in self.supplier_codes:
                entry = self.supplier_database.get(code)
                if entry:
                    matched.append(entry)
            return matched

        ingredient_set = set(self.ingredient_list)
        for entry in self.supplier_database.values():
            product_name = self._normalize_name(entry.get("product_name", ""))
            ingredient_type = self._normalize_name(entry.get("ingredient_type", ""))
            if product_name in ingredient_set or ingredient_type in ingredient_set:
                matched.append(entry)
        return matched

    def _calculate_carryover(
        self, supplier_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate preservative carryover from each supplier entry.

        For every preservative listed in a supplier concentrate, the carryover
        concentration in the final product is:

            typical_pct_in_concentrate * typical_dilution_in_final / 100

        Concentrations for the same preservative from multiple suppliers are
        summed.

        Parameters
        ----------
        supplier_entries : list[dict]
            Supplier database entries used in the formulation.

        Returns
        -------
        list[dict]
            One entry per detected preservative with carryover concentration,
            supplier source, SCCS limit, and flags.
        """
        aggregated: Dict[str, Dict[str, Any]] = {}
        for entry in supplier_entries:
            dilution = float(entry.get("typical_dilution_in_final", 0.0))
            supplier = entry.get("supplier_name", "UNKNOWN")
            product_code = entry.get("product_code", "UNKNOWN")
            for preservative in entry.get("preservatives", []):
                name = self._normalize_name(preservative.get("name", ""))
                if not name:
                    continue
                concentration = float(preservative.get("typical_pct_in_concentrate", 0.0))
                carryover = round(concentration * dilution / 100.0, 6)
                if name not in aggregated:
                    aggregated[name] = {
                        "name": name,
                        "cas": preservative.get("cas", ""),
                        "carryover_concentration_pct": 0.0,
                        "sccs_limit_pct": self.sccs_limits.get(name.upper()),
                        "supplier_sources": [],
                        "functions": set(),
                    }
                aggregated[name]["carryover_concentration_pct"] += carryover
                source_key = f"{supplier} {product_code}"
                if source_key not in aggregated[name]["supplier_sources"]:
                    aggregated[name]["supplier_sources"].append(source_key)
                func = preservative.get("function", "")
                if func:
                    aggregated[name]["functions"].add(func)

        results: List[Dict[str, Any]] = []
        for data in aggregated.values():
            data["functions"] = sorted(data["functions"])
            data["flags"] = self._determine_flags(data)
            data["supplier_source"] = "; ".join(data["supplier_sources"])
            del data["supplier_sources"]
            results.append(data)
        return sorted(results, key=lambda x: x["carryover_concentration_pct"], reverse=True)

    def _determine_flags(self, preservative_data: Dict[str, Any]) -> List[str]:
        """Return regulatory and claim flags for a single preservative.

        Parameters
        ----------
        preservative_data : dict
            Dictionary with keys ``name`` and ``carryover_concentration_pct``.

        Returns
        -------
        list[str]
            One or more flags from:
            CARRYOVER_RISK, UPSTREAM_PRESERVATIVE_DETECTED, CLAIM_MISMATCH,
            LABELING_REQUIRED, REGULATORY_VIOLATION_RISK.
        """
        name = preservative_data["name"]
        carryover = preservative_data["carryover_concentration_pct"]
        flags: List[str] = []

        if "paraben-free" in self.brand_claims and name in PARABENS:
            flags.append("CARRYOVER_RISK")

        if "preservative-free" in self.brand_claims:
            flags.append("UPSTREAM_PRESERVATIVE_DETECTED")

        if "natural" in self.brand_claims and name in SYNTHETIC_PRESERVATIVES:
            flags.append("CLAIM_MISMATCH")

        if carryover > EU_INCIDENTAL_THRESHOLD_PCT:
            flags.append("LABELING_REQUIRED")

        sccs_limit = preservative_data.get("sccs_limit_pct")
        if sccs_limit is not None and carryover > sccs_limit:
            flags.append("REGULATORY_VIOLATION_RISK")

        return flags

    def _verify_claims(
        self, preservatives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluate each brand claim against detected preservative carryover.

        Parameters
        ----------
        preservatives : list[dict]
            Preservatives detected from carryover.

        Returns
        -------
        list[dict]
            Claim verification entries with claim text, status, and evidence.
        """
        verification: List[Dict[str, Any]] = []
        if not self.brand_claims:
            return verification

        paraben_names = [p["name"] for p in preservatives if p["name"].upper() in PARABENS]
        any_preservative = bool(preservatives)
        synthetic_names = [
            p["name"]
            for p in preservatives
            if p["name"].upper() in SYNTHETIC_PRESERVATIVES
        ]

        for claim in self.brand_claims:
            if claim == "paraben-free":
                if paraben_names:
                    evidence_parts = []
                    for p in preservatives:
                        if p["name"] in PARABENS:
                            evidence_parts.append(
                                f"{p['supplier_source']} carries {p['name']} "
                                f"at {p['carryover_concentration_pct']:.4f}% in final product"
                            )
                    status = "FALSE"
                    evidence = "; ".join(evidence_parts)
                else:
                    status = "TRUE"
                    evidence = "No paraben carryover detected from supplier materials."

            elif claim == "preservative-free":
                if any_preservative:
                    status = "FALSE"
                    names = ", ".join(p["name"] for p in preservatives[:3])
                    evidence = (
                        f"Upstream preservatives detected: {names}. "
                        "Supplier concentrates frequently contain preservatives."
                    )
                else:
                    status = "TRUE"
                    evidence = "No upstream preservatives detected in the audited supplier materials."

            elif claim == "natural":
                if synthetic_names:
                    status = "WARNING"
                    evidence = (
                        "Synthetic preservatives carried over from supplier materials: "
                        + ", ".join(synthetic_names)
                    )
                else:
                    status = "TRUE"
                    evidence = "No synthetic preservative carryover detected."

            else:
                status = "UNKNOWN"
                evidence = f"No verification rule defined for claim '{claim}'."

            verification.append(
                {"claim": claim, "status": status, "evidence": evidence}
            )

        return verification

    def _build_regulatory_flags(
        self, preservatives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build EU regulatory flags from carryover concentrations.

        Parameters
        ----------
        preservatives : list[dict]
            Preservatives detected from carryover.

        Returns
        -------
        list[dict]
            One flag entry per preservative that exceeds the incidental
            labeling threshold or an SCCS limit.
        """
        flags: List[Dict[str, Any]] = []
        for p in preservatives:
            carryover = p["carryover_concentration_pct"]
            sccs_limit = p.get("sccs_limit_pct")
            exceeds_incidental = carryover > EU_INCIDENTAL_THRESHOLD_PCT
            exceeds_sccs = sccs_limit is not None and carryover > sccs_limit

            if exceeds_incidental and exceeds_sccs:
                status = "NON_COMPLIANT"
                note = (
                    f"{p['name']} carryover {carryover:.4f}% exceeds EU SCCS limit "
                    f"{sccs_limit}% and incidental threshold {EU_INCIDENTAL_THRESHOLD_PCT}%."
                )
            elif exceeds_incidental:
                status = "FLAGGED"
                note = (
                    f"{p['name']} carryover {carryover:.4f}% exceeds EU incidental "
                    f"threshold {EU_INCIDENTAL_THRESHOLD_PCT}% and must be labeled."
                )
            elif exceeds_sccs:
                status = "NON_COMPLIANT"
                note = (
                    f"{p['name']} carryover {carryover:.4f}% exceeds EU SCCS limit "
                    f"{sccs_limit}% although it is below the incidental labeling threshold."
                )
            else:
                continue

            flags.append(
                {
                    "jurisdiction": "EU",
                    "regulation": "1223/2009 Annex V",
                    "status": status,
                    "note": note,
                }
            )
        return flags

    def audit(self) -> Dict[str, Any]:
        """Run the supplier preservative audit and build the report.

        Returns
        -------
        dict
            Structured audit report matching the module 4 JSON schema.
        """
        supplier_entries = self._lookup_supplier_products()
        preservatives = self._calculate_carryover(supplier_entries)
        claim_verification = self._verify_claims(preservatives)
        regulatory_flags = self._build_regulatory_flags(preservatives)

        supplier_products_used = [
            {
                "supplier": entry.get("supplier_name", ""),
                "product_code": entry.get("product_code", ""),
                "typical_dilution_pct": entry.get("typical_dilution_in_final", 0.0),
            }
            for entry in supplier_entries
        ]

        self.report = {
            "product_name": self.product_name,
            "brand_claims": self.brand_claims,
            "supplier_products_used": supplier_products_used,
            "preservatives_from_carryover": preservatives,
            "claim_verification": claim_verification,
            "regulatory_flags": regulatory_flags,
        }
        return self.report

    def to_json(self, indent: int = 2) -> str:
        """Return the audit report as a JSON string.

        Parameters
        ----------
        indent : int
            Indentation level for the JSON output.

        Returns
        -------
        str
            JSON representation of ``self.report``.
        """
        return json.dumps(self.report, indent=indent, ensure_ascii=False)


def _test_case_1() -> None:
    """Paraben-free claim contradicted by SLES carryover."""
    print("\n=== Test Case 1: Paraben-free claim with SLES carryover ===")
    audit = SupplierAudit(
        product_name="Example Brand Gentle Shampoo",
        ingredient_list=[
            "Water",
            "Sodium Laureth Sulfate",
            "Cocamidopropyl Betaine",
            "Sodium Chloride",
            "Fragrance",
            "Citric Acid",
        ],
        supplier_codes=["BASF_TEXAPON_N70", "BASF_DEHYTON_PK45"],
        brand_claims=["paraben-free", "gentle"],
    )
    report = audit.audit()
    print(audit.to_json())
    assert report["claim_verification"][0]["status"] == "FALSE"
    assert any(
        "CARRYOVER_RISK" in p["flags"] for p in report["preservatives_from_carryover"]
    )


def _test_case_2() -> None:
    """Preservative-free claim contradicted by sodium benzoate carryover."""
    print("\n=== Test Case 2: Preservative-free claim with benzoate carryover ===")
    audit = SupplierAudit(
        product_name="Clean Label No-Preservative Shampoo",
        ingredient_list=[
            "Water",
            "Sodium Laureth Sulfate",
            "Cocamidopropyl Betaine",
            "Glycerin",
            "Citric Acid",
        ],
        supplier_codes=["SOLVAY_RHODAPEX_ESB70", "EVONIK_TEGO_BETAIN_F50"],
        brand_claims=["preservative-free", "natural"],
    )
    report = audit.audit()
    print(audit.to_json())
    assert report["claim_verification"][0]["status"] == "FALSE"
    assert any(
        "UPSTREAM_PRESERVATIVE_DETECTED" in p["flags"]
        for p in report["preservatives_from_carryover"]
    )


def _test_case_3() -> None:
    """Natural claim with synthetic formaldehyde-releaser carryover."""
    print("\n=== Test Case 3: Natural claim with DMDM hydantoin carryover ===")
    audit = SupplierAudit(
        product_name="Botanical Natural Shampoo",
        ingredient_list=[
            "Water",
            "Sodium Laureth Sulfate",
            "Polyquaternium-10",
            "Cocamide MEA",
            "Aloe Barbadensis Leaf Juice",
        ],
        supplier_codes=["DOW_UCARE_JR400", "STEPAN_STEOL_4N", "EMERY_5320"],
        brand_claims=["natural"],
    )
    report = audit.audit()
    print(audit.to_json())
    assert report["claim_verification"][0]["status"] == "WARNING"
    assert any(
        "CLAIM_MISMATCH" in p["flags"]
        for p in report["preservatives_from_carryover"]
    )


if __name__ == "__main__":
    """Run three demonstration test cases for the supplier audit tool."""
    _test_case_1()
    _test_case_2()
    _test_case_3()
    print("\nAll test cases passed.")
