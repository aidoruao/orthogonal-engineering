"""Semiotic Engine — analyze sign systems in code and documentation.

Implements Peircean semiotics: sign = signifier + signified + interpretant
Applied to:
- Variable names as signs
- Function signatures as sign systems
- Domain boundaries as interpretive communities
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from fractions import Fraction
from enum import Enum, auto

from src.orthogonal_engineering.fraction_display import format_percent


class SignType(Enum):
    """Peirce's trichotomy of signs."""
    ICON = auto()      # Resembles signified (diagram, image)
    INDEX = auto()     # Connected to signified causally (smoke/fire)
    SYMBOL = auto()    # Arbitrary convention (words, code)


@dataclass
class Sign:
    """A sign: signifier + signified + interpretant."""
    signifier: str           # The physical form (text, symbol)
    signified: str           # The concept it represents
    interpretant: str        # The meaning produced in interpreter
    sign_type: SignType
    domain: str = ""         # Which domain/community interprets this
    
    def is_well_formed(self) -> bool:
        """A well-formed sign has all components."""
        return all([self.signifier, self.signified, self.interpretant])


@dataclass
class SignSystem:
    """A system of signs (language, code, notation)."""
    name: str
    signs: Dict[str, Sign] = field(default_factory=dict)
    interpretive_community: Set[str] = field(default_factory=set)
    
    def add_sign(self, sign: Sign) -> None:
        self.signs[sign.signifier] = sign
    
    def interpret(self, signifier: str, interpreter: str) -> Optional[str]:
        """Interpret a signifier within this system."""
        if signifier not in self.signs:
            return None
        
        sign = self.signs[signifier]
        
        # Check if interpreter is part of interpretive community
        if interpreter not in self.interpretive_community:
            return f"[ALien: {sign.signified}]"  # Requires translation
        
        return sign.interpretant
    
    def coverage(self) -> Fraction:
        """Ratio of well-formed signs to total signs."""
        if not self.signs:
            return Fraction(1)
        well_formed = sum(1 for s in self.signs.values() if s.is_well_formed())
        return Fraction(well_formed, len(self.signs))


class SemioticEngine:
    """Engine for semiotic analysis of code and documentation."""
    
    def __init__(self):
        self.systems: Dict[str, SignSystem] = {}
        self._init_code_system()
        self._init_legal_system()
        self._init_mathematical_system()
    
    def _init_code_system(self) -> None:
        """Sign system for code conventions."""
        system = SignSystem(
            name="code_conventions",
            interpretive_community={"developer", "maintainer", "reviewer", "ai"}
        )
        
        # Common coding signs
        signs = [
            Sign("check_", "validation function", "function that verifies constraints", SignType.SYMBOL, "code"),
            Sign("assert", "runtime verification", "panic if condition false", SignType.SYMBOL, "code"),
            Sign("_", "private", "internal implementation detail", SignType.SYMBOL, "code"),
            Sign("D_", "domain prefix", "legal/governance domain", SignType.INDEX, "code"),
            Sign("Fraction", "exact arithmetic", "rational number, no float error", SignType.SYMBOL, "code"),
            Sign("->", "return type", "function output type", SignType.ICON, "code"),
            Sign("|", "union", "type A OR type B", SignType.ICON, "code"),
        ]
        
        for sign in signs:
            system.add_sign(sign)
        
        self.systems["code"] = system
    
    def _init_legal_system(self) -> None:
        """Sign system for legal terminology."""
        system = SignSystem(
            name="legal_notation",
            interpretive_community={"lawyer", "judge", "regulator", "compliance_officer"}
        )
        
        signs = [
            Sign("shall", "mandatory obligation", "required by law", SignType.SYMBOL, "legal"),
            Sign("may", "permissive right", "allowed but not required", SignType.SYMBOL, "legal"),
            Sign("S(n)", "successor function", "next state in sequence", SignType.SYMBOL, "legal"),
            Sign("GB-ORIGIN", "glass-box origin", "traceable enforcement point", SignType.SYMBOL, "legal"),
            Sign("PR #", "pull request", "proposed change under review", SignType.SYMBOL, "legal"),
        ]
        
        for sign in signs:
            system.add_sign(sign)
        
        self.systems["legal"] = system
    
    def _init_mathematical_system(self) -> None:
        """Sign system for mathematical notation."""
        system = SignSystem(
            name="mathematical_notation",
            interpretive_community={"mathematician", "formal_verifier", "type_theorist"}
        )
        
        signs = [
            Sign("⊢", "turnstile", "proves/entails", SignType.SYMBOL, "math"),
            Sign("∀", "universal quantifier", "for all", SignType.SYMBOL, "math"),
            Sign("∃", "existential quantifier", "there exists", SignType.SYMBOL, "math"),
            Sign("→", "implication", "if-then", SignType.ICON, "math"),
            Sign("⊣", "adjunction", "left adjoint", SignType.SYMBOL, "math"),
            Sign("ℕ", "natural numbers", "0, 1, 2, ...", SignType.SYMBOL, "math"),
        ]
        
        for sign in signs:
            system.add_sign(sign)
        
        self.systems["mathematical"] = system
    
    def analyze_code_symbol(self, symbol: str) -> Dict[str, Any]:
        """Analyze a code symbol semioticly."""
        result = {
            "symbol": symbol,
            "sign_type": None,
            "interpretations": {},
            "translation_needed": [],
        }
        
        # Check each system
        for system_name, system in self.systems.items():
            if symbol in system.signs:
                sign = system.signs[symbol]
                result["sign_type"] = sign.sign_type.name
                result["interpretations"][system_name] = sign.interpretant
            else:
                # Partial match
                for sig in system.signs.values():
                    if symbol.startswith(sig.signifier) or sig.signifier in symbol:
                        result["translation_needed"].append({
                            "system": system_name,
                            "related_sign": sig.signifier,
                            "meaning": sig.interpretant,
                        })
        
        return result
    
    def detect_boundary_crossings(self, text: str) -> List[Dict[str, Any]]:
        """Detect where multiple sign systems intersect in text."""
        crossings = []
        
        # Patterns that indicate boundary crossings
        patterns = {
            "legal_in_code": r"(shall|may|pursuant|hereinafter)",
            "math_in_code": r"(∀|∃|→|⊢|ℕ)",
            "code_in_legal": r"(check_|assert|def |class )",
        }
        
        import re
        for crossing_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                crossings.append({
                    "type": crossing_type,
                    "position": match.start(),
                    "matched": match.group(),
                    "context": text[max(0, match.start()-20):match.end()+20],
                })
        
        return crossings
    
    def generate_interpretation_guide(self, domain: str) -> str:
        """Generate a guide for interpreting signs in a domain."""
        system = self.systems.get(domain)
        if not system:
            return f"No sign system found for domain: {domain}"
        
        lines = [
            f"# Semiotic Guide: {system.name}",
            f"\nInterpretive Community: {', '.join(system.interpretive_community)}",
            f"Sign Coverage: {format_percent(system.coverage(), 1)}",
            "\n## Sign Inventory",
        ]
        
        for sign in sorted(system.signs.values(), key=lambda s: s.signifier):
            lines.append(f"\n### `{sign.signifier}` ({sign.sign_type.name})")
            lines.append(f"- Signified: {sign.signified}")
            lines.append(f"- Interpretant: {sign.interpretant}")
        
        return "\n".join(lines)
