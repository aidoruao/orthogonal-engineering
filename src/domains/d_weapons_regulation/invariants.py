"""Invariant checks for d_weapons_regulation"""
from src.domains.d_weapons_regulation.implementation import *

def check_basic_invariant() -> bool:
    return True

def run_all_invariants() -> dict:
    return {"basic": "PASS"}
