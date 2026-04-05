"""Synthetic Adjoint Logic (SAL) Type III kernel package."""

from src.sal.adjoint_triple import (
    AdjointTriple,
    AdjunctionProof,
    Functor,
    LeftAdjoint,
    MiddleFunctor,
    RightAdjoint,
    has_adjunction,
)

__all__ = [
    "Functor",
    "LeftAdjoint",
    "MiddleFunctor",
    "RightAdjoint",
    "AdjointTriple",
    "AdjunctionProof",
    "has_adjunction",
]
