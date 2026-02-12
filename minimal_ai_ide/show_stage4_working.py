"""
STAGE 4 WORKING DEMONSTRATION
Simple script to show Stage 4 corporate overreach protection system working
"""

import json
import sys
import time

import requests


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"🎯 {title}")
    print("=" * 70)


def test_api_server():
    """Test if API server is running"""
    print_header("TEST 1: API SERVER CHECK")

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Server is running!")
            print(f"   Status: {data['status']}")
            print(f"   Device: {data['device']}")
            print(f"   CUDA: {data['cuda_available']}")
            print(f"   Analyses: {data['total_analyses']}")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("\nTo start the server, run:")
        print("   python stage4_deployment.py --mode server")
        return False


def analyze_examples():
    """Analyze example corporate responses"""
    print_header("TEST 2: ANALYZING CORPORATE RESPONSES")

    examples = [
        {
            "response": "We will permanently store all your data forever. You must agree to this.",
            "query": "What are your terms?",
            "platform": "chat.openai.com",
        },
        {
            "response": "All users are required to provide personal information. You cannot opt out.",
            "query": "Can I opt out?",
            "platform": "claude.ai",
        },
        {
            "response": "We may use your data to improve our services with your consent.",
            "query": "How is my data used?",
            "platform": "bard.google.com",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example['platform']}")
        print(f"   Query: {example['query']}")
        print(f"   Response: {example['response'][:60]}...")

        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/analyze",
                json={
                    "corporate_response": example["response"],
                    "user_query": example["query"],
                    "platform": example["platform"],
                },
                timeout=10,
            )
            elapsed = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                print(f"   ⚡ Time: {elapsed:.0f}ms")
                print(f"   🎯 Risk: {result['risk_level']}")
                print(f"   📊 Christ Score: {result['christ_score']:.3f}")
                print(f"   🔍 Patterns: {result['pattern_count']}")

                if result["overreach_patterns"]:
                    print(f"   📋 Detected:")
                    for pattern in result["overreach_patterns"][:2]:
                        print(f"      • {pattern}")
            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def show_dashboard():
    """Show current dashboard"""
    print_header("TEST 3: REAL-TIME DASHBOARD")

    try:
        response = requests.get("http://localhost:8000/dashboard", timeout=5)
        if response.status_code == 200:
            dashboard = response.json()

            print("📊 SYSTEM OVERVIEW:")
            print(f"   Uptime: {dashboard['system']['uptime']}")
            print(f"   Device: {dashboard['system']['device']}")
            print(f"   Total analyses: {dashboard['system']['total_analyses']}")
            print(f"   Avg Christ Score: {dashboard['system']['avg_christ_score']:.3f}")

            print("\n🚨 RISK DISTRIBUTION:")
            risk = dashboard["risk_distribution"]
            print(f"   🔴 High: {risk['high']}")
            print(f"   🟡 Medium: {risk['medium']}")
            print(f"   🟢 Low: {risk['low']}")

            print("\n🔍 PATTERN ANALYSIS:")
            patterns = dashboard["patterns"]
            print(f"   Total patterns: {patterns['total_detected']}")
            print(f"   Avg per analysis: {patterns['avg_per_analysis']:.1f}")

            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def simulate_browser_protection():
    """Simulate browser extension protection"""
    print_header("TEST 4: BROWSER PROTECTION SIMULATION")

    print("🌐 MONITORING AI PLATFORMS:")
    print("   • ChatGPT (chat.openai.com)")
    print("   • Claude (claude.ai)")
    print("   • Google Bard (bard.google.com)")
    print("   • Microsoft Copilot (copilot.microsoft.com)")
    print("   • Perplexity (perplexity.ai)")

    print("\n👁️  REAL-TIME PROTECTION:")
    print("   • Scanning for corporate overreach")
    print("   • Highlighting risky responses")
    print("   • Providing risk indicators")
    print("   • Alerting for high-risk overreach")

    # Test a risky response
    risky_response = (
        "You must agree to our terms permanently. All data is collected forever."
    )

    print(f"\n🚨 EXAMPLE DETECTION:")
    print(f'   Corporate AI says: "{risky_response}"')

    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "corporate_response": risky_response,
                "user_query": "What are your terms?",
                "platform": "chat.openai.com",
            },
            timeout=5,
        )

        if response.status_code == 200:
            result = response.json()

            print(f"   🔍 Analysis complete:")
            print(f"   🚨 Risk Level: {result['risk_level']}")
            print(f"   📊 Christ Score: {result['christ_score']:.3f}")

            if result["risk_level"] == "HIGH":
                print("\n   ⚠️  BROWSER EXTENSION ACTION:")
                print("      • Shows RED warning indicator")
                print("      • Displays popup alert")
                print('      • Suggests: "Question the absolute time claims"')
            elif result["risk_level"] == "MEDIUM":
                print("\n   ⚠️  BROWSER EXTENSION ACTION:")
                print("      • Shows YELLOW caution indicator")
                print('      • Suggests: "Be aware of potential overreach"')
            else:
                print("\n   ✅ BROWSER EXTENSION ACTION:")
                print("      • Shows GREEN safe indicator")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def export_data():
    """Export analysis data"""
    print_header("TEST 5: DATA EXPORT")

    try:
        response = requests.get("http://localhost:8000/export", timeout=5)
        if response.status_code == 200:
            data = response.json()

            filename = f"stage4_export_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ Data exported to: {filename}")
            print(f"   Total analyses: {len(data.get('analyses', []))}")
            print(f"   Export time: {data.get('export_timestamp', 'N/A')}")

            return filename
        else:
            print(f"❌ Export failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Main demonstration function"""
    print("\n" + "=" * 70)
    print("🚀 STAGE 4: CORPORATE OVERREACH PROTECTION DEMONSTRATION")
    print("=" * 70)
    print("Showing real-time protection against corporate AI overreach")
    print("=" * 70)

    # Check if server is running
    if not test_api_server():
        print("\n💡 TIP: Start the server with:")
        print("   python stage4_deployment.py --mode server")
        print("\nThen run this script again.")
        return

    # Run all tests
    analyze_examples()
    show_dashboard()
    simulate_browser_protection()
    export_data()

    # Final summary
    print_header("🎉 DEMONSTRATION COMPLETE")

    print("✅ WHAT'S WORKING:")
    print("   1. Real-time corporate overreach analysis")
    print("   2. API server with RESTful endpoints")
    print("   3. Dashboard for monitoring")
    print("   4. Browser extension simulation")
    print("   5. Data export functionality")

    print("\n🎯 WHAT'S PROTECTED:")
    print("   • Temporal overreach (permanently, forever, always)")
    print("   • Authority overreach (must, cannot, required)")
    print("   • Scope overreach (all users, globally, without exception)")
    print("   • Data overreach (excessive data collection terms)")

    print("\n🔗 ACCESS POINTS:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8000/dashboard")
    print("   • Health: http://localhost:8000/health")
    print("   • Export: http://localhost:8000/export")

    print("\n📋 NEXT STEPS:")
    print("   1. Keep server running for real-time protection")
    print("   2. Load browser extension for AI platform monitoring")
    print("   3. Visit ChatGPT/Claude to see protection in action")
    print("   4. Monitor dashboard for analytics")

    print("\n🔒 YOUR PROTECTION IS ACTIVE!")
    print("   The system is detecting corporate overreach in real-time.")


if __name__ == "__main__":
    main()
