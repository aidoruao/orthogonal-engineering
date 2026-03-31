"""pcfe_kernel/departments/__init__.py — All built-in PCFE departments."""

from pcfe_kernel.departments.d_bio import D_BIO
from pcfe_kernel.departments.d_chem import D_CHEM
from pcfe_kernel.departments.d_fdacs import D_FDACS
from pcfe_kernel.departments.d_sense import D_SENSE
from pcfe_kernel.departments.d_train import D_TRAIN
from pcfe_kernel.department import DepartmentRegistry


def build_default_registry() -> DepartmentRegistry:
    """Return a DepartmentRegistry pre-loaded with all five built-in departments."""
    registry = DepartmentRegistry()
    for dept in (D_BIO, D_CHEM, D_FDACS, D_SENSE, D_TRAIN):
        registry.register(dept)
    return registry


__all__ = [
    "D_BIO",
    "D_CHEM",
    "D_FDACS",
    "D_SENSE",
    "D_TRAIN",
    "build_default_registry",
]
