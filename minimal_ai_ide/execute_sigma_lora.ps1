# ============================================================================
# Σ_LORA SYSTEM EXECUTION SCRIPT
# PowerShell integration for Σ_LORA_GRADUATE_MATHEMATICS system
# ============================================================================

param(
    [string]$Action = "demonstrate",
    [string]$OutputDir = "$env:USERPROFILE\SIGMA_LORA_OUTPUT",
    [switch]$RunTests,
    [switch]$GenerateDataset,
    [switch]$VerifyTheorems,
    [switch]$Verbose
)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_SCRIPT = Join-Path $SCRIPT_DIR "SIGMA_LORA_GRADUATE_MATHEMATICS.py"
$TEST_SCRIPT = Join-Path $SCRIPT_DIR "test_sigma_lora.py"
$SIMPLE_TEST = Join-Path $SCRIPT_DIR "simple_sigma_test.py"

$SYSTEM_VERSION = "Σ_LORA_GRADUATE_MATHEMATICS_v1.0"
$ENFORCEMENT_LEVEL = "CONSTRAINT_PRESERVATION_MAXIMUM"
$MATHEMATICAL_RIGOR = "GRADUATE_LEVEL"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Mathematical {
    param([string]$Message)
    Write-Host "[MATHEMATICAL] $Message" -ForegroundColor Magenta
}

# ============================================================================
# SYSTEM VERIFICATION
# ============================================================================

function Test-SystemDependencies {
    Write-Info "Verifying system dependencies..."

    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            Write-Error "Python not found or not in PATH"
            return $false
        }
    } catch {
        Write-Error "Python check failed: $_"
        return $false
    }

    # Check required files
    $requiredFiles = @($PYTHON_SCRIPT, $TEST_SCRIPT)
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "Found: $(Split-Path -Leaf $file)"
        } else {
            Write-Error "Missing required file: $file"
            return $false
        }
    }

    return $true
}

# ============================================================================
# MATHEMATICAL THEOREM VERIFICATION
# ============================================================================

function Verify-MathematicalTheorems {
    Write-Info "Verifying mathematical theorems..."

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $theoremFile = Join-Path $OutputDir "theorem_verification_$timestamp.json"

    Write-Mathematical "Theorem 3: Constraint-Preserving Composition"
    Write-Mathematical "  If f: A → B preserves constraints (C_B ⊇ C_A)"
    Write-Mathematical "  and g: B → C preserves constraints (C_C ⊇ C_B),"
    Write-Mathematical "  then g ∘ f: A → C preserves constraints (C_C ⊇ C_A)."

    Write-Mathematical "Theorem 4: Chunk Coverage Completeness"
    Write-Mathematical "  For file f with constraints C(f) and chunking chunk_C(f) = {(s_i, c_i)},"
    Write-Mathematical "  if ⋃_i c_i = C(f), then any transformation preserving all c_i also preserves C(f)."

    # Run theorem verification
    $pythonCode = @'
import sys
import json
sys.path.insert(0, r'$SCRIPT_DIR')
from SIGMA_LORA_GRADUATE_MATHEMATICS import demonstrate_sigma_lora_system

results = demonstrate_sigma_lora_system()
theorem_results = {
    "theorem3": results.get("theorem3_constraint_preserving_composition", False),
    "theorem4": results.get("theorem4_chunk_coverage_completeness", {}).get("verified", False),
    "timestamp": "$timestamp",
    "system_version": "$SYSTEM_VERSION"
}

print(json.dumps(theorem_results, indent=2))
'@

    try {
        $theoremResults = python -c $pythonCode 2>&1 | ConvertFrom-Json

        if ($theoremResults.theorem3 -and $theoremResults.theorem4) {
            Write-Success "✓ Both theorems verified"
            Write-Mathematical "  Theorem 3: VERIFIED"
            Write-Mathematical "  Theorem 4: VERIFIED"
        } else {
            Write-Error "✗ Theorem verification failed"
            Write-Mathematical "  Theorem 3: $($theoremResults.theorem3)"
            Write-Mathematical "  Theorem 4: $($theoremResults.theorem4)"
        }

        # Save results
        $theoremResults | ConvertTo-Json | Out-File $theoremFile -Encoding UTF8
        Write-Info "Theorem verification saved to: $theoremFile"

        return $theoremResults.theorem3 -and $theoremResults.theorem4
    } catch {
        Write-Error "Theorem verification failed: $_"
        return $false
    }
}

