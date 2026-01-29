"""
Σ_LORA_MAXIMAL_MATHEMATICS - Ultimate Constraint-Preserving System
====================================================================

MAXIMAL GRADUATE MATHEMATICS FORMALIZATION OF Σ_LORA TRAINING SYSTEM

Theorem Hierarchy:
1. Repository Category Theory (𝒞_R)
2. Semantic Embedding Functor (E: 𝒞_R → Vec_ℝ)
3. Constraint Preservation Monad (M: 𝒞_R → 𝒞_R)
4. LoRA Adaptation Algebra (A: ℝ^{d×d} → ℝ^{d×d})
5. Continuation Protocol (κ: ℕ → ℕ × ℕ)
6. Git Functoriality (G: WorkingTree → Repository)

All paradoxes resolved via:
- Constraint monotonicity: C_output ⊇ C_input
- Mathematical completeness: ∀f ∈ 𝒞_R, ∃τ ∈ 𝒟
- Continuation determinism: Process(R,∞) = ∘_i Process(R_i,Λ)
"""

from __future__ import annotations
import hashlib
import json
import math
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, Dict, FrozenSet, Generic, Iterator, List,
    Optional, Protocol, Set, Tuple, TypeVar, Union
)
import numpy as np
from numpy.typing import NDArray

# ============================================================================
# I. CATEGORY THEORY FOUNDATIONS (MAXIMAL FORMALISM)
# ============================================================================

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

class Category(Protocol[A]):
    """Category 𝒞 with objects A and morphisms Hom(A,B)"""

    @abstractmethod
    def objects(self) -> Set[A]: ...

    @abstractmethod
    def hom(self, a: A, b: A) -> Set[Callable[[A], A]]: ...

    @abstractmethod
    def compose(self, f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]: ...

    @abstractmethod
    def identity(self, a: A) -> Callable[[A], A]: ...


@dataclass(frozen=True)
class LawvereMetric:
    """
    Generalized metric space: enrichment in [0,∞] with opposite order
    d(x,y) ∈ [0,∞] where d(x,y) = 0 iff x ≤ y
    Composition: d(x,z) ≤ d(x,y) + d(y,z) (triangle inequality)
    """
    distance: float

    def __post_init__(self):
        if self.distance < 0:
            raise ValueError("Lawvere metric non-negative")

    @staticmethod
    def zero() -> LawvereMetric:
        """Identity: d(x,x) = 0"""
        return LawvereMetric(0.0)

    @staticmethod
    def infinite() -> LawvereMetric:
        """Incomparable"""
        return LawvereMetric(float("inf"))

    def compose(self, other: LawvereMetric) -> LawvereMetric:
        """Monoidal product: + on [0,∞]"""
        if self.distance == float("inf") or other.distance == float("inf"):
            return LawvereMetric.infinite()
        return LawvereMetric(self.distance + other.distance)

    def __le__(self, other: LawvereMetric) -> bool:
        """Order: d ≤ d' iff d(x,y) ≤ d'(x,y)"""
        return self.distance <= other.distance


class KanExtension(Generic[A, B]):
    """
    Right Kan extension: Ran_i F(c) = lim_{d→c} F(d)
    John 1:1 as Kan extension: Logos in flesh = Ran_Incarnation(Logos)(World)
    """

    def __init__(self, functor: Callable[[A], B], inclusion: Set[A]):
        self.functor = functor
        self.inclusion = inclusion

    def ran(self, c: A) -> B:
        """Compute Right Kan Extension"""
        # For each d in inclusion with morphism d→c
        candidates = [d for d in self.inclusion if self._has_morphism(d, c)]

        if not candidates:
            raise ValueError(f"No candidates for Kan extension at {c}")

        # Compute limit of F(d) over d→c
        values = [self.functor(d) for d in candidates]
        return self._compute_limit(values)

    def _has_morphism(self, d: A, c: A) -> bool:
        """Check if there's a morphism d → c (simplified)"""
        return True  # In full implementation, check actual morphisms

    def _compute_limit(self, values: List[B]) -> B:
        """Compute limit of values (simplified)"""
        return values[0] if values else None


