"""D_AGRICULTURE domain definition — Agriculture

Layer: 3
CardinalStrength: PREDICATIVE

Agriculture encompasses crop production, livestock, precision farming, and sustainability.
Precision agriculture uses sensors, GPS, and data analytics for optimized resource use.
Soil health, water management, and yield prediction are critical domains.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AGRICULTURE"
DOMAIN_NAME = "Agriculture"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'precision-ag',
    'crop-science',
    'soil-health',
    'irrigation',
    'fertilization',
    'pest-management',
    'yield-prediction',
    'GPS-guidance',
    'variable-rate-application',
    'remote-sensing',
    'NDVI',
    'soil-moisture',
    'pH-monitoring',
    'nutrient-management',
    'crop-rotation',
    'cover-crops',
    'no-till',
    'organic-farming',
    'livestock-monitoring',
    'feed-optimization',
    'disease-detection',
    'weather-forecasting',
    'harvest-optimization',
]

INVARIANTS = [
    'Crop yield estimates within confidence interval (±5% for major grains with full-season data).',
    'Soil nutrient levels (N, P, K) meet crop-specific thresholds.',
    'Irrigation scheduling minimizes water use while maintaining yield (deficit irrigation constraints).',
    'Variable-rate fertilizer application matches soil test zones with <10m spatial resolution.',
    'NDVI (Normalized Difference Vegetation Index) correlates with biomass within calibrated range.',
    'Soil moisture sensors report values within ±2% volumetric water content accuracy.',
    'pH measurements accurate to ±0.1 pH units for precision liming.',
    'Pest detection models have <10% false negative rate for economically damaging thresholds.',
    'Crop rotation sequences maintain soil organic matter and break disease cycles.',
    'Cover crop termination timing optimized for nitrogen release synchronization.',
    'GPS guidance accuracy <2cm RTK for controlled traffic farming.',
    'Remote sensing data georeferenced with <5m absolute accuracy.',
    'Livestock health monitoring detects anomalies within 24 hours of symptom onset.',
    'Feed ration formulation meets nutritional requirements within ±5% of target.',
    'Weather forecast integration updates field operations with <6-hour lead time.',
]

FALSIFICATION_TESTS = ["F_AGRICULTURE_001"]
ONTOLOGICAL_ISSUES = ["OI_AGRICULTURE_001"]
