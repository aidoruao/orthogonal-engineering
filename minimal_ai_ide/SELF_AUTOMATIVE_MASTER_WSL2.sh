#!/bin/bash
# SELF_AUTOMATIVE_MASTER_WSL2.sh
# ==============================
# WSL2/Linux Setup and Launcher for Self-Automative Master System
#
# This script:
# 1. Sets up WSL2/Linux environment for the self-automative master system
# 2. Installs required dependencies
# 3. Configures cross-platform compatibility
# 4. Launches the autonomous system with Popperian validation
# 5. Provides monitoring and management tools

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/venv_wsl2"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements_v57_lora.txt"
LOG_DIR="$PROJECT_ROOT/logs"
REPORT_DIR="$PROJECT_ROOT/system_reports"

# Print colored message
print_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running in WSL2
check_wsl2() {
    if grep -q -i "microsoft" /proc/version 2>/dev/null || grep -q -i "wsl" /proc/version 2>/dev/null; then
        print_success "Running in WSL2"
        return 0
    elif [[ "$(uname -s)" == "Linux" ]]; then
        print_success "Running on Linux"
        return 0
    else
        print_error "Not running on WSL2 or Linux"
        return 1
    fi
}

# Setup directory structure
setup_directories() {
    print_message "Setting up directory structure..."

    mkdir -p "$LOG_DIR"
    mkdir -p "$REPORT_DIR"
    mkdir -p "$PROJECT_ROOT/trained_lora"
    mkdir -p "$PROJECT_ROOT/lora_dataset"

    print_success "Directories created"
}

# Check and install system dependencies
install_system_deps() {
    print_message "Installing system dependencies..."

    # Update package list
    sudo apt-get update

    # Install Python and development tools
    sudo apt-get install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        build-essential \
        git \
        curl \
        wget \
        htop \
        tmux

    # Install CUDA dependencies if NVIDIA GPU is available
    if command -v nvidia-smi &> /dev/null; then
        print_message "NVIDIA GPU detected, installing CUDA dependencies..."
        sudo apt-get install -y \
            nvidia-cuda-toolkit \
            nvidia-driver-535
    fi

    print_success "System dependencies installed"
}

# Setup Python virtual environment
setup_python_env() {
    print_message "Setting up Python virtual environment..."

    # Create virtual environment
    python3.11 -m venv "$VENV_DIR"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install requirements
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        print_message "Installing Python requirements..."
        pip install -r "$REQUIREMENTS_FILE"
    else
        print_warning "Requirements file not found, installing core packages..."
        pip install \
            torch torchvision torchaudio \
            transformers \
            peft \
            accelerate \
            datasets \
            numpy \
            pandas \
            scipy \
            matplotlib \
            seaborn \
            jupyter \
            ipython \
            aiohttp \
            prometheus-client \
            z3-solver \
            networkx \
            sympy \
            graphviz \
            pytest \
            black \
            ruff \
            mypy
    fi

    print_success "Python environment setup complete"
}

# Setup Σ_LORA constraint system
setup_sigma_lora() {
    print_message "Setting up Σ_LORA constraint system..."

    # Check if Σ_LORA files exist
    if [[ -f "$PROJECT_ROOT/Σ_LORA_MANIFEST.json" ]]; then
        print_success "Σ_LORA manifest found"
    else
        print_warning "Σ_LORA manifest not found, creating basic structure..."

        cat > "$PROJECT_ROOT/Σ_LORA_MANIFEST.json" << 'EOF'
{
  "system": "Σ_LORA_MAXIMAL_MATHEMATICS_v1.0",
  "timestamp": "$(date -Iseconds)",
  "constraints": {
    "LOGOS": "Truth and logical consistency",
    "CHALCEDON": "Hypostatic union preservation",
    "GRACE": "Undeserved favor and forgiveness",
    "ESCHATON": "Forward-looking redemptive purpose",
    "AGAPE": "Self-sacrificial love",
    "KENOSIS": "Self-emptying for greater purpose"
  },
  "mathematical_properties": {
    "category_theory": "System as category with objects and morphisms",
    "constraint_lattice": "Complete lattice of constraints",
    "hash_algebra": "Commutative monoid for verification",
    "functoriality": "System transformations preserve structure"
  }
}
EOF
    fi

    print_success "Σ_LORA constraint system setup complete"
}

