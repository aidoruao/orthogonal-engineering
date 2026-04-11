#!/usr/bin/env python3
"""
Compiler Specification — Lexer, Parser, Type Checker, Codegen

Kingdom OS programs are compiled to an abstract machine.
This module specifies the compiler pipeline.

Biblical: Psalm 19:7 — "The law of the Lord is perfect, refreshing the soul."
  The compiler enforces the law of types — perfect and refreshing.
"""

from . import lexer_spec
from . import parser_spec
from . import type_checker
from . import codegen_spec

__all__ = ["lexer_spec", "parser_spec", "type_checker", "codegen_spec"]
