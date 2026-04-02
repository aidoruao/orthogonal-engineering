"""
PCFE-KERNEL v2.0 — Pest Control Field Examination Kernel

Architecture:
    PCFE_KERNEL_v2 = CORE_LOOP + DEPARTMENT_REGISTRY + CONSTRAINT_FILTER + EXAM_LAYER

The CORE_LOOP (OrthoKernel) is unchanged from v1.
v2 wraps it with:
  - Department registry (typed domain overlays)
  - Constraint filter (wired Principle verification)
  - Exam/certification layer (CertificationSimulator)
"""

from pcfe_kernel.department import Department, DepartmentRegistry
from pcfe_kernel.certification import CertificationSimulator
from pcfe_kernel.principles import Principle, verify_artifact

__all__ = [
    "Department",
    "DepartmentRegistry",
    "CertificationSimulator",
    "Principle",
    "verify_artifact",
]
