#!/usr/bin/env python3
"""
Lexer Specification — Tokenization of source code

Mathematical Foundation:
  - axioms/formal_languages.py (regular languages)
  - axioms/computability.py (decidability of lexing)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum, auto

from axioms.logic import ProofObject


class TokenType(Enum):
    """Token types for Kingdom OS programs."""
    # Literals
    INTEGER = auto()
    FLOAT = auto()  # Only for spec, runtime uses Fraction
    STRING = auto()
    BOOL = auto()
    
    # Keywords
    FN = auto()
    LET = auto()
    CONST = auto()
    TYPE = auto()
    CAP = auto()  # Capability keyword
    PROOF = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    MATCH = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LEQ = auto()
    GEQ = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    ARROW = auto()  # ->
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """A token in the source code."""
    token_type: TokenType
    value: str
    line: int
    column: int
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="Token",
            premises=[f"type={self.token_type.name}", f"line={self.line}"],
            conclusion="token valid"
        )


@dataclass
class Lexer:
    """Lexer for Kingdom OS programs."""
    source: str
    tokens: List[Token] = None
    pos: int = 0
    line: int = 1
    column: int = 1
    
    def __post_init__(self):
        if self.tokens is None:
            self.tokens = []
    
    def tokenize(self) -> Tuple[List[Token], ProofObject]:
        """Tokenize source code."""
        # Abstract tokenization
        # Would implement full lexer here
        
        return self.tokens, ProofObject(
            rule="Tokenize",
            premises=[f"source_len={len(self.source)}"],
            conclusion=f"tokens={len(self.tokens)}"
        )