# Setup monitoring and logging
setup_monitoring() {
    print_message "Setting up monitoring and logging..."

    # Create log rotation configuration
    cat > "$PROJECT_ROOT/logrotate_self_automative" << 'EOF'
$LOG_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}
EOF

    # Create systemd service file for WSL2 (if systemd is available)
    if systemctl --user list-units --type=service | grep -q systemd; then
        cat > "$PROJECT_ROOT/self-automative-master.service" << EOF
[Unit]
Description=Self-Automative Master System
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/python $PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py --run-continuous --cycles -1 --interval 300
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/system.log
StandardError=append:$LOG_DIR/error.log

[Install]
WantedBy=default.target
EOF

        # Enable the service
        systemctl --user enable "$PROJECT_ROOT/self-automative-master.service"
        print_success "Systemd service configured"
    fi

    print_success "Monitoring setup complete"
}

# Run Popperian validation tests
run_popperian_tests() {
    print_message "Running Popperian falsification tests..."

    source "$VENV_DIR/bin/activate"

    python3 -c "
import asyncio
import sys
sys.path.insert(0, '$PROJECT_ROOT')

async def run_tests():
    try:
        from SELF_AUTOMATIVE_MASTER_COMPLETE import PopperianValidator, Σ_LORA_ConstraintExecutor
        import asyncio
        from pathlib import Path

        root_dir = Path('$PROJECT_ROOT')

        # Initialize validators
        popperian = PopperianValidator(root_dir)
        constraint_executor = Σ_LORA_ConstraintExecutor(root_dir)

        # Create test functions
        def test_system_exists():
            import os
            return os.path.exists('$PROJECT_ROOT')

        def test_python_works():
            try:
                import torch
                import transformers
                return True
            except:
                return False

        def test_constraints_defined():
            constraints = constraint_executor.constraints
            return len(constraints) == 6

        # Register tests
        popperian.register_falsification_test('system_exists', test_system_exists)
        popperian.register_falsification_test('python_works', test_python_works)
        popperian.register_falsification_test('constraints_defined', test_constraints_defined)

        # Run tests
        results = await popperian.run_falsification_suite()

        print('Popperian Test Results:')
        for test_name, result in results.items():
            print(f'  {test_name}: {result.value}')

        # Count results
        corroborated = sum(1 for r in results.values() if r.value == 'corroborated')
        falsified = sum(1 for r in results.values() if r.value == 'falsified')

        print(f'\\nSummary: {corroborated} corroborated, {falsified} falsified')

        return falsified == 0

    except Exception as e:
        print(f'Error running Popperian tests: {e}')
        return False

# Run tests
success = asyncio.run(run_tests())
sys.exit(0 if success else 1)
"

    if [[ $? -eq 0 ]]; then
        print_success "Popperian tests passed"
    else
        print_error "Popperian tests failed"
        return 1
    fi
}

