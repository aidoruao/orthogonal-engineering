#!/usr/bin/env python3
"""
Compiler Design Domain — Type Soundness, Optimization Correctness

Key concepts:
- Type soundness: Progress + Preservation
- Graph coloring for register allocation
- Semantics-preserving optimizations
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum, auto


class TypeExpr(Enum):
    INT = "int"
    BOOL = "bool"
    FUN = "fun"
    VOID = "void"


@dataclass
class Term:
    """AST node for type checking."""
    term_type: str
    typ: Optional[TypeExpr] = None
    subterms: List['Term'] = field(default_factory=list)


@dataclass
class TypeChecker:
    """Type checker with progress and preservation."""
    term: Term
    
    def is_well_typed(self) -> bool:
        """Check if term has a valid type ( Preservation check)."""
        return self.term.typ is not None
    
    def can_take_step(self) -> bool:
        """Check if term can evaluate (Progress check)."""
        # Simplified: values cannot step, non-values can
        return self.term.term_type not in ["value", "literal"]


@dataclass
class OptimizationPass:
    """Compiler optimization with correctness verification."""
    name: str
    input_ir: str
    output_ir: str
    
    def preserves_semantics(self) -> bool:
        """Check if optimization preserves program semantics."""
        # Simplified: compare normalized forms
        return self._normalize(self.input_ir) == self._normalize(self.output_ir)
    
    def _normalize(self, ir: str) -> str:
        """Normalize IR for comparison."""
        # Remove whitespace for simple comparison
        return ''.join(ir.split())


@dataclass
class InterferenceGraph:
    """Graph for register allocation."""
    nodes: Set[str] = field(default_factory=set)
    edges: Set[Tuple[str, str]] = field(default_factory=set)
    
    def add_node(self, node: str) -> None:
        self.nodes.add(node)
    
    def add_edge(self, u: str, v: str) -> None:
        if u != v:
            self.edges.add(tuple(sorted([u, v])))
    
    def degree(self, node: str) -> int:
        return sum(1 for u, v in self.edges if u == node or v == node)
    
    def is_k_colorable(self, k: int) -> bool:
        """Check if graph is k-colorable using greedy approach."""
        if not self.nodes:
            return True
        
        coloring: Dict[str, int] = {}
        
        for node in sorted(self.nodes):
            # Find used colors by neighbors
            used_colors = set()
            for u, v in self.edges:
                if u == node and v in coloring:
                    used_colors.add(coloring[v])
                if v == node and u in coloring:
                    used_colors.add(coloring[u])
            
            # Find first available color
            color = 0
            while color in used_colors:
                color += 1
            
            if color >= k:
                return False
            coloring[node] = color
        
        return True


@dataclass
class RegisterAllocator:
    """Register allocation using graph coloring."""
    interference: InterferenceGraph
    num_registers: int
    
    def can_allocate(self) -> bool:
        """Check if all variables can be assigned to registers."""
        return self.interference.is_k_colorable(self.num_registers)


# Type soundness thresholds
MAX_TYPE_CHECKING_TIME_MS = Fraction(1000)
