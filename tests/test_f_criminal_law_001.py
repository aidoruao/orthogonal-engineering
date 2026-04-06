"""Falsification tests for D_CRIMINAL_LAW"""
from fractions import Fraction
from src.domains.d_criminal_law import CriminalLaw, OffenseClass, BurdenOfProof

def test_nullum_crimen():
    law = CriminalLaw()
    result = law.prosecute("D", "Unknown Crime", ["evidence"])
    assert result["verdict"] == "DISMISSED"

def test_burden_of_proof():
    law = CriminalLaw()
    law.define_offense("Theft", "PC § 484", OffenseClass.MISDEMEANOR, ["taking"], 1, Fraction(1000))
    result = law.prosecute("D", "Theft", ["weak"])
    assert result["verdict"] == "NOT GUILTY"

def test_conviction_with_evidence():
    law = CriminalLaw()
    law.define_offense("Assault", "PC § 240", OffenseClass.MISDEMEANOR, ["attempt"], 6, Fraction(1000))
    result = law.prosecute("D", "Assault", ["video", "witness", "physical"])
    assert result["verdict"] == "GUILTY"

def test_sentencing_range():
    law = CriminalLaw()
    law.define_offense("Theft", "PC § 484", OffenseClass.MISDEMEANOR, ["taking"], 1, Fraction(1000))
    result = law.sentence("D", "Theft", 5, Fraction(100), [], [])  # 5 years > 1 max
    assert "error" in result

if __name__ == "__main__":
    test_nullum_crimen()
    test_burden_of_proof()
    test_conviction_with_evidence()
    test_sentencing_range()
    print("All D_CRIMINAL_LAW tests: PASS")
