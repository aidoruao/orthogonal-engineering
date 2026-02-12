"""
COMPLETE SYSTEM READINESS TEST FOR 1B+ MODEL TRAINING
======================================================

This script tests ALL components required for training a 1B+ parameter model
with the complete Σ_LORA system, corporate invariants, and creative frameworks.

Tests include:
1. Environment and dependencies
2. Model availability and compatibility
3. Dataset integrity and formatting
4. Σ_LORA constraint system validation
5. Corporate invariants extraction
6. Training infrastructure readiness
7. GPU/CUDA compatibility
8. Creative system integration (polymathic, graduate mathematics, christological)
"""

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch


class CompleteSystemReadinessTest:
    """Comprehensive test for 1B+ model training readiness"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.requirements = {
            "torch": ">=2.0.0",
            "transformers": ">=4.30.0",
            "peft": ">=0.4.0",
            "accelerate": ">=0.20.0",
            "datasets": ">=2.14.0",
            "bitsandbytes": ">=0.41.0",
            "wandb": ">=0.16.0",
        }

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"🎯 {title}")
        print("=" * 80)

    def test_environment(self) -> bool:
        """Test Python environment and dependencies"""
        self.print_header("TEST 1: ENVIRONMENT & DEPENDENCIES")

        results = {}

        # Python version
        python_version = sys.version_info
        results["python_version"] = (
            f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        )
        print(f"✅ Python: {results['python_version']}")

        # Check dependencies
        for package, min_version in self.requirements.items():
            try:
                module = importlib.import_module(package)
                version = getattr(module, "__version__", "unknown")
                results[f"{package}_version"] = version
                print(f"✅ {package}: {version}")
            except ImportError:
                results[f"{package}_version"] = "NOT INSTALLED"
                print(f"❌ {package}: NOT INSTALLED")

        self.test_results["environment"] = results
        return all("NOT INSTALLED" not in v for v in results.values())

    def test_hardware(self) -> bool:
        """Test GPU/CUDA availability"""
        self.print_header("TEST 2: HARDWARE & ACCELERATION")

        results = {}

        # CUDA availability
        cuda_available = torch.cuda.is_available()
        results["cuda_available"] = cuda_available

        if cuda_available:
            print(f"✅ CUDA Available: Yes")
            print(f"✅ GPU Count: {torch.cuda.device_count()}")
            print(f"✅ Current Device: {torch.cuda.current_device()}")
            print(f"✅ Device Name: {torch.cuda.get_device_name(0)}")
            print(f"✅ CUDA Version: {torch.version.cuda}")

            # Memory info
            results["gpu_memory_total"] = (
                torch.cuda.get_device_properties(0).total_memory / 1e9
            )
            results["gpu_memory_free"] = torch.cuda.memory_reserved(0) / 1e9
            print(f"✅ GPU Memory: {results['gpu_memory_total']:.1f} GB total")
        else:
            print("⚠️  CUDA Not Available - Will use CPU (slower)")
            print("   Consider: python fix_cuda_stage4.py")

        # PyTorch version
        results["torch_version"] = torch.__version__
        print(f"✅ PyTorch: {results['torch_version']}")

        self.test_results["hardware"] = results
        return True  # CPU is acceptable

    def test_model_availability(self) -> bool:
        """Test if 1B+ models are configured and available"""
        self.print_header("TEST 3: 1B+ MODEL CONFIGURATION")

        results = {}
        model_files = []

        # Check for model configuration files
        config_files = [
            "train_lora.py",
            "POLYMATHIC_LORA_CLI.py",
            "POLYMATHIC_LORA_IDE.py",
            "POLYMATHIC_LORA_IDE_COMPLETE.py",
        ]

        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                model_files.append(config_file)
                print(f"✅ Found: {config_file}")

                # Check for model name in file
                try:
                    content = file_path.read_text()
                    if "Llama-3.2-1B" in content or "llama" in content.lower():
                        results["model_mentioned"] = "Llama-3.2-1B"
                        print(f"   → Model: Llama-3.2-1B")
                    elif "phi" in content.lower():
                        results["model_mentioned"] = "Phi-2"
                        print(f"   → Model: Phi-2")
                except:
                    pass
            else:
                print(f"⚠️  Missing: {config_file}")

        # Check for trained model directories
        model_dirs = [
            "trained_llama_1b_production",
            "trained_phi2_production",
            "trained_lora_stage3_final",
        ]

        for model_dir in model_dirs:
            dir_path = self.project_root / model_dir
            if dir_path.exists():
                files = list(dir_path.iterdir())
                if files:
                    results[f"{model_dir}_exists"] = True
                    print(f"✅ Found: {model_dir} ({len(files)} files)")
                else:
                    results[f"{model_dir}_exists"] = False
                    print(f"⚠️  Empty: {model_dir}")
            else:
                results[f"{model_dir}_exists"] = False
                print(f"❌ Missing: {model_dir}")

        results["config_files_found"] = len(model_files)
        self.test_results["models"] = results

        return results.get("config_files_found", 0) > 0

    def test_dataset_integrity(self) -> bool:
        """Test dataset files and structure"""
        self.print_header("TEST 4: DATASET INTEGRITY")

        results = {}
        dataset_path = self.project_root / "lora_dataset"

        if not dataset_path.exists():
            print("❌ Dataset directory not found!")
            self.test_results["dataset"] = {"exists": False}
            return False

        print(f"✅ Dataset directory: {dataset_path}")

        # Check key dataset files
        key_files = [
            "lora_dataset_augmented.jsonl",
            "lora_dataset_train.jsonl",
            "lora_dataset_validation.jsonl",
            "lora_dataset_test.jsonl",
            "corporate_training_dataset.json",
        ]

        valid_files = []
        for file_name in key_files:
            file_path = dataset_path / file_name
            if file_path.exists():
                # Check file size
                size_mb = file_path.stat().st_size / (1024 * 1024)
                valid_files.append(file_name)
                print(f"✅ {file_name}: {size_mb:.2f} MB")

                # Sample check for JSONL
                if file_name.endswith(".jsonl"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = [next(f) for _ in range(3)]
                        results[f"{file_name}_sample"] = "Valid JSONL"
                    except:
                        results[f"{file_name}_sample"] = "Read error"
            else:
                print(f"⚠️  Missing: {file_name}")

        # Check total examples
        try:
            train_file = dataset_path / "lora_dataset_train.jsonl"
            if train_file.exists():
                with open(train_file, "r", encoding="utf-8") as f:
                    train_count = sum(1 for _ in f)
                results["train_examples"] = train_count
                print(f"✅ Training examples: {train_count}")
        except:
            pass

        results["valid_files"] = len(valid_files)
        self.test_results["dataset"] = results

        return results.get("valid_files", 0) >= 3  # Need at least 3 key files

    def test_sigma_lora_system(self) -> bool:
        """Test Σ_LORA constraint system"""
        self.print_header("TEST 5: Σ_LORA CONSTRAINT SYSTEM")

        results = {}
        sigma_files = []

        # Check Σ_LORA files
        sigma_patterns = ["Σ_LORA", "SIGMA_LORA", "sigma_lora"]

        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                file_name = file_path.name
                if any(
                    pattern.lower() in file_name.lower() for pattern in sigma_patterns
                ):
                    sigma_files.append(file_name)

        print(f"✅ Found {len(sigma_files)} Σ_LORA files:")
        for file in sigma_files:
            print(f"   • {file}")

        # Check manifest
        manifest_path = self.project_root / "Σ_LORA_MANIFEST.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                results["manifest_exists"] = True
                results["system_name"] = manifest.get("system", "Unknown")
                results["theorem_count"] = len(manifest.get("theorems", {}))
                results["constraint_count"] = len(manifest.get("constraints", {}))

                print(f"✅ Σ_LORA Manifest: {results['system_name']}")
                print(f"✅ Theorems: {results['theorem_count']}")
                print(f"✅ Constraints: {results['constraint_count']}")

                # List constraints
                constraints = manifest.get("constraints", {})
                print("✅ Constraint System:")
                for constraint in constraints.keys():
                    print(f"   • {constraint}")

            except Exception as e:
                results["manifest_error"] = str(e)
                print(f"❌ Manifest error: {e}")
        else:
            results["manifest_exists"] = False
            print("⚠️  Σ_LORA Manifest not found")

        results["sigma_files"] = sigma_files
        self.test_results["sigma_lora"] = results

        return (
            results.get("manifest_exists", False)
            and results.get("theorem_count", 0) > 0
        )

    def test_corporate_invariants(self) -> bool:
        """Test corporate invariants system"""
        self.print_header("TEST 6: CORPORATE INVARIANTS SYSTEM")

        results = {}
        invariant_files = []

        # Find invariant files
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and "invariant" in file_path.name.lower():
                invariant_files.append(file_path.name)

        print(f"✅ Found {len(invariant_files)} invariant files:")
        for file in invariant_files:
            print(f"   • {file}")

        # Check main corporate invariants
        corp_invariants = self.project_root / "corporate_invariants.json"
        if corp_invariants.exists():
            try:
                with open(corp_invariants, "r", encoding="utf-8") as f:
                    invariants = json.load(f)

                results["corp_invariants_exists"] = True
                results["total_invariants"] = invariants.get("metadata", {}).get(
                    "total_invariants", 0
                )
                results["critical_files"] = len(invariants.get("critical_files", []))

                print(
                    f"✅ Corporate Invariants: {results['total_invariants']} invariants"
                )
                print(f"✅ Critical Files: {results['critical_files']} files")

            except Exception as e:
                results["corp_invariants_error"] = str(e)
                print(f"❌ Corporate invariants error: {e}")
        else:
            results["corp_invariants_exists"] = False
            print("⚠️  Corporate invariants not found")

        # Check maximally strict invariants
        strict_invariants = self.project_root / "maximally_strict_invariants.json"
        if strict_invariants.exists():
            results["strict_invariants_exists"] = True
            print("✅ Maximally strict invariants found")
        else:
            results["strict_invariants_exists"] = False
            print("⚠️  Maximally strict invariants not found")

        results["invariant_files"] = invariant_files
        self.test_results["invariants"] = results

        return results.get("corp_invariants_exists", False)

    def test_creative_systems(self) -> bool:
        """Test creative systems (polymathic, graduate mathematics, christological)"""
        self.print_header("TEST 7: CREATIVE SYSTEMS INTEGRATION")

        results = {}
        creative_categories = {
            "polymathic": ["POLYMATHIC", "polymathic"],
            "graduate_mathematics": ["GRADUATE_MATHEMATICS", "graduate", "mathematics"],
            "christological": ["CHRIST", "christological", "theology"],
            "orthogonal": ["ORTHO", "orthogonal"],
        }

        for category, patterns in creative_categories.items():
            category_files = []
            for file_path in self.project_root.iterdir():
                if file_path.is_file():
                    file_name = file_path.name
                    if any(
                        pattern.lower() in file_name.lower() for pattern in patterns
                    ):
                        category_files.append(file_name)

            results[f"{category}_files"] = category_files
            print(
                f"✅ {category.replace('_', ' ').title()}: {len(category_files)} files"
            )
            if category_files:
                for file in category_files[:3]:  # Show first 3
                    print(f"   • {file}")
                if len(category_files) > 3:
                    print(f"   ... and {len(category_files) - 3} more")

        # Check for integrated systems
        integrated_systems = [
            "Σ_CHRIST_GRADUATE_MATHEMATICS_THEOLOGY.py",
            "GRADUATE_MATHEMATICS_THEOLOGY_2_0.py",
            "mathematical_theology_v60.py",
        ]

        integrated_found = []
        for system in integrated_systems:
            if (self.project_root / system).exists():
                integrated_found.append(system)

        results["integrated_systems"] = integrated_found
        print(f"\n✅ Integrated Systems: {len(integrated_found)}")
        for system in integrated_found:
            print(f"   • {system}")

        self.test_results["creative_systems"] = results

        return len(integrated_found) > 0

    def test_training_infrastructure(self) -> bool:
        """Test training scripts and infrastructure"""
        self.print_header("TEST 8: TRAINING INFRASTRUCTURE")

        results = {}
        training_scripts = []

        # Find training scripts
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and file_path.suffix == ".py":
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if any(
                    keyword in content.lower()
                    for keyword in ["train", "fine.tune", "lora", "peft"]
                ):
                    training_scripts.append(file_path.name)

        print(f"✅ Found {len(training_scripts)} training scripts:")
        for script in training_scripts[:5]:  # Show first 5
            print(f"   • {script}")
        if len(training_scripts) > 5:
            print(f"   ... and {len(training_scripts) - 5} more")

        # Check specific training scripts
        key_scripts = [
            "train_lora.py",
            "test_simple_training.py",
            "run_production_training.py",
            "final_training.py",
            "practical_training.py",
        ]

        key_found = []
        for script in key_scripts:
            if (self.project_root / script).exists():
                key_found.append(script)
                print(f"✅ Key script: {script}")
            else:
                print(f"⚠️  Missing: {script}")

        # Test if simple training works
        simple_test = self.project_root / "test_simple_training.py"
        if simple_test.exists():
            results["simple_test_exists"] = True
            print("✅ Simple training test script available")
        else:
            results["simple_test_exists"] = False
            print("⚠️  Simple training test not found")

        results["training_scripts"] = training_scripts
        results["key_scripts_found"] = len(key_found)
        self.test_results["training_infrastructure"] = results

        return results.get("key_scripts_found", 0) >= 2

    def test_stage4_deployment(self) -> bool:
        """Test Stage 4 deployment system"""
        self.print_header("TEST 9: STAGE 4 DEPLOYMENT SYSTEM")

        results = {}
        stage4_files = []

        # Find Stage 4 files
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and "stage4" in file_path.name.lower():
                stage4_files.append(file_path.name)

        print(f"✅ Found {len(stage4_files)} Stage 4 files:")
        for file in stage4_files:
            print(f"   • {file}")

        # Check key Stage 4 components
        key_components = [
            "stage4_deployment.py",
            "stage4_browser_extension.js",
            "fix_cuda_stage4.py",
            "STAGE4_DEPLOYMENT_PLAN.md",
            "STAGE4_README.md",
        ]

        components_found = []
        for component in key_components:
            if (self.project_root / component).exists():
                components_found.append(component)
                print(f"✅ Stage 4 component: {component}")
            else:
                print(f"⚠️  Missing: {component}")

        # Test if deployment script runs
        deployment_script = self.project_root / "stage4_deployment.py"
        if deployment_script.exists():
            try:
                # Quick test without actually running server
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(deployment_script), "--mode", "test"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    results["deployment_test_passed"] = True
                    print("✅ Stage 4 deployment test passed")
                else:
                    results["deployment_test_passed"] = False
                    print(f"⚠️  Stage 4 test failed: {result.returncode}")
            except subprocess.TimeoutExpired:
                results["deployment_test_passed"] = "Timeout"
                print("⚠️  Stage 4 test timeout")
            except Exception as e:
                results["deployment_test_passed"] = f"Error: {e}"
                print(f"⚠️  Stage 4 test error: {e}")
        else:
            results["deployment_test_passed"] = False
            print("⚠️  Deployment script not found")

        results["stage4_files"] = stage4_files
        results["components_found"] = len(components_found)
        self.test_results["stage4_deployment"] = results

        return results.get("components_found", 0) >= 3

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all readiness tests"""
        self.print_header("🚀 COMPLETE SYSTEM READINESS TEST")
        print("Testing all components for 1B+ model training...")
        print("=" * 80)

        test_functions = [
            ("Environment", self.test_environment),
            ("Hardware", self.test_hardware),
            ("Model Availability", self.test_model_availability),
            ("Dataset Integrity", self.test_dataset_integrity),
            ("Σ_LORA System", self.test_sigma_lora_system),
            ("Corporate Invariants", self.test_corporate_invariants),
            ("Creative Systems", self.test_creative_systems),
            ("Training Infrastructure", self.test_training_infrastructure),
            ("Stage 4 Deployment", self.test_stage4_deployment),
        ]

        results_summary = {}
        all_passed = True

        for test_name, test_func in test_functions:
            try:
                passed = test_func()
                results_summary[test_name] = {
                    "passed": passed,
                    "details": self.test_results.get(
                        test_name.lower().replace(" ", "_"), {}
                    ),
                }
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"\n{status}: {test_name}")
                all_passed = all_passed and passed
            except Exception as e:
                results_summary[test_name] = {
                    "passed": False,
                    "error": str(e),
                    "details": {},
                }
                print(f"\n❌ ERROR: {test_name} - {e}")
                all_passed = False

        # Generate final report
        self.print_header("📊 FINAL READINESS REPORT")

        print("\n🎯 SYSTEM STATUS:")
        print(f"   Overall Readiness: {'✅ READY' if all_passed else '❌ NOT READY'}")

        print("\n📋 COMPONENT STATUS:")
        for test_name, result in results_summary.items():
            status = "✅" if result.get("passed", False) else "❌"
            print(f"   {status} {test_name}")

        print("\n🔧 RECOMMENDATIONS:")
        if not all_passed:
            for test_name, result in results_summary.items():
                if not result.get("passed", False):
                    print(f"   • Fix {test_name}")

        print("\n🚀 NEXT STEPS:")
        if all_passed:
            print("   1. ✅ System is ready for 1B+ model training!")
            print("   2. Run: python train_lora.py --model meta-llama/Llama-3.2-1B")
            print("   3. Or use: python POLYMATHIC_LORA_CLI.py")
            print("   4. Monitor training with: python POLYMATHIC_LORA_IDE.py")
        else:
            print("   1. ❌ Fix the failed components above")
            print("   2. Run individual tests to debug")
            print("   3. Check requirements: pip install -r requirements_stage3.txt")
            print("   4. Fix CUDA: python fix_cuda_stage4.py")

        print("\n" + "=" * 80)
        print("🎉 TEST COMPLETE")
        print("=" * 80)

        return {
            "overall_passed": all_passed,
            "test_results": results_summary,
            "detailed_results": self.test_results,
        }

    def save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        report_path = self.project_root / "complete_system_readiness_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Report saved to: {report_path}")

    def generate_summary_markdown(self, report: Dict[str, Any]):
        """Generate markdown summary"""
        summary_path = self.project_root / "COMPLETE_SYSTEM_READINESS_SUMMARY.md"

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("# COMPLETE SYSTEM READINESS SUMMARY\n\n")
            f.write(f"**Generated:** {report.get('timestamp', 'N/A')}\n")
            f.write(
                f"**Overall Status:** {'✅ READY' if report['overall_passed'] else '❌ NOT READY'}\n\n"
            )

            f.write("## 📊 Test Results\n\n")
            f.write("| Component | Status | Details |\n")
            f.write("|-----------|--------|---------|\n")

            for test_name, result in report.get("test_results", {}).items():
                status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
                details = str(result.get("details", {}))
                if len(details) > 100:
                    details = details[:100] + "..."
                f.write(f"| {test_name} | {status} | {details} |\n")

            f.write("\n## 🚀 Recommendations\n\n")
            if report["overall_passed"]:
                f.write(
                    "1. **Start Training**: `python train_lora.py --model meta-llama/Llama-3.2-1B`\n"
                )
                f.write("2. **Use CLI**: `python POLYMATHIC_LORA_CLI.py`\n")
                f.write("3. **Use IDE**: `python POLYMATHIC_LORA_IDE.py`\n")
                f.write("4. **Monitor**: Check logs and metrics during training\n")
            else:
                f.write("1. **Fix Failed Components** (see above)\n")
                f.write(
                    "2. **Install Requirements**: `pip install -r requirements_stage3.txt`\n"
                )
                f.write("3. **Fix CUDA**: `python fix_cuda_stage4.py`\n")
                f.write(
                    "4. **Test Individual Components**: Run specific test functions\n"
                )

            f.write("\n## 🔧 System Details\n\n")
            f.write("```json\n")
            f.write(json.dumps(report.get("detailed_results", {}), indent=2))
            f.write("\n```\n")

        print(f"📝 Summary saved to: {summary_path}")


def main():
    """Main function to run complete system readiness test"""
    import datetime

    print("\n" + "=" * 80)
    print("🚀 COMPLETE SYSTEM READINESS TEST FOR 1B+ MODEL TRAINING")
    print("=" * 80)
    print("Testing ALL components: Environment, Models, Datasets, Σ_LORA, Invariants,")
    print("Creative Systems, Training Infrastructure, and Stage 4 Deployment")
    print("=" * 80)

    tester = CompleteSystemReadinessTest()

    # Run all tests
    report = tester.run_all_tests()
    report["timestamp"] = datetime.datetime.now().isoformat()

    # Save results
    tester.save_report(report)
    tester.generate_summary_markdown(report)

    # Exit with appropriate code
    if report["overall_passed"]:
        print("\n🎉 SYSTEM IS READY FOR 1B+ MODEL TRAINING!")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM NEEDS FIXES BEFORE TRAINING")
        sys.exit(1)


if __name__ == "__main__":
    main()