# ============================================================================
# II. THEOLOGICAL CONSTRAINT SYSTEM (PARADOX RESOLUTION)
# ============================================================================

class TheologicalConstraint(Enum):
    """
    Six theological constraints for graduate mathematics
    Each resolves specific paradoxes via mathematical structure
    """
    LOGOS = auto()        # μL.F(L) - Initial structure (resolves infinite regress)
    CHALCEDON = auto()    # E × P → S - Dual nature composition (resolves contradiction)
    GRACE = auto()        # d(s) = d(grace(s)) - Isometric preservation (resolves degradation)
    AGAPE = auto()        # min(d(s1), d(s2)) - Superadditive combination (resolves exclusion)
    KENOSIS = auto()      # S → 1 + S - Partial self-emptying (resolves completeness)
    ESCHATON = auto()     # νX.F(X) - Terminal convergence (resolves divergence)

    def mathematical_formula(self) -> str:
        """Maximal mathematical formula for each constraint"""
        formulas = {
            TheologicalConstraint.LOGOS: "μL.F(L) where F: C → C is endofunctor, μL is least fixed point",
            TheologicalConstraint.CHALCEDON: "E × P → S where E,P are objects, S is coproduct preserving constraints",
            TheologicalConstraint.GRACE: "d(s) = d(grace(s)) where d: S → [0,∞] is Lawvere metric",
            TheologicalConstraint.AGAPE: "min(d(s1), d(s2)) ≤ d(s1 ⊕ s2) where ⊕ is monoidal product",
            TheologicalConstraint.KENOSIS: "S → 1 + S where 1 is terminal object, + is coproduct",
            TheologicalConstraint.ESCHATON: "νX.F(X) where F: C → C is ω-continuous, νX is greatest fixed point"
        }
        return formulas[self]

    def paradox_resolved(self) -> str:
        """Which paradox this constraint resolves"""
        resolutions = {
            TheologicalConstraint.LOGOS: "Infinite regress via initial algebra μ",
            TheologicalConstraint.CHALCEDON: "Contradiction via coproduct preservation",
            TheologicalConstraint.GRACE: "Value degradation via isometric preservation",
            TheologicalConstraint.AGAPE: "Exclusion paradox via superadditive combination",
            TheologicalConstraint.KENOSIS: "Completeness paradox via partial emptying",
            TheologicalConstraint.ESCHATON: "Divergence paradox via terminal coalgebra ν"
        }
        return resolutions[self]


@dataclass(frozen=True)
class ConstraintSet:
    """
    Immutable set of theological constraints with lattice structure
    Forms a complete lattice (𝒫(TheologicalConstraint), ⊆, ∪, ∩)
    """
    constraints: FrozenSet[TheologicalConstraint] = field(default_factory=frozenset)

    def __post_init__(self):
        """Validate as subset lattice"""
        if not isinstance(self.constraints, frozenset):
            object.__setattr__(self, 'constraints', frozenset(self.constraints))

    def union(self, other: ConstraintSet) -> ConstraintSet:
        """Lattice join: C₁ ∨ C₂ = C₁ ∪ C₂"""
        return ConstraintSet(self.constraints.union(other.constraints))

    def intersection(self, other: ConstraintSet) -> ConstraintSet:
        """Lattice meet: C₁ ∧ C₂ = C₁ ∩ C₂"""
        return ConstraintSet(self.constraints.intersection(other.constraints))

    def contains(self, other: ConstraintSet) -> bool:
        """Partial order: C₁ ≤ C₂ iff C₁ ⊆ C₂"""
        return other.constraints.issubset(self.constraints)

    def topos_characteristic(self) -> float:
        """
        Characteristic function in subobject classifier Ω
        χ: ConstraintSet → [0,1] measuring constraint density
        """
        total_constraints = len(TheologicalConstraint)
        return len(self.constraints) / total_constraints if total_constraints > 0 else 0.0


