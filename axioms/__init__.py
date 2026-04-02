"""axioms package — Foundational Axiom Layer"""
from axioms.peano import ZERO, peano_add, peano_mul, successor, predecessor, PeanoNat, PeanoProof
from axioms.logic import ProofObject, modus_ponens, universal_instantiation, induction_rule, merkle_root_over_proofs
from axioms.yeshua_axioms import YeshuaClaim, YeshuaViolation, verify_yeshua_standard, YESHUA_AXIOMS
from axioms.peano_extended import *
from axioms.number_theory import *
from axioms.combinatorics import *
from axioms.game_theory import *
from axioms.epistemic_logic import *
from axioms.computability import *
from axioms.pattern_recognition import *
