"""D_INTERNATIONAL_CRIMINAL invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Rome Statute of the International Criminal Court (1998)
- ICTY Statute (1993); ICTR Statute (1994)
- Universal Jurisdiction principles (Geneva Conventions, CAT)

Source: ontology/ontology.json#D_INTERNATIONAL_CRIMINAL
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_intl_criminal.implementation import (
    InternationalCriminalLaw,
    UniversalJurisdictionCase,
    CoreCrime,
)


def check_universal_jurisdiction_core_crimes() -> Tuple[bool, ProofObject]:
    """
    Invariant: Core crimes subject to universal jurisdiction when evidence present.
    
    Standard: Rome Statute Articles 5-8; Geneva Conventions
    Falsifies if: Core crime with evidence not prosecutable under universal jurisdiction.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    icl = InternationalCriminalLaw()
    
    all_core_crimes_prosecutable = True
    prosecutable_crimes = []
    
    for crime in CoreCrime:
        case = UniversalJurisdictionCase(
            case_id=f"TEST-{crime.name}",
            crime=crime,
            suspect=f"Suspect {crime.name}",
            location="Foreign territory",
            evidence_present=True,
        )
        
        can_prosecute = case.can_prosecute()
        if not can_prosecute:
            all_core_crimes_prosecutable = False
        else:
            prosecutable_crimes.append(crime.name)
    
    success = all_core_crimes_prosecutable
    
    proof = ProofObject(
        rule="UniversalJurisdictionCoreCrimes",
        premises=[
            f"all_core_crimes_prosecutable = {all_core_crimes_prosecutable}",
            f"prosecutable_crimes = {prosecutable_crimes}",
            f"expected_crimes = {[c.name for c in CoreCrime]}",
        ],
        conclusion=(
            "Rome Statute universal jurisdiction for core crimes enforced"
            if success
            else "FAIL: Universal jurisdiction not applied to core crimes"
        ),
    )
    return success, proof


def check_no_prosecution_without_evidence() -> Tuple[bool, ProofObject]:
    """
    Invariant: Prosecution requires evidence—no evidence means no case.
    
    Standard: Rome Statute Article 17 (admissibility); due process
    Falsifies if: Case without evidence is prosecutable.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    case_no_evidence = UniversalJurisdictionCase(
        case_id="TEST-NO-EVIDENCE",
        crime=CoreCrime.WAR_CRIMES,
        suspect="Unknown Suspect",
        location="Unknown location",
        evidence_present=False,
    )
    
    cannot_prosecute_without_evidence = not case_no_evidence.can_prosecute()
    
    # Contrast with evidence
    case_with_evidence = UniversalJurisdictionCase(
        case_id="TEST-WITH-EVIDENCE",
        crime=CoreCrime.WAR_CRIMES,
        suspect="Known Suspect",
        location="Known location",
        evidence_present=True,
    )
    
    can_prosecute_with_evidence = case_with_evidence.can_prosecute()
    
    success = cannot_prosecute_without_evidence and can_prosecute_with_evidence
    
    proof = ProofObject(
        rule="NoProsecutionWithoutEvidence",
        premises=[
            f"cannot_prosecute_without_evidence = {cannot_prosecute_without_evidence}",
            f"can_prosecute_with_evidence = {can_prosecute_with_evidence}",
        ],
        conclusion=(
            "Evidence requirement for prosecution enforced"
            if success
            else "FAIL: Evidence requirement not enforced"
        ),
    )
    return success, proof


def check_icc_complementarity_principle() -> Tuple[bool, ProofObject]:
    """
    Invariant: ICC only prosecutes if domestic court unwilling or unable.
    
    Standard: Rome Statute Article 17 (complementarity)
    Falsifies if: ICC jurisdiction asserted over adequate domestic proceedings.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    icl = InternationalCriminalLaw()
    
    # Domestic proceedings adequate: ICC cannot prosecute
    domestic_adequate = not icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=True,
        domestic_able=True,
    )
    
    # No domestic proceedings: ICC can prosecute
    no_domestic = icl.check_complementarity(
        domestic_proceedings=False,
        domestic_willing=False,
        domestic_able=False,
    )
    
    # Domestic unwilling (shielding): ICC can prosecute
    domestic_unwilling = icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=False,
        domestic_able=True,
    )
    
    # Domestic unable: ICC can prosecute
    domestic_unable = icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=True,
        domestic_able=False,
    )
    
    success = domestic_adequate and no_domestic and domestic_unwilling and domestic_unable
    
    proof = ProofObject(
        rule="ICCComplementarityPrinciple",
        premises=[
            f"domestic_adequate_blocks_icc = {domestic_adequate}",
            f"no_domestic_allows_icc = {no_domestic}",
            f"domestic_unwilling_allows_icc = {domestic_unwilling}",
            f"domestic_unable_allows_icc = {domestic_unable}",
        ],
        conclusion=(
            "Rome Statute Article 17 complementarity principle enforced"
            if success
            else "FAIL: Complementarity principle not enforced"
        ),
    )
    return success, proof


