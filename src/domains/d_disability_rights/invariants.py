#!/usr/bin/env python3
"""Disability Rights Invariants — ADA, WCAG compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ColorContrast, InteractiveElement, ADAAnalyzer, WCAGChecker,
    MIN_CONTRAST_RATIO_AA
)


def check_contrast_ratio(contrast: ColorContrast) -> Tuple[bool, ProofObject]:
    """WCAG 2.1 AA: Color contrast must be at least 4.5:1.

    Falsifies if: contrast.ratio() < MIN_CONTRAST_RATIO_AA.
    """
    ratio = contrast.ratio()
    
    if ratio < MIN_CONTRAST_RATIO_AA:
        return False, ProofObject(
            conclusion=f"VIOLATION: Contrast ratio {ratio} < {MIN_CONTRAST_RATIO_AA}",
            premises=[],
            rule="wcag_contrast_aa"
        )
    
    return True, ProofObject(
        conclusion=f"Contrast ratio adequate ({ratio} >= {MIN_CONTRAST_RATIO_AA})",
        premises=[],
        rule="wcag_contrast_aa"
    )


def check_interactive_accessibility(element: InteractiveElement) -> Tuple[bool, ProofObject]:
    """Interactive elements must be keyboard accessible and labeled.

    Falsifies if: keyboard access, screen reader label, or focus indicator is missing.
    """
    missing = []
    if not element.has_keyboard_access:
        missing.append("keyboard")
    if not element.has_screen_reader_label:
        missing.append("label")
    if not element.has_focus_indicator:
        missing.append("focus")
    
    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: Element missing accessibility: {missing}",
            premises=[],
            rule="wcag_interactive"
        )
    
    return True, ProofObject(
        conclusion="Interactive element accessible",
        premises=[],
        rule="wcag_interactive"
    )


def check_ada_accommodation(analyzer: ADAAnalyzer) -> Tuple[bool, ProofObject]:
    """ADA Title III: Public accommodations must be accessible.

    Falsifies if: site lacks accessibility and no reasonable accommodation (without undue hardship).
    """
    if not analyzer.physical_accessible and not analyzer.reasonable_accommodation_provided:
        if analyzer.undue_hardship_claimed:
            return True, ProofObject(
                conclusion="ADA accommodation waived (undue hardship)",
                premises=[],
                rule="ada_undue_hardship"
            )
        return False, ProofObject(
            conclusion="VIOLATION: ADA accommodation not provided",
            premises=[],
            rule="ada_accommodation"
        )
    
    return True, ProofObject(
        conclusion="ADA accommodation satisfied",
        premises=[],
        rule="ada_accommodation"
    )


def check_wcag_compliance(checker: WCAGChecker) -> Tuple[bool, ProofObject]:
    """WCAG 2.1 AA compliance check.

    Falsifies if: any element fails contrast AA or accessibility checks.
    """
    if not checker.all_contrast_aa():
        return False, ProofObject(
            conclusion="VIOLATION: Not all elements meet WCAG AA contrast",
            premises=[],
            rule="wcag_aa"
        )
    
    if not checker.all_elements_accessible():
        return False, ProofObject(
            conclusion="VIOLATION: Not all interactive elements accessible",
            premises=[],
            rule="wcag_aa"
        )
    
    return True, ProofObject(
        conclusion="WCAG 2.1 AA compliance satisfied",
        premises=[],
        rule="wcag_aa"
    )
