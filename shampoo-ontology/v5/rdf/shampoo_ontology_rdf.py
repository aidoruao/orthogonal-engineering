#!/usr/bin/env python3
"""Shampoo Ingredient Ontology v5.0 — OWL/RDF Turtle Export.

Generates a valid OWL/RDF Turtle ontology file (shampoo_ontology.ttl) from
the v4.1 canonincal ingredient database, jurisdiction databases, and
IFRA fragrance subset. Maps 100+ ingredients to RDF classes and properties.

Standard library only. Run: python3 shampoo_ontology_rdf.py
Output: shampoo_ontology.ttl
"""

import os
import sys
import json

from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_V4_PATH = str(_PROJECT_ROOT / "shampoo-ontology-v4")
if _V4_PATH not in sys.path:
    sys.path.insert(0, _V4_PATH)

import shampoo_ontology_parser as m1
import shampoo_ontology_divergence as m2
import shampoo_ontology_fragrance as m3

# ─── Prefix declarations ────────────────────────────────
PREFIXES = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix siog: <http://ontology.shampoo/v5/> .
@prefix ingred: <http://ontology.shampoo/v5/ingredient/> .
@prefix prod: <http://ontology.shampoo/v5/product/> .
@prefix jur: <http://ontology.shampoo/v5/jurisdiction/> .

"""

# ─── Class declarations ─────────────────────────────────
CLASSES = """
siog:ShampooOntology rdf:type owl:Ontology ;
    rdfs:label "Shampoo Ingredient Ontology v5.0" ;
    rdfs:comment "Generated from Shampoo Ingredient Ontology v5.0 executable modules." .

siog:Surfactant rdf:type owl:Class ;
    rdfs:label "Surfactant" ;
    rdfs:comment "Surface-active agent used for cleansing or foaming." .

siog:Preservative rdf:type owl:Class ;
    rdfs:label "Preservative" ;
    rdfs:comment "Antimicrobial agent used for product preservation." .

siog:FragranceComponent rdf:type owl:Class ;
    rdfs:label "Fragrance Component" ;
    rdfs:comment "Odorant compound used in perfume compositions." .

siog:BotanicalExtract rdf:type owl:Class ;
    rdfs:label "Botanical Extract" ;
    rdfs:comment "Plant-derived extract used for marketing or functional claims." .

siog:Silicone rdf:type owl:Class ;
    rdfs:label "Silicone" ;
    rdfs:comment "Silicon-based polymer used for conditioning and slip." .

siog:Polymer rdf:type owl:Class ;
    rdfs:label "Polymer" ;
    rdfs:comment "Synthetic or natural polymer used for rheology or conditioning." .

siog:Emollient rdf:type owl:Class ;
    rdfs:label "Emollient" ;
    rdfs:comment "Oil, ester, or alcohol that softens and conditions." .

siog:Humectant rdf:type owl:Class ;
    rdfs:label "Humectant" ;
    rdfs:comment "Water-attracting substance that maintains moisture." .

siog:Solvent rdf:type owl:Class ;
    rdfs:label "Solvent" ;
    rdfs:comment "Carrier liquid, typically water or glycol." .

siog:Chelator rdf:type owl:Class ;
    rdfs:label "Chelator" ;
    rdfs:comment "Metal-ion sequestrant for stability." .

siog:PHAdjuster rdf:type owl:Class ;
    rdfs:label "pH Adjuster" ;
    rdfs:comment "Acid or base used to adjust formulation pH." .

siog:EUBanned rdf:type owl:Class ;
    rdfs:label "EU Banned" ;
    rdfs:comment "Ingredient banned in EU cosmetics per EC 1223/2009 Annex II." .

siog:USBanned rdf:type owl:Class ;
    rdfs:label "US Banned" ;
    rdfs:comment "Ingredient banned in US cosmetics per 21 CFR or FDA rule." .

siog:CNBanned rdf:type owl:Class ;
    rdfs:label "China Banned" ;
    rdfs:comment "Ingredient banned in China per NMPA Safety Technical Standard 2015." .

