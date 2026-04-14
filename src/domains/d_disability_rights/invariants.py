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
    falsifies_if: contrast.ratio() < MIN_CONTRAST_RATIO_AA.
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
    falsifies_if: keyboard access, screen reader label, or focus indicator is missing.
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
    falsifies_if: site lacks accessibility and no reasonable accommodation (without undue hardship).
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
    falsifies_if: any element fails contrast AA or accessibility checks.
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


def run_all_invariants() -> dict:
    """Run all D_DISABILITY_RIGHTS invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    ada_analyzer = ADAAnalyzer(
        facility_name="Sample DISABILI",
    )
    color_contrast = ColorContrast(
        foreground_luminance=Fraction(1),
        background_luminance=Fraction(1),
    )
    interactive_element = InteractiveElement(
        element_id="DISABILI-001",
    )
    wcag_checker = WCAGChecker(
        page_elements=[InteractiveElement(
        element_id="DISABILI-001",
    )],
        contrast_checks=[ColorContrast(
        foreground_luminance=Fraction(1),
        background_luminance=Fraction(1),
    )],
    )

    checks = [
        ("check_ada_accommodation", lambda: check_ada_accommodation(ada_analyzer)),
        ("check_contrast_ratio", lambda: check_contrast_ratio(color_contrast)),
        ("check_interactive_accessibility", lambda: check_interactive_accessibility(interactive_element)),
        ("check_wcag_compliance", lambda: check_wcag_compliance(wcag_checker)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DISABILITY_RIGHTS invariants: PASS")