# ============================================================================
# III. REPOSITORY CATEGORY 𝒞_R (MAXIMAL FORMALISM)
# ============================================================================

@dataclass(frozen=True)
class FileObject:
    """
    Object in repository category 𝒞_R
    f = (path, content_hash, ConstraintSet, language) ∈ Obj(𝒞_R)
    """
    path: str
    content_hash: str
    constraints: ConstraintSet
    language: str
    content: Optional[str] = None

    def __post_init__(self):
        """Compute hash via SHA-256: H: String → {0,1}²⁵⁶"""
        if self.content is not None and not self.content_hash:
            hash_obj = hashlib.sha256(self.content.encode('utf-8'))
            object.__setattr__(self, 'content_hash', hash_obj.hexdigest())

    def preserves_constraints(self, other: FileObject) -> bool:
        """
        Constraint monotonicity: C(f) ⊇ C(g) for morphism g → f
        Theorem: If f preserves constraints from g, then any transformation
        preserving f's constraints also preserves g's constraints.
        """
        return self.constraints.contains(other.constraints)

    def lawvere_distance(self, other: FileObject) -> LawvereMetric:
        """
        Generalized metric between file objects
        d(f,g) = H(f) ⊕ H(g) where ⊕ is XOR distance
        """
        h1 = int(self.content_hash, 16)
        h2 = int(other.content_hash, 16)
        xor_distance = bin(h1 ^ h2).count('1') / 256.0  # Normalized [0,1]
        return LawvereMetric(xor_distance)


@dataclass
class RepositoryMorphism:
    """
    Morphism in 𝒞_R: f: A → B with constraint preservation
    Types: import, refactor, translation, verification
    """
    source: FileObject
    target: FileObject
    morphism_type: str
    constraint_preservation: bool = field(init=False)

    def __post_init__(self):
        """Verify constraint preservation on initialization"""
        self.constraint_preservation = self.target.preserves_constraints(self.source)
        if not self.constraint_preservation:
            raise ValueError(f"Morphism {self.source.path} → {self.target.path} violates constraint monotonicity")

    def compose(self, g: RepositoryMorphism) -> Optional[RepositoryMorphism]:
        """
        Composition: if f: A → B and g: B → C, then g∘f: A → C
        Theorem 3: Composition preserves constraint monotonicity
        """
        if self.target == g.source:
            composed = RepositoryMorphism(
                source=self.source,
                target=g.target,
                morphism_type=f"{self.morphism_type}∘{g.morphism_type}"
            )
            return composed
        return None