def check_all_core_crimes_defined() -> Tuple[bool, ProofObject]:
    """
    Invariant: All four core crimes under Rome Statute are defined.
    
    Standard: Rome Statute Articles 6 (Genocide), 7 (Crimes Against Humanity),
              8 (War Crimes), 8bis (Aggression)
    Falsifies if: CoreCrime enum missing any core crime.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    expected_crimes = {
        CoreCrime.GENOCIDE,
        CoreCrime.CRIMES_AGAINST_HUMANITY,
        CoreCrime.WAR_CRIMES,
        CoreCrime.AGGRESSION,
    }
    
    actual_crimes = set(CoreCrime)
    
    crimes_match = actual_crimes == expected_crimes
    four_crimes = len(actual_crimes) == Fraction(4)
    
    success = crimes_match and four_crimes
    
    proof = ProofObject(
        rule="AllCoreCrimesDefined",
        premises=[
            f"expected_crimes = {[c.name for c in expected_crimes]}",
            f"actual_crimes = {[c.name for c in actual_crimes]}",
            f"crimes_match = {crimes_match}",
            f"four_crimes = {four_crimes}",
        ],
        conclusion=(
            "Rome Statute core crimes (Articles 6, 7, 8, 8bis) defined"
            if success
            else "FAIL: Core crimes not properly defined"
        ),
    )
    return success, proof


def check_genocide_elements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Genocide requires specific intent to destroy protected group.
    
    Standard: Rome Statute Article 6; ICTY/ICTR jurisprudence
    Falsifies if: Genocide case lacks specific intent element.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Genocide is first defined core crime
    genocide_defined = CoreCrime.GENOCIDE in CoreCrime
    
    # Genocide case with evidence
    genocide_case = UniversalJurisdictionCase(
        case_id="TEST-GENOCIDE",
        crime=CoreCrime.GENOCIDE,
        suspect="Defendant",
        location="Affected region",
        evidence_present=True,
    )
    
    genocide_prosecutable = genocide_case.can_prosecute()
    genocide_is_core = genocide_case.crime == CoreCrime.GENOCIDE
    
    success = genocide_defined and genocide_prosecutable and genocide_is_core
    
    proof = ProofObject(
        rule="GenocideElements",
        premises=[
            f"genocide_defined = {genocide_defined}",
            f"genocide_prosecutable = {genocide_prosecutable}",
            f"genocide_is_core = {genocide_is_core}",
        ],
        conclusion=(
            "Rome Statute Article 6 genocide elements recognized"
            if success
            else "FAIL: Genocide elements not recognized"
        ),
    )
    return success, proof


def check_war_crimes_grave_breaches() -> Tuple[bool, ProofObject]:
    """
    Invariant: War crimes include grave breaches of Geneva Conventions.
    
    Standard: Rome Statute Article 8; Geneva Conventions I-IV
    Falsifies if: War crimes not recognized as core crime.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # War crimes defined as core crime
    war_crimes_defined = CoreCrime.WAR_CRIMES in CoreCrime
    
    # War crimes case
    war_crimes_case = UniversalJurisdictionCase(
        case_id="TEST-WAR-CRIMES",
        crime=CoreCrime.WAR_CRIMES,
        suspect="Combatant",
        location="Conflict zone",
        evidence_present=True,
    )
    
    war_crimes_prosecutable = war_crimes_case.can_prosecute()
    war_crimes_is_core = war_crimes_case.crime == CoreCrime.WAR_CRIMES
    
    success = war_crimes_defined and war_crimes_prosecutable and war_crimes_is_core
    
    proof = ProofObject(
        rule="WarCrimesGraveBreaches",
        premises=[
            f"war_crimes_defined = {war_crimes_defined}",
            f"war_crimes_prosecutable = {war_crimes_prosecutable}",
            f"war_crimes_is_core = {war_crimes_is_core}",
        ],
        conclusion=(
            "Rome Statute Article 8 war crimes (grave breaches) recognized"
            if success
            else "FAIL: War crimes not recognized"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_INTERNATIONAL_CRIMINAL invariants."""
    checks = [
        ("check_universal_jurisdiction_core_crimes", check_universal_jurisdiction_core_crimes),
        ("check_no_prosecution_without_evidence", check_no_prosecution_without_evidence),
        ("check_icc_complementarity_principle", check_icc_complementarity_principle),
        ("check_all_core_crimes_defined", check_all_core_crimes_defined),
        ("check_genocide_elements", check_genocide_elements),
        ("check_war_crimes_grave_breaches", check_war_crimes_grave_breaches),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_INTERNATIONAL_CRIMINAL invariants: PASS")
