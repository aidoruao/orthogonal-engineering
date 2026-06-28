"""Fixture for formal structure scanner tests."""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Functor(Generic[T]):
    """A covariant functor mapping objects and morphisms between categories."""

    def fmap(self, morphism: T) -> T:
        return morphism


class Sheaf:
    """Sheaf of sections over a topological space with restriction maps."""

    def restrict(self, section: object, subset: object) -> object:
        return section


class ForcingPoset:
    """Forcing conditions ordered by a partial order."""

    def is_dense(self, subset: set) -> bool:
        return True


def generic_filter_realizes(condition: str) -> bool:
    """Check whether a generic filter realizes the forcing condition."""
    return True


# This assignment should not trigger because there is no corroboration.
monad_word = "just a string"
