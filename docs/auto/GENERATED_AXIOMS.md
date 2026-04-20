---
tags: [docs, auto, generated-axioms]
register: documentation
---

# Axiom Cross-Reference Index

**Total Axiom Modules:** 27
**Total Defined Types:** 69

## ⚠️ Unreferenced Axioms

- `__init__`
- `algebra`
- `arc_dsl`
- `arc_solver`
- `arc_types`
- `combinatorics`
- `complex_analysis`
- `computability`
- `cryptographic_verification`
- `epistemic_logic`
- `formal_languages`
- `game_theory`
- `measure_theory`
- `number_theory`
- `pattern_recognition`
- `peano`
- `peano_extended`
- `quantum_logic`
- `real_analysis`
- `synthetic_differential_geometry`
- `temporal_logic`
- `topology`
- `type_registry`
- `zero_knowledge`

## Axiom Modules

### __init__
- **File:** `axioms/__init__.py`
- **Types:** None
- **Theorems:** 0
- **Proofs:** 0

### algebra
- **File:** `axioms/algebra.py`
- **Types:** GroupOperation, GroupElement, Group, CyclicGroup, Ring, Ideal
- **Theorems:** 1
- **Proofs:** 0

### arc_dsl
- **File:** `axioms/arc_dsl.py`
- **Types:** BoundedDSL
- **Theorems:** 0
- **Proofs:** 0

### arc_solver
- **File:** `axioms/arc_solver.py`
- **Types:** ARCSolution, ARCBenchmarkResult, _Timeout
- **Theorems:** 0
- **Proofs:** 0

### arc_types
- **File:** `axioms/arc_types.py`
- **Types:** InteractionType, Interaction, GoalHypothesis, ARCTask, Program, ConceptLibrary
- **Theorems:** 0
- **Proofs:** 1

### category_theory
- **File:** `axioms/category_theory.py`
- **Types:** Object, Morphism, Category, Functor, NaturalTransformation, RepresentableFunctor, Diagram, Monad, DomainCategory
- **Theorems:** 0
- **Proofs:** 0
- **Referenced in:**
  - `src/sal/yoneda_embedding.py`

### combinatorics
- **File:** `axioms/combinatorics.py`
- **Types:** None
- **Theorems:** 0
- **Proofs:** 0

### complex_analysis
- **File:** `axioms/complex_analysis.py`
- **Types:** ComplexFraction
- **Theorems:** 1
- **Proofs:** 0

### computability
- **File:** `axioms/computability.py`
- **Types:** GoedelianReflector
- **Theorems:** 1
- **Proofs:** 4

### cryptographic_verification
- **File:** `axioms/cryptographic_verification.py`
- **Types:** HashChainLink, MerkleNode
- **Theorems:** 0
- **Proofs:** 0

### epistemic_logic
- **File:** `axioms/epistemic_logic.py`
- **Types:** KripkeModel, ModalOperator, ModalFormula, ParaconsistentTruthValue
- **Theorems:** 0
- **Proofs:** 0

### formal_languages
- **File:** `axioms/formal_languages.py`
- **Types:** Symbol, Alphabet, DFA, NFA, PDA, TuringMachine
- **Theorems:** 0
- **Proofs:** 0

### game_theory
- **File:** `axioms/game_theory.py`
- **Types:** StrategyProfile, ProofObligation, Theorem
- **Theorems:** 0
- **Proofs:** 2

### logic
- **File:** `axioms/logic.py`
- **Types:** ProofObject
- **Theorems:** 0
- **Proofs:** 1
- **Referenced in:**
  - `src/sal/adjoint_triple.py`
  - `src/sal/forcing_operation.py`
  - `src/sal/higher_adjunction.py`
  - `src/sal/self_referential.py`
  - `src/sal/topos_subobject_classifier.py`

### measure_theory
- **File:** `axioms/measure_theory.py`
- **Types:** SigmaAlgebra, Measure, ProbabilitySpace
- **Theorems:** 1
- **Proofs:** 0

### number_theory
- **File:** `axioms/number_theory.py`
- **Types:** None
- **Theorems:** 2
- **Proofs:** 0

### pattern_recognition
- **File:** `axioms/pattern_recognition.py`
- **Types:** PrimitiveOperation, Grid, CompositionalRule, ObjectComponent, KolmogorovComplexityEstimator
- **Theorems:** 0
- **Proofs:** 0

### peano
- **File:** `axioms/peano.py`
- **Types:** None
- **Theorems:** 0
- **Proofs:** 2

### peano_extended
- **File:** `axioms/peano_extended.py`
- **Types:** None
- **Theorems:** 0
- **Proofs:** 1

### quantum_logic
- **File:** `axioms/quantum_logic.py`
- **Types:** QuantumState, Observable, OrthomodularLattice
- **Theorems:** 1
- **Proofs:** 0

### real_analysis
- **File:** `axioms/real_analysis.py`
- **Types:** Sequence
- **Theorems:** 2
- **Proofs:** 0

### synthetic_differential_geometry
- **File:** `axioms/synthetic_differential_geometry.py`
- **Types:** Infinitesimal, Microquantity, MicrolinearSpace
- **Theorems:** 1
- **Proofs:** 0

### temporal_logic
- **File:** `axioms/temporal_logic.py`
- **Types:** KripkeStructure
- **Theorems:** 0
- **Proofs:** 0

### topology
- **File:** `axioms/topology.py`
- **Types:** Point, TopologicalSpace
- **Theorems:** 0
- **Proofs:** 0

### type_registry
- **File:** `axioms/type_registry.py`
- **Types:** TypeKind, TypeUniverse, Multiplicity, TypeNode
- **Theorems:** 0
- **Proofs:** 0

### yeshua_axioms
- **File:** `axioms/yeshua_axioms.py`
- **Types:** YeshuaClaim, YeshuaViolation
- **Theorems:** 0
- **Proofs:** 0
- **Referenced in:**
  - `src/sal/adjoint_triple.py`
  - `src/sal/forcing_operation.py`
  - `src/sal/higher_adjunction.py`
  - `src/sal/self_referential.py`
  - `src/sal/topos_subobject_classifier.py`

### zero_knowledge
- **File:** `axioms/zero_knowledge.py`
- **Types:** Commitment, SchnorrProtocol
- **Theorems:** 0
- **Proofs:** 0