# Run Σ_LORA constraint verification
run_constraint_verification() {
    print_message "Running Σ_LORA constraint verification..."

    source "$VENV_DIR/bin/activate"

    python3 -c "
import asyncio
import json
import sys
sys.path.insert(0, '$PROJECT_ROOT')

async def verify_constraints():
    try:
        from SELF_AUTOMATIVE_MASTER_COMPLETE import Σ_LORA_ConstraintExecutor
        from pathlib import Path

        root_dir = Path('$PROJECT_ROOT')
        executor = Σ_LORA_ConstraintExecutor(root_dir)

        # Test constraints on the system itself
        test_component = {
            'name': 'Self-Automative Master System',
            'description': 'Autonomous AI controller with Popperian validation',
            'components': ['PopperianValidator', 'Σ_LORA_ConstraintExecutor', 'LoRA_LLM_Integrator']
        }

        results = await executor.verify_all_constraints(test_component)

        print('Σ_LORA Constraint Verification Results:')
        for constraint_name, (satisfied, message) in results.items():
            status = '✓ SATISFIED' if satisfied else '✗ VIOLATED'
            print(f'  {constraint_name}: {status}')
            print(f'     {message}')

        # Calculate compliance score
        satisfied_count = sum(1 for r in results.values() if r[0])
        total_constraints = len(results)
        compliance_score = satisfied_count / total_constraints if total_constraints > 0 else 0

        print(f'\\nCompliance Score: {compliance_score:.2f} ({satisfied_count}/{total_constraints})')

        # Save results
        with open('$REPORT_DIR/constraint_verification.json', 'w') as f:
            json.dump({
                'timestamp': '$(date -Iseconds)',
                'results': {k: {'satisfied': v[0], 'message': v[1]} for k, v in results.items()},
                'compliance_score': compliance_score
            }, f, indent=2)

        return compliance_score >= 0.8

    except Exception as e:
        print(f'Error verifying constraints: {e}')
        return False

# Run verification
success = asyncio.run(verify_constraints())
sys.exit(0 if success else 1)
"

    if [[ $? -eq 0 ]]; then
        print_success "Σ_LORA constraint verification passed"
    else
        print_error "Σ_LORA constraint verification failed"
        return 1
    fi
}

# Launch the self-automative master system
launch_system() {
    local mode="$1"
    local cycles="${2:--1}"
    local interval="${3:-60}"

    print_message "Launching Self-Automative Master System..."

    source "$VENV_DIR/bin/activate"

    case "$mode" in
        "single")
            print_message "Running single autonomous cycle..."
            python "$PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py" --run-cycle
            ;;
        "continuous")
            print_message "Running continuous autonomous cycles (cycles: $cycles, interval: ${interval}s)..."
            python "$PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py" \
                --run-continuous \
                --cycles "$cycles" \
                --interval "$interval"
            ;;
        "interactive")
            print_message "Starting interactive mode..."
            python "$PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py" --init
            python "$PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py" --report
            ;;
        "train")
            print_message "Starting training mode..."
            python "$PROJECT_ROOT/SELF_AUTOMATIVE_MASTER_COMPLETE.py" --init
            # Additional training commands can be added here
            ;;
        *)
            print_error "Unknown mode: $mode"
            return 1
            ;;
    esac
}

# Generate system report
generate_report() {
    print_message "Generating system report..."

    source "$VENV_DIR/bin/activate"

    python3 -c "
import json
import sys
import platform
import subprocess
from datetime import datetime

def get_system_info():
    info = {
        'timestamp': datetime.now().isoformat(),
        'system': {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'memory': {},
            'disk': {}
        },
        'project': {
            'directory': '$PROJECT_ROOT',
            'wsl2': $(check_wsl2 && echo 'true' || echo 'false'),
            'venv': '$VENV_DIR'
        },
        'components': {
            'sigma_lora': '$(ls -la "$PROJECT_ROOT/Σ_LORA"* 2>/dev/null | wc -l) files',
            'trained_models': '$(ls -la "$PROJECT_ROOT/trained_lora" 2>/dev/null | wc -l) models',
            'scripts': '$(find "$PROJECT_ROOT" -name "*.py" | wc -l) Python scripts'
        }
    }

    # Get memory info
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemTotal' in line:
                    info['system']['memory']['total'] = line.split()[1] + ' kB'
                elif 'MemAvailable' in line:
                    info['system']['memory']['available'] = line.split()[1] + ' kB'
    except:
        pass

    # Get disk info
    try:
        result = subprocess.run(['df', '-h', '$PROJECT_ROOT'], capture_output=True, text=True)
        info['system']['disk'] = result.stdout.strip()
    except:
        pass

    return info

info = get_system_info()
report_file = '$REPORT_DIR/system_report_$(date +%Y%m%d_%H%M%S).json'

with open(report_file, 'w') as f:
    json.dump(info, f, indent=2)

print(f'System report generated: {report_file}')
print(json.dumps(info, indent=2))
"

    print_success "System report generated"
}