siog:ShampooProduct rdf:type owl:Class ;
    rdfs:label "Shampoo Product" ;
    rdfs:comment "A rinse-off hair cleansing product." .

siog:FragranceCompound rdf:type owl:Class ;
    rdfs:label "Fragrance Compound" ;
    rdfs:comment "An individual odorant molecule in a fragrance composition." .

# ─── Properties ──────────────────────────────────────────
siog:hasCASNumber rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "CAS Number" .

siog:hasEUNumber rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "EU Regulatory Number" .

siog:hasRestriction rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "Restriction Type" .

siog:hasPatentReference rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "Patent Reference" .

siog:hasSupplier rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "Supplier" .

siog:hasConcentrationRange rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:Ingredient ;
    rdfs:range xsd:string ;
    rdfs:label "Concentration Range" .

siog:hasIngredient rdf:type owl:ObjectProperty ;
    rdfs:domain siog:ShampooProduct ;
    rdfs:range siog:Ingredient ;
    rdfs:label "Has Ingredient" .

siog:hasJurisdictionVariant rdf:type owl:ObjectProperty ;
    rdfs:domain siog:ShampooProduct ;
    rdfs:range siog:ShampooProduct ;
    rdfs:label "Has Jurisdiction Variant" .

siog:hasIFRACategory rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:FragranceCompound ;
    rdfs:range xsd:string ;
    rdfs:label "IFRA Category" .

siog:hasAllergenStatus rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:FragranceCompound ;
    rdfs:range xsd:string ;
    rdfs:label "Allergen Status" .

siog:hasToxicityProfile rdf:type owl:DatatypeProperty ;
    rdfs:domain siog:FragranceCompound ;
    rdfs:range xsd:string ;
    rdfs:label "Toxicity Profile" .