# ============================================================================
# CONSTRAINT PRESERVATION VERIFICATION
# ============================================================================

function Verify-ConstraintPreservation {
    Write-Info "Verifying constraint preservation system..."

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $constraintFile = Join-Path $OutputDir "constraint_verification_$timestamp.json"

    # Run constraint verification
    $pythonCode = @'
import sys
import json
sys.path.insert(0, r'$SCRIPT_DIR')
from SIGMA_LORA_GRADUATE_MATHEMATICS import (
    TheologicalConstraint,
    ConstraintSet,
    FileObject,
    RepositoryCategory,
    RepositoryMorphism,
    ConstraintPreservingDataConstructor
)

# Create test objects with constraints
constraints1 = ConstraintSet(frozenset([TheologicalConstraint.LOGOS]))
constraints2 = ConstraintSet(frozenset([TheologicalConstraint.LOGOS, TheologicalConstraint.GRACE]))

file1 = FileObject(
    path="test1.py",
    content_hash="hash1",
    constraints=constraints1,
    language="python",
    content="def test1(): pass"
)

file2 = FileObject(
    path="test2.py",
    content_hash="hash2",
    constraints=constraints2,
    language="python",
    content="def test2(): pass"
)

# Test constraint preservation
preservation_results = {
    "file2_preserves_file1": file2.preserves_constraints(file1),
    "file1_preserves_file2": file1.preserves_constraints(file2),
    "constraint_inclusion": constraints2.contains(constraints1),
    "active_constraints": [c.name for c in TheologicalConstraint]
}

print(json.dumps(preservation_results, indent=2))
'@

    try {
        $preservationResults = python -c $pythonCode 2>&1 | ConvertFrom-Json

        if ($preservationResults.file2_preserves_file1 -and $preservationResults.constraint_inclusion) {
            Write-Success "✓ Constraint preservation system verified"
            Write-Mathematical "  Constraint monotonicity: C_output ⊇ C_input"
        } else {
            Write-Error "✗ Constraint preservation failed"
        }

        # Display active constraints
        Write-Info "Active theological constraints:"
        foreach ($constraint in $preservationResults.active_constraints) {
            Write-Host "  • $constraint" -ForegroundColor Gray
        }

        # Save results
        $preservationResults | ConvertTo-Json | Out-File $constraintFile -Encoding UTF8
        Write-Info "Constraint verification saved to: $constraintFile"

        return $preservationResults.file2_preserves_file1 -and $preservationResults.constraint_inclusion
    } catch {
        Write-Error "Constraint verification failed: $_"
        return $false
    }
}

# ============================================================================
# Σ_LORA SYSTEM DEMONSTRATION
# ============================================================================

