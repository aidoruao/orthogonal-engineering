"""Pattern: Deterministic Formula

Implements the requirement that calculations are reproducible.
same inputs → same outputs (Yeshua Axiom Y2).

Mathematical: ∀x, y: x = y → f(x) = f(y)

Used by: D_TAX_LAW, D_BANKRUPTCY, D_CHILD_WELFARE, D_ELECTION_LAW, D_SECURITIES_LAW
"""

from dataclasses import dataclass
from typing import Dict, Any, Callable, List
from fractions import Fraction
import hashlib
import json


@dataclass
class FormulaResult:
    """Result of a deterministic formula calculation."""
    inputs: Dict[str, Any]
    output: Any
    computation_hash: str
    
    def verify_determinism(self, other: "FormulaResult") -> bool:
        """Verify that same inputs produce same output."""
        return self.inputs == other.inputs and self.output == other.output


class DeterministicFormula:
    """
    Enforces determinism in calculations.
    
    All calculations must be reproducible: same inputs always
    produce same outputs. No randomness, no floating-point error.
    
    Attributes:
        formula_name: Name of the formula
        computation: The formula function
    """
    
    def __init__(self, formula_name: str, computation: Callable):
        self.formula_name = formula_name
        self.computation = computation
        self.execution_log: List[FormulaResult] = []
    
    def compute(self, inputs: Dict[str, Any]) -> FormulaResult:
        """
        Execute the formula with given inputs.
        
        Args:
            inputs: Input parameters
        
        Returns:
            FormulaResult with output and verification hash
        """
        # Compute result
        output = self.computation(inputs)
        
        # Create deterministic hash of computation
        computation_data = json.dumps({
            "formula": self.formula_name,
            "inputs": self._serialize_inputs(inputs),
            "output": self._serialize_output(output),
        }, sort_keys=True)
        computation_hash = hashlib.sha256(
            computation_data.encode()
        ).hexdigest()
        
        result = FormulaResult(
            inputs=inputs,
            output=output,
            computation_hash=computation_hash,
        )
        
        self.execution_log.append(result)
        return result
    
    def verify_reproducibility(
        self,
        inputs: Dict[str, Any],
        expected_output: Any,
    ) -> bool:
        """
        Verify that formula produces expected output for given inputs.
        
        Returns:
            True if computation is reproducible
        """
        result = self.compute(inputs)
        return result.output == expected_output
    
    def check_determinism(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check determinism across multiple test cases.
        
        Returns:
            Dict with determinism check results
        """
        results = []
        
        for inputs in test_cases:
            result = self.compute(inputs)
            # Run again to verify same result
            result2 = self.compute(inputs)
            
            is_deterministic = result.verify_determinism(result2)
            results.append({
                "inputs": inputs,
                "deterministic": is_deterministic,
                "hash": result.computation_hash,
            })
        
        all_deterministic = all(r["deterministic"] for r in results)
        
        return {
            "formula": self.formula_name,
            "deterministic": all_deterministic,
            "test_cases": len(test_cases),
            "passed": sum(1 for r in results if r["deterministic"]),
            "results": results,
        }
    
    def _serialize_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize inputs for hashing."""
        serialized = {}
        for k, v in inputs.items():
            if isinstance(v, Fraction):
                serialized[k] = {"fraction": [v.numerator, v.denominator]}
            else:
                serialized[k] = v
        return serialized
    
    def _serialize_output(self, output: Any) -> Any:
        """Serialize output for hashing."""
        if isinstance(output, Fraction):
            return {"fraction": [output.numerator, output.denominator]}
        return output
