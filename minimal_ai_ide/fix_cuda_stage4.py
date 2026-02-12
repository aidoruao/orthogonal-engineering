"""
STAGE 4: CUDA FIX SCRIPT
Fix Python 3.14 + CUDA compatibility issue for production deployment
"""

import os
import subprocess
import sys
from pathlib import Path


class CUDAFixer:
    """Fix CUDA compatibility issues for Stage 4 deployment"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_name = "venv_stage4"
        self.venv_path = self.project_root / self.venv_name

    def check_current_environment(self):
        """Check current Python and CUDA status"""
        print("=" * 60)
        print("STAGE 4: CUDA COMPATIBILITY CHECK")
        print("=" * 60)

        try:
            import torch

            print(f"✓ PyTorch version: {torch.__version__}")
            print(f"✓ CUDA available: {torch.cuda.is_available()}")

            if torch.cuda.is_available():
                print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
                print(f"✓ CUDA version: {torch.version.cuda}")
                return True
            else:
                print("✗ CUDA not available (CPU-only PyTorch)")
                return False

        except ImportError:
            print("✗ PyTorch not installed")
            return False

    def check_python_version(self):
        """Check Python version compatibility"""
        print("\n" + "=" * 60)
        print("PYTHON VERSION CHECK")
        print("=" * 60)

        version = sys.version_info
        print(f"Current Python: {version.major}.{version.minor}.{version.micro}")

        # Python 3.14 has CUDA compatibility issues
        if version.major == 3 and version.minor == 14:
            print("⚠️  Python 3.14 detected - known CUDA compatibility issues")
            print("   Recommendation: Use Python 3.11 or 3.12 for CUDA")
            return False
        elif version.major == 3 and version.minor in [11, 12]:
            print("✓ Python 3.11/3.12 detected - good CUDA compatibility")
            return True
        else:
            print(f"ℹ️  Python {version.major}.{version.minor} - may work with CUDA")
            return True

    def create_compatible_environment(self):
        """Create a Python 3.11/3.12 virtual environment"""
        print("\n" + "=" * 60)
        print("CREATING COMPATIBLE ENVIRONMENT")
        print("=" * 60)

        # Check if Python 3.11 or 3.12 is available
        python_versions = []

        for version in ["3.11", "3.12", "python3.11", "python3.12"]:
            try:
                result = subprocess.run(
                    [version, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    python_versions.append(version)
                    print(f"✓ Found: {version}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        if not python_versions:
            print("✗ No compatible Python version found (3.11 or 3.12)")
            print("\nOPTIONS:")
            print("1. Install Python 3.11 from python.org")
            print("2. Use WSL2 with Ubuntu")
            print("3. Use cloud GPU (Google Colab)")
            return None

        # Use first compatible version
        python_cmd = python_versions[0]

        # Create virtual environment
        print(f"\nCreating virtual environment with {python_cmd}...")

        try:
            # Create venv
            subprocess.run(
                [python_cmd, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Virtual environment created: {self.venv_path}")

            # Get pip path
            if os.name == "nt":  # Windows
                pip_path = self.venv_path / "Scripts" / "pip.exe"
                python_path = self.venv_path / "Scripts" / "python.exe"
            else:  # Linux/Mac
                pip_path = self.venv_path / "bin" / "pip"
                python_path = self.venv_path / "bin" / "python"

            # Install PyTorch with CUDA
            print("\nInstalling PyTorch with CUDA support...")

            # Try CUDA 11.8 (most compatible)
            torch_command = [
                str(pip_path),
                "install",
                "torch",
                "torchvision",
                "torchaudio",
                "--index-url",
                "https://download.pytorch.org/whl/cu118",
            ]

            result = subprocess.run(
                torch_command,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            if result.returncode == 0:
                print("✓ PyTorch with CUDA installed successfully")
            else:
                print("⚠️  CUDA 11.8 failed, trying CPU version...")
                subprocess.run(
                    [str(pip_path), "install", "torch", "torchvision", "torchaudio"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                print("✓ PyTorch CPU version installed")

            # Install other requirements
            print("\nInstalling other requirements...")
            requirements_file = self.project_root / "requirements_stage3.txt"

            if requirements_file.exists():
                subprocess.run(
                    [str(pip_path), "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                print("✓ Requirements installed")
            else:
                # Install basic requirements
                basic_reqs = [
                    "transformers>=4.30.0,<5.0.0",
                    "peft>=0.4.0,<1.0.0",
                    "accelerate>=0.20.0,<1.0.0",
                    "safetensors>=0.3.0,<1.0.0",
                    "numpy>=1.21.0,<2.0.0",
                    "tqdm>=4.64.0,<5.0.0",
                ]

                for req in basic_reqs:
                    subprocess.run(
                        [str(pip_path), "install", req],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                print("✓ Basic requirements installed")

            return str(python_path)

        except subprocess.CalledProcessError as e:
            print(f"✗ Error creating environment: {e}")
            return None
        except subprocess.TimeoutExpired:
            print("✗ Timeout creating environment")
            return None

    def test_cuda_in_new_env(self, python_path):
        """Test CUDA in the new environment"""
        print("\n" + "=" * 60)
        print("TESTING CUDA IN NEW ENVIRONMENT")
        print("=" * 60)

        test_script = """
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")

    # Test tensor operations
    x = torch.randn(3, 3).cuda()
    y = torch.randn(3, 3).cuda()
    z = x @ y
    print(f"GPU tensor operation successful: {z.shape}")

    # Test memory
    print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
    print(f"GPU memory cached: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
else:
    print("CUDA not available - using CPU")
    x = torch.randn(3, 3)
    y = torch.randn(3, 3)
    z = x @ y
    print(f"CPU tensor operation successful: {z.shape}")
"""

        try:
            result = subprocess.run(
                [python_path, "-c", test_script],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(result.stdout)

            if "CUDA available: True" in result.stdout:
                print("\n✅ CUDA WORKING IN NEW ENVIRONMENT!")
                return True
            else:
                print("\n⚠️  CUDA not available in new environment")
                return False

        except subprocess.TimeoutExpired:
            print("✗ Timeout testing CUDA")
            return False

    def create_activation_script(self, python_path):
        """Create script to activate the new environment"""
        print("\n" + "=" * 60)
        print("CREATING ACTIVATION SCRIPTS")
        print("=" * 60)

        # Windows batch file
        if os.name == "nt":
            bat_content = f"""@echo off
REM Stage 4 CUDA-Compatible Environment
echo Activating Stage 4 CUDA environment...
call "{self.venv_path}\\Scripts\\activate.bat"
echo Environment activated!
echo Python: {python_path}
python --version
python -c "import torch; print(f'CUDA: {{torch.cuda.is_available()}}')"
"""

            bat_file = self.project_root / "activate_stage4.bat"
            bat_file.write_text(bat_content)
            print(f"✓ Created: {bat_file}")

            # Also create run script
            run_bat = self.project_root / "run_stage4.bat"
            run_content = f"""@echo off
call "{bat_file}"
python stage4_deployment.py %*
"""
            run_bat.write_text(run_content)
            print(f"✓ Created: {run_bat}")

        # Linux/Mac shell script
        shell_content = f"""#!/bin/bash
# Stage 4 CUDA-Compatible Environment
echo "Activating Stage 4 CUDA environment..."
source "{self.venv_path}/bin/activate"
echo "Environment activated!"
echo "Python: {python_path}"
python --version
python -c "import torch; print(f'CUDA: {{torch.cuda.is_available()}}')"
"""

        shell_file = self.project_root / "activate_stage4.sh"
        shell_file.write_text(shell_content)

        # Make executable
        try:
            shell_file.chmod(0o755)
        except:
            pass  # Windows doesn't have chmod

        print(f"✓ Created: {shell_file}")

        # Create run script
        run_sh = self.project_root / "run_stage4.sh"
        run_sh_content = f"""#!/bin/bash
source "{shell_file}"
python stage4_deployment.py "$@"
"""
        run_sh.write_text(run_sh_content)

        try:
            run_sh.chmod(0o755)
        except:
            pass

        print(f"✓ Created: {run_sh}")

    def create_cloud_fallback(self):
        """Create cloud deployment option as fallback"""
        print("\n" + "=" * 60)
        print("CLOUD DEPLOYMENT FALLBACK")
        print("=" * 60)

        colab_notebook = """# Stage 4: Corporate Overreach Protection - Google Colab
# Run this in Google Colab for free GPU access

!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install transformers peft accelerate safetensors

# Clone repository
!git clone https://github.com/yourusername/corporate-overreach-protection.git
%cd corporate-overreach-protection

# Test CUDA
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Run Stage 4 deployment
!python stage4_deployment.py --cloud
"""

        colab_file = self.project_root / "stage4_colab.ipynb"

        # Create simple text version
        colab_file.write_text("# Google Colab Notebook\n\n" + colab_notebook)
        print(f"✓ Created: {colab_file}")

        # Create requirements for cloud
        cloud_reqs = self.project_root / "requirements_cloud.txt"
        cloud_reqs.write_text("""# Cloud deployment requirements
torch>=2.0.0,<3.0.0
transformers>=4.30.0,<5.0.0
peft>=0.4.0,<1.0.0
accelerate>=0.20.0,<1.0.0
safetensors>=0.3.0,<1.0.0
fastapi>=0.104.0,<1.0.0
uvicorn>=0.24.0,<1.0.0
pydantic>=2.0.0,<3.0.0
""")
        print(f"✓ Created: {cloud_reqs}")

    def run(self):
        """Run the complete CUDA fix process"""
        print("\n" + "=" * 60)
        print("STAGE 4 CUDA FIX - STARTING")
        print("=" * 60)

        # Step 1: Check current environment
        cuda_working = self.check_current_environment()

        if cuda_working:
            print("\n✅ CUDA already working! No fix needed.")
            return True

        # Step 2: Check Python version
        python_ok = self.check_python_version()

        if not python_ok:
            print("\n⚠️  Python version incompatible with CUDA")
            print("   Creating compatible environment...")

        # Step 3: Create compatible environment
        python_path = self.create_compatible_environment()

        if not python_path:
            print("\n❌ Failed to create compatible environment")
            print("   Creating cloud fallback option...")
            self.create_cloud_fallback()
            return False

        # Step 4: Test CUDA in new environment
        cuda_working = self.test_cuda_in_new_env(python_path)

        # Step 5: Create activation scripts
        self.create_activation_script(python_path)

        # Step 6: Create cloud fallback
        self.create_cloud_fallback()

        if cuda_working:
            print("\n" + "=" * 60)
            print("✅ STAGE 4 CUDA FIX COMPLETE!")
            print("=" * 60)
            print("\nNEXT STEPS:")
            print(
                f"1. Run: activate_stage4.bat (Windows) or source activate_stage4.sh (Linux/Mac)"
            )
            print(
                f'2. Test: python -c "import torch; print(torch.cuda.is_available())"'
            )
            print(f"3. Run Stage 4: run_stage4.bat or ./run_stage4.sh")
            return True
        else:
            print("\n" + "=" * 60)
            print("⚠️  STAGE 4 CUDA FIX PARTIAL")
            print("=" * 60)
            print("\nCUDA could not be enabled locally.")
            print("OPTIONS:")
            print("1. Use cloud GPU (Google Colab): stage4_colab.ipynb")
            print("2. Continue with CPU (slower but works)")
            print("3. Install Python 3.11/3.12 manually")
            return False


def main():
    """Main entry point"""
    fixer = CUDAFixer()
    success = fixer.run()

    if success:
        print("\n🎉 Stage 4 CUDA fix successful!")
        print("   Ready for production deployment.")
        return 0
    else:
        print("\n⚠️  Stage 4 CUDA fix partially successful")
        print("   Cloud deployment option created.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
