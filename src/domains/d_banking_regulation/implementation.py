"""D_BANKING_REGULATION implementation — Banking Regulation

Implements banking regulation under Dodd-Frank, FDIC insurance,
Basel capital requirements, and usury limitations.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Dodd-Frank Act, FDIA (12 U.S.C. §1811), Basel Accords, 12 CFR

Biblical: Exodus 22:25 — "If you lend money to one of my people among
you who is needy, do not treat it like a business deal; charge no interest."
Also: Deuteronomy 23:19-20 — limits on interest to fellow Israelites.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class AssetClass(Enum):
    """Risk weight categories for capital adequacy."""
    CASH_AND_GOLD = auto()           # 0% risk weight
    SOVEREIGN_DEBT_OECD = auto()     # 0% risk weight
    SOVEREIGN_DEBT_NON_OECD = auto() # Variable
    MUNICIPAL_BONDS = auto()         # 20% risk weight
    MORTGAGES_RESIDENTIAL = auto()   # 50% risk weight
    CORPORATE_LOANS = auto()         # 100% risk weight
    PAST_DUE_LOANS = auto()          # 150% risk weight
    COMMERCIAL_REAL_ESTATE = auto()  # 100% risk weight


class LoanType(Enum):
    """Types of loans for compliance checking."""
    RESIDENTIAL_MORTGAGE = auto()
    COMMERCIAL_REAL_ESTATE = auto()
    CONSUMER_INSTALLMENT = auto()
    CREDIT_CARD = auto()
    AUTO_LOAN = auto()
    STUDENT_LOAN = auto()
    SMALL_BUSINESS = auto()
    PAYDAY = auto()


@dataclass
class Bank:
    """A regulated banking institution."""
    bank_id: str
    bank_name: str
    charter_type: str  # "national", "state", "federal_savings"
    
    # Capital (Tier 1 = core capital, Tier 2 = supplementary)
    tier1_capital: Fraction
    tier2_capital: Fraction
    
    # Assets
    total_assets: Fraction
    
    # Deposits
    total_deposits: Fraction
    insured_deposits: Fraction
    
    # Reserves
    vault_cash: Fraction
    reserves_at_fed: Fraction
    
    # Optional: calculated from total_assets if not provided
    risk_weighted_assets: Optional[Fraction] = None
    
    def __post_init__(self):
        """Calculate total capital."""
        if self.risk_weighted_assets is None:
            # Simplified: assume 75% of total assets are risk-weighted
            self.risk_weighted_assets = self.total_assets * Fraction(75, 100)
    
    @property
    def total_capital(self) -> Fraction:
        """Total regulatory capital."""
        return self.tier1_capital + self.tier2_capital
    
    @property
    def tier1_ratio(self) -> Fraction:
        """Tier 1 capital ratio."""
        if self.risk_weighted_assets == 0:
            return Fraction(0)
        return self.tier1_capital / self.risk_weighted_assets
    
    @property
    def total_capital_ratio(self) -> Fraction:
        """Total capital ratio."""
        if self.risk_weighted_assets == 0:
            return Fraction(0)
        return self.total_capital / self.risk_weighted_assets
    
    @property
    def leverage_ratio(self) -> Fraction:
        """Tier 1 leverage ratio."""
        if self.total_assets == 0:
            return Fraction(0)
        return self.tier1_capital / self.total_assets
    
    @property
    def total_reserves(self) -> Fraction:
        """Total reserve holdings."""
        return self.vault_cash + self.reserves_at_fed


@dataclass
class Loan:
    """A loan for compliance analysis."""
    loan_id: str
    borrower_name: str
    loan_type: LoanType
    principal: Fraction
    interest_rate: Fraction  # Annual rate as fraction (e.g., 5/100 = 5%)
    term_months: int
    
    # Risk assessment
    credit_score: Optional[int] = None
    debt_to_income: Optional[Fraction] = None
    loan_to_value: Optional[Fraction] = None
    
    # Compliance
    documented_income: bool = False
    ability_to_repay_verified: bool = False
    
    @property
    def annual_interest(self) -> Fraction:
        """Annual interest amount."""
        return self.principal * self.interest_rate
    
    @property
    def is_high_cost(self) -> bool:
        """Check if loan is high-cost under HOEPA."""
        # Simplified: APR > 8% above average prime
        return self.interest_rate > Fraction(15, 100)  # Threshold


class CapitalAdequacyCalculator:
    """Calculator for Basel capital adequacy requirements.
    
    Basel III requirements:
    - Minimum Tier 1 ratio: 6%
    - Minimum Total capital ratio: 8%
    - Conservation buffer: 2.5%
    - Countercyclical buffer: 0-2.5%
    """
    
    # Minimum requirements (as fractions)
    MIN_TIER1_RATIO = Fraction(6, 100)
    MIN_TOTAL_CAPITAL_RATIO = Fraction(8, 100)
    MIN_LEVERAGE_RATIO = Fraction(4, 100)  # Tier 1 / Total assets
    
    # Buffer requirements
    CAPITAL_CONSERVATION_BUFFER = Fraction(25, 1000)  # 2.5%
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def calculate_capital_ratios(self, bank: Bank) -> Dict:
        """Calculate all capital ratios for a bank."""
        return {
            "tier1_ratio": bank.tier1_ratio,
            "total_capital_ratio": bank.total_capital_ratio,
            "leverage_ratio": bank.leverage_ratio,
            "tier1_amount": bank.tier1_capital,
            "total_capital": bank.total_capital,
            "rwa": bank.risk_weighted_assets,
        }
    
    def check_capital_adequacy(self, bank: Bank) -> Dict:
        """Check if bank meets capital adequacy requirements.
        
        Returns:
            Compliance assessment
        """
        issues = []
        
        # Check Tier 1 ratio
        if bank.tier1_ratio < self.MIN_TIER1_RATIO:
            shortfall = self.MIN_TIER1_RATIO - bank.tier1_ratio
            issues.append({
                "type": "TIER1_RATIO",
                "current": bank.tier1_ratio,
                "required": self.MIN_TIER1_RATIO,
                "shortfall": shortfall,
            })
        
        # Check total capital ratio
        if bank.total_capital_ratio < self.MIN_TOTAL_CAPITAL_RATIO:
            shortfall = self.MIN_TOTAL_CAPITAL_RATIO - bank.total_capital_ratio
            issues.append({
                "type": "TOTAL_CAPITAL_RATIO",
                "current": bank.total_capital_ratio,
                "required": self.MIN_TOTAL_CAPITAL_RATIO,
                "shortfall": shortfall,
            })
        
        # Check leverage ratio
        if bank.leverage_ratio < self.MIN_LEVERAGE_RATIO:
            shortfall = self.MIN_LEVERAGE_RATIO - bank.leverage_ratio
            issues.append({
                "type": "LEVERAGE_RATIO",
                "current": bank.leverage_ratio,
                "required": self.MIN_LEVERAGE_RATIO,
                "shortfall": shortfall,
            })
        
        # Well capitalized standards (higher than minimum)
        well_capitalized = (
            bank.tier1_ratio >= Fraction(6, 100) and
            bank.total_capital_ratio >= Fraction(10, 100) and
            bank.leverage_ratio >= Fraction(5, 100)
        )
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "well_capitalized": well_capitalized,
            "prompt_corrective_action": self._determine_pca(bank, issues),
        }
    
    def _determine_pca(self, bank: Bank, issues: List[Dict]) -> str:
        """Determine Prompt Corrective Action category.
        
        Categories: Well capitalized, Adequately capitalized,
        Undercapitalized, Significantly undercapitalized,
        Critically undercapitalized
        """
        if bank.total_capital_ratio < Fraction(2, 100):
            return "CRITICALLY_UNDERCAPITALIZED"
        elif bank.total_capital_ratio < Fraction(4, 100):
            return "SIGNIFICANTLY_UNDERCAPITALIZED"
        elif bank.total_capital_ratio < self.MIN_TOTAL_CAPITAL_RATIO:
            return "UNDERCAPITALIZED"
        elif len(issues) == 0:
            return "ADEQUATELY_CAPITALIZED"
        else:
            return "ADEQUATELY_CAPITALIZED"


class FDICInsuranceCalculator:
    """Calculator for FDIC deposit insurance.
    
    Standard coverage: $250,000 per depositor, per institution,
    per ownership category.
    """
    
    STANDARD_COVERAGE = Fraction(250_000)
    
    def __init__(self):
        self.coverage_map: Dict[str, Fraction] = {}
    
    def calculate_insurance_coverage(
        self,
        deposit_amount: Fraction,
        account_ownership: str = "single",
    ) -> Dict:
        """Calculate FDIC insurance coverage.
        
        Args:
            deposit_amount: Total deposits at institution
            account_ownership: "single", "joint", "revocable_trust", etc.
            
        Returns:
            Coverage analysis
        """
        # Different ownership categories have different limits
        ownership_limits = {
            "single": self.STANDARD_COVERAGE,
            "joint": self.STANDARD_COVERAGE * 2,  # Each co-owner
            "revocable_trust": self.STANDARD_COVERAGE * 5,  # Per beneficiary
            "ira": self.STANDARD_COVERAGE,
            "corporation": self.STANDARD_COVERAGE,
        }
        
        limit = ownership_limits.get(account_ownership, self.STANDARD_COVERAGE)
        
        insured = min(deposit_amount, limit)
        uninsured = max(deposit_amount - limit, Fraction(0))
        
        return {
            "deposit_amount": deposit_amount,
            "insured_amount": insured,
            "uninsured_amount": uninsured,
            "coverage_limit": limit,
            "ownership_category": account_ownership,
            "fully_insured": uninsured == 0,
        }
    
    def check_bank_insurance_fund(self, bank: Bank, fund_balance: Fraction) -> Dict:
        """Check if bank's deposit insurance fund is adequate.
        
        DIF reserve ratio should be at least 1.35%.
        """
        if bank.insured_deposits == 0:
            return {"reserve_ratio": Fraction(0), "adequate": True}
        
        reserve_ratio = fund_balance / bank.insured_deposits
        adequate = reserve_ratio >= Fraction(135, 10000)  # 1.35%
        
        return {
            "reserve_ratio": reserve_ratio,
            "adequate": adequate,
            "fund_balance": fund_balance,
            "insured_deposits": bank.insured_deposits,
        }


class LendingComplianceChecker:
    """Checker for lending compliance including usury and ATR."""
    
    # State usury limits (simplified - highest and lowest examples)
    USURY_LIMITS = {
        "california": Fraction(10, 100),      # 10% for non-exempt lenders
        "texas": Fraction(10, 100),           # Varies by loan type
        "new_york": Fraction(16, 100),        # Civil usury
        "delaware": Fraction(0),              # No limit for corporations
        "federal": Fraction(0),               # National banks export rates
    }
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def check_usury_compliance(
        self,
        loan: Loan,
        jurisdiction: str = "california",
    ) -> Dict:
        """Check if loan complies with usury limits.
        
        Args:
            loan: The loan to check
            jurisdiction: State jurisdiction
            
        Returns:
            Usury compliance analysis
        """
        limit = self.USURY_LIMITS.get(jurisdiction.lower(), Fraction(100))
        
        if limit == 0:
            # No usury limit (e.g., Delaware corporations)
            return {
                "compliant": True,
                "usury_limit": None,
                "interest_rate": loan.interest_rate,
                "jurisdiction": jurisdiction,
            }
        
        compliant = loan.interest_rate <= limit
        
        return {
            "compliant": compliant,
            "usury_limit": limit,
            "interest_rate": loan.interest_rate,
            "excess": max(loan.interest_rate - limit, Fraction(0)) if not compliant else Fraction(0),
            "jurisdiction": jurisdiction,
        }
    
    def check_ability_to_repay(self, loan: Loan) -> Dict:
        """Check Ability-to-Repay (ATR) compliance under TILA/Reg Z.
        
        ATR requires lenders to verify borrower's ability to repay
        considering: income/assets, employment, monthly payment, debts,
        credit history, etc.
        """
        issues = []
        
        if not loan.documented_income:
            issues.append("Income not documented")
        
        if not loan.ability_to_repay_verified:
            issues.append("Ability to repay not verified")
        
        if loan.debt_to_income and loan.debt_to_income > Fraction(43, 100):
            issues.append("Debt-to-income exceeds 43%")
        
        # Credit score check
        if loan.credit_score and loan.credit_score < 620:
            issues.append("Subprime credit score")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "qualified_mortgage": len(issues) == 0 and loan.debt_to_income and loan.debt_to_income <= Fraction(43, 100),
        }
    
    def check_lending_standards(self, loans: List[Loan]) -> Dict:
        """Check overall lending standards compliance."""
        total_loans = len(loans)
        
        subprime_count = sum(1 for l in loans if l.credit_score and l.credit_score < 620)
        high_cost_count = sum(1 for l in loans if l.is_high_cost)
        
        subprime_ratio = Fraction(subprime_count, total_loans) if total_loans > 0 else Fraction(0)
        high_cost_ratio = Fraction(high_cost_count, total_loans) if total_loans > 0 else Fraction(0)
        
        issues = []
        if subprime_ratio > Fraction(20, 100):
            issues.append(f"High subprime concentration: {subprime_ratio * 100}%")
        if high_cost_ratio > Fraction(10, 100):
            issues.append(f"High high-cost concentration: {high_cost_ratio * 100}%")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "subprime_ratio": subprime_ratio,
            "high_cost_ratio": high_cost_ratio,
        }


class BankExaminer:
    """Comprehensive bank examiner for regulatory compliance."""
    
    def __init__(self):
        self.capital_calculator = CapitalAdequacyCalculator()
        self.fdic_calculator = FDICInsuranceCalculator()
        self.lending_checker = LendingComplianceChecker()
    
    def conduct_examination(self, bank: Bank, loan_portfolio: List[Loan]) -> Dict:
        """Conduct comprehensive bank examination.
        
        Returns:
            Examination report
        """
        capital = self.capital_calculator.check_capital_adequacy(bank)
        lending = self.lending_checker.check_lending_standards(loan_portfolio)
        
        # Calculate reserve ratio
        reserves_ratio = bank.total_reserves / bank.total_deposits if bank.total_deposits > 0 else Fraction(0)
        
        all_issues = []
        all_issues.extend(capital.get("issues", []))
        all_issues.extend(lending.get("issues", []))
        
        return {
            "bank_id": bank.bank_id,
            "examination_date": "2024-01-01",  # Simplified
            "capital_adequacy": capital,
            "lending_standards": lending,
            "reserves_ratio": reserves_ratio,
            "compliant": len(all_issues) == 0,
            "issues": all_issues,
            "rating": self._assign_rating(capital, lending),
        }
    
    def _assign_rating(self, capital: Dict, lending: Dict) -> str:
        """Assign CAMELS-style rating."""
        if not capital.get("compliant", True):
            return "4"  # Problem bank
        if not lending.get("compliant", True):
            return "3"  # Fair
        return "2"  # Satisfactory


# Convenience functions
def check_capital_ratio_minimum(
    tier1_capital: float,
    risk_weighted_assets: float,
) -> Dict:
    """Quick check if capital ratio meets minimum.
    
    Usage:
        result = check_capital_ratio_minimum(100_000_000, 1_000_000_000)
        print(f"Compliant: {result['compliant']}")
    """
    ratio = Fraction(int(tier1_capital * 100), int(risk_weighted_assets * 100))
    required = Fraction(6, 100)
    
    return {
        "tier1_ratio": ratio,
        "required": required,
        "compliant": ratio >= required,
    }


def check_fdic_coverage_limits(deposit_amount: float) -> Dict:
    """Check FDIC coverage for deposit amount."""
    calc = FDICInsuranceCalculator()
    return calc.calculate_insurance_coverage(Fraction(int(deposit_amount * 100), 100))


def check_usury_caps(interest_rate: float, state: str = "california") -> Dict:
    """Check if interest rate complies with state usury law."""
    checker = LendingComplianceChecker()
    loan = Loan(
        loan_id="L001",
        borrower_name="Test",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10000),
        interest_rate=Fraction(int(interest_rate * 100), 100),
        term_months=36,
    )
    return checker.check_usury_compliance(loan, state)


def check_reserve_requirements(total_deposits: float, vault_cash: float) -> Dict:
    """Check if bank meets reserve requirements."""
    # Simplified: Assume 10% reserve requirement
    required_ratio = Fraction(10, 100)
    deposits = Fraction(int(total_deposits * 100), 100)
    reserves = Fraction(int(vault_cash * 100), 100)
    
    actual_ratio = reserves / deposits if deposits > 0 else Fraction(0)
    
    return {
        "required_ratio": required_ratio,
        "actual_ratio": actual_ratio,
        "compliant": actual_ratio >= required_ratio,
        "shortfall": max(required_ratio * deposits - reserves, Fraction(0)),
    }


# ---------------------------------------------------------------------------
# Frozen dataclasses for invariant checks
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BankCapitalReport:
    """Capital adequacy report for Basel III compliance (12 CFR 3, Basel III)."""

    bank_id: str
    tier1_capital: Fraction
    tier2_capital: Fraction
    total_rwa: Fraction
    min_tier1_ratio: Fraction
    min_total_ratio: Fraction


@dataclass(frozen=True)
class LoanApplicationReport:
    """Loan application compliance record (TRID, HMDA, usury statutes)."""

    loan_id: str
    loan_type: str
    interest_rate_pct: Fraction
    state_usury_limit_pct: Fraction
    borrower_ability_to_repay: bool
    trid_disclosure_provided: bool
    hmda_reported: bool