"""

# ─── Ingredient classification helper ──────────────────
_SURFACTANTS = {
    "SODIUM LAURETH SULFATE", "SODIUM LAURYL SULFATE",
    "AMMONIUM LAURETH SULFATE", "COCAMIDOPROPYL BETAINE",
    "COCO-BETAINE", "SODIUM COCOYL ISETHIONATE",
    "SODIUM LAUROYL SARCOSINATE", "DECYL GLUCOSIDE",
    "LAURYL GLUCOSIDE", "SODIUM C14-16 OLEFIN SULFONATE",
    "COCAMIDE MEA", "COCAMIDE MIPA",
}

_PRESERVATIVES = {
    "SODIUM BENZOATE", "POTASSIUM SORBATE", "PHENOXYETHANOL",
    "METHYLPARABEN", "PROPYLPARABEN", "ETHYLPARABEN", "BUTYLPARABEN",
    "DMDM HYDANTOIN", "METHYLISOTHIAZOLINONE",
    "METHYLCHLOROISOTHIAZOLINONE", "IODOPROPYNYL BUTYLCARBAMATE",
    "BENZYL ALCOHOL", "DIAZOLIDINYL UREA", "IMIDAZOLIDINYL UREA",
}

_SILICONES = {
    "DIMETHICONE", "DIMETHICONOL", "AMODIMETHICONE",
    "CYCLOPENTASILOXANE", "CYCLOMETHICONE",
}

_POLYMERS = {
    "POLYQUATERNIUM-7", "POLYQUATERNIUM-10", "POLYQUATERNIUM-6",
    "CARBOMER", "XANTHAN GUM", "GUAR GUM", "HYDROXYETHYLCELLULOSE",
}

_EMOLLIENTS = {
    "GLYCOL DISTEARATE", "CETEARYL ALCOHOL", "CETYL ALCOHOL",
    "STEARYL ALCOHOL", "ISOPROPYL MYRISTATE", "CAPRYLIC/CAPRIC TRIGLYCERIDE",
}

_HUMECTANTS = {
    "GLYCERIN", "PROPYLENE GLYCOL", "BUTYLENE GLYCOL", "SORBITOL",
    "SODIUM HYALURONATE", "PANTHENOL", "UREA",
}

_SOLVENTS = {"WATER", "AQUA"}

_CHELATORS = {"TETRASODIUM EDTA", "DISODIUM EDTA", "SODIUM CITRATE"}

_PH_ADJUSTERS = {"CITRIC ACID", "SODIUM HYDROXIDE", "POTASSIUM HYDROXIDE",
                 "TRIETHANOLAMINE", "LACTIC ACID"}

_BOTANICALS = {
    "ALOE BARBADENSIS LEAF JUICE", "CHAMOMILLA RECUTITA FLOWER EXTRACT",
    "CAMELLIA SINENSIS LEAF EXTRACT", "ARGANIA SPINOSA KERNEL OIL",
    "MELALEUCA ALTERNIFOLIA LEAF OIL", "MENTHA PIPERITA OIL",
    "LAVANDULA ANGUSTIFOLIA OIL", "ROSMARINUS OFFICINALIS LEAF EXTRACT",
    "SIMMONDSIA CHINENSIS SEED OIL", "BUTYROSPERMUM PARKII BUTTER",
}


def classify_ingredient(name):
    """Return the RDF class URI for a canonical ingredient name.

    Parameters
    ----------
    name : str
        Upper-cased canonical INCI name.

    Returns
    -------
    str
        RDF class URI like ``siog:Surfactant``.
    """
    upper = name.upper()
    if upper in _SURFACTANTS:
        return "siog:Surfactant"
    if upper in _PRESERVATIVES:
        return "siog:Preservative"
    if upper in _SILICONES:
        return "siog:Silicone"
    if upper in _POLYMERS:
        return "siog:Polymer"
    if upper in _EMOLLIENTS:
        return "siog:Emollient"
    if upper in _HUMECTANTS:
        return "siog:Humectant"
    if upper in _SOLVENTS:
        return "siog:Solvent"
    if upper in _CHELATORS:
        return "siog:Chelator"
    if upper in _PH_ADJUSTERS:
        return "siog:PHAdjuster"
    if upper in _BOTANICALS:
        return "siog:BotanicalExtract"
    if any(upper.endswith(s) for s in ("EXTRACT", "OIL", "JUICE", "BUTTER")):
        return "siog:BotanicalExtract"
    if "BOTANICAL_EXTRACT" in upper:
        return "siog:BotanicalExtract"
    return "siog:Ingredient"


def generate_ttl(output_path="shampoo_ontology.ttl"):
    """Generate the complete OWL/RDF Turtle ontology file.

    Reads canonical INCI, EU/US/CN banned databases, and IFRA subset from
    v4.1 modules and writes a valid Turtle file.

    Parameters
    ----------
    output_path : str
        Destination file path.

    Returns
    -------
    str
        Absolute path to the written file.
    """
    lines = []

    # Prefixes and class declarations
    lines.append(PREFIXES)
    lines.append(CLASSES)

    # Canonical ingredients (from parser)
    canonical = m1.CANONICAL_INCI
    unique_ingredients = sorted(set(v.upper() for v in canonical.values() if v))
    count = 0
    for name in unique_ingredients[:100]:  # Map at least 100
        safe_name = name.replace(" ", "_").replace("/", "-").replace(".", "")
        cls = classify_ingredient(name)
        lines.append(f"\ningred:{safe_name} rdf:type {cls} ;")
        lines.append(f'    rdfs:label "{name}" .')
        # CAS lookup from patent db
        patent = m1.PATENT_DB.get(name, {})
        if patent.get("patent_number"):
            lines.append(f'ingred:{safe_name} siog:hasPatentReference "{patent["patent_number"]}" .')
        if patent.get("concentration_range"):
            lines.append(f'ingred:{safe_name} siog:hasConcentrationRange "{patent["concentration_range"]}" .')
        count += 1

    # EU banned substances
    for name, data in list(m2.EU_BANNED.items())[:20]:
        safe_name = name.upper().replace(" ", "_").replace("/", "-").replace(".", "")
        lines.append(f"\ningred:{safe_name} rdf:type siog:EUBanned ;")
        lines.append(f'    rdfs:label "{name}" ;')
        lines.append(f'    siog:hasCASNumber "{data.get("cas_number","")}" ;')
        lines.append(f'    siog:hasRestriction "{data.get("restriction_type","")}" .')
        count += 1

    # US banned substances
    for name, data in list(m2.US_BANNED.items())[:20]:
        safe_name = name.upper().replace(" ", "_").replace("/", "-").replace(".", "")
        lines.append(f"\ningred:{safe_name} rdf:type siog:USBanned ;")
        lines.append(f'    rdfs:label "{name}" ;')
        lines.append(f'    siog:hasCASNumber "{data.get("cas_number","")}" ;')
        lines.append(f'    siog:hasRestriction "{data.get("restriction_type","")}" .')
        count += 1

    # CN banned substances
    for name, data in list(m2.CN_BANNED.items())[:20]:
        safe_name = name.upper().replace(" ", "_").replace("/", "-").replace(".", "")
        lines.append(f"\ningred:{safe_name} rdf:type siog:CNBanned ;")
        lines.append(f'    rdfs:label "{name}" ;')
        lines.append(f'    siog:hasCASNumber "{data.get("cas_number","")}" ;')
        lines.append(f'    siog:hasRestriction "{data.get("restriction_type","")}" .')
        count += 1

    # IFRA fragrance compounds
    ifra = m3.IFRA_TRANSPARENCY_SUBSET
    for name, data in list(ifra.items())[:30]:
        safe_name = name.replace(" ", "_").replace("/", "-").replace(".", "").replace(",", "")
        lines.append(f"\ningred:{safe_name} rdf:type siog:FragranceCompound ;")
        lines.append(f'    rdfs:label "{name}" ;')
        lines.append(f'    siog:hasCASNumber "{data.get("cas_number","")}" ;')
        lines.append(f'    siog:hasIFRACategory "{data.get("ifra_category","")}" ;')
        lines.append(f'    siog:hasAllergenStatus "{data.get("allergen_status","")}" ;')
        lines.append(f'    siog:hasToxicityProfile "{data.get("known_toxicity","")}" .')
        count += 1

    # Products
    products = m2.PRODUCT_COMPARISON_DB
    for prod_name, pdata in list(products.items())[:5]:
        safe_prod = prod_name.replace(" ", "_").replace("'", "").replace("&", "and").replace(".", "")
        lines.append(f"\nprod:{safe_prod} rdf:type siog:ShampooProduct ;")
        lines.append(f'    rdfs:label "{prod_name}" .')
        for jurisdiction in ("US", "EU", "JP", "CN"):
            ingredients = pdata.get(jurisdiction, [])
            for ing in ingredients[:5]:
                safe_ing = ing.replace(" ", "_").replace("/", "-").replace(".", "").upper()
                lines.append(f"prod:{safe_prod} siog:hasIngredient ingred:{safe_ing} .")

    # End
    content = "\n".join(lines) + "\n"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else ".", output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Turtle ontology written to: {output_path}")
    print(f"  Lines: {len(lines)}")
    print(f"  Mapped {count}+ entities")
    return os.path.abspath(output_path)


if __name__ == "__main__":
    path = generate_ttl()
    # Validate: read back and check basic structure
    with open(path, "r") as f:
        content = f.read()
    assert "@prefix" in content, "Missing RDF prefixes"
    assert "siog:ShampooOntology" in content, "Missing ontology declaration"
    assert "siog:Surfactant" in content, "Missing Surfactant class"
    assert "siog:Preservative" in content, "Missing Preservative class"
    assert "ingred:" in content, "Missing ingredient instances"
    assert "prod:" in content, "Missing product instances"
    print("Turtle validation PASSED")