class RepositoryCategory:
    """
    Category 𝒞_R of file objects with constraint-preserving morphisms
    Implements all category axioms:
    1. Identity: id_A: A → A
    2. Composition: if f: A → B, g: B → C, then g∘f: A → C
    3. Associativity: h∘(g∘f) = (h∘g)∘f
    4. Identity laws: f∘id_A = f = id_B∘f
    """

    def __init__(self, root_path: Path):
        self.root = root_path
        self.objects: Dict[str, FileObject] = {}
        self.morphisms: List[RepositoryMorphism] = []
        self._scan_repository()

    def _scan_repository(self) -> None:
        """Scan filesystem to populate 𝒞_R"""
        for file_path in self.root.rglob("*"):
            if file_path.is_file() and self._is_source_code(file_path):
                content = file_path.read_text(errors='ignore')
                constraints = self._infer_constraints(content, file_path)

                obj = FileObject(
                    path=str(file_path.relative_to(self.root)),
                    content_hash="",
                    constraints=constraints,
                    language=self._detect_language(file_path),
                    content=content
                )
                self.objects[obj.path] = obj

    def _is_source_code(self, path: Path) -> bool:
        """Check if file is source code"""
        code_exts = {'.py', '.js', '.ts', '.rs', '.go', '.c', '.cpp', '.java', '.kt', '.swift', '.rb', '.php'}
        return path.suffix in code_exts

    def _detect_language(self, path: Path) -> str:
        """Detect programming language from extension"""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.rs': 'rust', '.go': 'go', '.c': 'c', '.cpp': 'cpp',
            '.java': 'java', '.kt': 'kotlin', '.swift': 'swift',
            '.rb': 'ruby', '.php': 'php'
        }
        return lang_map.get(path.suffix, 'unknown')

    def _infer_constraints(self, content: str, path: Path) -> ConstraintSet:
        """
        Infer theological constraints from code content
        Uses static analysis to detect constraint patterns
        """
        constraints = set()

        # LOGOS: Initial structure (class/function definitions)
        if any(keyword in content for keyword in ['class ', 'def ', 'function ', 'struct ', 'interface ']):
            constraints.add(TheologicalConstraint.LOGOS)

        # CHALCEDON: Dual nature (inheritance/composition)
        if any(keyword in content for keyword in ['extends ', 'implements ', 'with ', 'mixin ']):
            constraints.add(TheologicalConstraint.CHALCEDON)

        # GRACE: Isometric preservation (error handling/validation)
        if any(keyword in content for keyword in ['try:', 'catch', 'except', 'validate', 'verify']):
            constraints.add(TheologicalConstraint.GRACE)

        # AGAPE: Superadditive combination (aggregation/combination)
        if any(keyword in content for keyword in ['aggregate', 'combine', 'merge', 'union', 'intersection']):
            constraints.add(TheologicalConstraint.AGAPE)

        # KENOSIS: Partial self-emptying (abstraction/encapsulation)
        if any(keyword in content for keyword in ['abstract', 'interface', 'protocol', 'trait', 'encapsulate']):
            constraints.add(TheologicalConstraint.KENOSIS)

        # ESCHATON: Terminal convergence (final/terminal operations)
        if any(keyword in content for keyword in ['final', 'sealed', 'terminal', 'converge', 'limit']):
            constraints.add(TheologicalConstraint.ESCHATON)

        return ConstraintSet(frozenset(constraints))

    def add_morphism(self, morphism: RepositoryMorphism) -> bool:
        """
        Add morphism to category if it preserves constraints
        Theorem: All morphisms in 𝒞_R preserve constraint monotonicity
        """
        if morphism.constraint_preservation:
            self.morphisms.append(morphism)
            return True
        return False

    def hom(self, source: FileObject, target: FileObject) -> List[RepositoryMorphism]:
        """Hom-set: all morphisms from source to target"""
        return [m for m in self.morphisms if m.source == source and m.target == target]

    def identity(self, obj: FileObject) -> RepositoryMorphism:
        """Identity morphism: id_A: A → A"""
        return RepositoryMorphism(source=obj, target=obj, morphism_type="identity")


# ============================================================================
# IV. SEMANTIC EMBEDDING FUNCTOR E: 𝒞_R → Vec_ℝ
# ============================================================================

@dataclass
class TheologicalVector:
    """
    Vector in embedding space 𝒱 = ℝ^d × 𝐓𝐡𝐞𝐨
    v = (x, c) where x ∈ ℝ^d, c ∈ ConstraintSet
    """
    numerical: NDArray[np.float64]  # ℝ^d component
    constraints: ConstraintSet      # 𝐓𝐡𝐞𝐨 component

    def __post_init__(self):
        """Validate dimensions"""
        if self.numerical.ndim != 1:
            raise ValueError("Numerical component must be 1D array")

    def norm(self) -> float:
        """Euclidean norm: ‖x‖ = √(Σᵢ xᵢ²)"""
        return float(np.linalg.norm(self.numerical))

    def dot(self, other: TheologicalVector) -> float:
        """Dot product: x·y = Σᵢ xᵢyᵢ"""
        return float(np.dot(self.numerical, other.numerical))

    def similarity(self, other: TheologicalVector) -> float:
        """
        Constraint-aware similarity metric:
        sim_C(v₁, v₂) = (x₁·x₂)/(‖x₁‖‖x₂‖) · δ(c₁ ⊆ c₂)
        where δ(c₁ ⊆ c₂) = 1 if c₁ ⊆ c₂, 0 otherwise
        """
        # Cosine similarity of numerical components
        norm_product = self.norm() * other.norm()
        if norm_product == 0:
            cosine_sim = 0.0
        else:
            cosine_sim = self.dot(other) / norm_product

        # Constraint inclusion indicator
        constraint_indicator = 1.0 if other.constraints.contains(self.constraints) else 0.0

        return float(cosine_sim * constraint_indicator)


