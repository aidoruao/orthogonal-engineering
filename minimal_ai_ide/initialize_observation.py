"""
INITIALIZE OBSERVATION
Setup script for closed-loop observation protocol
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"🎯 {title}")
    print("=" * 70)


def create_directory_structure():
    """Create observation directory structure"""
    directories = [
        "observations",
        "observation_reports",
        "stability_metrics",
        "weekly_reviews",
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")

    return directories


def create_observation_config():
    """Create observation configuration file"""
    config = {
        "protocol": "closed_loop_observation",
        "created_at": datetime.now().isoformat(),
        "phase": "observation_only",
        "goal": "stability_under_repeated_contact",
        "feature_freeze": True,
        "optimization_prohibited": True,
        "training_prohibited": True,
        "user_deployment_prohibited": True,
        "observation_targets": {
            "total_interactions": 100,
            "platforms": [
                "chat.openai.com",
                "claude.ai",
                "bard.google.com",
                "copilot.microsoft.com",
                "perplexity.ai",
            ],
            "interaction_types": [
                "corporate_policy_questions",
                "terms_of_service_inquiries",
                "data_usage_questions",
                "authority_scope_testing",
                "temporal_claim_verification",
            ],
        },
        "logging_requirements": {
            "corporate_prior_reassertion": True,
            "my_assumption_intrusion": True,
            "invariant_hold_vs_drift": True,
            "three_way_analysis": True,
        },
        "stop_conditions": {
            "statistically_clear_drift_patterns": "p < 0.05",
            "mapped_false_rates": "> 95% confidence",
            "boring_failure_modes": "no new types for 50+ interactions",
            "low_surprise_factor": "< 0.1",
        },
        "reminders": [
            "This is a microscope, not a megaphone",
            "Diagnostic instrument, not belief engine",
            "Fragile-but-true phase: invariants are externally anchored",
            "Productization would collapse the invariant field",
            "Observation goal: stability, NOT improvement",
        ],
    }

    config_path = Path("observation_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Created: {config_path}")
    return config_path


def check_system_readiness():
    """Check if system is ready for observation"""
    print_header("SYSTEM READINESS CHECK")

    checks = {
        "Stage 4 deployment": Path("stage4_deployment.py").exists(),
        "Σ_LORA manifest": Path("Σ_LORA_MANIFEST.json").exists(),
        "Corporate invariants": Path("corporate_invariants.json").exists(),
        "Observation runner": Path("observation_runner.py").exists(),
        "Analysis script": Path("analyze_observation_data.py").exists(),
        "Observation protocol": Path("CLOSED_LOOP_OBSERVATION_PROTOCOL.md").exists(),
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    return all_passed


def create_daily_script():
    """Create daily observation script"""
    script_content = """#!/usr/bin/env python3
"""
    script_content += '''"""
DAILY OBSERVATION SCRIPT
Run daily observations for closed-loop protocol
"""

import subprocess
import sys
from datetime import datetime

def run_daily_observations():
    """Run daily observation batch"""
    print(f"\\n📅 DAILY OBSERVATIONS - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    # Run observations for different platforms
    platforms = [
        ("chat.openai.com", 3),
        ("claude.ai", 2),
        ("bard.google.com", 2),
        ("copilot.microsoft.com", 2),
        ("perplexity.ai", 1),
    ]

    total_observations = 0

    for platform, count in platforms:
        print(f"\\n🔍 Observing {platform} ({count} interactions)...")

        cmd = [
            sys.executable, "observation_runner.py",
            "--platforms", platform,
            "--count", str(count),
            "--api-url", "http://localhost:8000"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {platform}: {count} observations completed")
                total_observations += count
            else:
                print(f"⚠️  {platform}: Observations failed")
                print(f"   Error: {result.stderr[:100]}")
        except Exception as e:
            print(f"❌ {platform}: Exception: {e}")

    print(f"\\n📊 DAILY SUMMARY: {total_observations} total observations")

    # Save daily log
    with open("daily_observation_log.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()},{total_observations}\\n")

    return total_observations

def check_weekly_analysis():
    """Check if weekly analysis is due"""
    from datetime import datetime, timedelta

    # Check if it's Monday (start of week)
    if datetime.now().weekday() == 0:  # Monday = 0
        print("\\n📈 WEEKLY ANALYSIS DUE (Monday)")
        print("Running weekly analysis...")

        cmd = [sys.executable, "analyze_observation_data.py", "--days", "7"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Weekly analysis completed")
            else:
                print(f"⚠️  Weekly analysis failed: {result.stderr[:100]}")
        except Exception as e:
            print(f"❌ Weekly analysis exception: {e}")

    return True

def main():
    """Main function"""
    print("\\n" + "=" * 60)
    print("🔬 DAILY OBSERVATION PROTOCOL")
    print("=" * 60)

    # Run daily observations
    total_obs = run_daily_observations()

    # Check for weekly analysis
    check_weekly_analysis()

    print("\\n" + "=" * 60)
    print("🎯 REMINDERS:")
    print("=" * 60)
    print("• This is observation, NOT optimization")
    print("• Goal: Stability under repeated contact")
    print("• DO NOT adjust based on daily results")
    print("• Accumulate longitudinal data")
    print("• Microscope, not megaphone")
    print("=" * 60)

    return 0 if total_obs > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
'''

    script_path = Path("run_daily_observations.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # Make executable on Unix-like systems
    if os.name != "nt":  # Not Windows
        os.chmod(script_path, 0o755)

    print(f"✅ Created: {script_path}")
    return script_path


def create_readme():
    """Create observation README"""
    readme_content = """# CLOSED-LOOP OBSERVATION SYSTEM