# Main menu
show_menu() {
    while true; do
        echo ""
        echo "========================================="
        echo "  SELF-AUTOMATIVE MASTER SYSTEM - WSL2  "
        echo "========================================="
        echo ""
        echo "1.  Full Setup (First Time)"
        echo "2.  Run Popperian Tests"
        echo "3.  Run Σ_LORA Constraint Verification"
        echo "4.  Run Single Autonomous Cycle"
        echo "5.  Run Continuous Autonomous Cycles"
        echo "6.  Start Interactive Mode"
        echo "7.  Start Training Mode"
        echo "8.  Generate System Report"
        echo "9.  Monitor System Logs"
        echo "10. View System Reports"
        echo "11. Exit"
        echo ""
        read -p "Select option [1-11]: " choice

        case $choice in
            1)
                check_wsl2
                setup_directories
                install_system_deps
                setup_python_env
                setup_sigma_lora
                setup_monitoring
                run_popperian_tests
                run_constraint_verification
                ;;
            2)
                run_popperian_tests
                ;;
            3)
                run_constraint_verification
                ;;
            4)
                launch_system "single"
                ;;
            5)
                read -p "Number of cycles (-1 for infinite): " cycles
                read -p "Interval between cycles (seconds): " interval
                launch_system "continuous" "$cycles" "$interval"
                ;;
            6)
                launch_system "interactive"
                ;;
            7)
                launch_system "train"
                ;;
            8)
                generate_report
                ;;
            9)
                tail -f "$LOG_DIR/system.log"
                ;;
            10)
                ls -la "$REPORT_DIR/"
                read -p "Enter report filename to view: " report_file
                if [[ -f "$REPORT_DIR/$report_file" ]]; then
                    cat "$REPORT_DIR/$report_file" | python3 -m json.tool
                else
                    print_error "Report not found"
                fi
                ;;
            11)
                print_message "Exiting Self-Automative Master System"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
}

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Self-Automative Master System - WSL2/Linux Launcher"
    echo ""
    echo "Options:"
    echo "  --setup           Run full system setup (first time)"
    echo "  --test            Run all validation tests"
    echo "  --run MODE        Run system in specified mode"
    echo "                    MODE: single, continuous, interactive, train"
    echo "  --report          Generate system report"
    echo "  --monitor         Monitor system logs"
    echo "  --menu            Show interactive menu"
    echo "  --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --setup        # First time setup"
    echo "  $0 --test         # Run validation tests"
    echo "  $0 --run single   # Run single autonomous cycle"
    echo "  $0 --menu         # Show interactive menu"
}

# Parse command line arguments
parse_args() {
    if [[ $# -eq 0 ]]; then
        show_menu
        exit 0
    fi

    case "$1" in
        --setup)
            check_wsl2
            setup_directories
            install_system_deps
            setup_python_env
            setup_sigma_lora
            setup_monitoring
            run_popperian_tests
            run_constraint_verification
            print_success "Setup complete!"
            ;;
        --test)
            run_popperian_tests
            run_constraint_verification
            ;;
        --run)
            if [[ $# -lt 2 ]]; then
                print_error "Mode required for --run option"
                show_help
                exit 1
            fi
            mode="$2"
            cycles="${3:--1}"
            interval="${4:-60}"
            launch_system "$mode" "$cycles" "$interval"
            ;;
        --report)
            generate_report
            ;;
        --monitor)
            tail -f "$LOG_DIR/system.log"
            ;;
        --menu)
            show_menu
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Main execution
main() {
    print_message "========================================="
    print_message "  SELF-AUTOMATIVE MASTER SYSTEM - WSL2  "
    print_message "========================================="
    print_message "Project Root: $PROJECT_ROOT"
    print_message "Timestamp: $(date)"
    print_message ""

    # Check WSL2/Linux
    if ! check_wsl2; then
        print_error "This script requires WSL2 or Linux"
        exit 1
    fi

    # Parse command line arguments
    parse_args "$@"
}

# Run main function
main "$@"
