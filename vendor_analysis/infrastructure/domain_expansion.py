#!/usr/bin/env python3
"""
Domain Expansion Framework for Orthogonal Engineering
New Types of Types, New Kinds of Kinds, Maximal Restoration

This module implements the maximal polymathic expansion across all fields,
domains, and categories. It creates new ontological structures for capturing
and organizing the 500+ vendored repositories and their associated issues.

Author: Kimi CLI (Architectural Steward)
Session: 24ae8482-54c6-4ff6-869a-e737c2ad2917
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologicalLayer(Enum):
    """
    The 8 Ontological Layers of Orthogonal Engineering.
    Each layer represents a fundamental stratum of existence/organization.
    """
    LAYER_0_SUPRANATIONAL = 0      # Universal, pre-legal
    LAYER_1_CONSTITUTIONAL = 1     # Foundational law
    LAYER_2_STATUTORY = 2          # Legislative frameworks
    LAYER_3_REGULATORY = 3         # Agency rules
    LAYER_4_INSTITUTIONAL = 4      # Organizational
    LAYER_5_TECHNICAL = 5          # Implementation
    LAYER_6_MATHEMATICAL = 6       # Formal systems
    LAYER_7_METAPHYSICAL = 7       # Ontological ground


class DomainType(Enum):
    """Extended domain types beyond the original 141 domains."""
    # Original categories (preserved)
    LEGAL = "legal"
    REGULATORY = "regulatory"
    TECHNICAL = "technical"
    MATHEMATICAL = "mathematical"
    
    # New expanded categories
    COMPUTATIONAL = "computational"
    COGNITIVE = "cognitive"
    SEMIOTIC = "semiotic"
    PHENOMENOLOGICAL = "phenomenological"
    EPISTEMIC = "epistemic"
    PRAXEOLOGICAL = "praxeological"  # Study of action
    AXIOPOETIC = "axiopoetic"        # Value creation
    CHRONOPOLITICAL = "chronopolitical"  # Time governance
    TOPOLOGICAL = "topological_social"
    ECOLOGICAL = "ecological"
    BIOSOCIAL = "biosocial"
    TECHNOSOCIAL = "technosocial"
    LUDIC = "ludic"  # Game/play domains
    AESTHETIC = "aesthetic"
    NARRATIVE = "narrative"
    RESTORATIVE = "restorative"


class IssueCategory(Enum):
    """Taxonomy of issue types across all domains."""
    # Technical Issues
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    DEADLOCK = "deadlock"
    INFINITE_LOOP = "infinite_loop"
    REGRESSION = "regression"
    COMPATIBILITY = "compatibility"
    BUILD_FAILURE = "build_failure"
    
    # AI-Specific Issues
    HALLUCINATION = "hallucination"
    STATE_AMNESIA = "state_amnesia"
    PHASE_VIOLATION = "phase_violation"
    PROMPT_INJECTION = "prompt_injection"
    TOKEN_EXHAUSTION = "token_exhaustion"
    CONTEXT_COLLAPSE = "context_collapse"
    DETERMINISM_FAILURE = "determinism_failure"
    
    # Modding Issues
    CRASH_ON_LOAD = "crash_on_load"
    RENDER_CORRUPTION = "render_corruption"
    SAVE_GAME_CORRUPTION = "save_game_corruption"
    MOD_CONFLICT = "mod_conflict"
    API_BREAKAGE = "api_breakage"
    VERSION_MISMATCH = "version_mismatch"
    
    # Ontological Issues
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MERKLE_MISMATCH = "merkle_mismatch"
    INVARIANT_VIOLATION = "invariant_violation"
    TYPE_ERROR = "type_error"
    BOUNDARY_BREACH = "boundary_breach"
    
    # Social/Process Issues
    DOCUMENTATION_GAP = "documentation_gap"
    COMMUNICATION_FAILURE = "communication_failure"
    PRIORITY_INVERSION = "priority_inversion"
    SCOPE_CREEP = "scope_creep"
    TECHNICAL_DEBT = "technical_debt"


@dataclass
class TypeConstructor:
    """
    A type constructor for creating new kinds of types.
    Implements dependent type theory concepts for the OE framework.
    """
    name: str
    arity: int  # Number of type parameters
    parameters: List[str]
    constraints: List[str]
    documentation: str
    
    def instantiate(self, *args: str) -> "ConstructedType":
        """Instantiate this constructor with concrete types."""
        if len(args) != self.arity:
            raise ValueError(f"Expected {self.arity} arguments, got {len(args)}")
        return ConstructedType(
            constructor=self,
            arguments=list(args),
            hash=self._compute_hash(args)
        )
    
    def _compute_hash(self, args: Tuple[str, ...]) -> str:
        """Compute SHA-256 hash of this type instance."""
        data = f"{self.name}:{','.join(args)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class ConstructedType:
    """A concrete type constructed from a type constructor."""
    constructor: TypeConstructor
    arguments: List[str]
    hash: str
    
    def __str__(self) -> str:
        if self.arguments:
            return f"{self.constructor.name}<{', '.join(self.arguments)}>"
        return self.constructor.name


@dataclass
class DomainSchema:
    """
    Schema for a domain in the expanded taxonomy.
    """
    domain_id: str
    name: str
    layer: OntologicalLayer
    domain_type: DomainType
    description: str
    
    # Relationships
    parent_domains: List[str] = field(default_factory=list)
    child_domains: List[str] = field(default_factory=list)
    adjacent_domains: List[str] = field(default_factory=list)
    
    # Content
    repositories: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    invariants: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    merkle_root: str = ""
    
    def compute_merkle_root(self) -> str:
        """Compute merkle root for this domain."""
        data = json.dumps({
            "domain_id": self.domain_id,
            "name": self.name,
            "layer": self.layer.name,
            "domain_type": self.domain_type.value,
            "repositories": sorted(self.repositories),
            "invariants": self.invariants,
        }, sort_keys=True)
        self.merkle_root = hashlib.sha256(data.encode()).hexdigest()
        return self.merkle_root


class DomainExpansionEngine:
    """
    Engine for expanding the domain taxonomy to maximal coverage.
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.domains: Dict[str, DomainSchema] = {}
        self.type_constructors: Dict[str, TypeConstructor] = {}
        self.issue_taxonomy: Dict[str, List[str]] = {}
        
        self._initialize_type_constructors()
        self._initialize_base_domains()
    
    def _initialize_type_constructors(self) -> None:
        """Initialize the type constructor system."""
        constructors = [
            TypeConstructor(
                name="Repository",
                arity=1,
                parameters=["category"],
                constraints=["category must be valid RepoCategory"],
                documentation="A software repository of a specific category"
            ),
            TypeConstructor(
                name="Issue",
                arity=2,
                parameters=["category", "severity"],
                constraints=["category must be valid IssueCategory", "severity in [LOW, MEDIUM, HIGH, CRITICAL]"],
                documentation="An issue with category and severity"
            ),
            TypeConstructor(
                name="Adjunction",
                arity=2,
                parameters=["domain_a", "domain_b"],
                constraints=["domain_a and domain_b must exist"],
                documentation="An adjunction relationship between two domains"
            ),
            TypeConstructor(
                name="Morphism",
                arity=2,
                parameters=["source", "target"],
                constraints=["source and target must be valid domains"],
                documentation="A structure-preserving mapping between domains"
            ),
            TypeConstructor(
                name="Sheaf",
                arity=1,
                parameters=["base_space"],
                constraints=["base_space must be a topological domain"],
                documentation="A sheaf over a base topological space"
            ),
            TypeConstructor(
                name="Functor",
                arity=2,
                parameters=["source_category", "target_category"],
                constraints=["categories must be valid"],
                documentation="A functor between categories"
            ),
            TypeConstructor(
                name="Invariant",
                arity=1,
                parameters=["domain"],
                constraints=["domain must exist"],
                documentation="An invariant property of a domain"
            ),
            TypeConstructor(
                name="GlassBox",
                arity=1,
                parameters=["system"],
                constraints=["system must be auditable"],
                documentation="A glass-box audit wrapper for a system"
            ),
            TypeConstructor(
                name="AuditTrail",
                arity=1,
                parameters=["subject"],
                constraints=["subject must be traceable"],
                documentation="An audit trail for a subject"
            ),
        ]
        
        for tc in constructors:
            self.type_constructors[tc.name] = tc
        
        logger.info(f"Initialized {len(constructors)} type constructors")
    
    def _initialize_base_domains(self) -> None:
        """Initialize base domains for the expansion."""
        base_domains = [
            # Computational Domains
            DomainSchema(
                domain_id="d_computational_foundations",
                name="Computational Foundations",
                layer=OntologicalLayer.LAYER_6_MATHEMATICAL,
                domain_type=DomainType.COMPUTATIONAL,
                description="Foundational computational theory: lambda calculus, Turing machines, type theory"
            ),
            DomainSchema(
                domain_id="d_programming_languages",
                name="Programming Languages",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.COMPUTATIONAL,
                description="Programming language design, implementation, semantics"
            ),
            DomainSchema(
                domain_id="d_software_engineering",
                name="Software Engineering",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.TECHNICAL,
                description="Software development methodologies, patterns, practices"
            ),
            DomainSchema(
                domain_id="d_distributed_systems",
                name="Distributed Systems",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.TECHNICAL,
                description="Distributed computing, consensus, replication"
            ),
            DomainSchema(
                domain_id="d_machine_learning_systems",
                name="Machine Learning Systems",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.COGNITIVE,
                description="ML infrastructure, training, inference, deployment"
            ),
            
            # Game/Ludic Domains
            DomainSchema(
                domain_id="d_game_engines",
                name="Game Engines",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.LUDIC,
                description="Game engine architecture, rendering, physics, audio"
            ),
            DomainSchema(
                domain_id="d_game_design",
                name="Game Design",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.LUDIC,
                description="Game mechanics, level design, player psychology"
            ),
            DomainSchema(
                domain_id="d_modding_communities",
                name="Modding Communities",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.LUDIC,
                description="Game modification ecosystems, tools, community governance"
            ),
            DomainSchema(
                domain_id="d_game_ai",
                name="Game AI",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.LUDIC,
                description="NPC behavior, procedural generation, player modeling"
            ),
            
            # AI/ML Domains
            DomainSchema(
                domain_id="d_neural_networks",
                name="Neural Networks",
                layer=OntologicalLayer.LAYER_6_MATHEMATICAL,
                domain_type=DomainType.COGNITIVE,
                description="Neural network architectures, training, optimization"
            ),
            DomainSchema(
                domain_id="d_natural_language_processing",
                name="Natural Language Processing",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.COGNITIVE,
                description="Language models, tokenization, semantic analysis"
            ),
            DomainSchema(
                domain_id="d_computer_vision",
                name="Computer Vision",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.COGNITIVE,
                description="Image processing, object detection, scene understanding"
            ),
            DomainSchema(
                domain_id="d_ai_safety",
                name="AI Safety",
                layer=OntologicalLayer.LAYER_3_REGULATORY,
                domain_type=DomainType.COGNITIVE,
                description="AI alignment, safety constraints, oversight mechanisms"
            ),
            DomainSchema(
                domain_id="d_ai_governance",
                name="AI Governance",
                layer=OntologicalLayer.LAYER_2_STATUTORY,
                domain_type=DomainType.COGNITIVE,
                description="AI policy, regulation, ethical frameworks"
            ),
            
            # New Expanded Domains
            DomainSchema(
                domain_id="d_semiotic_systems",
                name="Semiotic Systems",
                layer=OntologicalLayer.LAYER_6_MATHEMATICAL,
                domain_type=DomainType.SEMIOTIC,
                description="Sign systems, representation, meaning-making"
            ),
            DomainSchema(
                domain_id="d_epistemic_infrastructure",
                name="Epistemic Infrastructure",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.EPISTEMIC,
                description="Knowledge systems, verification, validation"
            ),
            DomainSchema(
                domain_id="d_axiopoetic_systems",
                name="Axiopoetic Systems",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.AXIOPOETIC,
                description="Value creation, norm generation, ethical emergence"
            ),
            DomainSchema(
                domain_id="d_chronopolitical_governance",
                name="Chronopolitical Governance",
                layer=OntologicalLayer.LAYER_3_REGULATORY,
                domain_type=DomainType.CHRONOPOLITICAL,
                description="Time governance, temporal policy, scheduling systems"
            ),
            DomainSchema(
                domain_id="d_topological_social",
                name="Topological Social Systems",
                layer=OntologicalLayer.LAYER_6_MATHEMATICAL,
                domain_type=DomainType.TOPOLOGICAL,
                description="Social topology, network structures, adjacency"
            ),
            DomainSchema(
                domain_id="d_ecological_computing",
                name="Ecological Computing",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.ECOLOGICAL,
                description="Sustainable computing, energy-aware systems, circular tech"
            ),
            DomainSchema(
                domain_id="d_biosocial_systems",
                name="Biosocial Systems",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.BIOSOCIAL,
                description="Bio-digital integration, human-computer symbiosis"
            ),
            DomainSchema(
                domain_id="d_technosocial_dynamics",
                name="Technosocial Dynamics",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.TECHNOSOCIAL,
                description="Technology-society interaction, digital sociology"
            ),
            DomainSchema(
                domain_id="d_restorative_systems",
                name="Restorative Systems",
                layer=OntologicalLayer.LAYER_3_REGULATORY,
                domain_type=DomainType.RESTORATIVE,
                description="System repair, healing, reconciliation mechanisms"
            ),
            DomainSchema(
                domain_id="d_narrative_systems",
                name="Narrative Systems",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.NARRATIVE,
                description="Story systems, narrative generation, plot structures"
            ),
            DomainSchema(
                domain_id="d_aesthetic_computation",
                name="Aesthetic Computation",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.AESTHETIC,
                description="Beauty in computation, elegant solutions, visual programming"
            ),
            DomainSchema(
                domain_id="d_praxeological_systems",
                name="Praxeological Systems",
                layer=OntologicalLayer.LAYER_4_INSTITUTIONAL,
                domain_type=DomainType.PRAXEOLOGICAL,
                description="Action theory, workflow optimization, process design"
            ),
            DomainSchema(
                domain_id="d_phenomenological_interfaces",
                name="Phenomenological Interfaces",
                layer=OntologicalLayer.LAYER_5_TECHNICAL,
                domain_type=DomainType.PHENOMENOLOGICAL,
                description="Lived experience of technology, UX from first-person perspective"
            ),
        ]
        
        for domain in base_domains:
            self.domains[domain.domain_id] = domain
        
        logger.info(f"Initialized {len(base_domains)} base domains")
    
    def create_domain(
        self,
        domain_id: str,
        name: str,
        layer: OntologicalLayer,
        domain_type: DomainType,
        description: str,
        parent_domains: Optional[List[str]] = None
    ) -> DomainSchema:
        """Create a new domain in the taxonomy."""
        domain = DomainSchema(
            domain_id=domain_id,
            name=name,
            layer=layer,
            domain_type=domain_type,
            description=description,
            parent_domains=parent_domains or []
        )
        
        # Link to parent domains
        for parent_id in domain.parent_domains:
            if parent_id in self.domains:
                self.domains[parent_id].child_domains.append(domain_id)
        
        self.domains[domain_id] = domain
        logger.info(f"Created domain: {domain_id}")
        return domain
    
    def add_repository_to_domain(self, domain_id: str, repo_id: str) -> None:
        """Associate a repository with a domain."""
        if domain_id not in self.domains:
            raise ValueError(f"Domain {domain_id} not found")
        self.domains[domain_id].repositories.append(repo_id)
        self.domains[domain_id].modified_at = datetime.now(timezone.utc).isoformat()
    
    def classify_issue(
        self,
        issue_id: str,
        category: IssueCategory,
        severity: str,
        domain_id: str
    ) -> Dict[str, Any]:
        """Classify an issue within the taxonomy."""
        classification = {
            "issue_id": issue_id,
            "category": category.value,
            "severity": severity,
            "domain_id": domain_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if category.value not in self.issue_taxonomy:
            self.issue_taxonomy[category.value] = []
        self.issue_taxonomy[category.value].append(issue_id)
        
        return classification
    
    def save_expansion(self) -> None:
        """Save the domain expansion to disk."""
        # Save domains
        domains_path = self.base_path / "expanded_domains.json"
        domains_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_domains": len(self.domains),
            "domains": {
                domain_id: {
                    "domain_id": d.domain_id,
                    "name": d.name,
                    "layer": d.layer.name,
                    "domain_type": d.domain_type.value,
                    "description": d.description,
                    "parent_domains": d.parent_domains,
                    "child_domains": d.child_domains,
                    "adjacent_domains": d.adjacent_domains,
                    "repositories": d.repositories,
                    "invariants": d.invariants,
                    "merkle_root": d.compute_merkle_root(),
                }
                for domain_id, d in self.domains.items()
            }
        }
        with open(domains_path, "w") as f:
            json.dump(domains_data, f, indent=2, sort_keys=True)
        logger.info(f"Saved {len(self.domains)} domains to {domains_path}")
        
        # Save type constructors
        types_path = self.base_path / "type_constructors.json"
        types_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "constructors": {
                name: {
                    "name": tc.name,
                    "arity": tc.arity,
                    "parameters": tc.parameters,
                    "constraints": tc.constraints,
                    "documentation": tc.documentation,
                }
                for name, tc in self.type_constructors.items()
            }
        }
        with open(types_path, "w") as f:
            json.dump(types_data, f, indent=2, sort_keys=True)
        logger.info(f"Saved {len(self.type_constructors)} type constructors to {types_path}")
        
        # Save issue taxonomy
        issues_path = self.base_path / "issue_taxonomy.json"
        issues_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "categories": {cat.value: {} for cat in IssueCategory},
            "taxonomy": self.issue_taxonomy,
        }
        with open(issues_path, "w") as f:
            json.dump(issues_data, f, indent=2, sort_keys=True)
        logger.info(f"Saved issue taxonomy to {issues_path}")