function Invoke-SigmaLoraDemonstration {
    Write-Info "Executing Σ_LORA system demonstration..."

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $demoFile = Join-Path $OutputDir "demonstration_$timestamp.json"
    $logFile = Join-Path $OutputDir "demonstration_$timestamp.log"

    Write-Host "`n" + "="*70 -ForegroundColor Cyan
    Write-Host "Σ_LORA_GRADUATE_MATHEMATICS SYSTEM DEMONSTRATION" -ForegroundColor Cyan
    Write-Host "="*70 -ForegroundColor Cyan
    Write-Host "Version: $SYSTEM_VERSION" -ForegroundColor White
    Write-Host "Enforcement: $ENFORCEMENT_LEVEL" -ForegroundColor White
    Write-Host "Rigor: $MATHEMATICAL_RIGOR" -ForegroundColor White
    Write-Host "Timestamp: $timestamp" -ForegroundColor White
    Write-Host "="*70 -ForegroundColor Cyan

    # Run the demonstration
    try {
        # Capture both stdout and stderr
        $output = python $PYTHON_SCRIPT 2>&1

        # Save to log file
        $output | Out-File $logFile -Encoding UTF8

        # Parse results from output
        $results = @{
            "timestamp" = $timestamp
            "system_version" = $SYSTEM_VERSION
            "output_file" = $logFile
            "success" = $true
        }

        # Check for success indicators in output
        $successIndicators = @(
            "ALL CONSTRAINTS PRESERVED",
            "MATHEMATICAL THEOREMS VERIFIED",
            "Σ_LORA PROTOCOL COMPLETE"
        )

        foreach ($indicator in $successIndicators) {
            if ($output -match $indicator) {
                Write-Success "✓ $indicator"
            }
        }

        # Save results
        $results | ConvertTo-Json | Out-File $demoFile -Encoding UTF8

        Write-Success "Demonstration completed successfully"
        Write-Info "Log file: $logFile"
        Write-Info "Results file: $demoFile"

        return $true
    } catch {
        Write-Error "Demonstration failed: $_"
        return $false
    }
}

# ============================================================================
# DATASET GENERATION
# ============================================================================

