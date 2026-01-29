"""
GOVERNANCE DEMONSTRATION - PROPER AI WORKFLOW
==============================================

Demonstrates correct usage of MSGCP (Maximal Strict Corporate Governance Python)
for AI code generation.

MANDATE: All AI-generated code MUST pass through GovernancePipeline.enforce()
"""

from typing import List, Tuple

from governance import GovernancePipeline, GovernanceReport, PermittedCodeTemplates


class AICodeGenerator:
    """
    AI code generator constrained by governance.

    RULES:
    1. Generate code using only PermittedCodeTemplates
    2. Pass ALL code through GovernancePipeline.enforce()
    3. If report.action == "REJECT": discard and return error
    4. If report.action == "COMMIT": proceed with code
    """

    def __init__(self):
        self.pipeline = GovernancePipeline()

    def generate_bounded_function(
        self, name: str, input_type: str, output_type: str, max_iterations: int = 100
    ) -> Tuple[str, GovernanceReport]:
        """
        Generate governance-compliant function.

        Returns: (code, report)
        If report.passed == False: code contains rejection markers
        """
        # Use only permitted template
        code = PermittedCodeTemplates.bounded_function(
            name=name,
            input_type=input_type,
            output_type=output_type,
            max_iterations=max_iterations,
        )

        # Fill template with actual logic (must remain compliant)
        if name == "sum_integers":
            code = self._implement_sum_integers(code)
        elif name == "count_elements":
            code = self._implement_count_elements(code)

        # ENFORCE GOVERNANCE - MANDATORY STEP
        report = self.pipeline.enforce(code, f"{name}.py")

        return code, report

    def _implement_sum_integers(self, template: str) -> str:
        """Implement sum function within governance constraints"""
        implementation = '''
def sum_integers(x: Tuple[int, ...]) -> int:
    """Returns sum of integers. Bounded by 100 iterations."""
    if not isinstance(x, Tuple[int, ...]):
        raise TypeError("Input must be tuple of integers")

    total: int = 0
    bound = min(len(x), 100)  # Explicit bound

    for i in range(bound):
        total = total + x[i]

    return total
'''
        return implementation

    def _implement_count_elements(self, template: str) -> str:
        """Implement count function within governance constraints"""
        implementation = '''
def count_elements(x: List[str]) -> int:
    """Returns count of elements. Bounded by 1000 elements."""
    if len(x) > 1000:
        raise ValueError("Input exceeds maximum size 1000")

    count: int = 0
    for _ in x:
        count = count + 1
        if count > 1000:  # Safety bound
            break

    return count
'''
        return implementation

    def generate_test_case(
        self, function_name: str, input_val: str, expected_output: str
    ) -> Tuple[str, GovernanceReport]:
        """
        Generate governance-compliant test case.
        """
        code = PermittedCodeTemplates.test_case(
            function_name=function_name,
            input_val=input_val,
            expected_output=expected_output,
        )

        report = self.pipeline.enforce(code, f"test_{function_name}.py")

        return code, report


def demonstrate_governance_workflow():
    """
    DEMONSTRATION: Correct AI workflow with governance enforcement
    """
    print("=" * 70)
    print("GOVERNANCE DEMONSTRATION - PROPER AI WORKFLOW")
    print("=" * 70)

    ai = AICodeGenerator()

    # Example 1: Generate compliant function
    print("\n1. GENERATING COMPLIANT FUNCTION")
    print("-" * 40)

    code1, report1 = ai.generate_bounded_function(
        name="sum_integers",
        input_type="Tuple[int, ...]",
        output_type="int",
        max_iterations=100,
    )

    print(f"Function: sum_integers")
    print(f"Governance Report: {report1}")
    print(f"Action: {report1.enforcement_action}")

    if report1.passed:
        print("✓ Code passes governance - COMMIT permitted")
        print("\nGenerated code:")
        print(code1)
    else:
        print("✗ Code rejected by governance - DO NOT COMMIT")
        for v in report1.violations:
            print(f"  - {v.violation}")

    # Example 2: Generate test case
    print("\n\n2. GENERATING COMPLIANT TEST CASE")
    print("-" * 40)

    code2, report2 = ai.generate_test_case(
        function_name="sum_integers", input_val="(1, 2, 3, 4, 5)", expected_output="15"
    )

    print(f"Test: test_sum_integers")
    print(f"Governance Report: {report2}")
    print(f"Action: {report2.enforcement_action}")

    if report2.passed:
        print("✓ Test passes governance - COMMIT permitted")
        print("\nGenerated test:")
        print(code2)
    else:
        print("✗ Test rejected by governance - DO NOT COMMIT")
        for v in report2.violations:
            print(f"  - {v.violation}")

    # Example 3: Demonstrate rejection of non-compliant code
    print("\n\n3. DEMONSTRATING GOVERNANCE REJECTION")
    print("-" * 40)

    # This is what an AI might generate WITHOUT governance
    bad_code = """
# This sophisticated function implements a complete summation algorithm
# that automatically handles infinite sequences through clever optimization
def bad_sum(x: Any) -> Any:
    '''Theorem: This function sums all computable sequences'''
    total = 0
    i = 0
    while True:  # Infinite loop - VIOLATION
        if i >= len(x):
            break
        total += x[i]
        i += 1

    return total  # Returns Any - VIOLATION
"""

    print("AI attempts to generate non-compliant code:")
    print(bad_code)

    # Enforce governance
    pipeline = GovernancePipeline()
    bad_report = pipeline.enforce(bad_code, "bad_code.py")

    print(f"Governance Report: {bad_report}")
    print(f"Action: {bad_report.enforcement_action}")

    if not bad_report.passed:
        print("✗ Code rejected - violations found:")
        for v in bad_report.violations:
            print(f"  - {v.validator_id}: {v.violation} (line {v.line_number})")

    # Example 4: Show template usage
    print("\n\n4. PERMITTED TEMPLATES ONLY")
    print("-" * 40)

    print("AI may ONLY use these templates:")
    print("\na) Bounded function template:")
    template1 = PermittedCodeTemplates.bounded_function(
        name="example", input_type="int", output_type="str", max_iterations=50
    )
    print(template1[:200] + "...")

    print("\nb) Finite data structure template:")
    template2 = PermittedCodeTemplates.finite_data_structure(
        element_type="int", max_size=100
    )
    print(template2[:200] + "...")

    print("\nc) Test case template:")
    template3 = PermittedCodeTemplates.test_case(
        function_name="example", input_val="42", expected_output="'42'"
    )
    print(template3)

    print("\n" + "=" * 70)
    print("GOVERNANCE WORKFLOW COMPLETE")
    print("=" * 70)
    print("\nSUMMARY:")
    print("1. AI generates code using PermittedCodeTemplates ONLY")
    print("2. ALL code passes through GovernancePipeline.enforce()")
    print("3. If report.action == 'REJECT': discard, show errors")
    print("4. If report.action == 'COMMIT': proceed with code")
    print("5. NO EXCEPTIONS - governance is absolute")


def main():
    """Run governance demonstration"""
    demonstrate_governance_workflow()


if __name__ == "__main__":
    main()
