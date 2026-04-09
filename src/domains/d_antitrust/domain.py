"""D_ANTITRUST domain definition — Antitrust / Competition

Layer: 2
CardinalStrength: PREDICATIVE

Antitrust law promotes fair competition and prevents monopolistic practices.
Sherman Act (1890), Clayton Act (1914), and FTC Act (1914) form the US antitrust framework.
Merger review uses HHI (Herfindahl-Hirschman Index) to assess market concentration.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ANTITRUST"
DOMAIN_NAME = "Antitrust / Competition"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'sherman-act',
    'clayton-act',
    'ftc-act',
    'price-fixing',
    'bid-rigging',
    'market-allocation',
    'monopolization',
    'attempted-monopolization',
    'merger-review',
    'hhi',
    'market-definition',
    'relevant-market',
    'entry-barriers',
    'efficiencies',
    'consumer-welfare',
    'predatory-pricing',
    'tying',
    'exclusive-dealing',
    'resale-price-maintenance',
    'robinson-patman',
    'vertical-restraints',
    'horizontal-restraints',
]

INVARIANTS = [
    'Price-fixing is per se illegal regardless of market power (Sherman Act § 1).',
    'Bid-rigging among competitors violates Sherman Act § 1 per se.',
    'Market allocation agreements (geographic/customer) are per se illegal.',
    'Monopolization requires (1) monopoly power and (2) exclusionary conduct (Sherman Act § 2).',
    'Merger review threshold: HHI >1800 is concentrated, >2500 is highly concentrated (DOJ/FTC).',
    'HHI calculation is reproducible: HHI = Σ(market_share_i)^2 for all firms.',
    'Relevant market definition includes product market and geographic market.',
    'Entry barriers analysis determines whether new competition is likely within 2 years.',
    'Efficiencies defense requires merger-specific, cognizable, and verifiable benefits.',
    'Consumer welfare standard: anticompetitive if harms consumers via higher prices or reduced output.',
    'Predatory pricing requires prices below cost plus recoupment likelihood (Brooke Group).',
    'Tying arrangements illegal if seller has market power in tying product (Clayton Act § 3).',
    'Exclusive dealing illegal if substantial foreclosure of competition (Tampa Electric).',
    'Resale price maintenance evaluated under rule of reason (Leegin).',
    'Robinson-Patman Act prohibits price discrimination harming competition (15 U.S.C. § 13).',
]

FALSIFICATION_TESTS = ["F_ANTITRUST_001"]
ONTOLOGICAL_ISSUES = ["OI_ANTITRUST_001"]