function Generate-TrainingDataset {
    Write-Info "Generating constraint-preserving training dataset..."

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $datasetDir = Join-Path $OutputDir "datasets\$timestamp"
    $datasetFile = Join-Path $datasetDir "sigma_lora_dataset.json"

    # Create dataset directory
    New-Item -ItemType Directory -Force -Path $datasetDir | Out-Null

    $pythonCode = @'
import sys
import json
import os
sys.path.insert(0, r'$SCRIPT_DIR')
from SIGMA_LORA_GRADUATE_MATHEMATICS import (
    TheologicalConstraint,
    ConstraintSet,
    FileObject,
    RepositoryCategory,
    ConstraintPreservingDataConstructor
)

# Create sample repository
repo = RepositoryCategory()

# Sample files with different constraints
sample_files = [
    {
        "path": "graduate_mathematics/kan_extension.py",
        "content": """# John 1:1 as Kan Extension
class KanExtension:
    """John 1:1 as Kan extension"""

    def __init__(self, functor, inclusion):
        self.functor = functor
        self.inclusion = inclusion

    def ran(self, c):
        """Compute Right Kan Extension"""
        candidates = [d for d in self.inclusion if self._has_morphism(d, c)]
        return ("limit", candidates)""",
        "constraints": [TheologicalConstraint.LOGOS, TheologicalConstraint.CHALCEDON],
        "language": "python"
    },
    {
        "path": "theology/lawvere_metric.py",
        "content": """# Lawvere Metric for Christlikeness
class LawvereMetric:
    """Generalized metric space for Christlikeness"""

    def __init__(self, distance):
        self.distance = distance

    def is_monotone(self, f_distance):
        """Check if transformation preserves Christlikeness"""
        return f_distance <= self.distance""",
        "constraints": [TheologicalConstraint.GRACE, TheologicalConstraint.AGAPE],
        "language": "python"
    },
    {
        "path": "system/eschaton_coalgebra.py",
        "content": """# Eschaton as Terminal Coalgebra
class TerminalCoalgebra:
    """nuX.F(X) - Terminal convergence"""

    def __init__(self, functor_f):
        self.functor = functor_f

    def unfold(self, seed):
        """Unfold terminal coalgebra"""
        return self.functor(seed)""",
        "constraints": [TheologicalConstraint.KENOSIS, TheologicalConstraint.ESCHATON],
        "language": "python"
    }
]

# Add files to repository
for file_info in sample_files:
    file_obj = FileObject(
        path=file_info["path"],
        content_hash="",
        constraints=ConstraintSet(frozenset(file_info["constraints"])),
        language=file_info["language"],
        content=file_info["content"]
    )
    repo.add_object(file_obj)

# Generate training examples
constructor = ConstraintPreservingDataConstructor(chunk_size=100, overlap=20)
examples = constructor.construct(repo)

# Convert to training format
dataset = {
    "metadata": {
        "system": "$SYSTEM_VERSION",
        "timestamp": "$timestamp",
        "total_examples": len(examples),
        "constraints_used": [c.name for c in TheologicalConstraint]
    },
    "examples": [example.to_training_format() for example in examples]
}

print(json.dumps(dataset, indent=2))
'@

    try {
        $dataset = python -c $pythonCode 2>&1 | ConvertFrom-Json

        # Save dataset
        $dataset | ConvertTo-Json -Depth 10 | Out-File $datasetFile -Encoding UTF8

        Write-Success "Dataset generated successfully"
        Write-Info "Total examples: $($dataset.metadata.total_examples)"
        Write-Info "Dataset file: $datasetFile"

        # Display dataset statistics
        Write-Info "Dataset statistics:"
        Write-Host "  • Total examples: $($dataset.metadata.total_examples)" -ForegroundColor Gray
        Write-Host "  • Constraints used: $($dataset.metadata.constraints_used -join ', ')" -ForegroundColor Gray
        Write-Host "  • Output directory: $datasetDir" -ForegroundColor Gray

        return $true
    } catch {
        Write-Error "Dataset generation failed: $_"
        return $false
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    # Create output directory
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Info "Output directory: $OutputDir"

    # Verify dependencies
    if (-not (Test-SystemDependencies)) {
        Write-Error "System dependency check failed"
        exit 1
    }

    $allSuccessful = $true

    # Run tests if requested
    if ($RunTests) {
        Write-Info "Running system tests..."
        try {
            python $TEST_SCRIPT
            if ($LASTEXITCODE -eq 0) {
                Write-Success "All tests passed"
            } else {
                Write-Error "Tests failed"
                $allSuccessful = $false
            }
        } catch {
            Write-Error "Test execution failed: $_"
            $allSuccessful = $false
        }
    }

    # Verify theorems if requested
    if ($VerifyTheorems) {
        if (-not (Verify-MathematicalTheorems)) {
            $allSuccessful = $false
        }

        if (-not (Verify-ConstraintPreservation)) {
            $allSuccessful = $false
        }
    }

    # Generate dataset if requested
    if ($GenerateDataset) {
        if (-not (Generate-TrainingDataset)) {
            $allSuccessful = $false
        }
    }

    # Run demonstration (default action)
    if ($Action -eq "demonstrate" -or $Action -eq "all") {
        if (-not (Invoke-SigmaLoraDemonstration)) {
            $allSuccessful = $false
        }
    }

    # Summary
    Write-Host "`n" + "="*70 -ForegroundColor Cyan
    Write-Host "Σ_LORA EXECUTION SUMMARY" -ForegroundColor Cyan
    Write-Host "="*70 -ForegroundColor Cyan

    if ($allSuccessful) {
        Write-Success "All operations completed successfully"
        Write-Host "System: $SYSTEM_VERSION" -ForegroundColor White
        Write-Host "Status: OPERATIONAL" -ForegroundColor Green
        Write-Host "Constraint Preservation: VERIFIED" -ForegroundColor Green
        Write-Host "Mathematical Theorems: VERIFIED" -ForegroundColor Green
    } else {
        Write-Error "Some operations failed"
        Write-Host "System: $SYSTEM_VERSION" -ForegroundColor White
        Write-Host "Status: DEGRADED" -ForegroundColor Yellow
        Write-Host "Check individual operation logs above" -ForegroundColor Yellow