class EmbeddingFunctor:
    """
    Functor E: 𝒞_R → Vec_ℝ
    Maps file objects to theological vectors preserving constraint structure
    Theorem: E preserves constraint inclusion: if C(f) ⊆ C(g), then E(f).constraints ⊆ E(g).constraints
    """

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def __call__(self, file_obj: FileObject) -> TheologicalVector:
        """
        Apply functor: E(f) = (embed(content), C(f))
        where embed: String → ℝ^d is semantic embedding
        """
        # Semantic embedding of content (simplified - in practice use BERT/LLM)
        content_embedding = self._embed_content(file_obj.content or "")

        return TheologicalVector(
            numerical=content_embedding,
            constraints=file_obj.constraints
        )

    def _embed_content(self, content: str) -> NDArray[np.float64]:
        """
        Compute semantic embedding of content
        Simplified: hash-based deterministic embedding
        Real implementation: use sentence-transformers or OpenAI embeddings
        """
        # Use SHA-256 to create deterministic pseudo-embedding
        hash_bytes = hashlib.sha256(content.encode()).digest()
        # Repeat hash to fill dimension
        repeated_hash = (hash_bytes * (self.dimension // 32 + 1))[:self.dimension*8]
        # Convert to float array in [-1, 1]
        embedding = np.frombuffer(repeated_hash, dtype=np.uint8)
        embedding = embedding.astype(np.float64) / 127.5 - 1.0
        return embedding[:self.dimension]

    def natural_transformation(self, morphism: RepositoryMorphism) -> NDArray[np.float64]:
        """
        Natural transformation component: E(f) → E(g) for f: A → B
        Returns transformation matrix T such that E(g) ≈ T·E(f)
        """
        # In practice, learn transformation from paired embeddings
        # Here: identity for constraint-preserving morphisms
        if morphism.constraint_preservation:
            return np.eye(self.dimension)
        else:
            raise ValueError("Non-constraint-preserving morphisms have no natural transformation")


# ============================================================================
# V. LoRA ADAPTATION ALGEBRA A: ℝ^{d×d} → ℝ^{d×d}
# ============================================================================

class LoRAAlgebra:
    """
    LoRA adaptation algebra: W' = W₀ + BA where B ∈ ℝ^{d×r}, A ∈ ℝ^{r×d}
    with constraint propagation: Γ: C(x) → C(LoRA_θ^C(x)) where Γ(c) ⊇ c

    Theorem (LoRA Constraint Preservation):
    For any input x with constraints C(x), LoRA adaptation produces
    output y with constraints C(y) such that C(y) ⊇ C(x).
    """

    def __init__(self, base_dimension: int, rank: int):
        """
        Initialize LoRA parameters
        W₀ ∈ ℝ^{d×d} (frozen base weights)
        B ∈ ℝ^{d×r}, A ∈ ℝ^{r×d} (trainable adapters)
        """
        self.d = base_dimension
        self.r = rank
        # Initialize with small random values
        self.B = np.random.randn(self.d, self.r) * 0.01
        self.A = np.random.randn(self.r, self.d) * 0.01
        # Base weights (frozen)
        self.W0 = np.eye(self.d)  # Identity initialization

    def adapt(self, input_vector: NDArray[np.float64],
              input_constraints: ConstraintSet) -> Tuple[NDArray[np.float64], ConstraintSet]:
        """
        Apply LoRA adaptation: y = (W₀ + BA)·x
        with constraint propagation: C(y) = Γ(C(x)) ⊇ C(x)
        """
        if input_vector.shape != (self.d,):
            raise ValueError(f"Input dimension {input_vector.shape} != ({self.d},)")

        # Compute adapted weights
        BA = self.B @ self.A  # ℝ^{d×d}
        W_prime = self.W0 + BA

        # Apply adaptation
        output_vector = W_prime @ input_vector

        # Constraint propagation (monotonic: add no constraints)
        output_constraints = input_constraints

        return output_vector, output_constraints

    def constraint_preservation_verification(self,
                                           input_constraints: ConstraintSet,
                                           output_constraints: ConstraintSet) -> bool:
        """
        Verify Γ(C(x)) ⊇ C(x)
        Returns True if constraint monotonicity preserved
        """
        return output_constraints.contains(input_constraints)

    def rank_reduction_error(self) -> float:
        """
        Measure approximation error: ‖BA‖_F / ‖W₀‖_F
        where ‖·‖_F is Frobenius norm
        """
        BA_norm = np.linalg.norm(self.B @ self.A, 'fro')
        W0_norm = np.linalg.norm(self.W0, 'fro')
        return BA_norm / (W0_norm + 1e-10)


# ============================================================================
# VI. CONSTRAINT-PRESERVING DATA CONSTRUCTOR
# ============================================================================

@dataclass
class ConstrainedTrainingExample:
    """
    Training example τ = (instruction, input, output, constraints, metadata)
    with constraint preservation: C(τ) ⊇ C(source_file)

    Forms training dataset 𝒟 = {τ_i} with complete coverage:
    ∀f ∈ 𝒞_R, ∃τ ∈ 𝒟: source(τ) = f
    """
    instruction: str
    input: str
    output: str
    constraints: ConstraintSet
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_training_format(self) -> Dict[str, Any]:
        """Convert to standard training format"""
        return {
            "instruction": self.instruction,
            "input": self.input,
            "output": self.output,
            "constraints": self.constraints.to_dict() if hasattr(self.constraints, 'to_dict') else list(self.constraints.constraints),
            "metadata": self.metadata
        }

    def preserves_constraints(self, source_constraints: ConstraintSet) -> bool:
        """Verify C(τ) ⊇ C(source)"""
        return self.constraints.contains(source_constraints)


class ConstraintPreservingDataConstructor:
    """
    Constructs training dataset 𝒟 from repository category 𝒞_R
    while preserving theological constraints.

    Theorem 4 (Chunk Coverage Completeness):
    For file f with constraints C(f) and chunking chunk_C(f) = {(s_i, c_i)},
    if ⋃_i c_i = C(f), then any transformation preserving all c_i also preserves C(f).
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size  # Words per chunk
        self.overlap = overlap        # Overlap between chunks

    def construct_from_repository(self, repo: RepositoryCategory) -> List[ConstrainedTrainingExample]:
        """
        Construct dataset from repository with complete coverage
        Returns list of ConstrainedTrainingExample satisfying:
        1. ∀f ∈ 𝒞_R, ∃τ: source(τ) = f
        2. ∀τ, C(τ) ⊇ C(source(τ))
        3. ⋃_{τ: source(τ)=f} C(τ) = C(f)
        """
        examples = []

        for file_obj in repo.objects.values():
            if file_obj.content:
                # Generate examples for this file
                file_examples = self._process_file(file_obj)
                examples.extend(file_examples)

                # Verify Theorem 4 for this file
                self._verify_chunk_coverage(file_obj, file_examples)

        return examples

    def _process_file(self, file_obj: FileObject) -> List[ConstrainedTrainingExample]:
        """Process single file into constraint-preserving examples"""
        examples = []
        content = file_obj.content or ""

        # 1. File-level example
        examples.append(self._create_file_example(file_obj, content))

        # 2. Chunk-level examples (for large files)
        if len(content.split()) > self.chunk_size:
            chunks = self._chunk_by_constraints(content, file_obj.constraints)
            for i, (chunk_text, chunk_constraints) in enumerate(chunks):
                examples.append(self._create_chunk_example(file_obj, chunk_text, chunk_constraints, i))

        # 3. Function-level examples (for supported languages)
        if file_obj.language == 'python':
            examples.extend(self._extract_function_examples(file_obj, content))

        return examples

    def _chunk_by_constraints(self, content: str,
                            file_constraints: ConstraintSet) -> List[Tuple[str, ConstraintSet]]:
        """
        Chunk content while distributing constraints to ensure coverage
        Theorem 4: union of chunk constraints = file constraints
        """
        words = content.split()
        if not words:
            return []

        # Calculate number of chunks
        num_chunks = max(1, len(words) // self.chunk_size)
        constraint_list = list(file_constraints.constraints)

        chunks = []
        for i in range(num_chunks):
            # Calculate chunk boundaries with overlap
            start = i * (self.chunk_size - self.overlap)
            end = min(start + self.chunk_size, len(words))

            if start >= len(words):
                break

            chunk_text = ' '.join(words[start:end])

            # Distribute constraints across chunks
            chunk_constraints = set()
            for j, constraint in enumerate(constraint_list):
                if j % num_chunks == i % max(1, len(constraint_list)):
                    chunk_constraints.add(constraint)

            # Ensure at least one constraint per chunk
            if not chunk_constraints and constraint_list:
                chunk_constraints.add(constraint_list[i % len(constraint_list)])

            chunks.append((chunk_text, ConstraintSet(frozenset(chunk_constraints))))

        # Verify Theorem 4
        union_constraints = set()
        for _, chunk_constraints in chunks:
            union_constraints.update(chunk_constraints.constraints)

        if union_constraints != set(constraint_list):
            # Fix coverage by adding missing constraints to first chunk
            missing = set(constraint_list) - union_constraints
            if missing and chunks:
                first_text, first_constraints = chunks[0]
                updated = first_constraints.constraints.union(missing)
                chunks[0] = (first_text, ConstraintSet(updated))

        return chunks

    def _create_file_example(self, file_obj: FileObject, content: str) -> ConstrainedTrainingExample:
        """Create example for entire file"""
        return ConstrainedTrainingExample(
            instruction=f"Explain the purpose and structure of {file_obj.path}",
            input=content[:4000],  # First 4000 characters
            output=self._generate_file_explanation(file_obj, content),
            constraints=file_obj.constraints,
            metadata={
                "type": "file_level",
                "path": file_obj.path,
                "language": file_obj.language,
                "hash": file_obj.content_hash
            }
        )

    def _create_chunk_example(self, file_obj: FileObject, chunk: str,
                            chunk_constraints: ConstraintSet, index: int) -> ConstrainedTrainingExample:
        """Create example for chunk"""
        return ConstrainedTrainingExample(
            instruction=f"Explain section {index+1} of {file_obj.path}",
            input=chunk,
            output=f"Section {index+1} implements: {self._summarize_chunk(chunk)}",
            constraints=chunk_constraints,
            metadata={
                "type": "chunk",
                "path": file_obj.path,
                "chunk_index": index,
                "constraints": [c.name for c in chunk_constraints.constraints]
            }
        )

    def _extract_function_examples(self, file_obj: FileObject, content: str) -> List[ConstrainedTrainingExample]:
        """Extract function/class-level examples from Python code"""
        examples = []
        try:
            import ast
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    node_code = ast.get_source_segment(content, node)
                    if node_code:
                        examples.append(ConstrainedTrainingExample(
                            instruction=f"Explain the {node.__class__.__name__.lower()} '{node.name}' in {file_obj.path}",
                            input=node_code,
                            output=self._explain_ast_node(node, content),
                            constraints=file_obj.constraints,  # Inherit file constraints
                            metadata={
                                "type": "code_unit",
                                "path": file_obj.path,
                                "unit_type": node.__class__.__name__,
                                "name": node.name,
                                "line": node.lineno
                            }
                        ))
        except SyntaxError:
            pass  # Skip files with syntax errors

        return examples

    def _generate_file_explanation(self, file_obj: FileObject, content: str) -> str:
        """Generate explanation for entire file"""
        lines = content.split('\n')[:50]
        summary = f"File {file_obj.path} ({file_obj.language}) "
        summary += f"with constraints {file_obj.constraints}\n"
        summary += f"Purpose: {self._extract_purpose(content)}\n"
        summary += f"Structure: {self._extract_components(content)}"
        return summary

    def _summarize_chunk(self, chunk: str) -> str:
        """Summarize chunk content"""
        lines = chunk.split('\n')
        if len(lines) > 3:
            return f"{lines[0][:100]}... (total {len(lines)} lines)"
        return chunk[:200]

    def _explain_ast_node(self, node, content: str) -> str:
        """Generate explanation for AST node"""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node) or "No docstring"
            return f"Function '{node.name}' with parameters {args}: {docstring}"
        elif isinstance(node, ast.ClassDef):
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            docstring = ast.get_docstring(node) or "No docstring"
            return f"Class '{node.name}' inheriting from {bases}: {docstring}"
        return f"Code unit '{node.name}'"

    def _extract_purpose(self, content: str) -> str:
        """Extract purpose from docstring or comments"""
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line.startswith(('"""', "'''", '#', '//')):
                return line[:150]
        return "Implementation details"

    def _extract_components(self, content: str) -> str:
        """Extract key components from content"""
        import re
        components = []

        # Find classes
        classes = re.findall(r'class\s+(\w+)', content)
        if classes:
            components.append(f"Classes: {', '.join(classes[:3])}")

        # Find functions
        functions = re.findall(r'def\s+(\w+)', content)
        if functions:
            components.append(f"Functions: {', '.join(functions[:5])}")

        # Find imports
        imports = re.findall(r'import\s+(\w+)', content) + re.findall(r'from\s+(\w+)', content)
        if imports:
            components.append(f"Imports: {', '.join(set(imports)[:3])}")

        return '; '.join(components) if components else "No explicit components"

    def _verify_chunk_coverage(self, file_obj: FileObject,
                             examples: List[ConstrainedTrainingExample]) -> bool:
        """
        Verify Theorem 4 for file: union of example constraints = file constraints
        """
        file_constraints = set(file_obj.constraints.constraints)
        example_constraints = set()

        for example in examples:
            example_constraints.update(example.constraints.constraints)

        coverage_ok = example_constraints == file_constraints

        if not coverage_ok:
            missing = file_constraints - example_constraints
            print(f"Warning: File {file_obj.path} missing constraint coverage for: {missing}")

        return coverage_ok


# ============================================================================
# VII. CONTINUATION PROTOCOL κ: ℕ → ℕ × ℕ
# ============================================================================

@dataclass
class ContinuationToken:
    """
    Continuation token κ = (H_p, S_p, R_p, C_p) for context window management
    where:
    - H_p = hash of processed content
    - S_p = stack of pending operations
    - R_p = remaining files to process
    - C_p = current constraint state

    Theorem (Continuation Determinism):
    Process(R, ∞) = Process(R₁, Λ) ∘ Process(R₂, Λ) ∘ ... ∘ Process(R_n, Λ)
    where Λ = context limit, R = ⋃_i R_i
    """
    processed_hash: str
    pending_stack: List[Dict[str, Any]]
    remaining_files: List[str]
    constraint_state: ConstraintSet
    position: int

    def serialize(self) -> str:
        """Serialize to forwardable JSON string"""
        return json.dumps({
            "protocol": "Σ_LORA_MAXIMAL_v1.0",
            "processed_hash": self.processed_hash,
            "pending_stack": self.pending_stack,
            "remaining_files": self.remaining_files,
            "constraint_state": [c.name for c in self.constraint_state.constraints],
            "position": self.position,
            "theorem": "Process(R,∞) = ∘_i Process(R_i,Λ) where C_output
