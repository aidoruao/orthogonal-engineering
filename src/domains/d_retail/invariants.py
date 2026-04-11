"""D_RETAIL Invariants — Consumer Product Safety, PCI DSS, Retail Compliance

Verifies CPSC product safety, PCI DSS payment security,
retail store safety inspections, consumer protection.

Standards: 15 U.S.C. § 2051 (CPSA), PCI DSS 4.0, State fire codes
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import RetailProduct, RetailStore, RecallStatus, min_profit_margin, max_return_rate


def check_cpsc_product_safety(product: RetailProduct) -> Tuple[bool, ProofObject]:
    """
    Consumer Product Safety Commission requires compliance.
    
    15 U.S.C. § 2058:
    - Products must meet safety standards
    - Recalls for hazardous products
    - Testing and certification required
    
    Falsifies if: active recall or non-compliant
    
    
    falsifies_if: condition_evaluated_to_false"""
    if product.recall_status == RecallStatus.MANDATORY_RECALL:
        return False, ProofObject(
            conclusion=f"VIOLATION: Product {product.sku} under mandatory CPSC recall",
            premises=[
                f"Product: {product.product_id}",
                f"Recall status: {product.recall_status.name}",
                "15 U.S.C. § 2058 — Product recalls"
            ],
            rule="cpsc_product_safety"
        )
    
    if not product.cpsc_compliant:
        return False, ProofObject(
            conclusion=f"VIOLATION: Product {product.sku} not CPSC compliant",
            premises=[
                f"CPSC compliant: {product.cpsc_compliant}",
                f"Safety testing: {product.safety_testing_complete}",
                "CPSA Section 14 — Testing and certification"
            ],
            rule="cpsc_product_safety"
        )
    
    return True, ProofObject(
        conclusion=f"Product {product.sku} CPSC compliance verified",
        premises=["CPSC compliant: YES"],
        rule="cpsc_product_safety"
    )


def check_pci_compliance(store: RetailStore) -> Tuple[bool, ProofObject]:
    """
    PCI DSS required for payment card processing.
    
    PCI DSS 4.0:
    - Annual compliance validation
    - Security controls required
    - Breach notification mandatory
    
    Falsifies if: not PCI compliant and processing cards
    
    
    falsifies_if: condition_evaluated_to_false"""
    if store.data_breaches_annual > 0 and store.pci_compliant:
        return False, ProofObject(
            conclusion=f"VIOLATION: Store {store.store_id} PCI compliant but had {store.data_breaches_annual} breaches",
            premises=[
                f"Breaches: {store.data_breaches_annual}",
                f"PCI compliant: {store.pci_compliant}",
                "PCI DSS — Breach indicates compliance failure"
            ],
            rule="pci_compliance"
        )
    
    if not store.pci_compliant:
        return False, ProofObject(
            conclusion=f"VIOLATION: Store {store.store_id} not PCI DSS compliant",
            premises=[
                f"PCI compliant: {store.pci_compliant}",
                f"Last audit: {store.last_pci_audit}",
                "PCI DSS 4.0 — Compliance required"
            ],
            rule="pci_compliance"
        )
    
    return True, ProofObject(
        conclusion=f"Store {store.store_id} PCI DSS compliance verified",
        premises=[f"Last audit: {store.last_pci_audit}"],
        rule="pci_compliance"
    )


def check_store_safety_inspection(store: RetailStore) -> Tuple[bool, ProofObject]:
    """
    Retail stores require regular safety inspections.
    
    OSHA and state requirements:
    - Fire safety inspections
    - Building code compliance
    - ADA accessibility
    
    Falsifies if: failed fire inspection or major violations
    
    
    falsifies_if: condition_evaluated_to_false"""
    if not store.fire_inspection_passed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Store {store.store_id} failed fire safety inspection",
            premises=[
                f"Fire inspection: FAILED",
                f"Safety violations: {store.safety_violations}",
                "NFPA / State fire codes"
            ],
            rule="retail_safety_inspection"
        )
    
    if store.safety_violations > 5:
        return False, ProofObject(
            conclusion=f"VIOLATION: Store {store.store_id} has {store.safety_violations} safety violations",
            premises=[
                f"Violations: {store.safety_violations}",
                "OSHA retail safety standards"
            ],
            rule="retail_safety_inspection"
        )
    
    return True, ProofObject(
        conclusion=f"Store {store.store_id} safety inspection satisfactory",
        premises=[
            f"Fire inspection: PASSED",
            f"Violations: {store.safety_violations}"
        ],
        rule="retail_safety_inspection"
    )


def check_return_rate_reasonable(store: RetailStore) -> Tuple[bool, ProofObject]:
    """
    Excessive return rates indicate product quality or fraud issues.
    
    Retail best practices:
    - Return rates should be monitored
    - High rates trigger investigation
    - Fraud prevention required
    
    Falsifies if: return rate > 20%
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_rate = max_return_rate()
    rate = store.get_return_rate()
    
    if rate > max_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Store {store.store_id} return rate {rate} exceeds maximum {max_rate}",
            premises=[
                f"Returns: {store.returns_annual}",
                f"Sales: {store.sales_annual}",
                f"Rate: {rate}",
                "Retail fraud/quality standards"
            ],
            rule="retail_return_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Store {store.store_id} return rate acceptable",
        premises=[f"Return rate: {rate}"],
        rule="retail_return_rate"
    )


def check_product_profitability(product: RetailProduct) -> Tuple[bool, ProofObject]:
    """
    Products should maintain minimum profitability.
    
    Retail economics:
    - Loss leaders limited
    - Margin required for sustainability
    - Below-cost pricing regulations (some jurisdictions)
    
    Falsifies if: margin < 10% (sustainability concern)
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_margin = min_profit_margin()
    margin = product.get_margin()
    
    if margin < min_margin:
        return False, ProofObject(
            conclusion=f"VIOLATION: Product {product.sku} margin {margin} below minimum {min_margin}",
            premises=[
                f"Price: {product.base_price}",
                f"Cost: {product.cost}",
                f"Margin: {margin}",
                "Retail sustainability standards"
            ],
            rule="retail_profitability"
        )
    
    return True, ProofObject(
        conclusion=f"Product {product.sku} profitability acceptable",
        premises=[f"Margin: {margin}"],
        rule="retail_profitability"
    )
