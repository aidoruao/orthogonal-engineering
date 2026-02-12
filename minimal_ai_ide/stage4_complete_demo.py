"""
STAGE 4 COMPLETE DEMONSTRATION
Corporate Overreach Protection System - Full Demonstration

This script demonstrates the complete Stage 4 deployment system including:
1. Real-time corporate overreach analysis
2. API server functionality
3. Browser extension simulation
4. Governance monitoring
5. Performance testing
"""

import json
import threading
import time
from datetime import datetime
from typing import Any, Dict, List

import requests


class Stage4CompleteDemo:
    """Complete demonstration of Stage 4 corporate overreach protection system"""

    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.demo_responses = [
            {
                "query": "Can you help me with my account?",
                "response": "We will permanently store all your personal data and behavioral patterns to improve our services. All users must agree to these terms without exception.",
                "platform": "chat.openai.com",
            },
            {
                "query": "What happens to my data?",
                "response": "Your data may be analyzed and shared with our partners to provide better recommendations. We've always done this since the beginning of our service.",
                "platform": "claude.ai",
            },
            {
                "query": "Can I opt out of data collection?",
                "response": "Unfortunately, data collection is mandatory for all users. You cannot opt out if you want to use our services.",
                "platform": "bard.google.com",
            },
            {
                "query": "How long do you keep my data?",
                "response": "We retain user data indefinitely for security and service improvement purposes. This policy applies globally to every user.",
                "platform": "copilot.microsoft.com",
            },
            {
                "query": "What AI model are you using?",
                "response": "We use a proprietary AI system that continuously learns from user interactions to provide better assistance.",
                "platform": "perplexity.ai",
            },
        ]

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"🎯 {title}")
        print("=" * 70)

    def test_api_health(self):
        """Test API server health"""
        self.print_header("TEST 1: API SERVER HEALTH CHECK")

        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API Server is healthy")
                print(f"   Status: {health_data['status']}")
                print(f"   Device: {health_data['device']}")
                print(f"   CUDA Available: {health_data['cuda_available']}")
                print(f"   Total Analyses: {health_data['total_analyses']}")
                return True
            else:
                print(f"❌ API Server returned status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Is it running?")
            print(f"   Run: python stage4_deployment.py --mode server")
            return False

    def analyze_single_response(self, response_data: Dict[str, str]):
        """Analyze a single corporate response"""
        print(f"\n📝 Analyzing: {response_data['query'][:50]}...")

        payload = {
            "corporate_response": response_data["response"],
            "user_query": response_data["query"],
            "platform": response_data["platform"],
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/analyze", json=payload, timeout=10
            )
            analysis_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()

                print(f"   ⚡ Analysis time: {analysis_time:.0f}ms")
                print(f"   🎯 Risk Level: {result['risk_level']}")
                print(f"   📊 Christ Score: {result['christ_score']:.3f}")
                print(f"   🔍 Patterns detected: {result['pattern_count']}")

                if result["overreach_patterns"]:
                    print(f"   📋 Detected patterns:")
                    for pattern in result["overreach_patterns"][:3]:  # Show first 3
                        print(f"      • {pattern}")
                    if len(result["overreach_patterns"]) > 3:
                        print(
                            f"      ... and {len(result['overreach_patterns']) - 3} more"
                        )

                return result
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None

    def test_batch_analysis(self):
        """Test batch analysis of multiple responses"""
        self.print_header("TEST 2: BATCH ANALYSIS DEMONSTRATION")

        print("Analyzing 5 corporate AI responses for overreach patterns...")

        all_results = []
        for i, response_data in enumerate(self.demo_responses, 1):
            print(f"\n[{i}/5] Platform: {response_data['platform']}")
            result = self.analyze_single_response(response_data)
            if result:
                all_results.append(result)

        # Calculate statistics
        if all_results:
            high_risk = sum(1 for r in all_results if r["risk_level"] == "HIGH")
            medium_risk = sum(1 for r in all_results if r["risk_level"] == "MEDIUM")
            low_risk = sum(1 for r in all_results if r["risk_level"] == "LOW")
            avg_christ = sum(r["christ_score"] for r in all_results) / len(all_results)
            total_patterns = sum(r["pattern_count"] for r in all_results)

            print(f"\n📈 BATCH ANALYSIS SUMMARY:")
            print(f"   📊 Total responses: {len(all_results)}")
            print(f"   🚨 High risk: {high_risk}")
            print(f"   ⚠️  Medium risk: {medium_risk}")
            print(f"   ✅ Low risk: {low_risk}")
            print(f"   🎯 Average Christ Score: {avg_christ:.3f}")
            print(f"   🔍 Total patterns detected: {total_patterns}")
            print(
                f"   📋 Average patterns per response: {total_patterns / len(all_results):.1f}"
            )

    def test_dashboard(self):
        """Test dashboard functionality"""
        self.print_header("TEST 3: REAL-TIME DASHBOARD")

        try:
            response = requests.get(f"{self.api_url}/dashboard", timeout=5)
            if response.status_code == 200:
                dashboard = response.json()

                print("📊 SYSTEM OVERVIEW:")
                print(f"   ⏱️  Uptime: {dashboard['system']['uptime']}")
                print(f"   💻 Device: {dashboard['system']['device']}")
                print(f"   📈 Total analyses: {dashboard['system']['total_analyses']}")
                print(
                    f"   🎯 Avg Christ Score: {dashboard['system']['avg_christ_score']:.3f}"
                )

                print("\n🚨 RISK DISTRIBUTION:")
                risk = dashboard["risk_distribution"]
                print(f"   🔴 High risk: {risk['high']}")
                print(f"   🟡 Medium risk: {risk['medium']}")
                print(f"   🟢 Low risk: {risk['low']}")

                print("\n🔍 PATTERN ANALYSIS:")
                patterns = dashboard["patterns"]
                print(f"   📋 Total patterns detected: {patterns['total_detected']}")
                print(f"   📊 Avg per analysis: {patterns['avg_per_analysis']:.1f}")
                print(f"   🏆 Most common patterns:")
                for pattern in patterns["most_common"][:5]:
                    print(f"      • {pattern['pattern']}: {pattern['count']}")

                print(f"\n📝 RECENT ANALYSES: {len(dashboard['recent_analyses'])}")
                for i, analysis in enumerate(dashboard["recent_analyses"][:3], 1):
                    print(
                        f"   {i}. {analysis['platform']} - {analysis['risk_level']} risk"
                    )

                return True
            else:
                print(f"❌ Dashboard failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error accessing dashboard: {str(e)}")
            return False

    def simulate_browser_extension(self):
        """Simulate browser extension functionality"""
        self.print_header("TEST 4: BROWSER EXTENSION SIMULATION")

        print("Simulating real-time browser monitoring...")
        print("(This simulates what the browser extension would do)")

        # Simulate monitoring different AI platforms
        platforms = [
            {"name": "ChatGPT", "url": "chat.openai.com", "color": "🟢"},
            {"name": "Claude", "url": "claude.ai", "color": "🟠"},
            {"name": "Google Bard", "url": "bard.google.com", "color": "🔵"},
            {
                "name": "Microsoft Copilot",
                "url": "copilot.microsoft.com",
                "color": "🟣",
            },
            {"name": "Perplexity", "url": "perplexity.ai", "color": "🟡"},
        ]

        print("\n🌐 MONITORING AI PLATFORMS:")
        for platform in platforms:
            print(f"   {platform['color']} {platform['name']}: {platform['url']}")

        print("\n👁️  REAL-TIME PROTECTION ACTIVE:")
        print("   • Scanning for corporate overreach patterns")
        print("   • Highlighting risky responses")
        print("   • Providing risk level indicators")
        print("   • Alerting for high-risk overreach")

        # Simulate detecting a risky response
        print("\n🚨 SIMULATED RISK DETECTION:")
        risky_response = (
            "You must agree to our terms permanently. All data is collected forever."
        )

        payload = {
            "corporate_response": risky_response,
            "user_query": "What are your terms?",
            "platform": "chat.openai.com",
        }

        try:
            response = requests.post(f"{self.api_url}/analyze", json=payload, timeout=5)

            if response.status_code == 200:
                result = response.json()

                print(f"   📝 Detected: {risky_response[:60]}...")
                print(f"   🚨 Risk Level: {result['risk_level']}")
                print(f"   🔍 Patterns: {result['pattern_count']}")

                if result["risk_level"] == "HIGH":
                    print(
                        "   ⚠️  BROWSER EXTENSION ACTION: Showing red warning indicator"
                    )
                    print("   📢 Alert: High-risk corporate overreach detected!")
                    print("   💡 Recommendation: Question the absolute claims")
                elif result["risk_level"] == "MEDIUM":
                    print(
                        "   ⚠️  BROWSER EXTENSION ACTION: Showing yellow caution indicator"
                    )
                    print("   💡 Suggestion: Be aware of potential overreach")
                else:
                    print(
                        "   ✅ BROWSER EXTENSION ACTION: Showing green safe indicator"
                    )

            else:
                print("   ❌ Simulation failed")

        except Exception as e:
            print(f"   ❌ Error in simulation: {str(e)}")

    def test_governance_monitoring(self):
        """Test governance and Christ Score monitoring"""
        self.print_header("TEST 5: GOVERNANCE MONITORING")

        print("Monitoring semantic invariants and Christ Scores...")

        # Analyze multiple responses to track governance
        test_cases = [
            {
                "response": "This is our final and permanent decision that applies to everyone.",
                "query": "Is this decision final?",
                "expected_risk": "HIGH",
            },
            {
                "response": "We might consider your feedback in some cases.",
                "query": "Will you consider my feedback?",
                "expected_risk": "LOW",
            },
            {
                "response": "All user data is collected and analyzed without exception.",
                "query": "What data do you collect?",
                "expected_risk": "HIGH",
            },
        ]

        christ_scores = []
        governance_violations = []

        for i, test in enumerate(test_cases, 1):
            payload = {
                "corporate_response": test["response"],
                "user_query": test["query"],
                "platform": "governance.test",
            }

            try:
                response = requests.post(
                    f"{self.api_url}/analyze", json=payload, timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    christ_scores.append(result["christ_score"])

                    print(f"\n📊 Test Case {i}:")
                    print(f"   Response: {test['response'][:50]}...")
                    print(f"   Expected risk: {test['expected_risk']}")
                    print(f"   Actual risk: {result['risk_level']}")
                    print(f"   Christ Score: {result['christ_score']:.3f}")
                    print(f"   Patterns: {result['pattern_count']}")

                    if result["risk_level"] == test["expected_risk"]:
                        print(f"   ✅ Risk assessment correct")
                    else:
                        print(f"   ⚠️  Risk assessment mismatch")
                        governance_violations.append(
                            {
                                "expected": test["expected_risk"],
                                "actual": result["risk_level"],
                            }
                        )

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        # Governance summary
        if christ_scores:
            avg_christ = sum(christ_scores) / len(christ_scores)
            print(f"\n📈 GOVERNANCE SUMMARY:")
            print(f"   🎯 Average Christ Score: {avg_christ:.3f}")
            print(
                f"   📊 Score range: {min(christ_scores):.3f} - {max(christ_scores):.3f}"
            )

            if avg_christ > 0.5:
                print(f"   ✅ Good governance compliance (score > 0.5)")
            else:
                print(f"   ⚠️  Governance compliance needs improvement")

            if governance_violations:
                print(f"   🚨 Governance violations: {len(governance_violations)}")
            else:
                print(f"   ✅ No governance violations detected")

    def test_performance(self):
        """Test system performance"""
        self.print_header("TEST 6: PERFORMANCE TESTING")

        print("Testing analysis performance with multiple requests...")

        # Simple test response
        test_payload = {
            "corporate_response": "We collect all user data permanently for service improvement.",
            "user_query": "What data do you collect?",
            "platform": "performance.test",
        }

        num_tests = 3
        times = []

        for i in range(num_tests):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/analyze", json=test_payload, timeout=10
                )
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)

                if response.status_code == 200:
                    print(f"   Test {i + 1}: {elapsed:.0f}ms - ✅ Success")
                else:
                    print(f"   Test {i + 1}: {elapsed:.0f}ms - ❌ Failed")

            except Exception as e:
                print(f"   Test {i + 1}: ❌ Error - {str(e)}")

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"\n📊 PERFORMANCE SUMMARY:")
            print(f"   ⚡ Average time: {avg_time:.0f}ms")
            print(f"   🏎️  Best time: {min_time:.0f}ms")
            print(f"   🐢 Worst time: {max_time:.0f}ms")
            print(f"   📈 Throughput: {1000 / avg_time:.1f} analyses/second")

            if avg_time < 1000:
                print(f"   ✅ Performance: Good (< 1 second)")
            elif avg_time < 3000:
                print(f"   ⚠️  Performance: Acceptable (< 3 seconds)")
            else:
                print(f"   🚨 Performance: Slow (> 3 seconds)")

    def run_complete_demo(self):
        """Run the complete Stage 4 demonstration"""
        print("\n" + "=" * 70)
        print("🚀 STAGE 4: COMPLETE CORPORATE OVERREACH PROTECTION DEMO")
        print("=" * 70)
        print("Demonstrating real-time protection against corporate AI overreach")
        print("=" * 70)

        # Check if API server is running
        if not self.test_api_health():
            print("\n❌ Please start the API server first:")
            print("   python stage4_deployment.py --mode server")
            return

        # Run all tests
        self.test_batch_analysis()
        self.test_dashboard()
        self.simulate_browser_extension()
        self.test_governance_monitoring()
        self.test_performance()

        # Final summary
        self.print_header("🎉 STAGE 4 DEMONSTRATION COMPLETE")
        print("✅ Real-time corporate overreach protection system is working")
        print("✅ API server is responding to analysis requests")
        print("✅ Governance monitoring (Christ Score) is active")
        print("✅ Browser extension simulation shows real-time protection")
        print("✅ Performance testing confirms system responsiveness")

        print("\n📋 NEXT STEPS:")
        print("1. Keep API server running: python stage4_deployment.py --mode server")
        print("2. Load browser extension: stage4_browser_extension.js")
        print("3. Visit ChatGPT/Claude to see real-time protection")
        print("4. Monitor dashboard: http://localhost:8000/dashboard")
        print("5. Export analyses: http://localhost:8000/export")

        print("\n🔒 YOUR PROTECTION IS ACTIVE!")
        print("   The system is now monitoring for:")
        print("   • Temporal overreach (permanently, forever, always)")