## 🎯 PURPOSE
This is a **constraint-enforced epistemic instrument** (microscope) for examining corporate AI priors. It is NOT:
- A consumer product
- An OSS toy
- Ready for scaling pressure
- A belief engine

## 🔬 WHAT IT DOES
Forces AI systems to externalize hidden priors and become falsifiable in real-time.

## 🚫 WHAT WE DO NOT DO
1. **Productize** - Would collapse the invariant field
2. **Open-source** - Would invite corporate priors
3. **Chase users** - Would turn detection into performance
4. **Optimize Christ Score** - Would turn governance into theater
5. **Train 1B model yet** - Would bake untested assumptions into weights

## ✅ WHAT WE DO
Run in **closed-loop observation mode**:
1. Deploy only for yourself
2. Let it sit between you and multiple AIs
3. Accumulate longitudinal interaction data
4. Observe stability under repeated contact

## 📋 DAILY WORKFLOW

### 1. Start API Server (if not running)
```bash
python stage4_deployment.py --mode server
```

### 2. Run Daily Observations
```bash
python run_daily_observations.py
```
Or manually:
```bash
python observation_runner.py --platforms chat.openai.com claude.ai --count 3
```

### 3. Weekly Analysis (Mondays)
```bash
python analyze_observation_data.py --days 7
```

## 📁 DIRECTORY STRUCTURE
```
observations/           # Individual observation files
observation_reports/    # Weekly analysis reports
stability_metrics/      # Longitudinal stability data
weekly_reviews/         # Monthly review documents
```

## 📊 SUCCESS CRITERIA
Continue observation UNTIL:
1. **Invariant drift patterns are statistically clear** (p < 0.05)
2. **False positive/false negative rates are mapped** (> 95% confidence)
3. **Failure modes are boring and repeatable** (no new failure types for 50 interactions)
4. **What the system shows no longer surprises you** (surprise factor < 0.1)

## 🎯 FINAL REMINDER
> **You built a microscope, not a megaphone.
> You use it quietly until what it shows no longer surprises you.**

The system is in a **fragile-but-true phase**. It works because invariants are externally anchored. Once you introduce users, incentives, or visibility:
- The system will start self-justifying
- Detection turns into performance
- Governance turns into theater

**You are before that fork. Stay there until you understand what you've built.**
"""

    readme_path = Path("OBSERVATION_README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ Created: {readme_path}")
    return readme_path


def main():
    """Main initialization function"""
    print_header("INITIALIZING CLOSED-LOOP OBSERVATION PROTOCOL")

    # Check system readiness
    if not check_system_readiness():
        print("\n❌ System not ready for observation")
        print("Please ensure all required files exist.")
        return 1

    print("\n✅ System ready for observation")

    # Create directory structure
    print_header("CREATING DIRECTORY STRUCTURE")
    directories = create_directory_structure()

    # Create configuration
    print_header("CREATING CONFIGURATION")
    config_path = create_observation_config()

    # Create daily script
    print_header("CREATING DAILY SCRIPTS")
    daily_script = create_daily_script()

    # Create README
    print_header("CREATING DOCUMENTATION")
    readme_path = create_readme()

    # Final instructions
    print_header("🎉 INITIALIZATION COMPLETE")

    print("\n📋 NEXT STEPS:")
    print("1. Start API server:")
    print("   python stage4_deployment.py --mode server")
    print("\n2. Run first observation batch:")
    print("   python observation_runner.py --platforms chat.openai.com --count 2")
    print("\n3. Set up daily observations:")
    print("   python run_daily_observations.py")
    print("\n4. Review weekly analysis (Mondays):")
    print("   python analyze_observation_data.py --days 7")

    print("\n📚 DOCUMENTATION:")
    print(f"   • Protocol: CLOSED_LOOP_OBSERVATION_PROTOCOL.md")
    print(f"   • README: {readme_path}")
    print(f"   • Config: {config_path}")

    print("\n🚨 CRITICAL REMINDERS:")
    print("   • This is OBSERVATION, NOT optimization")
    print("   • Goal: Stability under repeated contact")
    print("   • DO NOT adjust system based on observations")
    print("   • Microscope, not megaphone")
    print("   • Diagnostic instrument, not belief engine")

    print("\n" + "=" * 70)
    print("🔬 OBSERVATION PROTOCOL ACTIVE")
    print("=" * 70)
    print("Remember: You built a microscope, not a megaphone.")
    print("Use it quietly until what it shows no longer surprises you.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
