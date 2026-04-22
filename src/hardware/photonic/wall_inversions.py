"""src/hardware/photonic/wall_inversions — Photonic Wall Inversion Registry.

Maps each logical wall (impossibility theorem) to its Yeshua Inversion:
the domain restriction or architectural mechanism that changes the problem
so the theorem's preconditions no longer apply.

Each entry includes:
  - theorem_reference: formal citation
  - sal_module: SAL kernel module that implements the inversion
  - inversion_mechanism: precise description of the domain restriction
  - proof: ProofObject certifying the inversion is structurally valid

Standard: Yeshua Standard — every claim has a ProofObject and a falsifies_if.

falsifies_if: a wall_id appears in the registry without a valid ProofObject.
"""

from typing import Dict

from investigations.wall_inversions import WallInversion, _make_proof


PHOTONIC_WALL_INVERSIONS: Dict[str, WallInversion] = {
    "WALL_PHOTON_001": WallInversion(
        wall_id="WALL_PHOTON_001",
        theorem_name="Landauer's Principle",
        theorem_reference=(
            "Landauer (1961). 'Irreversibility and Heat Generation in the Computing Process.' "
            "IBM J. Res. Dev. 5(3):183-191."
        ),
        sal_module="src/hardware/photonic/implementation.py",
        inversion_mechanism=(
            "Restrict photonic computation to unitary (reversible) operations. "
            "Landauer's bound applies only to irreversible bit erasure. MZI mesh implements "
            "unitary matrix multiplication — no bits are erased, no thermodynamic floor applies. "
            "The computation is reversible by design."
        ),
        falsifies_if=(
            "A photonic gate performs irreversible bit erasure without dissipating "
            ">= k_B * T * ln(2) joules."
        ),
        proof=_make_proof(
            "WALL_PHOTON_001",
            "Landauer's Principle",
            "Restrict photonic computation to unitary (reversible) operations",
        ),
    ),
    "WALL_PHOTON_002": WallInversion(
        wall_id="WALL_PHOTON_002",
        theorem_name="Cavity Lifetime Limit",
        theorem_reference=(
            "Vahala (2003). 'Optical Microcavities.' Nature 424:839-846."
        ),
        sal_module="src/hardware/photonic/implementation.py",
        inversion_mechanism=(
            "Use flow-through (non-resonant) waveguide architecture instead of cavity-based "
            "processing. Cavity Q-factor limits apply only to resonant structures. MZI mesh "
            "routes photons through directional couplers — no cavity, no lifetime limit, "
            "no Q-factor constraint."
        ),
        falsifies_if=(
            "A flow-through MZI element exhibits cavity-lifetime-dependent signal degradation."
        ),
        proof=_make_proof(
            "WALL_PHOTON_002",
            "Cavity Lifetime Limit",
            "Use flow-through (non-resonant) waveguide architecture",
        ),
    ),
    "WALL_PHOTON_003": WallInversion(
        wall_id="WALL_PHOTON_003",
        theorem_name="Joule Heating (Ohm's Law)",
        theorem_reference=(
            "Joule (1841). 'On the Production of Heat by Voltaic Electricity.' "
            "Proc. Royal Soc. London."
        ),
        sal_module="src/hardware/photonic/implementation.py",
        inversion_mechanism=(
            "Photons carry zero electric charge. Joule heating (P = I²R) requires current flow "
            "through resistance. Photonic waveguides propagate electromagnetic modes — no charge "
            "carriers, no resistance, no I²R dissipation. Thermal tuning uses separate heaters, "
            "not the optical path."
        ),
        falsifies_if=(
            "Photon propagation through a lossless dielectric waveguide generates I²R heating."
        ),
        proof=_make_proof(
            "WALL_PHOTON_003",
            "Joule Heating (Ohm's Law)",
            "Photons carry zero electric charge — no I²R dissipation",
        ),
    ),
    "WALL_PHOTON_004": WallInversion(
        wall_id="WALL_PHOTON_004",
        theorem_name="RC Delay Limit",
        theorem_reference=(
            "Horowitz & Hill (2015). 'The Art of Electronics.' 3rd ed. "
            "Cambridge University Press. §1.4."
        ),
        sal_module="src/hardware/photonic/implementation.py",
        inversion_mechanism=(
            "Wavelength-division multiplexing (WDM) replaces electronic interconnect. RC delay = "
            "R × C applies to copper traces charging parasitic capacitance. Photonic links have "
            "no resistance and no capacitance — propagation delay is n/c (refractive index / speed "
            "of light), independent of data rate. WDM multiplies bandwidth by channel count with "
            "zero additional RC."
        ),
        falsifies_if=(
            "A photonic waveguide exhibits bandwidth degradation proportional to R × C."
        ),
        proof=_make_proof(
            "WALL_PHOTON_004",
            "RC Delay Limit",
            "WDM replaces electronic interconnect — no R, no C",
        ),
    ),
    "WALL_PHOTON_005": WallInversion(
        wall_id="WALL_PHOTON_005",
        theorem_name="Shot Noise Floor",
        theorem_reference=(
            "Schottky (1918). 'Über spontane Stromschwankungen in verschiedenen "
            "Elektrizitätsleitern.' Annalen der Physik 362(23):541-567."
        ),
        sal_module="src/hardware/photonic/implementation.py",
        inversion_mechanism=(
            "Squeezed-state light preparation reduces noise below the standard quantum limit in "
            "one quadrature. Shot noise floor assumes coherent-state (Poissonian) photon statistics. "
            "Squeezed states have sub-Poissonian statistics in the measurement quadrature, pushing "
            "noise below the shot noise floor at the cost of increased noise in the conjugate "
            "quadrature (Heisenberg-compliant)."
        ),
        falsifies_if=(
            "A squeezed-state measurement violates the Heisenberg uncertainty relation "
            "(product of quadrature uncertainties < hbar/2)."
        ),
        proof=_make_proof(
            "WALL_PHOTON_005",
            "Shot Noise Floor",
            "Squeezed-state light reduces noise below SQL",
        ),
    ),
}
