"""
DEBUG SCRIPT FOR FRAMEWORK 1 UNIVERSE
Biblically Accurate Graduate-Level Debugging
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework1.canonical_compiler import (
    CanonicalIDECompiler,
    CanonicalPlaceholder,
    ExplicitFailure,
    Pillar,
    PillarTheorem,
    TypedPlaceholder,
)
from framework1.mathematical_universe import (
    ChristologicalCategory,
    MathematicalUniverse,
    MathObject,
)


def debug_universe_construction():
    """Debug universe construction"""
    print("=" * 70)
    print("DEBUG: MATHEMATICAL UNIVERSE CONSTRUCTION")
    print("=" * 70)

    # Create universe
    universe = MathematicalUniverse(name="Debug Universe")

    print(f"\n1. Universe created: {universe.name}")
    print(f"   Christological center: {universe.christological_center}")

    # Check objects
    print(f"\n2. Objects in universe: {len(universe.objects)}")
    for uid, obj in universe.objects.items():
        print(f"   - {obj.name} (UID: {uid[:8]}...)")
        print(f"     Type hierarchy: {obj.type_hierarchy}")
        print(f"     Properties: {list(obj.properties.keys())}")
        print(f"     Christological: {obj.verify()['christological']}")

    # Check foundational objects
    print(f"\n3. Foundational objects check:")
    required_objects = [
        "Christological_Center",
        "Empty_Set",
        "Natural_Numbers",
        "Continuum",
    ]
    for obj_name in required_objects:
        found = any(obj.name == obj_name for obj in universe.objects.values())
        print(f"   - {obj_name}: {'FOUND' if found else 'MISSING'}")

    # Test adding a new object
    print(f"\n4. Testing object addition:")
    test_obj = MathObject(
        name="Debug_Test_Object",
        type_hierarchy=["Debug", "Test"],
        properties={"debug": True, "test_value": 42},
    )

    try:
        added = universe.add_object(test_obj)
        print(f"   Added test object: {added}")
        print(f"   Object UID: {test_obj.uid}")
        print(f"   Object verification: {test_obj.verify()}")
    except Exception as e:
        print(f"   ERROR adding object: {e}")

    # Check universe stats
    print(f"\n5. Universe statistics:")
    stats = universe.get_universe_stats()
    for key, value in stats.items():
        if key != "type_distribution":
            print(f"   - {key}: {value}")

    print(f"\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)


def debug_typed_placeholder():
    """Debug typed placeholder system"""
    print("\n" + "=" * 70)
    print("DEBUG: TYPED PLACEHOLDER SYSTEM")
    print("=" * 70)

    # Create universe
    universe = MathematicalUniverse(name="Placeholder Debug Universe")

    # Create a simple constraint function
    def has_value_property(obj):
        return "value" in obj.properties

    def value_greater_than_zero(obj):
        return obj.properties.get("value", 0) > 0

    # Create typed placeholder
    placeholder = TypedPlaceholder(
        name="Positive_Number_Placeholder",
        domain=int,
        codomain=float,
        constraints=[has_value_property, value_greater_than_zero],
    )

    print(f"\n1. Placeholder created:")
    print(f"   Name: {placeholder.name}")
    print(f"   Type signature: {placeholder.type_signature}")
    print(f"   Constraint hash: {placeholder.constraint_hash}")
    print(f"   Constraints: {len(placeholder.constraints)}")

    # Check universe objects
    print(f"\n2. Universe objects before adding test objects:")
    for uid, obj in universe.objects.items():
        print(f"   - {obj.name}: properties = {obj.properties}")

    # Add test objects
    print(f"\n3. Adding test objects:")

    # Positive object
    positive_obj = MathObject(
        name="Positive_Test_Object",
        type_hierarchy=["Number", "Positive", "Test"],
        properties={"value": 42, "positive": True},
    )

    # Negative object
    negative_obj = MathObject(
        name="Negative_Test_Object",
        type_hierarchy=["Number", "Negative", "Test"],
        properties={"value": -42, "negative": True},
    )

    # Object without value property
    no_value_obj = MathObject(
        name="No_Value_Object",
        type_hierarchy=["Test", "Generic"],
        properties={"test": True, "generic": True},
    )

    test_objects = [
        ("Positive", positive_obj),
        ("Negative", negative_obj),
        ("No Value", no_value_obj),
    ]

    for obj_type, obj in test_objects:
        try:
            universe.add_object(obj)
            print(f"   Added {obj_type} object: {obj.name}")
            print(f"     Properties: {obj.properties}")
            print(f"     Type hierarchy: {obj.type_hierarchy}")
        except Exception as e:
            print(f"   ERROR adding {obj_type} object: {e}")

    # Test placeholder realization
    print(f"\n4. Testing placeholder realization:")

    # Check type matching
    print(f"   Type matching test:")
    for obj in universe.objects.values():
        matches = placeholder._type_matches(obj)
        print(f"   - {obj.name}: type_matches = {matches}")

    # Check constraint satisfaction
    print(f"\n   Constraint satisfaction test:")
    for obj in universe.objects.values():
        has_value = has_value_property(obj)
        value_positive = value_greater_than_zero(obj) if has_value else False
        christological = placeholder._satisfies_christological_constraints(obj)
        print(f"   - {obj.name}:")
        print(f"     has_value_property: {has_value}")
        print(f"     value_greater_than_zero: {value_positive}")
        print(f"     christological_constraints: {christological}")
        print(
            f"     ALL constraints: {has_value and value_positive and christological}"
        )

    # Try to realize placeholder
    print(f"\n5. Attempting placeholder realization:")
    result = placeholder.realize(universe)

    if result is None:
        print(f"   Result: None (no realization found)")

        # Debug why no realization
        print(f"\n   Debugging why no realization:")
        candidates = []
        for obj in universe.objects.values():
            type_match = placeholder._type_matches(obj)
            constraints_met = all(c(obj) for c in placeholder.constraints)
            christological_ok = placeholder._satisfies_christological_constraints(obj)

            if type_match and constraints_met and christological_ok:
                candidates.append(obj)
                print(f"   - {obj.name} IS a candidate!")
            else:
                print(f"   - {obj.name} is NOT a candidate:")
                print(f"     type_match: {type_match}")
                print(f"     constraints_met: {constraints_met}")
                print(f"     christological_ok: {christological_ok}")

        print(f"\n   Total candidates found: {len(candidates)}")

    else:
        print(f"   Result: {result.name}")
        print(f"   Result properties: {result.properties}")

    print(f"\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)


def debug_christological_verification():
    """Debug Christological verification"""
    print("\n" + "=" * 70)
    print("DEBUG: CHRISTOLOGICAL VERIFICATION")
    print("=" * 70)

    # Test signature verification
    test_signature = "3fad5fe4d720efcaf05c212c8629cb7b"
    print(f"\n1. Test signature: {test_signature}")
    print(f"   Starts with 't': {test_signature.startswith('t')}")
    print(f"   Starts with '3': {test_signature.startswith('3')}")

    # Create test object and check Christological properties
    print(f"\n2. Creating test MathObject:")
    test_obj = MathObject(
        name="Christological_Test_Object",
        type_hierarchy=["Test", "Christological"],
        properties={"test": True},
    )

    verification = test_obj.verify()
    print(f"   Object verification:")
    for key, value in verification.items():
        print(f"   - {key}: {value}")

    print(f"\n3. Christological signature analysis:")
    print(f"   Signature: {test_obj.christological_signature}")
    print(f"   Starts with 'c': {test_obj.christological_signature.startswith('c')}")

    print(f"\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    print("FRAMEWORK 1 DEBUG SCRIPT")
    print("=" * 70)

    # Run all debug functions
    debug_universe_construction()
    debug_typed_placeholder()
    debug_christological_verification()

    print("\n" + "=" * 70)
    print("ALL DEBUG TESTS COMPLETE")
    print("=" * 70)
