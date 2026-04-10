"""D_ENERGY domain definition — Energy

Layer: 3
CardinalStrength: PREDICATIVE

Energy systems include power generation, transmission, distribution, and smart grids.
Demand response (DR) balances supply and demand to maintain grid stability.
Renewable energy integration requires forecasting and storage coordination.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ENERGY"
DOMAIN_NAME = "Energy"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'smart-grid',
    'demand-response',
    'renewable',
    'solar-PV',
    'wind-turbine',
    'battery-storage',
    'grid-frequency',
    'load-shedding',
    'SCADA',
    'PMU',
    'synchrophasor',
    'microgrid',
    'islanding',
    'power-quality',
    'harmonics',
    'voltage-regulation',
    'reactive-power',
    'transient-stability',
    'load-forecasting',
    'generation-dispatch',
    'energy-trading',
    'carbon-accounting',
]

INVARIANTS = [
    'Demand response (DR) events actioned within 30 seconds of signal receipt.',
    'Grid frequency deviation triggers load shedding at ±0.5 Hz from nominal (60 Hz or 50 Hz).',
    'Solar PV forecasting: day-ahead accuracy >80% for clear-sky conditions.',
    'Wind turbine power curve: actual output within ±5% of manufacturer curve for given wind speed.',
    'Battery storage: round-trip efficiency >85% for li-ion systems.',
    'SCADA (Supervisory Control and Data Acquisition): data latency <1 second for critical signals.',
    'Phasor Measurement Unit (PMU): synchrophasor measurements synchronized to <1 microsecond (GPS).',
    'Microgrid islanding: seamless transition to island mode within <100 ms of grid loss.',
    'Power quality: Total Harmonic Distortion (THD) <5% for voltage (IEEE 519).',
    'Voltage regulation: bus voltage maintained within ±5% of nominal under load variations.',
    'Reactive power: power factor >0.95 to minimize transmission losses.',
    'Transient stability: system remains stable under single-contingency faults (N-1 criterion).',
    'Load forecasting: mean absolute percentage error (MAPE) <3% for day-ahead forecasts.',
    'Generation dispatch: economic dispatch minimizes cost subject to constraints (linear programming).',
    'Carbon accounting: emissions calculated per kWh with fuel-specific coefficients (e.g., coal: 1 kg CO2/kWh).',
]

FALSIFICATION_TESTS = ["F_ENERGY_001"]
ONTOLOGICAL_ISSUES = ["OI_ENERGY_001"]