# Global expansion engine
expansion_engine = DomainExpansionEngine(
    Path("/home/idor/orthogonal-engineering/vendor_analysis/taxonomy")
)


if __name__ == "__main__":
    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - DOMAIN EXPANSION FRAMEWORK")
    print("New Types of Types, New Kinds of Kinds")
    print("=" * 70)
    print()
    
    print(f"Initialized {len(expansion_engine.domains)} domains")
    print(f"Initialized {len(expansion_engine.type_constructors)} type constructors")
    print(f"Issue categories: {len(IssueCategory)}")
    print()
    
    # Demonstrate type construction
    print("Type Constructor Examples:")
    repo_type = expansion_engine.type_constructors["Repository"].instantiate("machine_learning_phd")
    print(f"  Repository<machine_learning_phd> → {repo_type.hash}")
    
    issue_type = expansion_engine.type_constructors["Issue"].instantiate("security", "CRITICAL")
    print(f"  Issue<security, CRITICAL> → {issue_type.hash}")
    
    adjunction_type = expansion_engine.type_constructors["Adjunction"].instantiate("d_game_engines", "d_modding_communities")
    print(f"  Adjunction<d_game_engines, d_modding_communities> → {adjunction_type.hash}")
    
    print()
    
    # Save expansion
    expansion_engine.save_expansion()
    
    print("=" * 70)
    print("Domain expansion complete. All new ontological structures initialized.")
    print("=" * 70)
