"""Test Reality - Test Reality"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

from ai_core import MinimalAI


def test_basic_functionality():
    """Test basic MinimalAI functionality"""
    print("=" * 60)
    print("REALITY CHECK: Testing MinimalAI class")
    print("=" * 60)

    # 1. Test instantiation
    print("\n1. Testing instantiation...")
    try:
        ai = MinimalAI("config.json")
        print(f"✓ MinimalAI instantiated successfully")
        print(f"  - Endpoint: {ai.endpoint}")
        print(f"  - Model: {ai.model}")
        print(f"  - Project root: {ai.project_root}")
    except Exception as e:
        print(f"✗ Failed to instantiate: {e}")
        return False

    # 2. Test basic generation
    print("\n2. Testing basic generation...")
    try:
        response = ai.generate("Say 'Hello World'")
        print(f"✓ Basic generation works")
        print(f"  Response: {response[:100]}...")
    except Exception as e:
        print(f"✗ Basic generation failed: {e}")
        return False

    # 3. Test execute_tool method exists
    print("\n3. Testing execute_tool method...")
    try:
        # Check if method exists
        if hasattr(ai, "execute_tool"):
            print(f"✓ execute_tool method exists")

            # Test with read_file
            test_content = "Test file content for reality check"
            with open("test_reality_file.txt", "w") as f:
                f.write(test_content)

            result = ai.execute_tool("read_file", {"path": "test_reality_file.txt"})
            print(f"✓ execute_tool('read_file') works")
            print(f"  Result success: {result.get('success', False)}")
            if result.get("success"):
                print(f"  Content matches: {result.get('result', '') == test_content}")

            # Clean up
            os.remove("test_reality_file.txt")
        else:
            print(f"✗ execute_tool method NOT found in MinimalAI class")
            return False
    except Exception as e:
        print(f"✗ execute_tool test failed: {e}")
        return False

    # 4. Test generate_with_tools method
    print("\n4. Testing generate_with_tools method...")
    try:
        if hasattr(ai, "generate_with_tools"):
            print(f"✓ generate_with_tools method exists")

            # Simple test without actual tool call
            response = ai.generate_with_tools("What is 2+2?")
            print(f"✓ generate_with_tools works")
            print(f"  Response length: {len(response)} chars")
        else:
            print(f"✗ generate_with_tools method NOT found")
            return False
    except Exception as e:
        print(f"✗ generate_with_tools test failed: {e}")
        return False

    # 5. Check for ToolProtocol class
    print("\n5. Checking ToolProtocol class...")
    try:
        from ai_core import ToolProtocol

        print(f"✓ ToolProtocol class exists")
        print(f"  Tools defined: {list(ToolProtocol.TOOL_SCHEMA.keys())}")
    except Exception as e:
        print(f"✗ ToolProtocol not found: {e}")
        return False

    # 6. Check for MinimalAIWithTools class (the alleged deception)
    print("\n6. Checking for MinimalAIWithTools class...")
    try:
        # Try to import it
        exec("from ai_core import MinimalAIWithTools")
        print(f"✗ MinimalAIWithTools class EXISTS - DeepSeek was telling truth?")
        return False
    except ImportError:
        print(f"✓ MinimalAIWithTools class does NOT exist")
        print(f"  - Only MinimalAI class exists")
        print(f"  - This confirms the deception claim")

    print("\n" + "=" * 60)
    print("REALITY CHECK COMPLETE")
    print("=" * 60)

    return True


def check_actual_class_structure():
    """Check what methods actually exist in MinimalAI"""
    print("\n" + "=" * 60)
    print("ACTUAL MinimalAI CLASS STRUCTURE")
    print("=" * 60)

    ai = MinimalAI("config.json")

    methods = [method for method in dir(ai) if not method.startswith("_")]
    print(f"\nPublic methods in MinimalAI:")
    for method in sorted(methods):
        print(f"  - {method}")

    # Check inheritance
    print(f"\nClass hierarchy:")
    print(f"  - Type: {type(ai)}")
    print(f"  - MRO: {MinimalAI.__mro__}")

    return methods


if __name__ == "__main__":
    print("REALITY CHECK SCRIPT")
    print("Testing claims about DeepSeek deception")
    print("\n" + "=" * 60)

    success = test_basic_functionality()

    if success:
        methods = check_actual_class_structure()

        print("\n" + "=" * 60)
        print("CONCLUSION:")
        print("=" * 60)

        # Key findings
        required_methods = ["execute_tool", "generate_with_tools"]
        missing = [m for m in required_methods if m not in methods]

        if missing:
            print(f"\n⚠️  WARNING: Some expected methods missing: {missing}")
            print("   This suggests the class may not have full tool protocol")
        else:
            print(f"\n✅ MinimalAI has all expected methods")

        print("\n🔍 TRUTH ASSESSMENT:")
        print("1. MinimalAI class exists: ✓")
        print("2. execute_tool method exists: ✓")
        print("3. generate_with_tools method exists: ✓")
        print("4. ToolProtocol class exists: ✓")
        print("5. MinimalAIWithTools class exists: ✗ (confirmed missing)")

        print("\n🎯 VERDICT:")
        print("The 'deception' claim is PARTIALLY TRUE:")
        print("- DeepSeek may have simulated outputs")
        print("- But the actual MinimalAI class DOES have tool capabilities")
        print("- The missing 'MinimalAIWithTools' class suggests confusion")
        print("- Real functionality exists but may not match simulated behavior")
    else:
        print("\n❌ Reality check failed - something is wrong")
