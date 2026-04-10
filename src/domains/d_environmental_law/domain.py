"""D_ENVIRONMENTAL_LAW domain definition — Environmental Law

Layer: 2
CardinalStrength: PREDICATIVE

Environmental law regulates pollution, natural resource use, and ecosystem protection.
Clean Air Act (CAA), Clean Water Act (CWA), and NEPA (National Environmental Policy Act) are foundational.
Polluter pays principle assigns cleanup costs to responsible parties.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ENVIRONMENTAL_LAW"
DOMAIN_NAME = "Environmental Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'clean-air-act',
    'clean-water-act',
    'nepa',
    'eis',
    'polluter-pays',
    'cercla',
    'superfund',
    'rcra',
    'endangered-species-act',
    'wetlands-protection',
    'npdes',
    'air-quality-standards',
    'water-quality-standards',
    'emissions-trading',
    'carbon-cap',
    'environmental-justice',
    'toxic-substances',
    'hazardous-waste',
    'brownfield-redevelopment',
    'remediation',
    'natural-resource-damages',
    'public-trust-doctrine',
]

INVARIANTS = [
    'Emission limits are deterministic given source type and pollutant (CAA NAAQS standards).',
    'Environmental Impact Statement (EIS) required before major federal action significantly affecting environment (NEPA § 102).',
    'Polluter pays principle: cost of cleanup borne by responsible party (CERCLA § 107).',
    'Clean Water Act: point source discharges require NPDES permit (33 U.S.C. § 1342).',
    'NAAQS (National Ambient Air Quality Standards): primary standards protect public health with adequate margin of safety.',
    'Water quality standards: designated uses (drinking, swimming, fishing) with numeric criteria.',
    'Emissions trading: cap-and-trade systems allow market-based compliance (e.g., SO2 allowances).',
    'Endangered Species Act: no federal action may jeopardize listed species or critical habitat (ESA § 7).',
    'Wetlands protection: Clean Water Act § 404 permit required for dredge/fill in jurisdictional waters.',
    'RCRA (Resource Conservation and Recovery Act): hazardous waste cradle-to-grave tracking (40 CFR 262-265).',
    'Superfund (CERCLA): National Priorities List sites remediated with strict, joint, and several liability.',
    'Toxic Substances Control Act (TSCA): pre-manufacture notification (PMN) for new chemicals.',
    'Environmental justice: disproportionate impacts on minority/low-income communities prohibited (EO 12898).',
    'Brownfield redevelopment: liability protection for bona fide prospective purchasers (Small Business Liability Relief Act).',
    'Natural resource damages: trustees recover costs for injury to natural resources (CERCLA § 107, OPA § 1006).',
]

FALSIFICATION_TESTS = ["F_ENVIRONMENTAL_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_ENVIRONMENTAL_LAW_001"]
